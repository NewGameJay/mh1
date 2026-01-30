# BrightMatter Brain: 3-Phase Implementation Plan

**Version:** 1.0 (Pre-Review)  
**Date:** January 28, 2026  
**Status:** Draft for subagent review

---

## Overview

This plan implements the BrightMatter intelligence infrastructure as the "brain" behind MH1-HQ in 3 phases:

1. **Phase 1: Core Engine** - Scoring, ingestion, data layer
2. **Phase 2: Learning & Intelligence** - Compound learning, predictions, recommendations
3. **Phase 3: Automation & Integration** - Reporting, scheduling, UI, existing system integration

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MH1 BRAIN (lib/brain/)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐     │
│  │   INGEST    │──▶│   SCORE     │──▶│   PREDICT   │──▶│  RECOMMEND  │     │
│  │  Gateway    │   │   Engine    │   │   Engine    │   │   (NBMs)    │     │
│  └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘     │
│         │                │                 │                 │              │
│         ▼                ▼                 ▼                 ▼              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    LEARNING LOOP (Compound Learning)                 │   │
│  │    Outcomes → Weight Updates → Shadow Testing → Model Promotion     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         REPORTING ENGINE                             │   │
│  │         Hourly Scores │ Daily Analysis │ Weekly Recommendations     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                      │
├──────────────────┬──────────────────┬───────────────────────────────────────┤
│     Firebase     │   CRM/Warehouse  │        Existing MH1 Libs              │
│   (State Store)  │   (Data Sources) │  (forecasting, knowledge, client)     │
└──────────────────┴──────────────────┴───────────────────────────────────────┘
```

---

# PHASE 1: Core Engine (Weeks 1-2)

## 1.1 Module Structure

Create `lib/brain/` (renamed from `intelligence` to avoid conflict):

```
lib/brain/
├── __init__.py              # Public exports
├── engine.py                # Main BrainEngine orchestrator
├── scoring.py               # PerformanceScorer (BrightMatter V' formula)
├── ingest.py                # EventGateway and FeedRouter
├── templates.py             # ProcessingTemplate system
├── anomaly.py               # AnomalyDetector
├── config.py                # BrainConfig dataclass
└── types.py                 # Type definitions (Score, Event, etc.)
```

## 1.2 Event Gateway & Feed Router

**Purpose:** Unified entry point for all marketing data (from BrightMatter Section 2.2)

```python
# lib/brain/ingest.py
"""
Event Gateway and Feed Router
Adapted from BrightMatter Section 2.2.1
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import hashlib

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
    
    # Core metrics (normalized)
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
    
    # Hashed identifiers (privacy)
    creator_hash: Optional[str] = None
    cohort_hash: Optional[str] = None
    
    # Raw data preserved
    raw_data: Dict = field(default_factory=dict)

class EventGateway:
    """
    Unified ingestion point for all marketing telemetry.
    
    From BrightMatter:
    - All telemetry funnels into the Unified Event Gateway
    - Events are normalized to common schema
    - Identifiers are pseudonymized with SHA-256
    """
    
    def __init__(self, firebase_client, config: 'BrainConfig'):
        self.firebase = firebase_client
        self.config = config
        self.feed_router = FeedRouter()
        
    def ingest(self, source: str, raw_data: Dict, client_id: str) -> MarketingEvent:
        """
        Ingest raw data from any source into normalized event.
        
        Steps:
        1. Detect feed type from source
        2. Normalize to MarketingEvent schema
        3. Pseudonymize identifiers
        4. Route to appropriate feed
        5. Persist to Firebase
        """
        # 1. Detect feed
        feed_type = self.feed_router.detect_feed(source, raw_data)
        
        # 2. Normalize
        event = self._normalize(raw_data, feed_type, client_id)
        
        # 3. Pseudonymize
        event = self._pseudonymize(event)
        
        # 4. Validate
        self._validate(event)
        
        # 5. Persist
        self._persist(event)
        
        return event
        
    def _normalize(self, raw: Dict, feed_type: FeedType, client_id: str) -> MarketingEvent:
        """Normalize raw data to common schema."""
        normalizer = self._get_normalizer(feed_type)
        return normalizer.normalize(raw, client_id)
        
    def _pseudonymize(self, event: MarketingEvent) -> MarketingEvent:
        """SHA-256 hash sensitive identifiers."""
        if event.content_id:
            salt = self.config.hash_salt
            event.creator_hash = hashlib.sha256(
                f"{event.content_id}{salt}".encode()
            ).hexdigest()[:16]
        return event
        
    def _persist(self, event: MarketingEvent):
        """Store event in Firebase."""
        self.firebase.set(
            f"clients/{event.client_id}/events/{event.event_id}",
            event.__dict__
        )

class FeedRouter:
    """
    Routes events to appropriate processing feeds.
    
    From BrightMatter Section 2.2:
    - Feed Router sorts each event into data feeds
    - Each feed has specialized processing templates
    """
    
    FEED_PATTERNS = {
        FeedType.EMAIL: ["mailchimp", "sendgrid", "hubspot_email", "klaviyo"],
        FeedType.SOCIAL_LINKEDIN: ["linkedin"],
        FeedType.SOCIAL_TWITTER: ["twitter", "x.com"],
        FeedType.SOCIAL_INSTAGRAM: ["instagram"],
        FeedType.SOCIAL_TIKTOK: ["tiktok"],
        FeedType.SOCIAL_YOUTUBE: ["youtube"],
        FeedType.ADS_GOOGLE: ["google_ads", "adwords"],
        FeedType.ADS_META: ["facebook_ads", "instagram_ads", "meta"],
        FeedType.CRM_HUBSPOT: ["hubspot"],
        FeedType.CRM_SALESFORCE: ["salesforce"],
    }
    
    def detect_feed(self, source: str, data: Dict) -> FeedType:
        """Detect feed type from source identifier."""
        source_lower = source.lower()
        for feed_type, patterns in self.FEED_PATTERNS.items():
            if any(p in source_lower for p in patterns):
                return feed_type
        return FeedType.CUSTOM
        
    def get_template(self, feed_type: FeedType) -> 'ProcessingTemplate':
        """Get processing template for feed."""
        from .templates import ProcessingTemplate
        return ProcessingTemplate(feed_type)
```

## 1.3 Performance Scoring System

**Purpose:** Calculate BrightMatter V' scores (corrected formula)

```python
# lib/brain/scoring.py
"""
Performance Scoring System
BrightMatter canonical formula (Section 6.1.2):
V' = ((E/F)^0.6 × I^0.4 × G × A) × Mv × Q' × T' × 1000
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import math

@dataclass
class PerformanceScore:
    """Composite performance score."""
    overall: float           # V' score (0-1000+ scale)
    
    # Core components
    engagement_ratio: float  # E/F (engagements / followers)
    impressions: float       # I (reach)
    growth: float            # G (momentum)
    authenticity: float      # A (1 - bots - coordinated)
    
    # Modifiers
    vertical_multiplier: float  # Mv
    quality_index: float        # Q' [0.7, 1.3]
    temporal_weight: float      # T'
    
    # Confidence
    confidence: float        # C (0-1)
    
    # Metadata
    calculated_at: datetime = None
    model_version: str = "1.0.0"
    
    def __post_init__(self):
        if self.calculated_at is None:
            self.calculated_at = datetime.now()

