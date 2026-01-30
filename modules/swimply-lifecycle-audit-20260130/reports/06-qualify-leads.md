# Lead Qualification Analysis
## Module: swimply-lifecycle-audit-20260130 | Skill #6

**Generated:** 2026-01-30
**Client:** B0bCCLkqvFhK7JCWKNR1
**Data Sources:** Braze Attributes, Behavioral Events, Segment Definitions

---

## Page 1: Executive Summary & Key Findings

### Executive Summary

This analysis develops a lead qualification framework for Swimply guests, scoring users based on intent signals, engagement patterns, and conversion likelihood. Unlike B2B lead scoring, marketplace lead qualification focuses on booking propensity and lifetime value potential. The scoring model leverages Braze's custom attributes and events to identify high-intent users for prioritized marketing investment.

### Key Findings

1. **Behavioral Signals Rich:** 250 custom events provide extensive intent data (cart, favorites, messages)
2. **Recency Data Available:** `DAYS_SINCE_LAST_PLATFORM_ACTIVITY` enables activity-based scoring
3. **Value Proxy Clear:** `COMPLETED_BOOKINGS_COUNT_AS_GUEST` indicates proven value
4. **Credit Indicator:** Users with credit balance are pre-qualified for conversion
5. **Host Interaction:** `GuestMessageSent` shows high-intent engagement

### Lead Scoring Model (Guest)

| Score Range | Qualification | Est. % of Base | Marketing Treatment |
|-------------|---------------|----------------|---------------------|
| 80-100 | Hot Lead | 5% | Immediate conversion focus |
| 60-79 | Warm Lead | 15% | Nurture to booking |
| 40-59 | Cool Lead | 30% | Education/awareness |
| 0-39 | Cold Lead | 50% | Re-engagement or exclude |

### Scoring Factors

```
BEHAVIORAL SIGNALS (50 points max)
├── CartCreated (last 7d): +20 pts
├── GuestCreatedFavoriteList: +15 pts
├── GuestMessageSent: +25 pts
├── GuestPressedAcceptAndPay: +30 pts
└── Search activity (sessions): +5-15 pts

PROFILE ATTRIBUTES (30 points max)
├── CURRENT_CREDIT_BALANCE > 0: +15 pts
├── COMPLETED_BOOKINGS_COUNT >= 1: +20 pts
├── DAYS_SINCE_LAST_ACTIVITY < 7: +10 pts
└── Email verified: +5 pts

ENGAGEMENT RECENCY (20 points max)
├── Activity today: +20 pts
├── Activity last 7d: +15 pts
├── Activity last 30d: +10 pts
└── Activity 30-90d: +5 pts
```

---

## Page 2: Detailed Scoring Model & Implementation

### Tier 1: Hot Leads (Score 80-100)

**Definition:** Users showing immediate booking intent

**Qualifying Behaviors:**
| Signal | Points | Braze Event/Attribute |
|--------|--------|----------------------|
| Cart created (7d) | +20 | `CartCreated` |
| Pressed Accept & Pay | +30 | `GuestPressedAcceptAndPay` |
| Messaged host | +25 | `GuestMessageSent` |
| Has credits | +15 | `CURRENT_CREDIT_BALANCE > 0` |
| Active today | +20 | `DAYS_SINCE_LAST_ACTIVITY = 0` |

**Marketing Treatment:**
- Cart abandonment sequences (already active)
- SMS for urgency messaging
- Host-side nudge to respond quickly
- Real-time retargeting ads

**Recommended Segment:** `HOT_LEAD_GUESTS`
```
Criteria:
- CartCreated in last 7 days
- OR GuestPressedAcceptAndPay in last 7 days
- OR (GuestMessageSent in last 7 days AND DAYS_SINCE_LAST_ACTIVITY < 3)
```

### Tier 2: Warm Leads (Score 60-79)

**Definition:** Users with demonstrated interest but not immediate intent

