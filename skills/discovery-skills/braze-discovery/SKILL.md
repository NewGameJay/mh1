---
name: braze-discovery
description: |
  Discover and audit Braze customer engagement platform data including custom attributes,
  custom events, segments, campaigns, canvases, and KPIs.
  Use when asked to 'discover Braze data', 'audit Braze', 'explore customer data',
  'what data is in Braze', 'list Braze segments', or 'Braze data dictionary'.
license: Proprietary
compatibility:
  - Braze REST API
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  created: "2026-01-30"
  updated: "2026-01-30"
  estimated_runtime: "2-5min"
  max_runtime: "10min"
  estimated_cost: "$0.10"
  max_cost: "$0.50"
  client_facing: false
  requires_human_review: false
  tags:
    - discovery
    - braze
    - customer-data
    - cdp
    - marketing-automation
allowed-tools: Read Write Bash
---

# Braze Discovery Skill

Comprehensive discovery of Braze customer engagement platform data for clients using Braze as their primary CDP/CRM.

## When to Use

Use this skill when:
- Client uses Braze as their customer data platform
- Need to understand available custom attributes and events
- Auditing existing segments, campaigns, or canvases
- Building data dictionary for a Braze-centric client
- Planning lifecycle marketing automation

Do NOT use when:
- Client uses a different CDP (use appropriate discovery skill)
- Only need to send a campaign (use campaign execution skill)
- Need real-time user data (use user export endpoints directly)

