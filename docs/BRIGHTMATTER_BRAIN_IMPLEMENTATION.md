# BrightMatter Brain Implementation Plan for MH1

**Date:** January 28, 2026  
**Status:** Draft  
**Scope:** Intelligence layer, learning system, scoring, insights generation

---

## Executive Summary

This plan adapts BrightMatter's compound learning and intelligence architecture to become the "brain" behind MH1-HQ. We extract the following from the whitepaper (excluding crypto, rewards, blockchain):

1. **Intelligent Resonance Layer (IRL)** → MH1 Intelligence Engine
2. **Compound Learning Architecture** → Self-improving skill system
3. **Resonance Scoring** → Marketing Performance Scoring
4. **Next Best Moves (NBMs)** → AI-generated marketing recommendations
5. **Feed/Cohort System** → Client/Campaign management
6. **Reporting Layer** → Automated insights and projections

---

## Architecture Mapping

### BrightMatter → MH1 Translation

| BrightMatter Concept | MH1 Equivalent | Implementation |
|---------------------|----------------|----------------|
| Veri (Interface Layer) | MH1 CLI/UI | Current `mh1` CLI + `ui/` dashboard |
| Creator/Studio | Client/Campaign | `clients/{clientId}/` directory |
| Intelligent Resonance Layer | MH1 Intelligence Engine | New `lib/intelligence/` module |
| Oracle Feeds | Data Sources | CRM, Warehouse, Analytics MCPs |
| Private Cohorts | Client Campaigns | Firebase `clients` collection |
| Resonance Score | Performance Score | New scoring system |
| Next Best Moves (NBMs) | Marketing Recommendations | New skill: `generate-recommendations` |
| Template Processing | Skill Execution | Current skills system |
| Compound Learning | Self-improving models | New learning loop |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           MH1 INTELLIGENCE ENGINE                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │   INGEST     │───▶│   ANALYZE    │───▶│    SCORE     │              │
│  │   Layer      │    │   Layer      │    │    Layer     │              │
│  └──────────────┘    └──────────────┘    └──────────────┘              │
│         │                   │                   │                        │
│         ▼                   ▼                   ▼                        │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │   GENERATE   │◀───│   LEARN      │◀───│   REPORT     │              │
│  │   (NBMs)     │    │   (Feedback) │    │   (Insights) │              │
│  └──────────────┘    └──────────────┘    └──────────────┘              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                                     │
├──────────────────┬──────────────────┬───────────────────────────────────┤
│  Firebase        │  CRM (HubSpot,   │  Data Warehouse                   │
│  (Client State)  │  Salesforce...)  │  (Snowflake, BigQuery...)         │
└──────────────────┴──────────────────┴───────────────────────────────────┘
```

---

## Phase 1: Foundation - Intelligence Engine Core

### 1.1 Create Intelligence Engine Module

**Location:** `lib/intelligence/`

```python
# lib/intelligence/__init__.py
from .engine import IntelligenceEngine
from .scoring import PerformanceScorer
from .learning import LearningLoop
from .recommendations import RecommendationGenerator
```

**Core Components:**

```python
# lib/intelligence/engine.py
"""
MH1 Intelligence Engine
Adapted from BrightMatter's Intelligent Resonance Layer (IRL)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class IntelligenceConfig:
    """Configuration for the intelligence engine."""
    model_version: str = "1.0.0"
    learning_rate: float = 0.01
    batch_size: int = 100
    prediction_horizons: List[str] = field(default_factory=lambda: ["24h", "7d", "30d"])
    scoring_weights: Dict[str, float] = field(default_factory=lambda: {
        "engagement": 0.3,
        "quality": 0.25,
        "authenticity": 0.25,
        "growth": 0.2
    })

class IntelligenceEngine:
    """
    Main intelligence engine for MH1.
    
    Responsibilities:
    - Ingest marketing data from multiple sources
    - Analyze and score content/campaign performance
    - Generate predictions and recommendations
    - Learn from outcomes to improve predictions
    """
    
    def __init__(self, config: IntelligenceConfig):
        self.config = config
        self.scorer = PerformanceScorer(config.scoring_weights)
        self.learner = LearningLoop(config.learning_rate)
        self.recommender = RecommendationGenerator()
        self.knowledge_graph = KnowledgeGraph()
        
    async def ingest(self, source: str, data: Dict) -> Dict:
        """Ingest data from CRM, warehouse, or analytics."""
        normalized = self._normalize(source, data)
        self.knowledge_graph.update(normalized)
        return normalized
        
    async def analyze(self, client_id: str) -> AnalysisResult:
        """Analyze client's current state."""
        data = await self._gather_client_data(client_id)
        scores = self.scorer.score(data)
        predictions = self._generate_predictions(data, scores)
        return AnalysisResult(scores=scores, predictions=predictions)
        
    async def generate_recommendations(self, client_id: str) -> List[Recommendation]:
        """Generate Next Best Moves (NBMs) for client."""
        analysis = await self.analyze(client_id)
        return self.recommender.generate(analysis)
        
    async def learn(self, outcome: Outcome):
        """Update weights based on prediction vs observation."""
        delta = outcome.observed - outcome.predicted
        self.learner.update_weights(delta)