class PerformanceScorer:
    """
    Calculates performance scores using BrightMatter methodology.
    """
    
    # Platform-specific baselines (from BrightMatter Section 6.2.2)
    PLATFORM_BASELINES = {
        "linkedin": {"engagement_rate": 0.02, "decay_rate": 0.01, "decay_half_life_hours": 69},
        "twitter": {"engagement_rate": 0.015, "decay_rate": 0.22, "decay_half_life_hours": 3.2},
        "instagram": {"engagement_rate": 0.03, "decay_rate": 0.12, "decay_half_life_hours": 5.8},
        "tiktok": {"engagement_rate": 0.05, "decay_rate": 0.35, "decay_half_life_hours": 2.0},
        "youtube": {"engagement_rate": 0.02, "decay_rate": 0.003, "decay_half_life_hours": 231},
        "facebook": {"engagement_rate": 0.025, "decay_rate": 0.15, "decay_half_life_hours": 4.6},
        "email": {"open_rate": 0.20, "click_rate": 0.025, "decay_rate": 0.5, "decay_half_life_hours": 1.4},
        "newsletter": {"open_rate": 0.35, "click_rate": 0.02, "decay_rate": 0.4, "decay_half_life_hours": 1.7},
        "google_ads": {"ctr": 0.02, "conversion_rate": 0.03, "decay_rate": 0.2},
        "meta_ads": {"ctr": 0.009, "conversion_rate": 0.02, "decay_rate": 0.25},
    }
    
    # Vertical multipliers (from BrightMatter Section 6.1.4)
    VERTICAL_MULTIPLIERS = {
        # Original BrightMatter
        "mobile": 0.8,
        "pc": 1.0,
        "console": 1.2,
        "web3": 1.1,
        "indie": 0.9,
        # Marketing verticals
        "b2b_saas": 1.1,
        "b2b_services": 1.05,
        "ecommerce": 1.0,
        "d2c": 1.05,
        "agency": 0.95,
        "enterprise": 1.15,
        "smb": 0.9,
        "fintech": 1.1,
        "healthcare": 1.05,
    }
    
    # Quality index weights (from BrightMatter Section 6.4.1)
    # Q' = 0.4*S + 0.3*C + 0.3*R
    QUALITY_WEIGHTS = {
        "sentiment": 0.4,
        "consistency": 0.3,
        "relevance": 0.3,
    }
    
    # Platform-specific Q' adaptations
    PLATFORM_QUALITY_OVERRIDES = {
        "tiktok": {"relevance": 0.5, "sentiment": 0.3, "consistency": 0.2},  # Trend alignment
        "youtube": {"consistency": 0.4, "sentiment": 0.35, "relevance": 0.25},  # Posting cadence
        "twitter": {"sentiment": 0.3, "relevance": 0.4, "consistency": 0.3},  # Brevity limits sentiment
    }
    
    def __init__(self, config: 'BrainConfig' = None):
        self.config = config or BrainConfig()
        
    def score(self, event: 'MarketingEvent', history: List['MarketingEvent'] = None) -> PerformanceScore:
        """
        Calculate composite performance score.
        
        Formula: V' = ((E/F)^0.6 × I^0.4 × G × A) × Mv × Q' × T' × 1000
        """
        platform = event.platform or "email"
        
        # Core components
        e_over_f = self._calculate_engagement_ratio(event)
        impressions = self._normalize_impressions(event)
        growth = self._calculate_growth(event, history)
        authenticity = self._calculate_authenticity(event)
        
        # Modifiers
        mv = self._get_vertical_multiplier(event)
        q_prime = self._calculate_quality_index(event)
        t_prime = self._calculate_temporal_weight(event)
        
        # Confidence
        confidence = self._calculate_confidence(event, history)
        
        # BrightMatter canonical formula
        v_prime = (
            (e_over_f ** 0.6) *
            (impressions ** 0.4) *
            growth *
            authenticity *
            mv *
            q_prime *
            t_prime *
            1000
        )
        
        return PerformanceScore(
            overall=v_prime,
            engagement_ratio=e_over_f,
            impressions=impressions,
            growth=growth,
            authenticity=authenticity,
            vertical_multiplier=mv,
            quality_index=q_prime,
            temporal_weight=t_prime,
            confidence=confidence,
            model_version=self.config.model_version
        )
        
    def _calculate_engagement_ratio(self, event: 'MarketingEvent') -> float:
        """
        Calculate normalized E/F ratio.
        
        From BrightMatter 6.2.2:
        (E/F)* = (E/F) / μ_p
        where μ_p is platform baseline
        """
        platform = event.platform or "email"
        baseline = self.PLATFORM_BASELINES.get(platform, {})
        baseline_rate = baseline.get("engagement_rate", 0.02)
        
        # Calculate raw engagement rate
        total_engagements = event.engagements or (
            event.likes + event.comments + event.shares + event.clicks
        )
        audience = max(event.audience_size, 1)
        
        raw_rate = total_engagements / audience
        
        # Normalize against baseline
        normalized = raw_rate / baseline_rate if baseline_rate > 0 else raw_rate
        
        # Cap at 3x baseline to prevent outliers
        return min(3.0, max(0.01, normalized))
        
    def _normalize_impressions(self, event: 'MarketingEvent') -> float:
        """
        Normalize impressions using logarithmic compression.
        
        From BrightMatter 6.2.2:
        I* = ln(I / μ_I) / ln(10)
        """
        impressions = max(event.impressions, 1)
        
        # Median impressions by audience tier
        audience = event.audience_size
        if audience < 1000:
            median_impressions = 100
        elif audience < 10000:
            median_impressions = 1000
        elif audience < 100000:
            median_impressions = 10000
        else:
            median_impressions = 50000
            
        # Logarithmic normalization
        normalized = math.log(impressions / median_impressions) / math.log(10)
        
        # Shift to positive range and cap
        return min(3.0, max(0.1, normalized + 1.5))
        
    def _calculate_growth(self, event: 'MarketingEvent', history: List['MarketingEvent'] = None) -> float:
        """
        Calculate growth momentum coefficient.
        
        G = short_term_velocity / long_term_average
        """
        if not history or len(history) < 2:
            return 1.0  # Neutral growth if no history
            
        # Sort by timestamp
        sorted_history = sorted(history, key=lambda e: e.timestamp)
        
        # Short-term: last 7 days
        week_ago = datetime.now() - timedelta(days=7)
        recent = [e for e in sorted_history if e.timestamp > week_ago]
        
        # Long-term: last 30 days
        month_ago = datetime.now() - timedelta(days=30)
        historical = [e for e in sorted_history if e.timestamp > month_ago]
        
        if not recent or not historical:
            return 1.0
            
        recent_avg = sum(e.engagements for e in recent) / len(recent)
        historical_avg = sum(e.engagements for e in historical) / len(historical)
        
        if historical_avg == 0:
            return 1.0
            
        growth = recent_avg / historical_avg
        
        # Cap between 0.5 and 2.0
        return min(2.0, max(0.5, growth))
        
    def _calculate_authenticity(self, event: 'MarketingEvent') -> float:
        """
        Calculate authenticity factor.
        
        From BrightMatter 6.4.2:
        A = max(0.3, 1 - 0.5*B - 0.4*Sc - 0.3*Tc)
        
        B = bot ratio
        Sc = coordinated share ratio
        Tc = temporal coherence penalty
        """
        raw = event.raw_data
        
        # Extract or estimate bot ratio
        bot_ratio = raw.get("bot_ratio", 0)
        if bot_ratio == 0 and event.engagements > 0:
            # Heuristic: suspicious if engagement velocity too high
            if raw.get("engagement_velocity_per_minute", 0) > 100:
                bot_ratio = 0.2
                
        # Coordinated share detection
        coord_ratio = raw.get("coordinated_ratio", 0)
        
        # Temporal coherence penalty
        temporal_penalty = raw.get("temporal_anomaly", 0)
        if temporal_penalty == 0:
            # Heuristic: penalty if 70%+ engagement in first minute
            first_minute_pct = raw.get("first_minute_engagement_pct", 0)
            if first_minute_pct > 0.7:
                temporal_penalty = 0.3
                
        # BrightMatter formula
        a = 1 - 0.5 * bot_ratio - 0.4 * coord_ratio - 0.3 * temporal_penalty
        
        return max(0.3, a)
        
    def _get_vertical_multiplier(self, event: 'MarketingEvent') -> float:
        """Get vertical multiplier Mv."""
        vertical = event.vertical or "b2b_saas"
        return self.VERTICAL_MULTIPLIERS.get(vertical, 1.0)
        
    def _calculate_quality_index(self, event: 'MarketingEvent') -> float:
        """
        Calculate quality index Q'.
        
        From BrightMatter 6.4.1:
        Q' = 0.4*S + 0.3*C + 0.3*R
        
        Bounded [0.7, 1.3]
        """
        platform = event.platform or "email"
        weights = self.PLATFORM_QUALITY_OVERRIDES.get(platform, self.QUALITY_WEIGHTS)
        
        raw = event.raw_data
        
        # S: Sentiment score (0-1, where 0.5 is neutral)
        sentiment = raw.get("sentiment_score", 0.5)
        
        # C: Consistency (posting frequency vs optimal)
        consistency = raw.get("consistency_score", 0.7)
        
        # R: Relevance alignment (topic match)
        relevance = raw.get("relevance_score", 0.6)
        
        q_prime = (
            weights["sentiment"] * sentiment +
            weights["consistency"] * consistency +
            weights["relevance"] * relevance
        )
        
        # Add 0.5 to shift range, then bound [0.7, 1.3]
        q_prime = q_prime + 0.5
        return max(0.7, min(1.3, q_prime))
        
    def _calculate_temporal_weight(self, event: 'MarketingEvent') -> float:
        """
        Calculate temporal decay weight T'.
        
        From BrightMatter 6.3.1:
        E_t = E₀ × e^(-λt)
        T' = ∫₀ᵗ E_t dt / ∫₀^∞ E_t dt
        
        Simplified: T' ≈ 1 - (1 - e^(-λt))
        """
        platform = event.platform or "email"
        baseline = self.PLATFORM_BASELINES.get(platform, {})
        decay_rate = baseline.get("decay_rate", 0.1)
        
        # Hours since event
        hours_elapsed = (datetime.now() - event.timestamp).total_seconds() / 3600
        
        # Exponential decay
        t_prime = math.exp(-decay_rate * hours_elapsed)
        
        # Floor at 0.1 to preserve some residual value
        return max(0.1, t_prime)
        
    def _calculate_confidence(self, event: 'MarketingEvent', history: List['MarketingEvent'] = None) -> float:
        """
        Calculate confidence coefficient.
        
        Based on:
        - Data completeness
        - Sample size
        - Historical consistency
        """
        completeness = 0.0
        
        # Check required fields
        if event.engagements > 0:
            completeness += 0.3
        if event.impressions > 0:
            completeness += 0.2
        if event.audience_size > 0:
            completeness += 0.2
        if event.platform:
            completeness += 0.1
        if event.vertical:
            completeness += 0.1
            
        # History bonus
        if history and len(history) >= 10:
            completeness += 0.1
            
        return min(1.0, completeness)
```

## 1.4 Processing Templates

**Purpose:** Ensure consistent processing across data feeds (from BrightMatter Section 4.2)

```python
# lib/brain/templates.py
"""
Processing Templates
From BrightMatter Section 4.2:
- Modular inference scripts referencing IRL for scalars/embeddings
- Template versioning with cryptographic hash
"""

from dataclasses import dataclass
from typing import Dict, Callable
import hashlib
from datetime import datetime

@dataclass
class TemplateVersion:
    """Versioned template with hash."""
    version: str
    hash: str
    created_at: datetime
    scalars: Dict[str, float]
    
