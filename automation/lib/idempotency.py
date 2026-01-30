"""
Idempotency and Retry System for MH1.

Provides:
1. IdempotencyManager - Cache execution results to prevent duplicate work
2. RetryPolicy - Configurable retry behavior per error class
3. RetryExecutor - Execute functions with automatic retry and idempotency

Thread-safe with SQLite WAL mode for 20+ concurrent agents.

Usage:
    from lib.idempotency import RetryExecutor, IdempotencyManager, RetryPolicy

    # Basic usage with defaults
    executor = RetryExecutor()
    result = executor.execute_with_retry(
        func=my_skill_function,
        client_id="acme",
        module_id="lifecycle-audit",
        skill_name="data-extraction",
        input_data={"contact_ids": [1, 2, 3]}
    )

    # Check if operation succeeded
    if result.success:
        print(f"Output: {result.output}")
    else:
        print(f"Failed: {result.error_class} - {result.error_message}")
"""

import hashlib
import json
import os
import random
import re
import sqlite3
import threading
import time
import queue
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import yaml


# Base paths
SYSTEM_ROOT = Path(__file__).parent.parent
CONFIG_DIR = SYSTEM_ROOT / "config"
CACHE_DIR = SYSTEM_ROOT / ".mh1" / "idempotency_cache"
CACHE_DB_PATH = CACHE_DIR / "idempotency.db"

# Ensure directories exist
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class ErrorClass(Enum):
    """Classification of errors for retry policy selection."""
    TRANSIENT_API = "transient_api"
    EVALUATOR_FAILURE = "evaluator_failure"
    VALIDATION_ERROR = "validation_error"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


@dataclass
class ExecutionResult:
    """Result of a skill/function execution."""
    success: bool
    output: Any
    error_class: Optional[ErrorClass] = None
    error_message: Optional[str] = None
    attempt_count: int = 1
    total_duration_ms: int = 0
    cached: bool = False
    idempotency_key: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "output": self.output,
            "error_class": self.error_class.value if self.error_class else None,
            "error_message": self.error_message,
            "attempt_count": self.attempt_count,
            "total_duration_ms": self.total_duration_ms,
            "cached": self.cached,
            "idempotency_key": self.idempotency_key
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ExecutionResult":
        """Create from dictionary."""
        error_class = None
        if data.get("error_class"):
            try:
                error_class = ErrorClass(data["error_class"])
            except ValueError:
                error_class = ErrorClass.UNKNOWN

        return cls(
            success=data["success"],
            output=data.get("output"),
            error_class=error_class,
            error_message=data.get("error_message"),
            attempt_count=data.get("attempt_count", 1),
            total_duration_ms=data.get("total_duration_ms", 0),
            cached=data.get("cached", False),
            idempotency_key=data.get("idempotency_key")
        )


@dataclass
class RetryAttempt:
    """Record of a single retry attempt."""
    attempt_number: int
    timestamp: str
    duration_ms: int
    success: bool
    error_class: Optional[str] = None
    error_message: Optional[str] = None


# ============================================================================
# Connection Pool for SQLite
# ============================================================================