```

### 1.2 Performance Scoring System

**Adapted from BrightMatter's Resonance Scoring (Section 6)**

```python
# lib/intelligence/scoring.py
"""
Performance Scoring System
Adapted from BrightMatter's V' = f(E', I', T', G, Q', A, C)
"""

from dataclasses import dataclass
from typing import Dict, Optional
import math

@dataclass
class PerformanceScore:
    """Composite performance score for marketing content/campaigns."""
    overall: float  # 0-100
    engagement: float  # E' - normalized engagement
    reach: float  # I' - normalized impressions/reach
    temporal: float  # T' - time-weighted performance
    growth: float  # G - growth trajectory
    quality: float  # Q' - content quality index
    authenticity: float  # A - authenticity factor
    confidence: float  # C - confidence coefficient
    
class PerformanceScorer:
    """
    Scores marketing content and campaigns.
    
    Formula (adapted from BrightMatter):
    V' = w1*E' + w2*I' + w3*T' + w4*G + w5*Q' + w6*A
    
    Where:
    - E' = Normalized engagement (likes, comments, shares / followers)
    - I' = Normalized reach (impressions / baseline)
    - T' = Temporal weight (decay-adjusted recency)
    - G = Growth coefficient (velocity of engagement)
    - Q' = Quality index (sentiment + consistency + relevance)
    - A = Authenticity factor (1 - bot_ratio - coord_ratio)
    """
    
    # Platform-specific normalization baselines (from BrightMatter 6.2.2)
    PLATFORM_BASELINES = {
        "linkedin": {"engagement_rate": 0.02, "decay_rate": 0.01},
        "twitter": {"engagement_rate": 0.015, "decay_rate": 0.22},
        "instagram": {"engagement_rate": 0.03, "decay_rate": 0.12},
        "youtube": {"engagement_rate": 0.02, "decay_rate": 0.003},
        "tiktok": {"engagement_rate": 0.05, "decay_rate": 0.35},
        "email": {"open_rate": 0.20, "click_rate": 0.025, "decay_rate": 0.5},
    }
    
    def __init__(self, weights: Dict[str, float]):
        self.weights = weights
        
    def score(self, data: Dict) -> PerformanceScore:
        """Calculate composite performance score."""
        e_prime = self._calculate_engagement(data)
        i_prime = self._calculate_reach(data)
        t_prime = self._calculate_temporal(data)
        g = self._calculate_growth(data)
        q_prime = self._calculate_quality(data)
        a = self._calculate_authenticity(data)
        c = self._calculate_confidence(data)
        
        # Composite score (0-100 scale)
        overall = (
            self.weights["engagement"] * e_prime +
            self.weights.get("reach", 0.15) * i_prime +
            self.weights.get("temporal", 0.1) * t_prime +
            self.weights["growth"] * g +
            self.weights["quality"] * q_prime +
            self.weights["authenticity"] * a
        ) * 100
        
        return PerformanceScore(
            overall=min(100, max(0, overall)),
            engagement=e_prime,
            reach=i_prime,
            temporal=t_prime,
            growth=g,
            quality=q_prime,
            authenticity=a,
            confidence=c
        )
        
    def _calculate_engagement(self, data: Dict) -> float:
        """
        Normalized engagement rate.
        E' = (E/F) / μ_p where μ_p is platform baseline.
        """
        platform = data.get("platform", "email")
        baseline = self.PLATFORM_BASELINES.get(platform, {})
        
        engagements = data.get("engagements", 0)
        audience = data.get("audience_size", 1)
        
        raw_rate = engagements / max(audience, 1)
        baseline_rate = baseline.get("engagement_rate", 0.02)
        
        return min(2.0, raw_rate / baseline_rate)  # Cap at 2x baseline
        
    def _calculate_quality(self, data: Dict) -> float:
        """
        Quality index from BrightMatter 6.4.1:
        Q' = 0.4*S + 0.3*C + 0.3*R
        
        S = sentiment score (0-1)
        C = consistency (posting frequency vs optimal)
        R = relevance alignment
        """
        sentiment = data.get("sentiment_score", 0.5)
        consistency = data.get("consistency_score", 0.5)
        relevance = data.get("relevance_score", 0.5)
        
        q_prime = 0.4 * sentiment + 0.3 * consistency + 0.3 * relevance
        
        # Bound between 0.7 and 1.3 (from BrightMatter)
        return max(0.7, min(1.3, q_prime + 0.5))
        
    def _calculate_authenticity(self, data: Dict) -> float:
        """
        Authenticity factor from BrightMatter 6.4.2:
        A = max(0.3, 1 - 0.5*B - 0.4*Sc - 0.3*Tc)
        
        B = bot ratio
        Sc = coordinated share ratio
        Tc = temporal coherence penalty
        """
        bot_ratio = data.get("bot_ratio", 0)
        coord_ratio = data.get("coordinated_ratio", 0)
        temporal_penalty = data.get("temporal_anomaly", 0)
        
        a = 1 - 0.5 * bot_ratio - 0.4 * coord_ratio - 0.3 * temporal_penalty
        return max(0.3, a)
