# Swimply Braze Data Discovery
## CRM & Data Warehouse Discovery Report
Generated: 2026-01-30

Since Swimply uses **Braze as their unified customer data platform**, this report serves as both CRM discovery and data warehouse discovery.

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Total Custom Attributes** | 50 |
| **Total Custom Events** | 250 |
| **Daily Active Users (avg)** | ~6,500 |
| **Daily Sessions (avg)** | ~24,000 |
| **Sessions per DAU** | ~3.7 |
| **App Uninstalls (30d)** | 5,638 |

---

## Platform Activity (Last 30 Days)

### Daily Active Users Trend
```
Jan 03-04: Peak at 8,000-8,700 DAU (weekend)
Jan 12-14: Low at 5,600-6,100 DAU (mid-week)
Jan 29:    6,833 DAU (current)
```

**Insight:** Weekend peaks suggest consumer leisure usage pattern. ~40% variance between peak and trough.

### Sessions Trend
```
Peak: 28,634 sessions (Jan 6)
Low:  19,420 sessions (Dec 31)
Avg:  ~24,000 sessions/day
```

**Sessions per user:** 3.5-4.0 (indicates engaged users browse multiple listings)

---

## Custom Attributes (Data Dictionary)

### Booking Metrics (22 attributes)

| Attribute | Type | Description |
|-----------|------|-------------|
| `BOOKING_COUNT_AS_GUEST` | Number | Lifetime bookings as guest |
| `COMPLETED_BOOKINGS_COUNT_AS_GUEST` | Number | Completed bookings as guest |
| `COMPLETED_BOOKINGS_YTD_AS_GUEST` | Number | Year-to-date completions |
| `CONFIRMED_BOOKINGS_COUNT_AS_GUEST` | Number | Confirmed (upcoming) bookings |
| `CANCELLED_BOOKINGS_COUNT_AS_GUEST` | Number | Cancellations as guest |
| `DENIED_BOOKINGS_COUNT_AS_GUEST` | Number | Host-declined requests |
| `COMPLETED_BOOKINGS_COUNT_AS_HOST` | Number | Completed bookings as host |
| `COMPLETED_BOOKINGS_YTD_AS_HOST` | Number | YTD completions as host |
| `CONFIRMED_BOOKINGS_COUNT_AS_HOST` | Number | Upcoming bookings as host |
| `CANCELLED_BOOKINGS_COUNT_AS_HOST` | Number | Cancellations as host |
| `DENIED_BOOKINGS_COUNT_AS_HOST` | Number | Declined requests as host |
| `ALL_COMPLETED_BOOKING_DATES_AS_GUEST` | Array | Array of booking dates |

**Use Cases:**
- Identify repeat guests (COMPLETED_BOOKINGS_COUNT_AS_GUEST >= 2)
- Find power guests (COMPLETED_BOOKINGS_COUNT_AS_GUEST >= 5)
- Calculate cancellation rate (CANCELLED / COMPLETED)
- Segment by booking recency

### User Activity (1 attribute)

| Attribute | Type | Description |
|-----------|------|-------------|
| `DAYS_SINCE_LAST_PLATFORM_ACTIVITY` | Number | Days since last app/web visit |

**Use Cases:**
- Identify dormant users (> 30 days)
- Trigger re-engagement campaigns
- Calculate activity cohorts

### Listing/Favorites Data (15 attributes)

| Attribute | Type | Description |
|-----------|------|-------------|
| `F2_POOL_ID` | Number | Second favorite pool ID |
| `F2_POOL_TITLE` | String | Pool name |
| `F2_CITY` | String | Pool city |
| `F2_STATE` | String | Pool state |
| `F2_HOURLY_PRICE` | Number | Hourly price |
| `F2_COVER_PHOTO_URL` | String | Photo URL for personalization |
| `F2_ADDED_FAV_LIST_DATE` | Time | When favorited |
| `5S_POOL_*` | Various | 5-star pool attributes |
| `AU_LY_*` | Various | Australia last-year attributes |

**Use Cases:**
- Personalize emails with favorite pool data
- Recommend similar listings
- Geographic segmentation

### Financial (5 attributes)

| Attribute | Type | Description |
|-----------|------|-------------|
| `CURRENT_CREDIT_BALANCE` | Number | Account credit balance |
| `CURRENT_CREDIT_BALANCE_*` | Number | Dated snapshots |

**Use Cases:**
- Target users with credits (conversion campaigns)
- Credit expiration reminders

### Identity (3 attributes)

| Attribute | Type | Description |
|-----------|------|-------------|
| `ACCOUNT_CREATED_AT` | Time | Registration date |
| `EMAIL` | String | Email (blocklisted for export) |
| `EMAIL_VERIFIED_AT` | Time | Verification timestamp |

**Use Cases:**
- Cohort by signup date
- Target unverified accounts

---

## Custom Events (250 total)

### Booking Lifecycle (80 events)

