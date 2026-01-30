# BrightMatter Brain: Final Implementation Plan

**Version:** 2.0 (Post-Review)  
**Date:** January 28, 2026  
**Status:** Ready for Implementation

---

## Executive Summary

This document consolidates the original 3-phase implementation plan with all fixes identified by four independent reviews:
- **Phase 1 Review:** 36 issues (7 Critical, 9 High)
- **Phase 2 Review:** 26 issues (6 Critical, 8 High)
- **Phase 3 Review:** 44 issues (8 Critical, 12 High)
- **Architecture Review:** 35 issues (13 Critical, 15 High)

Total: **141 issues identified, 34 Critical, 44 High**

All critical and high-severity issues have been addressed in this plan.

---

## Architecture Overview (Updated)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   MH1 BRAIN (lib/brain/) - UPDATED                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                     INFRASTRUCTURE LAYER (NEW)                        │  │
│  │  exceptions.py │ retry.py │ rate_limiter.py │ metrics.py │ cache.py  │  │
│  │  health.py │ middleware.py │ validation.py │ circuit_breaker.py      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐     │
│  │   INGEST    │──▶│   SCORE     │──▶│   PREDICT   │──▶│  RECOMMEND  │     │
│  │  Gateway    │   │   Engine    │   │   Engine    │   │   (NBMs)    │     │
│  └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘     │
│         │                │                 │                 │              │
│         ▼                ▼                 ▼                 ▼              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │               LEARNING LOOP (with bounds + locking)                  │   │
│  │    Outcomes → Weight Updates → Shadow Testing → Model Promotion     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    REPORTING ENGINE (with pagination)                │   │
│  │         Hourly │ Daily │ Weekly │ Graceful Degradation              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                       OBSERVABILITY (NEW)                            │   │
│  │      Structured Logging │ Metrics │ Tracing │ Health Checks         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Module Structure (Final)

```
lib/brain/
├── __init__.py              # Public exports
├── exceptions.py            # NEW: Exception hierarchy
├── config.py                # Configuration (with secrets support)
├── types.py                 # Type definitions
├── validation.py            # NEW: Input validation
├── retry.py                 # NEW: Retry/backoff decorators
├── circuit_breaker.py       # NEW: Circuit breaker pattern
├── rate_limiter.py          # NEW: Rate limiting
├── cache.py                 # NEW: Caching layer
├── metrics.py               # NEW: Telemetry
├── health.py                # NEW: Health checks
├── middleware.py            # NEW: Auth/validation middleware
├── engine.py                # Main BrainEngine orchestrator
├── ingest.py                # EventGateway, FeedRouter
├── scoring.py               # PerformanceScorer
├── templates.py             # ProcessingTemplate
├── anomaly.py               # AnomalyDetector
├── learning.py              # LearningLoop
├── predictions.py           # PredictionEngine
├── recommendations.py       # RecommendationEngine
├── reporting.py             # ReportingEngine
└── delivery.py              # ReportDeliveryManager

config/
├── brain_scheduler.yaml     # Scheduler with jitter
├── brain_benchmarks.yaml    # Gold standards
├── brain_features.yaml      # NEW: Feature flags
├── brain_slos.yaml          # NEW: SLI/SLO definitions
├── brain_alerts.yaml        # NEW: Alert configs
└── firestore.rules          # NEW: Security rules

ui/app/api/brain/
├── health/route.ts          # NEW: Health endpoint
├── [clientId]/
│   ├── scores/route.ts      # With auth + rate limiting
│   ├── predictions/route.ts
│   ├── recommendations/route.ts
│   └── reports/route.ts
```

---

# PHASE 1: Core Engine + Infrastructure (Weeks 1-3)

## 1.0 NEW: Infrastructure Foundation

### 1.0.1 Exception Hierarchy

```python
# lib/brain/exceptions.py
"""
Structured exception hierarchy for Brain module.
All exceptions include error codes, severity, and retry eligibility.
"""

from enum import Enum
from typing import Optional, Dict, Any

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    TRANSIENT = "transient"      # Retry eligible
    PERMANENT = "permanent"      # Don't retry
    VALIDATION = "validation"    # Reject input
    RESOURCE = "resource"        # Backoff and retry

class BrainError(Exception):
    """Base exception for all Brain errors."""
    
    error_code: str = "BRAIN_ERROR"
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    category: ErrorCategory = ErrorCategory.PERMANENT
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        severity: Optional[ErrorSeverity] = None,
        category: Optional[ErrorCategory] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.error_code
        self.severity = severity or self.__class__.severity
        self.category = category or self.__class__.category
        self.context = context or {}
        self.cause = cause
        
    @property
    def is_retryable(self) -> bool:
        return self.category in (ErrorCategory.TRANSIENT, ErrorCategory.RESOURCE)
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_code": self.error_code,
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category.value,
            "context": self.context,
            "retryable": self.is_retryable,
        }

class ValidationError(BrainError):
    """Input validation failed."""
    error_code = "VALIDATION_ERROR"
    severity = ErrorSeverity.LOW
    category = ErrorCategory.VALIDATION

class ScoringError(BrainError):
    """Error during score calculation."""
    error_code = "SCORING_ERROR"
    severity = ErrorSeverity.MEDIUM
    category = ErrorCategory.PERMANENT

class IngestionError(BrainError):
    """Error during event ingestion."""
    error_code = "INGESTION_ERROR"
    severity = ErrorSeverity.MEDIUM
    category = ErrorCategory.TRANSIENT

class LearningError(BrainError):
    """Error in learning loop."""
    error_code = "LEARNING_ERROR"
    severity = ErrorSeverity.HIGH
    category = ErrorCategory.PERMANENT

class PredictionError(BrainError):
    """Error generating predictions."""
    error_code = "PREDICTION_ERROR"
    severity = ErrorSeverity.MEDIUM
    category = ErrorCategory.PERMANENT

class RateLimitExceeded(BrainError):
    """Rate limit exceeded."""
    error_code = "RATE_LIMIT_EXCEEDED"
    severity = ErrorSeverity.LOW
    category = ErrorCategory.RESOURCE

class CircuitOpenError(BrainError):
    """Circuit breaker is open."""
    error_code = "CIRCUIT_OPEN"
    severity = ErrorSeverity.MEDIUM
    category = ErrorCategory.TRANSIENT

class SecurityError(BrainError):
    """Security violation."""
    error_code = "SECURITY_ERROR"
    severity = ErrorSeverity.CRITICAL
    category = ErrorCategory.PERMANENT

class DuplicateEventError(BrainError):
    """Duplicate event detected."""
    error_code = "DUPLICATE_EVENT"
    severity = ErrorSeverity.LOW
    category = ErrorCategory.VALIDATION

class ConcurrencyError(BrainError):
    """Concurrent modification detected."""
    error_code = "CONCURRENCY_ERROR"
    severity = ErrorSeverity.MEDIUM
    category = ErrorCategory.TRANSIENT
```

### 1.0.2 Retry and Circuit Breaker