class ProcessingTemplate:
    """
    Feed-specific processing template.
    
    Ensures all processing for a feed type follows
    identical logic with versioned parameters.
    """
    
    # Template definitions per feed
    TEMPLATES = {
        "email": {
            "version": "1.0.0",
            "scalars": {
                "open_weight": 0.4,
                "click_weight": 0.6,
                "bounce_penalty": 0.2,
                "unsubscribe_penalty": 0.5,
            },
            "normalizer": "_normalize_email",
            "scorer": "_score_email",
        },
        "social_linkedin": {
            "version": "1.0.0",
            "scalars": {
                "like_weight": 0.3,
                "comment_weight": 0.5,
                "share_weight": 0.7,
                "click_weight": 0.4,
            },
            "normalizer": "_normalize_social",
            "scorer": "_score_social",
        },
        "social_twitter": {
            "version": "1.0.0",
            "scalars": {
                "like_weight": 0.2,
                "reply_weight": 0.5,
                "retweet_weight": 0.8,
                "quote_weight": 0.9,
            },
            "normalizer": "_normalize_social",
            "scorer": "_score_social",
        },
        # ... additional templates
    }
    
    def __init__(self, feed_type: 'FeedType'):
        self.feed_type = feed_type
        self.template = self.TEMPLATES.get(feed_type.value, self.TEMPLATES["email"])
        self.version = TemplateVersion(
            version=self.template["version"],
            hash=self._compute_hash(),
            created_at=datetime.now(),
            scalars=self.template["scalars"]
        )
        
    def _compute_hash(self) -> str:
        """Compute deterministic hash of template."""
        content = str(sorted(self.template.items()))
        return hashlib.sha256(content.encode()).hexdigest()[:16]
        
    def process(self, event: 'MarketingEvent') -> 'MarketingEvent':
        """Process event through template."""
        normalizer = getattr(self, self.template["normalizer"])
        return normalizer(event)
        
    def _normalize_email(self, event: 'MarketingEvent') -> 'MarketingEvent':
        """Normalize email metrics."""
        raw = event.raw_data
        scalars = self.template["scalars"]
        
        # Composite engagement for email
        opens = raw.get("opens", 0)
        clicks = raw.get("clicks", 0)
        bounces = raw.get("bounces", 0)
        unsubscribes = raw.get("unsubscribes", 0)
        sent = raw.get("sent", 1)
        
        event.engagements = int(
            opens * scalars["open_weight"] +
            clicks * scalars["click_weight"] -
            bounces * scalars["bounce_penalty"] -
            unsubscribes * scalars["unsubscribe_penalty"]
        )
        event.impressions = opens
        event.audience_size = sent
        
        return event
        
    def _normalize_social(self, event: 'MarketingEvent') -> 'MarketingEvent':
        """Normalize social metrics."""
        raw = event.raw_data
        
        event.likes = raw.get("likes", 0)
        event.comments = raw.get("comments", raw.get("replies", 0))
        event.shares = raw.get("shares", raw.get("retweets", 0))
        event.clicks = raw.get("clicks", 0)
        event.engagements = event.likes + event.comments + event.shares + event.clicks
        event.impressions = raw.get("impressions", raw.get("views", 0))
        event.audience_size = raw.get("followers", raw.get("connections", 0))
        
        return event
```

## 1.5 Anomaly Detection

**Purpose:** Detect fake engagement, bots, coordinated manipulation (from BrightMatter Section 4.4)

```python
# lib/brain/anomaly.py
"""
Anomaly Detection System
From BrightMatter Section 4.4:
- View-engagement disproportions
- Comment-share imbalance
- Follower-engagement tier deviations
- Two-level detection (local heuristics + ML classifiers)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime
import math

class AnomalyType(Enum):
    """Anomaly taxonomy from BrightMatter 4.4."""
    VIEW_ENGAGEMENT_DISPROPORTION = "view_engagement_disproportion"
    COMMENT_SHARE_IMBALANCE = "comment_share_imbalance"
    FOLLOWER_TIER_DEVIATION = "follower_tier_deviation"
    TEMPORAL_BURST = "temporal_burst"
    BOT_PATTERN = "bot_pattern"
    COORDINATED_ACTIVITY = "coordinated_activity"

class AnomalySeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Anomaly:
    """Detected anomaly."""
    type: AnomalyType
    severity: AnomalySeverity
    z_score: float
    description: str
    affected_metrics: List[str]
    detected_at: datetime = None
    
    def __post_init__(self):
        if self.detected_at is None:
            self.detected_at = datetime.now()

class AnomalyDetector:
    """
    Two-level anomaly detection system.
    
    Level 1: Local heuristics (fast, rule-based)
    Level 2: Statistical detection (z-score based)
    """
    
    # Thresholds (from BrightMatter analysis)
    THRESHOLDS = {
        "view_engagement_ratio_max": 100,  # Views/engagements
        "comment_share_ratio_max": 50,
        "follower_engagement_rate_max": 0.5,  # Suspiciously high
        "first_minute_engagement_max": 0.7,
        "z_score_outlier": 2.0,
        "z_score_critical": 3.0,
    }
    
    def __init__(self):
        self.history_buffer: Dict[str, List[float]] = {}
        
    def detect(self, event: 'MarketingEvent', history: List['MarketingEvent'] = None) -> List[Anomaly]:
        """
        Run full anomaly detection.
        
        Returns list of detected anomalies.
        """
        anomalies = []
        
        # Level 1: Heuristic checks
        anomalies.extend(self._check_view_engagement(event))
        anomalies.extend(self._check_comment_share(event))
        anomalies.extend(self._check_follower_tier(event))
        anomalies.extend(self._check_temporal_burst(event))
        
        # Level 2: Statistical checks (if history available)
        if history and len(history) >= 10:
            anomalies.extend(self._statistical_detection(event, history))
            
        return anomalies
        
    def _check_view_engagement(self, event: 'MarketingEvent') -> List[Anomaly]:
        """Check for view-engagement disproportions."""
        anomalies = []
        
        views = event.impressions
        engagements = event.engagements
        
        if engagements > 0:
            ratio = views / engagements
            threshold = self.THRESHOLDS["view_engagement_ratio_max"]
            
            if ratio > threshold:
                severity = AnomalySeverity.HIGH if ratio > threshold * 2 else AnomalySeverity.MEDIUM
                anomalies.append(Anomaly(
                    type=AnomalyType.VIEW_ENGAGEMENT_DISPROPORTION,
                    severity=severity,
                    z_score=ratio / threshold,
                    description=f"View/engagement ratio ({ratio:.1f}) exceeds threshold ({threshold})",
                    affected_metrics=["impressions", "engagements"]
                ))
                
        return anomalies
        
    def _check_comment_share(self, event: 'MarketingEvent') -> List[Anomaly]:
        """Check for comment-share imbalance."""
        anomalies = []
        
        comments = event.comments
        shares = event.shares
        
        if shares > 0:
            ratio = comments / shares
            threshold = self.THRESHOLDS["comment_share_ratio_max"]
            
            if ratio > threshold:
                anomalies.append(Anomaly(
                    type=AnomalyType.COMMENT_SHARE_IMBALANCE,
                    severity=AnomalySeverity.MEDIUM,
                    z_score=ratio / threshold,
                    description=f"Comment/share ratio ({ratio:.1f}) suggests engagement pod",
                    affected_metrics=["comments", "shares"]
                ))
                
        return anomalies
        
    def _check_follower_tier(self, event: 'MarketingEvent') -> List[Anomaly]:
        """Check for follower-engagement tier deviations."""
        anomalies = []
        
        followers = event.audience_size
        engagements = event.engagements
        
        if followers > 0:
            rate = engagements / followers
            threshold = self.THRESHOLDS["follower_engagement_rate_max"]
            
            if rate > threshold:
                anomalies.append(Anomaly(
                    type=AnomalyType.FOLLOWER_TIER_DEVIATION,
                    severity=AnomalySeverity.HIGH,
                    z_score=rate / threshold,
                    description=f"Engagement rate ({rate:.2%}) exceeds realistic threshold ({threshold:.0%})",
                    affected_metrics=["engagements", "audience_size"]
                ))
                
        return anomalies
        
    def _check_temporal_burst(self, event: 'MarketingEvent') -> List[Anomaly]:
        """Check for suspicious temporal patterns."""
        anomalies = []
        
        raw = event.raw_data
        first_minute_pct = raw.get("first_minute_engagement_pct", 0)
        threshold = self.THRESHOLDS["first_minute_engagement_max"]
        
        if first_minute_pct > threshold:
            anomalies.append(Anomaly(
                type=AnomalyType.TEMPORAL_BURST,
                severity=AnomalySeverity.HIGH,
                z_score=first_minute_pct / threshold,
                description=f"{first_minute_pct:.0%} of engagement in first minute (threshold: {threshold:.0%})",
                affected_metrics=["engagement_velocity"]
            ))
            
        return anomalies
        
    def _statistical_detection(self, event: 'MarketingEvent', history: List['MarketingEvent']) -> List[Anomaly]:
        """
        Level 2: Statistical z-score based detection.
        
        From BrightMatter 6.2.3:
        - Engagement density histograms examined for bimodal anomalies
        - Trimmed-mean aggregation excluding top/bottom 2%
        """
        anomalies = []
        
        # Get historical engagement rates
        historical_rates = []
        for h in history:
            if h.audience_size > 0:
                historical_rates.append(h.engagements / h.audience_size)
                
        if len(historical_rates) < 10:
            return anomalies
            
        # Trimmed mean (exclude top/bottom 2%)
        sorted_rates = sorted(historical_rates)
        trim_count = max(1, int(len(sorted_rates) * 0.02))
        trimmed = sorted_rates[trim_count:-trim_count] if trim_count > 0 else sorted_rates
        
        mean = sum(trimmed) / len(trimmed)
        variance = sum((x - mean) ** 2 for x in trimmed) / len(trimmed)
        std = math.sqrt(variance) if variance > 0 else 0.01
        
        # Current event z-score
        current_rate = event.engagements / max(event.audience_size, 1)
        z_score = (current_rate - mean) / std if std > 0 else 0
        
        if abs(z_score) > self.THRESHOLDS["z_score_critical"]:
            anomalies.append(Anomaly(
                type=AnomalyType.BOT_PATTERN,
                severity=AnomalySeverity.CRITICAL,
                z_score=z_score,
                description=f"Engagement rate z-score ({z_score:.2f}) indicates anomaly",
                affected_metrics=["engagements", "engagement_rate"]
            ))
        elif abs(z_score) > self.THRESHOLDS["z_score_outlier"]:
            anomalies.append(Anomaly(
                type=AnomalyType.BOT_PATTERN,
                severity=AnomalySeverity.MEDIUM,
                z_score=z_score,
                description=f"Engagement rate z-score ({z_score:.2f}) is outlier",
                affected_metrics=["engagements", "engagement_rate"]
            ))
            
        return anomalies
```

## 1.6 Firebase Schema

**Purpose:** Persist all brain state in Firebase

```javascript
// Firebase Firestore Schema for Brain

// clients/{clientId}/brain/state
{
  "model_version": "1.0.0",
  "last_analysis": "2026-01-28T12:00:00Z",
  "processing_template_hash": "a1b2c3d4e5f6g7h8"
}

// clients/{clientId}/brain/scores/{scoreId}
{
  "overall": 725.5,
  "engagement_ratio": 1.2,
  "impressions": 1.5,
  "growth": 1.1,
  "authenticity": 0.95,
  "vertical_multiplier": 1.1,
  "quality_index": 1.05,
  "temporal_weight": 0.85,
  "confidence": 0.88,
  "calculated_at": "2026-01-28T12:00:00Z",
  "event_id": "evt_123"
}

// clients/{clientId}/events/{eventId}
{
  "event_id": "evt_123",
  "client_id": "client_456",
  "feed_type": "social_linkedin",
  "timestamp": "2026-01-28T10:00:00Z",
  "engagements": 150,
  "impressions": 5000,
  "audience_size": 2500,
  "likes": 100,
  "comments": 30,
  "shares": 20,
  "platform": "linkedin",
  "vertical": "b2b_saas",
  "creator_hash": "a1b2c3d4",
  "raw_data": {...}
}

// clients/{clientId}/brain/anomalies/{anomalyId}
{
  "type": "temporal_burst",
  "severity": "high",
  "z_score": 2.5,
  "description": "85% of engagement in first minute",
  "affected_metrics": ["engagement_velocity"],
  "event_id": "evt_123",
  "detected_at": "2026-01-28T12:00:00Z",
  "resolved": false
}
```

## 1.7 Configuration

```python
# lib/brain/config.py
"""
Brain Configuration
"""

from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class BrainConfig:
    """Configuration for the Brain engine."""
    
    # Model
    model_version: str = "1.0.0"
    hash_salt: str = "mh1_brain_salt_2026"
    
    # Scoring
    scoring_exponents: Dict[str, float] = field(default_factory=lambda: {
        "engagement": 0.6,
        "impressions": 0.4,
    })
    scoring_scale: int = 1000
    
    # Quality bounds
    quality_min: float = 0.7
    quality_max: float = 1.3
    
    # Confidence thresholds
    min_confidence_for_prediction: float = 0.6
    min_history_for_growth: int = 2
    
    # Anomaly detection
    z_score_outlier: float = 2.0
    z_score_critical: float = 3.0
    
    # Feeds
    supported_feeds: List[str] = field(default_factory=lambda: [
        "email", "social_linkedin", "social_twitter",
        "social_instagram", "social_tiktok", "social_youtube",
        "ads_google", "ads_meta", "crm_hubspot", "crm_salesforce"
    ])
```

---

# PHASE 2: Learning & Intelligence (Weeks 3-4)

## 2.1 Compound Learning Loop

**Purpose:** Self-improving system that learns from outcomes (from BrightMatter Section 5)

```python
# lib/brain/learning.py
"""
Compound Learning System
From BrightMatter Section 5 and 9.1.1:
- Online learning with weight updates
- Shadow mode for model testing
- Gold standard validation
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import hashlib

