# Platform Reference: [Platform Name]

## Overview

**Platform**: [e.g., HubSpot, Salesforce, LinkedIn]
**Connection Method**: [MCP, API, Browser Automation]
**Rate Limits**: [Requests per minute/hour]

## Authentication

```yaml
# Required credentials
credentials:
  - name: API_KEY
    type: secret
    source: environment
  - name: ACCESS_TOKEN
    type: oauth
    refresh: true
```

## Key Endpoints/Operations

### Operation 1: [Name]

**Purpose**: [What this does]

**Request**:
```json
{
  "endpoint": "/api/v3/...",
  "method": "GET",
  "params": {
    "limit": 100,
    "properties": ["email", "firstname", "lastname"]
  }
}
```

**Response**:
```json
{
  "results": [...],
  "paging": {
    "next": {...}
  }
}
```

**Common Errors**:
| Code | Meaning | Solution |
|------|---------|----------|
| 401 | Unauthorized | Refresh token |
| 429 | Rate limited | Backoff and retry |
| 404 | Not found | Check ID format |

### Operation 2: [Name]

[Similar structure...]

## Data Models

### Model: [Entity Name]

```json
{
  "id": "string",
  "properties": {
    "email": "string (required)",
    "firstname": "string",
    "lastname": "string",
    "company": "string",
    "lifecycle_stage": "enum: subscriber|lead|mql|sql|opportunity|customer"
  },
  "associations": {
    "companies": ["string"],
    "deals": ["string"]
  }
}
```

## Query Patterns

### Pattern 1: [Common Query Type]

```sql
-- Purpose: [What this achieves]
SELECT
  contact.email,
  contact.firstname,
  deal.amount
FROM contacts contact
LEFT JOIN deals deal ON contact.id = deal.contact_id
WHERE contact.lifecycle_stage = 'customer'
```

### Pattern 2: [Another Common Query]

[Similar structure...]

## Best Practices

1. **Always paginate** - Never assume results fit in one call
2. **Cache aggressively** - Data doesn't change that often
3. **Batch operations** - Group creates/updates when possible
4. **Handle rate limits** - Implement exponential backoff

## MH1-Specific Usage

### Via MCP

```python
# Example using MCP
result = mcp.hubspot.get_contacts(
    limit=100,
    properties=["email", "firstname", "lifecycle_stage"]
)
```

### Via Browser Automation (Fallback)

```python
# When API fails, use browser
from lib.browser_automation import MH1BrowserClient

with MH1BrowserClient() as browser:
    browser.open("https://app.hubspot.com/contacts/...")
    snapshot = browser.snapshot()
```

## Troubleshooting

### Issue: [Common Problem]

**Symptoms**: [What you observe]

**Cause**: [Root cause]

**Solution**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Issue: [Another Problem]

[Similar structure...]

## Changelog

| Date | Change | Impact |
|------|--------|--------|
| 2024-01 | API v3 released | New endpoints, deprecations |
| 2024-03 | Rate limits changed | Reduced from 100 to 50/min |