```python
# lib/brain/retry.py
"""
Retry decorators with exponential backoff.
"""

import functools
import time
import random
from typing import Type, Tuple, Callable, Optional
import structlog

from .exceptions import BrainError, ErrorCategory

logger = structlog.get_logger()

def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Retry decorator with exponential backoff and jitter.
    
    Args:
        max_attempts: Maximum number of attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Add random jitter to prevent thundering herd
        retryable_exceptions: Tuple of exceptions to retry on
        on_retry: Callback on each retry (attempt, exception, delay)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    
                    # Check if exception is retryable (for BrainError)
                    if isinstance(e, BrainError) and not e.is_retryable:
                        raise
                    
                    if attempt == max_attempts:
                        break
                    
                    # Calculate delay
                    delay = min(
                        max_delay,
                        base_delay * (exponential_base ** (attempt - 1))
                    )
                    
                    # Add jitter (±25%)
                    if jitter:
                        delay = delay * (0.75 + random.random() * 0.5)
                    
                    logger.warning(
                        "retry.attempt",
                        function=func.__name__,
                        attempt=attempt,
                        max_attempts=max_attempts,
                        delay=delay,
                        error=str(e)
                    )
                    
                    if on_retry:
                        on_retry(attempt, e, delay)
                    
                    time.sleep(delay)
            
            raise last_exception
        return wrapper
    return decorator


# lib/brain/circuit_breaker.py
"""
Circuit breaker pattern implementation.
"""

import time
import threading
from enum import Enum
from typing import Type, Tuple, Optional, Callable
from dataclasses import dataclass, field
import structlog

from .exceptions import CircuitOpenError

logger = structlog.get_logger()

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject all requests
    HALF_OPEN = "half_open"  # Testing if service recovered

@dataclass
class CircuitBreakerState:
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[float] = None
    last_state_change: float = field(default_factory=time.time)

class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures.
    
    States:
    - CLOSED: Normal operation, track failures
    - OPEN: After threshold failures, reject all calls for recovery_timeout
    - HALF_OPEN: After recovery_timeout, allow one test call
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exceptions: Tuple[Type[Exception], ...] = (Exception,),
        name: str = "default"
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exceptions = expected_exceptions
        self.name = name
        self._state = CircuitBreakerState()
        self._lock = threading.Lock()
        
    @property
    def state(self) -> CircuitState:
        with self._lock:
            self._maybe_transition()
            return self._state.state
            
    def _maybe_transition(self):
        """Check if state should transition."""
        if self._state.state == CircuitState.OPEN:
            # Check if recovery timeout elapsed
            if time.time() - self._state.last_state_change >= self.recovery_timeout:
                self._transition_to(CircuitState.HALF_OPEN)
                
    def _transition_to(self, new_state: CircuitState):
        """Transition to new state."""
        old_state = self._state.state
        self._state.state = new_state
        self._state.last_state_change = time.time()
        self._state.failure_count = 0
        self._state.success_count = 0
        
        logger.info(
            "circuit_breaker.state_change",
            name=self.name,
            from_state=old_state.value,
            to_state=new_state.value
        )
        
    def record_success(self):
        """Record successful call."""
        with self._lock:
            if self._state.state == CircuitState.HALF_OPEN:
                # Success in half-open means service recovered
                self._transition_to(CircuitState.CLOSED)
            else:
                self._state.success_count += 1
                
    def record_failure(self):
        """Record failed call."""
        with self._lock:
            self._state.failure_count += 1
            self._state.last_failure_time = time.time()
            
            if self._state.state == CircuitState.HALF_OPEN:
                # Failure in half-open means still broken
                self._transition_to(CircuitState.OPEN)
            elif self._state.failure_count >= self.failure_threshold:
                # Too many failures, open circuit
                self._transition_to(CircuitState.OPEN)
                
    def __enter__(self):
        """Context manager entry - check if call should proceed."""
        if self.state == CircuitState.OPEN:
            raise CircuitOpenError(
                f"Circuit breaker '{self.name}' is open",
                context={"recovery_in": self.recovery_timeout}
            )
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - record result."""
        if exc_type is None:
            self.record_success()
        elif issubclass(exc_type, self.expected_exceptions):
            self.record_failure()
        return False  # Don't suppress exception
        
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        with self:
            return func(*args, **kwargs)
```

### 1.0.3 Rate Limiter

```python
# lib/brain/rate_limiter.py
"""
Token bucket rate limiter.
"""

import time
import threading
from typing import Dict, Optional
from dataclasses import dataclass, field
import structlog

from .exceptions import RateLimitExceeded

logger = structlog.get_logger()

@dataclass
class TokenBucket:
    """Token bucket for rate limiting."""
    capacity: float
    refill_rate: float  # tokens per second
    tokens: float = field(init=False)
    last_refill: float = field(default_factory=time.time)
    
    def __post_init__(self):
        self.tokens = self.capacity
        
    def try_consume(self, tokens: float = 1.0) -> bool:
        """Try to consume tokens. Returns True if successful."""
        now = time.time()
        
        # Refill tokens
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
        
        # Try to consume
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

class RateLimiter:
    """
    Multi-bucket rate limiter.
    
    Supports:
    - Per-client rate limiting
    - Global rate limiting
    - Burst allowance
    """
    
    def __init__(
        self,
        default_capacity: float = 100.0,
        default_refill_rate: float = 10.0,  # 10 tokens/second
        global_capacity: Optional[float] = None,
        global_refill_rate: Optional[float] = None
    ):
        self.default_capacity = default_capacity
        self.default_refill_rate = default_refill_rate
        self._buckets: Dict[str, TokenBucket] = {}
        self._lock = threading.Lock()
        
        # Global bucket (optional)
        self._global_bucket = None
        if global_capacity and global_refill_rate:
            self._global_bucket = TokenBucket(global_capacity, global_refill_rate)
            
    def _get_bucket(self, key: str) -> TokenBucket:
        """Get or create bucket for key."""
        with self._lock:
            if key not in self._buckets:
                self._buckets[key] = TokenBucket(
                    self.default_capacity,
                    self.default_refill_rate
                )
            return self._buckets[key]
            
    def allow(self, key: str, tokens: float = 1.0) -> bool:
        """Check if request is allowed."""
        # Check global limit first
        if self._global_bucket and not self._global_bucket.try_consume(tokens):
            return False
            
        # Check per-key limit
        bucket = self._get_bucket(key)
        return bucket.try_consume(tokens)
        
    def check_or_raise(self, key: str, tokens: float = 1.0):
        """Check rate limit and raise if exceeded."""
        if not self.allow(key, tokens):
            raise RateLimitExceeded(
                f"Rate limit exceeded for key: {key}",
                context={"key": key, "tokens_requested": tokens}
            )
            
    def reset(self, key: str):
        """Reset bucket for key (for testing)."""
        with self._lock:
            if key in self._buckets:
                del self._buckets[key]
```

### 1.0.4 Input Validation

```python
# lib/brain/validation.py
"""
Input validation utilities.
"""

import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta

from .exceptions import ValidationError, SecurityError

# Patterns
CLIENT_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{1,64}$')
EVENT_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{1,128}$')

# Size limits
MAX_RAW_DATA_SIZE = 100_000  # 100KB
MAX_ENGAGEMENTS = 10**12     # 1 trillion (sanity check)
MAX_IMPRESSIONS = 10**12

def validate_client_id(client_id: str) -> str:
    """Validate and sanitize client_id."""
    if not client_id:
        raise ValidationError("client_id is required")
    
    if not CLIENT_ID_PATTERN.match(client_id):
        raise ValidationError(f"Invalid client_id format: {client_id}")
    
    # Path traversal check
    if '..' in client_id or '/' in client_id or '\\' in client_id:
        raise SecurityError(
            f"Potential path traversal in client_id",
            context={"client_id": client_id[:20]}
        )
    
    return client_id

def validate_event_id(event_id: str) -> str:
    """Validate event_id format."""
    if not event_id:
        raise ValidationError("event_id is required")
    
    if not EVENT_ID_PATTERN.match(event_id):
        raise ValidationError(f"Invalid event_id format")
    
    return event_id

def validate_raw_data(data: Dict) -> Dict:
    """Validate and sanitize raw_data."""
    # Check size
    try:
        serialized = json.dumps(data)
        if len(serialized) > MAX_RAW_DATA_SIZE:
            # Truncate to essential fields only
            essential_fields = {
                'likes', 'comments', 'shares', 'clicks', 'opens', 'views',
                'impressions', 'engagements', 'followers', 'sent', 'bounces'
            }
            data = {k: v for k, v in data.items() if k in essential_fields}
    except (TypeError, ValueError) as e:
        raise ValidationError(f"raw_data is not JSON serializable: {e}")
    
    return data

def validate_event_data(
    engagements: int,
    impressions: int,
    audience_size: int,
    timestamp: datetime
) -> None:
    """Validate event numeric fields."""
    errors = []
    
    # Non-negative checks
    if engagements < 0:
        errors.append("engagements cannot be negative")
    if impressions < 0:
        errors.append("impressions cannot be negative")
    if audience_size < 0:
        errors.append("audience_size cannot be negative")
    
    # Sanity checks
    if engagements > MAX_ENGAGEMENTS:
        errors.append(f"engagements exceeds maximum ({MAX_ENGAGEMENTS})")
    if impressions > MAX_IMPRESSIONS:
        errors.append(f"impressions exceeds maximum ({MAX_IMPRESSIONS})")
    
    # Timestamp checks
    now = datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    
    if timestamp > now + timedelta(hours=1):
        errors.append("timestamp cannot be more than 1 hour in future")
    if timestamp < now - timedelta(days=365):
        errors.append("timestamp cannot be more than 1 year in past")
    
    if errors:
        raise ValidationError(
            f"Event validation failed: {'; '.join(errors)}",
            context={"errors": errors}
        )

def validate_outcome_timestamps(
    prediction_timestamp: datetime,
    observation_timestamp: datetime
) -> None:
    """Validate outcome timestamp relationships."""
    now = datetime.now(timezone.utc)
    
    # Ensure timezone-aware
    if prediction_timestamp.tzinfo is None:
        prediction_timestamp = prediction_timestamp.replace(tzinfo=timezone.utc)
    if observation_timestamp.tzinfo is None:
        observation_timestamp = observation_timestamp.replace(tzinfo=timezone.utc)
    
    if prediction_timestamp > now:
        raise ValidationError("Prediction timestamp cannot be in future")
    
    if observation_timestamp < prediction_timestamp:
        raise ValidationError("Observation must come after prediction")
    
    min_latency = timedelta(minutes=5)
    if observation_timestamp - prediction_timestamp < min_latency:
        raise ValidationError(
            "Observation too soon after prediction",
            context={"minimum_latency_minutes": 5}
        )
```

