# LinkedIn Keyword Search - Quick Reference

## API Endpoint

```
POST https://api.crustdata.com/screener/linkedin_posts/keyword_search/
```

## Authentication

```bash
Authorization: Token YOUR_API_KEY
```

## Quick Start Command

```bash
curl -X POST "https://api.crustdata.com/screener/linkedin_posts/keyword_search/" \
  -H "Authorization: Token $CRUSTDATA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "AI",
    "limit": 10,
    "date_posted": "past-week"
  }'
```

## Filter Types Reference

| Filter Type | Description | Value Format | Notes |
|------------|-------------|--------------|-------|
| **MEMBER** | Posts by specific people | LinkedIn profile URLs | Cannot combine with COMPANY |
| **COMPANY** | Posts from company pages | LinkedIn company URLs | Cannot combine with AUTHOR_* or MEMBER |
| **AUTHOR_COMPANY** | Posts by employees of companies | LinkedIn company URLs | Cannot combine with COMPANY |
| **AUTHOR_INDUSTRY** | Posts by people in industries | Industry name strings | Cannot combine with COMPANY |
| **AUTHOR_TITLE** | Posts by people with job titles | Job title strings | **Single value only**, cannot combine with COMPANY |
| **MENTIONING_MEMBER** | Posts mentioning people | LinkedIn profile URLs | No restrictions |
| **MENTIONING_COMPANY** | Posts mentioning companies | LinkedIn company URLs | No restrictions |

## Incompatible Filter Combinations

❌ These combinations will return 400 Bad Request:

- `AUTHOR_COMPANY` + `COMPANY`
- `MEMBER` + `COMPANY`
- `AUTHOR_INDUSTRY` + `COMPANY`
- `AUTHOR_TITLE` + `COMPANY`

**Why?** A LinkedIn post is either from a company page OR from an individual author, never both.

## Date Range Options

- `past-24h` - Last 24 hours
- `past-week` - Last 7 days
- `past-month` - Last 30 days (default)
- `past-quarter` - Last 3 months
- `past-year` - Last 12 months

## Content Type Options

- `photos` - Posts with images
- `videos` - Video posts
- `documents` - Posts with documents
- `jobs` - Job postings
- `collaborativeArticles` - LinkedIn articles
- `liveVideos` - Live video posts

## Boolean Keyword Search

Supports "OR" and "AND" operators (max 6 keywords):

```json
{
  "keyword": "AI OR machine learning OR artificial intelligence"
}
```

```json
{
  "keyword": "Series A AND fundraise AND startup"
}
```

## Credit Costs

| Feature | Credits per Post |
|---------|-----------------|
| Base search | 1 credit |
| With `reactors` | 5 credits |
| With `comments` | 5 credits |
| With both | 10 credits |
| With `exact_keyword_match=true` | 3 credits |

**No results = No charge**

## Engagement Data

To fetch reactors and/or comments:

```json
{
  "keyword": "product launch",
  "limit": 50,
  "fields": "reactors,comments",
  "max_reactors": 100,
  "max_comments": 50
}
```

⚠️ **Warning:** This costs 10 credits per post (vs 1 credit without engagement data)

## Exact Keyword Match

For precise phrase matching:

```json
{
  "keyword": "Starting a new position",
  "limit": 100,
  "exact_keyword_match": true
}
```

- Scans first N posts (N = limit)
- Returns only exact matches
- Costs 3 credits per post returned
- Cannot use `page` parameter (must use `limit`)

## Pagination

**Option 1: Page-based** (for browsing)
```json
{
  "keyword": "AI",
  "page": 1
}
```
- Each page has 5 posts
- Max page: 100

**Option 2: Limit-based** (for bulk collection)
```json
{
  "keyword": "AI",
  "limit": 500
}
```
- Max limit: 500
- Required when using `exact_keyword_match=true`

## Common Filter Examples

### Posts by specific people

```json
{
  "filters": [
    {
      "filter_type": "MEMBER",
      "type": "in",
      "value": [
        "https://www.linkedin.com/in/satyanadella",
        "https://www.linkedin.com/in/jeffweiner08/"
      ]
    }
  ]
}
```

### Posts from company pages

```json
{
  "filters": [
    {
      "filter_type": "COMPANY",
      "type": "in",
      "value": [
        "https://www.linkedin.com/company/microsoft",
        "https://www.linkedin.com/company/openai"
      ]
    }
  ]
}
```

### Posts by employees of companies

```json
{
  "filters": [
    {
      "filter_type": "AUTHOR_COMPANY",
      "type": "in",
      "value": [
        "https://www.linkedin.com/company/google",
        "https://www.linkedin.com/company/meta"
      ]
    }
  ]
}
```

### Posts by industry

```json
{
  "filters": [
    {
      "filter_type": "AUTHOR_INDUSTRY",
      "type": "in",
      "value": [
        "Software Development",
        "Technology, Information and Internet"
      ]
    }
  ]
}
```

### Posts mentioning companies

```json
{
  "filters": [
    {
      "filter_type": "MENTIONING_COMPANY",
      "type": "in",
      "value": [
        "https://www.linkedin.com/company/openai",
        "https://www.linkedin.com/company/anthropic"
      ]
    }
  ]
}
```

## Valid Industry Values

Get the full list:
```
https://crustdata-docs-region-json.s3.us-east-2.amazonaws.com/industry_values.json
```

Common industries:
- Software Development
- Technology, Information and Internet
- Marketing & Advertising
- Financial Services
- Venture Capital & Private Equity
- Computer & Network Security
- Artificial Intelligence
- Internet Publishing
- IT Services and IT Consulting

## Rate Limiting

- Monitor `X-RateLimit-Limit` and `X-RateLimit-Remaining` headers
- 429 responses indicate rate limit exceeded
- Implement exponential backoff

## Response Format

Success (200):
```json
{
  "posts": [...],
  "total_count": 234
}
```

Error (404 with exact match):
```json
{
  "total_fetched_posts": 150,
  "error": "No matching posts found..."
}
```

Error (400):
```json
{
  "error": "Invalid filter combination..."
}
```

## Tips for Cost Optimization

1. **Start without engagement data** - Test queries with base 1 credit/post
2. **Use smaller limits for testing** - Try limit=10-20 first
3. **Avoid exact_keyword_match for exploration** - Use it only when needed
4. **Combine filters strategically** - Narrow results to reduce post count
5. **Check for incompatible filters** - Validate before running

## Troubleshooting Checklist

**No results?**
- [ ] Verify keywords are spelled correctly
- [ ] Check date range isn't too narrow
- [ ] Test without filters first
- [ ] Search LinkedIn manually to verify content exists

**400 Bad Request?**
- [ ] Check for incompatible filter combinations
- [ ] Verify all LinkedIn URLs include https://www.linkedin.com/
- [ ] Ensure AUTHOR_TITLE has only one value
- [ ] Validate industry names against official list

**High cost?**
- [ ] Remove reactors/comments fields if not needed
- [ ] Reduce limit value
- [ ] Use standard search instead of exact_keyword_match

**429 Rate Limit?**
- [ ] Implement exponential backoff
- [ ] Add delays between requests
- [ ] Check X-RateLimit-* headers

## Full API Documentation

https://fulldocs.crustdata.com/