class IdempotencyConnectionPool:
    """
    Thread-safe SQLite connection pool for idempotency cache.

    Uses WAL mode for concurrent read/write performance with 20+ agents.
    """

    def __init__(self, db_path: Path, pool_size: int = 20, timeout: float = 30.0):
        """
        Initialize connection pool.

        Args:
            db_path: Path to SQLite database
            pool_size: Maximum number of pooled connections
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
            check_same_thread=False,
            isolation_level=None  # Autocommit mode
        )
        conn.row_factory = sqlite3.Row

        # Enable WAL mode for better concurrent access
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA cache_size=-32000")  # 32MB cache
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA busy_timeout=30000")  # 30 seconds

        return conn

    def get_connection(self) -> sqlite3.Connection:
        """Get a connection from the pool or create a new one."""
        try:
            return self._pool.get_nowait()
        except queue.Empty:
            with self._lock:
                if self._created_count < self.pool_size:
                    self._created_count += 1
                    return self._create_connection()

            try:
                return self._pool.get(timeout=self.timeout)
            except queue.Empty:
                raise TimeoutError(f"Could not get database connection within {self.timeout}s")

    def return_connection(self, conn: sqlite3.Connection):
        """Return a connection to the pool."""
        try:
            self._pool.put_nowait(conn)
        except queue.Full:
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


# Global connection pool
_idempotency_pool: Optional[IdempotencyConnectionPool] = None
_pool_lock = threading.Lock()


def _get_pool() -> IdempotencyConnectionPool:
    """Get or create the global idempotency connection pool."""
    global _idempotency_pool
    if _idempotency_pool is None:
        with _pool_lock:
            if _idempotency_pool is None:
                _idempotency_pool = IdempotencyConnectionPool(CACHE_DB_PATH, pool_size=20)
    return _idempotency_pool


@contextmanager
def get_idempotency_db():
    """Thread-safe context manager for idempotency database connections."""
    pool = _get_pool()
    conn = pool.get_connection()
    try:
        yield conn
    finally:
        pool.return_connection(conn)


# Thread-safe initialization
_db_initialized = False
_init_lock = threading.Lock()


def init_idempotency_db():
    """Initialize idempotency database with WAL mode. Thread-safe."""
    global _db_initialized

    if _db_initialized:
        return

    with _init_lock:
        if _db_initialized:
            return

        with get_idempotency_db() as conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN IMMEDIATE")

            try:
                # Main cache table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS idempotency_cache (
                        idempotency_key TEXT PRIMARY KEY,
                        client_id TEXT NOT NULL,
                        module_id TEXT,
                        skill_name TEXT NOT NULL,
                        input_hash TEXT NOT NULL,
                        result_json TEXT NOT NULL,
                        success INTEGER NOT NULL,
                        error_class TEXT,
                        created_at TEXT NOT NULL,
                        expires_at TEXT NOT NULL,
                        attempt_count INTEGER DEFAULT 1,
                        total_duration_ms INTEGER DEFAULT 0
                    )
                """)

                # Index for cleanup queries
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_cache_expires
                    ON idempotency_cache(expires_at)
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_cache_client
                    ON idempotency_cache(client_id, skill_name)
                """)

                # Retry attempts tracking table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS retry_attempts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        idempotency_key TEXT NOT NULL,
                        attempt_number INTEGER NOT NULL,
                        timestamp TEXT NOT NULL,
                        duration_ms INTEGER,
                        success INTEGER NOT NULL,
                        error_class TEXT,
                        error_message TEXT,
                        FOREIGN KEY (idempotency_key) REFERENCES idempotency_cache(idempotency_key)
                    )
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_attempts_key
                    ON retry_attempts(idempotency_key)
                """)

                cursor.execute("COMMIT")
                _db_initialized = True

            except Exception:
                cursor.execute("ROLLBACK")
                raise


# ============================================================================
# IdempotencyManager
# ============================================================================

