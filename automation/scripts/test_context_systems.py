#!/usr/bin/env python3
"""
Test suite for MH1 context and memory management systems.

Tests:
1. ContextManager initialization and chunking
2. Budget reservation and tracking
3. SQLite WAL mode and connection pooling
4. Thread safety under concurrent load

Results written to telemetry/context_systems_test.json
"""

import json
import os
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.runner import ContextManager, ContextConfig, ContextStrategy
from lib.budget import (
    BudgetManager, BudgetConfig, BudgetStatus,
    BudgetConnectionPool, init_budget_db, get_budget_db, BUDGET_DB_PATH
)
from lib.telemetry import (
    TelemetryCollector, ConnectionPool, init_db, get_db, DB_PATH,
    log_run, get_tenant_costs
)

SYSTEM_ROOT = Path(__file__).parent.parent
OUTPUT_PATH = SYSTEM_ROOT / "telemetry" / "context_systems_test.json"


class TestResults:
    """Collects test results for JSON output."""

    def __init__(self):
        self.tests = []
        self.start_time = datetime.now(timezone.utc).isoformat()
        self.end_time = None
        self.summary = {}

    def add_test(self, name: str, passed: bool, duration_ms: float, details: dict = None):
        self.tests.append({
            "name": name,
            "passed": passed,
            "duration_ms": round(duration_ms, 2),
            "details": details or {}
        })

    def finalize(self):
        self.end_time = datetime.now(timezone.utc).isoformat()
        passed = sum(1 for t in self.tests if t["passed"])
        failed = len(self.tests) - passed
        self.summary = {
            "total": len(self.tests),
            "passed": passed,
            "failed": failed,
            "pass_rate": round(passed / len(self.tests) * 100, 1) if self.tests else 0
        }

    def to_dict(self):
        return {
            "test_run": {
                "start_time": self.start_time,
                "end_time": self.end_time,
                "summary": self.summary
            },
            "tests": self.tests
        }


results = TestResults()


# =============================================================================
# TEST 1: ContextManager Initialization
# =============================================================================

def test_context_manager_initialization():
    """Test ContextManager creates correctly with various input types."""
    start = time.perf_counter()
    details = {}

    try:
        # Test with list data
        list_data = [{"id": i, "name": f"item_{i}"} for i in range(100)]
        ctx_list = ContextManager(list_data)
        details["list_context_size"] = ctx_list.context_size
        details["list_length"] = len(ctx_list)

        # Test with dict data
        dict_data = {f"key_{i}": {"value": i} for i in range(50)}
        ctx_dict = ContextManager(dict_data)
        details["dict_context_size"] = ctx_dict.context_size
        details["dict_length"] = len(ctx_dict)

        # Test with string data
        string_data = "Lorem ipsum " * 1000
        ctx_str = ContextManager(string_data)
        details["string_context_size"] = ctx_str.context_size
        details["string_length"] = len(ctx_str)

        # Test with None
        ctx_none = ContextManager(None)
        details["none_context_size"] = ctx_none.context_size

        # Test with custom config
        config = ContextConfig(max_inline_tokens=4000, chunk_size=100)
        ctx_custom = ContextManager(list_data, config)
        details["custom_config_applied"] = ctx_custom.config.max_inline_tokens == 4000

        passed = True

    except Exception as e:
        passed = False
        details["error"] = str(e)

    duration = (time.perf_counter() - start) * 1000
    results.add_test("context_manager_initialization", passed, duration, details)
    return passed


# =============================================================================
# TEST 2: ContextManager Chunking Behavior
# =============================================================================

