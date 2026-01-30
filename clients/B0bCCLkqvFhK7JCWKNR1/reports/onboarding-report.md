# Client Onboarding Report
## Swimply
Generated: 2026-01-30

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Status** | **COMPLETE** |
| Primary Platform | Braze (US-05) |
| Custom Attributes | 50+ |
| Custom Events | 250 |
| Segments | 95+ |
| Campaigns | 100+ |
| Canvases | 90+ |

**Swimply uses Braze as their unified customer data platform** - serving as CRM, CDP, and marketing automation in one. No separate data warehouse or CRM.

---

## Company Overview

| Attribute | Value |
|-----------|-------|
| Company | Swimply |
| Industry | Two-sided marketplace |
| Business Model | Commission (10% guest + 15% host) |
| Founded | 2017 |
| HQ | Santa Monica, CA |
| Size | 11-50 employees |
| Total Funding | $63.2M |
| Scale | 15,000+ hosts, 150+ cities, 4M+ experiences |

---

## Platform Configuration

### Braze (Primary Platform)
- **Cluster:** US-05
- **Endpoint:** `https://rest.iad-05.braze.com`
- **Status:** Connected and audited

**Capabilities:**
- Customer profiles with 50+ custom attributes
- 250 custom events tracking full user journey
- 95+ segments (guest, host, geographic, behavioral)
- 100+ campaigns (seasonal, transactional, marketing)
- 90+ canvases (lifecycle automation)
- Multi-channel: Email, Push, SMS, In-App

### Data Model Summary

**Guest Attributes:**
- `BOOKING_COUNT_AS_GUEST` - Total bookings
- `COMPLETED_BOOKINGS_COUNT_AS_GUEST` - Completed bookings
- `DAYS_SINCE_LAST_PLATFORM_ACTIVITY` - Activity recency
- `CURRENT_CREDIT_BALANCE` - Account credits

**Host Attributes:**
- `COMPLETED_BOOKINGS_COUNT_AS_HOST` - Bookings received
- `CANCELLED_BOOKINGS_COUNT_AS_HOST` - Cancellation rate

**Key Events:**
- `BookingConfirmedToGuest/Host` - Booking success
- `BookingCompletedToGuest/Host` - Experience completed
- `GuestLeavesReview` - Review submitted
- `CartCreated` - Checkout started

---

## Lifecycle Automation (Canvases)

### Guest Journey
| Stage | Canvas | Status |
|-------|--------|--------|
| Onboarding | `Onboarding-AccountCreated-NoBooking` | Active |
| Cart Recovery | `V1_MinusMI-Guest-CartAbandon-US` | Active |
| Post-Booking | `Guest_Marketing_PostBooking_Retention_SP` | Active |
| Win-Back | `Guest_Marketing_YoY_Retention_360dSinceLastbooking` | Active |
| Birthday | `Guest_Marketing_BirthdayFlow` | Active |
| Review Request | `GuestLeavesReviewToGuest_Post5Star_ExternalReviewRequest` | Active |

### Host Journey
| Stage | Canvas | Status |
|-------|--------|--------|
| Onboarding | `Host_All_Marketing_General_HostOnboardingWaitlist` | Active |
| Stuck: Photos | `Host_All_Marketing_StuckOnStep_Photos` | Active |
| Stuck: Pricing | `Host_All_Marketing_StuckOnStep_Price` | Active |
| Stuck: Details | `Host_All_Marketing_StuckOnStep_SpaceDetails` | Active |
| Listing Live | `Host_All_Transactional_ListingGoesLive` | Active |
| First Booking | `Transactional_Host_1stBookingCompleted` | Active |
| Inactive 30D | `Host_Live_Marketing_InactiveHosts30D` | Active |
| Wake-Up | `Host_Wake_Up` | Active |

---

## Segments Overview

### Guest Segments
- `Guest-HasAccount0bookings` - Signed up, no bookings
- `Guest-HasBookings` - Has booked
- `MASTER-GUEST` - All guests