```

### 1.3 Firebase Schema Extension

**Location:** Firebase Firestore

```javascript
// Firebase schema for intelligence data

// clients/{clientId}/intelligence
{
  "model_version": "1.0.0",
  "last_analysis": "2026-01-28T12:00:00Z",
  "current_scores": {
    "overall": 72.5,
    "engagement": 0.85,
    "quality": 1.1,
    "authenticity": 0.95,
    "growth": 0.7,
    "confidence": 0.88
  },
  "predictions": {
    "24h": {
      "engagement_delta": 0.05,
      "confidence": 0.82
    },
    "7d": {
      "engagement_delta": 0.12,
      "confidence": 0.75
    },
    "30d": {
      "engagement_delta": 0.25,
      "confidence": 0.65
    }
  },
  "learning_state": {
    "weights": {...},
    "iteration": 1542,
    "last_update": "2026-01-28T11:00:00Z"
  }
}

// clients/{clientId}/recommendations
[
  {
    "id": "nbm_001",
    "type": "CONTENT",
    "action": "Post LinkedIn article on industry trends",
    "confidence": 0.85,
    "estimated_impact": {
      "engagement": "+15%",
      "reach": "+500"
    },
    "effort": "medium",
    "priority": "high",
    "reasoning": "Based on 7-day engagement velocity and content gap analysis",
    "status": "pending",
    "created_at": "2026-01-28T10:00:00Z"
  }
]

