"""
Working Memory Module for MH1 Intelligence System

This module provides fast, in-memory storage for the current session's
predictions, outcomes, and contextual data. Unlike episodic or semantic
memory which persist to Firebase, working memory is volatile and exists
only for the duration of a session.

Working memory serves as the "scratch pad" for the intelligence system:
- Holds active predictions awaiting outcome resolution
- Maintains a sliding window of recent outcomes for pattern matching
- Stores arbitrary session context for cross-component communication

Thread Safety:
    All operations are protected by an RLock to ensure thread-safe access
    in multi-threaded environments (e.g., async task processing).

Typical Usage:
    >>> from lib.intelligence.memory.working import WorkingMemory
    >>> wm = WorkingMemory()
    >>> pred_id = wm.register_prediction(my_prediction)
    >>> # ... later, when outcome is observed ...
    >>> episodic = wm.complete_prediction(pred_id, observed_outcome)
"""

import threading
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..types import EpisodicMemory, Outcome, Prediction


@dataclass
class WorkingMemoryConfig:
    """
    Configuration for working memory limits.
    
    Attributes:
        max_recent_outcomes: Maximum number of recent outcomes to retain
            in the FIFO queue. Older outcomes are evicted when limit is reached.
        max_active_predictions: Maximum number of predictions that can be
            awaiting outcomes simultaneously. Oldest predictions are evicted
            when limit is reached.
    """
    max_recent_outcomes: int = 10
    max_active_predictions: int = 5


