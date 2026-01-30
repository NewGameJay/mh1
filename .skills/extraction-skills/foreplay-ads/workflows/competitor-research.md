# Competitor Research Workflow

Fetch competitor ads by domain, Facebook page ID, or brand ID.

## By Domain

**Step 1:** Extract domain from URL
- `https://example.com/page` → `example.com`
- `www.example.com` → `example.com`

**Step 2:** Find brand
```bash
curl -X GET "https://public.api.foreplay.co/api/brand/getBrandsByDomain?domain={domain}&limit=10" \
  -H "Authorization: $FOREPLAY_API_KEY"
```

**Step 3:** If multiple brands returned, confirm with user which to use

**Step 4:** Fetch ads
```bash
curl -X GET "https://public.api.foreplay.co/api/brand/getAdsByBrandId?brand_ids={brand_id}&limit=50&order=newest" \
  -H "Authorization: $FOREPLAY_API_KEY"
```

---

## By Facebook Page ID

**Step 1:** Extract page ID from user input or Facebook URL

**Step 2:** Fetch ads directly
```bash
curl -X GET "https://public.api.foreplay.co/api/brand/getAdsByPageId?page_id={page_id}&limit=50&order=newest" \
  -H "Authorization: $FOREPLAY_API_KEY"
```

---

## By Brand IDs

**Step 1:** Collect brand IDs (single or comma-separated list)

**Step 2:** Fetch ads for all brands
```bash
curl -X GET "https://public.api.foreplay.co/api/brand/getAdsByBrandId?brand_ids={id1}&brand_ids={id2}&limit=100" \
  -H "Authorization: $FOREPLAY_API_KEY"
```

**Step 3:** Handle pagination with cursor if more results exist

---

## Common Filters

| Filter | Example | Purpose |
|--------|---------|---------|
| Active only | `live=true` | Currently running ads |
| Long-running | `running_duration_min_days=30` | Proven performers |
| Recent | `order=newest` | Latest launches |
| Video only | `display_format=video` | Video creatives |
| Platform | `publisher_platform=instagram` | Platform-specific |

---

## Output

Return as structured data:
- Brand metadata (name, category, domain)
- Ad count (total, active, inactive)
- Ad list with: headline, format, days running, status, platforms
