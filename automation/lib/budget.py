"""
Simple Budget Management for MH1.

NOT a full budget enforcement system. Just:
1. Track costs per tenant
2. Warn when approaching limits
3. Block when exceeded (optional)

Designed for 100+ clients with simple per-tenant limits.
Thread-safe with SQLite WAL mode for 20+ concurrent agents.
"""

from dataclasses import dataclass
from typing import Optional, Dict
from datetime import datetime, timedelta
import threading
import sqlite3
import queue
from pathlib import Path
from contextlib import contextmanager


# Database path for budget-specific data (separate from telemetry)
SYSTEM_ROOT = Path(__file__).parent.parent
BUDGET_DIR = SYSTEM_ROOT / "telemetry"
BUDGET_DB_PATH = BUDGET_DIR / "budget.db"

# Ensure directory exists
BUDGET_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class BudgetConfig:
    """Budget configuration for a tenant."""
    tenant_id: str
    daily_limit_usd: float = 100.0
    monthly_limit_usd: float = 2000.0
    per_run_limit_usd: float = 10.0
    warn_at_percent: float = 0.8  # Warn at 80% usage
    block_on_exceed: bool = False  # If True, block runs when over budget


@dataclass
class BudgetStatus:
    """Current budget status for a tenant."""
    tenant_id: str
    daily_spent: float
    daily_limit: float
    daily_remaining: float
    daily_percent_used: float
    monthly_spent: float
    monthly_limit: float
    monthly_remaining: float
    monthly_percent_used: float
    status: str  # "ok", "warning", "exceeded"
    message: str


class BudgetConnectionPool:
    """
    Thread-safe SQLite connection pool for budget operations.
    
    Uses WAL mode for better concurrent read/write performance with 20+ agents.
    """
    
    def __init__(self, db_path: Path, pool_size: int = 20, timeout: float = 30.0):
        """
        Initialize connection pool.
        
        Args:
            db_path: Path to SQLite database
            pool_size: Maximum number of pooled connections (default 20 for 20 agents)
            timeout: Timeout in seconds waiting for a connection
        """
        self.db_path = str(db_path)
        self.pool_size = pool_size
        self.timeout = timeout
        self._pool = queue.Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        self._created_count = 0
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection with WAL mode."""
        conn = sqlite3.connect(
            self.db_path,
            timeout=self.timeout,
            check_same_thread=False,  # Allow connection sharing with proper locking
            isolation_level=None  # Autocommit mode for better concurrency
        )
        conn.row_factory = sqlite3.Row
        
        # Enable WAL mode for better concurrent access
        conn.execute("PRAGMA journal_mode=WAL")
        # Increase cache size for better performance
        conn.execute("PRAGMA cache_size=-32000")  # 32MB cache
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys=ON")
        # Synchronous mode for durability with good performance
        conn.execute("PRAGMA synchronous=NORMAL")
        # Increase busy timeout for concurrent writes (30 seconds)
        conn.execute("PRAGMA busy_timeout=30000")
        
        return conn
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a connection from the pool or create a new one."""
        try:
            # Try to get from pool (non-blocking)
            return self._pool.get_nowait()
        except queue.Empty:
            # Pool is empty, create new connection if under limit
            with self._lock:
                if self._created_count < self.pool_size:
                    self._created_count += 1
                    return self._create_connection()
            
            # At limit, wait for a connection to be returned
            try:
                return self._pool.get(timeout=self.timeout)
            except queue.Empty:
                raise TimeoutError(f"Could not get database connection within {self.timeout}s")
    
    def return_connection(self, conn: sqlite3.Connection):
        """Return a connection to the pool."""
        try:
            self._pool.put_nowait(conn)
        except queue.Full:
            # Pool is full, close the connection
            conn.close()
            with self._lock:
                self._created_count -= 1
    
    def close_all(self):
        """Close all pooled connections."""
        while True:
            try:
                conn = self._pool.get_nowait()
                conn.close()
            except queue.Empty:
                break
        with self._lock:
            self._created_count = 0


# Global connection pool for budget operations
_budget_pool: Optional[BudgetConnectionPool] = None
_budget_pool_lock = threading.Lock()


