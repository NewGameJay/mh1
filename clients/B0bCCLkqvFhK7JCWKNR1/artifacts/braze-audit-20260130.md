# Swimply Braze Audit
Generated: 2026-01-30

## Overview

| Metric | Count |
|--------|-------|
| Segments | 95+ |
| Campaigns | 100+ |
| Canvases | 90+ |

**Platform:** Braze (US-05 cluster)
**Status:** Active, mature implementation

---

## Segment Analysis

### Guest Segments
| Segment | Purpose |
|---------|---------|
| `Guest-HasAccount0bookings` | Signed up, no bookings |
| `Guest-HasBookings` | Has made bookings |
| `MASTER-GUEST` | All guests |
| `GUESTS` | Alternative all-guests segment |

### Host Segments
| Segment | Purpose |
|---------|---------|
| `V2_Hosts-CurrentlyLive` | Active listings |
| `V2_Hosts-NOT-Currently-Live` | Inactive/paused |
| `WaitlistedHost` | Pending approval |
| `Host` | All hosts |
| `LiveHost2022` | Historical active hosts |

### Market Segments (Geographic)
**US Markets:**
- LA, Miami, NYC, Austin, Houston, Seattle, Boston, Portland, Phoenix

**Australia:**
- Sydney, Victoria, Brisbane, Perth

### Behavioral Segments
- `SMS Subscribed` - SMS opt-ins
- `PushOptIns(iOS)` / `PushOptIns(Android)` - Push subscribers
- `BookingToday` - Same-day bookings
- `Unsubscribed` - Email opt-outs
- `Bounces/Spam-exclusion` - Suppression list

---

## Campaign Categories

### Recent Activity (Jan 2026)
- Host webinars (SwimU, Bunim)
- 2025 Recap / Year-end
- Swimply Choice Awards

### Seasonal Campaigns
- **Summer:** Labor Day, Memorial Day, 4th of July
- **Winter:** Igloos announcement, Blue Friday
- **Holidays:** Valentine's Day, National Pool Day, Father's Day
- **Weather-triggered:** LA Weather, NY Weather

### Product Campaigns
- **Igloos** - Winter product push (heated enclosures)
- **Premium Passes** - Subscription upsell
- **Courts** - Tennis/pickleball expansion
- **Homes** - Full home rentals

### Transactional Campaigns
- Booking confirmations
- Review requests (24hr after experience)
- Booking reminders
- Day-of booking prep

### Host Campaigns
- Webinar invitations
- Meetup announcements (city-specific)
- Wake-up / re-engagement
- Season prep

---

## Canvas (Automation) Analysis

### Guest Lifecycle Canvases

| Canvas | Trigger | Status |
|--------|---------|--------|
| `Onboarding-AccountCreated-NoBooking-HasControlGroup` | Account created | Active |
| `V1_MinusMI-Guest-CartAbandon-US` | Checkout abandoned | Active |
| `Guest_Marketing_PostBooking_Retention_SP` | Booking completed | Active |
| `Guest_Marketing_YoY_Retention_360dSinceLastbooking_SP` | 360d since last booking | Active |
| `Guest_Marketing_BirthdayFlow` | Birthday | Active |
| `GuestLeavesReviewToGuest_Marketing_Post5Star_ExternalReviewRequest_SP` | 5-star review | Active |

### Host Lifecycle Canvases

| Canvas | Trigger | Status |
|--------|---------|--------|
| `02.14.2024_US_AU_Host_All_Marketing_General_HostOnboardingWaitlist_SP` | Host application | Active |
| `02.27.2024_US_AU_Host_All_Marketing_StuckOnStep_Photos_HostOnboardingWaitlist_SP` | Stuck on photos step | Active |
| `02.26.2024_US_AU_Host_All_Marketing_StuckOnStep_Price_HostOnboardingWaitlist_SP` | Stuck on pricing step | Active |
| `02.16.2024_US_AU_Host_All_Marketing_StuckOnStep_GuestCount_HostOnboardingWaitlist_SP` | Stuck on guest count | Active |
| `02.14.2024_US_AU_Host_All_Marketing_StuckOnStep_SpaceDetails_HostOnboardingWaitlist_SP` | Stuck on space details | Active |
| `02.27.2024_US_AU_Host_All_Transactional_ListingGoesLive_SP` | Listing published | Active |
| `Transactional_Host_1stBookingCompleted_SP` | First booking received | Active |
| `03.21.2024_US_AU_Host_Live_Marketing_InactiveHosts30D_SP` | 30 days inactive | Active |
| `Host_Wake_Up` | Dormant host | Active |

### Transactional Canvases

| Canvas | Trigger |
|--------|---------|
| `Transactional_Expired_Booking_Push_SMS` | Booking request expires |
| `Booking_Request_Expires_3_Hours` | 3hr before expiration |
| `Booking_Request_Expires_6_Hours` | 6hr before expiration |
| `Booking_Request_Expires_12_Hours` | 12hr before expiration |
| `Booking_Inquiry_Guest_Homes` | Home booking inquiry |
| `Booking_Inquiry_Host` | New booking request to host |
| `c5f95033-..._Guest_Transactional_BookingFailure` | Booking failure |

### Premium/Upsell Canvases

| Canvas | Trigger |
|--------|---------|
| `Welcome_To_Swimply_Premium` | Premium subscription |
| `Premium_Pass_Launch` | Premium launch campaign |
| `Premium_Pass_Cancellation` | Subscription cancelled |
| `Premium_Pass_Cancellation_24_Hour_Reminder` | Pre-cancellation |
| `Guest_Marketing_PassesUpsell_AfterBookingComplete_SP` | Post-booking upsell |

### Geographic Variants
- Cart abandon: US, AU, Courts-US, Courts-AU, Homes-US
- Host onboarding: US + AU combined

---

## Key Findings

### Strengths
1. **Mature lifecycle automation** - Full guest & host journeys mapped
2. **Multi-channel** - Email, push, SMS, in-app all active
3. **Granular segmentation** - Market-level targeting
4. **Host onboarding excellence** - "Stuck on step" recovery flows are sophisticated
5. **Seasonal playbook** - Well-developed holiday/weather campaigns
6. **Control groups** - A/B testing infrastructure in place

### Gaps Identified
1. **Naming inconsistency** - Mix of date-prefixed and descriptive names
2. **Tag usage** - Sparse tagging makes filtering difficult
3. **No visible win-back for guests** - 360d retention canvas exists but no clear win-back
4. **Australia vs US** - Some flows combined, some separate (inconsistent)
5. **Old canvases** - Some date back to 2023/2024, may need refresh

### Opportunities
1. **Referral automation** - No visible referral program flows
2. **NPS-triggered flows** - Only high NPS → review request, no low NPS recovery
3. **Cross-sell** - Limited pools → courts / courts → pools automation
4. **Superhost recognition** - No visible superhost achievement flow
5. **Review recovery** - No flow for guests who don't leave reviews

---

## Recommended Actions

### Immediate
1. Audit existing canvas performance metrics
2. Standardize naming convention
3. Add tags to all canvases/campaigns

### Short-term
1. Build referral automation flow
2. Add low NPS recovery flow
3. Create cross-sell automation (pools ↔ courts)

### Long-term
1. Superhost recognition & gamification
2. Predictive churn modeling integration
3. Weather API integration for real-time triggers

---

## API Access

```
Endpoint: https://rest.iad-05.braze.com
API Key: [configured in credentials/.env]
```

Available endpoints tested:
- `/segments/list` ✅
- `/campaigns/list` ✅
- `/canvas/list` ✅