// clients/{clientId}/outcomes
[
  {
    "recommendation_id": "nbm_001",
    "predicted": {
      "engagement": 0.85,
      "reach": 1500
    },
    "observed": {
      "engagement": 0.92,
      "reach": 1750
    },
    "delta": {
      "engagement": 0.07,
      "reach": 250
    },
    "recorded_at": "2026-01-30T12:00:00Z"
  }
]
```

---

## Phase 2: Learning System

### 2.1 Compound Learning Loop

**Adapted from BrightMatter Section 5 (Compound Learning)**

```python
# lib/intelligence/learning.py
"""
Compound Learning System
Adapted from BrightMatter's weight update rule:
w_{t+1} = w_t + η(R_observed - R_predicted)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import json
from datetime import datetime

@dataclass
class Outcome:
    """Observed outcome vs prediction."""
    recommendation_id: str
    predicted: Dict[str, float]
    observed: Dict[str, float]
    timestamp: datetime
    
    @property
    def delta(self) -> Dict[str, float]:
        return {
            k: self.observed.get(k, 0) - self.predicted.get(k, 0)
            for k in self.predicted.keys()
        }

class LearningLoop:
    """
    Continuous learning system that improves predictions.
    
    From BrightMatter:
    - Online learning updates weights after each observation
    - Shadow mode tests new model versions
    - Gold standard datasets validate changes
    """
    
    def __init__(self, learning_rate: float = 0.01):
        self.learning_rate = learning_rate
        self.weights = self._load_weights()
        self.iteration = 0
        self.shadow_candidate = None
        
    def update_weights(self, outcome: Outcome):
        """
        Update model weights based on prediction error.
        
        Rule: w_{t+1} = w_t + η * (observed - predicted)
        """
        for metric, delta in outcome.delta.items():
            if metric in self.weights:
                self.weights[metric] += self.learning_rate * delta
                
        self.iteration += 1
        self._save_weights()
        
        # Check if we should spawn shadow candidate
        if self.iteration % 100 == 0:
            self._evaluate_for_shadow_mode()
            
    def _evaluate_for_shadow_mode(self):
        """
        Spawn shadow candidate if performance drift detected.
        (From BrightMatter 4.3)
        """
        recent_errors = self._get_recent_errors(window=50)
        mean_error = sum(recent_errors) / len(recent_errors) if recent_errors else 0
        
        if mean_error > 0.15:  # 15% average error threshold
            self.shadow_candidate = self._create_candidate()
            
    def _create_candidate(self) -> Dict:
        """Create shadow model candidate with adjusted weights."""
        return {
            "version": f"shadow_{self.iteration}",
            "weights": self.weights.copy(),
            "created_at": datetime.now().isoformat(),
            "status": "testing"
        }
        
    def promote_candidate(self, candidate_version: str):
        """Promote shadow candidate to production after validation."""
        if self.shadow_candidate and self.shadow_candidate["version"] == candidate_version:
            self.weights = self.shadow_candidate["weights"]
            self.shadow_candidate = None
            self._save_weights()
```

### 2.2 Knowledge Graph

**Adapted from BrightMatter 4.1.2**

```python
# lib/intelligence/knowledge_graph.py
"""
Knowledge Graph for storing relationships and embeddings.
Integrates with existing knowledge/knowledge_base/ structure.
"""

from typing import Dict, List, Optional
from pathlib import Path
import json

class KnowledgeGraph:
    """
    Maintains relationships between:
    - Clients and their performance history
    - Content types and their effectiveness
    - Platforms and their engagement patterns
    - Industry benchmarks and trends
    """
    
    def __init__(self, base_path: str = "knowledge/knowledge_base"):
        self.base_path = Path(base_path)
        self.nodes = {}
        self.edges = {}
        self.embeddings = {}
        
    def update(self, data: Dict):
        """Update graph with new data."""
        node_type = data.get("type", "unknown")
        node_id = data.get("id")
        
        if node_id:
            self.nodes[node_id] = {
                "type": node_type,
                "data": data,
                "updated_at": datetime.now().isoformat()
            }
            
            # Update relationships
            for relation, target in data.get("relations", {}).items():
                self._add_edge(node_id, target, relation)
                
    def query(self, node_type: str = None, filters: Dict = None) -> List[Dict]:
        """Query nodes by type and filters."""
        results = []
        for node_id, node in self.nodes.items():
            if node_type and node["type"] != node_type:
                continue
            if filters:
                if all(node["data"].get(k) == v for k, v in filters.items()):
                    results.append(node)
            else:
                results.append(node)
        return results
        
    def get_related(self, node_id: str, relation: str = None) -> List[str]:
        """Get related nodes."""
        edges = self.edges.get(node_id, [])
        if relation:
            return [e["target"] for e in edges if e["relation"] == relation]
        return [e["target"] for e in edges]
```

---

## Phase 3: Recommendation Engine (NBMs)

### 3.1 Next Best Moves Generator

**Adapted from BrightMatter's NBM system**

```python
# lib/intelligence/recommendations.py
"""
Next Best Moves (NBM) Generator
Adapted from BrightMatter's recommendation system.