class IdempotencyManager:
    """
    Manages idempotency keys and caching of execution results.

    Thread-safe for 20+ concurrent agents using SQLite WAL mode.

    Usage:
        manager = IdempotencyManager()

        # Generate a key
        key = manager.generate_key("acme", "lifecycle", "data-extract", {"ids": [1,2,3]})

        # Check cache
        cached = manager.check(key)
        if cached:
            return cached

        # Execute and store
        result = execute_skill(...)
        manager.store(key, result)
    """

    def __init__(self, cache_dir: str = None, config_path: str = None):
        """
        Initialize IdempotencyManager.

        Args:
            cache_dir: Directory for cache storage (default: .mh1/idempotency_cache/)
            config_path: Path to retry_policy.yaml (default: config/retry_policy.yaml)
        """
        self.cache_dir = Path(cache_dir) if cache_dir else CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.config_path = Path(config_path) if config_path else CONFIG_DIR / "retry_policy.yaml"
        self._config = None
        self._config_lock = threading.Lock()

        init_idempotency_db()

    @property
    def config(self) -> Dict:
        """Load and cache configuration. Thread-safe."""
        if self._config is None:
            with self._config_lock:
                if self._config is None:
                    if self.config_path.exists():
                        with open(self.config_path) as f:
                            self._config = yaml.safe_load(f)
                    else:
                        self._config = self._default_config()
        return self._config

    def _default_config(self) -> Dict:
        """Return default configuration if config file not found."""
        return {
            "idempotency": {
                "key_format": "{client_id}:{module_id}:{skill_name}:{input_hash}",
                "cache_ttl_hours": 24,
                "on_duplicate_success": "SKIP",
                "on_duplicate_failure": "RETRY"
            }
        }

    def generate_key(
        self,
        client_id: str,
        module_id: str,
        skill_name: str,
        input_data: Any
    ) -> str:
        """
        Generate a unique idempotency key for the given inputs.

        Args:
            client_id: Client/tenant identifier
            module_id: Module or workflow identifier
            skill_name: Name of the skill being executed
            input_data: Input data (will be hashed)

        Returns:
            Idempotency key string
        """
        # Hash the input data
        input_str = json.dumps(input_data, sort_keys=True, default=str)
        input_hash = hashlib.sha256(input_str.encode()).hexdigest()[:16]

        # Format key according to config
        key_format = self.config.get("idempotency", {}).get(
            "key_format",
            "{client_id}:{module_id}:{skill_name}:{input_hash}"
        )

        return key_format.format(
            client_id=client_id or "default",
            module_id=module_id or "default",
            skill_name=skill_name,
            input_hash=input_hash
        )

    def check(self, key: str) -> Optional[ExecutionResult]:
        """
        Check if a cached result exists for the given key.

        Args:
            key: Idempotency key

        Returns:
            ExecutionResult if cached and not expired, None otherwise
        """
        with get_idempotency_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT result_json, success, error_class, expires_at,
                       attempt_count, total_duration_ms
                FROM idempotency_cache
                WHERE idempotency_key = ? AND expires_at > datetime('now')
            """, (key,))

            row = cursor.fetchone()
            if not row:
                return None

            # Parse cached result
            result_data = json.loads(row["result_json"])
            success = bool(row["success"])

            # Check policy for duplicates
            idempotency_config = self.config.get("idempotency", {})

            if success:
                policy = idempotency_config.get("on_duplicate_success", "SKIP")
                if policy == "RETRY":
                    return None  # Force re-execution
            else:
                policy = idempotency_config.get("on_duplicate_failure", "RETRY")
                if policy == "RETRY":
                    return None  # Force re-execution

            # Return cached result
            error_class = None
            if row["error_class"]:
                try:
                    error_class = ErrorClass(row["error_class"])
                except ValueError:
                    error_class = ErrorClass.UNKNOWN

            return ExecutionResult(
                success=success,
                output=result_data.get("output"),
                error_class=error_class,
                error_message=result_data.get("error_message"),
                attempt_count=row["attempt_count"],
                total_duration_ms=row["total_duration_ms"],
                cached=True,
                idempotency_key=key
            )

    def store(
        self,
        key: str,
        result: ExecutionResult,
        client_id: str = None,
        module_id: str = None,
        skill_name: str = None,
        input_hash: str = None
    ):
        """
        Store an execution result in the cache.

        Args:
            key: Idempotency key
            result: Execution result to cache
            client_id: Client identifier (for indexing)
            module_id: Module identifier
            skill_name: Skill name
            input_hash: Input data hash
        """
        ttl_hours = self.config.get("idempotency", {}).get("cache_ttl_hours", 24)

        result_json = json.dumps({
            "output": result.output,
            "error_message": result.error_message
        }, default=str)

        now = datetime.now(timezone.utc)
        expires = now + timedelta(hours=ttl_hours)

        with get_idempotency_db() as conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN IMMEDIATE")

            try:
                # Parse key to extract components if not provided
                if not client_id:
                    parts = key.split(":")
                    if len(parts) >= 4:
                        client_id = parts[0]
                        module_id = parts[1]
                        skill_name = parts[2]
                        input_hash = parts[3]

                cursor.execute("""
                    INSERT OR REPLACE INTO idempotency_cache
                    (idempotency_key, client_id, module_id, skill_name, input_hash,
                     result_json, success, error_class, created_at, expires_at,
                     attempt_count, total_duration_ms)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    key,
                    client_id or "unknown",
                    module_id or "unknown",
                    skill_name or "unknown",
                    input_hash or "unknown",
                    result_json,
                    1 if result.success else 0,
                    result.error_class.value if result.error_class else None,
                    now.isoformat(),
                    expires.isoformat(),
                    result.attempt_count,
                    result.total_duration_ms
                ))

                cursor.execute("COMMIT")

            except Exception:
                cursor.execute("ROLLBACK")
                raise

    def clear(self, key: str):
        """
        Remove a cached result.

        Args:
            key: Idempotency key to remove
        """
        with get_idempotency_db() as conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN IMMEDIATE")
            try:
                cursor.execute(
                    "DELETE FROM idempotency_cache WHERE idempotency_key = ?",
                    (key,)
                )
                cursor.execute(
                    "DELETE FROM retry_attempts WHERE idempotency_key = ?",
                    (key,)
                )
                cursor.execute("COMMIT")
            except Exception:
                cursor.execute("ROLLBACK")
                raise

    def cleanup_expired(self):
        """Remove expired entries from the cache. Thread-safe."""
        with get_idempotency_db() as conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN IMMEDIATE")
            try:
                # Delete expired cache entries
                cursor.execute("""
                    DELETE FROM idempotency_cache
                    WHERE expires_at <= datetime('now')
                """)

                # Delete orphaned retry attempts
                cursor.execute("""
                    DELETE FROM retry_attempts
                    WHERE idempotency_key NOT IN (
                        SELECT idempotency_key FROM idempotency_cache
                    )
                """)

                cursor.execute("COMMIT")
            except Exception:
                cursor.execute("ROLLBACK")
                raise

    def log_attempt(
        self,
        key: str,
        attempt: RetryAttempt
    ):
        """
        Log a retry attempt for telemetry.

        Args:
            key: Idempotency key
            attempt: Retry attempt details
        """
        with get_idempotency_db() as conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN IMMEDIATE")
            try:
                cursor.execute("""
                    INSERT INTO retry_attempts
                    (idempotency_key, attempt_number, timestamp, duration_ms,
                     success, error_class, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    key,
                    attempt.attempt_number,
                    attempt.timestamp,
                    attempt.duration_ms,
                    1 if attempt.success else 0,
                    attempt.error_class,
                    attempt.error_message
                ))
                cursor.execute("COMMIT")
            except Exception:
                cursor.execute("ROLLBACK")
                raise

    def get_attempts(self, key: str) -> List[RetryAttempt]:
        """
        Get all retry attempts for a key.

        Args:
            key: Idempotency key

        Returns:
            List of retry attempts
        """
        with get_idempotency_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT attempt_number, timestamp, duration_ms, success,
                       error_class, error_message
                FROM retry_attempts
                WHERE idempotency_key = ?
                ORDER BY attempt_number
            """, (key,))

            return [
                RetryAttempt(
                    attempt_number=row["attempt_number"],
                    timestamp=row["timestamp"],
                    duration_ms=row["duration_ms"],
                    success=bool(row["success"]),
                    error_class=row["error_class"],
                    error_message=row["error_message"]
                )
                for row in cursor.fetchall()
            ]


