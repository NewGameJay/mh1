# MH1 Intelligence System: Final Implementation Plan

**Version:** 1.0  
**Date:** January 28, 2026  
**Status:** Ready for Implementation  
**Supersedes:** BRIGHTMATTER_IMPLEMENTATION_FINAL.md

---

## Executive Summary

This document defines the **MH1 Intelligence System** — a true self-improving, continuously learning architecture that goes far beyond simple outcome logging. It implements:

1. **Multi-Layer Memory Architecture** — Working → Episodic → Semantic → Procedural memory with automatic consolidation
2. **Self-Cleansing Mechanisms** — Temporal decay, relevance pruning, and memory compression
3. **Continuous Learning Loop** — Bayesian confidence updates, exploration/exploitation, and concept drift detection
4. **Universal Scoring** — Domain-agnostic Signal/Baseline/Context formula with pluggable adapters
5. **Cross-Skill Transfer** — Patterns that generalize across skills and clients

This replaces the domain-locked BrightMatter approach with a research-backed architecture drawing from MemVerse, Nemori, MESU, and RLUF frameworks (2025-2026).

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        MH1 INTELLIGENCE SYSTEM                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                    MULTI-LAYER MEMORY SYSTEM                               │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │  │
│  │  │   WORKING   │→ │  EPISODIC   │→ │  SEMANTIC   │→ │ PROCEDURAL  │      │  │
│  │  │   MEMORY    │  │   MEMORY    │  │   MEMORY    │  │   MEMORY    │      │  │
│  │  │  (session)  │  │ (90 days)   │  │ (patterns)  │  │ (cross-skill)│     │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘      │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                      │                                           │
│  ┌───────────────────────────────────┴───────────────────────────────────────┐  │
│  │                    CONTINUOUS LEARNING ENGINE                              │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐           │  │
│  │  │   PREDICT &     │  │   LEARN FROM    │  │    DETECT &     │           │  │
│  │  │   CALIBRATE     │  │    OUTCOMES     │  │     ADAPT       │           │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘           │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                      │                                           │
│  ┌───────────────────────────────────┴───────────────────────────────────────┐  │
│  │                    DOMAIN ADAPTERS (Universal Scoring)                     │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │  │
│  │  │ Content │  │ Revenue │  │ Health  │  │Campaign │  │ Custom  │        │  │
│  │  │ Adapter │  │ Adapter │  │ Adapter │  │ Adapter │  │ Adapter │        │  │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                      │                                           │
│  ┌───────────────────────────────────┴───────────────────────────────────────┐  │
│  │                    INFRASTRUCTURE (from BrightMatter)                      │  │
│  │  exceptions │ retry │ circuit_breaker │ rate_limiter │ metrics │ health   │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Module Structure

```
lib/
├── intelligence/                    # NEW: Intelligence system
│   ├── __init__.py                 # Public exports
│   ├── types.py                    # Core data types
│   ├── memory/                     # Multi-layer memory
│   │   ├── __init__.py
│   │   ├── working.py              # Session-scoped working memory
│   │   ├── episodic.py             # Experience-based memory
│   │   ├── semantic.py             # Pattern-based memory
│   │   ├── procedural.py           # Cross-skill generalizations
│   │   └── consolidation.py        # Memory lifecycle management
│   ├── learning/                   # Continuous learning
│   │   ├── __init__.py
│   │   ├── predictor.py            # Prediction with confidence
│   │   ├── learner.py              # Bayesian updates from outcomes
│   │   ├── explorer.py             # Exploration/exploitation
│   │   └── drift_detector.py       # Concept drift detection
│   ├── adapters/                   # Domain adapters
│   │   ├── __init__.py
│   │   ├── base.py                 # Base adapter interface
│   │   ├── content.py              # Content/engagement domain
│   │   ├── revenue.py              # Deal/pipeline domain
│   │   ├── health.py               # Customer health domain
│   │   └── campaign.py             # Marketing campaign domain
│   └── firebase/                   # Firebase integration
│       ├── __init__.py
│       ├── memory_store.py         # Memory persistence
│       └── sync.py                 # Cross-client sync
│
├── brain/                          # KEEP: BrightMatter infrastructure
│   ├── __init__.py
│   ├── exceptions.py               # Error hierarchy
│   ├── retry.py                    # Retry decorators
│   ├── circuit_breaker.py          # Circuit breaker pattern
│   ├── rate_limiter.py             # Token bucket rate limiting
│   ├── metrics.py                  # Observability
│   ├── health.py                   # Health checks
│   └── validation.py               # Input sanitization
│
├── runner.py                       # EXTEND: Wire intelligence into workflows
├── evaluator.py                    # EXTEND: Add GCR/BIE/MTR dimensions
└── intelligence.py                 # DEPRECATE: Replaced by lib/intelligence/

config/
├── semantic_layer/
│   ├── event_dictionary.yml        # KEEP: Platform-agnostic events
│   ├── lifecycle_steps.yml         # KEEP: Lifecycle definitions
│   └── domain_adapters.yml         # NEW: Domain scoring definitions
└── intelligence/
    ├── memory_config.yml           # NEW: Memory lifecycle settings
    ├── learning_config.yml         # NEW: Learning parameters
    └── exploration_config.yml      # NEW: Exploration settings
```

---

# PHASE 1: Multi-Layer Memory System

## 1.1 Core Types

```python
# lib/intelligence/types.py
"""
Core types for the MH1 Intelligence System.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum
import uuid


class MemoryLayer(Enum):
    """Memory layer types following cognitive architecture."""
    WORKING = "working"         # Session-scoped, immediate context
    EPISODIC = "episodic"       # Specific experiences with decay
    SEMANTIC = "semantic"       # Learned patterns with confidence
    PROCEDURAL = "procedural"   # Cross-skill generalizations


class Domain(Enum):
    """Business domains for scoring adaptation."""
    CONTENT = "content"         # Engagement, impressions, growth
    REVENUE = "revenue"         # Deals, pipeline, velocity
    HEALTH = "health"           # Churn, retention, satisfaction
    CAMPAIGN = "campaign"       # ROI, attribution, CPL
    GENERIC = "generic"         # Fallback domain


@dataclass
class Prediction:
    """A prediction registered before skill execution."""
    prediction_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    skill_name: str = ""
    tenant_id: str = ""
    domain: Domain = Domain.GENERIC
    
    # What we predict
    expected_signal: float = 0.0
    expected_baseline: float = 1.0
    confidence: float = 0.5
    confidence_interval: tuple = (0.0, 1.0)
    
    # Context at prediction time
    context: Dict[str, Any] = field(default_factory=dict)
    patterns_used: List[str] = field(default_factory=list)  # IDs of semantic patterns
    is_exploration: bool = False
    
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "prediction_id": self.prediction_id,
            "skill_name": self.skill_name,
            "tenant_id": self.tenant_id,
            "domain": self.domain.value,
            "expected_signal": self.expected_signal,
            "expected_baseline": self.expected_baseline,
            "confidence": self.confidence,
            "confidence_interval": list(self.confidence_interval),
            "context": self.context,
            "patterns_used": self.patterns_used,
            "is_exploration": self.is_exploration,
            "created_at": self.created_at,
        }


@dataclass
class Outcome:
    """An observed outcome after skill execution."""
    outcome_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    prediction_id: str = ""
    
    # What actually happened
    observed_signal: float = 0.0
    observed_baseline: float = 1.0
    
    # Computed metrics
    prediction_error: float = 0.0
    goal_completed: bool = False
    business_impact: float = 0.0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    observed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "outcome_id": self.outcome_id,
            "prediction_id": self.prediction_id,
            "observed_signal": self.observed_signal,
            "observed_baseline": self.observed_baseline,
            "prediction_error": self.prediction_error,
            "goal_completed": self.goal_completed,
            "business_impact": self.business_impact,
            "metadata": self.metadata,
            "observed_at": self.observed_at,
        }


@dataclass
class EpisodicMemory:
    """
    A specific experience stored in episodic memory.
    Decays over time and consolidates into semantic patterns.
    """
    episode_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    prediction: Prediction = field(default_factory=Prediction)
    outcome: Outcome = field(default_factory=Outcome)
    
    # Memory properties
    weight: float = 1.0                    # Decays over time
    retrieval_count: int = 0               # How often retrieved
    last_retrieved_at: Optional[str] = None
    
    # Lifecycle
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    consolidated_at: Optional[str] = None  # When compressed to semantic
    archived_at: Optional[str] = None      # When moved to archive
    
    def to_dict(self) -> Dict:
        return {
            "episode_id": self.episode_id,
            "prediction": self.prediction.to_dict(),
            "outcome": self.outcome.to_dict(),
            "weight": self.weight,
            "retrieval_count": self.retrieval_count,
            "last_retrieved_at": self.last_retrieved_at,
            "created_at": self.created_at,
            "consolidated_at": self.consolidated_at,
            "archived_at": self.archived_at,
        }


@dataclass
class SemanticPattern:
    """
    A learned pattern in semantic memory.
    Generalizes from multiple episodic memories.
    """
    pattern_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    
    # Pattern definition
    skill_name: str = ""
    domain: Domain = Domain.GENERIC
    condition: Dict[str, Any] = field(default_factory=dict)  # When pattern applies
    recommendation: Dict[str, Any] = field(default_factory=dict)  # What to do
    
    # Learning state
    confidence: float = 0.5                # Bayesian confidence [0, 1]
    expected_value: float = 1.0            # Expected Signal/Baseline ratio
    variance: float = 1.0                  # Uncertainty in expected value
    
    # Evidence tracking
    evidence_count: int = 0
    successes: int = 0
    failures: int = 0
    recent_accuracy: float = 0.5           # Rolling 10-episode accuracy
    
    # Scope
    tenant_ids: List[str] = field(default_factory=list)  # Empty = all tenants
    
    # Lifecycle
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_reinforced_at: Optional[str] = None
    decay_rate: float = 0.99               # Per-day confidence decay without reinforcement
    
    def to_dict(self) -> Dict:
        return {
            "pattern_id": self.pattern_id,
            "skill_name": self.skill_name,
            "domain": self.domain.value,
            "condition": self.condition,
            "recommendation": self.recommendation,
            "confidence": self.confidence,
            "expected_value": self.expected_value,
            "variance": self.variance,
            "evidence_count": self.evidence_count,
            "successes": self.successes,
            "failures": self.failures,
            "recent_accuracy": self.recent_accuracy,
            "tenant_ids": self.tenant_ids,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_reinforced_at": self.last_reinforced_at,
            "decay_rate": self.decay_rate,
        }


@dataclass
class ProceduralKnowledge:
    """
    Cross-skill generalization in procedural memory.
    Applies to multiple skills and/or all tenants.
    """
    knowledge_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    
    # What this knowledge captures
    description: str = ""
    pattern_type: str = ""                 # "parameter_range", "sequence", "channel_preference"
    
    # Applicability
    applicable_skills: List[str] = field(default_factory=list)
    applicable_domains: List[Domain] = field(default_factory=list)
    
    # The knowledge itself
    knowledge: Dict[str, Any] = field(default_factory=dict)
    
    # Confidence from multiple skill validations
    cross_skill_confidence: float = 0.5
    validating_skills: Dict[str, float] = field(default_factory=dict)  # skill -> accuracy
    
    # Lifecycle
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "knowledge_id": self.knowledge_id,
            "description": self.description,
            "pattern_type": self.pattern_type,
            "applicable_skills": self.applicable_skills,
            "applicable_domains": [d.value for d in self.applicable_domains],
            "knowledge": self.knowledge,
            "cross_skill_confidence": self.cross_skill_confidence,
            "validating_skills": self.validating_skills,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class Guidance:
    """
    Guidance returned to a skill from the intelligence system.
    """
    # Recommended parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Confidence and reasoning
    confidence: float = 0.5
    uncertainty: float = 0.5
    reasoning: str = ""
    
    # Source tracking
    patterns_used: List[str] = field(default_factory=list)
    procedural_knowledge_used: List[str] = field(default_factory=list)
    
    # Exploration flag
    is_exploration: bool = False
    exploration_reason: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "parameters": self.parameters,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "reasoning": self.reasoning,
            "patterns_used": self.patterns_used,
            "procedural_knowledge_used": self.procedural_knowledge_used,
            "is_exploration": self.is_exploration,
            "exploration_reason": self.exploration_reason,
        }
```

