# Lead Magnet Effectiveness Analysis
## Module: swimply-lifecycle-audit-20260130 | Skill #5

**Generated:** 2026-01-30
**Client:** B0bCCLkqvFhK7JCWKNR1
**Data Sources:** Braze Attributes, Campaign Analysis, Industry Benchmarks

---

## Page 1: Executive Summary & Key Findings

### Executive Summary

This analysis evaluates Swimply's lead magnet and acquisition incentive strategies for converting visitors into registered users and first-time bookers. Primary lead magnets include account credits, referral bonuses, and seasonal promotions. The analysis reveals that credits are effectively tracked (`CURRENT_CREDIT_BALANCE` attribute) but referral completion tracking has gaps.

### Key Findings

1. **Credit System Active:** `CURRENT_CREDIT_BALANCE` attribute tracks user credits, used as conversion lever
2. **Referral Program Exists but Undertracked:** `DisplayedReferral` event exists, but no `ReferralCompleted` visible
3. **Special Offers Active:** `GuestReceivedSpecialOffer` and `GuestDeclinedSpecialOffer` events track offer responses
4. **Seasonal Promotions:** Blue Friday, holiday campaigns used as acquisition drivers
5. **No Welcome Offer Canvas:** Onboarding flow doesn't show clear welcome credit/discount incentive

### Current Lead Magnet Inventory

| Lead Magnet | Mechanism | Tracking | Effectiveness |
|-------------|-----------|----------|---------------|
| Account Credits | Sign-up bonus | `CURRENT_CREDIT_BALANCE` | Tracked |
| Referral Credits | Give $X, Get $X | `DisplayedReferral` | Partial |
| Special Offers | Host-initiated discounts | `GuestReceivedSpecialOffer` | Tracked |
| Seasonal Promos | Holiday campaigns | Campaign-level | Tracked |
| First Booking Discount | New user incentive | Unknown | Gap |

### Credit Balance Distribution Insight

```
Credit Usage Indicators:
- CURRENT_CREDIT_BALANCE tracked as custom attribute
- Historical snapshots (CURRENT_CREDIT_BALANCE_*) suggest tracking over time
- Credits as re-engagement lever for dormant users

Recommended Segments:
- Users with credits > $0 who haven't booked in 30d
- New users who haven't used welcome credit
- Users whose credits will expire
```

---

## Page 2: Detailed Analysis & Recommendations

### Lead Magnet #1: Account Credits

**Current Implementation:**
- Credits tracked via `CURRENT_CREDIT_BALANCE` attribute
- Used across booking flow as payment method
- Historical tracking suggests active monitoring

**Effectiveness Indicators:**
| Metric | Status | Notes |
|--------|--------|-------|
| Credit tracking | ✅ Active | Attribute exists |
| Credit expiration | ❓ Unknown | No visible expiration trigger |
| Credit reminder flows | ❓ Unknown | Not visible in canvas audit |
| Credit-to-booking correlation | ❓ Unknown | Requires analysis |

**Recommendations:**
1. Create "Use Your Credits" reminder campaign
2. Implement credit expiration warning flow
3. Segment users by credit balance for targeted offers
4. Track credit redemption rate as KPI

### Lead Magnet #2: Referral Program

**Current Implementation:**
- `DisplayedReferral` event tracks referral UI views
- `DisplayedReferralDetailsHost` for host referrals
- `DisplayedSharingInvitesOptions` for share actions

**Gap Identified:**
- No `ReferralCompleted` or `ReferralCredited` event visible
- No referral automation canvas in audit
- Cannot measure referral program ROI

**Effectiveness Indicators:**
| Metric | Status | Notes |
|--------|--------|-------|
| Referral display tracking | ✅ Active | Event exists |
| Referral completion tracking | ❌ Missing | Critical gap |
| Referral automation | ❌ Missing | No canvas found |
| Referral reminder flow | ❌ Missing | Opportunity |

**Recommendations:**
1. Implement `ReferralCompleted` event tracking
2. Build referral automation canvas:
   - Trigger: First booking complete
   - Reminder: 7d, 14d, 30d post-booking
   - Incentive escalation for non-converters
3. Create referral leaderboard/gamification
4. Test referral incentive amounts ($10 vs $25 vs $50)

### Lead Magnet #3: Special Offers

**Current Implementation:**
- `GuestReceivedSpecialOffer` tracks offer delivery
- `GuestDeclinedSpecialOffer` tracks rejection
- Host-initiated pricing/discount system

**Effectiveness Indicators:**
| Metric | Status | Notes |
|--------|--------|-------|
| Offer delivery tracking | ✅ Active | Event exists |
| Offer acceptance tracking | ❓ Implied | Via booking events |
| Offer decline tracking | ✅ Active | Event exists |
| Offer A/B testing | ❓ Unknown | Not visible |

**Recommendations:**
1. Create `GuestAcceptedSpecialOffer` event for clarity
2. Build special offer reminder sequence
3. A/B test offer timing (immediate vs. 24hr delay)
4. Analyze decline reasons via survey

### Lead Magnet #4: Seasonal/Holiday Promotions

**Current Campaigns Identified:**
- Blue Friday (November)
- Labor Day / Memorial Day
- Valentine's Day
- National Pool Day
- Summer kickoff campaigns

**Effectiveness Indicators:**
| Metric | Status | Notes |
|--------|--------|-------|
| Campaign tracking | ✅ Active | Campaign-level metrics |
| Seasonal attribution | ❓ Unknown | UTM tracking unclear |
| Repeat seasonal engagement | ❓ Unknown | YoY comparison needed |

**Recommendations:**
1. Create seasonal anticipation sequences (pre-summer)
2. Build "Summer countdown" campaign for Q1
3. Track seasonal campaign attribution end-to-end
4. Develop weather-triggered lead magnets

### Lead Magnet Effectiveness Score

| Lead Magnet | Visibility | Tracking | Automation | Score |
|-------------|------------|----------|------------|-------|
| Account Credits | High | Good | Partial | 7/10 |
| Referral Program | Medium | Poor | None | 3/10 |
| Special Offers | Medium | Good | Partial | 6/10 |
| Seasonal Promos | High | Good | Good | 8/10 |
| Welcome Offer | Low | Unknown | Unknown | 4/10 |

### Priority Recommendations

| Action | Impact | Effort | Priority |
|--------|--------|--------|----------|
| Build referral automation canvas | High | Medium | **P1** |
| Add referral completion tracking | High | Low | **P1** |
| Create credit reminder flow | Medium | Low | **P2** |
| Optimize welcome offer sequence | Medium | Medium | **P2** |
| Seasonal pre-engagement campaign | Medium | Medium | **P3** |

### Lead Magnet Strategy Gaps

1. **No Clear Welcome Offer:** New user incentive not visible in onboarding flow
2. **Referral Underutilized:** Program exists but lacks automation and tracking
3. **Credit Expiration:** No visible urgency/expiration messaging
4. **Content Lead Magnets:** No guides, checklists, or content offers visible
5. **Social Proof:** No "X people booked this pool" or review highlights in acquisition

---

*Report generated by MH1 lead-magnet skill v1.0.0*
*Data source: Braze events, campaign audit*