# ============================================================================
# RetryPolicy
# ============================================================================

class RetryPolicy:
    """
    Configurable retry policy loaded from retry_policy.yaml.

    Supports different backoff strategies per error class:
    - exponential: 2^attempt * initial_delay
    - linear: attempt * initial_delay
    - fixed: constant delay

    Thread-safe for concurrent access.
    """

    def __init__(self, config_path: str = None):
        """
        Initialize RetryPolicy.

        Args:
            config_path: Path to retry_policy.yaml (default: config/retry_policy.yaml)
        """
        self.config_path = Path(config_path) if config_path else CONFIG_DIR / "retry_policy.yaml"
        self._config = None
        self._config_lock = threading.Lock()

    @property
    def config(self) -> Dict:
        """Load and cache configuration. Thread-safe."""
        if self._config is None:
            with self._config_lock:
                if self._config is None:
                    if self.config_path.exists():
                        with open(self.config_path) as f:
                            self._config = yaml.safe_load(f)
                    else:
                        self._config = self._default_config()
        return self._config

    def _default_config(self) -> Dict:
        """Return default configuration if config file not found."""
        return {
            "retry_policy": {
                "TRANSIENT_API": {
                    "max_attempts": 3,
                    "backoff_type": "exponential",
                    "initial_delay_ms": 1000,
                    "max_delay_ms": 30000,
                    "jitter": True
                },
                "EVALUATOR_FAILURE": {
                    "max_attempts": 2,
                    "backoff_type": "fixed",
                    "delay_ms": 5000
                },
                "VALIDATION_ERROR": {
                    "max_attempts": 1,
                    "escalate_to": "human_review"
                },
                "TIMEOUT": {
                    "max_attempts": 2,
                    "backoff_type": "exponential",
                    "initial_delay_ms": 5000,
                    "max_delay_ms": 60000
                },
                "UNKNOWN": {
                    "max_attempts": 1,
                    "escalate_to": "human_review"
                }
            },
            "hard_limits": {
                "max_total_attempts_per_skill": 5,
                "max_total_attempts_per_module": 20,
                "cooldown_between_module_retries_ms": 60000
            }
        }

    def get_policy(self, error_class: ErrorClass) -> Dict:
        """
        Get retry configuration for an error class.

        Args:
            error_class: The error classification

        Returns:
            Policy dict with max_attempts, backoff settings, etc.
        """
        policies = self.config.get("retry_policy", {})
        key = error_class.value.upper()

        # Try to find matching policy
        if key in policies:
            return policies[key]

        # Fall back to UNKNOWN policy
        return policies.get("UNKNOWN", {"max_attempts": 1})

    def should_retry(self, error_class: ErrorClass, attempt: int) -> bool:
        """
        Check if another retry is allowed.

        Args:
            error_class: The error classification
            attempt: Current attempt number (1-based)

        Returns:
            True if retry is allowed
        """
        policy = self.get_policy(error_class)
        max_attempts = policy.get("max_attempts", 1)

        # Check hard limits
        hard_limits = self.config.get("hard_limits", {})
        skill_max = hard_limits.get("max_total_attempts_per_skill", 5)

        return attempt < max_attempts and attempt < skill_max

    def get_delay(self, error_class: ErrorClass, attempt: int) -> float:
        """
        Calculate delay before next retry.

        Args:
            error_class: The error classification
            attempt: Current attempt number (1-based)

        Returns:
            Delay in seconds
        """
        policy = self.get_policy(error_class)
        backoff_type = policy.get("backoff_type", "fixed")

        if backoff_type == "exponential":
            initial_ms = policy.get("initial_delay_ms", 1000)
            max_ms = policy.get("max_delay_ms", 30000)
            delay_ms = min(initial_ms * (2 ** (attempt - 1)), max_ms)

        elif backoff_type == "linear":
            initial_ms = policy.get("initial_delay_ms", 1000)
            max_ms = policy.get("max_delay_ms", 30000)
            delay_ms = min(initial_ms * attempt, max_ms)

        else:  # fixed
            delay_ms = policy.get("delay_ms", 5000)

        # Add jitter if enabled (prevents thundering herd)
        if policy.get("jitter", False):
            jitter = random.uniform(0, 0.1) * delay_ms
            delay_ms += jitter

        return delay_ms / 1000.0  # Convert to seconds

    def should_escalate(self, error_class: ErrorClass) -> Optional[str]:
        """
        Check if this error class should escalate to human review.

        Args:
            error_class: The error classification

        Returns:
            Escalation target (e.g., "human_review") or None
        """
        policy = self.get_policy(error_class)
        return policy.get("escalate_to")

    def get_hard_limits(self) -> Dict:
        """Get hard limits configuration."""
        return self.config.get("hard_limits", {
            "max_total_attempts_per_skill": 5,
            "max_total_attempts_per_module": 20,
            "cooldown_between_module_retries_ms": 60000
        })


