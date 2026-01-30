"""
MH1 Telemetry Collector
Logs workflow runs, token usage, and errors.

Thread-safe with SQLite WAL mode for concurrent agent access (20+ agents).
"""

import json
import os
import sqlite3
import threading
import queue
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from contextlib import contextmanager

SYSTEM_ROOT = Path(__file__).parent.parent
TELEMETRY_DIR = SYSTEM_ROOT / "telemetry"
RUNS_DIR = TELEMETRY_DIR / "runs"
DB_PATH = TELEMETRY_DIR / "telemetry.db"

# Ensure directories exist
RUNS_DIR.mkdir(parents=True, exist_ok=True)

# Thread-safety: lock for init operations
_init_lock = threading.Lock()
_db_initialized = False


class ConnectionPool:
    """
    Thread-safe SQLite connection pool for concurrent access.
    
    Uses WAL mode for better concurrent read/write performance.
    Maintains a pool of connections to avoid connection overhead.
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
        conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys=ON")
        # Synchronous mode for durability with good performance
        conn.execute("PRAGMA synchronous=NORMAL")
        # Increase busy timeout for concurrent writes
        conn.execute("PRAGMA busy_timeout=30000")  # 30 seconds
        
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


# Global connection pool (initialized lazily)
_connection_pool: Optional[ConnectionPool] = None
_pool_lock = threading.Lock()


def _get_pool() -> ConnectionPool:
    """Get or create the global connection pool."""
    global _connection_pool
    if _connection_pool is None:
        with _pool_lock:
            if _connection_pool is None:
                _connection_pool = ConnectionPool(DB_PATH, pool_size=20)
    return _connection_pool


def init_db():
    """
    Initialize SQLite database for telemetry.
    
    Thread-safe initialization with WAL mode for concurrent access.
    """
    global _db_initialized
    
    if _db_initialized:
        return
    
    with _init_lock:
        if _db_initialized:
            return
        
        pool = _get_pool()
        conn = pool.get_connection()
        try:
            cursor = conn.cursor()
            
            # Begin transaction for schema creation
            cursor.execute("BEGIN IMMEDIATE")
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    tenant_id TEXT,
                    type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    version TEXT,
                    status TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration_seconds REAL,
                    tokens_input INTEGER DEFAULT 0,
                    tokens_output INTEGER DEFAULT 0,
                    tokens_total INTEGER DEFAULT 0,
                    cost_estimate_usd REAL,
                    model TEXT,
                    client TEXT,
                    error_type TEXT,
                    error_message TEXT,
                    eval_score REAL,
                    eval_pass INTEGER,
                    tags TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    step_number INTEGER,
                    step_name TEXT NOT NULL,
                    agent TEXT,
                    status TEXT NOT NULL,
                    start_time TEXT,
                    end_time TEXT,
                    duration_seconds REAL,
                    tokens_input INTEGER DEFAULT 0,
                    tokens_output INTEGER DEFAULT 0,
                    error TEXT,
                    FOREIGN KEY (run_id) REFERENCES runs(run_id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tool_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    step_name TEXT,
                    tool TEXT NOT NULL,
                    timestamp TEXT,
                    duration_ms INTEGER,
                    status TEXT,
                    error TEXT,
                    FOREIGN KEY (run_id) REFERENCES runs(run_id)
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_runs_name ON runs(name)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_runs_start_time ON runs(start_time)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_runs_tenant_id ON runs(tenant_id)
            """)
            
            cursor.execute("COMMIT")
            _db_initialized = True
            
        except Exception as e:
            cursor.execute("ROLLBACK")
            raise
        finally:
            pool.return_connection(conn)


@contextmanager
def get_db():
    """
    Thread-safe context manager for database connections.
    
    Uses connection pooling for efficient concurrent access.
    """
    init_db()
    pool = _get_pool()
    conn = pool.get_connection()
    try:
        yield conn
    finally:
        pool.return_connection(conn)