@dataclass
class Outcome:
    """Observed outcome vs prediction."""
    outcome_id: str
    recommendation_id: Optional[str]
    event_id: str
    client_id: str
    
    # Predictions made
    predicted: Dict[str, float]
    
    # Actual observations
    observed: Dict[str, float]
    
    # Metadata
    prediction_timestamp: datetime
    observation_timestamp: datetime
    move_type: str = "standard"  # standard, validation, self_generated
    
    @property
    def delta(self) -> Dict[str, float]:
        """Calculate prediction error."""
        return {
            k: self.observed.get(k, 0) - self.predicted.get(k, 0)
            for k in self.predicted.keys()
        }
        
    @property
    def move_weight(self) -> float:
        """Get weight based on move type (from BrightMatter 6.5)."""
        weights = {
            "standard": 1.25,
            "validation": 1.50,
            "self_generated": 1.15,
        }
        return weights.get(self.move_type, 1.0)

@dataclass
class LearningState:
    """Persisted learning state."""
    weights: Dict[str, float]
    iteration: int
    model_version: str
    last_update: datetime
    shadow_candidate: Optional[Dict] = None
    
    # Performance tracking
    cumulative_error: float = 0.0
    outcome_count: int = 0

class LearningLoop:
    """
    Compound learning system.
    
    From BrightMatter:
    - Weight update rule: w_{t+1} = w_t + η(R_observed - R_predicted)
    - Shadow mode testing
    - Candidate promotion at 3% improvement
    """
    
    # Default weights for scoring components
    DEFAULT_WEIGHTS = {
        "engagement": 1.0,
        "impressions": 1.0,
        "growth": 1.0,
        "authenticity": 1.0,
        "quality": 1.0,
        "temporal": 1.0,
    }
    
    # Learning parameters
    BASE_LEARNING_RATE = 0.01
    MIN_IMPROVEMENT_FOR_PROMOTION = 0.03  # 3%
    MIN_OBSERVATIONS_FOR_PROMOTION = 100
    SHADOW_TEST_DURATION_DAYS = 7
    ERROR_THRESHOLD_FOR_SHADOW = 0.15  # 15% avg error triggers shadow
    
    def __init__(self, firebase_client, config: 'BrainConfig'):
        self.firebase = firebase_client
        self.config = config
        self.state = self._load_state()
        
    def _load_state(self) -> LearningState:
        """Load learning state from Firebase."""
        try:
            doc = self.firebase.get("system/brain/learning_state")
            return LearningState(**doc)
        except:
            return LearningState(
                weights=self.DEFAULT_WEIGHTS.copy(),
                iteration=0,
                model_version=self.config.model_version,
                last_update=datetime.now()
            )
            
    def _save_state(self):
        """Persist learning state to Firebase."""
        state_dict = {
            "weights": self.state.weights,
            "iteration": self.state.iteration,
            "model_version": self.state.model_version,
            "last_update": self.state.last_update.isoformat(),
            "shadow_candidate": self.state.shadow_candidate,
            "cumulative_error": self.state.cumulative_error,
            "outcome_count": self.state.outcome_count,
        }
        self.firebase.set("system/brain/learning_state", state_dict)
        
        # Also save to history for rollback
        self.firebase.set(
            f"system/brain/learning_history/{self.state.iteration}",
            state_dict
        )
        
    def record_outcome(self, outcome: Outcome):
        """
        Record outcome and update weights.
        
        From BrightMatter:
        w_{t+1} = w_t + η * move_weight * (observed - predicted)
        """
        # Calculate adaptive learning rate
        eta = self._adaptive_learning_rate()
        
        # Update weights based on outcome deltas
        for metric, delta in outcome.delta.items():
            if metric in self.state.weights:
                adjustment = eta * outcome.move_weight * delta
                self.state.weights[metric] += adjustment
                
        # Track error
        error = sum(abs(d) for d in outcome.delta.values()) / len(outcome.delta)
        self.state.cumulative_error += error
        self.state.outcome_count += 1
        
        self.state.iteration += 1
        self.state.last_update = datetime.now()
        
        # Persist outcome
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
        
        # Check if shadow mode needed
        if self.state.iteration % 50 == 0:
            self._evaluate_for_shadow_mode()
            
        self._save_state()
        
    def _adaptive_learning_rate(self) -> float:
        """
        Calculate adaptive learning rate.
        
        Decreases as model stabilizes (more iterations).
        """
        decay_factor = 1.0 / (1.0 + 0.001 * self.state.iteration)
        return self.BASE_LEARNING_RATE * decay_factor
        
    def _evaluate_for_shadow_mode(self):
        """
        Spawn shadow candidate if performance degraded.
        
        From BrightMatter 4.3.
        """
        if self.state.outcome_count < 50:
            return
            
        avg_error = self.state.cumulative_error / self.state.outcome_count
        
        if avg_error > self.ERROR_THRESHOLD_FOR_SHADOW and not self.state.shadow_candidate:
            self.state.shadow_candidate = {
                "version": f"shadow_{self.state.iteration}",
                "weights": self._generate_candidate_weights(),
                "created_at": datetime.now().isoformat(),
                "status": "testing",
                "test_outcomes": [],
                "production_error": avg_error,
            }
            
    def _generate_candidate_weights(self) -> Dict[str, float]:
        """Generate candidate weights with perturbation."""
        import random
        candidate = {}
        for key, value in self.state.weights.items():
            # Small random perturbation
            perturbation = random.uniform(-0.1, 0.1)
            candidate[key] = value * (1 + perturbation)
        return candidate
        
    def test_shadow_candidate(self, outcomes: List[Outcome]) -> bool:
        """
        Test shadow candidate against outcomes.
        
        Returns True if candidate should be promoted.
        """
        if not self.state.shadow_candidate:
            return False
            
        candidate = self.state.shadow_candidate
        
        # Need minimum observations
        if len(outcomes) < self.MIN_OBSERVATIONS_FOR_PROMOTION:
            return False
            
        # Calculate error with candidate weights
        candidate_error = self._calculate_error_with_weights(
            outcomes, candidate["weights"]
        )
        
        # Calculate error with production weights
        production_error = candidate.get("production_error", 0.15)
        
        # Check improvement
        if production_error > 0:
            improvement = (production_error - candidate_error) / production_error
            
            if improvement >= self.MIN_IMPROVEMENT_FOR_PROMOTION:
                return True
                
        return False
        
    def promote_candidate(self):
        """Promote shadow candidate to production."""
        if not self.state.shadow_candidate:
            return
            
        # Archive current weights
        self.firebase.set(
            f"system/brain/archived_models/{self.state.iteration}",
            {
                "weights": self.state.weights,
                "replaced_at": datetime.now().isoformat(),
                "replaced_by": self.state.shadow_candidate["version"],
            }
        )
        
        # Promote candidate
        self.state.weights = self.state.shadow_candidate["weights"]
        self.state.model_version = self.state.shadow_candidate["version"]
        self.state.shadow_candidate = None
        
        # Reset error tracking
        self.state.cumulative_error = 0.0
        self.state.outcome_count = 0
        
        self._save_state()
        
    def _calculate_error_with_weights(self, outcomes: List[Outcome], weights: Dict[str, float]) -> float:
        """Calculate mean absolute error with given weights."""
        total_error = 0.0
        for outcome in outcomes:
            weighted_delta = sum(
                weights.get(k, 1.0) * abs(v)
                for k, v in outcome.delta.items()
            )
            total_error += weighted_delta
        return total_error / len(outcomes) if outcomes else 0.0