### 1.0.5 Observability (Metrics + Logging)

```python
# lib/brain/metrics.py
"""
Telemetry and metrics collection.
"""

import time
import functools
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
import structlog

logger = structlog.get_logger()

@dataclass
class MetricPoint:
    name: str
    value: float
    timestamp: float = field(default_factory=time.time)
    tags: Dict[str, str] = field(default_factory=dict)

class MetricsCollector:
    """
    Metrics collection with multiple backends.
    
    Collects:
    - Counters (incrementing values)
    - Gauges (point-in-time values)
    - Histograms (distributions)
    - Timers (latency tracking)
    """
    
    def __init__(self, prefix: str = "brain"):
        self.prefix = prefix
        self._counters: Dict[str, float] = {}
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = {}
        
    def _format_name(self, name: str) -> str:
        return f"{self.prefix}.{name}"
        
    def increment(self, name: str, value: float = 1.0, tags: Dict[str, str] = None):
        """Increment a counter."""
        full_name = self._format_name(name)
        tag_str = self._tags_to_str(tags or {})
        key = f"{full_name}:{tag_str}"
        
        self._counters[key] = self._counters.get(key, 0) + value
        
        # Also emit to logger
        logger.debug(
            "metric.counter",
            metric=full_name,
            value=value,
            tags=tags
        )
        
    def gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set a gauge value."""
        full_name = self._format_name(name)
        tag_str = self._tags_to_str(tags or {})
        key = f"{full_name}:{tag_str}"
        
        self._gauges[key] = value
        
        logger.debug(
            "metric.gauge",
            metric=full_name,
            value=value,
            tags=tags
        )
        
    def histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a histogram value."""
        full_name = self._format_name(name)
        tag_str = self._tags_to_str(tags or {})
        key = f"{full_name}:{tag_str}"
        
        if key not in self._histograms:
            self._histograms[key] = []
        self._histograms[key].append(value)
        
        # Keep last 1000 values
        if len(self._histograms[key]) > 1000:
            self._histograms[key] = self._histograms[key][-1000:]
            
    @contextmanager
    def timer(self, name: str, tags: Dict[str, str] = None):
        """Context manager to time operations."""
        start = time.time()
        try:
            yield
        finally:
            elapsed_ms = (time.time() - start) * 1000
            self.histogram(f"{name}.duration_ms", elapsed_ms, tags)
            
    def _tags_to_str(self, tags: Dict[str, str]) -> str:
        return ",".join(f"{k}={v}" for k, v in sorted(tags.items()))

# Global metrics instance
metrics = MetricsCollector()

def timed(name: str = None, tags: Dict[str, str] = None):
    """Decorator to time function execution."""
    def decorator(func):
        metric_name = name or func.__name__
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with metrics.timer(metric_name, tags):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# lib/brain/health.py
"""
Health check implementation.
"""

from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime, timezone
from enum import Enum
import structlog

logger = structlog.get_logger()

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class ComponentHealth:
    name: str
    status: HealthStatus
    message: Optional[str] = None
    latency_ms: Optional[float] = None
    last_check: datetime = None
    
    def __post_init__(self):
        if self.last_check is None:
            self.last_check = datetime.now(timezone.utc)

class HealthChecker:
    """
    System health checker.
    
    Checks:
    - Firebase connectivity
    - Scoring engine
    - Learning loop state
    - Last successful operations
    """
    
    def __init__(self, firebase_client, config):
        self.firebase = firebase_client
        self.config = config
        
    async def check_all(self) -> Dict[str, ComponentHealth]:
        """Check all components."""
        checks = {}
        
        # Firebase check
        checks["firebase"] = await self._check_firebase()
        
        # Scorer check
        checks["scorer"] = await self._check_scorer()
        
        # Learning loop check
        checks["learning"] = await self._check_learning()
        
        return checks
        
    async def _check_firebase(self) -> ComponentHealth:
        """Check Firebase connectivity."""
        import time
        start = time.time()
        
        try:
            # Simple read operation
            await self.firebase.get("system/brain/health_check")
            latency = (time.time() - start) * 1000
            
            return ComponentHealth(
                name="firebase",
                status=HealthStatus.HEALTHY if latency < 1000 else HealthStatus.DEGRADED,
                latency_ms=latency
            )
        except Exception as e:
            return ComponentHealth(
                name="firebase",
                status=HealthStatus.UNHEALTHY,
                message=str(e)
            )
            
    async def _check_scorer(self) -> ComponentHealth:
        """Check scorer is functional."""
        try:
            # Import and instantiate scorer
            from .scoring import PerformanceScorer
            scorer = PerformanceScorer(self.config)
            
            # Test with mock event
            from .ingest import MarketingEvent, FeedType
            test_event = MarketingEvent(
                event_id="health_check",
                client_id="system",
                feed_type=FeedType.EMAIL,
                timestamp=datetime.now(timezone.utc),
                engagements=100,
                impressions=1000,
                audience_size=5000
            )
            
            import time
            start = time.time()
            score = scorer.score(test_event)
            latency = (time.time() - start) * 1000
            
            return ComponentHealth(
                name="scorer",
                status=HealthStatus.HEALTHY,
                latency_ms=latency
            )
        except Exception as e:
            return ComponentHealth(
                name="scorer",
                status=HealthStatus.UNHEALTHY,
                message=str(e)
            )
            
    async def _check_learning(self) -> ComponentHealth:
        """Check learning loop state."""
        try:
            state = await self.firebase.get("system/brain/learning_state")
            
            if not state:
                return ComponentHealth(
                    name="learning",
                    status=HealthStatus.DEGRADED,
                    message="No learning state found"
                )
            
            # Check if learning is progressing
            last_update = datetime.fromisoformat(state.get("last_update", "2000-01-01"))
            age_hours = (datetime.now(timezone.utc) - last_update).total_seconds() / 3600
            
            if age_hours > 24:
                return ComponentHealth(
                    name="learning",
                    status=HealthStatus.DEGRADED,
                    message=f"Learning state stale ({age_hours:.0f}h old)"
                )
            
            return ComponentHealth(
                name="learning",
                status=HealthStatus.HEALTHY
            )
        except Exception as e:
            return ComponentHealth(
                name="learning",
                status=HealthStatus.UNHEALTHY,
                message=str(e)
            )
```

## 1.1 Configuration (Updated with Secrets)

```python
# lib/brain/config.py
"""
Brain Configuration with secrets management.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class BrainConfig:
    """Configuration for the Brain engine."""
    
    # Model
    model_version: str = "1.0.0"
    
    # Hash salt - MUST come from environment/secrets
    hash_salt: str = field(
        default_factory=lambda: os.environ.get(
            "BRAIN_HASH_SALT",
            None  # Will raise if not set
        )
    )
    
    # Scoring bounds (prevents overflow)
    scoring_max_output: float = 10000.0
    scoring_min_output: float = 0.0
    
    # Quality bounds
    quality_min: float = 0.7
    quality_max: float = 1.3
    
    # Confidence thresholds
    min_confidence_for_prediction: float = 0.6
    min_history_for_growth: int = 2
    min_history_for_reliable_prediction: int = 10
    
    # Anomaly detection
    z_score_outlier: float = 2.0
    z_score_critical: float = 3.0
    min_std_dev: float = 0.001  # Floor for std dev
    
    # Learning bounds (prevents weight explosion)
    weight_min: float = 0.1
    weight_max: float = 10.0
    gradient_clip: float = 0.1
    
    # Rate limits
    ingestion_rate_per_client: int = 1000  # per minute
    ingestion_rate_global: int = 10000     # per minute
    api_rate_per_ip: int = 100             # per minute
    
    # Feature flags path
    feature_flags_path: str = "system/brain/features"
    
    # Feeds
    supported_feeds: List[str] = field(default_factory=lambda: [
        "email", "social_linkedin", "social_twitter",
        "social_instagram", "social_tiktok", "social_youtube",
        "ads_google", "ads_meta", "crm_hubspot", "crm_salesforce"
    ])
    
    def __post_init__(self):
        if not self.hash_salt:
            raise ValueError(
                "BRAIN_HASH_SALT environment variable must be set. "
                "Generate with: python -c 'import secrets; print(secrets.token_hex(32))'"
            )
```