def _get_budget_pool() -> BudgetConnectionPool:
    """Get or create the global budget connection pool."""
    global _budget_pool
    if _budget_pool is None:
        with _budget_pool_lock:
            if _budget_pool is None:
                _budget_pool = BudgetConnectionPool(BUDGET_DB_PATH, pool_size=20)
    return _budget_pool


@contextmanager
def get_budget_db():
    """Thread-safe context manager for budget database connections."""
    pool = _get_budget_pool()
    conn = pool.get_connection()
    try:
        yield conn
    finally:
        pool.return_connection(conn)


# Thread-safe initialization
_budget_db_initialized = False
_budget_init_lock = threading.Lock()


def init_budget_db():
    """Initialize budget database with WAL mode. Thread-safe."""
    global _budget_db_initialized
    
    if _budget_db_initialized:
        return
    
    with _budget_init_lock:
        if _budget_db_initialized:
            return
        
        with get_budget_db() as conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN IMMEDIATE")
            
            try:
                # Table for storing budget configs (persistent)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS budget_configs (
                        tenant_id TEXT PRIMARY KEY,
                        daily_limit_usd REAL DEFAULT 100.0,
                        monthly_limit_usd REAL DEFAULT 2000.0,
                        per_run_limit_usd REAL DEFAULT 10.0,
                        warn_at_percent REAL DEFAULT 0.8,
                        block_on_exceed INTEGER DEFAULT 0,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Table for budget reservations (for concurrent budget checking)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS budget_reservations (
                        reservation_id TEXT PRIMARY KEY,
                        tenant_id TEXT NOT NULL,
                        amount_usd REAL NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        expires_at TEXT NOT NULL,
                        status TEXT DEFAULT 'active'
                    )
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_reservations_tenant 
                    ON budget_reservations(tenant_id, status)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_reservations_expires 
                    ON budget_reservations(expires_at)
                """)
                
                cursor.execute("COMMIT")
                _budget_db_initialized = True
                
            except Exception:
                cursor.execute("ROLLBACK")
                raise


class BudgetManager:
    """
    Thread-safe budget tracking and enforcement for 20+ concurrent agents.
    
    Uses SQLite WAL mode and connection pooling for concurrent access.
    Supports budget reservations to prevent race conditions during concurrent runs.
    
    Usage:
        budget = BudgetManager()
        
        # Check before run
        status = budget.check_budget("tenant_123", estimated_cost=0.50)
        if status.status == "exceeded" and config.block_on_exceed:
            raise BudgetExceededError(status.message)
        
        # Reserve budget for a run (prevents over-allocation)
        reservation_id = budget.reserve_budget("tenant_123", 0.50, ttl_seconds=300)
        
        # After run completes, release the reservation
        budget.release_reservation(reservation_id)
    """
    
    # Default configs - in production, load from config/quotas.yaml
    DEFAULT_CONFIG = BudgetConfig(
        tenant_id="default",
        daily_limit_usd=100.0,
        monthly_limit_usd=2000.0,
        per_run_limit_usd=10.0
    )
    
    # Thread-safe config cache
    _config_lock = threading.RLock()
    
    def __init__(self, telemetry_collector=None):
        """
        Initialize with optional telemetry collector for cost data.
        
        Thread-safe initialization.
        If no collector provided, creates a new one.
        """
        if telemetry_collector is None:
            from lib.telemetry import TelemetryCollector
            telemetry_collector = TelemetryCollector()
        self.telemetry = telemetry_collector
        self._configs: Dict[str, BudgetConfig] = {}  # In-memory cache
        self._local = threading.local()  # Thread-local storage
        init_budget_db()
    
    def get_config(self, tenant_id: str) -> BudgetConfig:
        """
        Get budget config for tenant, or default. Thread-safe.
        
        First checks in-memory cache, then database, then returns default.
        """
        with self._config_lock:
            if tenant_id in self._configs:
                return self._configs[tenant_id]
        
        # Try loading from database
        with get_budget_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT daily_limit_usd, monthly_limit_usd, per_run_limit_usd, 
                       warn_at_percent, block_on_exceed
                FROM budget_configs WHERE tenant_id = ?
            """, (tenant_id,))
            row = cursor.fetchone()
            
            if row:
                config = BudgetConfig(
                    tenant_id=tenant_id,
                    daily_limit_usd=row[0],
                    monthly_limit_usd=row[1],
                    per_run_limit_usd=row[2],
                    warn_at_percent=row[3],
                    block_on_exceed=bool(row[4])
                )
                with self._config_lock:
                    self._configs[tenant_id] = config
                return config
        
        return self.DEFAULT_CONFIG
    
    def set_config(self, config: BudgetConfig):
        """
        Set budget config for a tenant. Thread-safe.
        
        Persists to database and updates in-memory cache.
        """
        with get_budget_db() as conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN IMMEDIATE")
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO budget_configs 
                    (tenant_id, daily_limit_usd, monthly_limit_usd, per_run_limit_usd,
                     warn_at_percent, block_on_exceed, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                """, (
                    config.tenant_id,
                    config.daily_limit_usd,
                    config.monthly_limit_usd,
                    config.per_run_limit_usd,
                    config.warn_at_percent,
                    1 if config.block_on_exceed else 0
                ))
                cursor.execute("COMMIT")
            except Exception:
                cursor.execute("ROLLBACK")
                raise
        
        with self._config_lock:
            self._configs[config.tenant_id] = config
    
    def _get_active_reservations(self, tenant_id: str) -> float:
        """Get total amount of active (non-expired) reservations for a tenant."""
        with get_budget_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE(SUM(amount_usd), 0.0) 
                FROM budget_reservations 
                WHERE tenant_id = ? 
                  AND status = 'active' 
                  AND expires_at > datetime('now')
            """, (tenant_id,))
            return cursor.fetchone()[0]
    
    def _cleanup_expired_reservations(self):
        """Clean up expired reservations. Thread-safe."""
        with get_budget_db() as conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN IMMEDIATE")
            try:
                cursor.execute("""
                    UPDATE budget_reservations 
                    SET status = 'expired'
                    WHERE status = 'active' AND expires_at <= datetime('now')
                """)
                cursor.execute("COMMIT")
            except Exception:
                cursor.execute("ROLLBACK")
    
    def reserve_budget(self, tenant_id: str, amount_usd: float, ttl_seconds: int = 300) -> Optional[str]:
        """
        Reserve budget for an upcoming run. Thread-safe.
        
        Prevents race conditions where multiple concurrent agents might
        all pass budget checks but collectively exceed the budget.
        
        Args:
            tenant_id: Tenant identifier
            amount_usd: Amount to reserve
            ttl_seconds: How long the reservation is valid (default 5 minutes)
        
        Returns:
            reservation_id if successful, None if budget would be exceeded
        """
        import uuid
        
        # First check if this would exceed budget
        status = self.check_budget(tenant_id, amount_usd)
        if status.status == "exceeded":
            config = self.get_config(tenant_id)
            if config.block_on_exceed:
                return None
        
        reservation_id = str(uuid.uuid4())
        
        with get_budget_db() as conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN IMMEDIATE")
            try:
                cursor.execute("""
                    INSERT INTO budget_reservations 
                    (reservation_id, tenant_id, amount_usd, expires_at, status)
                    VALUES (?, ?, ?, datetime('now', '+' || ? || ' seconds'), 'active')
                """, (reservation_id, tenant_id, amount_usd, ttl_seconds))
                cursor.execute("COMMIT")
                return reservation_id
            except Exception:
                cursor.execute("ROLLBACK")
                raise
    
    def release_reservation(self, reservation_id: str):
        """
        Release a budget reservation after run completes. Thread-safe.
        
        Args:
            reservation_id: The reservation to release
        """
        with get_budget_db() as conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN IMMEDIATE")
            try:
                cursor.execute("""
                    UPDATE budget_reservations 
                    SET status = 'released'
                    WHERE reservation_id = ?
                """, (reservation_id,))
                cursor.execute("COMMIT")
            except Exception:
                cursor.execute("ROLLBACK")
    
    def check_budget(self, tenant_id: str, estimated_cost: float = 0) -> BudgetStatus:
        """
        Check current budget status for a tenant. Thread-safe.
        
        Includes active reservations from concurrent runs in calculations.
        
        Args:
            tenant_id: Tenant identifier
            estimated_cost: Estimated cost of upcoming run (optional)
        
        Returns:
            BudgetStatus with current usage and status
        """
        # Periodically clean up expired reservations
        self._cleanup_expired_reservations()
        
        config = self.get_config(tenant_id)
        
        # Get current spend from telemetry
        daily_costs = self.telemetry.get_tenant_costs(tenant_id, days=1)
        monthly_costs = self.telemetry.get_tenant_costs(tenant_id, days=30)
        
        daily_spent = daily_costs["total_cost_usd"]
        monthly_spent = monthly_costs["total_cost_usd"]
        
        # Include active reservations (pending concurrent runs)
        active_reservations = self._get_active_reservations(tenant_id)
        
        # Calculate with estimated cost AND active reservations
        daily_projected = daily_spent + active_reservations + estimated_cost
        monthly_projected = monthly_spent + active_reservations + estimated_cost
        
        daily_percent = (daily_projected / config.daily_limit_usd) * 100 if config.daily_limit_usd > 0 else 0
        monthly_percent = (monthly_projected / config.monthly_limit_usd) * 100 if config.monthly_limit_usd > 0 else 0
        
        # Determine status
        if daily_projected > config.daily_limit_usd or monthly_projected > config.monthly_limit_usd:
            status = "exceeded"
            message = f"Budget exceeded: Daily ${daily_projected:.2f}/${config.daily_limit_usd:.2f}, Monthly ${monthly_projected:.2f}/${config.monthly_limit_usd:.2f}"
            if active_reservations > 0:
                message += f" (includes ${active_reservations:.2f} reserved for pending runs)"
        elif daily_percent >= config.warn_at_percent * 100 or monthly_percent >= config.warn_at_percent * 100:
            status = "warning"
            message = f"Budget warning: {max(daily_percent, monthly_percent):.0f}% used"
        else:
            status = "ok"
            message = "Budget within limits"
        
        return BudgetStatus(
            tenant_id=tenant_id,
            daily_spent=daily_spent,
            daily_limit=config.daily_limit_usd,
            daily_remaining=max(0, config.daily_limit_usd - daily_spent - active_reservations),
            daily_percent_used=daily_percent,
            monthly_spent=monthly_spent,
            monthly_limit=config.monthly_limit_usd,
            monthly_remaining=max(0, config.monthly_limit_usd - monthly_spent - active_reservations),
            monthly_percent_used=monthly_percent,
            status=status,
            message=message
        )
    
    def check_run_cost(self, tenant_id: str, estimated_cost: float) -> tuple[bool, str]:
        """
        Quick check if a run's estimated cost is within limits. Thread-safe.
        
        Returns:
            (allowed: bool, message: str)
        """
        config = self.get_config(tenant_id)
        
        # Check per-run limit
        if estimated_cost > config.per_run_limit_usd:
            return False, f"Estimated cost ${estimated_cost:.2f} exceeds per-run limit ${config.per_run_limit_usd:.2f}"
        
        # Check overall budget
        status = self.check_budget(tenant_id, estimated_cost)
        
        if status.status == "exceeded" and config.block_on_exceed:
            return False, status.message
        
        return True, status.message
    
    def check_and_reserve(self, tenant_id: str, estimated_cost: float, ttl_seconds: int = 300) -> tuple[bool, str, Optional[str]]:
        """
        Atomic check-and-reserve operation for concurrent safety. Thread-safe.
        
        Combines budget check and reservation in one operation to prevent
        race conditions between check and reserve.
        
        Args:
            tenant_id: Tenant identifier
            estimated_cost: Estimated cost of the run
            ttl_seconds: Reservation TTL in seconds
        
        Returns:
            (allowed: bool, message: str, reservation_id: Optional[str])
        """
        config = self.get_config(tenant_id)
        
        # Check per-run limit first
        if estimated_cost > config.per_run_limit_usd:
            return False, f"Estimated cost ${estimated_cost:.2f} exceeds per-run limit ${config.per_run_limit_usd:.2f}", None
        
        # Check budget and reserve atomically
        status = self.check_budget(tenant_id, estimated_cost)
        
        if status.status == "exceeded" and config.block_on_exceed:
            return False, status.message, None
        
        # Create reservation
        reservation_id = self.reserve_budget(tenant_id, estimated_cost, ttl_seconds)
        if reservation_id is None:
            return False, "Could not reserve budget", None
        
        return True, status.message, reservation_id


class BudgetExceededError(Exception):
    """Raised when a run would exceed budget limits."""
    pass