**Guest Booking Flow:**
```
CartCreated
  → BookingNewRequestToGuest
  → BookingApprovedToGuest / BookingDeclinedToGuest
  → BookingConfirmedToGuest
  → Booking24HourReminderGuest
  → BookingDayReminderGuest
  → BookingCompletedToGuest
  → GuestLeavesReview
```

**Host Booking Flow:**
```
BookingNewRequestToHost
  → BookingApprovedToHost / BookingDeclinedToHost
  → BookingConfirmedToHost
  → Booking24HourReminderHost
  → BookingCompletedToHost
  → BookingPaidToHost
```

**Key Events:**
| Event | Description | Use Case |
|-------|-------------|----------|
| `CartCreated` | Checkout initiated | Cart abandonment trigger |
| `BookingCompletedToGuest` | Experience finished | Review request, retention |
| `BookingCancelledToGuest` | Cancellation | Win-back, survey |
| `BookingRequestExpiredToHost` | Host didn't respond | Host engagement |
| `360DaysSinceLastBookingConfirmed` | 1 year since booking | Win-back trigger |

### Guest Actions (57 events)

**High-Value Events:**
| Event | Description |
|-------|-------------|
| `GuestCreatedFavoriteList` | Saved a pool |
| `GuestMessageSent` | Messaged a host |
| `GuestPressedAcceptAndPay` | Ready to checkout |
| `GuestPressedPurchasePass` | Premium interest |
| `GuestReceivedSpecialOffer` | Got discount |
| `GuestDeclinedSpecialOffer` | Rejected discount |
| `GuestSubmittedRefundRequest` | Refund requested |

### Host Actions (45 events)

**Key Onboarding Events:**
| Event | Description |
|-------|-------------|
| `HostAmenitiesAdded` | Added amenities |
| `HostAdjustPricing` | Changed price |
| `HostBookingRules` | Set rules |
| `FirstActiveListing` | First listing live |
| `HostAwardEarned` | Earned award |
| `HostAddedPromotionToListing` | Running promo |

### Review/Rating (6 events)

| Event | Description |
|-------|-------------|
| `GuestLeavesReview` | Review submitted |
| `GuestLeavesReviewToHost` | Review to host |
| `GuestLeavesReviewToGuest` | Host reviewed guest |
| `GuestAcceptReviewChangesFromHost` | Accepted edit |
| `GuestDeclineReviewChangesFromHost` | Rejected edit |

### Premium/Pass (30 events)

| Event | Description |
|-------|-------------|
| `GuestPurchasedPremiumMembership` | Subscribed |
| `GuestCancelledPremiumMembership` | Cancelled |
| `GuestMembershipActivated` | Activated |
| `GuestMembershipPaymentFailed` | Payment failed |
| `GuestPassPurchaseSuccess` | Pass bought |
| `GuestPassHoursUsed` | Used pass hours |
| `GuestConfirmedCancelPass` | Cancelled pass |

### Referral (3 events)

| Event | Description |
|-------|-------------|
| `DisplayedReferral` | Saw referral UI |
| `DisplayedReferralDetailsHost` | Host saw referral |
| `DisplayedSharingInvitesOptions` | Sharing options |

**Gap:** No `ReferralCompleted` event visible - may not be tracked

### App Events (6 events)

| Event | Description |
|-------|-------------|
| `Application Installed` | New install |
| `Application Opened` | App opened |
| `Application Updated` | App updated |
| `Application Backgrounded` | App backgrounded |
| `AppCrash` | Crash occurred |
| `Deep Link Opened` | Deep link used |

---

## Segments Analysis

### Key Segments (from API)

| Segment | Definition |
|---------|------------|
| `All Users` | No filters - total user base |
| `Guest-HasAccount0bookings` | Signed up but never booked |
| `Guest-HasBookings` | Has completed bookings after April 2022 |
| `V2_Hosts-CurrentlyLive` | Hosts with live listings |
| `V2_Hosts-NOT-Currently-Live` | Hosts without live listings |
| `WaitlistedHost` | Pending host approval |

### Segment Definitions (discovered)

**Guest-HasBookings:**
```
ROLE equals Guest
AND COMPLETED_BOOKINGS_COUNT_AS_GUEST > 0
AND LAST_BOOKING_START_DATE_AS_GUEST after 2022-04-30
```

**V2_Hosts-CurrentlyLive:**
```
ROLE equals Host
AND TOTAL_LIVE_LISTINGS_AS_HOST > 0
```

### Additional Attributes Referenced (system/undocumented)
- `ROLE` (Guest/Host)
- `TOTAL_LIVE_LISTINGS_AS_HOST`
- `LAST_BOOKING_START_DATE_AS_GUEST`

---

## Data Export Capabilities

### Available via API