## 1.2 Event Gateway (Updated with All Fixes)

```python
# lib/brain/ingest.py (key sections updated)
"""
Event Gateway and Feed Router - Updated with all fixes.
"""

import hashlib
import hmac
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timezone
from enum import Enum
import structlog

from .exceptions import (
    IngestionError, ValidationError, SecurityError, 
    DuplicateEventError, RateLimitExceeded
)
from .validation import (
    validate_client_id, validate_event_id, validate_raw_data,
    validate_event_data
)
from .retry import retry
from .circuit_breaker import CircuitBreaker
from .rate_limiter import RateLimiter
from .metrics import metrics, timed

logger = structlog.get_logger()

class FeedType(Enum):
    """Data feed categories."""
    EMAIL = "email"
    SOCIAL_LINKEDIN = "social_linkedin"
    SOCIAL_TWITTER = "social_twitter"
    SOCIAL_INSTAGRAM = "social_instagram"
    SOCIAL_TIKTOK = "social_tiktok"
    SOCIAL_YOUTUBE = "social_youtube"
    ADS_GOOGLE = "ads_google"
    ADS_META = "ads_meta"
    CRM_HUBSPOT = "crm_hubspot"
    CRM_SALESFORCE = "crm_salesforce"
    WAREHOUSE = "warehouse"
    CUSTOM = "custom"

@dataclass
class MarketingEvent:
    """Normalized marketing event."""
    event_id: str
    client_id: str
    feed_type: FeedType
    timestamp: datetime
    
    # Core metrics
    engagements: int = 0
    impressions: int = 0
    audience_size: int = 0
    
    # Engagement breakdown
    likes: int = 0
    comments: int = 0
    shares: int = 0
    clicks: int = 0
    
    # Content metadata
    content_id: Optional[str] = None
    content_type: Optional[str] = None
    platform: Optional[str] = None
    vertical: Optional[str] = None
    
    # Hashed identifiers
    creator_hash: Optional[str] = None
    
    # Raw data (size-limited)
    raw_data: Dict = field(default_factory=dict)
    
    # Correlation ID for tracing
    correlation_id: Optional[str] = None

class EventGateway:
    """
    Unified ingestion point with all production hardening.
    """
    
    def __init__(self, firebase_client, config: 'BrainConfig'):
        self.firebase = firebase_client
        self.config = config
        self.feed_router = FeedRouter()
        
        # Rate limiter
        self.rate_limiter = RateLimiter(
            default_capacity=config.ingestion_rate_per_client,
            default_refill_rate=config.ingestion_rate_per_client / 60,
            global_capacity=config.ingestion_rate_global,
            global_refill_rate=config.ingestion_rate_global / 60
        )
        
        # Circuit breaker for Firebase
        self.firebase_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            name="firebase_ingest"
        )
        
    @timed("ingest")
    def ingest(
        self,
        source: str,
        raw_data: Dict,
        client_id: str,
        correlation_id: Optional[str] = None
    ) -> MarketingEvent:
        """
        Ingest raw data from any source into normalized event.
        
        Steps:
        1. Validate inputs
        2. Check rate limits
        3. Generate idempotent event_id
        4. Detect feed type
        5. Normalize to MarketingEvent
        6. Pseudonymize identifiers
        7. Validate event data
        8. Check for duplicates
        9. Persist with retry
        """
        correlation_id = correlation_id or str(uuid.uuid4())
        log = logger.bind(correlation_id=correlation_id, client_id=client_id)
        
        try:
            # 1. Validate inputs
            client_id = validate_client_id(client_id)
            raw_data = validate_raw_data(raw_data)
            
            # 2. Check rate limits
            self.rate_limiter.check_or_raise(f"ingest:{client_id}")
            
            # 3. Generate idempotent event_id from content hash
            event_id = self._generate_event_id(raw_data, client_id)
            
            # 4. Detect feed type
            feed_type = self.feed_router.detect_feed(source, raw_data)
            
            # 5. Normalize
            event = self._normalize(raw_data, feed_type, client_id, event_id)
            event.correlation_id = correlation_id
            
            # 6. Pseudonymize
            event = self._pseudonymize(event)
            
            # 7. Validate event data
            validate_event_data(
                event.engagements,
                event.impressions,
                event.audience_size,
                event.timestamp
            )
            
            # 8. Check for duplicates and persist
            self._persist_idempotent(event)
            
            metrics.increment("ingest.success", tags={"feed_type": feed_type.value})
            log.info("event.ingested", event_id=event.event_id, feed_type=feed_type.value)
            
            return event
            
        except (ValidationError, SecurityError, RateLimitExceeded) as e:
            metrics.increment("ingest.rejected", tags={"reason": e.error_code})
            log.warning("event.rejected", error=str(e))
            raise
        except Exception as e:
            metrics.increment("ingest.error")
            log.error("event.failed", error=str(e))
            raise IngestionError(
                f"Failed to ingest event: {e}",
                context={"source": source, "client_id": client_id},
                cause=e
            )
            
    def _generate_event_id(self, raw_data: Dict, client_id: str) -> str:
        """Generate deterministic event_id for idempotency."""
        import json
        content = json.dumps(raw_data, sort_keys=True, default=str)
        hash_input = f"{client_id}:{content}"
        return f"evt_{hashlib.sha256(hash_input.encode()).hexdigest()[:24]}"
        
    def _normalize(
        self,
        raw: Dict,
        feed_type: FeedType,
        client_id: str,
        event_id: str
    ) -> MarketingEvent:
        """Normalize raw data to MarketingEvent."""
        template = self.feed_router.get_template(feed_type)
        
        # Base event
        event = MarketingEvent(
            event_id=event_id,
            client_id=client_id,
            feed_type=feed_type,
            timestamp=self._parse_timestamp(raw),
            platform=feed_type.value.replace("social_", "").replace("ads_", "").replace("crm_", ""),
            raw_data=raw
        )
        
        # Apply template normalization
        event = template.process(event)
        
        return event
        
    def _parse_timestamp(self, raw: Dict) -> datetime:
        """Parse timestamp from raw data."""
        ts = raw.get("timestamp") or raw.get("created_at") or raw.get("date")
        
        if isinstance(ts, datetime):
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            return ts
        elif isinstance(ts, str):
            try:
                parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                return parsed
            except ValueError:
                pass
        
        # Default to now
        return datetime.now(timezone.utc)
        
    def _pseudonymize(self, event: MarketingEvent) -> MarketingEvent:
        """HMAC-SHA256 hash sensitive identifiers."""
        if event.content_id:
            event.creator_hash = hmac.new(
                self.config.hash_salt.encode(),
                event.content_id.encode(),
                hashlib.sha256
            ).hexdigest()[:16]
        return event
        
    @retry(
        max_attempts=3,
        retryable_exceptions=(IngestionError,)
    )
    def _persist_idempotent(self, event: MarketingEvent):
        """Persist event with idempotency check and circuit breaker."""
        path = f"clients/{event.client_id}/events/{event.event_id}"
        
        with self.firebase_breaker:
            # Transaction for idempotent upsert
            def transaction_fn(transaction, client):
                doc_ref = client.document(path)
                doc = doc_ref.get(transaction=transaction)
                
                if doc.exists:
                    raise DuplicateEventError(
                        f"Event {event.event_id} already exists"
                    )
                
                transaction.set(doc_ref, self._serialize_event(event))
            
            try:
                self.firebase.transaction(transaction_fn)
            except DuplicateEventError:
                # Idempotent - return success
                metrics.increment("ingest.duplicate")
                pass
                
    def _serialize_event(self, event: MarketingEvent) -> Dict:
        """Serialize event for Firebase storage."""
        data = {}
        for key, value in event.__dict__.items():
            if isinstance(value, Enum):
                data[key] = value.value
            elif isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, dict):
                data[key] = value
            else:
                data[key] = value
        data["_ingested_at"] = datetime.now(timezone.utc).isoformat()
        return data
```