class GoldStandardValidator:
    """
    Validates models against gold standard datasets.
    
    From BrightMatter 4.3.2.
    """
    
    def __init__(self, firebase_client):
        self.firebase = firebase_client
        
    def validate(self, weights: Dict[str, float], dataset_name: str = "default") -> Dict:
        """Validate weights against gold standard dataset."""
        dataset = self._load_dataset(dataset_name)
        
        results = {
            "dataset": dataset_name,
            "sample_count": len(dataset),
            "metrics": {},
        }
        
        for metric, expected in dataset.get("expected_metrics", {}).items():
            # Calculate actual metric with weights
            actual = self._calculate_metric(dataset["samples"], weights, metric)
            error = abs(actual - expected) / expected if expected > 0 else 0
            
            results["metrics"][metric] = {
                "expected": expected,
                "actual": actual,
                "error": error,
                "passed": error < 0.15,  # 15% tolerance
            }
            
        results["all_passed"] = all(m["passed"] for m in results["metrics"].values())
        return results
        
    def _load_dataset(self, name: str) -> Dict:
        """Load gold standard dataset."""
        try:
            return self.firebase.get(f"system/brain/gold_standards/{name}")
        except:
            return {"samples": [], "expected_metrics": {}}
            
    def _calculate_metric(self, samples: List, weights: Dict, metric: str) -> float:
        """Calculate metric on samples with weights."""
        # Simplified - actual implementation would run scorer
        return 0.0
```

## 2.2 Prediction Engine

**Purpose:** Generate T+24h and T+7d predictions (integrated with existing forecasting)

```python
# lib/brain/predictions.py
"""
Prediction Engine
Integrates with existing lib/forecasting.py and adds BrightMatter temporal decay.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import math

# Import existing forecasting
from lib.forecasting import MarketingForecaster, TrendDirection

@dataclass
class Prediction:
    """Prediction with confidence interval."""
    metric: str
    horizon: str  # "24h", "7d", "30d"
    
    # Point estimate
    value: float
    
    # Confidence interval (5th and 95th percentile)
    lower_bound: float
    upper_bound: float
    
    # Confidence
    confidence: float
    
    # Metadata
    generated_at: datetime = None
    model_version: str = "1.0.0"
    
    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.now()

class PredictionEngine:
    """
    Generates predictions using BrightMatter temporal models.
    
    Integrates with existing TATS forecaster.
    """
    
    # Platform decay rates (from BrightMatter 6.3.1)
    DECAY_RATES = {
        "linkedin": 0.01,
        "twitter": 0.22,
        "instagram": 0.12,
        "tiktok": 0.35,
        "youtube": 0.003,
        "facebook": 0.15,
        "email": 0.5,
    }
    
    # Prediction horizons in hours
    HORIZONS = {
        "24h": 24,
        "7d": 168,
        "30d": 720,
    }
    
    def __init__(self, config: 'BrainConfig'):
        self.config = config
        self.forecaster = MarketingForecaster(metric_type="engagement")
        
    def predict(
        self,
        current_score: 'PerformanceScore',
        history: List['PerformanceScore'],
        platform: str,
        horizons: List[str] = None
    ) -> Dict[str, Prediction]:
        """
        Generate predictions for specified horizons.
        
        Combines:
        1. Existing TATS forecaster for trend
        2. BrightMatter temporal decay
        """
        horizons = horizons or ["24h", "7d"]
        predictions = {}
        
        # Determine trend direction
        trend = self._detect_trend(history)
        
        for horizon in horizons:
            hours = self.HORIZONS.get(horizon, 24)
            
            # Get decay factor
            decay_rate = self.DECAY_RATES.get(platform, 0.1)
            decay_factor = math.exp(-decay_rate * hours)
            
            # Get trend adjustment from TATS
            trend_adjustment = self._get_trend_adjustment(history, trend, hours)
            
            # Calculate prediction
            base_value = current_score.overall
            predicted_value = base_value * decay_factor * trend_adjustment
            
            # Calculate confidence interval
            confidence = self._calculate_confidence(history, hours)
            std_dev = self._estimate_std_dev(history)
            
            lower = predicted_value - 1.96 * std_dev
            upper = predicted_value + 1.96 * std_dev
            
            predictions[horizon] = Prediction(
                metric="overall_score",
                horizon=horizon,
                value=predicted_value,
                lower_bound=max(0, lower),
                upper_bound=upper,
                confidence=confidence,
                model_version=self.config.model_version
            )
            
        return predictions
        
    def _detect_trend(self, history: List['PerformanceScore']) -> TrendDirection:
        """Detect trend from history."""
        if not history or len(history) < 3:
            return TrendDirection.FLAT
            
        recent = [h.overall for h in history[-7:]]
        older = [h.overall for h in history[-14:-7]] if len(history) >= 14 else recent
        
        recent_avg = sum(recent) / len(recent)
        older_avg = sum(older) / len(older)
        
        if recent_avg > older_avg * 1.1:
            return TrendDirection.UP
        elif recent_avg < older_avg * 0.9:
            return TrendDirection.DOWN
        return TrendDirection.FLAT
        
    def _get_trend_adjustment(self, history: List, trend: TrendDirection, hours: int) -> float:
        """Get trend-based adjustment factor."""
        base_adjustments = {
            TrendDirection.UP: 1.1,
            TrendDirection.DOWN: 0.9,
            TrendDirection.FLAT: 1.0,
        }
        
        # Diminish trend effect over longer horizons
        base = base_adjustments.get(trend, 1.0)
        days = hours / 24
        
        # Trend effect halves every 7 days
        decay = 0.5 ** (days / 7)
        
        return 1 + (base - 1) * decay
        
    def _calculate_confidence(self, history: List, hours: int) -> float:
        """Calculate prediction confidence."""
        # Base confidence from history length
        history_confidence = min(1.0, len(history) / 30)
        
        # Confidence decreases with horizon
        horizon_confidence = 1.0 / (1 + 0.01 * hours)
        
        return history_confidence * horizon_confidence
        
    def _estimate_std_dev(self, history: List['PerformanceScore']) -> float:
        """Estimate standard deviation from history."""
        if not history or len(history) < 2:
            return 100  # Default high uncertainty
            
        values = [h.overall for h in history]
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        
        return math.sqrt(variance)
```

## 2.3 Recommendation Engine (NBMs)

**Purpose:** Generate Next Best Moves (from BrightMatter TLDR Section 1)

```python
# lib/brain/recommendations.py
"""
Next Best Moves (NBM) Generator
From BrightMatter TLDR and Section 6.5
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import uuid

class MoveType(Enum):
    """Move types with learning weights (from BrightMatter 6.5)."""
    STANDARD = "standard"          # 1.25x weight
    VALIDATION = "validation"      # 1.50x weight
    SELF_GENERATED = "self_generated"  # 1.15x weight

class ReasonCode(Enum):
    """Marketing action reason codes."""
    REENGAGEMENT = "reengagement"
    CONVERSION = "conversion"
    RETENTION = "retention"
    UPSELL = "upsell"
    ADVOCACY = "advocacy"
    WIN_BACK = "win_back"
    ONBOARDING = "onboarding"
    DISCOVERY = "discovery"
    CONTENT_GAP = "content_gap"
    TREND_OPPORTUNITY = "trend_opportunity"

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Effort(Enum):
    LOW = "low"         # < 1 hour
    MEDIUM = "medium"   # 1-4 hours
    HIGH = "high"       # 4+ hours

@dataclass
class Recommendation:
    """A Next Best Move recommendation."""
    id: str
    client_id: str
    
    # Classification
    move_type: MoveType
    reason_code: ReasonCode
    priority: Priority
    effort: Effort
    
    # Action
    action: str
    description: str
    
    # Predictions
    confidence: float
    estimated_impact: Dict[str, float]
    
    # Reasoning
    reasoning: str
    supporting_data: Dict = field(default_factory=dict)
    
    # Prerequisites
    prerequisites: List[str] = field(default_factory=list)
    deadline: Optional[datetime] = None
    
    # Status tracking
    status: str = "pending"  # pending, accepted, rejected, completed, expired
    created_at: datetime = None
    expires_at: datetime = None
    
    def __post_init__(self):
        if not self.id:
            self.id = f"nbm_{uuid.uuid4().hex[:12]}"
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(days=7)