---

## 1.2 Working Memory

```python
# lib/intelligence/memory/working.py
"""
Working Memory: Session-scoped immediate context.

- Holds current skill execution state
- Last N outcomes for fast retrieval
- Cleared at session end
- NOT persisted to Firebase
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from collections import deque
import threading

from ..types import Prediction, Outcome, EpisodicMemory


@dataclass
class WorkingMemoryConfig:
    """Configuration for working memory."""
    max_recent_outcomes: int = 10
    max_active_predictions: int = 5


class WorkingMemory:
    """
    Session-scoped working memory.
    
    Provides fast access to:
    - Current active predictions (awaiting outcomes)
    - Recent outcomes for pattern matching
    - Session context
    """
    
    def __init__(self, config: WorkingMemoryConfig = None):
        self.config = config or WorkingMemoryConfig()
        self._lock = threading.RLock()
        
        # Active predictions awaiting outcomes
        self._active_predictions: Dict[str, Prediction] = {}
        
        # Recent outcomes (FIFO)
        self._recent_outcomes: deque = deque(maxlen=self.config.max_recent_outcomes)
        
        # Session context
        self._session_context: Dict[str, Any] = {}
    
    def register_prediction(self, prediction: Prediction) -> str:
        """Register a prediction, returns prediction_id."""
        with self._lock:
            self._active_predictions[prediction.prediction_id] = prediction
            
            # Evict oldest if over limit
            if len(self._active_predictions) > self.config.max_active_predictions:
                oldest_id = min(
                    self._active_predictions.keys(),
                    key=lambda k: self._active_predictions[k].created_at
                )
                del self._active_predictions[oldest_id]
            
            return prediction.prediction_id
    
    def get_prediction(self, prediction_id: str) -> Optional[Prediction]:
        """Get an active prediction."""
        with self._lock:
            return self._active_predictions.get(prediction_id)
    
    def complete_prediction(self, prediction_id: str, outcome: Outcome) -> Optional[EpisodicMemory]:
        """
        Complete a prediction with an outcome.
        Returns an EpisodicMemory for consolidation.
        """
        with self._lock:
            prediction = self._active_predictions.pop(prediction_id, None)
            if not prediction:
                return None
            
            # Calculate prediction error
            if prediction.expected_baseline > 0:
                expected_ratio = prediction.expected_signal / prediction.expected_baseline
            else:
                expected_ratio = prediction.expected_signal
            
            if outcome.observed_baseline > 0:
                observed_ratio = outcome.observed_signal / outcome.observed_baseline
            else:
                observed_ratio = outcome.observed_signal
            
            outcome.prediction_error = observed_ratio - expected_ratio
            
            # Create episodic memory
            episode = EpisodicMemory(
                prediction=prediction,
                outcome=outcome
            )
            
            # Add to recent outcomes
            self._recent_outcomes.append(episode)
            
            return episode
    
    def get_recent_outcomes(
        self,
        skill_name: str = None,
        tenant_id: str = None,
        limit: int = None
    ) -> List[EpisodicMemory]:
        """Get recent outcomes, optionally filtered."""
        with self._lock:
            results = list(self._recent_outcomes)
            
            if skill_name:
                results = [e for e in results if e.prediction.skill_name == skill_name]
            
            if tenant_id:
                results = [e for e in results if e.prediction.tenant_id == tenant_id]
            
            if limit:
                results = results[-limit:]
            
            return results
    
    def set_context(self, key: str, value: Any):
        """Set session context value."""
        with self._lock:
            self._session_context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get session context value."""
        with self._lock:
            return self._session_context.get(key, default)
    
    def clear(self):
        """Clear all working memory (end of session)."""
        with self._lock:
            self._active_predictions.clear()
            self._recent_outcomes.clear()
            self._session_context.clear()
```

---

## 1.3 Episodic Memory with Firebase

```python
# lib/intelligence/memory/episodic.py
"""
Episodic Memory: Specific experiences with temporal decay.

- Persisted to Firebase
- Automatic temporal decay
- Consolidates to semantic memory after threshold
- TTL: 90 days before archival
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
import math
import threading

from ..types import EpisodicMemory, Prediction, Domain


@dataclass
class EpisodicMemoryConfig:
    """Configuration for episodic memory."""
    decay_rate: float = 0.95               # Per-day decay
    relevance_threshold: float = 0.3       # Below this, consolidate
    max_episodes_per_skill: int = 1000     # Per skill/tenant
    ttl_days: int = 90                     # Days before archival
    consolidation_threshold: int = 10      # Episodes before pattern extraction


class EpisodicMemoryStore:
    """
    Episodic memory with Firebase persistence.
    
    Firebase Structure:
    system/
    └── intelligence/
        └── episodic/
            └── {tenant_id}/
                └── {skill_name}/
                    └── {episode_id}: EpisodicMemory
    """
    
    def __init__(
        self,
        firebase_client,
        config: EpisodicMemoryConfig = None
    ):
        self.firebase = firebase_client
        self.config = config or EpisodicMemoryConfig()
        self._lock = threading.RLock()
        self._collection_base = "system/intelligence/episodic"
    
    def _get_collection_path(self, tenant_id: str, skill_name: str) -> str:
        """Get Firebase collection path for a tenant/skill."""
        return f"{self._collection_base}/{tenant_id}/{skill_name}"
    
    def store(self, episode: EpisodicMemory) -> str:
        """Store an episode to Firebase."""
        tenant_id = episode.prediction.tenant_id
        skill_name = episode.prediction.skill_name
        
        # Store to Firebase
        self.firebase.set_document(
            self._collection_base,
            tenant_id,
            subcollection=skill_name,
            subdoc_id=episode.episode_id,
            data=episode.to_dict()
        )
        
        return episode.episode_id
    
    def retrieve(
        self,
        tenant_id: str,
        skill_name: str,
        domain: Domain = None,
        min_weight: float = None,
        limit: int = 100
    ) -> List[EpisodicMemory]:
        """
        Retrieve episodes with optional filtering.
        Applies temporal decay on retrieval.
        """
        # Query from Firebase
        filters = []
        if domain:
            filters.append(("prediction.domain", "==", domain.value))
        if min_weight:
            filters.append(("weight", ">=", min_weight))
        
        docs = self.firebase.query(
            skill_name,
            filters=filters,
            limit=limit,
            order_by="created_at",
            order_direction="DESCENDING",
            parent_collection=self._collection_base,
            parent_doc=tenant_id
        )
        
        episodes = []
        now = datetime.now(timezone.utc)
        
        for doc in docs:
            episode = self._doc_to_episode(doc)
            
            # Apply temporal decay
            created = datetime.fromisoformat(episode.created_at.replace("Z", "+00:00"))
            age_days = (now - created).days
            episode.weight *= (self.config.decay_rate ** age_days)
            
            # Increment retrieval count
            episode.retrieval_count += 1
            episode.last_retrieved_at = now.isoformat()
            
            episodes.append(episode)
        
        return episodes
    
    def decay_all(self, tenant_id: str = None) -> Dict[str, int]:
        """
        Apply temporal decay to all episodes.
        Returns stats on decayed and consolidated episodes.
        """
        stats = {"decayed": 0, "to_consolidate": 0, "archived": 0}
        now = datetime.now(timezone.utc)
        
        # Get all tenant/skill combinations
        if tenant_id:
            tenants = [tenant_id]
        else:
            # Query all tenants
            tenant_docs = self.firebase.get_collection(self._collection_base)
            tenants = [doc["_id"] for doc in tenant_docs]
        
        for tid in tenants:
            # Get all skills for this tenant
            skill_docs = self.firebase.get_collection(
                tid,
                parent_collection=self._collection_base,
                parent_doc=None
            )
            
            for skill_doc in skill_docs:
                skill_name = skill_doc["_id"]
                episodes = self.retrieve(tid, skill_name, limit=10000)
                
                for episode in episodes:
                    created = datetime.fromisoformat(episode.created_at.replace("Z", "+00:00"))
                    age_days = (now - created).days
                    
                    # Archive if past TTL
                    if age_days > self.config.ttl_days:
                        self._archive_episode(episode)
                        stats["archived"] += 1
                        continue
                    
                    # Mark for consolidation if below threshold
                    if episode.weight < self.config.relevance_threshold:
                        stats["to_consolidate"] += 1
                    
                    stats["decayed"] += 1
        
        return stats
    
    def get_for_consolidation(
        self,
        tenant_id: str,
        skill_name: str,
        limit: int = None
    ) -> List[EpisodicMemory]:
        """Get episodes ready for consolidation to semantic memory."""
        limit = limit or self.config.consolidation_threshold
        
        episodes = self.retrieve(
            tenant_id,
            skill_name,
            min_weight=0.0,  # Include all
            limit=limit * 2  # Get extra to filter
        )
        
        # Filter to those below relevance threshold
        ready = [e for e in episodes if e.weight < self.config.relevance_threshold]
        
        return ready[:limit]
    
    def mark_consolidated(self, episode_id: str, tenant_id: str, skill_name: str):
        """Mark an episode as consolidated."""
        now = datetime.now(timezone.utc).isoformat()
        
        self.firebase.update_document(
            skill_name,
            episode_id,
            data={"consolidated_at": now},
            parent_collection=self._collection_base,
            parent_doc=tenant_id
        )
    
    def _archive_episode(self, episode: EpisodicMemory):
        """Move episode to archive collection."""
        tenant_id = episode.prediction.tenant_id
        skill_name = episode.prediction.skill_name
        
        # Store to archive
        episode.archived_at = datetime.now(timezone.utc).isoformat()
        
        self.firebase.set_document(
            f"system/intelligence/archive/{tenant_id}",
            skill_name,
            subdoc_id=episode.episode_id,
            data=episode.to_dict()
        )
        
        # Delete from active episodic
        self.firebase.delete_document(
            skill_name,
            episode.episode_id,
            subcollection=None,
            subdoc_id=None
        )
    
    def _doc_to_episode(self, doc: Dict) -> EpisodicMemory:
        """Convert Firebase document to EpisodicMemory."""
        pred_data = doc.get("prediction", {})
        out_data = doc.get("outcome", {})
        
        prediction = Prediction(
            prediction_id=pred_data.get("prediction_id", ""),
            skill_name=pred_data.get("skill_name", ""),
            tenant_id=pred_data.get("tenant_id", ""),
            domain=Domain(pred_data.get("domain", "generic")),
            expected_signal=pred_data.get("expected_signal", 0.0),
            expected_baseline=pred_data.get("expected_baseline", 1.0),
            confidence=pred_data.get("confidence", 0.5),
            context=pred_data.get("context", {}),
            patterns_used=pred_data.get("patterns_used", []),
            is_exploration=pred_data.get("is_exploration", False),
            created_at=pred_data.get("created_at", ""),
        )
        
        outcome = Outcome(
            outcome_id=out_data.get("outcome_id", ""),
            prediction_id=out_data.get("prediction_id", ""),
            observed_signal=out_data.get("observed_signal", 0.0),
            observed_baseline=out_data.get("observed_baseline", 1.0),
            prediction_error=out_data.get("prediction_error", 0.0),
            goal_completed=out_data.get("goal_completed", False),
            business_impact=out_data.get("business_impact", 0.0),
            metadata=out_data.get("metadata", {}),
            observed_at=out_data.get("observed_at", ""),
        )
        
        return EpisodicMemory(
            episode_id=doc.get("episode_id", doc.get("_id", "")),
            prediction=prediction,
            outcome=outcome,
            weight=doc.get("weight", 1.0),
            retrieval_count=doc.get("retrieval_count", 0),
            last_retrieved_at=doc.get("last_retrieved_at"),
            created_at=doc.get("created_at", ""),
            consolidated_at=doc.get("consolidated_at"),
            archived_at=doc.get("archived_at"),
        )
```