# Token costs (approximate, per 1M tokens)
TOKEN_COSTS = {
    "claude-sonnet-4": {"input": 3.0, "output": 15.0},
    "claude-haiku": {"input": 0.25, "output": 1.25},
    "claude-opus-4": {"input": 15.0, "output": 75.0},
}


def estimate_cost(tokens_input: int, tokens_output: int, model: str = "claude-sonnet-4") -> float:
    """Estimate cost in USD for a run."""
    costs = TOKEN_COSTS.get(model, TOKEN_COSTS["claude-sonnet-4"])
    input_cost = (tokens_input / 1_000_000) * costs["input"]
    output_cost = (tokens_output / 1_000_000) * costs["output"]
    return round(input_cost + output_cost, 4)


# Thread-local file lock for JSON writes
_file_write_lock = threading.Lock()


def log_run(
    run_id: str,
    type: str,
    name: str,
    status: str,
    start_time: str,
    end_time: str = None,
    version: str = None,
    duration_seconds: float = None,
    tokens_input: int = 0,
    tokens_output: int = 0,
    model: str = None,
    client: str = None,
    tenant_id: str = None,
    error: dict = None,
    evaluation: dict = None,
    steps: list = None,
    tool_calls: list = None,
    tags: list = None
):
    """
    Log a workflow/skill run to the database.
    
    Thread-safe for concurrent calls from 20+ agents.
    Uses WAL mode and connection pooling for optimal performance.
    """
    init_db()
    
    tokens_total = tokens_input + tokens_output
    cost = estimate_cost(tokens_input, tokens_output, model or "claude-sonnet-4")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Use IMMEDIATE transaction for write operations to avoid SQLITE_BUSY
        cursor.execute("BEGIN IMMEDIATE")
        
        try:
            # Insert main run record
            cursor.execute("""
                INSERT OR REPLACE INTO runs (
                    run_id, tenant_id, type, name, version, status, start_time, end_time,
                    duration_seconds, tokens_input, tokens_output, tokens_total,
                    cost_estimate_usd, model, client, error_type, error_message,
                    eval_score, eval_pass, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id,
                tenant_id,
                type,
                name,
                version,
                status,
                start_time,
                end_time,
                duration_seconds,
                tokens_input,
                tokens_output,
                tokens_total,
                cost,
                model,
                client,
                error.get("type") if error else None,
                error.get("message") if error else None,
                evaluation.get("score") if evaluation else None,
                1 if evaluation and evaluation.get("pass") else 0 if evaluation else None,
                json.dumps(tags) if tags else None
            ))
            
            # Insert steps
            if steps:
                for i, step in enumerate(steps):
                    cursor.execute("""
                        INSERT INTO steps (
                            run_id, step_number, step_name, agent, status,
                            start_time, end_time, duration_seconds,
                            tokens_input, tokens_output, error
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        run_id,
                        i + 1,
                        step.get("step_name"),
                        step.get("agent"),
                        step.get("status"),
                        step.get("start_time"),
                        step.get("end_time"),
                        step.get("duration_seconds"),
                        step.get("tokens_input", 0),
                        step.get("tokens_output", 0),
                        step.get("error")
                    ))
            
            # Insert tool calls
            if tool_calls:
                for call in tool_calls:
                    cursor.execute("""
                        INSERT INTO tool_calls (
                            run_id, step_name, tool, timestamp, duration_ms, status, error
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        run_id,
                        call.get("step_name"),
                        call.get("tool"),
                        call.get("timestamp"),
                        call.get("duration_ms"),
                        call.get("status"),
                        call.get("error")
                    ))
            
            cursor.execute("COMMIT")
            
        except Exception as e:
            cursor.execute("ROLLBACK")
            raise
    
    # Build run data for JSON file and return value
    run_data = {
        "run_id": run_id,
        "tenant_id": tenant_id,
        "type": type,
        "name": name,
        "version": version,
        "status": status,
        "start_time": start_time,
        "end_time": end_time,
        "duration_seconds": duration_seconds,
        "tokens": {"input": tokens_input, "output": tokens_output, "total": tokens_total},
        "cost_estimate_usd": cost,
        "model": model,
        "client": client,
        "error": error,
        "evaluation": evaluation,
        "steps": steps,
        "tool_calls": tool_calls,
        "tags": tags
    }
    
    # Thread-safe JSON file write
    json_path = RUNS_DIR / f"{run_id}.json"
    with _file_write_lock:
        with open(json_path, "w") as f:
            json.dump(run_data, f, indent=2)
    
    return run_data


def query_runs(
    status: str = None,
    name: str = None,
    client: str = None,
    since: str = None,
    limit: int = 100
) -> list:
    """
    Query runs from the database.
    
    Args:
        status: Filter by status (success, failed, review)
        name: Filter by workflow/skill name
        client: Filter by client
        since: Filter by start_time >= since (ISO format)
        limit: Maximum results
        
    Returns:
        List of run records
    """
    init_db()
    
    query = "SELECT * FROM runs WHERE 1=1"
    params = []
    
    if status:
        query += " AND status = ?"
        params.append(status)
    if name:
        query += " AND name = ?"
        params.append(name)
    if client:
        query += " AND client = ?"
        params.append(client)
    if since:
        query += " AND start_time >= ?"
        params.append(since)
    
    query += " ORDER BY start_time DESC LIMIT ?"
    params.append(limit)
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_stats(days: int = 7) -> dict:
    """
    Get aggregate statistics for the last N days.
    """
    init_db()
    
    since = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    from datetime import timedelta
    since = (since - timedelta(days=days)).isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Total runs by status
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM runs
            WHERE start_time >= ?
            GROUP BY status
        """, (since,))
        status_counts = {row["status"]: row["count"] for row in cursor.fetchall()}
        
        # Total tokens and cost
        cursor.execute("""
            SELECT 
                SUM(tokens_input) as total_input,
                SUM(tokens_output) as total_output,
                SUM(tokens_total) as total_tokens,
                SUM(cost_estimate_usd) as total_cost
            FROM runs
            WHERE start_time >= ?
        """, (since,))
        row = cursor.fetchone()
        
        # Average eval score
        cursor.execute("""
            SELECT AVG(eval_score) as avg_score
            FROM runs
            WHERE start_time >= ? AND eval_score IS NOT NULL
        """, (since,))
        avg_score = cursor.fetchone()["avg_score"]
        
        # Top workflows by runs
        cursor.execute("""
            SELECT name, COUNT(*) as count
            FROM runs
            WHERE start_time >= ?
            GROUP BY name
            ORDER BY count DESC
            LIMIT 5
        """, (since,))
        top_workflows = [(row["name"], row["count"]) for row in cursor.fetchall()]
        
        return {
            "period_days": days,
            "since": since,
            "total_runs": sum(status_counts.values()),
            "by_status": status_counts,
            "tokens": {
                "input": row["total_input"] or 0,
                "output": row["total_output"] or 0,
                "total": row["total_tokens"] or 0
            },
            "cost_usd": round(row["total_cost"] or 0, 2),
            "avg_eval_score": round(avg_score, 2) if avg_score else None,
            "top_workflows": top_workflows
        }