class WorkingMemory:
    """
    Session-scoped working memory for the MH1 intelligence system.
    
    Working memory provides fast, volatile storage for:
    - Active predictions awaiting outcome resolution
    - Recent outcomes for pattern matching and learning
    - Arbitrary session context data
    
    This memory layer is NOT persisted to Firebase and is lost when the
    session ends. For persistent storage, completed predictions should
    be written to episodic memory via the MemoryManager.
    
    Thread Safety:
        All public methods are thread-safe, protected by an RLock.
        Multiple threads can safely register predictions and record
        outcomes concurrently.
    
    Example:
        >>> config = WorkingMemoryConfig(max_recent_outcomes=20)
        >>> wm = WorkingMemory(config)
        >>> 
        >>> # Register a prediction
        >>> pred_id = wm.register_prediction(prediction)
        >>> 
        >>> # Store session context
        >>> wm.set_context("current_client", "acme-corp")
        >>> 
        >>> # Later, complete the prediction with observed outcome
        >>> episodic = wm.complete_prediction(pred_id, outcome)
        >>> 
        >>> # Query recent outcomes for a skill
        >>> recent = wm.get_recent_outcomes(skill_name="email-optimizer")
    """
    
    def __init__(self, config: Optional[WorkingMemoryConfig] = None):
        """
        Initialize working memory with optional configuration.
        
        Args:
            config: Configuration for memory limits. If None, uses defaults
                (10 recent outcomes, 5 active predictions).
        """
        self._config = config or WorkingMemoryConfig()
        self._lock = threading.RLock()
        
        # Active predictions awaiting outcomes, keyed by prediction_id
        self._active_predictions: Dict[str, Prediction] = {}
        
        # FIFO queue of recent completed outcomes (EpisodicMemory instances)
        self._recent_outcomes: deque = deque(maxlen=self._config.max_recent_outcomes)
        
        # Arbitrary session context data
        self._session_context: Dict[str, Any] = {}
        
        # Track registration order for eviction (oldest first)
        self._prediction_order: deque = deque()
    
    def register_prediction(self, prediction: Prediction) -> str:
        """
        Store a prediction awaiting outcome resolution.
        
        If the maximum number of active predictions is reached, the oldest
        prediction is evicted to make room for the new one.
        
        Args:
            prediction: The prediction to register. Should have all required
                fields populated (skill_name, tenant_id, expected values, etc.)
        
        Returns:
            The prediction_id assigned to this prediction. Use this ID to
            retrieve or complete the prediction later.
        
        Example:
            >>> pred = Prediction(
            ...     skill_name="email-optimizer",
            ...     tenant_id="acme-corp",
            ...     expected_signal=0.25,
            ...     expected_baseline=0.20,
            ...     ...
            ... )
            >>> pred_id = wm.register_prediction(pred)
        """
        with self._lock:
            prediction_id = prediction.prediction_id or str(uuid.uuid4())
            
            # Evict oldest if at capacity
            while len(self._active_predictions) >= self._config.max_active_predictions:
                if self._prediction_order:
                    oldest_id = self._prediction_order.popleft()
                    self._active_predictions.pop(oldest_id, None)
                else:
                    # Fallback: remove arbitrary prediction if order tracking is empty
                    if self._active_predictions:
                        oldest_id = next(iter(self._active_predictions))
                        del self._active_predictions[oldest_id]
                    break
            
            # Update prediction with assigned ID if not set
            if not prediction.prediction_id:
                # Create a new prediction with the ID set
                prediction = Prediction(
                    prediction_id=prediction_id,
                    skill_name=prediction.skill_name,
                    tenant_id=prediction.tenant_id,
                    context=prediction.context,
                    expected_signal=prediction.expected_signal,
                    expected_baseline=prediction.expected_baseline,
                    confidence=prediction.confidence,
                    confidence_interval=prediction.confidence_interval,
                    domain=prediction.domain,
                    patterns_used=prediction.patterns_used,
                    is_exploration=prediction.is_exploration,
                    created_at=prediction.created_at,
                )
            
            self._active_predictions[prediction_id] = prediction
            self._prediction_order.append(prediction_id)
            
            return prediction_id
    
    def get_prediction(self, prediction_id: str) -> Optional[Prediction]:
        """
        Retrieve an active prediction by its ID.
        
        Args:
            prediction_id: The ID returned from register_prediction().
        
        Returns:
            The Prediction if found, None if not found or already completed.
        """
        with self._lock:
            return self._active_predictions.get(prediction_id)
    
    def complete_prediction(
        self, 
        prediction_id: str, 
        outcome: Outcome
    ) -> Optional[EpisodicMemory]:
        """
        Complete a prediction with an observed outcome.
        
        This method:
        1. Removes the prediction from active predictions
        2. Calculates the prediction error
        3. Creates an EpisodicMemory record
        4. Adds the record to recent outcomes
        5. Returns the EpisodicMemory for optional persistence
        
        Prediction Error Calculation:
            error = (observed_signal / observed_baseline) - (expected_signal / expected_baseline)
            
            A positive error means the actual result exceeded the prediction.
            A negative error means the actual result fell short.
        
        Args:
            prediction_id: The ID of the prediction to complete.
            outcome: The observed outcome with actual signal and baseline values.
        
        Returns:
            EpisodicMemory record if prediction was found and completed,
            None if prediction_id was not found.
        
        Example:
            >>> outcome = Outcome(
            ...     outcome_id="out-123",
            ...     prediction_id=pred_id,
            ...     observed_signal=0.28,
            ...     observed_baseline=0.22,
            ...     prediction_error=0.0,  # Will be recalculated
            ...     goal_completed=True,
            ...     business_impact=1000.0,
            ...     metadata={},
            ...     observed_at=datetime.now(timezone.utc).isoformat(),
            ... )
            >>> episodic = wm.complete_prediction(pred_id, outcome)
            >>> if episodic:
            ...     print(f"Prediction error: {episodic.outcome.prediction_error}")
        """
        with self._lock:
            prediction = self._active_predictions.pop(prediction_id, None)
            if prediction is None:
                return None
            
            # Remove from order tracking
            try:
                self._prediction_order.remove(prediction_id)
            except ValueError:
                pass  # Already removed or never tracked
            
            # Calculate prediction error
            # error = (observed_signal/observed_baseline) - (expected_signal/expected_baseline)
            observed_ratio = (
                outcome.observed_signal / outcome.observed_baseline
                if outcome.observed_baseline != 0 else 0.0
            )
            expected_ratio = (
                prediction.expected_signal / prediction.expected_baseline
                if prediction.expected_baseline != 0 else 0.0
            )
            prediction_error = observed_ratio - expected_ratio
            
            # Update outcome with calculated prediction error if not already set
            # Create a new Outcome with the calculated error
            completed_outcome = Outcome(
                outcome_id=outcome.outcome_id,
                prediction_id=prediction.prediction_id,
                observed_signal=outcome.observed_signal,
                observed_baseline=outcome.observed_baseline,
                prediction_error=prediction_error,
                goal_completed=outcome.goal_completed,
                business_impact=outcome.business_impact,
                metadata=outcome.metadata,
                observed_at=outcome.observed_at,
            )
            
            # Create episodic memory record
            episodic = EpisodicMemory(
                episode_id=str(uuid.uuid4()),
                prediction=prediction,
                outcome=completed_outcome,
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            
            # Add to recent outcomes (FIFO with automatic eviction)
            self._recent_outcomes.append(episodic)
            
            return episodic
    
    def get_recent_outcomes(
        self,
        skill_name: Optional[str] = None,
        tenant_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[EpisodicMemory]:
        """
        Retrieve recent outcomes, optionally filtered by skill or tenant.
        
        Args:
            skill_name: If provided, only return outcomes for this skill.
            tenant_id: If provided, only return outcomes for this tenant.
            limit: Maximum number of outcomes to return. If None, returns
                all matching outcomes up to max_recent_outcomes.
        
        Returns:
            List of EpisodicMemory records, most recent first.
        
        Example:
            >>> # Get all recent outcomes
            >>> all_recent = wm.get_recent_outcomes()
            >>> 
            >>> # Get outcomes for a specific skill
            >>> email_outcomes = wm.get_recent_outcomes(skill_name="email-optimizer")
            >>> 
            >>> # Get last 3 outcomes for a client
            >>> client_recent = wm.get_recent_outcomes(tenant_id="acme-corp", limit=3)
        """
        with self._lock:
            # Start with all outcomes, reversed for most-recent-first
            outcomes = list(reversed(self._recent_outcomes))
            
            # Apply filters
            if skill_name is not None:
                outcomes = [
                    o for o in outcomes 
                    if o.prediction.skill_name == skill_name
                ]
            
            if tenant_id is not None:
                outcomes = [
                    o for o in outcomes 
                    if o.prediction.tenant_id == tenant_id
                ]
            
            # Apply limit
            if limit is not None:
                outcomes = outcomes[:limit]
            
            return outcomes
    
    def set_context(self, key: str, value: Any) -> None:
        """
        Store a value in session context.
        
        Session context provides a simple key-value store for sharing
        data between components during a session. Common uses:
        - Current client/tenant being processed
        - Feature flags or configuration overrides
        - Intermediate computation results
        
        Args:
            key: The context key (string).
            value: Any value to store. Should be serializable if you plan
                to log or debug the context.
        
        Example:
            >>> wm.set_context("current_client", "acme-corp")
            >>> wm.set_context("debug_mode", True)
            >>> wm.set_context("batch_size", 100)
        """
        with self._lock:
            self._session_context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a value from session context.
        
        Args:
            key: The context key to retrieve.
            default: Value to return if key is not found. Defaults to None.
        
        Returns:
            The stored value, or default if not found.
        
        Example:
            >>> client = wm.get_context("current_client")
            >>> debug = wm.get_context("debug_mode", False)
        """
        with self._lock:
            return self._session_context.get(key, default)
    
    def clear(self) -> None:
        """
        Clear all working memory.
        
        This removes:
        - All active predictions
        - All recent outcomes
        - All session context
        
        Use this when starting a new session or resetting state.
        
        Example:
            >>> wm.clear()
            >>> assert len(wm.get_recent_outcomes()) == 0
        """
        with self._lock:
            self._active_predictions.clear()
            self._recent_outcomes.clear()
            self._session_context.clear()
            self._prediction_order.clear()
    
    @property
    def active_prediction_count(self) -> int:
        """Return the number of active predictions awaiting outcomes."""
        with self._lock:
            return len(self._active_predictions)
    
    @property
    def recent_outcome_count(self) -> int:
        """Return the number of recent outcomes in memory."""
        with self._lock:
            return len(self._recent_outcomes)
    
    def __repr__(self) -> str:
        with self._lock:
            return (
                f"WorkingMemory("
                f"active_predictions={len(self._active_predictions)}, "
                f"recent_outcomes={len(self._recent_outcomes)}, "
                f"context_keys={list(self._session_context.keys())})"
            )