---

## 1.4 Semantic Memory with Pattern Learning

```python
# lib/intelligence/memory/semantic.py
"""
Semantic Memory: Learned patterns with confidence tracking.

- Generalized from episodic memories
- Bayesian confidence updates
- Decay without reinforcement
- Firebase persistence
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple
import math
import threading

from ..types import SemanticPattern, EpisodicMemory, Domain


@dataclass
class SemanticMemoryConfig:
    """Configuration for semantic memory."""
    initial_confidence: float = 0.5
    learning_rate: float = 0.1
    decay_rate: float = 0.99              # Per-day without reinforcement
    min_confidence: float = 0.01
    max_confidence: float = 0.99
    forget_threshold: float = 0.1         # Below this, archive
    min_evidence_for_trust: int = 5


class SemanticMemoryStore:
    """
    Semantic memory with Bayesian learning.
    
    Firebase Structure:
    system/
    └── intelligence/
        └── semantic/
            └── {domain}/
                └── {pattern_id}: SemanticPattern
    """
    
    def __init__(
        self,
        firebase_client,
        config: SemanticMemoryConfig = None
    ):
        self.firebase = firebase_client
        self.config = config or SemanticMemoryConfig()
        self._lock = threading.RLock()
        self._collection_base = "system/intelligence/semantic"
    
    def store(self, pattern: SemanticPattern) -> str:
        """Store a pattern to Firebase."""
        self.firebase.set_document(
            self._collection_base,
            pattern.domain.value,
            subcollection="patterns",
            subdoc_id=pattern.pattern_id,
            data=pattern.to_dict()
        )
        return pattern.pattern_id
    
    def retrieve_patterns(
        self,
        skill_name: str,
        domain: Domain,
        tenant_id: str = None,
        min_confidence: float = None,
        limit: int = 20
    ) -> List[SemanticPattern]:
        """
        Retrieve patterns matching skill/domain.
        Applies decay on retrieval.
        """
        filters = [("skill_name", "==", skill_name)]
        if min_confidence:
            filters.append(("confidence", ">=", min_confidence))
        
        docs = self.firebase.query(
            "patterns",
            filters=filters,
            limit=limit,
            order_by="confidence",
            order_direction="DESCENDING",
            parent_collection=self._collection_base,
            parent_doc=domain.value
        )
        
        patterns = []
        now = datetime.now(timezone.utc)
        
        for doc in docs:
            pattern = self._doc_to_pattern(doc)
            
            # Filter by tenant if specified
            if tenant_id and pattern.tenant_ids:
                if tenant_id not in pattern.tenant_ids:
                    continue
            
            # Apply decay if not recently reinforced
            if pattern.last_reinforced_at:
                last_reinforced = datetime.fromisoformat(
                    pattern.last_reinforced_at.replace("Z", "+00:00")
                )
                days_since = (now - last_reinforced).days
                if days_since > 0:
                    pattern.confidence *= (pattern.decay_rate ** days_since)
                    pattern.confidence = max(self.config.min_confidence, pattern.confidence)
            
            patterns.append(pattern)
        
        return patterns
    
    def consolidate_from_episodes(
        self,
        episodes: List[EpisodicMemory]
    ) -> Optional[SemanticPattern]:
        """
        Create or update a semantic pattern from episodic memories.
        This is the consolidation process.
        """
        if not episodes:
            return None
        
        # Group by common characteristics
        skill_name = episodes[0].prediction.skill_name
        domain = episodes[0].prediction.domain
        
        # Extract common context elements
        common_context = self._extract_common_context(episodes)
        
        # Calculate pattern metrics
        successes = sum(1 for e in episodes if e.outcome.goal_completed)
        failures = len(episodes) - successes
        
        # Calculate expected value from episodes
        ratios = []
        for e in episodes:
            if e.outcome.observed_baseline > 0:
                ratios.append(e.outcome.observed_signal / e.outcome.observed_baseline)
        
        if ratios:
            expected_value = sum(ratios) / len(ratios)
            variance = sum((r - expected_value) ** 2 for r in ratios) / len(ratios)
        else:
            expected_value = 1.0
            variance = 1.0
        
        # Find existing pattern or create new
        existing = self._find_similar_pattern(skill_name, domain, common_context)
        
        if existing:
            # Update existing pattern
            pattern = existing
            pattern.evidence_count += len(episodes)
            pattern.successes += successes
            pattern.failures += failures
            
            # Bayesian confidence update
            pattern.confidence = self._bayesian_update(
                pattern.confidence,
                successes,
                failures
            )
            
            # Update expected value with EMA
            pattern.expected_value = 0.8 * pattern.expected_value + 0.2 * expected_value
            pattern.variance = 0.8 * pattern.variance + 0.2 * variance
            
            # Update recent accuracy
            pattern.recent_accuracy = successes / len(episodes)
            
            pattern.updated_at = datetime.now(timezone.utc).isoformat()
            pattern.last_reinforced_at = pattern.updated_at
        else:
            # Create new pattern
            pattern = SemanticPattern(
                skill_name=skill_name,
                domain=domain,
                condition=common_context,
                recommendation=self._extract_recommendation(episodes),
                confidence=self._bayesian_update(
                    self.config.initial_confidence,
                    successes,
                    failures
                ),
                expected_value=expected_value,
                variance=variance,
                evidence_count=len(episodes),
                successes=successes,
                failures=failures,
                recent_accuracy=successes / len(episodes),
                tenant_ids=list(set(e.prediction.tenant_id for e in episodes)),
            )
        
        # Store to Firebase
        self.store(pattern)
        
        return pattern
    
    def update_from_outcome(
        self,
        pattern_id: str,
        domain: Domain,
        success: bool,
        observed_ratio: float
    ):
        """
        Update a pattern based on a new outcome.
        This is the learning step.
        """
        # Get pattern
        doc = self.firebase.get_document(
            self._collection_base,
            domain.value,
            subcollection="patterns",
            subdoc_id=pattern_id
        )
        
        if not doc:
            return
        
        pattern = self._doc_to_pattern(doc)
        
        # Update counts
        pattern.evidence_count += 1
        if success:
            pattern.successes += 1
        else:
            pattern.failures += 1
        
        # Bayesian confidence update
        pattern.confidence = self._bayesian_update(
            pattern.confidence,
            1 if success else 0,
            0 if success else 1
        )
        
        # Update expected value with EMA
        pattern.expected_value = 0.9 * pattern.expected_value + 0.1 * observed_ratio
        
        # Update recent accuracy (rolling window approximation)
        pattern.recent_accuracy = (
            0.9 * pattern.recent_accuracy + 
            0.1 * (1.0 if success else 0.0)
        )
        
        pattern.updated_at = datetime.now(timezone.utc).isoformat()
        pattern.last_reinforced_at = pattern.updated_at
        
        # Store update
        self.store(pattern)
    
    def forget_stale_patterns(self) -> int:
        """
        Archive patterns that have decayed below threshold.
        Returns count of archived patterns.
        """
        archived_count = 0
        
        for domain in Domain:
            patterns = self.retrieve_patterns(
                skill_name="",  # All skills
                domain=domain,
                min_confidence=0.0,
                limit=1000
            )
            
            for pattern in patterns:
                if pattern.confidence < self.config.forget_threshold:
                    if pattern.evidence_count >= self.config.min_evidence_for_trust:
                        # Pattern was once trusted but has decayed - archive
                        self._archive_pattern(pattern)
                        archived_count += 1
        
        return archived_count
    
    def _bayesian_update(
        self,
        prior: float,
        successes: int,
        failures: int
    ) -> float:
        """
        Bayesian update of confidence using Beta distribution.
        """
        # Convert prior to pseudo-counts (assuming uniform prior = 1,1)
        alpha = prior * 10 + successes
        beta = (1 - prior) * 10 + failures
        
        # Posterior mean
        posterior = alpha / (alpha + beta)
        
        # Clamp to bounds
        return max(
            self.config.min_confidence,
            min(self.config.max_confidence, posterior)
        )
    
    def _extract_common_context(self, episodes: List[EpisodicMemory]) -> Dict:
        """Extract common context elements from episodes."""
        if not episodes:
            return {}
        
        # Start with first episode's context
        common = dict(episodes[0].prediction.context)
        
        # Find intersection of all contexts
        for episode in episodes[1:]:
            ctx = episode.prediction.context
            common = {
                k: v for k, v in common.items()
                if k in ctx and ctx[k] == v
            }
        
        return common
    
    def _extract_recommendation(self, episodes: List[EpisodicMemory]) -> Dict:
        """Extract recommendation from successful episodes."""
        successful = [e for e in episodes if e.outcome.goal_completed]
        
        if not successful:
            successful = episodes  # Use all if none successful
        
        # Average the contexts of successful episodes
        # This is a simplification - could be more sophisticated
        recommendation = {}
        
        for episode in successful:
            for k, v in episode.prediction.context.items():
                if isinstance(v, (int, float)):
                    if k not in recommendation:
                        recommendation[k] = []
                    recommendation[k].append(v)
        
        # Average numeric values
        for k, values in recommendation.items():
            if values:
                recommendation[k] = sum(values) / len(values)
        
        return recommendation
    
    def _find_similar_pattern(
        self,
        skill_name: str,
        domain: Domain,
        context: Dict
    ) -> Optional[SemanticPattern]:
        """Find an existing pattern similar to the given context."""
        patterns = self.retrieve_patterns(
            skill_name=skill_name,
            domain=domain,
            limit=100
        )
        
        for pattern in patterns:
            if self._contexts_match(pattern.condition, context):
                return pattern
        
        return None
    
    def _contexts_match(self, pattern_ctx: Dict, episode_ctx: Dict) -> bool:
        """Check if contexts are similar enough to match."""
        if not pattern_ctx:
            return True  # Empty pattern matches all
        
        # Check if all pattern conditions are met in episode
        for k, v in pattern_ctx.items():
            if k not in episode_ctx:
                return False
            
            episode_v = episode_ctx[k]
            
            if isinstance(v, (int, float)) and isinstance(episode_v, (int, float)):
                # Numeric: check within 20%
                if abs(v - episode_v) > 0.2 * max(abs(v), 1):
                    return False
            elif v != episode_v:
                return False
        
        return True
    
    def _archive_pattern(self, pattern: SemanticPattern):
        """Move pattern to archive."""
        # Store to archive
        self.firebase.set_document(
            f"system/intelligence/archive/semantic",
            pattern.domain.value,
            subdoc_id=pattern.pattern_id,
            data={**pattern.to_dict(), "archived_at": datetime.now(timezone.utc).isoformat()}
        )
        
        # Delete from active
        self.firebase.delete_document(
            self._collection_base,
            pattern.domain.value,
            subcollection="patterns",
            subdoc_id=pattern.pattern_id
        )
    
    def _doc_to_pattern(self, doc: Dict) -> SemanticPattern:
        """Convert Firebase document to SemanticPattern."""
        return SemanticPattern(
            pattern_id=doc.get("pattern_id", doc.get("_id", "")),
            skill_name=doc.get("skill_name", ""),
            domain=Domain(doc.get("domain", "generic")),
            condition=doc.get("condition", {}),
            recommendation=doc.get("recommendation", {}),
            confidence=doc.get("confidence", 0.5),
            expected_value=doc.get("expected_value", 1.0),
            variance=doc.get("variance", 1.0),
            evidence_count=doc.get("evidence_count", 0),
            successes=doc.get("successes", 0),
            failures=doc.get("failures", 0),
            recent_accuracy=doc.get("recent_accuracy", 0.5),
            tenant_ids=doc.get("tenant_ids", []),
            created_at=doc.get("created_at", ""),
            updated_at=doc.get("updated_at", ""),
            last_reinforced_at=doc.get("last_reinforced_at"),
            decay_rate=doc.get("decay_rate", 0.99),
        )
```