## 1.3 Performance Scoring (Updated with Overflow Protection)

```python
# lib/brain/scoring.py (key sections)
"""
Performance Scoring System - Updated with all fixes.
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta
import structlog

from .exceptions import ScoringError
from .metrics import metrics, timed

logger = structlog.get_logger()

@dataclass
class PerformanceScore:
    """Composite performance score with bounds."""
    overall: float
    engagement_ratio: float
    impressions: float
    growth: float
    authenticity: float
    vertical_multiplier: float
    quality_index: float
    temporal_weight: float
    confidence: float
    calculated_at: datetime = None
    model_version: str = "1.0.0"
    
    def __post_init__(self):
        if self.calculated_at is None:
            self.calculated_at = datetime.now(timezone.utc)

class PerformanceScorer:
    """
    Calculates performance scores with BrightMatter methodology.
    Includes overflow protection, timezone safety, and quality checks.
    """
    
    # Platform baselines (unchanged from original)
    PLATFORM_BASELINES = {
        "linkedin": {"engagement_rate": 0.02, "decay_rate": 0.01},
        "twitter": {"engagement_rate": 0.015, "decay_rate": 0.22},
        "instagram": {"engagement_rate": 0.03, "decay_rate": 0.12},
        "tiktok": {"engagement_rate": 0.05, "decay_rate": 0.35},
        "youtube": {"engagement_rate": 0.02, "decay_rate": 0.003},
        "facebook": {"engagement_rate": 0.025, "decay_rate": 0.15},
        "email": {"open_rate": 0.20, "click_rate": 0.025, "decay_rate": 0.5},
    }
    
    VERTICAL_MULTIPLIERS = {
        "b2b_saas": 1.1, "b2b_services": 1.05, "ecommerce": 1.0,
        "d2c": 1.05, "agency": 0.95, "enterprise": 1.15,
    }
    
    def __init__(self, config: 'BrainConfig'):
        self.config = config
        
    @timed("score")
    def score(
        self,
        event: 'MarketingEvent',
        history: List['MarketingEvent'] = None
    ) -> PerformanceScore:
        """
        Calculate composite performance score with overflow protection.
        
        Formula: V' = ((E/F)^0.6 × I^0.4 × G × A) × Mv × Q' × T' × 1000
        """
        try:
            platform = event.platform or "email"
            
            # Calculate components with bounds
            e_over_f = self._calculate_engagement_ratio(event)
            impressions = self._normalize_impressions(event)
            growth = self._calculate_growth(event, history)
            authenticity = self._calculate_authenticity(event)
            mv = self._get_vertical_multiplier(event)
            q_prime = self._calculate_quality_index(event)
            t_prime = self._calculate_temporal_weight(event)
            confidence = self._calculate_confidence(event, history)
            
            # Validate all components are finite and positive
            components = {
                "engagement_ratio": e_over_f,
                "impressions": impressions,
                "growth": growth,
                "authenticity": authenticity,
                "vertical_multiplier": mv,
                "quality_index": q_prime,
                "temporal_weight": t_prime,
            }
            
            for name, value in components.items():
                if not math.isfinite(value) or value <= 0:
                    logger.warning(
                        "score.invalid_component",
                        component=name,
                        value=value,
                        event_id=event.event_id
                    )
                    # Use safe default
                    components[name] = 1.0
                    confidence *= 0.5  # Reduce confidence
            
            # Safe calculation
            try:
                v_prime = (
                    (components["engagement_ratio"] ** 0.6) *
                    (components["impressions"] ** 0.4) *
                    components["growth"] *
                    components["authenticity"] *
                    components["vertical_multiplier"] *
                    components["quality_index"] *
                    components["temporal_weight"] *
                    1000
                )
                
                # Clamp to bounds
                v_prime = max(
                    self.config.scoring_min_output,
                    min(self.config.scoring_max_output, v_prime)
                )
                
            except (OverflowError, ValueError) as e:
                logger.error(
                    "score.overflow",
                    error=str(e),
                    event_id=event.event_id
                )
                v_prime = 0.0
                confidence = 0.1
            
            metrics.increment("score.calculated", tags={"platform": platform})
            
            return PerformanceScore(
                overall=v_prime,
                engagement_ratio=components["engagement_ratio"],
                impressions=components["impressions"],
                growth=components["growth"],
                authenticity=components["authenticity"],
                vertical_multiplier=components["vertical_multiplier"],
                quality_index=components["quality_index"],
                temporal_weight=components["temporal_weight"],
                confidence=confidence,
                model_version=self.config.model_version
            )
            
        except Exception as e:
            logger.error("score.failed", error=str(e), event_id=event.event_id)
            raise ScoringError(
                f"Failed to calculate score: {e}",
                context={"event_id": event.event_id},
                cause=e
            )
            
    def _calculate_engagement_ratio(self, event: 'MarketingEvent') -> float:
        """Calculate normalized E/F ratio with safety."""
        platform = event.platform or "email"
        baseline = self.PLATFORM_BASELINES.get(platform, {})
        baseline_rate = baseline.get("engagement_rate", 0.02)
        
        total_engagements = event.engagements or (
            event.likes + event.comments + event.shares + event.clicks
        )
        audience = max(event.audience_size, 1)
        
        raw_rate = total_engagements / audience
        normalized = raw_rate / max(baseline_rate, 0.001)
        
        # Cap to prevent outliers
        return min(3.0, max(0.01, normalized))
        
    def _normalize_impressions(self, event: 'MarketingEvent') -> float:
        """Normalize impressions with log compression and safety."""
        impressions = max(event.impressions, 1)
        audience = event.audience_size
        
        if audience < 1000:
            median = 100
        elif audience < 10000:
            median = 1000
        elif audience < 100000:
            median = 10000
        else:
            median = 50000
            
        # Safe log
        ratio = impressions / max(median, 1)
        ratio = max(ratio, 1e-10)  # Prevent log(0)
        
        try:
            normalized = math.log10(ratio)
        except (ValueError, OverflowError):
            normalized = 0.0
            
        return min(3.0, max(0.1, normalized + 1.5))
        
    def _calculate_growth(
        self,
        event: 'MarketingEvent',
        history: List['MarketingEvent'] = None
    ) -> float:
        """Calculate growth momentum with timezone safety."""
        if not history or len(history) < self.config.min_history_for_growth:
            return 1.0
            
        # Ensure timezone-aware
        now = datetime.now(timezone.utc)
        
        def ensure_tz(ts):
            if ts.tzinfo is None:
                return ts.replace(tzinfo=timezone.utc)
            return ts
            
        sorted_history = sorted(history, key=lambda e: ensure_tz(e.timestamp))
        
        week_ago = now - timedelta(days=7)
        recent = [e for e in sorted_history if ensure_tz(e.timestamp) > week_ago]
        
        month_ago = now - timedelta(days=30)
        historical = [e for e in sorted_history if ensure_tz(e.timestamp) > month_ago]
        
        if not recent or not historical:
            return 1.0
            
        recent_avg = sum(e.engagements for e in recent) / max(len(recent), 1)
        historical_avg = sum(e.engagements for e in historical) / max(len(historical), 1)
        
        if historical_avg == 0:
            return 1.0
            
        growth = recent_avg / historical_avg
        return min(2.0, max(0.5, growth))
        
    def _calculate_authenticity(self, event: 'MarketingEvent') -> float:
        """Calculate authenticity factor."""
        raw = event.raw_data
        
        bot_ratio = raw.get("bot_ratio", 0)
        if bot_ratio == 0 and event.engagements > 0:
            velocity = raw.get("engagement_velocity_per_minute", 0)
            if velocity > 100:
                bot_ratio = 0.2
                
        coord_ratio = raw.get("coordinated_ratio", 0)
        
        first_minute_pct = raw.get("first_minute_engagement_pct", 0)
        temporal_penalty = 0.3 if first_minute_pct > 0.7 else 0
        
        a = 1 - 0.5 * bot_ratio - 0.4 * coord_ratio - 0.3 * temporal_penalty
        return max(0.3, a)
        
    def _get_vertical_multiplier(self, event: 'MarketingEvent') -> float:
        """Get vertical multiplier."""
        vertical = event.vertical or "b2b_saas"
        return self.VERTICAL_MULTIPLIERS.get(vertical, 1.0)
        
    def _calculate_quality_index(self, event: 'MarketingEvent') -> float:
        """Calculate quality index Q' bounded [0.7, 1.3]."""
        raw = event.raw_data
        
        sentiment = raw.get("sentiment_score", 0.5)
        consistency = raw.get("consistency_score", 0.7)
        relevance = raw.get("relevance_score", 0.6)
        
        # Weighted sum
        q = 0.4 * sentiment + 0.3 * consistency + 0.3 * relevance
        
        # Map [0,1] to [0.7, 1.3]
        q_prime = 0.7 + (q * 0.6)
        return max(self.config.quality_min, min(self.config.quality_max, q_prime))
        
    def _calculate_temporal_weight(self, event: 'MarketingEvent') -> float:
        """Calculate temporal decay with timezone safety."""
        platform = event.platform or "email"
        baseline = self.PLATFORM_BASELINES.get(platform, {})
        decay_rate = baseline.get("decay_rate", 0.1)
        
        now = datetime.now(timezone.utc)
        event_time = event.timestamp
        if event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=timezone.utc)
            
        hours_elapsed = max(0, (now - event_time).total_seconds() / 3600)
        
        t_prime = math.exp(-decay_rate * hours_elapsed)
        return max(0.1, t_prime)
        
    def _calculate_confidence(
        self,
        event: 'MarketingEvent',
        history: List['MarketingEvent'] = None
    ) -> float:
        """Calculate confidence with quality checks."""
        confidence = 0.0
        
        # Completeness checks
        if event.engagements >= 0:
            confidence += 0.15
        if event.impressions >= 0:
            confidence += 0.15
        if event.audience_size > 0:
            confidence += 0.15
        if event.platform:
            confidence += 0.1
        if event.vertical:
            confidence += 0.1
            
        # Quality checks
        if event.audience_size > 0:
            rate = event.engagements / event.audience_size
            if 0.0001 <= rate <= 0.5:
                confidence += 0.15
                
        if event.impressions < 10**9:
            confidence += 0.1
            
        # History bonus
        if history and len(history) >= 10:
            confidence += 0.1
            
        return min(1.0, confidence)
```

