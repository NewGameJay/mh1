# Brand Analytics Workflow

Fetch brand metrics including creative velocity and ad distribution.

## Prerequisites

Need brand_id or page_id. If user provides domain, first run competitor-research workflow.

---

## Fetch Analytics

```bash
curl -X GET "https://public.api.foreplay.co/api/brand/analytics?id={brand_id}&start_date={start}&end_date={end}" \
  -H "Authorization: $FOREPLAY_API_KEY"
```

**Parameters:**
| Parameter | Required | Format |
|-----------|----------|--------|
| id | Yes | Brand ID or Page ID |
| start_date | No | YYYY-MM-DD |
| end_date | No | YYYY-MM-DD |

---

## Response Data

The endpoint returns metrics including:
- Running ads count over time
- New ad launches per period
- Ad retirement rate
- Format mix (video/image/carousel distribution)
- Platform allocation (Facebook/Instagram split)

---

## Output

Return as structured data:
- Total ads tracked
- Currently active count
- New ads in period
- Retired ads in period
- Ads per week average
- Format breakdown (counts and percentages)
- Platform breakdown (counts and percentages)