class RecommendationEngine:
    """
    Generates Next Best Moves based on analysis.
    
    From BrightMatter:
    - NBMs include confidence scores, estimated effort, projected impact
    - Regenerated daily with pruning
    - Different weights for Standard (1.25x), Validation (1.50x), Self-Generated (1.15x)
    """
    
    # Reason code triggers (thresholds that trigger recommendations)
    TRIGGERS = {
        ReasonCode.REENGAGEMENT: {
            "engagement_ratio_below": 0.7,
            "temporal_weight_below": 0.5,
        },
        ReasonCode.CONVERSION: {
            "engagement_ratio_above": 1.2,
            "quality_index_above": 1.0,
        },
        ReasonCode.RETENTION: {
            "authenticity_below": 0.7,
            "churn_risk_above": 0.3,
        },
        ReasonCode.UPSELL: {
            "overall_score_above": 800,
            "growth_above": 1.3,
        },
        ReasonCode.ADVOCACY: {
            "quality_index_above": 1.15,
            "engagement_ratio_above": 1.5,
        },
        ReasonCode.WIN_BACK: {
            "churned": True,
            "reactivation_potential_above": 0.4,
        },
        ReasonCode.ONBOARDING: {
            "is_new_client": True,
        },
        ReasonCode.DISCOVERY: {
            "data_completeness_below": 0.5,
        },
        ReasonCode.CONTENT_GAP: {
            "content_frequency_below": 0.5,
        },
        ReasonCode.TREND_OPPORTUNITY: {
            "trend_score_above": 0.8,
        },
    }
    
    # Action templates per reason code
    TEMPLATES = {
        ReasonCode.REENGAGEMENT: [
            {
                "action": "Launch re-engagement email sequence",
                "description": "Send targeted emails to {dormant_count} dormant contacts",
                "effort": Effort.MEDIUM,
                "impact_multiplier": 1.2,
            },
            {
                "action": "Publish trending content on {platform}",
                "description": "Create content aligned with current trends to boost visibility",
                "effort": Effort.HIGH,
                "impact_multiplier": 1.5,
            },
        ],
        ReasonCode.CONVERSION: [
            {
                "action": "Create bottom-funnel content",
                "description": "Develop case study or demo to convert engaged audience",
                "effort": Effort.HIGH,
                "impact_multiplier": 1.8,
            },
            {
                "action": "Launch retargeting campaign",
                "description": "Target engaged but unconverted visitors",
                "effort": Effort.MEDIUM,
                "impact_multiplier": 1.4,
            },
        ],
        # ... additional templates for each reason code
    }
    
    def __init__(self, firebase_client, config: 'BrainConfig'):
        self.firebase = firebase_client
        self.config = config
        
    def generate(
        self,
        client_id: str,
        score: 'PerformanceScore',
        analysis_context: Dict,
        limit: int = 5
    ) -> List[Recommendation]:
        """
        Generate recommendations for client.
        
        Steps:
        1. Check each reason code trigger
        2. Generate recommendations for triggered codes
        3. Score and rank recommendations
        4. Prune to top N
        5. Add validation moves if model uncertain
        """
        candidates = []
        
        # 1. Check triggers and generate candidates
        for reason_code, triggers in self.TRIGGERS.items():
            if self._check_triggers(score, analysis_context, triggers):
                recs = self._create_recommendations(
                    client_id, reason_code, score, analysis_context
                )
                candidates.extend(recs)
                
        # 2. Add validation move if uncertainty high
        if score.confidence < self.config.min_confidence_for_prediction:
            validation = self._create_validation_move(client_id, score)
            candidates.append(validation)
            
        # 3. Score and rank
        scored = [(r, self._score_recommendation(r, score)) for r in candidates]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # 4. Return top N
        return [r for r, _ in scored[:limit]]
        
    def _check_triggers(self, score: 'PerformanceScore', context: Dict, triggers: Dict) -> bool:
        """Check if triggers are met."""
        for trigger, threshold in triggers.items():
            if trigger.endswith("_below"):
                metric = trigger.replace("_below", "")
                value = getattr(score, metric, None) or context.get(metric, 0)
                if value >= threshold:
                    return False
            elif trigger.endswith("_above"):
                metric = trigger.replace("_above", "")
                value = getattr(score, metric, None) or context.get(metric, 0)
                if value <= threshold:
                    return False
            elif trigger in context:
                if context[trigger] != threshold:
                    return False
        return True
        
    def _create_recommendations(
        self,
        client_id: str,
        reason_code: ReasonCode,
        score: 'PerformanceScore',
        context: Dict
    ) -> List[Recommendation]:
        """Create recommendations for a reason code."""
        templates = self.TEMPLATES.get(reason_code, [])
        recommendations = []
        
        for template in templates:
            # Fill in template variables
            action = template["action"].format(**context)
            description = template["description"].format(**context)
            
            # Calculate estimated impact
            base_impact = 0.1 * score.overall * template["impact_multiplier"]
            
            rec = Recommendation(
                id="",
                client_id=client_id,
                move_type=MoveType.STANDARD,
                reason_code=reason_code,
                priority=self._determine_priority(score, reason_code),
                effort=template["effort"],
                action=action,
                description=description,
                confidence=score.confidence * 0.9,
                estimated_impact={
                    "score_delta": base_impact,
                    "engagement_delta": base_impact * 0.01,
                },
                reasoning=f"Triggered by {reason_code.value} conditions",
                supporting_data={"score": score.overall, "context": context},
            )
            recommendations.append(rec)
            
        return recommendations
        
    def _create_validation_move(self, client_id: str, score: 'PerformanceScore') -> Recommendation:
        """Create validation move to test model assumptions."""
        return Recommendation(
            id="",
            client_id=client_id,
            move_type=MoveType.VALIDATION,
            reason_code=ReasonCode.DISCOVERY,
            priority=Priority.MEDIUM,
            effort=Effort.LOW,
            action="Run A/B test on content format",
            description="Test hypothesis about optimal content format to calibrate model",
            confidence=0.5,
            estimated_impact={"model_confidence": 0.1},
            reasoning="Model confidence below threshold, validation needed",
        )
        
    def _score_recommendation(self, rec: Recommendation, score: 'PerformanceScore') -> float:
        """Score recommendation for ranking."""
        # Higher priority = higher score
        priority_scores = {Priority.CRITICAL: 4, Priority.HIGH: 3, Priority.MEDIUM: 2, Priority.LOW: 1}
        priority_score = priority_scores.get(rec.priority, 1)
        
        # Lower effort = higher score
        effort_scores = {Effort.LOW: 3, Effort.MEDIUM: 2, Effort.HIGH: 1}
        effort_score = effort_scores.get(rec.effort, 1)
        
        # Higher confidence = higher score
        confidence_score = rec.confidence * 3
        
        # Validation moves get bonus when model uncertain
        validation_bonus = 2 if rec.move_type == MoveType.VALIDATION and score.confidence < 0.6 else 0
        
        return priority_score + effort_score + confidence_score + validation_bonus
        
    def _determine_priority(self, score: 'PerformanceScore', reason_code: ReasonCode) -> Priority:
        """Determine priority based on score and reason."""
        # Critical: score dropping and retention issue
        if reason_code == ReasonCode.RETENTION and score.overall < 400:
            return Priority.CRITICAL
            
        # High: significant opportunity or risk
        if reason_code in [ReasonCode.WIN_BACK, ReasonCode.CONVERSION]:
            return Priority.HIGH
            
        # Low: exploratory
        if reason_code in [ReasonCode.DISCOVERY, ReasonCode.TREND_OPPORTUNITY]:
            return Priority.LOW
            
        return Priority.MEDIUM
        
    def prune_expired(self, client_id: str):
        """Prune expired recommendations."""
        # Get all pending recommendations
        recs = self.firebase.query(
            f"clients/{client_id}/brain/recommendations",
            where=[("status", "==", "pending")]
        )
        
        now = datetime.now()
        for rec in recs:
            expires_at = datetime.fromisoformat(rec.get("expires_at", "2099-01-01"))
            if expires_at < now:
                self.firebase.update(
                    f"clients/{client_id}/brain/recommendations/{rec['id']}",
                    {"status": "expired"}
                )
                
    def regenerate_daily(self, client_id: str):
        """
        Daily regeneration of recommendations.
        
        From BrightMatter: NBMs regenerated daily with pruning.
        """
        # 1. Prune expired
        self.prune_expired(client_id)
        
        # 2. Get current score
        # (Would call scorer here)
        
        # 3. Generate new recommendations
        # (Would call generate here)
        
        pass
