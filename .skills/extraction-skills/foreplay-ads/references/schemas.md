# Foreplay API Data Schemas

## Ad Object

The complete ad object returned from API endpoints.

```json
{
  "id": "string",
  "ad_id": "string",
  "name": "string",
  "brand_id": "string",
  "description": "string",
  "headline": "string",
  "cta_title": "string",
  "cta_type": "string",
  "link_url": "string",
  "display_format": "string",
  "publisher_platform": ["string"],
  "started_running": "string",
  "live": true,
  "running_duration": 0,
  "video_duration": 0.0,
  "thumbnail": "string",
  "video": "string",
  "image": "string",
  "cards": [],
  "avatar": "string",
  "categories": ["string"],
  "niches": ["string"],
  "market_target": ["string"],
  "languages": ["string"],
  "persona": {},
  "emotional_drivers": ["string"],
  "creative_targeting": {},
  "full_transcription": "string",
  "timestamped_transcription": [],
  "product_category": "string",
  "content_filter": {}
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| id | string | Foreplay internal identifier |
| ad_id | string | Facebook Ad Library identifier |
| name | string | Ad name/title |
| brand_id | string | Associated brand ID |
| description | string | Ad body copy/primary text |
| headline | string | Ad headline |
| cta_title | string | Call-to-action button text |
| cta_type | string | CTA button type (LEARN_MORE, SHOP_NOW, etc.) |
| link_url | string | Destination URL |
| display_format | string | video, image, carousel, dco, story, reels |
| publisher_platform | array | Platforms: facebook, instagram, audience_network, messenger |
| started_running | string | Date ad started (YYYY-MM-DD) |
| live | boolean | Currently active |
| running_duration | integer | Days running |
| video_duration | number | Length in seconds (video only) |
| thumbnail | string | Thumbnail image URL |
| video | string | Video asset URL |
| image | string | Image asset URL |
| cards | array | Carousel card objects |
| avatar | string | Brand avatar/logo URL |
| categories | array | Ad categories |
| niches | array | Vertical classifications |
| market_target | array | b2b, b2c |
| languages | array | Detected languages (ISO codes) |
| persona | object | Target persona information |
| emotional_drivers | array | Emotional appeals used |
| creative_targeting | object | Targeting insights |
| full_transcription | string | Complete video transcript |
| timestamped_transcription | array | Transcript with timestamps |
| product_category | string | Product type classification |
| content_filter | object | Content classifications |

---

## Brand Object

```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "category": "string",
  "niches": ["string"],
  "verification_status": "string",
  "url": "string",
  "websites": ["string"],
  "avatar": "string",
  "ad_library_id": "string",
  "is_delegate_page_with_linked_primary_profile": false
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| id | string | Foreplay brand identifier |
| name | string | Brand name |
| description | string | Brand description |
| category | string | Primary category |
| niches | array | Associated verticals |
| verification_status | string | Verification state |
| url | string | Primary website |
| websites | array | All associated websites |
| avatar | string | Brand logo URL |
| ad_library_id | string | Facebook Ad Library page ID |
| is_delegate_page_with_linked_primary_profile | boolean | Page delegation status |

---

## Board Object

```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "created_at": "string",
  "updated_at": "string",
  "ad_count": 0
}
```

---

## Carousel Card Object

```json
{
  "headline": "string",
  "description": "string",
  "image": "string",
  "video": "string",
  "link_url": "string",
  "cta_type": "string"
}
```

---

## Timestamped Transcription Entry

```json
{
  "time": 0,
  "text": "string"
}
```

---

## Pagination Response Wrapper

```json
{
  "data": [],
  "cursor": "string",
  "count": 0,
  "filters_applied": {},
  "order": "string"
}
```

---

## Enum Values

### display_format
- `video`
- `image`
- `carousel`
- `dco` (Dynamic Creative Optimization)
- `story`
- `reels`

### publisher_platform
- `facebook`
- `instagram`
- `audience_network`
- `messenger`

### market_target
- `b2b`
- `b2c`

### order
- `newest`
- `oldest`
- `longest_running`
- `most_relevant`

### niches
- `travel`
- `fashion`
- `food`
- `technology`
- `sports`
- `beauty`
- `health`
- `finance`
- `education`
- `entertainment`
- `automotive`
- `real_estate`
- `home`
- `pets`
- `gaming`
- `music`
- `art`
- `politics`
- `science`
- `environment`

### languages (ISO 639-1)
- `en` - English
- `es` - Spanish
- `de` - German
- `fr` - French
- `it` - Italian
- `pt` - Portuguese
- `nl` - Dutch
- `pl` - Polish
- `ru` - Russian
- `ja` - Japanese
- `ko` - Korean
- `zh` - Chinese
- `ar` - Arabic
- `hi` - Hindi
- (and more)

### cta_type (Common Values)
- `LEARN_MORE`
- `SHOP_NOW`
- `SIGN_UP`
- `BOOK_NOW`
- `DOWNLOAD`
- `GET_OFFER`
- `CONTACT_US`
- `WATCH_MORE`
- `APPLY_NOW`
- `SUBSCRIBE`
