# Foreplay API Data Retrieval Patterns

Common queries for fetching ad data from Foreplay.

## Finding Competitor Ads

### By Domain
```
GET /api/brand/getBrandsByDomain?domain={competitor.com}
GET /api/brand/getAdsByBrandId?brand_ids={brand_id}&limit=50
```

### By Facebook Page ID
```
GET /api/brand/getAdsByPageId?page_id={page_id}&limit=50
```

### Multiple Competitors
```
GET /api/brand/getAdsByBrandId?brand_ids={id1}&brand_ids={id2}&brand_ids={id3}
```

---

## Filtering by Performance Signals

### Long-Running Ads (30+ days = proven performers)
```
running_duration_min_days=30&live=true&order=longest_running
```

### Recently Launched (testing phase)
```
running_duration_max_days=7&order=newest
```

### Currently Active Only
```
live=true
```

---

## Filtering by Creative Type

### Video Ads
```
display_format=video
```

### Short-Form Video (hooks under 15s)
```
display_format=video&video_duration_max=15
```

### Instagram Reels
```
display_format=reels&publisher_platform=instagram
```

### Carousel Ads
```
display_format=carousel
```

### Static Images
```
display_format=image
```

---

## Filtering by Platform

### Facebook Only
```
publisher_platform=facebook
```

### Instagram Only
```
publisher_platform=instagram
```

### Multi-Platform
```
publisher_platform=facebook&publisher_platform=instagram
```

---

## Filtering by Vertical/Market

### By Niche
```
niches=fashion&niches=beauty
```

### B2B vs B2C
```
market_target=b2b
market_target=b2c
```

---

## Date Range Queries

### Last 7 Days
```
start_date={7_days_ago}&end_date={today}
```

### Last 30 Days
```
start_date={30_days_ago}&end_date={today}
```

### Specific Quarter (e.g., Q4 2024)
```
start_date=2024-10-01&end_date=2024-12-31
```

---

## Swipe File Queries

### All Saved Ads
```
GET /api/swipefile/ads?limit=50&order=newest
```

### Saved Videos Only
```
GET /api/swipefile/ads?display_format=video&limit=50
```

### Saved Winners (long-running)
```
GET /api/swipefile/ads?running_duration_min_days=30&order=longest_running
```

---

## Board Queries

### List All Boards
```
GET /api/boards?limit=10
```

### Get Ads from Board
```
GET /api/board/ads?board_id={board_id}&limit=50
```

### Get Brands in Board
```
GET /api/board/brands?board_id={board_id}
```

---

## Spyder (Tracked Brands)

### List Tracked Brands
```
GET /api/spyder/brands?limit=10
```

### Get Tracked Brand's Ads
```
GET /api/spyder/brand/ads?brand_id={brand_id}&limit=50
```

### Recent Activity from Tracked Brand
```
GET /api/spyder/brand/ads?brand_id={brand_id}&start_date={7_days_ago}&order=newest
```

---

## Brand Analytics

### Get Brand Metrics
```
GET /api/brand/analytics?id={brand_id}&start_date={start}&end_date={end}
```

Returns: creative velocity, running ads distribution, format trends.

---

## Pagination

Most endpoints support pagination:
- `offset` + `limit` for boards/brands endpoints
- `cursor` + `limit` for ad endpoints

Default limit: 50 (balance between data and credits)
Max limit: 250

---

## Credit-Efficient Queries

To minimize credit usage:
1. Use specific filters to narrow results
2. Start with small limits, increase if needed
3. Use `order=longest_running` to get highest-value ads first
4. Check `X-Credits-Remaining` header after each request
