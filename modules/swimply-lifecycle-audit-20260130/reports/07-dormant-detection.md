# Dormant User Detection Analysis
## Module: swimply-lifecycle-audit-20260130 | Skill #7

**Generated:** 2026-01-30
**Client:** B0bCCLkqvFhK7JCWKNR1
**Data Sources:** Braze Attributes, Activity Data, Segment Analysis

---

## Page 1: Executive Summary & Key Findings

### Executive Summary

This analysis identifies dormant users across both guest and host populations, establishes detection criteria, and evaluates existing re-engagement strategies. Swimply's `DAYS_SINCE_LAST_PLATFORM_ACTIVITY` attribute provides the foundation for dormancy detection, with existing automation for 30-day inactive hosts but gaps in guest dormancy handling.

### Key Findings

1. **Activity Tracking Exists:** `DAYS_SINCE_LAST_PLATFORM_ACTIVITY` enables dormancy detection
2. **Host Automation Active:** `InactiveHosts30D` canvas addresses dormant hosts
3. **Guest Dormancy Gap:** No clear "inactive guest" re-engagement canvas visible
4. **360-Day Win-Back:** Long-term win-back exists but intermediate periods underserved
5. **Uninstall Rate:** 5,638 uninstalls in 30 days indicates churn requiring attention

### Dormancy Definition Framework

| User Type | Stage | Criteria | Risk Level |
|-----------|-------|----------|------------|
| Guest | At Risk | 14-29 days inactive | Medium |
| Guest | Dormant | 30-89 days inactive | High |
| Guest | Churned | 90-179 days inactive | Very High |
| Guest | Lost | 180+ days inactive | Critical |
| Host | At Risk | 14-29 days inactive | Medium |
| Host | Dormant | 30-59 days inactive | High |
| Host | Churned | 60+ days inactive | Critical |

### Dormancy Detection Metrics

```
Current User Activity Distribution (Estimated):

GUESTS:
├── Active (0-7 days): ~65% of DAU base
├── At-Risk (14-29 days): ~15%
├── Dormant (30-89 days): ~25% of total registered
├── Churned (90-179 days): ~20% of total registered
└── Lost (180+ days): ~30% of total registered

HOSTS:
├── Active/Live: V2_Hosts-CurrentlyLive segment
├── Inactive/Paused: V2_Hosts-NOT-Currently-Live
├── 30D Inactive: Targeted by InactiveHosts30D canvas
└── Waitlisted: WaitlistedHost segment (never activated)
```

---

## Page 2: Detection Logic & Re-engagement Strategies

### Guest Dormancy Detection

**Primary Attribute:** `DAYS_SINCE_LAST_PLATFORM_ACTIVITY`

**Detection Rules:**
| Segment Name | Criteria | Est. Size | Action |
|--------------|----------|-----------|--------|
| `GUEST_AT_RISK` | Activity 14-29d ago | Medium | Light touch re-engagement |
| `GUEST_DORMANT` | Activity 30-89d ago | Large | Active win-back campaign |
| `GUEST_CHURNED` | Activity 90-179d ago | Large | Seasonal/event triggers only |
| `GUEST_LOST` | Activity 180+ ago | Very Large | Suppress or re-permission |

**Existing Automation:**
- `Guest_Marketing_YoY_Retention_360dSinceLastbooking` - Long-term win-back
- `Guest_Marketing_PostBooking_Retention` - Post-booking retention
- **Gap:** No 30-day, 60-day, or 90-day inactive guest flows

**Recommended New Flows:**

1. **GUEST_AT_RISK (14-29d):**
   ```
   Trigger: DAYS_SINCE_LAST_PLATFORM_ACTIVITY = 14
   Sequence:
   - Day 14: "We miss you" email with personalized recommendations
   - Day 21: Push notification with special offer
   - Day 28: SMS with urgency ("Pools booking fast for summer")
   ```

