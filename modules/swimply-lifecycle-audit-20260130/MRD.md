# MRD: Swimply Full Lifecycle Audit - Click to Pool Guest

## Metadata
| Field | Value |
|-------|-------|
| Module ID | swimply-lifecycle-audit-20260130 |
| Client | B0bCCLkqvFhK7JCWKNR1 (Swimply) |
| Status | In Progress |
| Template | lifecycle-audit |
| Priority | P1 |
| Owner | MH1 Engineering |
| Created | 2026-01-30 |
| Updated | 2026-01-30 |

---

## Executive Summary

Comprehensive lifecycle audit for Swimply, the leading pool and outdoor space rental marketplace. This module analyzes the complete guest journey from initial click to pool experience completion, identifying conversion bottlenecks, at-risk segments, and growth opportunities.

**Business Context:**
- Two-sided marketplace (Guests + Hosts)
- $63.2M funding, 15,000+ hosts, 150+ cities
- Primary data platform: Braze (no separate CRM/warehouse)
- Peak seasonality: May-August (70% of bookings)

**Key Deliverables:**
1. 15+ skill execution reports (2 pages each)
2. Full guest lifecycle funnel analysis
3. Gap identification with prioritized solutions
4. GTM engineering recommendations for 2026

---

## Problem Statement

### What Changed?
- Swimply has mature Braze automation but lacks unified lifecycle visibility
- No comprehensive funnel analysis from click → booking → repeat guest
- Seasonal business requires proactive demand/supply management
- Winter product expansion (Igloos, hot tubs) needs optimization

### Why This Matters
- **Guest conversion optimization** could increase bookings 15-25%
- **Host supply retention** directly impacts marketplace liquidity
- **Seasonal planning** for Summer 2026 requires actionable insights now
- **Competitive pressure** from ResortPass, Peerspace entering adjacent markets

---

## Objectives

### Primary Goal
Deliver a comprehensive lifecycle audit with actionable recommendations to improve guest conversion, reduce churn, and optimize host supply for Summer 2026.

### Success Criteria
1. ✅ Complete guest funnel mapped (click → booking → repeat)
2. ✅ Host supply funnel mapped (apply → list → active → superhost)
3. ✅ At-risk segments identified with intervention strategies
4. ✅ 5+ high-impact recommendations with implementation plans
5. ✅ GTM strategy for Summer 2026 peak season

---

## Scope

### In Scope

**Phase 1: Discovery & Analysis**
- Company research & competitive intelligence
- Account 360 analysis
- Conversion funnel mapping (guest + host)
- Lead magnet effectiveness
- Lead qualification scoring
- Dormant user detection
- Engagement velocity analysis
- ICP historical analysis
- Pipeline analysis
- Renewal/repeat booking tracking
- Reactivation detection
- Full lifecycle audit

**Phase 2: Strategy & Action**
- Lifecycle mapping optimization
- Conversion funnel improvement recommendations
- Drop-off solution design
- Product positioning matrix
- Needs assessment
- GTM engineering plan

### Out of Scope
- Implementation of recommendations (separate module)
- Braze canvas/campaign creation (separate module)
- Host acquisition campaigns (future module)
- International expansion planning

---

## Data Sources

| Source | Type | Status | Data Available |
|--------|------|--------|----------------|
| Braze | CDP/Marketing | ✅ Connected | 50 attributes, 250 events, 95 segments |
| Braze KPIs | Analytics | ✅ Available | DAU (~6,500), sessions (~24,000/day) |
| Firebase | Context Store | ✅ Connected | Brand, audience, competitive, strategy docs |
| Web Research | External | ✅ Available | Company info, competitors, market data |

**Key Braze Attributes:**
- `BOOKING_COUNT_AS_GUEST` / `COMPLETED_BOOKINGS_COUNT_AS_GUEST`
- `DAYS_SINCE_LAST_PLATFORM_ACTIVITY`
- `CURRENT_CREDIT_BALANCE`
- `COMPLETED_BOOKINGS_COUNT_AS_HOST` / `TOTAL_LIVE_LISTINGS_AS_HOST`