def test_context_manager_chunking():
    """Test chunking with various data sizes and verify thresholds."""
    start = time.perf_counter()
    details = {}

    try:
        # Small data - should be inline
        small_data = [{"id": i} for i in range(10)]
        ctx_small = ContextManager(small_data, ContextConfig(max_inline_tokens=8000))
        details["small_should_offload"] = ctx_small.should_offload()
        details["small_strategy"] = ctx_small.get_strategy().value

        # Medium data - should chunk
        medium_data = [{"id": i, "data": "x" * 100} for i in range(500)]
        ctx_medium = ContextManager(medium_data, ContextConfig(max_inline_tokens=8000))
        details["medium_should_offload"] = ctx_medium.should_offload()
        details["medium_strategy"] = ctx_medium.get_strategy().value
        details["medium_size_tokens"] = ctx_medium.context_size

        # Large data - should offload
        large_data = [{"id": i, "data": "x" * 500} for i in range(2000)]
        ctx_large = ContextManager(large_data, ContextConfig(max_inline_tokens=8000))
        details["large_should_offload"] = ctx_large.should_offload()
        details["large_strategy"] = ctx_large.get_strategy().value
        details["large_size_tokens"] = ctx_large.context_size

        # Test actual chunking
        chunks = list(ctx_medium.chunk(size=100))
        details["chunk_count"] = len(chunks)
        details["first_chunk_size"] = len(chunks[0]) if chunks else 0
        details["chunks_total_items"] = sum(len(c) for c in chunks)

        # Test peek
        peek_result = ctx_medium.peek(start=0, count=5)
        details["peek_returned_items"] = len(peek_result)

        # Test filter
        filtered = ctx_medium.filter(lambda x: x["id"] < 50)
        details["filter_returned_items"] = len(filtered)

        # Test aggregation buffer
        ctx_medium.aggregate_buffer("test", {"result": 1})
        ctx_medium.aggregate_buffer("test", {"result": 2})
        aggregated = ctx_medium.get_aggregated("test")
        details["aggregation_works"] = len(aggregated) == 2

        # Verify strategies
        passed = (
            not ctx_small.should_offload() and
            ctx_medium.should_offload() and
            ctx_large.should_offload() and
            ctx_small.get_strategy() == ContextStrategy.INLINE and
            details["chunks_total_items"] == 500
        )

    except Exception as e:
        passed = False
        details["error"] = str(e)

    duration = (time.perf_counter() - start) * 1000
    results.add_test("context_manager_chunking", passed, duration, details)
    return passed


# =============================================================================
# TEST 3: Context Offloading Thresholds
# =============================================================================

def test_offloading_thresholds():
    """Verify context offloading triggers at correct token thresholds."""
    start = time.perf_counter()
    details = {}

    try:
        config = ContextConfig(max_inline_tokens=8000)

        # Test at different token counts
        # Threshold is 8000 tokens ~ 32000 chars

        # Just under threshold (7500 tokens ~ 30000 chars)
        data_under = "x" * 30000
        ctx_under = ContextManager(data_under, config)
        details["under_threshold_size"] = ctx_under.context_size
        details["under_threshold_offload"] = ctx_under.should_offload()

        # Just over threshold (8500 tokens ~ 34000 chars)
        data_over = "x" * 34000
        ctx_over = ContextManager(data_over, config)
        details["over_threshold_size"] = ctx_over.context_size
        details["over_threshold_offload"] = ctx_over.should_offload()

        # At exactly threshold
        data_exact = "x" * 32000  # 8000 tokens
        ctx_exact = ContextManager(data_exact, config)
        details["at_threshold_size"] = ctx_exact.context_size
        details["at_threshold_offload"] = ctx_exact.should_offload()

        # Check strategy transitions
        # INLINE: <= max_inline_tokens
        # CHUNKED: > max_inline_tokens AND <= 6x max_inline_tokens
        # OFFLOADED: > 6x max_inline_tokens

        # CHUNKED range test (8001 to 48000 tokens)
        data_chunked = "x" * 100000  # ~25000 tokens
        ctx_chunked = ContextManager(data_chunked, config)
        details["chunked_range_strategy"] = ctx_chunked.get_strategy().value

        # OFFLOADED range test (>48000 tokens)
        data_offloaded = "x" * 250000  # ~62500 tokens
        ctx_offloaded = ContextManager(data_offloaded, config)
        details["offloaded_range_strategy"] = ctx_offloaded.get_strategy().value

        passed = (
            not ctx_under.should_offload() and
            ctx_over.should_offload() and
            ctx_chunked.get_strategy() == ContextStrategy.CHUNKED and
            ctx_offloaded.get_strategy() == ContextStrategy.OFFLOADED
        )

    except Exception as e:
        passed = False
        details["error"] = str(e)

    duration = (time.perf_counter() - start) * 1000
    results.add_test("offloading_thresholds", passed, duration, details)
    return passed


# =============================================================================
# TEST 4: Budget Manager Initialization
# =============================================================================

