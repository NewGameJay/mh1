# Ad Details Workflow

Retrieve complete details for a specific ad by ID.

## Fetch Ad

**Option A - Query parameter:**
```bash
curl -X GET "https://public.api.foreplay.co/api/ad?ad_id={ad_id}" \
  -H "Authorization: $FOREPLAY_API_KEY"
```

**Option B - Path parameter:**
```bash
curl -X GET "https://public.api.foreplay.co/api/ad/{ad_id}" \
  -H "Authorization: $FOREPLAY_API_KEY"
```

---

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| id | string | Foreplay ID |
| ad_id | string | Ad Library ID |
| brand_id | string | Associated brand |
| headline | string | Ad headline |
| description | string | Body copy |
| cta_title | string | CTA text |
| cta_type | string | CTA type (LEARN_MORE, SHOP_NOW, etc.) |
| link_url | string | Destination URL |
| display_format | string | video/image/carousel/etc. |
| publisher_platform | array | Platforms |
| started_running | string | Launch date |
| live | boolean | Active status |
| running_duration | integer | Days running |
| video_duration | number | Seconds (if video) |
| thumbnail | string | Thumbnail URL |
| video | string | Video URL |
| image | string | Image URL |
| cards | array | Carousel cards |
| niches | array | Verticals |
| market_target | array | B2B/B2C |
| languages | array | Languages |
| emotional_drivers | array | Emotional appeals |
| full_transcription | string | Video transcript |
| timestamped_transcription | array | Transcript with timestamps |

---

## Output

Return all available fields organized by category:
- **Status:** format, platforms, active, days running
- **Assets:** thumbnail, video/image URLs
- **Copy:** headline, description, CTA
- **Targeting:** niches, market, languages
- **Transcript:** full text (if video)