**Qualifying Behaviors:**
| Signal | Points | Braze Event/Attribute |
|--------|--------|----------------------|
| Created favorite list | +15 | `GuestCreatedFavoriteList` |
| Has booking history | +20 | `COMPLETED_BOOKINGS_COUNT >= 1` |
| Active last 7d | +15 | `DAYS_SINCE_LAST_ACTIVITY < 7` |
| Multiple sessions | +10 | Session count indicator |
| Received special offer | +10 | `GuestReceivedSpecialOffer` |

**Marketing Treatment:**
- Personalized pool recommendations
- "Your favorited pools are booking up"
- Seasonal anticipation campaigns
- Referral program promotion

**Recommended Segment:** `WARM_LEAD_GUESTS`
```
Criteria:
- GuestCreatedFavoriteList ever
- AND DAYS_SINCE_LAST_ACTIVITY < 14
- AND NOT in HOT_LEAD_GUESTS
```

### Tier 3: Cool Leads (Score 40-59)

**Definition:** Users with potential but low recent engagement

**Qualifying Behaviors:**
| Signal | Points | Braze Event/Attribute |
|--------|--------|----------------------|
| Account created | +10 | `ACCOUNT_CREATED_AT` |
| Email verified | +5 | `EMAIL_VERIFIED_AT` exists |
| Active last 30d | +10 | `DAYS_SINCE_LAST_ACTIVITY < 30` |
| No bookings yet | 0 | `COMPLETED_BOOKINGS_COUNT = 0` |

**Marketing Treatment:**
- Educational content (how Swimply works)
- Social proof (reviews, popularity)
- Low-commitment CTAs (browse, save)
- Welcome series completion

**Recommended Segment:** `COOL_LEAD_GUESTS`
```
Criteria:
- ACCOUNT_CREATED_AT exists
- AND COMPLETED_BOOKINGS_COUNT = 0
- AND DAYS_SINCE_LAST_ACTIVITY between 7-30
```

### Tier 4: Cold Leads (Score 0-39)

**Definition:** Inactive or disengaged users

**Qualifying Behaviors:**
| Signal | Points | Braze Event/Attribute |
|--------|--------|----------------------|
| Inactive 30+ days | 0 | `DAYS_SINCE_LAST_ACTIVITY > 30` |
| No bookings | 0 | `COMPLETED_BOOKINGS_COUNT = 0` |
| Email unverified | 0 | No `EMAIL_VERIFIED_AT` |

**Marketing Treatment:**
- Win-back campaigns (seasonal triggers)
- Email frequency reduction
- Re-permission campaigns
- Consider suppression if 180+ days inactive

**Recommended Segment:** `COLD_LEAD_GUESTS` (maps to existing `Guest-HasAccount0bookings` with activity filter)

### Lead Score Implementation in Braze

**Option 1: Computed Attribute (Recommended)**
Create calculated field `LEAD_SCORE` updated daily based on:
```
LEAD_SCORE =
  (CartCreated_7d * 20) +
  (MessageSent_7d * 25) +
  (HasCredits * 15) +
  (HasBookings * 20) +
  (Recency_Score) +
  (FavoriteList * 15)
```

**Option 2: Segment-Based Scoring**
Create four segments (Hot, Warm, Cool, Cold) with rules above

### Qualification-Based Automation

| Trigger | Segment | Action |
|---------|---------|--------|
| Score drops below 40 | Was Warm | Re-engagement sequence |
| Score rises above 60 | Was Cool | Conversion-focused messages |
| Score rises above 80 | Any | Immediate cart/booking push |
| Score stays Hot 7d | Hot | Personalized outreach |

### Recommended Priority Actions

| Action | Impact | Effort | Priority |
|--------|--------|--------|----------|
| Create Hot Lead segment | High | Low | **P1** |
| Build score-based automation | High | Medium | **P1** |
| Implement lead score attribute | Medium | Medium | **P2** |
| Create lead score dashboard | Medium | Medium | **P2** |
| A/B test score thresholds | Medium | Low | **P3** |

---

*Report generated by MH1 qualify-leads skill v1.0.0*
*Data source: Braze attributes, event analysis*
