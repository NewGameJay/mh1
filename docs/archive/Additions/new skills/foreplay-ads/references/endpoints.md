# Foreplay API Endpoints Reference

Base URL: `https://public.api.foreplay.co`

## Authentication

All requests require API key in Authorization header:
```
Authorization: YOUR_API_KEY
```

---

## SwipeFile Endpoints

### GET /api/swipefile/ads
Retrieve ads from user's personal swipefile collection.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| start_date | string | No | YYYY-MM-DD format |
| end_date | string | No | YYYY-MM-DD format |
| live | boolean | No | Filter active/inactive |
| display_format | array | No | video, image, carousel, dco, story, reels |
| publisher_platform | array | No | facebook, instagram, audience_network, messenger |
| niches | array | No | travel, fashion, food, technology, etc. |
| market_target | array | No | b2b, b2c |
| languages | array | No | en, es, de, fr, etc. |
| video_duration_min | number | No | Minimum seconds |
| video_duration_max | number | No | Maximum seconds |
| running_duration_min_days | integer | No | Minimum days |
| running_duration_max_days | integer | No | Maximum days |
| offset | integer | No | Pagination offset |
| limit | integer | No | Max 250 |
| order | string | No | newest, oldest, longest_running, most_relevant |

**Response:** Array of ad objects with cursor and metadata

---

## Boards Endpoints

### GET /api/boards
Retrieve all boards for authenticated user.

**Parameters:**
| Name | Type | Required | Default | Max |
|------|------|----------|---------|-----|
| offset | integer | No | 0 | - |
| limit | integer | No | 10 | 10 |

**Response:** Array of board objects

---

### GET /api/board/brands
Get brands in a specific board.

**Parameters:**
| Name | Type | Required |
|------|------|----------|
| board_id | string | Yes |
| offset | integer | No |
| limit | integer | No |

**Response:** Array of brand objects

---

### GET /api/board/ads
Retrieve ads from a board with filters.

**Parameters:**
| Name | Type | Required |
|------|------|----------|
| board_id | string | Yes |
| start_date | string | No |
| end_date | string | No |
| live | boolean | No |
| display_format | array | No |
| publisher_platform | array | No |
| niches | array | No |
| market_target | array | No |
| languages | array | No |
| video_duration_min | number | No |
| video_duration_max | number | No |
| running_duration_min_days | integer | No |
| running_duration_max_days | integer | No |
| cursor | integer | No |
| limit | integer | No (max 250) |
| order | string | No |

**Response:** Array of ads with cursor pagination

---

## Spyder Endpoints

### GET /api/spyder/brands
Retrieve tracked brands in Spyder.

**Parameters:**
| Name | Type | Required | Default | Max |
|------|------|----------|---------|-----|
| offset | integer | No | 0 | - |
| limit | integer | No | 10 | 10 |

**Response:** Array of brand objects

---

### GET /api/spyder/brand
Get detailed info for a tracked brand.

**Parameters:**
| Name | Type | Required |
|------|------|----------|
| brand_id | string | Yes |

**Response:** Single brand object

---

### GET /api/spyder/brand/ads
Retrieve ads for a tracked brand.

**Parameters:**
| Name | Type | Required |
|------|------|----------|
| brand_id | string/integer | Yes |
| start_date | string | No |
| end_date | string | No |
| live | boolean | No |
| display_format | array | No |
| publisher_platform | array | No |
| niches | array | No |
| market_target | array | No |
| languages | array | No |
| video_duration_min | number | No |
| video_duration_max | number | No |
| running_duration_min_days | integer | No |
| running_duration_max_days | integer | No |
| cursor | integer | No |
| limit | integer | No (max 250) |
| order | string | No |

**Response:** Array of ads with pagination

---

## Ad Endpoints

### GET /api/ad
Retrieve ad details by ID (query parameter).

**Parameters:**
| Name | Type | Required |
|------|------|----------|
| ad_id | string | Yes |

**Response:** Single ad object

---

### GET /api/ad/{ad_id}
Retrieve ad details by ID (path parameter).

**Path Parameters:**
| Name | Type | Required |
|------|------|----------|
| ad_id | string | Yes |

**Response:** Single ad object

---

## Brand Endpoints

### GET /api/brand/getAdsByBrandId
Retrieve ads for specific brand IDs.

**Parameters:**
| Name | Type | Required |
|------|------|----------|
| brand_ids | array | Yes |
| live | boolean | No |
| display_format | array | No |
| publisher_platform | array | No |
| niches | array | No |
| market_target | array | No |
| languages | array | No |
| video_duration_min | number | No |
| video_duration_max | number | No |
| running_duration_min_days | integer | No |
| running_duration_max_days | integer | No |
| start_date | string | No |
| end_date | string | No |
| cursor | integer | No |
| limit | integer | No (max 250) |
| order | string | No |

**Response:** Array of ads with pagination

---

### GET /api/brand/getAdsByPageId
Get ads by Facebook page ID.

**Parameters:**
| Name | Type | Required |
|------|------|----------|
| page_id | string/integer | Yes |
| start_date | string | No |
| end_date | string | No |
| order | string | No |
| live | boolean | No |
| display_format | array | No |
| publisher_platform | array | No |
| niches | array | No |
| market_target | array | No |
| languages | array | No |
| video_duration_min | number | No |
| video_duration_max | number | No |
| running_duration_min_days | integer | No |
| running_duration_max_days | integer | No |
| cursor | integer | No |
| limit | integer | No (max 250) |

**Response:** Array of ads for the page's brand

---

### GET /api/brand/getBrandsByDomain
Search for brands by domain name.

**Parameters:**
| Name | Type | Required | Default |
|------|------|----------|---------|
| domain | string | Yes | - |
| limit | integer | No | 10 |
| order | string | No | most_ranked |

**Order Options:** most_ranked, least_ranked

**Response:** Array of potential brand matches (not guaranteed)

---

### GET /api/brand/analytics
Get brand analytics and trends.

**Parameters:**
| Name | Type | Required |
|------|------|----------|
| id | string | Yes (brand ID or page ID) |
| start_date | string | No |
| end_date | string | No |

**Response:** Analytics metrics from Clickhouse

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request - Check parameters |
| 401 | Unauthorized - Invalid API key |
| 402 | Insufficient Credits |
| 403 | Forbidden - Access denied |
| 404 | Not Found |
| 500 | Server Error |

---

## Rate Limiting & Credits

- Check `X-Credits-Remaining` response header
- 1 credit per ad returned
- 1 credit per brand request