```

---

# PHASE 3: Automation & Integration (Weeks 5-6)

## 3.1 Reporting Engine

**Purpose:** Automated reports at dual cadence (from BrightMatter TLDR Section 2)

```python
# lib/brain/reporting.py
"""
Reporting Engine
From BrightMatter TLDR Section 2:
- Hourly: Private cohort reports with projections
- Every 2 hours: Public category reports
- Rolling 90-day anomaly proof retention
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum

class ReportType(Enum):
    HOURLY_SCORE = "hourly_score"
    DAILY_ANALYSIS = "daily_analysis"
    WEEKLY_COMPREHENSIVE = "weekly_comprehensive"
    MONTHLY_SUMMARY = "monthly_summary"

class ReportCadence(Enum):
    HOURLY = "hourly"
    TWO_HOURLY = "two_hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

@dataclass
class Report:
    """Intelligence report."""
    report_id: str
    report_type: ReportType
    client_id: str
    
    # Content
    title: str
    summary: str
    scores: Dict[str, float]
    trends: Dict[str, Dict]
    predictions: Dict[str, Dict]
    anomalies: List[Dict]
    recommendations: List[Dict]
    
    # Metadata
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    model_version: str
    
    # Delivery
    delivery_channels: List[str] = field(default_factory=list)
    delivered_at: Optional[datetime] = None

class ReportingEngine:
    """
    Generates reports at specified cadences.
    """
    
    # Anomaly retention period (from BrightMatter)
    ANOMALY_RETENTION_DAYS = 90
    
    def __init__(self, firebase_client, scorer, predictor, recommender, anomaly_detector):
        self.firebase = firebase_client
        self.scorer = scorer
        self.predictor = predictor
        self.recommender = recommender
        self.anomaly_detector = anomaly_detector
        
    def generate_hourly(self, client_id: str) -> Report:
        """
        Hourly score update and anomaly check.
        
        From BrightMatter: Private cohort reports showing verified performance,
        anomalies, and projections for T+24h and T+7d.
        """
        # Get recent events
        events = self._get_recent_events(client_id, hours=1)
        
        # Score
        scores = {}
        for event in events:
            score = self.scorer.score(event)
            scores[event.event_id] = score.__dict__
            
        # Detect anomalies
        history = self._get_event_history(client_id, days=30)
        anomalies = []
        for event in events:
            detected = self.anomaly_detector.detect(event, history)
            anomalies.extend([a.__dict__ for a in detected])
            
        # Generate predictions (if enough data)
        predictions = {}
        if history:
            latest_score = list(scores.values())[-1] if scores else None
            if latest_score:
                from .scoring import PerformanceScore
                score_obj = PerformanceScore(**latest_score)
                predictions = self.predictor.predict(
                    score_obj,
                    [PerformanceScore(**s) for s in scores.values()],
                    events[0].platform if events else "email",
                    ["24h", "7d"]
                )
                predictions = {k: v.__dict__ for k, v in predictions.items()}
                
        # Create report
        now = datetime.now()
        report = Report(
            report_id=f"hourly_{client_id}_{now.strftime('%Y%m%d%H')}",
            report_type=ReportType.HOURLY_SCORE,
            client_id=client_id,
            title=f"Hourly Score Update - {now.strftime('%Y-%m-%d %H:00')}",
            summary=self._generate_hourly_summary(scores, anomalies),
            scores=scores,
            trends={},
            predictions=predictions,
            anomalies=anomalies,
            recommendations=[],
            generated_at=now,
            period_start=now - timedelta(hours=1),
            period_end=now,
            model_version=self.scorer.config.model_version,
        )
        
        # Persist
        self._persist_report(report)
        
        return report
        
    def generate_daily(self, client_id: str) -> Report:
        """
        Daily analysis with trends and predictions.
        """
        now = datetime.now()
        
        # Get 24-hour data
        events = self._get_recent_events(client_id, hours=24)
        history = self._get_event_history(client_id, days=30)
        
        # Calculate scores
        scores = {}
        for event in events:
            score = self.scorer.score(event, history)
            scores[event.event_id] = score.__dict__
            
        # Calculate trends (compare to yesterday)
        trends = self._calculate_trends(client_id, days=7)
        
        # Generate predictions
        predictions = {}
        if scores:
            latest = PerformanceScore(**list(scores.values())[-1])
            predictions = self.predictor.predict(latest, history, "email", ["24h", "7d", "30d"])
            predictions = {k: v.__dict__ for k, v in predictions.items()}
            
        # Detect anomalies
        anomalies = []
        for event in events:
            detected = self.anomaly_detector.detect(event, history)
            anomalies.extend([a.__dict__ for a in detected])
            
        report = Report(
            report_id=f"daily_{client_id}_{now.strftime('%Y%m%d')}",
            report_type=ReportType.DAILY_ANALYSIS,
            client_id=client_id,
            title=f"Daily Analysis - {now.strftime('%Y-%m-%d')}",
            summary=self._generate_daily_summary(scores, trends, anomalies),
            scores=scores,
            trends=trends,
            predictions=predictions,
            anomalies=anomalies,
            recommendations=[],
            generated_at=now,
            period_start=now - timedelta(days=1),
            period_end=now,
            model_version=self.scorer.config.model_version,
        )
        
        self._persist_report(report)
        return report
        
    def generate_weekly(self, client_id: str) -> Report:
        """
        Weekly comprehensive report with recommendations.
        """
        now = datetime.now()
        
        # Get week's data
        events = self._get_recent_events(client_id, hours=168)
        history = self._get_event_history(client_id, days=90)
        
        # Calculate scores
        scores = {}
        for event in events:
            score = self.scorer.score(event, history)
            scores[event.event_id] = score.__dict__
            
        # Calculate trends
        trends = self._calculate_trends(client_id, days=30)
        
        # Generate predictions
        predictions = {}
        if scores:
            latest = PerformanceScore(**list(scores.values())[-1])
            predictions = self.predictor.predict(latest, history, "email", ["7d", "30d"])
            predictions = {k: v.__dict__ for k, v in predictions.items()}
            
        # Detect anomalies
        anomalies = []
        for event in events:
            detected = self.anomaly_detector.detect(event, history)
            anomalies.extend([a.__dict__ for a in detected])
            
        # Generate recommendations
        if scores:
            latest_score = PerformanceScore(**list(scores.values())[-1])
            context = self._build_analysis_context(client_id, events, history)
            recs = self.recommender.generate(client_id, latest_score, context)
            recommendations = [r.__dict__ for r in recs]
        else:
            recommendations = []
            
        report = Report(
            report_id=f"weekly_{client_id}_{now.strftime('%Y%m%d')}",
            report_type=ReportType.WEEKLY_COMPREHENSIVE,
            client_id=client_id,
            title=f"Weekly Intelligence Report - Week of {now.strftime('%Y-%m-%d')}",
            summary=self._generate_weekly_summary(scores, trends, anomalies, recommendations),
            scores=scores,
            trends=trends,
            predictions=predictions,
            anomalies=anomalies,
            recommendations=recommendations,
            generated_at=now,
            period_start=now - timedelta(days=7),
            period_end=now,
            model_version=self.scorer.config.model_version,
        )
        
        self._persist_report(report)
        return report
        
    def _persist_report(self, report: Report):
        """Persist report to Firebase."""
        self.firebase.set(
            f"clients/{report.client_id}/brain/reports/{report.report_id}",
            {
                "report_type": report.report_type.value,
                "title": report.title,
                "summary": report.summary,
                "scores": report.scores,
                "trends": report.trends,
                "predictions": report.predictions,
                "anomalies": report.anomalies,
                "recommendations": report.recommendations,
                "generated_at": report.generated_at.isoformat(),
                "period_start": report.period_start.isoformat(),
                "period_end": report.period_end.isoformat(),
                "model_version": report.model_version,
            }
        )
        
    def cleanup_old_anomalies(self, client_id: str):
        """
        Remove anomalies older than retention period.
        
        From BrightMatter: Rolling 90-day archive for anomaly proofs.
        """
        cutoff = datetime.now() - timedelta(days=self.ANOMALY_RETENTION_DAYS)
        
        anomalies = self.firebase.query(
            f"clients/{client_id}/brain/anomalies",
            where=[("detected_at", "<", cutoff.isoformat())]
        )
        
        for anomaly in anomalies:
            self.firebase.delete(f"clients/{client_id}/brain/anomalies/{anomaly['id']}")
            
    # Helper methods
    def _get_recent_events(self, client_id: str, hours: int) -> List:
        """Get events from last N hours."""
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        return self.firebase.query(
            f"clients/{client_id}/events",
            where=[("timestamp", ">=", cutoff)],
            order_by="timestamp"
        )
        
    def _get_event_history(self, client_id: str, days: int) -> List:
        """Get event history for N days."""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        return self.firebase.query(
            f"clients/{client_id}/events",
            where=[("timestamp", ">=", cutoff)],
            order_by="timestamp"
        )
        
    def _calculate_trends(self, client_id: str, days: int) -> Dict:
        """Calculate trends over period."""
        # Simplified - would calculate deltas for each metric
        return {
            "engagement": {"delta": 0.05, "direction": "up"},
            "quality": {"delta": -0.02, "direction": "down"},
            "overall": {"delta": 0.03, "direction": "up"},
        }
        
    def _build_analysis_context(self, client_id: str, events: List, history: List) -> Dict:
        """Build context for recommendation generation."""
        return {
            "event_count": len(events),
            "history_length": len(history),
            "is_new_client": len(history) < 10,
            "data_completeness": min(1.0, len(history) / 30),
        }
        
    def _generate_hourly_summary(self, scores: Dict, anomalies: List) -> str:
        """Generate hourly summary text."""
        avg_score = sum(s.get("overall", 0) for s in scores.values()) / len(scores) if scores else 0
        return f"Average score: {avg_score:.0f}. {len(anomalies)} anomalies detected."
        
    def _generate_daily_summary(self, scores: Dict, trends: Dict, anomalies: List) -> str:
        """Generate daily summary text."""
        avg_score = sum(s.get("overall", 0) for s in scores.values()) / len(scores) if scores else 0
        trend_dir = trends.get("overall", {}).get("direction", "flat")
        return f"Daily average: {avg_score:.0f}. Trend: {trend_dir}. {len(anomalies)} anomalies."
        
    def _generate_weekly_summary(self, scores: Dict, trends: Dict, anomalies: List, recs: List) -> str:
        """Generate weekly summary text."""
        avg_score = sum(s.get("overall", 0) for s in scores.values()) / len(scores) if scores else 0
        return f"Weekly average: {avg_score:.0f}. {len(recs)} recommendations. {len(anomalies)} anomalies."
```

## 3.2 Scheduler Configuration

**Purpose:** Automated job scheduling (Firebase Cloud Functions)

```yaml
# config/brain_scheduler.yaml
# Scheduler configuration for Brain automated jobs

scheduler:
  provider: firebase_cloud_functions
  timezone: "UTC"
  
jobs:
  # Hourly score updates
  hourly_scores:
    function: "brainHourlyScores"
    schedule: "0 * * * *"  # Every hour
    timeout_seconds: 300
    memory: "256MB"
    description: "Calculate hourly scores and detect anomalies"
    
  # Daily analysis
  daily_analysis:
    function: "brainDailyAnalysis"
    schedule: "0 6 * * *"  # 6 AM UTC daily
    timeout_seconds: 600
    memory: "512MB"
    description: "Generate daily analysis with trends and predictions"
    
  # Weekly comprehensive report
  weekly_recommendations:
    function: "brainWeeklyReport"
    schedule: "0 9 * * 1"  # Monday 9 AM UTC
    timeout_seconds: 900
    memory: "512MB"
    description: "Generate weekly report with recommendations"
    
  # Daily recommendation refresh
  daily_recommendation_refresh:
    function: "brainRefreshRecommendations"
    schedule: "0 8 * * *"  # 8 AM UTC daily
    timeout_seconds: 300
    memory: "256MB"
    description: "Regenerate and prune recommendations"
    
  # Shadow mode evaluation (weekly)
  weekly_shadow_evaluation:
    function: "brainEvaluateShadowMode"
    schedule: "0 10 * * 0"  # Sunday 10 AM UTC
    timeout_seconds: 600
    memory: "512MB"
    description: "Evaluate and potentially promote shadow candidates"
    
  # Anomaly cleanup (monthly)
  monthly_anomaly_cleanup:
    function: "brainCleanupAnomalies"
    schedule: "0 0 1 * *"  # 1st of month midnight
    timeout_seconds: 300
    memory: "256MB"
    description: "Remove anomalies older than 90 days"

error_handling:
  retry_policy:
    max_retries: 3
    initial_delay_seconds: 60
    max_delay_seconds: 3600
    multiplier: 2.0
  
  alerts:
    - type: "slack"
      channel: "#mh1-alerts"
      on: ["failure", "timeout"]
    - type: "email"
      recipients: ["ops@mh1.com"]
      on: ["failure"]
```

## 3.3 Report Delivery

```python
# lib/brain/delivery.py
"""
Report Delivery System
"""

from typing import Dict, List
from abc import ABC, abstractmethod

class DeliveryChannel(ABC):
    @abstractmethod
    def send(self, report: 'Report', config: Dict) -> bool:
        pass

class FirebaseDelivery(DeliveryChannel):
    """Store in Firebase for UI consumption."""
    def send(self, report: 'Report', config: Dict) -> bool:
        # Already persisted in reporting engine
        return True

class SlackDelivery(DeliveryChannel):
    """Send to Slack channel."""
    def send(self, report: 'Report', config: Dict) -> bool:
        webhook_url = config.get("webhook_url")
        if not webhook_url:
            return False
            
        message = self._format_message(report)
        # POST to webhook
        return True
        
    def _format_message(self, report: 'Report') -> Dict:
        return {
            "text": f"*{report.title}*\n{report.summary}",
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": report.summary}
                }
            ]
        }

class EmailDelivery(DeliveryChannel):
    """Send via email."""
    def send(self, report: 'Report', config: Dict) -> bool:
        recipients = config.get("recipients", [])
        if not recipients:
            return False
        # Send email
        return True

class ReportDeliveryManager:
    """Manages report delivery to multiple channels."""
    
    CHANNELS = {
        "firebase": FirebaseDelivery,
        "slack": SlackDelivery,
        "email": EmailDelivery,
    }
    
    def deliver(self, report: 'Report', client_config: Dict):
        """Deliver report to configured channels."""
        channels = client_config.get("report_channels", ["firebase"])
        
        for channel_name in channels:
            channel_class = self.CHANNELS.get(channel_name)
            if channel_class:
                channel = channel_class()
                channel_config = client_config.get(f"{channel_name}_config", {})
                channel.send(report, channel_config)
```

## 3.4 UI API Endpoints

```typescript
// ui/app/api/brain/[clientId]/scores/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { clientId: string } }
) {
  const { clientId } = params;
  
  // Get latest scores from Firebase
  const scores = await getLatestScores(clientId);
  
  return NextResponse.json({
    clientId,
    scores,
    generatedAt: new Date().toISOString(),
  });
}

// ui/app/api/brain/[clientId]/predictions/route.ts
export async function GET(
  request: NextRequest,
  { params }: { params: { clientId: string } }
) {
  const { clientId } = params;
  
  const predictions = await getPredictions(clientId);
  
  return NextResponse.json({
    clientId,
    predictions,
  });
}

// ui/app/api/brain/[clientId]/recommendations/route.ts
export async function GET(
  request: NextRequest,
  { params }: { params: { clientId: string } }
) {
  const { clientId } = params;
  
  const recommendations = await getRecommendations(clientId);
  
  return NextResponse.json({
    clientId,
    recommendations,
  });
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: { clientId: string } }
) {
  const { clientId } = params;
  const { recommendationId, status } = await request.json();
  
  // Update recommendation status (accepted/rejected)
  await updateRecommendationStatus(clientId, recommendationId, status);
  
  return NextResponse.json({ success: true });
}
```

## 3.5 Integration with Existing Skills

```python
# Updates to existing skills to integrate with Brain

# In skills that generate content (ghostwrite-content, email-copy-generator):
"""
## Brain Integration

