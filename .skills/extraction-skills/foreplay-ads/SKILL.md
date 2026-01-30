---
name: foreplay-ads
description: Fetches ad data from Foreplay API. Use when retrieving competitor ads, swipe file contents, board collections, tracked brands, or ad details. This is a data retrieval skill - for strategic analysis, use with the paid-ads-analyst agent.
version: "1.0.0"
status: active
---

<objective>
Retrieve ad intelligence data from Foreplay's API. This skill handles authentication, endpoint routing, filtering, and pagination to return structured ad data for further analysis.
</objective>

<quick_start>
1. Get the API key from the project `.env` file (FOREPLAY_API_KEY variable)
2. State what data you need:
   - "Get ads for [domain]"
   - "Show my swipe file"
   - "List my boards"
   - "Get ads from board [name]"
   - "Show tracked brands"
   - "Get details for ad [id]"
3. Specify filters if needed (format, platform, date range, etc.)
</quick_start>

<authentication>
**API Key Location:** Project root `.env` file contains `FOREPLAY_API_KEY`

To retrieve the key, read the `.env` file and extract the FOREPLAY_API_KEY value.

All requests require API key in Authorization header:
```
Authorization: {FOREPLAY_API_KEY value from .env}
```
Base URL: https://public.api.foreplay.co
</authentication>

<capabilities>
| Capability | Endpoint | Use When |
|------------|----------|----------|
| competitor-research | /api/brand/* | Finding ads by domain, page ID, or brand ID |
| swipe-file-access | /api/swipefile/ads | Retrieving saved ads from personal collection |
| board-management | /api/boards, /api/board/* | Accessing organized ad collections |
| spyder-tracking | /api/spyder/* | Getting data on tracked/monitored brands |
| brand-analytics | /api/brand/analytics | Fetching brand metrics and velocity data |
| ad-details | /api/ad/* | Getting full details for specific ad IDs |
</capabilities>

<routing_logic>
| User Request | Workflow |
|--------------|----------|
| Ads by domain/URL | competitor-research |
| Ads by Facebook page | competitor-research |
| My saved ads | swipe-file-access |
| My boards / board contents | board-management |
| Tracked brands / competitor monitoring | spyder-tracking |
| Brand metrics / creative velocity | brand-analytics |
| Specific ad by ID | ad-details |
</routing_logic>

<common_filters>
Apply these across most endpoints:

| Filter | Values | Purpose |
|--------|--------|---------|
| display_format | video, image, carousel, dco, story, reels | Creative type |
| publisher_platform | facebook, instagram, audience_network, messenger | Platform |
| niches | travel, fashion, food, technology, sports, beauty, health, finance, education, entertainment, automotive, real_estate, home, pets, gaming, music, art, politics, science, environment | Vertical |
| market_target | b2b, b2c | Audience type |
| languages | en, es, de, fr, it, pt, etc. | Language |
| live | true/false | Active status |
| start_date, end_date | YYYY-MM-DD | Date range |
| video_duration_min/max | seconds | Video length |
| running_duration_min/max_days | days | Ad longevity |
| order | newest, oldest, longest_running, most_relevant | Sort |
| limit | max 250 | Results per request |
</common_filters>

<credit_system>
- 1 credit per ad returned
- 1 credit per brand request
- Check X-Credits-Remaining header in responses
</credit_system>

<error_codes>
| Code | Meaning | Action |
|------|---------|--------|
| 400 | Bad request | Check parameter format |
| 401 | Unauthorized | Verify API key |
| 402 | Insufficient credits | Check credit balance |
| 403 | Forbidden | Check account permissions |
| 404 | Not found | Verify ID exists |
| 500 | Server error | Retry with backoff |
</error_codes>

<output_format>
Return data in structured format:

**For ad lists:**
| Field | Brand | Headline | Format | Days | Status | Platforms |
|-------|-------|----------|--------|------|--------|-----------|

**For single ads:**
- Core metadata (id, brand, format, status, duration)
- Creative assets (thumbnail, video/image URLs)
- Copy (headline, description, CTA)
- Transcript (if video)

**For brands:**
- Brand info (name, category, domain, ad_library_id)
- Verification status
</output_format>

<references>
- references/endpoints.md - Complete API endpoint documentation
- references/schemas.md - Request/response data structures
- references/use-cases.md - Common data retrieval patterns
</references>

<workflows>
- workflows/competitor-research.md - Fetch ads by domain/page/brand
- workflows/swipe-file-access.md - Query personal swipe file
- workflows/board-management.md - Access board collections
- workflows/spyder-tracking.md - Get tracked brand data
- workflows/brand-analytics.md - Retrieve brand metrics
- workflows/ad-details.md - Get full ad details by ID
</workflows>
