# Spyder Tracking Workflow

Access brands monitored in Foreplay's Spyder feature.

## List Tracked Brands

```bash
curl -X GET "https://public.api.foreplay.co/api/spyder/brands?limit=10&offset=0" \
  -H "Authorization: $FOREPLAY_API_KEY"
```

Paginate with offset increments (max 10 per request).

---

## Get Brand Details

```bash
curl -X GET "https://public.api.foreplay.co/api/spyder/brand?brand_id={brand_id}" \
  -H "Authorization: $FOREPLAY_API_KEY"
```

---

## Get Tracked Brand's Ads

```bash
curl -X GET "https://public.api.foreplay.co/api/spyder/brand/ads?brand_id={brand_id}&limit=50&order=newest" \
  -H "Authorization: $FOREPLAY_API_KEY"
```

**Available Filters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| brand_id | string | Required |
| start_date | string | YYYY-MM-DD |
| end_date | string | YYYY-MM-DD |
| live | boolean | Active status |
| display_format | array | Creative types |
| publisher_platform | array | Platforms |
| cursor | integer | Pagination |
| limit | integer | Max 250 |
| order | string | Sort order |

---

## Common Queries

**Recent activity (last 7 days):**
```
brand_id={id}&start_date={7_days_ago}&order=newest
```

**Currently running:**
```
brand_id={id}&live=true
```

**Winners:**
```
brand_id={id}&running_duration_min_days=30&live=true
```

**New launches:**
```
brand_id={id}&running_duration_max_days=7&order=newest
```

---

## Output

**For brand list:**
- Brand name, category, verification status, ad_library_id

**For brand ads:**
- Total active ads
- Ad list with: headline, format, days running, status, platforms