---

## 1.5 Memory Consolidation Manager

```python
# lib/intelligence/memory/consolidation.py
"""
Memory Consolidation: Manages the memory lifecycle.

- Consolidates episodic → semantic
- Generalizes semantic → procedural
- Handles decay and forgetting
- Scheduled jobs for maintenance
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional
import threading
import logging

from ..types import EpisodicMemory, SemanticPattern, ProceduralKnowledge, Domain
from .episodic import EpisodicMemoryStore
from .semantic import SemanticMemoryStore
from .procedural import ProceduralMemoryStore

logger = logging.getLogger(__name__)


@dataclass
class ConsolidationConfig:
    """Configuration for memory consolidation."""
    consolidation_batch_size: int = 20
    min_episodes_for_consolidation: int = 5
    cross_skill_threshold: int = 3         # Skills needed for procedural
    cross_skill_min_confidence: float = 0.6


class MemoryConsolidationManager:
    """
    Manages the memory lifecycle and consolidation process.
    
    Lifecycle:
    1. Working Memory → Episodic (immediate, on outcome)
    2. Episodic → Semantic (when weight decays below threshold)
    3. Semantic → Procedural (when pattern validates across skills)
    """
    
    def __init__(
        self,
        episodic_store: EpisodicMemoryStore,
        semantic_store: SemanticMemoryStore,
        procedural_store: ProceduralKnowledge,
        config: ConsolidationConfig = None
    ):
        self.episodic = episodic_store
        self.semantic = semantic_store
        self.procedural = procedural_store
        self.config = config or ConsolidationConfig()
        self._lock = threading.RLock()
    
    def run_consolidation_cycle(self, tenant_id: str = None) -> Dict[str, int]:
        """
        Run a full consolidation cycle.
        
        Steps:
        1. Decay episodic memories
        2. Consolidate ready episodes to semantic patterns
        3. Decay semantic patterns
        4. Promote patterns to procedural knowledge
        5. Archive forgotten patterns
        
        Returns:
            Stats on consolidation activities
        """
        stats = {
            "episodic_decayed": 0,
            "episodes_consolidated": 0,
            "patterns_created": 0,
            "patterns_updated": 0,
            "patterns_archived": 0,
            "procedural_created": 0,
        }
        
        logger.info(f"Starting consolidation cycle for tenant: {tenant_id or 'all'}")
        
        # Step 1: Decay episodic memories
        decay_stats = self.episodic.decay_all(tenant_id)
        stats["episodic_decayed"] = decay_stats["decayed"]
        
        # Step 2: Consolidate ready episodes
        consolidation_stats = self._consolidate_ready_episodes(tenant_id)
        stats["episodes_consolidated"] = consolidation_stats["consolidated"]
        stats["patterns_created"] = consolidation_stats["patterns_created"]
        stats["patterns_updated"] = consolidation_stats["patterns_updated"]
        
        # Step 3: Archive forgotten patterns
        stats["patterns_archived"] = self.semantic.forget_stale_patterns()
        
        # Step 4: Promote cross-skill patterns to procedural
        stats["procedural_created"] = self._promote_to_procedural()
        
        logger.info(f"Consolidation cycle complete: {stats}")
        
        return stats
    
    def _consolidate_ready_episodes(self, tenant_id: str = None) -> Dict[str, int]:
        """Consolidate episodes that are ready."""
        stats = {"consolidated": 0, "patterns_created": 0, "patterns_updated": 0}
        
        # Get all tenant/skill combinations with ready episodes
        # (This would be more efficient with a direct query)
        
        tenants = [tenant_id] if tenant_id else self._get_all_tenants()
        
        for tid in tenants:
            skills = self._get_skills_for_tenant(tid)
            
            for skill_name in skills:
                episodes = self.episodic.get_for_consolidation(
                    tid,
                    skill_name,
                    limit=self.config.consolidation_batch_size
                )
                
                if len(episodes) >= self.config.min_episodes_for_consolidation:
                    # Consolidate to semantic pattern
                    pattern = self.semantic.consolidate_from_episodes(episodes)
                    
                    if pattern:
                        if pattern.evidence_count == len(episodes):
                            stats["patterns_created"] += 1
                        else:
                            stats["patterns_updated"] += 1
                        
                        # Mark episodes as consolidated
                        for episode in episodes:
                            self.episodic.mark_consolidated(
                                episode.episode_id,
                                tid,
                                skill_name
                            )
                            stats["consolidated"] += 1
        
        return stats
    
    def _promote_to_procedural(self) -> int:
        """
        Promote patterns that validate across multiple skills
        to procedural knowledge.
        """
        created_count = 0
        
        # Group patterns by similar conditions
        pattern_groups = self._find_cross_skill_patterns()
        
        for group in pattern_groups:
            if len(group["skills"]) >= self.config.cross_skill_threshold:
                avg_confidence = sum(p.confidence for p in group["patterns"]) / len(group["patterns"])
                
                if avg_confidence >= self.config.cross_skill_min_confidence:
                    # Create procedural knowledge
                    knowledge = ProceduralKnowledge(
                        description=self._generate_description(group),
                        pattern_type="cross_skill_recommendation",
                        applicable_skills=group["skills"],
                        applicable_domains=list(set(p.domain for p in group["patterns"])),
                        knowledge=group["common_recommendation"],
                        cross_skill_confidence=avg_confidence,
                        validating_skills={
                            p.skill_name: p.recent_accuracy 
                            for p in group["patterns"]
                        }
                    )
                    
                    self.procedural.store(knowledge)
                    created_count += 1
        
        return created_count
    
    def _find_cross_skill_patterns(self) -> List[Dict]:
        """Find patterns that share similar conditions across skills."""
        groups = []
        
        # Get all patterns across domains
        all_patterns = []
        for domain in Domain:
            patterns = self.semantic.retrieve_patterns(
                skill_name="",  # All skills
                domain=domain,
                min_confidence=self.config.cross_skill_min_confidence,
                limit=500
            )
            all_patterns.extend(patterns)
        
        # Group by similar conditions
        # (Simplified - could use clustering)
        condition_groups: Dict[str, List[SemanticPattern]] = {}
        
        for pattern in all_patterns:
            # Create a hashable key from condition
            key = self._condition_key(pattern.condition)
            
            if key not in condition_groups:
                condition_groups[key] = []
            condition_groups[key].append(pattern)
        
        # Convert to groups with multiple skills
        for key, patterns in condition_groups.items():
            skills = list(set(p.skill_name for p in patterns))
            
            if len(skills) >= 2:  # At least 2 different skills
                groups.append({
                    "condition_key": key,
                    "skills": skills,
                    "patterns": patterns,
                    "common_recommendation": self._merge_recommendations(patterns)
                })
        
        return groups
    
    def _condition_key(self, condition: Dict) -> str:
        """Generate a hashable key from condition dict."""
        items = sorted(condition.items())
        return str(items)
    
    def _merge_recommendations(self, patterns: List[SemanticPattern]) -> Dict:
        """Merge recommendations from multiple patterns."""
        merged = {}
        
        for pattern in patterns:
            for k, v in pattern.recommendation.items():
                if k not in merged:
                    merged[k] = []
                merged[k].append(v)
        
        # Average numeric values, take mode for others
        result = {}
        for k, values in merged.items():
            if all(isinstance(v, (int, float)) for v in values):
                result[k] = sum(values) / len(values)
            else:
                # Take most common
                result[k] = max(set(values), key=values.count)
        
        return result
    
    def _generate_description(self, group: Dict) -> str:
        """Generate human-readable description for procedural knowledge."""
        skills = ", ".join(group["skills"][:3])
        if len(group["skills"]) > 3:
            skills += f" and {len(group['skills']) - 3} more"
        
        return f"Cross-skill pattern validated across: {skills}"
    
    def _get_all_tenants(self) -> List[str]:
        """Get all tenant IDs with episodic memories."""
        # This would query Firebase for tenant list
        return []  # Implement based on Firebase structure
    
    def _get_skills_for_tenant(self, tenant_id: str) -> List[str]:
        """Get all skills with memories for a tenant."""
        # This would query Firebase
        return []  # Implement based on Firebase structure
```

