# Account 360 Analysis
## Module: swimply-lifecycle-audit-20260130 | Skill #3

**Generated:** 2026-01-30
**Client:** B0bCCLkqvFhK7JCWKNR1
**Data Sources:** Braze CDP, Platform KPIs, Segment Analysis

---

## Page 1: Executive Summary & Key Findings

### Executive Summary

This Account 360 provides a unified view of Swimply's customer data infrastructure, user segments, and engagement patterns as captured in their Braze customer data platform. With ~6,500 daily active users, ~24,000 daily sessions, and a mature two-sided marketplace (guests + hosts), Swimply has built sophisticated lifecycle automation on a Braze-only architecture that serves as both CDP and marketing automation platform.

### Key Findings

1. **Engaged User Base:** 3.7 sessions per DAU indicates highly engaged users browsing multiple listings
2. **Two-Sided Complexity:** 95+ segments manage distinct guest and host journeys
3. **Mature Automation:** 90+ canvases cover full lifecycle from onboarding to win-back
4. **Seasonal Patterns:** Weekend DAU peaks 40% higher than mid-week (leisure usage)
5. **Data Gaps:** No revenue/LTV attributes - booking counts used as proxy

### Platform Health Dashboard

| Metric | Value | Trend | Benchmark |
|--------|-------|-------|-----------|
| Daily Active Users (avg) | 6,500 | Stable | - |
| Daily Sessions (avg) | 24,000 | Stable | - |
| Sessions per DAU | 3.7 | Healthy | 2.5+ good |
| App Uninstalls (30d) | 5,638 | Monitor | - |
| Custom Attributes | 50 | Adequate | - |
| Custom Events | 250 | Comprehensive | - |
| Segments | 95+ | Mature | - |
| Active Campaigns | 100+ | Active | - |
| Active Canvases | 90+ | Comprehensive | - |

### User Activity Patterns (30-Day View)

```
DAU Trend:
Peak:    8,700 (Jan 3-4, weekend)
Trough:  5,600 (Jan 12-14, mid-week)
Current: 6,833 (Jan 29)
Variance: ~40% between peak and trough

Sessions Trend:
Peak:   28,634 (Jan 6)
Low:    19,420 (Dec 31)
Average: 24,000/day
```

**Insight:** Strong weekend leisure usage pattern. Mid-week represents opportunity for business/corporate bookings.

---

## Page 2: Detailed Data Model & Segmentation

### Customer Data Architecture

**Data Platform:** Braze serves as unified CDP (no separate warehouse/CRM)

```
┌─────────────────────────────────────────────────────────┐
│                    BRAZE CDP LAYER                      │
├─────────────────────────────────────────────────────────┤
│  50 Custom Attributes    │    250 Custom Events        │
│  - Booking metrics       │    - Booking lifecycle      │
│  - User activity         │    - Guest/Host actions     │
│  - Listing/favorites     │    - Review/Rating          │
│  - Financial (credits)   │    - Premium/Subscription   │
│  - Identity              │    - Referral               │
├─────────────────────────────────────────────────────────┤
│  95+ Segments            │    90+ Canvases             │
│  - Guest lifecycle       │    - Guest journey          │
│  - Host lifecycle        │    - Host onboarding        │
│  - Geographic            │    - Transactional          │
│  - Behavioral            │    - Win-back               │
└─────────────────────────────────────────────────────────┘
```

### Key Customer Attributes

**Booking Metrics (Core Value Indicators):**
| Attribute | Type | Use Case |
|-----------|------|----------|
| `BOOKING_COUNT_AS_GUEST` | Number | Lifetime value proxy |
| `COMPLETED_BOOKINGS_COUNT_AS_GUEST` | Number | Actual value delivered |
| `COMPLETED_BOOKINGS_YTD_AS_GUEST` | Number | Current year engagement |
| `CANCELLED_BOOKINGS_COUNT_AS_GUEST` | Number | Risk indicator |
| `DENIED_BOOKINGS_COUNT_AS_GUEST` | Number | Supply constraint signal |

**Activity & Engagement:**
| Attribute | Type | Use Case |
|-----------|------|----------|
| `DAYS_SINCE_LAST_PLATFORM_ACTIVITY` | Number | Churn risk scoring |
| `ACCOUNT_CREATED_AT` | Timestamp | Cohort analysis |
| `CURRENT_CREDIT_BALANCE` | Number | Conversion lever |

**Host-Specific:**
| Attribute | Type | Use Case |
|-----------|------|----------|
| `COMPLETED_BOOKINGS_COUNT_AS_HOST` | Number | Host performance |
| `TOTAL_LIVE_LISTINGS_AS_HOST` | Number | Supply indicator |
| `CANCELLED_BOOKINGS_COUNT_AS_HOST` | Number | Reliability score |

### Segment Architecture

**Guest Segments:**
| Segment | Definition | Est. Size |
|---------|------------|-----------|
| `Guest-HasAccount0bookings` | Signed up, never booked | Large |
| `Guest-HasBookings` | Completed 1+ bookings | Core |
| `MASTER-GUEST` | All guests | Total |

**Host Segments:**
| Segment | Definition | Est. Size |
|---------|------------|-----------|
| `V2_Hosts-CurrentlyLive` | Active listings | Supply base |
| `V2_Hosts-NOT-Currently-Live` | Paused/inactive | Win-back pool |
| `WaitlistedHost` | Pending approval | Pipeline |

**Value-Based (Derived):**
| Tier | Criteria | Marketing Focus |
|------|----------|-----------------|
| No Bookings | `COMPLETED_BOOKINGS = 0` | Activation |
| Low Value | `COMPLETED_BOOKINGS = 1` | Retention |
| Medium Value | `COMPLETED_BOOKINGS 2-4` | Upsell |
| High Value | `COMPLETED_BOOKINGS >= 5` | Loyalty |

### Channel Distribution

| Channel | Status | Use Case |
|---------|--------|----------|
| Email | Active | Primary lifecycle |
| Push (iOS) | Active | Transactional, urgency |
| Push (Android) | Active | Transactional, urgency |
| SMS | Active | Time-sensitive (cart abandon) |
| In-App | Active | Feature promotion |

### Data Quality Assessment

| Dimension | Score | Notes |
|-----------|-------|-------|
| Completeness | 7/10 | Missing revenue/LTV data |
| Accuracy | 8/10 | Well-maintained Braze instance |
| Timeliness | 8/10 | Real-time event tracking |
| Consistency | 6/10 | Naming conventions vary |
| Accessibility | 7/10 | Braze-only limits analytics depth |

### Recommended Data Enhancements

| Enhancement | Priority | Impact |
|-------------|----------|--------|
| Add `LIFETIME_GMV` attribute | High | Enable true LTV analysis |
| Add `NPS_SCORE` attribute | High | Link reviews to satisfaction |
| Add `LAST_BOOKING_DATE` attribute | Medium | Simplify recency queries |
| Enable Braze Currents | High | Deep analytics capability |
| Standardize segment naming | Medium | Operational efficiency |

### Account Health Indicators

| Indicator | Status | Action |
|-----------|--------|--------|
| User growth | Stable | Monitor seasonality |
| Engagement depth | Strong (3.7 sessions/user) | Maintain |
| Automation maturity | High | Optimize, don't rebuild |
| Data infrastructure | Adequate | Enhance with Currents |
| Channel coverage | Comprehensive | Test new channels |

---

*Report generated by MH1 account-360 skill v1.0.0*
*Data source: Braze REST API (US-05 cluster)*