Move Types (from BrightMatter 6.5):
- Standard NBMs (1.25x weight): Model-generated recommendations
- Validation Moves (1.50x weight): Hypothesis testing moves
- Self-Generated (1.15x weight): User-initiated actions
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

class MoveType(Enum):
    STANDARD = "standard"  # 1.25x weight
    VALIDATION = "validation"  # 1.50x weight
    SELF_GENERATED = "self_generated"  # 1.15x weight

class ReasonCode(Enum):
    """Marketing action reason codes."""
    REENGAGEMENT = "reengagement"  # Reactivate dormant users
    CONVERSION = "conversion"  # Turn engagement into sales
    RETENTION = "retention"  # Reduce churn risk
    UPSELL = "upsell"  # Upgrade to higher tier
    ADVOCACY = "advocacy"  # Activate power users
    WIN_BACK = "win_back"  # Recover churned accounts
    ONBOARDING = "onboarding"  # Welcome new customers
    DISCOVERY = "discovery"  # Gather information

@dataclass
class Recommendation:
    """A Next Best Move recommendation."""
    id: str
    type: MoveType
    reason_code: ReasonCode
    action: str
    description: str
    confidence: float
    estimated_impact: Dict[str, float]
    effort: str  # low, medium, high
    priority: str  # low, medium, high, critical
    reasoning: str
    prerequisites: List[str] = None
    deadline: str = None
    
class RecommendationGenerator:
    """
    Generates Next Best Moves based on analysis.
    
    Process:
    1. Analyze current state (scores, trends)
    2. Identify gaps and opportunities
    3. Match to recommendation templates
    4. Score and rank recommendations
    5. Return top N recommendations
    """
    
    def __init__(self):
        self.templates = self._load_templates()
        
    def generate(self, analysis: 'AnalysisResult', limit: int = 5) -> List[Recommendation]:
        """Generate recommendations based on analysis."""
        candidates = []
        
        # Check each reason code
        for reason_code in ReasonCode:
            if self._should_recommend(reason_code, analysis):
                rec = self._create_recommendation(reason_code, analysis)
                candidates.append(rec)
                
        # Score and rank
        scored = [(r, self._score_recommendation(r, analysis)) for r in candidates]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return [r for r, _ in scored[:limit]]
        
    def _should_recommend(self, reason_code: ReasonCode, analysis: 'AnalysisResult') -> bool:
        """Determine if a recommendation type applies."""
        scores = analysis.scores
        
        rules = {
            ReasonCode.REENGAGEMENT: scores.engagement < 0.6,
            ReasonCode.CONVERSION: scores.engagement > 0.8 and scores.growth > 0.5,
            ReasonCode.RETENTION: scores.authenticity < 0.7 or analysis.churn_risk > 0.3,
            ReasonCode.UPSELL: scores.overall > 80 and analysis.tier_upgrade_ready,
            ReasonCode.ADVOCACY: scores.quality > 1.1 and scores.engagement > 0.9,
            ReasonCode.WIN_BACK: analysis.is_churned and analysis.reactivation_potential > 0.5,
            ReasonCode.ONBOARDING: analysis.is_new_client,
            ReasonCode.DISCOVERY: analysis.data_completeness < 0.5,
        }
        
        return rules.get(reason_code, False)
```

### 3.2 New Skill: generate-recommendations

```yaml
# skills/generate-recommendations/SKILL.md
---
name: generate-recommendations
description: |
  Generate AI-powered Next Best Moves (NBMs) for marketing campaigns.
  Use when asked to 'recommend actions', 'what should we do next', 
  'generate recommendations', 'suggest improvements', or 'prioritize tasks'.
license: Proprietary
compatibility:
  - Firebase MCP
  - HubSpot MCP (optional)
  - Snowflake MCP (optional)
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  estimated_runtime: "30s-2min"
  max_cost: "$0.50"
  client_facing: true
  requires_human_review: true
  tags:
    - recommendations
    - nbm
    - intelligence
    - strategy
