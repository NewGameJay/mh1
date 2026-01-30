# Swipe File Access Workflow

Retrieve ads from personal Foreplay swipe file collection.

## Fetch Swipe File Ads

```bash
curl -X GET "https://public.api.foreplay.co/api/swipefile/ads?limit=50&order=newest" \
  -H "Authorization: $FOREPLAY_API_KEY"
```

---

## Available Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| start_date | string | YYYY-MM-DD |
| end_date | string | YYYY-MM-DD |
| live | boolean | Active/inactive filter |
| display_format | array | video, image, carousel, dco, story, reels |
| publisher_platform | array | facebook, instagram, audience_network, messenger |
| niches | array | Vertical categories |
| market_target | array | b2b, b2c |
| languages | array | Language codes |
| video_duration_min | number | Min seconds |
| video_duration_max | number | Max seconds |
| running_duration_min_days | integer | Min days running |
| running_duration_max_days | integer | Max days running |
| offset | integer | Pagination offset |
| limit | integer | Max 250 |
| order | string | newest, oldest, longest_running, most_relevant |

---

## Common Queries

**Recent saves:**
```
order=newest&limit=50
```

**Video hooks (short, proven):**
```
display_format=video&video_duration_max=15&running_duration_min_days=14
```

**Winners only:**
```
running_duration_min_days=30&live=true&order=longest_running
```

**By niche:**
```
niches=fashion&niches=beauty&market_target=b2c
```

---

## Pagination

For large collections:
1. First: `offset=0&limit=50`
2. Next: `offset=50&limit=50`
3. Continue until results < limit

---

## Output

Return as structured list:
- Ad count (total matching filters)
- Ad list with: brand, headline, format, days running, status