---

# PHASE 2: Continuous Learning Engine

## 2.1 Predictor with Exploration

```python
# lib/intelligence/learning/predictor.py
"""
Predictor: Generates predictions with confidence and exploration.

- Retrieves relevant patterns from semantic memory
- Balances exploitation (use best pattern) vs exploration (try new things)
- Uncertainty-guided exploration
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import random
import math

from ..types import (
    Prediction, Guidance, SemanticPattern, 
    ProceduralKnowledge, Domain
)
from ..memory.semantic import SemanticMemoryStore
from ..memory.procedural import ProceduralMemoryStore


@dataclass
class ExplorationConfig:
    """Configuration for exploration behavior."""
    base_exploration_rate: float = 0.15    # 15% random exploration
    uncertainty_threshold: float = 0.7     # Explore if confidence below this
    novelty_boost: float = 0.1             # Extra exploration for new skills
    decay_exploration_with_evidence: bool = True


class Predictor:
    """
    Generates predictions and guidance for skills.
    
    Implements exploration/exploitation trade-off:
    - Exploitation: Use highest-confidence pattern
    - Exploration: Try unexplored parameter regions
    """
    
    def __init__(
        self,
        semantic_store: SemanticMemoryStore,
        procedural_store: ProceduralMemoryStore,
        config: ExplorationConfig = None
    ):
        self.semantic = semantic_store
        self.procedural = procedural_store
        self.config = config or ExplorationConfig()
    
    def get_guidance(
        self,
        skill_name: str,
        tenant_id: str,
        domain: Domain,
        context: Dict
    ) -> Guidance:
        """
        Get guidance for a skill execution.
        
        Returns:
            Guidance with parameters, confidence, and exploration flag
        """
        # Retrieve relevant patterns
        patterns = self.semantic.retrieve_patterns(
            skill_name=skill_name,
            domain=domain,
            tenant_id=tenant_id,
            min_confidence=0.1,
            limit=20
        )
        
        # Get procedural knowledge
        procedural = self.procedural.retrieve(
            skill_name=skill_name,
            domain=domain
        )
        
        # Decide: explore or exploit?
        should_explore, explore_reason = self._should_explore(
            patterns,
            context
        )
        
        if should_explore or not patterns:
            return self._explore(
                skill_name,
                domain,
                context,
                procedural,
                explore_reason
            )
        else:
            return self._exploit(
                patterns,
                procedural,
                context
            )
    
    def _should_explore(
        self,
        patterns: List[SemanticPattern],
        context: Dict
    ) -> Tuple[bool, str]:
        """
        Decide whether to explore or exploit.
        
        Explore when:
        1. Random exploration rate triggers
        2. Best pattern confidence is below threshold
        3. Context is novel (no matching patterns)
        """
        # Random exploration
        if random.random() < self.config.base_exploration_rate:
            return True, "random_exploration"
        
        if not patterns:
            return True, "no_patterns_available"
        
        # Get best pattern
        best = max(patterns, key=lambda p: p.confidence)
        
        # Low confidence exploration
        if best.confidence < self.config.uncertainty_threshold:
            return True, f"low_confidence_{best.confidence:.2f}"
        
        # Check if context is novel
        matching = [p for p in patterns if self._context_matches(p.condition, context)]
        if not matching:
            return True, "novel_context"
        
        return False, ""
    
    def _explore(
        self,
        skill_name: str,
        domain: Domain,
        context: Dict,
        procedural: List[ProceduralKnowledge],
        reason: str
    ) -> Guidance:
        """
        Generate exploratory guidance.
        
        Tries parameter values we haven't tried before,
        or varies known-good parameters.
        """
        # Start with default parameters
        parameters = self._get_default_parameters(skill_name, domain)
        
        # Apply procedural knowledge if available
        for knowledge in procedural:
            parameters = self._apply_procedural(parameters, knowledge)
        
        # Perturb parameters for exploration
        parameters = self._perturb_parameters(parameters)
        
        return Guidance(
            parameters=parameters,
            confidence=0.3,  # Low confidence for exploration
            uncertainty=0.7,
            reasoning=f"Exploration: {reason}",
            patterns_used=[],
            procedural_knowledge_used=[k.knowledge_id for k in procedural],
            is_exploration=True,
            exploration_reason=reason
        )
    
    def _exploit(
        self,
        patterns: List[SemanticPattern],
        procedural: List[ProceduralKnowledge],
        context: Dict
    ) -> Guidance:
        """
        Generate exploitation guidance using best patterns.
        """
        # Filter patterns that match context
        matching = [
            p for p in patterns 
            if self._context_matches(p.condition, context)
        ]
        
        if not matching:
            matching = patterns  # Fall back to all patterns
        
        # Get best pattern
        best = max(matching, key=lambda p: p.confidence * p.recent_accuracy)
        
        # Build parameters from recommendation
        parameters = dict(best.recommendation)
        
        # Apply procedural knowledge
        for knowledge in procedural:
            parameters = self._apply_procedural(parameters, knowledge)
        
        # Calculate combined confidence
        confidence = best.confidence
        if procedural:
            proc_confidence = sum(k.cross_skill_confidence for k in procedural) / len(procedural)
            confidence = (confidence + proc_confidence) / 2
        
        reasoning = f"Using pattern '{best.pattern_id}' with {best.evidence_count} evidence points"
        
        return Guidance(
            parameters=parameters,
            confidence=confidence,
            uncertainty=1 - confidence,
            reasoning=reasoning,
            patterns_used=[best.pattern_id],
            procedural_knowledge_used=[k.knowledge_id for k in procedural],
            is_exploration=False,
            exploration_reason=""
        )
    
    def _context_matches(self, pattern_ctx: Dict, current_ctx: Dict) -> bool:
        """Check if pattern condition matches current context."""
        for k, v in pattern_ctx.items():
            if k not in current_ctx:
                return False
            
            current_v = current_ctx[k]
            
            if isinstance(v, (int, float)) and isinstance(current_v, (int, float)):
                # Allow 30% tolerance for numeric values
                if abs(v - current_v) > 0.3 * max(abs(v), 1):
                    return False
            elif v != current_v:
                return False
        
        return True
    
    def _get_default_parameters(self, skill_name: str, domain: Domain) -> Dict:
        """Get default parameters for a skill/domain."""
        # These would come from config/skill definitions
        defaults = {
            "dormant-detection": {
                "threshold_days": 30,
                "include_partial_engagement": True,
                "min_historical_activity": 2
            },
            "lifecycle-audit": {
                "sample_size": 100,
                "include_anonymous": False,
                "lookback_days": 90
            }
        }
        
        return defaults.get(skill_name, {})
    
    def _apply_procedural(
        self,
        parameters: Dict,
        knowledge: ProceduralKnowledge
    ) -> Dict:
        """Apply procedural knowledge to parameters."""
        for k, v in knowledge.knowledge.items():
            if k in parameters:
                # Blend with existing value
                existing = parameters[k]
                if isinstance(existing, (int, float)) and isinstance(v, (int, float)):
                    parameters[k] = 0.7 * existing + 0.3 * v
            else:
                parameters[k] = v
        
        return parameters
    
    def _perturb_parameters(self, parameters: Dict) -> Dict:
        """Perturb parameters for exploration."""
        perturbed = dict(parameters)
        
        for k, v in perturbed.items():
            if isinstance(v, (int, float)):
                # Add ±20% noise
                noise = (random.random() - 0.5) * 0.4 * abs(v)
                perturbed[k] = v + noise
                
                if isinstance(v, int):
                    perturbed[k] = int(round(perturbed[k]))
        
        return perturbed
```

---

## 2.2 Learner with Concept Drift Detection