---

# PHASE 2: Learning & Intelligence (Weeks 4-5)

## 2.1 Learning Loop (Updated with All Fixes)

```python
# lib/brain/learning.py (key sections)
"""
Compound Learning System - Updated with all fixes.
"""

import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta
import structlog

from .exceptions import LearningError, ConcurrencyError
from .validation import validate_outcome_timestamps
from .retry import retry
from .circuit_breaker import CircuitBreaker
from .metrics import metrics, timed

logger = structlog.get_logger()

@dataclass
class LearningState:
    """Persisted learning state with version for optimistic locking."""
    weights: Dict[str, float]
    iteration: int
    model_version: str
    last_update: datetime
    version: int = 0  # For optimistic locking
    shadow_candidate: Optional[Dict] = None
    ema_error: float = 0.0  # Exponential moving average error

class LearningLoop:
    """
    Compound learning system with all production hardening.
    """
    
    DEFAULT_WEIGHTS = {
        "engagement": 1.0, "impressions": 1.0, "growth": 1.0,
        "authenticity": 1.0, "quality": 1.0, "temporal": 1.0,
    }
    
    BASE_LEARNING_RATE = 0.01
    MIN_LEARNING_RATE = 0.001
    MIN_IMPROVEMENT_FOR_PROMOTION = 0.03
    MIN_OBSERVATIONS_FOR_PROMOTION = 500  # Increased for statistical power
    ERROR_THRESHOLD_FOR_SHADOW = 0.15
    EMA_ALPHA = 0.01
    
    def __init__(self, firebase_client, config: 'BrainConfig'):
        self.firebase = firebase_client
        self.config = config
        self._state_lock = threading.Lock()  # Thread safety
        self._state: Optional[LearningState] = None
        
        self.firebase_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            name="firebase_learning"
        )
        
    @property
    def state(self) -> LearningState:
        """Get current state, loading if needed."""
        if self._state is None:
            self._state = self._load_state()
        return self._state
        
    @retry(max_attempts=3)
    def _load_state(self) -> LearningState:
        """Load learning state from Firebase."""
        try:
            with self.firebase_breaker:
                doc = self.firebase.get("system/brain/learning_state")
            
            if doc:
                return LearningState(
                    weights=doc.get("weights", self.DEFAULT_WEIGHTS.copy()),
                    iteration=doc.get("iteration", 0),
                    model_version=doc.get("model_version", self.config.model_version),
                    last_update=datetime.fromisoformat(
                        doc.get("last_update", datetime.now(timezone.utc).isoformat())
                    ),
                    version=doc.get("version", 0),
                    shadow_candidate=doc.get("shadow_candidate"),
                    ema_error=doc.get("ema_error", 0.0)
                )
        except Exception:
            pass
            
        return LearningState(
            weights=self.DEFAULT_WEIGHTS.copy(),
            iteration=0,
            model_version=self.config.model_version,
            last_update=datetime.now(timezone.utc)
        )
        
    def _save_state(self):
        """Persist state with optimistic locking."""
        state_dict = {
            "weights": self._state.weights,
            "iteration": self._state.iteration,
            "model_version": self._state.model_version,
            "last_update": self._state.last_update.isoformat(),
            "version": self._state.version + 1,
            "shadow_candidate": self._state.shadow_candidate,
            "ema_error": self._state.ema_error,
        }
        
        def transaction_fn(transaction, client):
            doc_ref = client.document("system/brain/learning_state")
            doc = doc_ref.get(transaction=transaction)
            
            if doc.exists:
                current_version = doc.to_dict().get("version", 0)
                if current_version != self._state.version:
                    raise ConcurrencyError(
                        "Learning state was modified by another process",
                        context={
                            "expected_version": self._state.version,
                            "current_version": current_version
                        }
                    )
            
            transaction.set(doc_ref, state_dict)
        
        with self.firebase_breaker:
            self.firebase.transaction(transaction_fn)
            
        self._state.version += 1
        
        # Also save to history
        self.firebase.set(
            f"system/brain/learning_history/{self._state.iteration}",
            state_dict
        )
        
    @timed("record_outcome")
    def record_outcome(self, outcome: 'Outcome'):
        """
        Record outcome and update weights with full safety.
        """
        # Validate timestamps
        validate_outcome_timestamps(
            outcome.prediction_timestamp,
            outcome.observation_timestamp
        )
        
        with self._state_lock:  # Thread safety
            eta = self._adaptive_learning_rate()
            
            # Update weights with bounds
            for metric, delta in outcome.delta.items():
                if metric in self._state.weights:
                    # Gradient clipping
                    adjustment = eta * outcome.move_weight * delta
                    adjustment = max(
                        -self.config.gradient_clip,
                        min(self.config.gradient_clip, adjustment)
                    )
                    
                    self._state.weights[metric] += adjustment
                    
                    # Weight bounds
                    self._state.weights[metric] = max(
                        self.config.weight_min,
                        min(self.config.weight_max, self._state.weights[metric])
                    )
                    
            # EMA error tracking (instead of cumulative)
            error = sum(abs(d) for d in outcome.delta.values()) / max(len(outcome.delta), 1)
            self._state.ema_error = (
                self.EMA_ALPHA * error + 
                (1 - self.EMA_ALPHA) * self._state.ema_error
            )
            
            self._state.iteration += 1
            self._state.last_update = datetime.now(timezone.utc)
            
            # Check for shadow mode every 50 iterations
            if self._state.iteration % 50 == 0:
                self._evaluate_for_shadow_mode()
                
            self._save_state()
            
        # Persist outcome
        self._persist_outcome(outcome)
        
        metrics.increment("learning.outcome_recorded")
        metrics.gauge("learning.ema_error", self._state.ema_error)
        
    def _adaptive_learning_rate(self) -> float:
        """Adaptive learning rate with floor."""
        decay_factor = 1.0 / (1.0 + 0.001 * self._state.iteration)
        eta = self.BASE_LEARNING_RATE * decay_factor
        
        # Floor to prevent freeze
        eta = max(self.MIN_LEARNING_RATE, eta)
        
        # Shock detection: increase if recent error spike
        if self._state.ema_error > self.ERROR_THRESHOLD_FOR_SHADOW * 1.5:
            eta = min(self.BASE_LEARNING_RATE, eta * 3)
            
        return eta
        
    def _evaluate_for_shadow_mode(self):
        """Spawn shadow candidate if performance degraded."""
        if self._state.ema_error > self.ERROR_THRESHOLD_FOR_SHADOW:
            if not self._state.shadow_candidate:
                self._state.shadow_candidate = {
                    "version": f"shadow_{self._state.iteration}",
                    "weights": self._generate_candidate_weights(),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "status": "testing",
                    "baseline_error": self._state.ema_error,
                }
                logger.info(
                    "shadow.created",
                    version=self._state.shadow_candidate["version"]
                )
                
    def _generate_candidate_weights(self) -> Dict[str, float]:
        """Generate candidate using error analysis, not random noise."""
        # Analyze error contribution by metric
        error_analysis = self._analyze_error_by_metric()
        
        candidate = {}
        for key, value in self._state.weights.items():
            # Adjust in direction opposite to error
            error_contribution = error_analysis.get(key, 0)
            direction = -1 if error_contribution > 0 else 1
            magnitude = min(0.1, abs(error_contribution) * 0.5)
            candidate[key] = value * (1 + direction * magnitude)
            
            # Bound candidate weights
            candidate[key] = max(
                self.config.weight_min,
                min(self.config.weight_max, candidate[key])
            )
            
        return candidate
        
    def _analyze_error_by_metric(self) -> Dict[str, float]:
        """Analyze error contribution by metric (placeholder)."""
        # In production, this would analyze recent outcomes
        return {k: 0.0 for k in self.DEFAULT_WEIGHTS}
        
    @retry(max_attempts=3)
    def _persist_outcome(self, outcome: 'Outcome'):
        """Persist outcome to Firebase."""
        with self.firebase_breaker:
            self.firebase.set(
                f"clients/{outcome.client_id}/brain/outcomes/{outcome.outcome_id}",
                {
                    "recommendation_id": outcome.recommendation_id,
                    "event_id": outcome.event_id,
                    "predicted": outcome.predicted,
                    "observed": outcome.observed,
                    "delta": outcome.delta,
                    "move_type": outcome.move_type,
                    "prediction_timestamp": outcome.prediction_timestamp.isoformat(),
                    "observation_timestamp": outcome.observation_timestamp.isoformat(),
                }
            )
```