**Key Braze Events:**
- `CartCreated`, `BookingConfirmedToGuest`, `BookingCompletedToGuest`
- `GuestLeavesReview`, `GuestCancelsBooking`
- `FirstActiveListing`, `HostAwardEarned`

---

## Approach & Methodology

### Phase 1: Discovery & Analysis (Skills 1-13)

| # | Skill | Purpose | Output |
|---|-------|---------|--------|
| 1 | research-company | Deep dive on Swimply business model | 2-page report |
| 2 | research-competitors | Competitive landscape analysis | 2-page report |
| 3 | account-360 | Unified view of guest/host profiles | 2-page report |
| 4 | conversion-funnel | Guest journey funnel analysis | 2-page report |
| 5 | lead-magnet | Effectiveness of signup incentives | 2-page report |
| 6 | qualify-leads | Lead scoring model for guests | 2-page report |
| 7 | dormant-detection | Identify inactive guests/hosts | 2-page report |
| 8 | engagement-velocity | Activity trends and momentum | 2-page report |
| 9 | icp-historical-analysis | Ideal guest/host profile analysis | 2-page report |
| 10 | pipeline-analysis | Booking pipeline health | 2-page report |
| 11 | renewal-tracker | Repeat booking analysis | 2-page report |
| 12 | reactivation-detection | Win-back opportunity identification | 2-page report |
| 13 | lifecycle-audit | Comprehensive stage distribution | 2-page report |

### Phase 2: Strategy & Action (Skills 14-19)

| # | Skill | Purpose | Output |
|---|-------|---------|--------|
| 14 | lifecycle-mapping | Optimize stage definitions & transitions | 2-page report |
| 15 | funnel-improvement | Conversion rate optimization plan | 2-page report |
| 16 | drop-off-solutions | Interventions for each drop-off point | 2-page report |
| 17 | product-positioning-matrix | Position Swimply vs competitors | 2-page report |
| 18 | needs-assessment | Platform capability gap analysis | 2-page report |
| 19 | gtm-engineering | Go-to-market plan for Summer 2026 | 2-page report |

### Phase 3: Synthesis & Delivery

1. Compile all reports into unified deliverable
2. Generate executive summary
3. Create prioritized action plan
4. Review and finalize

---

## Dependencies & Blockers

### Critical Dependencies
- [x] Braze API access configured
- [x] Firebase context documents available
- [x] Client onboarding complete
- [ ] Budget approved for skill execution

### Optional Dependencies
- [ ] Historical booking data (would improve analysis depth)
- [ ] Customer interview transcripts (would validate ICP)

### Known Blockers
- **No direct revenue data in Braze** - Using booking counts as proxy
- **Segment sizes not exposed via API** - Estimating from DAU patterns

---

## Success Metrics

### Quantitative
- 19 skills executed with 2-page reports each
- Guest funnel conversion rates calculated
- Host supply funnel conversion rates calculated
- At-risk segment size quantified
- Reactivation opportunity size quantified

### Qualitative
- Recommendations are actionable and specific to Swimply
- Reports are clear and digestible
- Findings align with marketplace business model
- GTM plan is executable for Summer 2026

---

## Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Limited historical data | Medium | Medium | Use Braze segment definitions as proxy |
| Seasonal bias in current data (winter) | Medium | High | Note seasonality in all analyses |
| Two-sided marketplace complexity | Medium | Medium | Analyze guest and host separately |
| No revenue/GMV data | Low | High | Use booking counts and retention as proxy |

---

## Timeline & Milestones

| Milestone | Target | Status |
|-----------|--------|--------|
| Module Created | 2026-01-30 | ✅ Complete |
| Phase 1: Discovery Complete | 2026-01-30 | 🔄 In Progress |
| Phase 2: Strategy Complete | 2026-01-30 | ⏳ Pending |
| Phase 3: Synthesis Complete | 2026-01-30 | ⏳ Pending |
| Final Delivery | 2026-01-30 | ⏳ Pending |

---

## Stakeholders

| Role | Person | Responsibility |
|------|--------|----------------|
| Engineering Lead | MH1 Team | Module execution |
| Client Contact | Swimply Marketing | Review & approval |
| CS Owner | TBD | Action on recommendations |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-30 | MH1 | Initial MRD |