```python
# lib/intelligence/learning/learner.py
"""
Learner: Updates beliefs based on outcomes.

- Bayesian confidence updates
- Concept drift detection
- Triggered relearning when patterns become stale
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional
import math
import logging

from ..types import Prediction, Outcome, Domain
from ..memory.episodic import EpisodicMemoryStore
from ..memory.semantic import SemanticMemoryStore


logger = logging.getLogger(__name__)


@dataclass
class LearningConfig:
    """Configuration for learning behavior."""
    learning_rate: float = 0.1
    drift_window_size: int = 20
    drift_threshold: float = 2.0           # Std deviations
    relearning_exploration_boost: float = 0.3


class Learner:
    """
    Learns from outcomes and detects concept drift.
    
    Key responsibilities:
    1. Update pattern confidence based on outcomes
    2. Detect when the world has changed (concept drift)
    3. Trigger relearning when patterns become stale
    """
    
    def __init__(
        self,
        episodic_store: EpisodicMemoryStore,
        semantic_store: SemanticMemoryStore,
        config: LearningConfig = None
    ):
        self.episodic = episodic_store
        self.semantic = semantic_store
        self.config = config or LearningConfig()
        
        # Track recent errors for drift detection
        self._error_history: Dict[str, List[float]] = {}
    
    def learn_from_outcome(
        self,
        prediction: Prediction,
        outcome: Outcome
    ) -> Dict[str, any]:
        """
        Learn from a prediction-outcome pair.
        
        Returns:
            Learning result with updates made and drift detection
        """
        result = {
            "patterns_updated": 0,
            "drift_detected": False,
            "drift_skill": None
        }
        
        # Calculate prediction error
        if prediction.expected_baseline > 0:
            expected_ratio = prediction.expected_signal / prediction.expected_baseline
        else:
            expected_ratio = prediction.expected_signal
        
        if outcome.observed_baseline > 0:
            observed_ratio = outcome.observed_signal / outcome.observed_baseline
        else:
            observed_ratio = outcome.observed_signal
        
        error = observed_ratio - expected_ratio
        success = outcome.goal_completed
        
        # Update patterns that were used
        for pattern_id in prediction.patterns_used:
            self.semantic.update_from_outcome(
                pattern_id=pattern_id,
                domain=prediction.domain,
                success=success,
                observed_ratio=observed_ratio
            )
            result["patterns_updated"] += 1
        
        # Check for concept drift
        drift_key = f"{prediction.skill_name}:{prediction.domain.value}"
        drift = self._check_drift(drift_key, error)
        
        if drift:
            result["drift_detected"] = True
            result["drift_skill"] = prediction.skill_name
            self._trigger_relearning(prediction.skill_name, prediction.domain)
        
        return result
    
    def _check_drift(self, key: str, error: float) -> bool:
        """
        Check for concept drift using error tracking.
        
        Uses a sliding window comparison:
        - Compare recent errors to older errors
        - If significantly different, drift detected
        """
        if key not in self._error_history:
            self._error_history[key] = []
        
        self._error_history[key].append(error)
        
        # Keep only recent window
        if len(self._error_history[key]) > self.config.drift_window_size * 2:
            self._error_history[key] = self._error_history[key][-self.config.drift_window_size * 2:]
        
        errors = self._error_history[key]
        
        if len(errors) < self.config.drift_window_size:
            return False  # Not enough data
        
        # Split into recent and older
        half = len(errors) // 2
        recent = errors[-half:]
        older = errors[:half]
        
        # Compare means
        recent_mean = sum(recent) / len(recent)
        older_mean = sum(older) / len(older)
        
        # Calculate std dev of all errors
        all_mean = sum(errors) / len(errors)
        variance = sum((e - all_mean) ** 2 for e in errors) / len(errors)
        std_dev = math.sqrt(variance) if variance > 0 else 0.1
        
        # Check if difference is significant
        diff = abs(recent_mean - older_mean)
        
        if diff > self.config.drift_threshold * std_dev:
            logger.warning(
                f"Concept drift detected for {key}: "
                f"recent_mean={recent_mean:.3f}, older_mean={older_mean:.3f}, "
                f"diff={diff:.3f}, threshold={self.config.drift_threshold * std_dev:.3f}"
            )
            return True
        
        return False
    
    def _trigger_relearning(self, skill_name: str, domain: Domain):
        """
        Trigger relearning when concept drift is detected.
        
        Actions:
        1. Reduce confidence of patterns for this skill
        2. Increase exploration rate temporarily
        3. Log for monitoring
        """
        logger.info(f"Triggering relearning for skill={skill_name}, domain={domain.value}")
        
        # Get patterns for this skill
        patterns = self.semantic.retrieve_patterns(
            skill_name=skill_name,
            domain=domain,
            limit=100
        )
        
        # Reduce confidence of all patterns
        for pattern in patterns:
            new_confidence = pattern.confidence * 0.5  # 50% reduction
            new_confidence = max(0.1, new_confidence)
            
            self.semantic.update_from_outcome(
                pattern_id=pattern.pattern_id,
                domain=domain,
                success=False,  # Treat as failure to reduce confidence
                observed_ratio=1.0
            )
        
        # Clear error history to start fresh
        drift_key = f"{skill_name}:{domain.value}"
        self._error_history[drift_key] = []
```

---

# PHASE 3: Domain Adapters

## 3.1 Universal Scoring Formula

```python
# lib/intelligence/adapters/base.py
"""
Base Domain Adapter: Universal scoring abstraction.

Formula: Score = (Signal / Baseline) × Context × Confidence
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional

from ..types import Domain


@dataclass
class ScoringResult:
    """Result of universal scoring."""
    score: float
    signal: float
    baseline: float
    context_multiplier: float
    confidence: float
    components: Dict[str, float]
    explanation: str


class BaseDomainAdapter(ABC):
    """
    Base class for domain adapters.
    
    Each adapter implements the universal formula:
    Score = (Signal / Baseline) × Context_Multiplier × Confidence
    
    Where Signal, Baseline, and Context are domain-specific.
    """
    
    domain: Domain = Domain.GENERIC
    
    @abstractmethod
    def to_signal(self, event: Dict) -> float:
        """
        Convert domain event to universal signal.
        
        The signal represents the observed/expected outcome metric.
        """
        pass
    
    @abstractmethod
    def to_baseline(self, context: Dict) -> float:
        """
        Calculate expected baseline for context.
        
        The baseline represents what we'd expect without intervention.
        """
        pass
    
    @abstractmethod
    def get_context_multiplier(self, context: Dict) -> float:
        """
        Calculate context-specific multiplier.
        
        Adjusts score based on contextual factors.
        """
        pass
    
    def calculate_score(
        self,
        event: Dict,
        context: Dict,
        confidence: float = 1.0
    ) -> ScoringResult:
        """
        Calculate universal score using domain-specific implementations.
        
        Formula: Score = (Signal / Baseline) × Context × Confidence
        """
        signal = self.to_signal(event)
        baseline = max(self.to_baseline(context), 0.001)  # Prevent div by zero
        context_mult = self.get_context_multiplier(context)
        
        # Universal formula
        score = (signal / baseline) * context_mult * confidence
        
        return ScoringResult(
            score=score,
            signal=signal,
            baseline=baseline,
            context_multiplier=context_mult,
            confidence=confidence,
            components={
                "signal": signal,
                "baseline": baseline,
                "signal_baseline_ratio": signal / baseline,
                "context_multiplier": context_mult,
                "confidence": confidence
            },
            explanation=self._generate_explanation(signal, baseline, context_mult, confidence)
        )
    
    def goal_completed(self, score: float, threshold: float = 1.0) -> bool:
        """
        Determine if goal was completed.
        Score > threshold means signal exceeded baseline expectations.
        """
        return score >= threshold
    
    def _generate_explanation(
        self,
        signal: float,
        baseline: float,
        context_mult: float,
        confidence: float
    ) -> str:
        """Generate human-readable explanation of score."""
        ratio = signal / baseline if baseline > 0 else signal
        
        if ratio > 1.2:
            perf = "significantly exceeded"
        elif ratio > 1.0:
            perf = "exceeded"
        elif ratio > 0.8:
            perf = "nearly met"
        else:
            perf = "fell short of"
        
        return (
            f"Signal ({signal:.2f}) {perf} baseline ({baseline:.2f}) "
            f"with {ratio:.1%} ratio. "
            f"Context multiplier: {context_mult:.2f}, Confidence: {confidence:.0%}"
        )
```

---

## 3.2 Content Adapter

```python
# lib/intelligence/adapters/content.py
"""
Content Domain Adapter: Engagement, impressions, growth metrics.
"""

from typing import Dict
from .base import BaseDomainAdapter
from ..types import Domain


# Platform-specific baselines for engagement rates
PLATFORM_BASELINES = {
    "linkedin": {"engagement_rate": 0.02, "impression_rate": 0.10},
    "twitter": {"engagement_rate": 0.015, "impression_rate": 0.08},
    "instagram": {"engagement_rate": 0.03, "impression_rate": 0.15},
    "facebook": {"engagement_rate": 0.01, "impression_rate": 0.05},
    "email": {"engagement_rate": 0.20, "impression_rate": 0.25},
    "default": {"engagement_rate": 0.02, "impression_rate": 0.10}
}

# Decay curves for content (half-life in hours)
PLATFORM_DECAY = {
    "linkedin": 24,
    "twitter": 4,
    "instagram": 12,
    "facebook": 6,
    "email": 48,
    "default": 12
}


class ContentAdapter(BaseDomainAdapter):
    """
    Adapter for content engagement metrics.
    
    Signal: Impressions × (1 + engagement_rate)
    Baseline: follower_count × platform_baseline_rate × decay_factor
    Context: Topic relevance, posting time, content format
    """
    
    domain = Domain.CONTENT
    
    def to_signal(self, event: Dict) -> float:
        """
        Convert content event to signal.
        
        Signal = impressions × (1 + engagement_rate)
        """
        impressions = event.get("impressions", 0)
        engagements = event.get("engagements", 0)
        
        # Calculate engagement rate
        if impressions > 0:
            engagement_rate = engagements / impressions
        else:
            engagement_rate = 0
        
        # Signal combines reach with engagement quality
        signal = impressions * (1 + engagement_rate)
        
        return signal
    
    def to_baseline(self, context: Dict) -> float:
        """
        Calculate expected baseline for content.
        
        Baseline = followers × platform_rate × time_decay
        """
        platform = context.get("platform", "default")
        followers = context.get("follower_count", 1000)
        hours_since_post = context.get("hours_since_post", 24)
        
        # Get platform baseline
        baselines = PLATFORM_BASELINES.get(platform, PLATFORM_BASELINES["default"])
        base_rate = baselines["impression_rate"]
        
        # Apply time decay
        half_life = PLATFORM_DECAY.get(platform, PLATFORM_DECAY["default"])
        decay_factor = 0.5 ** (hours_since_post / half_life)
        
        baseline = followers * base_rate * max(decay_factor, 0.1)
        
        return baseline
    
    def get_context_multiplier(self, context: Dict) -> float:
        """
        Calculate context multiplier for content.
        
        Considers:
        - Topic relevance (historical pillar performance)
        - Posting time (time of day, day of week)
        - Content format (video, image, text)
        """
        multiplier = 1.0
        
        # Topic/pillar multiplier
        topic_score = context.get("topic_relevance", 1.0)
        multiplier *= min(1.5, max(0.5, topic_score))
        
        # Format multiplier
        format_multipliers = {
            "video": 1.3,
            "carousel": 1.2,
            "image": 1.0,
            "text": 0.8,
            "link": 0.7
        }
        content_format = context.get("format", "text")
        multiplier *= format_multipliers.get(content_format, 1.0)
        
        # Time of day multiplier (simplified)
        hour = context.get("post_hour", 12)
        if 9 <= hour <= 17:  # Business hours
            multiplier *= 1.1
        
        return multiplier
```

---

## 3.3 Revenue Adapter