2. **GUEST_DORMANT (30-89d):**
   ```
   Trigger: DAYS_SINCE_LAST_PLATFORM_ACTIVITY = 30
   Sequence:
   - Day 30: Re-engagement email with what's new
   - Day 45: Credit offer ($10 to return)
   - Day 60: "We're sorry to see you go" survey
   - Day 75: Final win-back with best offer
   ```

3. **GUEST_SEASONAL_WINBACK:**
   ```
   Trigger: DAYS_SINCE_LAST_PLATFORM_ACTIVITY > 90
           AND (current month = March OR April)
           AND COMPLETED_BOOKINGS_COUNT_AS_GUEST >= 1
   Message: "Summer is coming - book early for best selection"
   ```

### Host Dormancy Detection

**Existing Segments:**
- `V2_Hosts-CurrentlyLive` - Active, listings live
- `V2_Hosts-NOT-Currently-Live` - Paused or no listings

**Existing Automation:**
- `Host_Live_Marketing_InactiveHosts30D` - 30-day re-engagement
- `Host_Wake_Up` - General host wake-up

**Host Dormancy Enhancement:**
| Current State | Gap | Recommendation |
|---------------|-----|----------------|
| 30D inactive flow exists | No 14D early warning | Add pre-dormancy touch |
| Wake-up flow exists | Unclear triggers | Document and optimize |
| No "winback with booking" flow | Lost hosts with demand | Show booking requests |

### Churn Prediction Signals

**High Risk Indicators (Add to Scoring):**
| Signal | Weight | Braze Data Point |
|--------|--------|------------------|
| Declining session frequency | High | Session count trend |
| Cart abandon without rebooking | High | `CartCreated` + no conversion |
| Booking cancelled | Medium | `BookingCancelledToGuest` |
| Booking denied | Medium | `BookingDeclinedToGuest` |
| Negative review | High | Low NPS review |
| App uninstalled | Critical | Uninstall event |
| Email unsubscribe | High | Subscription status |

**Recommended Predictive Segment:**
```
CHURN_RISK_GUESTS:
- Last activity 7-14 days ago
- AND (Cart abandoned in last 30d OR Booking cancelled in last 30d)
- AND Session count declining
```

### Win-Back Campaign Effectiveness

**Current Win-Back Assets:**
| Campaign | Trigger | Channel | Status |
|---------|---------|---------|--------|
| YoY Retention | 360d since booking | Email | Active |
| Post-Booking Retention | Booking complete | Multi | Active |
| Birthday Flow | Birthday | Email | Active |

**Gaps in Win-Back Coverage:**
| Gap | Days Inactive | Recommendation |
|-----|---------------|----------------|
| Early dormancy | 14-30 days | Create new flow |
| Mid dormancy | 30-90 days | Create new flow |
| Seasonal dormancy | Off-season guests | Pre-summer campaign |
| App reinstall | Post-uninstall | Deep link campaign |

### Re-engagement Channel Strategy

| Dormancy Stage | Primary Channel | Secondary | Avoid |
|----------------|-----------------|-----------|-------|
| At-Risk (14-29d) | Email | Push | SMS |
| Dormant (30-89d) | Email + Push | SMS | - |
| Churned (90-179d) | Email | - | Push, SMS |
| Lost (180+d) | Paid retargeting | Email | Push, SMS |

### Implementation Priority

| Action | Impact | Effort | Priority |
|--------|--------|--------|----------|
| Create GUEST_AT_RISK segment | High | Low | **P1** |
| Build 14-day re-engagement flow | High | Medium | **P1** |
| Build 30-day win-back flow | High | Medium | **P1** |
| Add churn prediction scoring | Medium | High | **P2** |
| Optimize existing Host 30D flow | Medium | Low | **P2** |
| Pre-summer dormant reactivation | High | Medium | **P2** (timing: Feb-Mar) |

---

*Report generated by MH1 dormant-detection skill v1.0.0*
*Data source: Braze attributes, canvas audit*