def test_budget_manager_initialization():
    """Test BudgetManager initializes correctly with telemetry."""
    start = time.perf_counter()
    details = {}

    try:
        # Initialize budget manager
        budget = BudgetManager()
        details["budget_manager_created"] = True

        # Check default config
        default_config = budget.get_config("nonexistent_tenant")
        details["default_daily_limit"] = default_config.daily_limit_usd
        details["default_monthly_limit"] = default_config.monthly_limit_usd
        details["default_per_run_limit"] = default_config.per_run_limit_usd

        # Set a custom config
        custom_config = BudgetConfig(
            tenant_id="test_tenant_init",
            daily_limit_usd=50.0,
            monthly_limit_usd=500.0,
            per_run_limit_usd=5.0
        )
        budget.set_config(custom_config)

        # Retrieve and verify
        retrieved = budget.get_config("test_tenant_init")
        details["custom_config_stored"] = retrieved.daily_limit_usd == 50.0
        details["custom_monthly_limit"] = retrieved.monthly_limit_usd

        passed = (
            default_config.daily_limit_usd == 100.0 and
            retrieved.daily_limit_usd == 50.0
        )

    except Exception as e:
        passed = False
        details["error"] = str(e)

    duration = (time.perf_counter() - start) * 1000
    results.add_test("budget_manager_initialization", passed, duration, details)
    return passed


# =============================================================================
# TEST 5: Budget Reservation and Tracking
# =============================================================================

def test_budget_reservation():
    """Test budget reservation creation and release."""
    start = time.perf_counter()
    details = {}

    try:
        budget = BudgetManager()
        tenant_id = f"test_tenant_{uuid.uuid4().hex[:8]}"

        # Set up a tenant config
        config = BudgetConfig(
            tenant_id=tenant_id,
            daily_limit_usd=100.0,
            monthly_limit_usd=1000.0,
            per_run_limit_usd=10.0,
            block_on_exceed=False
        )
        budget.set_config(config)

        # Create a reservation
        reservation_id = budget.reserve_budget(tenant_id, 5.0, ttl_seconds=60)
        details["reservation_created"] = reservation_id is not None
        details["reservation_id"] = reservation_id

        # Check budget status includes reservation
        status = budget.check_budget(tenant_id)
        details["status_type"] = status.status
        details["daily_remaining_with_reservation"] = status.daily_remaining

        # Create another reservation
        reservation_id_2 = budget.reserve_budget(tenant_id, 3.0, ttl_seconds=60)
        details["second_reservation_created"] = reservation_id_2 is not None

        # Release first reservation
        budget.release_reservation(reservation_id)
        details["reservation_released"] = True

        # Check status again
        status_after = budget.check_budget(tenant_id)
        details["status_after_release"] = status_after.status

        # Release second reservation
        budget.release_reservation(reservation_id_2)

        passed = (
            reservation_id is not None and
            reservation_id_2 is not None
        )

    except Exception as e:
        passed = False
        details["error"] = str(e)

    duration = (time.perf_counter() - start) * 1000
    results.add_test("budget_reservation", passed, duration, details)
    return passed


# =============================================================================
# TEST 6: Budget Check and Reserve Atomic Operation
# =============================================================================

def test_budget_check_and_reserve():
    """Test atomic check-and-reserve operation."""
    start = time.perf_counter()
    details = {}

    try:
        budget = BudgetManager()
        tenant_id = f"test_tenant_atomic_{uuid.uuid4().hex[:8]}"

        # Set up config
        config = BudgetConfig(
            tenant_id=tenant_id,
            daily_limit_usd=20.0,
            monthly_limit_usd=200.0,
            per_run_limit_usd=5.0,
            block_on_exceed=True
        )
        budget.set_config(config)

        # Atomic check and reserve - should succeed
        allowed, message, res_id = budget.check_and_reserve(tenant_id, 4.0, ttl_seconds=60)
        details["first_allowed"] = allowed
        details["first_reservation_id"] = res_id

        # Try to reserve more than per-run limit
        allowed_over, message_over, res_id_over = budget.check_and_reserve(tenant_id, 6.0, ttl_seconds=60)
        details["over_per_run_allowed"] = allowed_over
        details["over_per_run_message"] = message_over

        # Clean up
        if res_id:
            budget.release_reservation(res_id)

        passed = (
            allowed and
            res_id is not None and
            not allowed_over and
            "per-run limit" in message_over
        )

    except Exception as e:
        passed = False
        details["error"] = str(e)

    duration = (time.perf_counter() - start) * 1000
    results.add_test("budget_check_and_reserve", passed, duration, details)
    return passed