```python
# lib/intelligence/adapters/revenue.py
"""
Revenue Domain Adapter: Deal velocity, pipeline health, conversion.
"""

from typing import Dict
from .base import BaseDomainAdapter
from ..types import Domain


# Stage velocity benchmarks (days)
STAGE_VELOCITY_BENCHMARKS = {
    "lead_to_mql": {"enterprise": 14, "mid_market": 7, "smb": 3},
    "mql_to_sql": {"enterprise": 21, "mid_market": 14, "smb": 7},
    "sql_to_opportunity": {"enterprise": 30, "mid_market": 21, "smb": 14},
    "opportunity_to_close": {"enterprise": 60, "mid_market": 30, "smb": 14},
    "default": {"enterprise": 30, "mid_market": 14, "smb": 7}
}


class RevenueAdapter(BaseDomainAdapter):
    """
    Adapter for revenue/deal metrics.
    
    Signal: Deal velocity (expected_days / actual_days)
    Baseline: Segment benchmark velocity
    Context: Deal size, industry, seasonality
    """
    
    domain = Domain.REVENUE
    
    def to_signal(self, event: Dict) -> float:
        """
        Convert deal event to velocity signal.
        
        Signal = expected_days / actual_days (higher = faster)
        """
        actual_days = event.get("days_in_stage", 1)
        expected_days = event.get("expected_stage_duration", 30)
        
        # Prevent division by zero
        actual_days = max(actual_days, 1)
        
        # Velocity ratio: > 1 means faster than expected
        signal = expected_days / actual_days
        
        return signal
    
    def to_baseline(self, context: Dict) -> float:
        """
        Calculate expected velocity baseline.
        
        Baseline = 1.0 (meeting benchmark)
        Adjusted by segment historical performance
        """
        segment = context.get("segment", "mid_market")
        stage = context.get("stage_transition", "default")
        
        # Get benchmark
        benchmarks = STAGE_VELOCITY_BENCHMARKS.get(
            stage, 
            STAGE_VELOCITY_BENCHMARKS["default"]
        )
        benchmark_days = benchmarks.get(segment, benchmarks.get("mid_market", 14))
        
        # Historical adjustment
        historical_multiplier = context.get("historical_velocity_multiplier", 1.0)
        
        # Baseline is the benchmark-adjusted expected velocity
        baseline = 1.0 * historical_multiplier
        
        return baseline
    
    def get_context_multiplier(self, context: Dict) -> float:
        """
        Calculate context multiplier for deals.
        
        Considers:
        - Deal size (larger deals move slower)
        - Industry velocity
        - Seasonality
        """
        multiplier = 1.0
        
        # Deal size adjustment
        deal_size = context.get("deal_value", 10000)
        if deal_size > 100000:
            multiplier *= 0.8  # Large deals expected to be slower
        elif deal_size < 5000:
            multiplier *= 1.2  # Small deals expected to be faster
        
        # Industry adjustment
        industry_factors = {
            "technology": 1.1,
            "finance": 0.9,
            "healthcare": 0.85,
            "retail": 1.15,
            "default": 1.0
        }
        industry = context.get("industry", "default")
        multiplier *= industry_factors.get(industry, 1.0)
        
        # Quarter-end boost (deals often close faster)
        is_quarter_end = context.get("is_quarter_end", False)
        if is_quarter_end:
            multiplier *= 1.15
        
        return multiplier
```

---

## 3.4 Customer Health Adapter

```python
# lib/intelligence/adapters/health.py
"""
Customer Health Domain Adapter: Churn risk, retention, satisfaction.
"""

from typing import Dict
from .base import BaseDomainAdapter
from ..types import Domain


class HealthAdapter(BaseDomainAdapter):
    """
    Adapter for customer health metrics.
    
    Signal: Engagement recency × activity frequency × satisfaction score
    Baseline: Contract value weighted benchmark
    Context: Account age, product usage, support history
    """
    
    domain = Domain.HEALTH
    
    def to_signal(self, event: Dict) -> float:
        """
        Convert health event to signal.
        
        Signal combines:
        - Recency: days since last engagement (inverted)
        - Frequency: actions per month
        - Satisfaction: NPS or CSAT score
        """
        days_since_active = event.get("days_since_active", 30)
        monthly_actions = event.get("monthly_actions", 10)
        nps_score = event.get("nps_score", 50)
        
        # Recency score (higher = more recent)
        recency_score = max(0, 1 - (days_since_active / 90))  # 0-1 scale
        
        # Frequency score (normalized to expected)
        expected_actions = event.get("expected_monthly_actions", 10)
        frequency_score = min(2.0, monthly_actions / max(expected_actions, 1))
        
        # Satisfaction score (normalized from NPS -100 to 100 → 0 to 1)
        satisfaction_score = (nps_score + 100) / 200
        
        # Combined signal
        signal = recency_score * frequency_score * (0.5 + satisfaction_score)
        
        return signal
    
    def to_baseline(self, context: Dict) -> float:
        """
        Calculate expected health baseline.
        
        Baseline considers:
        - Contract value tier
        - Account age
        - Historical retention rate
        """
        contract_value = context.get("contract_value", 10000)
        account_age_months = context.get("account_age_months", 12)
        segment_retention = context.get("segment_retention_rate", 0.85)
        
        # Higher value = higher expectations
        if contract_value > 50000:
            value_factor = 1.2
        elif contract_value > 10000:
            value_factor = 1.0
        else:
            value_factor = 0.8
        
        # Newer accounts have lower baselines (less established)
        if account_age_months < 3:
            age_factor = 0.7
        elif account_age_months < 12:
            age_factor = 0.9
        else:
            age_factor = 1.0
        
        baseline = value_factor * age_factor * segment_retention
        
        return baseline
    
    def get_context_multiplier(self, context: Dict) -> float:
        """
        Calculate context multiplier for health.
        
        Considers:
        - Recent support tickets (negative)
        - Feature adoption (positive)
        - Expansion signals (positive)
        """
        multiplier = 1.0
        
        # Support ticket impact
        recent_tickets = context.get("support_tickets_30d", 0)
        if recent_tickets > 5:
            multiplier *= 0.7
        elif recent_tickets > 2:
            multiplier *= 0.85
        
        # Feature adoption
        features_used = context.get("features_used_pct", 0.5)
        multiplier *= (0.8 + 0.4 * features_used)  # 0.8-1.2 range
        
        # Expansion signals
        has_expansion_signal = context.get("expansion_interest", False)
        if has_expansion_signal:
            multiplier *= 1.2
        
        return multiplier
```

---

# PHASE 4: Integration with WorkflowRunner

## 4.1 Intelligence Engine (Main Interface)

```python
# lib/intelligence/__init__.py
"""
MH1 Intelligence System: Main interface.

Usage:
    from lib.intelligence import IntelligenceEngine
    
    engine = IntelligenceEngine()
    
    # Before skill execution
    guidance = engine.get_guidance("dormant-detection", tenant_id, Domain.REVENUE)
    prediction = engine.register_prediction(skill, tenant_id, expected, baseline)
    
    # After skill execution
    engine.record_outcome(prediction_id, observed_signal, goal_completed)
"""

from typing import Dict, Optional
from datetime import datetime, timezone

from .types import (
    Prediction, Outcome, Guidance, Domain,
    EpisodicMemory, SemanticPattern
)
from .memory.working import WorkingMemory
from .memory.episodic import EpisodicMemoryStore
from .memory.semantic import SemanticMemoryStore
from .memory.procedural import ProceduralMemoryStore
from .memory.consolidation import MemoryConsolidationManager
from .learning.predictor import Predictor
from .learning.learner import Learner
from .adapters.base import BaseDomainAdapter, ScoringResult
from .adapters.content import ContentAdapter
from .adapters.revenue import RevenueAdapter
from .adapters.health import HealthAdapter
from .adapters.campaign import CampaignAdapter


class IntelligenceEngine:
    """
    Main interface to the MH1 Intelligence System.
    
    Provides:
    - Guidance for skill execution (with learning)
    - Prediction registration
    - Outcome recording
    - Domain-agnostic scoring
    """
    
    def __init__(self, firebase_client=None):
        """
        Initialize the intelligence engine.
        
        Args:
            firebase_client: FirebaseClient instance (lazy loaded if not provided)
        """
        if firebase_client is None:
            from lib.firebase_client import get_firebase_client
            firebase_client = get_firebase_client()
        
        self.firebase = firebase_client
        
        # Initialize memory layers
        self.working = WorkingMemory()
        self.episodic = EpisodicMemoryStore(firebase_client)
        self.semantic = SemanticMemoryStore(firebase_client)
        self.procedural = ProceduralMemoryStore(firebase_client)
        
        # Initialize consolidation manager
        self.consolidation = MemoryConsolidationManager(
            self.episodic,
            self.semantic,
            self.procedural
        )
        
        # Initialize learning components
        self.predictor = Predictor(self.semantic, self.procedural)
        self.learner = Learner(self.episodic, self.semantic)
        
        # Initialize domain adapters
        self.adapters: Dict[Domain, BaseDomainAdapter] = {
            Domain.CONTENT: ContentAdapter(),
            Domain.REVENUE: RevenueAdapter(),
            Domain.HEALTH: HealthAdapter(),
            Domain.CAMPAIGN: CampaignAdapter(),
        }
    
    def get_guidance(
        self,
        skill_name: str,
        tenant_id: str,
        domain: Domain,
        context: Dict = None
    ) -> Guidance:
        """
        Get guidance for a skill execution.
        
        This is the main entry point for skills to get learned recommendations.
        """
        context = context or {}
        
        return self.predictor.get_guidance(
            skill_name=skill_name,
            tenant_id=tenant_id,
            domain=domain,
            context=context
        )
    
    def register_prediction(
        self,
        skill_name: str,
        tenant_id: str,
        domain: Domain,
        expected_signal: float,
        expected_baseline: float,
        confidence: float = 0.5,
        context: Dict = None,
        guidance: Guidance = None
    ) -> str:
        """
        Register a prediction before skill execution.
        
        Returns:
            prediction_id for later outcome recording
        """
        prediction = Prediction(
            skill_name=skill_name,
            tenant_id=tenant_id,
            domain=domain,
            expected_signal=expected_signal,
            expected_baseline=expected_baseline,
            confidence=confidence,
            context=context or {},
            patterns_used=guidance.patterns_used if guidance else [],
            is_exploration=guidance.is_exploration if guidance else False,
        )
        
        return self.working.register_prediction(prediction)
    
    def record_outcome(
        self,
        prediction_id: str,
        observed_signal: float,
        observed_baseline: float = None,
        goal_completed: bool = False,
        business_impact: float = 0.0,
        metadata: Dict = None
    ) -> Dict:
        """
        Record an outcome after skill execution.
        
        This triggers:
        1. Working → Episodic memory transfer
        2. Pattern confidence updates
        3. Concept drift checking
        
        Returns:
            Result dict with learning updates
        """
        prediction = self.working.get_prediction(prediction_id)
        if not prediction:
            return {"error": "Prediction not found", "prediction_id": prediction_id}
        
        outcome = Outcome(
            prediction_id=prediction_id,
            observed_signal=observed_signal,
            observed_baseline=observed_baseline or prediction.expected_baseline,
            goal_completed=goal_completed,
            business_impact=business_impact,
            metadata=metadata or {}
        )
        
        # Complete prediction in working memory (creates episodic memory)
        episode = self.working.complete_prediction(prediction_id, outcome)
        
        if episode:
            # Store to episodic memory
            self.episodic.store(episode)
            
            # Learn from outcome
            learning_result = self.learner.learn_from_outcome(prediction, outcome)
            
            return {
                "success": True,
                "episode_id": episode.episode_id,
                "prediction_error": outcome.prediction_error,
                **learning_result
            }
        
        return {"success": False, "error": "Failed to create episode"}
    
    def score(
        self,
        domain: Domain,
        event: Dict,
        context: Dict
    ) -> ScoringResult:
        """
        Calculate universal score for a domain event.
        
        Uses the formula: Score = (Signal / Baseline) × Context × Confidence
        """
        adapter = self.adapters.get(domain)
        if not adapter:
            # Fall back to generic scoring
            signal = event.get("signal", event.get("value", 1.0))
            baseline = context.get("baseline", 1.0)
            return ScoringResult(
                score=signal / baseline if baseline > 0 else signal,
                signal=signal,
                baseline=baseline,
                context_multiplier=1.0,
                confidence=1.0,
                components={},
                explanation="Generic scoring (no domain adapter)"
            )
        
        return adapter.calculate_score(event, context)
    
    def run_consolidation(self, tenant_id: str = None) -> Dict:
        """
        Run memory consolidation cycle.
        
        Should be called periodically (e.g., daily via scheduler).
        """
        return self.consolidation.run_consolidation_cycle(tenant_id)
    
    def clear_session(self):
        """Clear working memory (end of session)."""
        self.working.clear()
```