# ============================================================================
# Error Classifier
# ============================================================================

class ErrorClassifier:
    """
    Classifies exceptions into ErrorClass categories.

    Uses patterns from retry_policy.yaml for classification.
    """

    def __init__(self, config_path: str = None):
        """
        Initialize ErrorClassifier.

        Args:
            config_path: Path to retry_policy.yaml
        """
        self.config_path = Path(config_path) if config_path else CONFIG_DIR / "retry_policy.yaml"
        self._config = None
        self._config_lock = threading.Lock()
        self._compiled_patterns = None

    @property
    def config(self) -> Dict:
        """Load and cache configuration."""
        if self._config is None:
            with self._config_lock:
                if self._config is None:
                    if self.config_path.exists():
                        with open(self.config_path) as f:
                            self._config = yaml.safe_load(f)
                    else:
                        self._config = {}
        return self._config

    @property
    def compiled_patterns(self) -> List[Tuple[re.Pattern, ErrorClass]]:
        """Compile and cache regex patterns."""
        if self._compiled_patterns is None:
            patterns = []
            classification = self.config.get("error_classification", {})

            for item in classification.get("exception_patterns", []):
                try:
                    pattern = re.compile(item["pattern"], re.IGNORECASE)
                    error_class = ErrorClass(item["error_class"].lower())
                    patterns.append((pattern, error_class))
                except (ValueError, re.error):
                    continue

            self._compiled_patterns = patterns

        return self._compiled_patterns

    def classify(self, exception: Exception) -> ErrorClass:
        """
        Classify an exception into an ErrorClass.

        Args:
            exception: The exception to classify

        Returns:
            ErrorClass categorization
        """
        exc_type = type(exception).__name__
        exc_message = str(exception)
        combined = f"{exc_type}: {exc_message}"

        # Check against patterns
        for pattern, error_class in self.compiled_patterns:
            if pattern.search(combined):
                return error_class

        # Check for common exception types
        if isinstance(exception, TimeoutError):
            return ErrorClass.TIMEOUT

        if isinstance(exception, ConnectionError):
            return ErrorClass.TRANSIENT_API

        if isinstance(exception, ValueError):
            return ErrorClass.VALIDATION_ERROR

        # Check HTTP status codes in message
        http_codes = self.config.get("error_classification", {}).get("http_status_codes", {})
        for code, error_class_str in http_codes.items():
            if str(code) in exc_message:
                try:
                    return ErrorClass(error_class_str.lower())
                except ValueError:
                    continue

        return ErrorClass.UNKNOWN

    def classify_http_status(self, status_code: int) -> ErrorClass:
        """
        Classify an HTTP status code into an ErrorClass.

        Args:
            status_code: HTTP status code

        Returns:
            ErrorClass categorization
        """
        http_codes = self.config.get("error_classification", {}).get("http_status_codes", {})

        if status_code in http_codes:
            try:
                return ErrorClass(http_codes[status_code].lower())
            except ValueError:
                pass

        # Default classification by status code range
        if 400 <= status_code < 500:
            return ErrorClass.VALIDATION_ERROR
        elif status_code >= 500:
            return ErrorClass.TRANSIENT_API

        return ErrorClass.UNKNOWN


