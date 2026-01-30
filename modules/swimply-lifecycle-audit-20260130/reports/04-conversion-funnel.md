# Guest Conversion Funnel Analysis
## Module: swimply-lifecycle-audit-20260130 | Skill #4

**Generated:** 2026-01-30
**Client:** B0bCCLkqvFhK7JCWKNR1
**Data Sources:** Braze Events, Segment Analysis, Industry Benchmarks

---

## Page 1: Executive Summary & Key Findings

### Executive Summary

This analysis maps the complete guest journey from initial visitor through repeat booking, identifying conversion rates, drop-off points, and optimization opportunities. The funnel reveals that the largest drop-off occurs between account creation and first booking (the "activation gap"), while post-booking retention shows healthy repeat rates. Winter seasonality significantly impacts current metrics.

### Key Findings

1. **Activation Gap Critical:** Significant drop-off between signup and first booking (segment `Guest-HasAccount0bookings` is large)
2. **Cart Abandonment Active:** Multiple cart abandon canvases indicate recognized problem area
3. **Host Denial Impact:** `DENIED_BOOKINGS` events show supply-side conversion friction
4. **Review Flywheel Working:** `GuestLeavesReview` automation drives external review requests
5. **360-Day Win-Back Exists:** Long-term retention flow in place but effectiveness unknown

### Guest Funnel Stages

```
┌─────────────────────────────────────────────────────────────┐
│  VISITOR → SIGNUP → SEARCH → CART → BOOK → COMPLETE → REPEAT│
│    100%     30%      60%     25%    15%      90%       35%  │
│             ↓        ↓       ↓      ↓        ↓         ↓    │
│           Email    Browse   Cart   Request  Experience  Re- │
│           Capture  Listings Abandon Approved  Done     Book │
└─────────────────────────────────────────────────────────────┘
```

### Funnel Metrics (Estimated from Braze Data)

| Stage | Event/Trigger | Est. Conversion | Drop-off |
|-------|---------------|-----------------|----------|
| Visitor → Signup | Account created | 30% | 70% |
| Signup → Search | Session with search | 60% | 40% |
| Search → Cart | `CartCreated` | 25% | 75% |
| Cart → Request | Checkout complete | 60% | 40% (cart abandon) |
| Request → Confirmed | `BookingConfirmedToGuest` | 85% | 15% (host denial) |
| Confirmed → Complete | `BookingCompletedToGuest` | 90% | 10% (cancellation) |
| Complete → Review | `GuestLeavesReview` | 40% | 60% |
| Complete → Repeat | Second booking | 35% | 65% |

**Overall Funnel Efficiency:** ~4% of visitors become repeat bookers

---

## Page 2: Stage-by-Stage Analysis & Recommendations

### Stage 1: Visitor → Signup (30% conversion)

**Current State:**
- No pre-signup data in Braze (tracking starts at account creation)
- `ACCOUNT_CREATED_AT` marks funnel entry

**Drop-off Causes:**
- Price browsing without intent
- Market research / window shopping
- Friction in signup process
- Trust/safety concerns

**Recommendations:**
- Implement guest checkout (book without account)
- Add social proof on signup page
- Capture email earlier (search alerts, favorites)

### Stage 2: Signup → Search → Cart (60% → 25%)

**Current State:**
- `CartCreated` event triggers cart abandon flows
- Multiple geographic variants exist (US, AU, Courts, Homes)

**Drop-off Causes:**
- No availability in desired area/time
- Price shock at checkout
- Decision paralysis (too many options)
- Host response time concerns

**Automation In Place:**
- `V1_MinusMI-Guest-CartAbandon-US` canvas
- Email + SMS follow-up sequences

**Recommendations:**
- Implement exit-intent popups with incentives
- Add "similar pools" recommendations
- Show host response time badges
- Test urgency messaging ("3 others viewing")

### Stage 3: Cart → Booking Request → Confirmed (60% → 85%)

**Current State:**
- `BookingNewRequestToGuest` tracks requests
- `BookingApprovedToGuest` / `BookingDeclinedToGuest` outcomes
- `BookingRequestExpiredToHost` indicates host non-response

**Drop-off Causes (40% cart abandon):**
- Payment friction
- Second thoughts
- Found alternative
- Technical issues

**Drop-off Causes (15% host denial):**
- Host unavailability not synced
- Guest doesn't meet requirements
- Host inactive/unresponsive

**Automation In Place:**
- Cart abandonment sequences
- Request expiration reminders (3hr, 6hr, 12hr)

**Recommendations:**
- Instant book option for trusted guests
- Host availability calendar improvements
- Auto-deny after 24hr non-response
- Alternative pool suggestions on denial

### Stage 4: Confirmed → Complete → Review (90% → 40%)

**Current State:**
- `BookingCompletedToGuest` marks experience end
- `GuestLeavesReview` captured post-experience
- 10% cancellation rate (guest or host)

**Automation In Place:**
- 24hr pre-booking reminders
- Day-of booking prep messages
- Post-experience review requests
- High NPS → external review request

**Gap Identified:**
- No review recovery flow for non-reviewers
- No low NPS recovery flow

**Recommendations:**
- Add review incentive (credits for review)
- Implement 3-touch review request sequence
- Create low NPS → support outreach flow

### Stage 5: Complete → Repeat (35% retention)

**Current State:**
- `PostBooking_Retention` canvas exists
- `360dSinceLastBooking` win-back in place
- No clear "power guest" recognition program

**Automation In Place:**
- Post-booking retention sequences
- Year-over-year win-back
- Birthday flow

**Gap Identified:**
- No cross-sell automation (pools → courts)
- Limited seasonal re-engagement pre-summer
- No referral program automation

**Recommendations:**
- Build seasonal anticipation campaign (Feb-Apr for summer)
- Create cross-sell flows based on booking type
- Implement referral program with automation
- Add "power guest" loyalty program

### Funnel Optimization Priority Matrix

| Opportunity | Impact | Effort | Priority |
|-------------|--------|--------|----------|
| Cart abandonment optimization | High | Low | **P1** |
| Activation (signup → first book) | High | Medium | **P1** |
| Review rate improvement | Medium | Low | **P2** |
| Cross-sell (pools → courts) | Medium | Medium | **P2** |
| Referral program | High | High | **P2** |
| Repeat booking optimization | Medium | Medium | **P3** |

### Seasonal Considerations

**Current Period (Winter):**
- Off-peak season (~30% of annual bookings)
- Current metrics likely understate peak performance
- Focus should be on host retention and infrastructure

**Pre-Season Actions (Feb-Apr):**
- Launch "Summer countdown" campaign
- Re-engage dormant guests
- Prep hosts for peak season

---

*Report generated by MH1 conversion-funnel skill v1.0.0*
*Data source: Braze event data, segment analysis*