After content is published:
1. Create MarketingEvent with initial metrics
2. Schedule follow-up to record final outcome
3. Feed outcome to learning loop

Example:
```python
from lib.brain import EventGateway, MarketingEvent

# After publishing
gateway = EventGateway(firebase_client, config)
event = gateway.ingest("linkedin", post_data, client_id)

# Schedule outcome recording (24h later)
schedule_outcome_recording(event.event_id, client_id, timedelta(hours=24))
```
"""

# In skills that analyze (lifecycle-audit, pipeline-analysis):
"""
## Brain Integration

After analysis complete:
1. Feed analysis data to Brain scorer
2. Store scores in Firebase
3. Trigger recommendation generation if scores below threshold

Example:
```python
from lib.brain import PerformanceScorer, RecommendationEngine

scorer = PerformanceScorer(config)
score = scorer.score(analysis_event, history)

if score.overall < 500:
    recommender = RecommendationEngine(firebase, config)
    recs = recommender.generate(client_id, score, context)
```
"""
```

## 3.6 Benchmarking / Gold Standard Datasets

```yaml
# config/brain_benchmarks.yaml
# Gold standard datasets for model validation

gold_standards:
  email_campaigns:
    location: "system/brain/gold_standards/email_campaigns"
    description: "50 verified email campaign outcomes"
    min_samples: 50
    metrics:
      engagement_prediction_error:
        threshold: 0.15
        description: "Mean absolute error on engagement rate prediction"
      score_prediction_error:
        threshold: 0.20
        description: "Mean absolute error on overall score prediction"
      trend_accuracy:
        threshold: 0.70
        description: "Accuracy of trend direction prediction"
        
  social_posts:
    location: "system/brain/gold_standards/social_posts"
    description: "100 verified social post outcomes"
    min_samples: 100
    metrics:
      engagement_prediction_error:
        threshold: 0.20
      viral_detection_accuracy:
        threshold: 0.60
        
  multi_platform:
    location: "system/brain/gold_standards/multi_platform"
    description: "Cross-platform campaign outcomes"
    min_samples: 30
    metrics:
      cross_platform_normalization_error:
        threshold: 0.10

validation:
  schedule: "weekly"
  on_shadow_promotion: required
  report_failures: true
  failure_threshold: 0.5  # If >50% of metrics fail, block promotion
```

---

# Summary: File Structure

```
lib/brain/
├── __init__.py              # Exports
├── config.py                # BrainConfig
├── types.py                 # Type definitions
├── engine.py                # Main BrainEngine (orchestrator)
├── ingest.py                # EventGateway, FeedRouter
├── scoring.py               # PerformanceScorer
├── templates.py             # ProcessingTemplate
├── anomaly.py               # AnomalyDetector
├── learning.py              # LearningLoop, GoldStandardValidator
├── predictions.py           # PredictionEngine
├── recommendations.py       # RecommendationEngine
├── reporting.py             # ReportingEngine
└── delivery.py              # ReportDeliveryManager

config/
├── brain_scheduler.yaml     # Scheduler jobs
└── brain_benchmarks.yaml    # Gold standard configs

skills/
├── generate-recommendations/SKILL.md
└── intelligence-report/SKILL.md

ui/app/api/brain/
├── [clientId]/
│   ├── scores/route.ts
│   ├── predictions/route.ts
│   ├── recommendations/route.ts
│   └── reports/route.ts
└── health/route.ts
```

---

# Implementation Checklist

## Phase 1 (Weeks 1-2)
- [ ] Create `lib/brain/` module structure
- [ ] Implement `config.py` and `types.py`
- [ ] Implement `ingest.py` (EventGateway, FeedRouter)
- [ ] Implement `scoring.py` (BrightMatter V' formula)
- [ ] Implement `templates.py` (ProcessingTemplate)
- [ ] Implement `anomaly.py` (AnomalyDetector)
- [ ] Create Firebase schema
- [ ] Unit tests for scoring

## Phase 2 (Weeks 3-4)
- [ ] Implement `learning.py` (LearningLoop, ShadowMode)
- [ ] Implement `predictions.py` (integrate with lib/forecasting.py)
- [ ] Implement `recommendations.py` (NBMs)
- [ ] Create gold standard datasets
- [ ] Implement GoldStandardValidator
- [ ] Unit tests for learning and recommendations

## Phase 3 (Weeks 5-6)
- [ ] Implement `reporting.py` (ReportingEngine)
- [ ] Implement `delivery.py` (multi-channel delivery)
- [ ] Create `config/brain_scheduler.yaml`
- [ ] Implement Cloud Functions for scheduled jobs
- [ ] Create UI API endpoints
- [ ] Create UI components
- [ ] Update existing skills for Brain integration
- [ ] Integration tests
- [ ] Documentation