# ============================================================================
# RetryExecutor
# ============================================================================

class RetryExecutor:
    """
    Executes functions with automatic retry and idempotency.

    Combines IdempotencyManager and RetryPolicy for resilient execution.
    Thread-safe for 20+ concurrent agents.

    Usage:
        executor = RetryExecutor()

        result = executor.execute_with_retry(
            func=my_skill_function,
            client_id="acme",
            module_id="lifecycle-audit",
            skill_name="data-extraction",
            input_data={"contact_ids": [1, 2, 3]}
        )

        if result.success:
            print(f"Output: {result.output}")
        else:
            print(f"Failed: {result.error_class} - {result.error_message}")
    """

    def __init__(
        self,
        idempotency: IdempotencyManager = None,
        policy: RetryPolicy = None,
        classifier: ErrorClassifier = None,
        enable_telemetry: bool = True
    ):
        """
        Initialize RetryExecutor.

        Args:
            idempotency: IdempotencyManager instance (creates default if None)
            policy: RetryPolicy instance (creates default if None)
            classifier: ErrorClassifier instance (creates default if None)
            enable_telemetry: Whether to log retry attempts
        """
        self.idempotency = idempotency or IdempotencyManager()
        self.policy = policy or RetryPolicy()
        self.classifier = classifier or ErrorClassifier()
        self.enable_telemetry = enable_telemetry

        # Module-level attempt tracking (thread-safe)
        self._module_attempts: Dict[str, int] = {}
        self._module_lock = threading.Lock()

    def _get_module_attempts(self, module_id: str) -> int:
        """Get current attempt count for a module."""
        with self._module_lock:
            return self._module_attempts.get(module_id, 0)

    def _increment_module_attempts(self, module_id: str):
        """Increment attempt count for a module."""
        with self._module_lock:
            self._module_attempts[module_id] = self._module_attempts.get(module_id, 0) + 1

    def _reset_module_attempts(self, module_id: str):
        """Reset attempt count for a module."""
        with self._module_lock:
            self._module_attempts.pop(module_id, None)

    def execute_with_retry(
        self,
        func: Callable,
        client_id: str,
        module_id: str,
        skill_name: str,
        input_data: Any,
        max_attempts: int = None,
        skip_cache: bool = False
    ) -> ExecutionResult:
        """
        Execute a function with retry and idempotency.

        Args:
            func: Function to execute. Should return a dict with "output" key
                  or raise an exception on failure.
            client_id: Client/tenant identifier
            module_id: Module or workflow identifier
            skill_name: Name of the skill
            input_data: Input data for the function
            max_attempts: Override max attempts (uses policy default if None)
            skip_cache: If True, bypass idempotency cache

        Returns:
            ExecutionResult with success status, output or error details
        """
        # Generate idempotency key
        key = self.idempotency.generate_key(client_id, module_id, skill_name, input_data)

        # Check cache first (unless skipped)
        if not skip_cache:
            cached = self.idempotency.check(key)
            if cached:
                return cached

        # Check module-level hard limits
        hard_limits = self.policy.get_hard_limits()
        module_max = hard_limits.get("max_total_attempts_per_module", 20)

        current_module_attempts = self._get_module_attempts(module_id)
        if current_module_attempts >= module_max:
            return ExecutionResult(
                success=False,
                output=None,
                error_class=ErrorClass.UNKNOWN,
                error_message=f"Module {module_id} exceeded max attempts ({module_max})",
                idempotency_key=key
            )

        # Execute with retry
        attempt = 0
        total_duration_ms = 0
        last_error_class = ErrorClass.UNKNOWN
        last_error_message = ""

        while True:
            attempt += 1
            self._increment_module_attempts(module_id)

            start_time = time.time()

            try:
                # Execute the function
                result = func(input_data)

                duration_ms = int((time.time() - start_time) * 1000)
                total_duration_ms += duration_ms

                # Build success result
                output = result.get("output") if isinstance(result, dict) else result

                execution_result = ExecutionResult(
                    success=True,
                    output=output,
                    attempt_count=attempt,
                    total_duration_ms=total_duration_ms,
                    idempotency_key=key
                )

                # Store in cache first (before logging attempt, due to FK constraint)
                self.idempotency.store(
                    key,
                    execution_result,
                    client_id=client_id,
                    module_id=module_id,
                    skill_name=skill_name
                )

                # Log successful attempt (after cache entry exists)
                if self.enable_telemetry:
                    self.idempotency.log_attempt(key, RetryAttempt(
                        attempt_number=attempt,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        duration_ms=duration_ms,
                        success=True
                    ))

                return execution_result

            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                total_duration_ms += duration_ms

                # Classify the error
                error_class = self.classifier.classify(e)
                last_error_class = error_class
                last_error_message = str(e)

                # Check if we should retry
                effective_max = max_attempts or self.policy.get_policy(error_class).get("max_attempts", 1)
                hard_skill_max = hard_limits.get("max_total_attempts_per_skill", 5)
                effective_max = min(effective_max, hard_skill_max)

                if attempt >= effective_max:
                    # No more retries - return failure
                    execution_result = ExecutionResult(
                        success=False,
                        output=None,
                        error_class=error_class,
                        error_message=last_error_message,
                        attempt_count=attempt,
                        total_duration_ms=total_duration_ms,
                        idempotency_key=key
                    )

                    # Store failure in cache first (before logging, due to FK constraint)
                    self.idempotency.store(
                        key,
                        execution_result,
                        client_id=client_id,
                        module_id=module_id,
                        skill_name=skill_name
                    )

                    # Log failed attempt (after cache entry exists)
                    if self.enable_telemetry:
                        self.idempotency.log_attempt(key, RetryAttempt(
                            attempt_number=attempt,
                            timestamp=datetime.now(timezone.utc).isoformat(),
                            duration_ms=duration_ms,
                            success=False,
                            error_class=error_class.value,
                            error_message=last_error_message
                        ))

                    return execution_result

                # For retry attempts, we need to store a temporary entry first to satisfy FK
                # Create a temporary cache entry for logging purposes
                temp_result = ExecutionResult(
                    success=False,
                    output=None,
                    error_class=error_class,
                    error_message=last_error_message,
                    attempt_count=attempt,
                    total_duration_ms=total_duration_ms,
                    idempotency_key=key
                )
                self.idempotency.store(
                    key,
                    temp_result,
                    client_id=client_id,
                    module_id=module_id,
                    skill_name=skill_name
                )

                # Log failed attempt
                if self.enable_telemetry:
                    self.idempotency.log_attempt(key, RetryAttempt(
                        attempt_number=attempt,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        duration_ms=duration_ms,
                        success=False,
                        error_class=error_class.value,
                        error_message=last_error_message
                    ))

                # Calculate and apply delay
                delay = self.policy.get_delay(error_class, attempt)
                time.sleep(delay)

    def execute_batch_with_retry(
        self,
        items: List[Any],
        item_func: Callable,
        client_id: str,
        module_id: str,
        skill_name: str,
        max_parallel: int = 1
    ) -> List[ExecutionResult]:
        """
        Execute a function for each item in a batch with retry.

        Args:
            items: List of items to process
            item_func: Function to call for each item. Receives (item, index).
            client_id: Client identifier
            module_id: Module identifier
            skill_name: Skill name
            max_parallel: Maximum parallel executions (default 1 = sequential)

        Returns:
            List of ExecutionResults, one per item
        """
        results = []

        if max_parallel <= 1:
            # Sequential execution
            for i, item in enumerate(items):
                result = self.execute_with_retry(
                    func=lambda data: item_func(data["item"], data["index"]),
                    client_id=client_id,
                    module_id=module_id,
                    skill_name=f"{skill_name}[{i}]",
                    input_data={"item": item, "index": i}
                )
                results.append(result)
        else:
            # Parallel execution with thread pool
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=max_parallel) as executor:
                futures = []
                for i, item in enumerate(items):
                    future = executor.submit(
                        self.execute_with_retry,
                        func=lambda data: item_func(data["item"], data["index"]),
                        client_id=client_id,
                        module_id=module_id,
                        skill_name=f"{skill_name}[{i}]",
                        input_data={"item": item, "index": i}
                    )
                    futures.append(future)

                results = [f.result() for f in futures]

        return results