---

## 4.2 WorkflowRunner Integration

```python
# Addition to lib/runner.py

# Add to imports at top of file:
# from lib.intelligence import IntelligenceEngine, Domain

class WorkflowRunner:
    """
    Executes workflows with intelligence integration.
    """

    def __init__(self, workflow_name: str, version: str = "v1.0.0", 
                 client: str = None, tenant_id: str = None):
        # ... existing init code ...
        
        # NEW: Initialize intelligence engine
        self._intelligence = None  # Lazy loaded
    
    @property
    def intelligence(self):
        """Lazy-load intelligence engine."""
        if self._intelligence is None:
            from lib.intelligence import IntelligenceEngine
            self._intelligence = IntelligenceEngine()
        return self._intelligence
    
    def get_guidance(self, domain: str = "generic", context: Dict = None) -> Dict:
        """
        Get learned guidance for this workflow.
        
        Usage in workflow:
            guidance = runner.get_guidance("revenue", {"segment": "enterprise"})
            threshold = guidance.parameters.get("threshold_days", 30)
        """
        from lib.intelligence.types import Domain
        
        domain_enum = Domain(domain)
        guidance = self.intelligence.get_guidance(
            skill_name=self.workflow_name,
            tenant_id=self.tenant_id,
            domain=domain_enum,
            context=context or {}
        )
        
        return guidance.to_dict()
    
    def register_prediction(
        self,
        expected_signal: float,
        expected_baseline: float,
        domain: str = "generic",
        context: Dict = None
    ) -> str:
        """
        Register a prediction for this workflow execution.
        
        Call before the main execution to track predictions.
        """
        from lib.intelligence.types import Domain
        
        domain_enum = Domain(domain)
        return self.intelligence.register_prediction(
            skill_name=self.workflow_name,
            tenant_id=self.tenant_id,
            domain=domain_enum,
            expected_signal=expected_signal,
            expected_baseline=expected_baseline,
            context=context or {}
        )
    
    def record_outcome(
        self,
        prediction_id: str,
        observed_signal: float,
        goal_completed: bool = False,
        metadata: Dict = None
    ) -> Dict:
        """
        Record the outcome after workflow execution.
        
        This enables the system to learn from results.
        """
        return self.intelligence.record_outcome(
            prediction_id=prediction_id,
            observed_signal=observed_signal,
            goal_completed=goal_completed,
            metadata=metadata or {}
        )
```

---

# PHASE 5: Configuration Files

## 5.1 Memory Configuration

```yaml
# config/intelligence/memory_config.yml
# Configuration for the multi-layer memory system

working_memory:
  max_recent_outcomes: 10
  max_active_predictions: 5

episodic_memory:
  decay_rate: 0.95              # Per-day decay
  relevance_threshold: 0.3      # Below this, consolidate
  max_episodes_per_skill: 1000  # Per skill/tenant
  ttl_days: 90                  # Days before archival
  consolidation_threshold: 10   # Episodes before pattern extraction

semantic_memory:
  initial_confidence: 0.5
  learning_rate: 0.1
  decay_rate: 0.99              # Per-day without reinforcement
  min_confidence: 0.01
  max_confidence: 0.99
  forget_threshold: 0.1         # Below this, archive
  min_evidence_for_trust: 5

procedural_memory:
  cross_skill_threshold: 3      # Skills needed for procedural
  cross_skill_min_confidence: 0.6

consolidation:
  schedule: "0 3 * * *"         # Daily at 3 AM
  batch_size: 100
```

## 5.2 Domain Adapters Configuration

```yaml
# config/semantic_layer/domain_adapters.yml
# Configuration for domain-specific scoring adapters

domains:
  content:
    description: "Engagement, impressions, and growth metrics"
    signal_formula: "impressions * (1 + engagement_rate)"
    baseline_formula: "follower_count * platform_rate * decay_factor"
    gcr_threshold: 1.0  # Signal/Baseline ratio for goal completion
    
    platforms:
      linkedin:
        engagement_rate: 0.02
        impression_rate: 0.10
        decay_half_life_hours: 24
      twitter:
        engagement_rate: 0.015
        impression_rate: 0.08
        decay_half_life_hours: 4
      instagram:
        engagement_rate: 0.03
        impression_rate: 0.15
        decay_half_life_hours: 12
      email:
        engagement_rate: 0.20
        impression_rate: 0.25
        decay_half_life_hours: 48

  revenue:
    description: "Deal velocity, pipeline health, and conversion"
    signal_formula: "expected_days / actual_days"
    baseline_formula: "segment_benchmark * historical_multiplier"
    gcr_threshold: 1.0
    
    segments:
      enterprise:
        lead_to_mql_days: 14
        mql_to_sql_days: 21
        sql_to_opportunity_days: 30
        opportunity_to_close_days: 60
      mid_market:
        lead_to_mql_days: 7
        mql_to_sql_days: 14
        sql_to_opportunity_days: 21
        opportunity_to_close_days: 30
      smb:
        lead_to_mql_days: 3
        mql_to_sql_days: 7
        sql_to_opportunity_days: 14
        opportunity_to_close_days: 14

  health:
    description: "Customer health, churn risk, and retention"
    signal_formula: "recency * frequency * (0.5 + satisfaction)"
    baseline_formula: "contract_tier * age_factor * segment_retention"
    gcr_threshold: 0.8  # Health threshold for "healthy" status
    
    risk_thresholds:
      high_risk: 0.3
      medium_risk: 0.6
      low_risk: 0.8

  campaign:
    description: "Campaign ROI, attribution, and efficiency"
    signal_formula: "conversions / spend * 1000"  # Cost per acquisition
    baseline_formula: "target_cpa * (1 + seasonal_factor)"
    gcr_threshold: 1.0  # Below target CPA = goal achieved
```

---

# Implementation Timeline

| Phase | Components | Estimated Effort |
|-------|-----------|------------------|
| **Phase 1** | Multi-Layer Memory (types, working, episodic, semantic, procedural, consolidation) | ~800 lines |
| **Phase 2** | Continuous Learning (predictor, learner, drift detector) | ~400 lines |
| **Phase 3** | Domain Adapters (base, content, revenue, health, campaign) | ~500 lines |
| **Phase 4** | Integration (engine, runner integration) | ~200 lines |
| **Phase 5** | Configuration (YAML files) | ~150 lines |
| **Total** | | **~2,050 lines** |

Plus: BrightMatter infrastructure (~700 lines) = **~2,750 total lines**

---

# Firebase Data Structure

```
Firebase Firestore Structure:
────────────────────────────────────────
system/
├── intelligence/
│   ├── episodic/
│   │   └── {tenant_id}/
│   │       └── {skill_name}/
│   │           └── {episode_id}: EpisodicMemory
│   │
│   ├── semantic/
│   │   └── {domain}/
│   │       └── patterns/
│   │           └── {pattern_id}: SemanticPattern
│   │
│   ├── procedural/
│   │   └── {knowledge_id}: ProceduralKnowledge
│   │
│   └── archive/
│       ├── episodic/{tenant_id}/{skill_name}/{episode_id}
│       └── semantic/{domain}/{pattern_id}
│
└── brain/
    ├── learning_state: { last_consolidation, drift_alerts }
    └── health_check: { last_check, status }
```

---

# Summary: What Makes This Innovative

| Capability | BrightMatter (Original) | MH1 Intelligence (New) |
|------------|------------------------|------------------------|
| Memory | Single-layer logging | 4-layer cognitive architecture |
| Learning | Records data only | Bayesian updates from outcomes |
| Forgetting | None (accumulates forever) | Temporal decay + relevance pruning |
| Exploration | None | 15% exploration + uncertainty-guided |
| Drift Detection | None | Statistical drift detection + relearning |
| Cross-Skill | None | Procedural knowledge transfer |
| Scoring | Domain-locked formula | Universal Signal/Baseline/Context |

This architecture transforms MH1 from a **logging system** to a **true self-improving intelligence system** that:
1. **Learns** from every skill execution
2. **Forgets** outdated patterns automatically
3. **Adapts** when the world changes (concept drift)
4. **Generalizes** patterns across skills and clients
5. **Explores** to discover new optimal strategies

---

# Next Steps

1. Review this plan for completeness
2. Implement Phase 1 (Memory System) first
3. Add Firebase security rules
4. Implement scheduled consolidation job
5. Integrate with existing skills (lifecycle-audit as pilot)
6. Monitor and tune learning parameters