def get_failures(hours: int = 24) -> list:
    """Get recent failures for debugging."""
    init_db()
    
    from datetime import timedelta
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT run_id, name, status, error_type, error_message, start_time
            FROM runs
            WHERE start_time >= ? AND status = 'failed'
            ORDER BY start_time DESC
        """, (since,))
        return [dict(row) for row in cursor.fetchall()]


def get_tenant_costs(tenant_id: str, days: int = 30) -> dict:
    """
    Get cost summary for a tenant over the last N days.
    
    Args:
        tenant_id: Tenant identifier
        days: Number of days to look back (default 30)
    
    Returns:
        Dict with run_count, total_input_tokens, total_output_tokens, total_cost_usd
    """
    init_db()
    
    from datetime import timedelta
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as run_count,
                SUM(tokens_input) as total_input_tokens,
                SUM(tokens_output) as total_output_tokens,
                SUM(cost_estimate_usd) as total_cost
            FROM runs
            WHERE tenant_id = ? AND start_time > ?
        """, (tenant_id, cutoff))
        
        row = cursor.fetchone()
        return {
            "tenant_id": tenant_id,
            "period_days": days,
            "run_count": row[0] or 0,
            "total_input_tokens": row[1] or 0,
            "total_output_tokens": row[2] or 0,
            "total_cost_usd": round(row[3] or 0, 4)
        }