allowed-tools: Read Write CallMcpTool
---

# Generate Recommendations Skill

Generate AI-powered Next Best Moves (NBMs) based on BrightMatter's compound learning system.

## When to Use

- Weekly strategy planning
- After campaign completion (to determine next steps)
- When client asks "what should we do next?"
- After detecting performance changes
- For quarterly planning

## Process

1. **Gather Data**: Pull client's current state from Firebase
2. **Score Performance**: Calculate engagement, quality, authenticity scores
3. **Analyze Trends**: Compare to historical data and benchmarks
4. **Generate NBMs**: Match conditions to recommendation templates
5. **Rank and Filter**: Return top 5 recommendations with confidence scores

## Output Format

```json
{
  "recommendations": [
    {
      "id": "nbm_001",
      "type": "standard",
      "reason_code": "REENGAGEMENT",
      "action": "Launch email nurture sequence for dormant contacts",
      "confidence": 0.85,
      "estimated_impact": {
        "engagement": "+15%",
        "pipeline": "+$50K"
      },
      "effort": "medium",
      "priority": "high",
      "reasoning": "245 contacts inactive for 30+ days with high historical engagement"
    }
  ],
  "analysis_summary": {
    "overall_score": 72.5,
    "primary_gap": "engagement_velocity",
    "top_opportunity": "dormant_reactivation"
  }
}
```
```

---

## Phase 4: Reporting & Insights Layer

### 4.1 Report Generation

**Adapted from BrightMatter's hourly/2-hour reporting**

```python
# lib/intelligence/reporting.py
"""
Automated Report Generation
Adapted from BrightMatter's dual-cadence reporting.
"""

from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime, timedelta

@dataclass
class Report:
    """Intelligence report."""
    report_type: str  # "hourly", "daily", "weekly"
    client_id: str
    generated_at: datetime
    scores: Dict[str, float]
    trends: Dict[str, float]
    predictions: Dict[str, Dict]
    anomalies: List[Dict]
    recommendations: List[Dict]
    
class ReportGenerator:
    """
    Generates reports at different cadences:
    - Hourly: Score updates, anomaly detection
    - Daily: Trend analysis, predictions
    - Weekly: Full analysis, recommendations, benchmarks
    """
    
    def generate_hourly(self, client_id: str) -> Report:
        """Quick score update and anomaly check."""
        scores = self._get_current_scores(client_id)
        anomalies = self._detect_anomalies(client_id)
        
        return Report(
            report_type="hourly",
            client_id=client_id,
            generated_at=datetime.now(),
            scores=scores,
            trends={},
            predictions={},
            anomalies=anomalies,
            recommendations=[]
        )
        
    def generate_daily(self, client_id: str) -> Report:
        """Daily trend analysis with predictions."""
        scores = self._get_current_scores(client_id)
        trends = self._calculate_trends(client_id, window_days=7)
        predictions = self._generate_predictions(client_id, horizons=["24h", "7d"])
        anomalies = self._detect_anomalies(client_id)
        
        return Report(
            report_type="daily",
            client_id=client_id,
            generated_at=datetime.now(),
            scores=scores,
            trends=trends,
            predictions=predictions,
            anomalies=anomalies,
            recommendations=[]
        )
        
    def generate_weekly(self, client_id: str) -> Report:
        """Full weekly analysis with recommendations."""
        scores = self._get_current_scores(client_id)
        trends = self._calculate_trends(client_id, window_days=30)
        predictions = self._generate_predictions(client_id, horizons=["7d", "30d"])
        anomalies = self._detect_anomalies(client_id)
        recommendations = self._generate_recommendations(client_id)
        
        return Report(
            report_type="weekly",
            client_id=client_id,
            generated_at=datetime.now(),
            scores=scores,
            trends=trends,
            predictions=predictions,
            anomalies=anomalies,
            recommendations=recommendations
        )
```

### 4.2 New Skill: intelligence-report

```yaml
# skills/intelligence-report/SKILL.md
---
name: intelligence-report
description: |
  Generate comprehensive intelligence reports with scores, trends, predictions, 
  and recommendations. Use when asked to 'generate report', 'analyze performance',
  'create intelligence brief', or 'weekly summary'.