# ============================================================================
# Convenience Functions
# ============================================================================

def with_retry(
    client_id: str,
    module_id: str,
    skill_name: str
) -> Callable:
    """
    Decorator for adding retry behavior to a function.

    Usage:
        @with_retry("acme", "lifecycle", "extract-contacts")
        def my_skill(input_data):
            return {"output": process(input_data)}

        result = my_skill({"contact_ids": [1, 2, 3]})
    """
    executor = RetryExecutor()

    def decorator(func: Callable) -> Callable:
        def wrapper(input_data: Any) -> ExecutionResult:
            return executor.execute_with_retry(
                func=func,
                client_id=client_id,
                module_id=module_id,
                skill_name=skill_name,
                input_data=input_data
            )
        return wrapper
    return decorator


def clear_cache(key: str = None, client_id: str = None):
    """
    Clear idempotency cache entries.

    Args:
        key: Specific key to clear (if provided)
        client_id: Clear all entries for a client (if key not provided)
    """
    manager = IdempotencyManager()

    if key:
        manager.clear(key)
    else:
        manager.cleanup_expired()


# ============================================================================
# Main - Testing
# ============================================================================

if __name__ == "__main__":
    # Test the idempotency and retry system
    print("Testing Idempotency and Retry System")
    print("=" * 50)

    # Initialize components
    manager = IdempotencyManager()
    policy = RetryPolicy()
    executor = RetryExecutor()

    # Test 1: Generate idempotency key
    print("\n1. Idempotency Key Generation")
    key = manager.generate_key(
        "test-client",
        "test-module",
        "test-skill",
        {"ids": [1, 2, 3]}
    )
    print(f"   Key: {key}")

    # Test 2: Retry policy
    print("\n2. Retry Policy")
    for ec in ErrorClass:
        p = policy.get_policy(ec)
        print(f"   {ec.value}: max_attempts={p.get('max_attempts', 1)}")

    # Test 3: Successful execution
    print("\n3. Successful Execution")

    def successful_skill(input_data):
        return {"output": f"Processed {len(input_data.get('ids', []))} items"}

    result = executor.execute_with_retry(
        func=successful_skill,
        client_id="test-client",
        module_id="test-module",
        skill_name="test-skill",
        input_data={"ids": [1, 2, 3]}
    )
    print(f"   Success: {result.success}")
    print(f"   Output: {result.output}")
    print(f"   Attempts: {result.attempt_count}")

    # Test 4: Cached result
    print("\n4. Cached Result")
    result2 = executor.execute_with_retry(
        func=successful_skill,
        client_id="test-client",
        module_id="test-module",
        skill_name="test-skill",
        input_data={"ids": [1, 2, 3]}
    )
    print(f"   Cached: {result2.cached}")
    print(f"   Output: {result2.output}")

    # Test 5: Failed execution with retry
    print("\n5. Failed Execution with Retry")
    attempt_counter = [0]

    def failing_skill(input_data):
        attempt_counter[0] += 1
        if attempt_counter[0] < 3:
            raise ConnectionError("Simulated transient error")
        return {"output": "Finally succeeded!"}

    result3 = executor.execute_with_retry(
        func=failing_skill,
        client_id="test-client",
        module_id="test-module",
        skill_name="failing-skill",
        input_data={"test": True},
        skip_cache=True
    )
    print(f"   Success: {result3.success}")
    print(f"   Output: {result3.output}")
    print(f"   Attempts: {result3.attempt_count}")

    # Test 6: Get retry attempts
    print("\n6. Retry Attempts Log")
    attempts = manager.get_attempts(result3.idempotency_key)
    for a in attempts:
        print(f"   Attempt {a.attempt_number}: success={a.success}, duration={a.duration_ms}ms")

    print("\n" + "=" * 50)
    print("All tests completed!")