class TelemetryCollector:
    """
    Thread-safe class wrapper around telemetry functions for use by other modules.
    
    Provides object-oriented interface while using the same underlying
    database and connection pool. Safe for use by 20+ concurrent agents.
    """
    
    # Class-level lock for thread-safe instance operations
    _instance_lock = threading.Lock()
    
    def __init__(self, db_path: Path = None):
        """
        Initialize collector with optional custom db path.
        
        Thread-safe initialization using global connection pool.
        """
        self.db_path = db_path or DB_PATH
        self._local = threading.local()  # Thread-local storage for per-thread state
        init_db()
    
    def log_run(self, **kwargs):
        """
        Log a run. Thread-safe. See module-level log_run for args.
        
        Uses connection pool for concurrent access.
        """
        return log_run(**kwargs)
    
    def get_tenant_costs(self, tenant_id: str, days: int = 30) -> dict:
        """
        Get cost summary for a tenant. Thread-safe.
        
        Safe for concurrent calls from multiple agents.
        """
        return get_tenant_costs(tenant_id, days)
    
    def query_runs(self, **kwargs) -> list:
        """Query runs. Thread-safe. See module-level function."""
        return query_runs(**kwargs)
    
    def get_stats(self, days: int = 7) -> dict:
        """Get aggregate stats. Thread-safe. See module-level function."""
        return get_stats(days)
    
    def get_failures(self, hours: int = 24) -> list:
        """Get recent failures. Thread-safe. See module-level function."""
        return get_failures(hours)
    
    def log_run_async(self, **kwargs) -> threading.Thread:
        """
        Log a run asynchronously in a background thread.
        
        Returns the thread handle for optional joining.
        Useful for non-blocking telemetry in hot paths.
        """
        thread = threading.Thread(target=log_run, kwargs=kwargs, daemon=True)
        thread.start()
        return thread


if __name__ == "__main__":
    # Test telemetry
    init_db()
    
    # Log a test run
    result = log_run(
        run_id="test-123",
        type="workflow",
        name="lifecycle-audit",
        status="success",
        start_time="2026-01-23T10:00:00Z",
        end_time="2026-01-23T10:02:30Z",
        version="v1.0.0",
        duration_seconds=150,
        tokens_input=5000,
        tokens_output=2000,
        model="claude-sonnet-4",
        client="Acme Corp",
        evaluation={"score": 0.92, "pass": True},
        steps=[
            {"step_name": "discovery", "status": "success", "duration_seconds": 45},
            {"step_name": "analysis", "status": "success", "duration_seconds": 90}
        ]
    )
    print(f"Logged run: {result['run_id']}")
    
    # Query recent runs
    runs = query_runs(limit=5)
    print(f"\nRecent runs: {len(runs)}")
    for run in runs:
        print(f"  - {run['run_id']}: {run['name']} ({run['status']})")
    
    # Get stats
    stats = get_stats(days=7)
    print(f"\n7-day stats:")
    print(f"  Total runs: {stats['total_runs']}")
    print(f"  By status: {stats['by_status']}")
    print(f"  Total cost: ${stats['cost_usd']}")