# =============================================================================
# TEST 7: SQLite WAL Mode Verification
# =============================================================================

def test_sqlite_wal_mode():
    """Verify SQLite databases use WAL mode."""
    start = time.perf_counter()
    details = {}

    try:
        import sqlite3

        # Check telemetry database
        init_db()
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode")
            telemetry_mode = cursor.fetchone()[0]
            details["telemetry_journal_mode"] = telemetry_mode

            cursor.execute("PRAGMA synchronous")
            telemetry_sync = cursor.fetchone()[0]
            details["telemetry_synchronous"] = telemetry_sync

        # Check budget database
        init_budget_db()
        with get_budget_db() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode")
            budget_mode = cursor.fetchone()[0]
            details["budget_journal_mode"] = budget_mode

            cursor.execute("PRAGMA busy_timeout")
            budget_timeout = cursor.fetchone()[0]
            details["budget_busy_timeout_ms"] = budget_timeout

        # Verify WAL files exist
        telemetry_wal = DB_PATH.with_suffix(".db-wal")
        budget_wal = BUDGET_DB_PATH.with_suffix(".db-wal")
        details["telemetry_wal_exists"] = telemetry_wal.exists()
        details["budget_wal_exists"] = budget_wal.exists()

        passed = (
            telemetry_mode.lower() == "wal" and
            budget_mode.lower() == "wal"
        )

    except Exception as e:
        passed = False
        details["error"] = str(e)

    duration = (time.perf_counter() - start) * 1000
    results.add_test("sqlite_wal_mode", passed, duration, details)
    return passed


# =============================================================================
# TEST 8: Connection Pooling
# =============================================================================

def test_connection_pooling():
    """Test connection pool behavior."""
    start = time.perf_counter()
    details = {}

    try:
        # Create a test pool
        test_db = SYSTEM_ROOT / "telemetry" / "test_pool.db"
        pool = ConnectionPool(test_db, pool_size=5, timeout=5.0)

        # Get connections up to pool size
        connections = []
        for i in range(5):
            conn = pool.get_connection()
            connections.append(conn)

        details["got_5_connections"] = len(connections) == 5
        details["created_count"] = pool._created_count

        # Return all connections
        for conn in connections:
            pool.return_connection(conn)

        # Pool should now have connections available
        conn_after = pool.get_connection()
        details["got_pooled_connection"] = conn_after is not None
        pool.return_connection(conn_after)

        # Test pool exhaustion with short timeout
        small_pool = ConnectionPool(test_db, pool_size=2, timeout=0.1)
        c1 = small_pool.get_connection()
        c2 = small_pool.get_connection()

        # Third should timeout
        timeout_occurred = False
        try:
            c3 = small_pool.get_connection()
        except TimeoutError:
            timeout_occurred = True

        details["timeout_on_exhaustion"] = timeout_occurred

        small_pool.return_connection(c1)
        small_pool.return_connection(c2)

        # Clean up
        pool.close_all()
        small_pool.close_all()

        # Remove test database
        if test_db.exists():
            test_db.unlink()

        passed = (
            len(connections) == 5 and
            timeout_occurred
        )

    except Exception as e:
        passed = False
        details["error"] = str(e)

    duration = (time.perf_counter() - start) * 1000
    results.add_test("connection_pooling", passed, duration, details)
    return passed


# =============================================================================
# TEST 9: Thread Safety - Concurrent Budget Operations
# =============================================================================