license: Proprietary
compatibility:
  - Firebase MCP
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  estimated_runtime: "1-3min"
  max_cost: "$0.75"
  client_facing: true
  requires_human_review: false
  tags:
    - intelligence
    - reporting
    - analysis
allowed-tools: Read Write CallMcpTool
---
```

---

## Phase 5: Integration with Existing MH1 Systems

### 5.1 Firebase Integration

Extend existing Firebase MCP to support intelligence data:

```javascript
// Firebase collections for intelligence

// clients/{clientId}/scores (time series)
{
  "timestamp": "2026-01-28T12:00:00Z",
  "overall": 72.5,
  "engagement": 0.85,
  "quality": 1.1,
  "authenticity": 0.95,
  "growth": 0.7,
  "confidence": 0.88
}

// clients/{clientId}/predictions
{
  "generated_at": "2026-01-28T12:00:00Z",
  "horizons": {
    "24h": { "engagement_delta": 0.05, "confidence": 0.82 },
    "7d": { "engagement_delta": 0.12, "confidence": 0.75 },
    "30d": { "engagement_delta": 0.25, "confidence": 0.65 }
  }
}

// clients/{clientId}/learning_state
{
  "model_version": "1.0.0",
  "weights": { ... },
  "iteration": 1542,
  "shadow_candidate": null,
  "last_update": "2026-01-28T11:00:00Z"
}
```

### 5.2 Skill Integration

Update existing skills to feed intelligence engine:

```yaml
# Updates to existing skills

# skills/lifecycle-audit/SKILL.md
# Add at end:
## Intelligence Integration
After audit completion, feed results to intelligence engine:
- Update client scores in Firebase
- Generate predictions
- Trigger recommendation generation if scores changed significantly

# skills/ghostwrite-content/SKILL.md  
# Add at end:
## Learning Loop Integration
After content is published and results are available:
- Record outcome (predicted vs observed engagement)
- Feed to learning loop for weight updates
```

---

## Implementation Timeline

### Week 1: Foundation
- [ ] Create `lib/intelligence/` module structure
- [ ] Implement `PerformanceScorer` class
- [ ] Implement `LearningLoop` class
- [ ] Extend Firebase schema

### Week 2: Recommendations
- [ ] Implement `RecommendationGenerator` class
- [ ] Create `generate-recommendations` skill
- [ ] Define recommendation templates

### Week 3: Reporting
- [ ] Implement `ReportGenerator` class
- [ ] Create `intelligence-report` skill
- [ ] Build report templates

### Week 4: Integration
- [ ] Integrate with Firebase MCP
- [ ] Update existing skills for learning loop
- [ ] Add UI components for intelligence dashboard

### Week 5: Testing & Refinement
- [ ] Test with sample client data
- [ ] Calibrate scoring weights
- [ ] Validate prediction accuracy
- [ ] Document and train

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Prediction Accuracy | >75% within 15% error | Compare predicted vs observed |
| Recommendation Adoption | >60% accepted | Track accepted/rejected NBMs |
| Learning Convergence | <100 iterations to stable | Monitor weight variance |
| Report Usefulness | >4/5 rating | User feedback surveys |

---

## Appendix: Key Formulas from BrightMatter

### Resonance Score (Section 6.1)
```
V' = f(E', I', T', G, Q', A, C)
```

### Quality Index (Section 6.4.1)
```
Q' = 0.4*S + 0.3*C + 0.3*R
```

### Authenticity Factor (Section 6.4.2)
```
A = max(0.3, 1 - 0.5*B - 0.4*Sc - 0.3*Tc)
```

### Learning Update (Section 5)
```
w_{t+1} = w_t + η(R_observed - R_predicted)
```

### Temporal Decay (Section 6.3.1)
```
E_t = E₀ * e^(-λt)
```

### Platform Decay Rates (λ)
- TikTok: 0.35 h⁻¹
- Twitter: 0.22 h⁻¹
- Instagram: 0.12 h⁻¹
- YouTube: 0.003 h⁻¹
- Email: ~0.5 h⁻¹ (estimated)
