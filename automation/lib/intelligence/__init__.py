"""
MH1 Intelligence System: Main interface.

Usage:
    from lib.intelligence import IntelligenceEngine, Domain
    
    engine = IntelligenceEngine()
    
    # Before skill execution
    guidance = engine.get_guidance("dormant-detection", tenant_id, Domain.REVENUE)
    prediction = engine.register_prediction(skill, tenant_id, Domain.REVENUE, expected, baseline)
    
    # After skill execution
    engine.record_outcome(prediction_id, observed_signal, goal_completed=True)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, TYPE_CHECKING

# Core types
from .types import (
    Domain,
    EpisodicMemory,
    MemoryLayer,
    Outcome,
    Prediction,
    ProceduralKnowledge,
    SemanticPattern,
)

# Memory stores
from .memory import (
    EpisodicMemoryConfig,
    EpisodicMemoryStore,
    ProceduralMemoryConfig,
    ProceduralMemoryStore,
    SemanticMemoryConfig,
    SemanticMemoryStore,
)
from .memory.working import WorkingMemory, WorkingMemoryConfig
from .memory.consolidation import ConsolidationConfig, MemoryConsolidationManager

# Learning components
from .learning import (
    ExplorationConfig,
    Guidance,
    Learner,
    LearningConfig,
    Predictor,
)

# Domain adapters
from .adapters import (
    BaseDomainAdapter,
    CampaignAdapter,
    ContentAdapter,
    HealthAdapter,
    RevenueAdapter,
    ScoringResult,
)

if TYPE_CHECKING:
    from lib.firebase_client import FirebaseClient

logger = logging.getLogger(__name__)


class IntelligenceEngine:
    """
    Main entry point for the MH1 Intelligence System.
    
    The IntelligenceEngine provides a unified interface to the memory,
    learning, and prediction subsystems. It coordinates:
    
    - Memory layers (working, episodic, semantic, procedural)
    - Prediction and outcome tracking
    - Continuous learning from execution results
    - Domain-specific scoring and adaptation
    - Memory consolidation and knowledge transfer
    
    Typical workflow:
    
    1. Before skill execution:
       - Get guidance based on historical patterns
       - Register a prediction with expected outcomes
    
    2. After skill execution:
       - Record the observed outcome
       - System automatically learns from prediction errors
    
    3. Periodically:
       - Run consolidation to promote patterns to long-term memory
    
    Example:
        >>> from lib.intelligence import IntelligenceEngine, Domain
        >>> 
        >>> engine = IntelligenceEngine()
        >>> 
        >>> # Get guidance before running a skill
        >>> guidance = engine.get_guidance(
        ...     skill_name="dormant-detection",
        ...     tenant_id="acme-corp",
        ...     domain=Domain.REVENUE
        ... )
        >>> 
        >>> # Register prediction
        >>> pred_id = engine.register_prediction(
        ...     skill_name="dormant-detection",
        ...     tenant_id="acme-corp",
        ...     domain=Domain.REVENUE,
        ...     expected_signal=0.15,
        ...     expected_baseline=1.0,
        ...     guidance=guidance
        ... )
        >>> 
        >>> # ... run skill ...
        >>> 
        >>> # Record outcome
        >>> result = engine.record_outcome(
        ...     prediction_id=pred_id,
        ...     observed_signal=0.18,
        ...     goal_completed=True,
        ...     business_impact=5000.0
        ... )
        >>> print(f"Prediction error: {result['prediction_error']}")
    
    Thread Safety:
        The IntelligenceEngine itself is stateless regarding thread safety,
        but delegates to thread-safe components. Working memory and all
        persistent stores use locking for thread-safe operations.
    """
    
    def __init__(self, firebase_client: Optional["FirebaseClient"] = None):
        """
        Initialize the Intelligence Engine.
        
        Args:
            firebase_client: Optional Firebase client for persistent storage.
                If not provided, will be lazy-loaded from lib.firebase_client.
        """
        # Lazy load firebase client if not provided
        if firebase_client is None:
            try:
                from lib.firebase_client import get_firebase_client
                firebase_client = get_firebase_client()
            except ImportError:
                logger.warning(
                    "Firebase client not available. "
                    "Persistent memory features will be limited."
                )
                firebase_client = None
        
        self._firebase = firebase_client
        
        # Initialize memory layers
        self.working = WorkingMemory()
        self.episodic = EpisodicMemoryStore(firebase_client)
        self.semantic = SemanticMemoryStore(firebase_client)
        self.procedural = ProceduralMemoryStore(firebase_client)
        
        # Initialize consolidation manager
        self._consolidation = MemoryConsolidationManager(
            episodic_store=self.episodic,
            semantic_store=self.semantic,
            procedural_store=self.procedural,
        )
        
        # Initialize learning components
        self.predictor = Predictor(
            semantic_store=self.semantic,
            procedural_store=self.procedural,
        )
        self.learner = Learner(
            episodic_store=self.episodic,
            semantic_store=self.semantic,
        )
        
        # Initialize domain adapters
        self._adapters: Dict[Domain, BaseDomainAdapter] = {
            Domain.CONTENT: ContentAdapter(),
            Domain.REVENUE: RevenueAdapter(),
            Domain.HEALTH: HealthAdapter(),
            Domain.CAMPAIGN: CampaignAdapter(),
        }
        
        logger.info("IntelligenceEngine initialized")
    
    def get_guidance(
        self,
        skill_name: str,
        tenant_id: str,
        domain: Domain,
        context: Optional[Dict[str, Any]] = None,
    ) -> Guidance:
        """
        Get guidance for skill execution based on historical patterns.
        
        Queries semantic and procedural memory to find relevant patterns,
        then generates guidance with predictions and recommendations.
        
        Args:
            skill_name: Name of the skill requesting guidance
            tenant_id: Tenant/client identifier
            domain: Business domain for the skill
            context: Optional context dict with current conditions
        
        Returns:
            Guidance object containing:
            - predicted_signal: Expected outcome signal
            - predicted_baseline: Expected baseline value
            - confidence: Confidence in prediction (0-1)
            - recommendations: Suggested parameter values
            - patterns_used: IDs of patterns that informed guidance
            - is_exploration: Whether this is an exploratory recommendation
        
        Example:
            >>> guidance = engine.get_guidance(
            ...     skill_name="email-optimizer",
            ...     tenant_id="acme-corp",
            ...     domain=Domain.CONTENT,
            ...     context={"segment": "enterprise", "time_of_day": "morning"}
            ... )
            >>> print(f"Predicted signal: {guidance.predicted_signal}")
            >>> print(f"Confidence: {guidance.confidence}")
        """
        return self.predictor.get_guidance(
            skill_name=skill_name,
            tenant_id=tenant_id,
            domain=domain,
            context=context or {},
        )
    
    def register_prediction(
        self,
        skill_name: str,
        tenant_id: str,
        domain: Domain,
        expected_signal: float,
        expected_baseline: float,
        confidence: float = 0.5,
        context: Optional[Dict[str, Any]] = None,
        guidance: Optional[Guidance] = None,
    ) -> str:
        """
        Register a prediction before skill execution.
        
        Creates a prediction record in working memory that will be matched
        with an outcome after skill execution completes.
        
        Args:
            skill_name: Name of the skill making the prediction
            tenant_id: Tenant/client identifier
            domain: Business domain for scoring
            expected_signal: Predicted signal value (e.g., lift, rate)
            expected_baseline: Baseline for comparison
            confidence: Prediction confidence (0-1), defaults to 0.5
            context: Optional context dict capturing conditions at prediction time
            guidance: Optional Guidance object that informed this prediction
        
        Returns:
            prediction_id: Unique identifier to use when recording outcome
        
        Example:
            >>> pred_id = engine.register_prediction(
            ...     skill_name="dormant-detection",
            ...     tenant_id="acme-corp",
            ...     domain=Domain.REVENUE,
            ...     expected_signal=0.15,
            ...     expected_baseline=1.0,
            ...     confidence=0.7,
            ...     context={"segment": "enterprise"},
            ...     guidance=guidance
            ... )
        """
        # Extract patterns used from guidance if provided
        patterns_used = []
        is_exploration = False
        if guidance is not None:
            patterns_used = guidance.patterns_used or []
            is_exploration = guidance.is_exploration
            # Use guidance confidence if not explicitly provided
            if confidence == 0.5 and guidance.confidence != 0.5:
                confidence = guidance.confidence
        
        # Create prediction object
        prediction = Prediction(
            skill_name=skill_name,
            tenant_id=tenant_id,
            domain=domain,
            expected_signal=expected_signal,
            expected_baseline=expected_baseline,
            confidence=confidence,
            context=context or {},
            patterns_used=patterns_used,
            is_exploration=is_exploration,
        )
        
        # Register in working memory
        prediction_id = self.working.register_prediction(prediction)
        
        logger.debug(
            f"Registered prediction {prediction_id} for {skill_name}/{tenant_id}: "
            f"expected={expected_signal}/{expected_baseline}, confidence={confidence}"
        )
        
        return prediction_id
    
    def record_outcome(
        self,
        prediction_id: str,
        observed_signal: float,
        observed_baseline: Optional[float] = None,
        goal_completed: bool = False,
        business_impact: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Record an observed outcome and trigger learning.
        
        This method:
        1. Retrieves the prediction from working memory
        2. Creates an outcome record with prediction error
        3. Stores the episode to episodic memory
        4. Triggers learning to update semantic patterns
        
        Args:
            prediction_id: ID returned from register_prediction()
            observed_signal: The actual signal value observed
            observed_baseline: The actual baseline (uses expected if None)
            goal_completed: Whether the skill achieved its goal
            business_impact: Monetary or business value impact
            metadata: Optional additional metadata about the outcome
        
        Returns:
            Result dict with keys:
            - success: Whether outcome was recorded successfully
            - episode_id: ID of the created episodic memory (if successful)
            - prediction_error: Difference between predicted and observed
            - learning_result: Results from the learning update
        
        Raises:
            ValueError: If prediction_id is not found in working memory
        
        Example:
            >>> result = engine.record_outcome(
            ...     prediction_id=pred_id,
            ...     observed_signal=0.18,
            ...     observed_baseline=1.0,
            ...     goal_completed=True,
            ...     business_impact=5000.0,
            ...     metadata={"contacts_reactivated": 42}
            ... )
            >>> if result["success"]:
            ...     print(f"Episode ID: {result['episode_id']}")
            ...     print(f"Prediction error: {result['prediction_error']}")
        """
        result = {
            "success": False,
            "episode_id": None,
            "prediction_error": 0.0,
            "learning_result": None,
        }
        
        # Get prediction from working memory
        prediction = self.working.get_prediction(prediction_id)
        if prediction is None:
            logger.warning(f"Prediction {prediction_id} not found in working memory")
            raise ValueError(f"Prediction {prediction_id} not found")
        
        # Use expected baseline if observed not provided
        if observed_baseline is None:
            observed_baseline = prediction.expected_baseline
        
        # Create outcome object
        outcome = Outcome(
            prediction_id=prediction_id,
            observed_signal=observed_signal,
            observed_baseline=observed_baseline,
            goal_completed=goal_completed,
            business_impact=business_impact,
            metadata=metadata or {},
        )
        
        # Complete prediction in working memory (creates EpisodicMemory)
        episode = self.working.complete_prediction(prediction_id, outcome)
        
        if episode is None:
            logger.error(f"Failed to complete prediction {prediction_id}")
            return result
        
        # Store episode to episodic memory
        try:
            self.episodic.store(
                episode=episode,
                tenant_id=prediction.tenant_id,
                skill_name=prediction.skill_name,
            )
            result["episode_id"] = episode.episode_id
            result["prediction_error"] = episode.outcome.prediction_error
            
            logger.debug(
                f"Stored episode {episode.episode_id} for {prediction.skill_name}/{prediction.tenant_id}, "
                f"error={episode.outcome.prediction_error:.4f}"
            )
        except Exception as e:
            logger.error(f"Failed to store episode: {e}")
            # Continue with learning even if storage fails
        
        # Trigger learning from the outcome
        try:
            learning_result = self.learner.learn_from_outcome(
                prediction=prediction,
                outcome=outcome,
            )
            result["learning_result"] = learning_result
            
            logger.debug(f"Learning complete: {learning_result}")
        except Exception as e:
            logger.error(f"Learning failed: {e}")
            result["learning_result"] = {"error": str(e)}
        
        result["success"] = True
        return result
    
    def score(
        self,
        domain: Domain,
        event: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ScoringResult:
        """
        Calculate a domain-specific score for an event.
        
        Uses the appropriate domain adapter to apply domain-specific
        scoring logic (signal extraction, baseline calculation, context
        multipliers, etc.).
        
        Args:
            domain: Business domain for scoring
            event: Event data dict containing the raw metrics
            context: Optional context for score adjustment
        
        Returns:
            ScoringResult with:
            - signal: Extracted signal value
            - baseline: Calculated baseline
            - score: Final score (signal/baseline * adjustments)
            - confidence: Confidence in the score
            - metadata: Additional scoring details
        
        Example:
            >>> result = engine.score(
            ...     domain=Domain.REVENUE,
            ...     event={
            ...         "deal_amount": 50000,
            ...         "days_in_stage": 15,
            ...         "close_probability": 0.6
            ...     },
            ...     context={"industry": "saas"}
            ... )
            >>> print(f"Score: {result.score}")
        """
        context = context or {}
        
        # Get domain adapter
        adapter = self._adapters.get(domain)
        
        if adapter is not None:
            return adapter.calculate_score(event=event, context=context)
        
        # Fallback to generic scoring
        logger.debug(f"No adapter for domain {domain}, using generic scoring")
        
        # Generic scoring: look for common signal/baseline fields
        signal = event.get("signal", event.get("value", event.get("metric", 0.0)))
        baseline = event.get("baseline", event.get("expected", 1.0))
        
        if baseline == 0:
            baseline = 1.0
        
        score = signal / baseline
        
        return ScoringResult(
            signal=float(signal),
            baseline=float(baseline),
            score=score,
            confidence=0.5,
            metadata={"domain": domain.value, "method": "generic"},
        )
    
    def run_consolidation(
        self,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, int]:
        """
        Run memory consolidation cycle.
        
        Consolidation promotes memories from lower to higher memory layers:
        - Decays episodic memories over time
        - Promotes decayed episodes to semantic patterns
        - Archives stale semantic patterns
        - Promotes cross-skill patterns to procedural knowledge
        
        This should be run periodically (e.g., daily) to maintain
        memory health and enable long-term learning.
        
        Args:
            tenant_id: Optional tenant to consolidate. If None, all tenants.
        
        Returns:
            Statistics dict with keys:
            - episodic_decayed: Episodes with decay applied
            - episodes_consolidated: Episodes promoted to semantic
            - patterns_created: New semantic patterns created
            - patterns_updated: Existing patterns updated
            - patterns_archived: Stale patterns archived
            - procedural_created: New procedural knowledge entries
        
        Example:
            >>> stats = engine.run_consolidation(tenant_id="acme-corp")
            >>> print(f"Consolidated {stats['episodes_consolidated']} episodes")
            >>> print(f"Created {stats['patterns_created']} new patterns")
        """
        logger.info(f"Running consolidation for tenant: {tenant_id or 'all'}")
        
        return self._consolidation.run_consolidation_cycle(tenant_id=tenant_id)
    
    def clear_session(self) -> None:
        """
        Clear working memory (session state).
        
        This removes:
        - All active predictions
        - All recent outcomes
        - All session context
        
        Does NOT affect persistent memory (episodic, semantic, procedural).
        
        Use when starting a new session or resetting state between runs.
        
        Example:
            >>> engine.clear_session()
        """
        self.working.clear()
        logger.debug("Working memory cleared")
    
    def __repr__(self) -> str:
        return (
            f"IntelligenceEngine("
            f"working={self.working}, "
            f"adapters={list(self._adapters.keys())})"
        )


__all__ = [
    # Main interface
    "IntelligenceEngine",
    
    # Core types
    "Domain",
    "MemoryLayer",
    "Prediction",
    "Outcome",
    "Guidance",
    "EpisodicMemory",
    "SemanticPattern",
    "ProceduralKnowledge",
    
    # Scoring
    "ScoringResult",
    
    # Memory stores
    "WorkingMemory",
    "WorkingMemoryConfig",
    "EpisodicMemoryStore",
    "EpisodicMemoryConfig",
    "SemanticMemoryStore",
    "SemanticMemoryConfig",
    "ProceduralMemoryStore",
    "ProceduralMemoryConfig",
    
    # Consolidation
    "ConsolidationConfig",
    "MemoryConsolidationManager",
    
    # Learning
    "Predictor",
    "ExplorationConfig",
    "Learner",
    "LearningConfig",
    
    # Domain adapters
    "BaseDomainAdapter",
    "ContentAdapter",
    "RevenueAdapter",
    "HealthAdapter",
    "CampaignAdapter",
]