def test_thread_safety_budget():
    """Test thread safety of budget operations under concurrent load."""
    start = time.perf_counter()
    details = {}

    try:
        budget = BudgetManager()
        tenant_id = f"test_concurrent_{uuid.uuid4().hex[:8]}"

        # Set up config
        config = BudgetConfig(
            tenant_id=tenant_id,
            daily_limit_usd=1000.0,
            monthly_limit_usd=10000.0,
            per_run_limit_usd=100.0
        )
        budget.set_config(config)

        # Track reservations made
        reservations = []
        errors = []
        lock = threading.Lock()

        def make_reservation(thread_id):
            try:
                allowed, msg, res_id = budget.check_and_reserve(tenant_id, 1.0, ttl_seconds=60)
                if res_id:
                    with lock:
                        reservations.append(res_id)
                return True
            except Exception as e:
                with lock:
                    errors.append(str(e))
                return False

        # Run 20 concurrent threads
        num_threads = 20
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(make_reservation, i) for i in range(num_threads)]
            results_list = [f.result() for f in as_completed(futures)]

        details["threads_run"] = num_threads
        details["reservations_made"] = len(reservations)
        details["errors_count"] = len(errors)
        if errors:
            details["first_error"] = errors[0]

        # Clean up reservations
        for res_id in reservations:
            budget.release_reservation(res_id)

        # All threads should succeed
        passed = (
            len(reservations) == num_threads and
            len(errors) == 0
        )

    except Exception as e:
        passed = False
        details["error"] = str(e)

    duration = (time.perf_counter() - start) * 1000
    results.add_test("thread_safety_budget", passed, duration, details)
    return passed


# =============================================================================
# TEST 10: Thread Safety - Concurrent Telemetry Logging
# =============================================================================

def test_thread_safety_telemetry():
    """Test thread safety of telemetry logging under concurrent load."""
    start = time.perf_counter()
    details = {}

    try:
        collector = TelemetryCollector()

        errors = []
        run_ids = []
        lock = threading.Lock()

        def log_test_run(thread_id):
            try:
                run_id = f"test_concurrent_{thread_id}_{uuid.uuid4().hex[:8]}"
                with lock:
                    run_ids.append(run_id)

                log_run(
                    run_id=run_id,
                    tenant_id="test_concurrent_tenant",
                    type="test",
                    name="concurrent_test",
                    status="success",
                    start_time=datetime.now(timezone.utc).isoformat(),
                    tokens_input=100,
                    tokens_output=50
                )
                return True
            except Exception as e:
                with lock:
                    errors.append(str(e))
                return False

        # Run 20 concurrent threads
        num_threads = 20
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(log_test_run, i) for i in range(num_threads)]
            results_list = [f.result() for f in as_completed(futures)]

        details["threads_run"] = num_threads
        details["runs_logged"] = len(run_ids)
        details["errors_count"] = len(errors)
        if errors:
            details["first_error"] = errors[0]

        # Verify runs were logged
        from lib.telemetry import query_runs
        logged_runs = query_runs(name="concurrent_test", limit=50)
        details["runs_in_db"] = len([r for r in logged_runs if r["run_id"] in run_ids])

        passed = (
            len(run_ids) == num_threads and
            len(errors) == 0
        )

    except Exception as e:
        passed = False
        details["error"] = str(e)

    duration = (time.perf_counter() - start) * 1000
    results.add_test("thread_safety_telemetry", passed, duration, details)
    return passed


# =============================================================================
# TEST 11: ContextManager Telemetry
# =============================================================================

def test_context_manager_telemetry():
    """Test that ContextManager properly tracks telemetry."""
    start = time.perf_counter()
    details = {}

    try:
        # Create context with data
        data = [{"id": i, "value": f"item_{i}"} for i in range(1000)]
        ctx = ContextManager(data, ContextConfig(max_inline_tokens=2000, chunk_size=100))

        # Process chunks and log sub-calls
        from lib.runner import SubCallResult

        chunk_count = 0
        for chunk in ctx.chunk(size=100):
            chunk_count += 1
            # Simulate a sub-call result
            result = SubCallResult(
                call_id=f"call_{chunk_count}",
                model="claude-haiku",
                tokens_input=len(chunk) * 10,
                tokens_output=50,
                duration_ms=100,
                status="success",
                output={"processed": len(chunk)}
            )
            ctx.log_sub_call(result)
            ctx.aggregate_buffer("results", {"chunk": chunk_count, "count": len(chunk)})

        # Get telemetry
        telemetry = ctx.get_telemetry()
        details["strategy"] = telemetry.strategy
        details["input_size_tokens"] = telemetry.input_size_tokens
        details["chunks_processed"] = telemetry.chunks_processed
        details["sub_calls_logged"] = len(telemetry.sub_calls)

        # Check aggregated results
        aggregated = ctx.get_aggregated("results")
        details["aggregated_count"] = len(aggregated)
        details["total_items_processed"] = sum(r["count"] for r in aggregated)

        passed = (
            telemetry.chunks_processed == chunk_count and
            len(telemetry.sub_calls) == chunk_count and
            details["total_items_processed"] == 1000
        )

    except Exception as e:
        passed = False
        details["error"] = str(e)

    duration = (time.perf_counter() - start) * 1000
    results.add_test("context_manager_telemetry", passed, duration, details)
    return passed