## 2.2 Recommendation Engine (Updated with Exploration)

```python
# lib/brain/recommendations.py (key sections)
"""
Recommendation Engine - Updated with exploration to prevent echo chambers.
"""

import random
from typing import List, Set
from collections import Counter

class RecommendationEngine:
    """
    NBM generator with exploration mechanism.
    """
    
    EXPLORATION_RATE = 0.15  # 15% exploration
    
    # Fix trigger comparison operators
    def _check_triggers(
        self,
        score: 'PerformanceScore',
        context: Dict,
        triggers: Dict
    ) -> bool:
        """Check if triggers are met with correct operators."""
        for trigger, threshold in triggers.items():
            if trigger.endswith("_below"):
                metric = trigger.replace("_below", "")
                value = getattr(score, metric, None) or context.get(metric, 0)
                # FIX: Use > not >= for "below" (value should be <= threshold)
                if value > threshold:
                    return False
            elif trigger.endswith("_above"):
                metric = trigger.replace("_above", "")
                value = getattr(score, metric, None) or context.get(metric, 0)
                # FIX: Use < not <= for "above" (value should be >= threshold)
                if value < threshold:
                    return False
            elif trigger in context:
                if context[trigger] != threshold:
                    return False
        return True
        
    def generate(
        self,
        client_id: str,
        score: 'PerformanceScore',
        analysis_context: Dict,
        limit: int = 5
    ) -> List['Recommendation']:
        """
        Generate recommendations with exploration.
        """
        candidates = []
        triggered_codes: Set[ReasonCode] = set()
        
        # Generate exploitation candidates
        for reason_code, triggers in self.TRIGGERS.items():
            if self._check_triggers(score, analysis_context, triggers):
                triggered_codes.add(reason_code)
                recs = self._create_recommendations(
                    client_id, reason_code, score, analysis_context
                )
                candidates.extend(recs)
                
        # Add validation move if uncertainty high
        if score.confidence < self.config.min_confidence_for_prediction:
            validation = self._create_validation_move(client_id, score)
            candidates.append(validation)
            
        # Score and rank exploitation candidates
        scored = [(r, self._score_recommendation(r, score)) for r in candidates]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Split between exploitation and exploration
        exploit_count = int(limit * (1 - self.EXPLORATION_RATE))
        explore_count = limit - exploit_count
        
        exploit_recs = [r for r, _ in scored[:exploit_count]]
        
        # Exploration: sample from untriggered reason codes
        explore_recs = []
        untriggered = set(ReasonCode) - triggered_codes
        if untriggered and explore_count > 0:
            explore_codes = random.sample(
                list(untriggered), 
                min(explore_count, len(untriggered))
            )
            for code in explore_codes:
                recs = self._create_recommendations(
                    client_id, code, score, analysis_context
                )
                if recs:
                    rec = recs[0]
                    rec.move_type = MoveType.SELF_GENERATED  # Lower weight
                    explore_recs.append(rec)
                    
        final = exploit_recs + explore_recs[:explore_count]
        
        metrics.increment("recommendations.generated", tags={"count": str(len(final))})
        
        return final[:limit]
        
    def _score_recommendation(
        self,
        rec: 'Recommendation',
        score: 'PerformanceScore'
    ) -> float:
        """Score with normalized components and freshness decay."""
        # Normalize to 0-1 range
        priority_normalized = {
            Priority.CRITICAL: 1.0, Priority.HIGH: 0.75,
            Priority.MEDIUM: 0.5, Priority.LOW: 0.25
        }[rec.priority]
        
        effort_normalized = {
            Effort.LOW: 1.0, Effort.MEDIUM: 0.6, Effort.HIGH: 0.3
        }[rec.effort]
        
        confidence_normalized = rec.confidence
        
        # Freshness decay
        age_hours = (datetime.now(timezone.utc) - rec.created_at).total_seconds() / 3600
        max_age_hours = 7 * 24
        freshness = 1 - (age_hours / max_age_hours) * 0.5
        freshness = max(0.5, freshness)
        
        # Weighted combination
        base_score = (
            0.35 * priority_normalized +
            0.25 * effort_normalized +
            0.25 * confidence_normalized +
            0.15 * freshness
        )
        
        # Bonus for validation when uncertain
        if rec.move_type == MoveType.VALIDATION and score.confidence < 0.6:
            base_score += 0.1
            
        return base_score
```

---

# PHASE 3: Automation & Integration (Weeks 6-7)

## 3.1 Scheduler Configuration (Updated with Jitter and DLQ)

```yaml
# config/brain_scheduler.yaml
scheduler:
  provider: firebase_cloud_functions
  timezone: "UTC"
  
jobs:
  hourly_scores:
    function: "brainHourlyScores"
    schedule: "0 * * * *"
    timeout_seconds: 300
    memory: "512MB"  # Increased for large clients
    jitter_seconds: 300  # Spread over 5 minutes
    
  daily_analysis:
    function: "brainDailyAnalysis"
    schedule: "0 6 * * *"
    timeout_seconds: 600
    memory: "512MB"
    jitter_seconds: 600
    
  weekly_recommendations:
    function: "brainWeeklyReport"
    schedule: "0 9 * * 1"
    timeout_seconds: 900
    memory: "1GB"  # Large for comprehensive reports
    jitter_seconds: 900

error_handling:
  retry_policy:
    max_retries: 3
    initial_delay_seconds: 60
    max_delay_seconds: 3600
    multiplier: 2.0
    
  dead_letter:
    collection: "system/brain/dead_letter_queue"
    retention_days: 30
    
  circuit_breaker:
    failure_threshold: 5
    recovery_timeout_seconds: 60
    
  alerts:
    - type: "pagerduty"
      severity: "critical"
      on: ["circuit_open", "max_retries_exceeded"]
    - type: "slack"
      channel: "#mh1-alerts"
      on: ["failure", "timeout", "degraded"]
```

## 3.2 Firebase Security Rules