### Host Segments
- `V2_Hosts-CurrentlyLive` - Active listings
- `V2_Hosts-NOT-Currently-Live` - Paused/inactive
- `WaitlistedHost` - Pending approval

### Geographic Segments
**US:** LA, Miami, NYC, Austin, Houston, Seattle, Boston, Portland, Phoenix
**Australia:** Sydney, Victoria, Brisbane, Perth

---

## Gaps & Opportunities

### Identified Gaps
1. **No referral automation** - `GuestReferralInviteCreated` event exists but no flow
2. **No low NPS recovery** - Only high NPS → review request
3. **Limited cross-sell** - No pools → courts automation
4. **No superhost recognition flow** - `HostAwardEarned` event exists
5. **Naming inconsistency** - Mix of date-prefixed and descriptive names

### Recommended New Flows
1. **Referral Program Canvas** - Trigger on referral, reward on conversion
2. **NPS Recovery Flow** - Low rating → support outreach
3. **Cross-Sell (Pools ↔ Courts)** - After booking, suggest other listing types
4. **Superhost Celebration** - Recognition when achieving status
5. **Seasonal Re-engagement** - Pre-season wake-up for lapsed guests

---

## Configuration Files

```
clients/B0bCCLkqvFhK7JCWKNR1/
├── config/
│   ├── datasources.yaml              # Main configuration
│   ├── integrations/
│   │   └── marketing.yaml            # Braze + other platforms
│   └── semantic_layer/
│       ├── lifecycle_stages.yaml     # Guest & host funnels
│       └── event_dictionary.yaml     # Event mappings
├── credentials/
│   └── .env                          # Braze API credentials
├── artifacts/
│   └── braze-audit-20260130.md       # Full Braze audit
└── reports/
    └── onboarding-report.md          # This report
```

---

## Quick Start Commands

```bash
# Set client context
export MH1_CLIENT=B0bCCLkqvFhK7JCWKNR1

# Query Braze segments
curl -s "https://rest.iad-05.braze.com/segments/list" \
  -H "Authorization: Bearer $BRAZE_API_KEY"

# Query Braze campaigns
curl -s "https://rest.iad-05.braze.com/campaigns/list" \
  -H "Authorization: Bearer $BRAZE_API_KEY"

# Run lifecycle audit (uses Braze data)
mh1 lifecycle-audit --client B0bCCLkqvFhK7JCWKNR1 --source braze
```

---

## Next Steps

### Immediate Actions
- [x] Connect to Braze API
- [x] Audit segments, campaigns, canvases
- [x] Document data model (attributes + events)
- [x] Create configuration files
- [x] Map lifecycle stages

### Recommended Projects
1. **Referral Program Automation** - Build Braze canvas for referral flow
2. **Seasonal Campaign Planning** - Prep for summer 2026 peak season
3. **Host Onboarding Optimization** - A/B test "stuck on step" flows
4. **Cross-Sell Implementation** - Pools ↔ Courts automation
5. **Analytics Dashboard** - Export Braze Currents to warehouse for deeper analysis

---

## Onboarding Output

```json
{
  "onboarding_complete": true,
  "client_id": "B0bCCLkqvFhK7JCWKNR1",
  "client_name": "Swimply",
  "primary_platform": "braze",
  "platform_status": "connected",
  "data_model": {
    "custom_attributes": 50,
    "custom_events": 250,
    "segments": 95,
    "campaigns": 100,
    "canvases": 90
  },
  "config_files_created": [
    "config/datasources.yaml",
    "config/integrations/marketing.yaml",
    "config/semantic_layer/lifecycle_stages.yaml",
    "config/semantic_layer/event_dictionary.yaml",
    "credentials/.env",
    "artifacts/braze-audit-20260130.md"
  ],
  "gaps_identified": 5,
  "recommended_projects": 5,
  "report_path": "clients/B0bCCLkqvFhK7JCWKNR1/reports/onboarding-report.md"
}
```

---

*Report generated by MH1 client-onboarding skill v1.1.0*
*Onboarding completed: 2026-01-30*