| Data Type | Endpoint | Notes |
|-----------|----------|-------|
| User profiles | `/users/export/ids` | Bulk export by ID |
| Segment users | `/users/export/segment` | Export segment members |
| Events | `/events/list` | Event names only |
| Segments | `/segments/list` | Segment metadata |
| Campaigns | `/campaigns/list` | Campaign metadata |
| Canvases | `/canvas/list` | Canvas metadata |
| KPIs | `/kpi/*/data_series` | DAU, sessions, etc. |
| Campaign stats | `/campaigns/data_series` | Per-campaign metrics |

### Braze Currents (Recommended for Analytics)

For deeper analytics, recommend enabling **Braze Currents** to export to:
- Snowflake
- BigQuery
- Redshift
- S3/GCS

**Currents exports:**
- All user events in real-time
- Campaign/canvas engagement
- User attribute changes
- Session data

---

## Queryable Dimensions

### By Lifecycle Stage
```
NEW_USER: ACCOUNT_CREATED_AT in last 30 days
ACTIVE: DAYS_SINCE_LAST_PLATFORM_ACTIVITY < 7
ENGAGED: BOOKING_COUNT_AS_GUEST >= 1
POWER_USER: BOOKING_COUNT_AS_GUEST >= 5
DORMANT: DAYS_SINCE_LAST_PLATFORM_ACTIVITY > 30
CHURNED: DAYS_SINCE_LAST_PLATFORM_ACTIVITY > 180
```

### By Value
```
NO_BOOKINGS: COMPLETED_BOOKINGS_COUNT_AS_GUEST = 0
LOW_VALUE: COMPLETED_BOOKINGS_COUNT_AS_GUEST = 1
MEDIUM_VALUE: COMPLETED_BOOKINGS_COUNT_AS_GUEST 2-4
HIGH_VALUE: COMPLETED_BOOKINGS_COUNT_AS_GUEST >= 5
```

### By Role
```
GUEST_ONLY: ROLE = Guest
HOST_ONLY: ROLE = Host
DUAL_USER: Both guest and host activity
```

### By Geography
- Market segments exist for all major US cities
- Australia segments: Sydney, Victoria, Brisbane, Perth

---

## Recommended Queries

### 1. Guest Funnel Analysis
```
Segment by:
- ACCOUNT_CREATED_AT (cohort)
- COMPLETED_BOOKINGS_COUNT_AS_GUEST (conversion)
- DAYS_SINCE_LAST_PLATFORM_ACTIVITY (engagement)
```

### 2. Host Performance
```
Segment by:
- TOTAL_LIVE_LISTINGS_AS_HOST
- COMPLETED_BOOKINGS_COUNT_AS_HOST
- CANCELLED_BOOKINGS_COUNT_AS_HOST (reliability)
```

### 3. At-Risk Detection
```
Trigger on:
- DAYS_SINCE_LAST_PLATFORM_ACTIVITY > 30
- AND COMPLETED_BOOKINGS_COUNT_AS_GUEST >= 1
```

### 4. Upsell Candidates
```
Trigger on:
- COMPLETED_BOOKINGS_COUNT_AS_GUEST >= 3
- AND not premium member
- AND CURRENT_CREDIT_BALANCE = 0
```

---

## Data Limitations

1. **No revenue/GMV attributes** - Booking value not stored as user attribute
2. **No LTV calculation** - Would need Currents export
3. **Limited historical data** - Attributes show current state, not trends
4. **No NPS/rating attribute** - Review scores not stored on user profile
5. **Segment sizes not in API** - Can only get segment definitions

---

## Recommendations

### Immediate Actions
1. **Add LIFETIME_GMV attribute** - Track total booking value per user
2. **Add NPS_SCORE attribute** - After reviews
3. **Add LAST_BOOKING_DATE attribute** - For recency calculations
4. **Enable Currents** - For detailed analytics

### Segment Improvements
1. Create `Power_Guest_5Plus` segment
2. Create `At_Risk_30D_Inactive` segment
3. Create `Premium_Eligible` segment
4. Create `Referral_Completed` event tracking

### Analytics Integration
1. Export Currents to Snowflake/BigQuery
2. Build cohort retention dashboard
3. Create booking funnel visualization
4. Track host supply metrics

---

## API Quick Reference

```bash
# List all segments
curl "https://rest.iad-05.braze.com/segments/list" \
  -H "Authorization: Bearer $BRAZE_API_KEY"

# Get DAU
curl "https://rest.iad-05.braze.com/kpi/dau/data_series?length=30&unit=day" \
  -H "Authorization: Bearer $BRAZE_API_KEY"

# Export users from segment
curl -X POST "https://rest.iad-05.braze.com/users/export/segment" \
  -H "Authorization: Bearer $BRAZE_API_KEY" \
  -d '{"segment_id": "...", "fields_to_export": ["email", "custom_attributes"]}'

# Get campaign stats
curl "https://rest.iad-05.braze.com/campaigns/data_series?campaign_id=..." \
  -H "Authorization: Bearer $BRAZE_API_KEY"
```

---

*Discovery completed: 2026-01-30*
*Data source: Braze REST API (US-05)*