```javascript
// config/firestore.rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Helper functions
    function isAuthenticated() {
      return request.auth != null;
    }
    
    function isServiceAccount() {
      return request.auth != null && request.auth.token.is_service_account == true;
    }
    
    function hasClientAccess(clientId) {
      return request.auth != null && (
        request.auth.token.client_ids.hasAny([clientId]) ||
        request.auth.token.is_admin == true
      );
    }
    
    function isValidEvent() {
      let data = request.resource.data;
      return data.keys().hasAll(['event_id', 'client_id', 'feed_type', 'timestamp'])
        && data.engagements is number
        && data.engagements >= 0
        && data.impressions is number
        && data.impressions >= 0;
    }
    
    // System data - service accounts only
    match /system/{document=**} {
      allow read: if isServiceAccount();
      allow write: if isServiceAccount();
    }
    
    // Client data - authorized users only
    match /clients/{clientId}/{document=**} {
      allow read: if hasClientAccess(clientId);
      allow write: if hasClientAccess(clientId);
    }
    
    // Events with validation
    match /clients/{clientId}/events/{eventId} {
      allow create: if hasClientAccess(clientId) && isValidEvent();
      allow update: if hasClientAccess(clientId);
      allow delete: if isServiceAccount();  // Only service can delete
    }
    
    // Learning state - service only
    match /system/brain/learning_state {
      allow read, write: if isServiceAccount();
    }
    
    // Gold standards - read by service, write by admin
    match /system/brain/gold_standards/{document=**} {
      allow read: if isServiceAccount();
      allow write: if request.auth.token.is_admin == true;
    }
  }
}
```

## 3.3 API Endpoints (Updated with Auth and Rate Limiting)

```typescript
// ui/app/api/brain/health/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const healthChecker = getHealthChecker();
  const checks = await healthChecker.checkAll();
  
  const overall = Object.values(checks).every(
    c => c.status === 'healthy'
  ) ? 'healthy' : 'degraded';
  
  return NextResponse.json({
    status: overall,
    components: checks,
    timestamp: new Date().toISOString(),
  }, {
    status: overall === 'healthy' ? 200 : 503
  });
}

// ui/lib/middleware.ts
import { NextRequest, NextResponse } from 'next/server';
import { verifyAuth } from './auth';
import { rateLimit } from './rate-limit';

const RATE_LIMIT = 100; // per minute
const CLIENT_ID_REGEX = /^[a-zA-Z0-9_-]{1,64}$/;

export function withProtection(
  handler: (
    request: NextRequest,
    context: { params: any; user: any }
  ) => Promise<NextResponse>
) {
  return async (request: NextRequest, context: { params: any }) => {
    // 1. Rate limiting
    const ip = request.ip ?? 'anonymous';
    const { success: rateLimitOk } = await rateLimit.check(RATE_LIMIT, ip);
    if (!rateLimitOk) {
      return NextResponse.json(
        { error: 'Rate limit exceeded' },
        { status: 429 }
      );
    }
    
    // 2. Authentication
    const authResult = await verifyAuth(request);
    if (!authResult.authenticated) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }
    
    // 3. Client ID validation (if present)
    const clientId = context.params?.clientId;
    if (clientId) {
      if (!CLIENT_ID_REGEX.test(clientId)) {
        return NextResponse.json(
          { error: 'Invalid client ID format' },
          { status: 400 }
        );
      }
      
      // 4. Authorization
      if (!authResult.user.clientIds.includes(clientId)) {
        return NextResponse.json(
          { error: 'Forbidden' },
          { status: 403 }
        );
      }
    }
    
    return handler(request, { ...context, user: authResult.user });
  };
}

// ui/app/api/brain/[clientId]/scores/route.ts
import { withProtection } from '@/lib/middleware';

export const GET = withProtection(async (request, { params, user }) => {
  const { clientId } = params;
  
  const scores = await getLatestScores(clientId);
  
  return NextResponse.json({
    clientId,
    scores,
    generatedAt: new Date().toISOString(),
  });
});
```

---

# Implementation Checklist (Updated)

## Phase 1 (Weeks 1-3)
- [ ] **Week 1: Infrastructure**
  - [ ] Create `lib/brain/exceptions.py`
  - [ ] Create `lib/brain/retry.py` and `circuit_breaker.py`
  - [ ] Create `lib/brain/rate_limiter.py`
  - [ ] Create `lib/brain/validation.py`
  - [ ] Create `lib/brain/metrics.py` and `health.py`
  - [ ] Set up structured logging with structlog
  
- [ ] **Week 2: Core Engine**
  - [ ] Create `lib/brain/config.py` (with secrets)
  - [ ] Create `lib/brain/ingest.py` (with all fixes)
  - [ ] Create `lib/brain/scoring.py` (with overflow protection)
  - [ ] Create `lib/brain/templates.py`
  - [ ] Create `lib/brain/anomaly.py`
  
- [ ] **Week 3: Integration**
  - [ ] Create Firebase schema
  - [ ] Deploy `config/firestore.rules`
  - [ ] Unit tests for all Phase 1 components
  - [ ] Integration tests with Firebase

## Phase 2 (Weeks 4-5)
- [ ] **Week 4: Learning**
  - [ ] Create `lib/brain/learning.py` (with bounds + locking)
  - [ ] Create gold standard datasets
  - [ ] Implement GoldStandardValidator
  
- [ ] **Week 5: Intelligence**
  - [ ] Create `lib/brain/predictions.py`
  - [ ] Create `lib/brain/recommendations.py` (with exploration)
  - [ ] Unit tests for all Phase 2 components

## Phase 3 (Weeks 6-7)
- [ ] **Week 6: Automation**
  - [ ] Create `lib/brain/reporting.py` (with pagination)
  - [ ] Create `lib/brain/delivery.py` (with retries)
  - [ ] Deploy `config/brain_scheduler.yaml`
  - [ ] Implement Cloud Functions
  
- [ ] **Week 7: Integration**
  - [ ] Create UI API endpoints (with auth + rate limiting)
  - [ ] Create health endpoint
  - [ ] Update existing skills for Brain integration
  - [ ] End-to-end tests
  - [ ] Documentation

---

# Risk Mitigation Summary

| Risk | Mitigation | Status |
|------|------------|--------|
| Race conditions | Thread locks + Firebase transactions | ✅ Addressed |
| Float overflow | Bounds checking + clamping | ✅ Addressed |
| Division by zero | Min values + guards | ✅ Addressed |
| Path traversal | Input validation + regex | ✅ Addressed |
| Weight explosion | Gradient clipping + bounds | ✅ Addressed |
| Memory leaks | Bounded buffers + pagination | ✅ Addressed |
| Echo chambers | Exploration mechanism | ✅ Addressed |
| Firebase quota | Batching + rate limiting | ✅ Addressed |
| Security holes | Auth + Firestore rules | ✅ Addressed |
| Observability gaps | Metrics + health checks | ✅ Addressed |

---

# Appendix: Files to Create

1. `lib/brain/__init__.py` - Public exports
2. `lib/brain/exceptions.py` - Exception hierarchy
3. `lib/brain/config.py` - Configuration
4. `lib/brain/types.py` - Type definitions
5. `lib/brain/validation.py` - Input validation
6. `lib/brain/retry.py` - Retry decorators
7. `lib/brain/circuit_breaker.py` - Circuit breaker
8. `lib/brain/rate_limiter.py` - Rate limiting
9. `lib/brain/cache.py` - Caching layer
10. `lib/brain/metrics.py` - Telemetry
11. `lib/brain/health.py` - Health checks
12. `lib/brain/engine.py` - Main orchestrator
13. `lib/brain/ingest.py` - Event gateway
14. `lib/brain/scoring.py` - Performance scorer
15. `lib/brain/templates.py` - Processing templates
16. `lib/brain/anomaly.py` - Anomaly detector
17. `lib/brain/learning.py` - Learning loop
18. `lib/brain/predictions.py` - Prediction engine
19. `lib/brain/recommendations.py` - NBM generator
20. `lib/brain/reporting.py` - Report engine
21. `lib/brain/delivery.py` - Report delivery
22. `config/brain_scheduler.yaml` - Scheduler config
23. `config/brain_benchmarks.yaml` - Gold standards
24. `config/brain_features.yaml` - Feature flags
25. `config/brain_slos.yaml` - SLI/SLO definitions
26. `config/firestore.rules` - Security rules
27. `ui/app/api/brain/health/route.ts` - Health endpoint
28. `ui/app/api/brain/[clientId]/scores/route.ts` - Scores API
29. `ui/app/api/brain/[clientId]/predictions/route.ts` - Predictions API
30. `ui/app/api/brain/[clientId]/recommendations/route.ts` - NBM API
31. `ui/lib/middleware.ts` - Auth + rate limiting

---

**Total Estimated Effort:** 7 weeks (expanded from 6 due to infrastructure additions)

**Critical Dependencies:**
1. Firebase project with Firestore enabled
2. Secret Manager for `BRAIN_HASH_SALT`
3. Cloud Functions deployment pipeline
4. Structured logging infrastructure

**Go/No-Go Criteria:**
- All critical issues addressed
- Unit test coverage > 80%
- Integration tests pass
- Security rules deployed
- Health check returns healthy