---

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `client_id` | string | yes | MH1 client ID |
| `braze_api_key` | string | yes | Braze REST API key |
| `braze_endpoint` | string | yes | Braze REST endpoint (e.g., https://rest.iad-05.braze.com) |
| `discovery_scope` | array | no | What to discover: ["attributes", "events", "segments", "campaigns", "canvases", "kpis"] |

---

## Outputs

| Name | Type | Description |
|------|------|-------------|
| `custom_attributes` | array | All custom attributes with types and categories |
| `custom_events` | array | All custom events categorized by type |
| `segments` | array | All segments with definitions |
| `campaigns` | array | Recent campaigns with metadata |
| `canvases` | array | All canvases (automation flows) |
| `kpis` | object | DAU, sessions, uninstalls data |
| `data_dictionary` | object | Comprehensive data model documentation |
| `recommendations` | array | Gaps and improvement suggestions |

**Output location:** `clients/{client_id}/artifacts/braze-data-discovery-{date}.md`

---

## Requirements

### Platform Connections (Required)

| Platform | Type | Purpose | How to Setup |
|----------|------|---------|--------------|
| Braze | CDP/Marketing | Source of all data | Add API key to clients/{id}/credentials/.env |

### Client Data Needed

| Data | Location | Required | How to Provide |
|------|----------|----------|----------------|
| Braze API Key | clients/{id}/credentials/.env | Yes | Get from Braze Dashboard → Settings → API Keys |
| Braze Endpoint | clients/{id}/credentials/.env | Yes | Based on cluster (US-01 to US-08, EU-01, EU-02) |

### Environment Variables

```bash
BRAZE_API_KEY=your-api-key-here
BRAZE_REST_ENDPOINT=https://rest.iad-05.braze.com
```

---

## Process

### Step 1: Validate Connection

Test API connectivity:

```bash
curl -s -X GET "${BRAZE_REST_ENDPOINT}/segments/list" \
  -H "Authorization: Bearer ${BRAZE_API_KEY}" \
  -H "Content-Type: application/json"
```

**Expected:** JSON response with segments array
**On failure:** Check API key permissions and endpoint

### Step 2: Discover Custom Attributes

```bash
curl -s -X GET "${BRAZE_REST_ENDPOINT}/custom_attributes" \
  -H "Authorization: Bearer ${BRAZE_API_KEY}" \
  -H "Content-Type: application/json"
```

**Categorize attributes by:**
- Booking/Transaction metrics
- User activity
- Listing/Product data
- Financial (credits, revenue)
- Identity (email, dates)
- Campaign/Flow tracking

### Step 3: Discover Custom Events

```bash
curl -s -X GET "${BRAZE_REST_ENDPOINT}/events/list" \
  -H "Authorization: Bearer ${BRAZE_API_KEY}" \
  -H "Content-Type: application/json"
```

**Categorize events by:**
- Booking/Purchase lifecycle
- Guest/Customer actions
- Host/Seller actions
- Review/Rating
- Premium/Subscription
- Referral
- App events

### Step 4: Audit Segments

```bash
curl -s -X GET "${BRAZE_REST_ENDPOINT}/segments/list" \
  -H "Authorization: Bearer ${BRAZE_API_KEY}" \
  -H "Content-Type: application/json"
```

For each key segment, get details:

```bash
curl -s -X GET "${BRAZE_REST_ENDPOINT}/segments/details?segment_id={id}" \
  -H "Authorization: Bearer ${BRAZE_API_KEY}"
```

### Step 5: Audit Campaigns

```bash
curl -s -X GET "${BRAZE_REST_ENDPOINT}/campaigns/list?page=0&include_archived=false&sort_direction=desc" \
  -H "Authorization: Bearer ${BRAZE_API_KEY}" \
  -H "Content-Type: application/json"
```

### Step 6: Audit Canvases

```bash
curl -s -X GET "${BRAZE_REST_ENDPOINT}/canvas/list?page=0&include_archived=false&sort_direction=desc" \
  -H "Authorization: Bearer ${BRAZE_API_KEY}" \
  -H "Content-Type: application/json"
```

### Step 7: Pull KPIs

```bash
# Daily Active Users (30 days)
curl -s -X GET "${BRAZE_REST_ENDPOINT}/kpi/dau/data_series?length=30&unit=day" \
  -H "Authorization: Bearer ${BRAZE_API_KEY}"

# Sessions (30 days)
curl -s -X GET "${BRAZE_REST_ENDPOINT}/sessions/data_series?length=30&unit=day" \
  -H "Authorization: Bearer ${BRAZE_API_KEY}"

# Uninstalls (30 days)
curl -s -X GET "${BRAZE_REST_ENDPOINT}/kpi/uninstalls/data_series?length=30&unit=day" \
  -H "Authorization: Bearer ${BRAZE_API_KEY}"
```

### Step 8: Generate Report

Compile all findings into:
1. Data dictionary markdown
2. Segment inventory
3. Campaign/Canvas audit
4. Gap analysis
5. Recommendations

---

## Braze API Reference

### Authentication

All requests use Bearer token:
```
Authorization: Bearer {api_key}
```

### Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/custom_attributes` | GET | List all custom attributes |
| `/events/list` | GET | List all custom events |
| `/segments/list` | GET | List all segments |
| `/segments/details` | GET | Get segment definition |
| `/campaigns/list` | GET | List campaigns |
| `/campaigns/details` | GET | Get campaign details |
| `/campaigns/data_series` | GET | Get campaign stats |
| `/canvas/list` | GET | List canvases |
| `/canvas/details` | GET | Get canvas details |
| `/kpi/dau/data_series` | GET | Daily active users |
| `/kpi/mau/data_series` | GET | Monthly active users |
| `/sessions/data_series` | GET | Session counts |
| `/kpi/uninstalls/data_series` | GET | App uninstalls |
| `/kpi/new_users/data_series` | GET | New user signups |
| `/users/export/segment` | POST | Export segment users |
| `/users/export/ids` | POST | Export users by ID |

### Rate Limits

| Endpoint Type | Limit |
|---------------|-------|
| Data series | 250,000 requests/hour |
| User export | 2,500 requests/minute |
| Segment export | 1 concurrent request |

### Braze Clusters

| Cluster | REST Endpoint |
|---------|---------------|
| US-01 | https://rest.iad-01.braze.com |
| US-02 | https://rest.iad-02.braze.com |
| US-03 | https://rest.iad-03.braze.com |
| US-04 | https://rest.iad-04.braze.com |
| US-05 | https://rest.iad-05.braze.com |
| US-06 | https://rest.iad-06.braze.com |
| US-07 | https://rest.iad-07.braze.com |
| US-08 | https://rest.iad-08.braze.com |
| EU-01 | https://rest.fra-01.braze.eu |
| EU-02 | https://rest.fra-02.braze.eu |

---

## Output Schema

```json
{
  "client_id": "string",
  "discovery_date": "ISO timestamp",
  "braze_cluster": "string",
  "summary": {
    "custom_attributes": "number",
    "custom_events": "number",
    "segments": "number",
    "campaigns": "number",
    "canvases": "number",
    "dau_average": "number",
    "sessions_average": "number"
  },
  "custom_attributes": [
    {
      "name": "string",
      "data_type": "string",
      "status": "Active|Blocklisted",
      "category": "string"
    }
  ],
  "custom_events": [
    {
      "name": "string",
      "category": "string"
    }
  ],
  "segments": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "tags": ["string"]
    }
  ],
  "campaigns": [
    {
      "id": "string",
      "name": "string",
      "last_edited": "ISO timestamp",
      "is_api_campaign": "boolean"
    }
  ],
  "canvases": [
    {
      "id": "string",
      "name": "string",
      "last_edited": "ISO timestamp",
      "tags": ["string"]
    }
  ],
  "kpis": {
    "dau": {"average": "number", "min": "number", "max": "number"},
    "sessions": {"average": "number", "min": "number", "max": "number"},
    "uninstalls": {"total_30d": "number", "daily_average": "number"}
  },
  "gaps": ["string"],
  "recommendations": ["string"]
}
```

---

## Quality Criteria

This skill's output passes if:
- [ ] API connection successful
- [ ] Custom attributes retrieved and categorized
- [ ] Custom events retrieved and categorized
- [ ] At least 1 segment found
- [ ] KPIs populated (DAU, sessions)
- [ ] Report written to artifacts folder

---

## Failure Modes

| Mode | Trigger | Output | Escalation |
|------|---------|--------|------------|
| Auth Failed | 401 response | Error with troubleshooting | Check API key |
| Rate Limited | 429 response | Partial data + retry time | Wait and retry |
| Invalid Endpoint | Connection error | Error with cluster list | Verify endpoint |
| Empty Data | No attributes/events | Warning + check account | Verify account has data |

---

## Common Issues

### "Unauthorized" Error
- API key may be expired or revoked
- API key may lack required permissions
- Check Braze Dashboard → Settings → API Keys

### "405 Not Allowed" on Some Endpoints
- Some endpoints require POST instead of GET
- Check API documentation for correct method

### Missing Attributes/Events
- Braze only shows attributes/events with recent activity
- Very old or unused attributes may not appear

### Segment Size Not Available
- Braze API doesn't expose segment sizes directly
- Use `/users/export/segment` with limit to estimate

---

## Examples

### Minimal Discovery (Attributes + Events Only)

```bash
claude /run-skill braze-discovery --client B0bCCLkqvFhK7JCWKNR1 \
  --scope attributes,events
```

### Full Audit

```bash
claude /run-skill braze-discovery --client B0bCCLkqvFhK7JCWKNR1 \
  --scope attributes,events,segments,campaigns,canvases,kpis
```

---

## Changelog

### v1.0.0 (2026-01-30)
- Initial release
- Full attribute and event discovery
- Segment, campaign, canvas auditing
- KPI pulling (DAU, sessions, uninstalls)
- Automated categorization
- Gap analysis and recommendations

---

## Notes

- **Braze as CDP:** Many modern companies use Braze as their primary customer data platform, not just for marketing automation. This skill treats Braze as a data warehouse equivalent.

- **Currents for Deep Analytics:** For time-series analysis and historical trends, recommend enabling Braze Currents to export to a proper data warehouse.

- **PII Handling:** The EMAIL attribute is typically blocklisted for export. Use user IDs for segmentation.

- **Two-Sided Marketplaces:** For marketplaces, expect dual user profiles (e.g., Guest vs Host roles) tracked via custom attributes like `ROLE`.
