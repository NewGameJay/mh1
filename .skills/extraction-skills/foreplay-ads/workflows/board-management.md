# Board Management Workflow

Access organized ad collections in Foreplay boards.

## List All Boards

```bash
curl -X GET "https://public.api.foreplay.co/api/boards?limit=10&offset=0" \
  -H "Authorization: $FOREPLAY_API_KEY"
```

Paginate with offset increments (max 10 per request).

---

## Get Brands in Board

```bash
curl -X GET "https://public.api.foreplay.co/api/board/brands?board_id={board_id}&limit=10" \
  -H "Authorization: $FOREPLAY_API_KEY"
```

---

## Get Ads from Board

```bash
curl -X GET "https://public.api.foreplay.co/api/board/ads?board_id={board_id}&limit=50&order=newest" \
  -H "Authorization: $FOREPLAY_API_KEY"
```

**Available Filters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| board_id | string | Required |
| start_date | string | YYYY-MM-DD |
| end_date | string | YYYY-MM-DD |
| live | boolean | Active status |
| display_format | array | Creative types |
| publisher_platform | array | Platforms |
| niches | array | Verticals |
| market_target | array | B2B/B2C |
| video_duration_min/max | number | Seconds |
| running_duration_min/max_days | integer | Days |
| cursor | integer | Pagination |
| limit | integer | Max 250 |
| order | string | Sort order |

---

## Common Queries

**All ads from board:**
```
board_id={id}&limit=50
```

**Winners from board:**
```
board_id={id}&running_duration_min_days=30&order=longest_running
```

**Videos only:**
```
board_id={id}&display_format=video
```

---

## Output

**For board list:**
- Board name, ID, ad count

**For board contents:**
- Brand summary (if multiple brands)
- Ad list with: brand, headline, format, days running, status