# =============================================================================
# TEST 12: Budget Status Calculation
# =============================================================================

def test_budget_status_calculation():
    """Test budget status correctly calculates remaining and percent used."""
    start = time.perf_counter()
    details = {}

    try:
        budget = BudgetManager()
        tenant_id = f"test_status_{uuid.uuid4().hex[:8]}"

        # Set up config
        config = BudgetConfig(
            tenant_id=tenant_id,
            daily_limit_usd=100.0,
            monthly_limit_usd=1000.0,
            per_run_limit_usd=20.0,
            warn_at_percent=0.8
        )
        budget.set_config(config)

        # Check initial status (no spending)
        status = budget.check_budget(tenant_id)
        details["initial_status"] = status.status
        details["initial_daily_remaining"] = status.daily_remaining
        details["initial_monthly_remaining"] = status.monthly_remaining

        # Create reservations to simulate spending
        res1 = budget.reserve_budget(tenant_id, 70.0, ttl_seconds=60)  # 70% of daily

        # Check status - should be warning (>80% with estimated)
        status_warning = budget.check_budget(tenant_id, estimated_cost=15.0)
        details["warning_status"] = status_warning.status
        details["warning_daily_percent"] = status_warning.daily_percent_used

        # Create more reservations to exceed
        res2 = budget.reserve_budget(tenant_id, 25.0, ttl_seconds=60)

        # Check status - should be exceeded
        status_exceeded = budget.check_budget(tenant_id, estimated_cost=10.0)
        details["exceeded_status"] = status_exceeded.status
        details["exceeded_message"] = status_exceeded.message

        # Clean up
        if res1:
            budget.release_reservation(res1)
        if res2:
            budget.release_reservation(res2)

        passed = (
            status.status == "ok" and
            status_warning.status == "warning" and
            status_exceeded.status == "exceeded"
        )

    except Exception as e:
        passed = False
        details["error"] = str(e)

    duration = (time.perf_counter() - start) * 1000
    results.add_test("budget_status_calculation", passed, duration, details)
    return passed


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 60)
    print("MH1 Context and Memory Management Test Suite")
    print("=" * 60)
    print()

    # Run all tests
    tests = [
        ("ContextManager Initialization", test_context_manager_initialization),
        ("ContextManager Chunking", test_context_manager_chunking),
        ("Offloading Thresholds", test_offloading_thresholds),
        ("Budget Manager Init", test_budget_manager_initialization),
        ("Budget Reservation", test_budget_reservation),
        ("Budget Check and Reserve", test_budget_check_and_reserve),
        ("SQLite WAL Mode", test_sqlite_wal_mode),
        ("Connection Pooling", test_connection_pooling),
        ("Thread Safety - Budget", test_thread_safety_budget),
        ("Thread Safety - Telemetry", test_thread_safety_telemetry),
        ("ContextManager Telemetry", test_context_manager_telemetry),
        ("Budget Status Calculation", test_budget_status_calculation),
    ]

    for name, test_func in tests:
        print(f"Running: {name}...", end=" ")
        try:
            passed = test_func()
            status = "PASS" if passed else "FAIL"
            print(status)
        except Exception as e:
            print(f"ERROR: {e}")
            results.add_test(name, False, 0, {"error": str(e)})

    # Finalize and write results
    results.finalize()

    print()
    print("=" * 60)
    print(f"Results: {results.summary['passed']}/{results.summary['total']} passed")
    print(f"Pass rate: {results.summary['pass_rate']}%")
    print("=" * 60)

    # Write to JSON
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results.to_dict(), f, indent=2)

    print(f"\nResults written to: {OUTPUT_PATH}")

    # Return exit code based on results
    return 0 if results.summary['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
