---
name: account-360
description: |
  Generate a full 360-degree account view combining data warehouse and CRM data.
  Use when asked to 'account overview', 'full account view', 'account 360',
  'account activity timeline', 'account summary', or 'deep dive on account'.
license: Proprietary
compatibility:
  - Snowflake MCP (user-snowflake)
  - BigQuery
  - Redshift
  - HubSpot MCP (user-hubspot)
  - Salesforce API
  - Pipedrive API
  - Zoho CRM API
  - Microsoft Dynamics API
metadata:
  author: mh1-engineering
  version: "2.0.0"
  status: active
  created: "2026-01-28"
  updated: "2026-01-28"
  estimated_runtime: "3-8min"
  max_runtime: "20min"
  estimated_cost: "$1.00"
  max_cost: "$3.00"
  client_facing: true
  requires_human_review: false
  tags:
    - account-intelligence
    - customer-360
    - activity-timeline
    - multi-crm
    - data-warehouse
allowed-tools: Read Write CallMcpTool
---

# Account 360 Skill

Generate a comprehensive 360-degree view of a customer account by combining data warehouse usage data with CRM activity (emails, calls, meetings, notes).

## When to Use

Use this skill when you need to:
- Prepare for an executive business review (EBR)
- Investigate account health or risk factors
- Understand full engagement history before renewal
- Build case studies with activity metrics
- Support CS handoffs with complete context

Do NOT use when:
- You need aggregate metrics across accounts (use portfolio-level skills)
- You only need CRM data (use CRM-specific skills)
- You only need usage data (use engagement-velocity skill)

---

## Configuration

```yaml
configuration:
  # CRM configuration
  crm_platform: hubspot | salesforce | pipedrive | zoho | dynamics
  
  # Data warehouse (optional - for usage/product data)
  warehouse:
    enabled: true | false
    type: snowflake | bigquery | redshift
    database: "{database_name}"
    schema: "{schema_name}"
    
    # Tables
    health_scores_table: "{table_name}"
    product_adoption_table: "{table_name}"  # optional
    usage_events_table: "{table_name}"  # optional
  
  # CRM field mapping
  crm_field_mapping:
    company_id: "hs_object_id" | "AccountId" | "id"
    company_name: "name" | "Name" | "company_name"
    domain: "domain" | "Website" | "company_domain"
    owner_field: "hubspot_owner_id" | "OwnerId" | "owner_id"
    revenue_field: "annualrevenue" | "AnnualRevenue" | "annual_revenue"
    industry: "industry" | "Industry" | "industry_type"
  
  # Data warehouse field mapping (if enabled)
  warehouse_field_mapping:
    account_id: "account_id" | "org_id"
    account_name: "account_name" | "org_name"
    revenue: "arr" | "annual_revenue" | "mrr"
    health_score: "health_score"
    health_status: "health_status"
    owner: "account_owner" | "cs_owner"
    report_date: "report_date" | "snapshot_date"
  
  # Activity object mapping
  activity_objects:
    emails: "emails" | "EmailMessage" | "activities"
    calls: "calls" | "Task" | "activities"
    meetings: "meetings" | "Event" | "activities"
    notes: "notes" | "Note" | "notes"
```

---

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `account_id` | string | yes* | - | Data warehouse account ID or CRM company ID |
| `account_name` | string | yes* | - | Company name for search if ID unknown |
| `include_contacts` | boolean | no | true | Include key contacts |
| `include_timeline` | boolean | no | true | Include activity timeline |
| `timeline_days` | number | no | 365 | Days of history for timeline |

*One of `account_id` or `account_name` required

---

## Platform-Specific Query Patterns

### Step 1: Resolve Account Identity

#### HubSpot Search

```json
{
  "filterGroups": [{
    "filters": [
      { "propertyName": "name", "operator": "CONTAINS_TOKEN", "value": "{account_name}" }
    ]
  }],
  "properties": ["name", "domain", "hs_object_id", "hubspot_owner_id", "annualrevenue"],
  "limit": 5
}
```

**MCP Tool:** `user-hubspot` → `hubspot_search` (object: companies)

#### Salesforce Search

```sql
SELECT Id, Name, Website, OwnerId, AnnualRevenue
FROM Account
WHERE Name LIKE '%{account_name}%'
ORDER BY AnnualRevenue DESC NULLS LAST
LIMIT 5
```

#### Data Warehouse Search (Generic)

```sql
SELECT {account_id}, {account_name}, {revenue}
FROM {database}.{schema}.{health_scores_table}
WHERE UPPER({account_name}) LIKE UPPER('%{account_name}%')
AND {report_date} = (SELECT MAX({report_date}) FROM {database}.{schema}.{health_scores_table})
ORDER BY {revenue} DESC
LIMIT 5
```

### Step 2: Get Account Profile

#### Data Warehouse Query

```sql
SELECT 
    {account_id},
    {account_name},
    {revenue} as current_revenue,
    {health_score},
    {health_status},
    {owner},
    {report_date} as snapshot_date
FROM {database}.{schema}.{health_scores_table}
WHERE {account_id} = '{account_id}'
AND {report_date} = (SELECT MAX({report_date}) FROM {database}.{schema}.{health_scores_table})
```

#### CRM Profile (HubSpot)

```json
{
  "filterGroups": [{
    "filters": [
      { "propertyName": "hs_object_id", "operator": "EQ", "value": "{company_id}" }
    ]
  }],
  "properties": [
    "name", "domain", "industry", "annualrevenue", 
    "hubspot_owner_id", "lifecyclestage", "hs_lead_status"
  ]
}
```

### Step 3: Get Product Adoption (if warehouse enabled)

```sql
SELECT 
    {account_id},
    platform,
    product_tier,
    features_enabled,
    activation_date,
    last_active_date
FROM {database}.{schema}.{product_adoption_table}
WHERE {account_id} = '{account_id}'
```

### Step 4: Get Usage Metrics (if warehouse enabled)

```sql
SELECT 
    DATE_TRUNC('month', event_date) as month,
    COUNT(*) as total_events,
    COUNT(DISTINCT user_id) as unique_users,
    SUM(CASE WHEN event_type = 'core_action' THEN 1 ELSE 0 END) as core_actions
FROM {database}.{schema}.{usage_events_table}
WHERE {account_id} = '{account_id}'
AND event_date >= DATEADD('day', -{timeline_days}, CURRENT_DATE())
GROUP BY 1
ORDER BY 1 DESC
```

### Step 5: Get Email Activity

#### HubSpot

```json
{
  "objectType": "emails",
  "associations": [{ "objectType": "companies", "objectId": "{company_id}" }],
  "properties": ["hs_email_subject", "hs_email_status", "hs_createdate", "hs_email_direction", "hubspot_owner_id"],
  "sorts": [{ "propertyName": "hs_createdate", "direction": "DESCENDING" }],
  "limit": 100
}
```

#### Salesforce

```sql
SELECT Id, Subject, Status, CreatedDate, Incoming, OwnerId
FROM EmailMessage
WHERE RelatedToId = '{account_id}'
ORDER BY CreatedDate DESC
LIMIT 100
```

### Step 6: Get Call Activity

#### HubSpot

```json
{
  "objectType": "calls",
  "associations": [{ "objectType": "companies", "objectId": "{company_id}" }],
  "properties": ["hs_call_title", "hs_call_duration", "hs_call_status", "hs_createdate", "hubspot_owner_id"],
  "sorts": [{ "propertyName": "hs_createdate", "direction": "DESCENDING" }],
  "limit": 100
}
```

#### Salesforce

```sql
SELECT Id, Subject, CallDurationInSeconds, Status, CreatedDate, OwnerId
FROM Task
WHERE WhatId = '{account_id}' AND TaskSubtype = 'Call'
ORDER BY CreatedDate DESC
LIMIT 100
```

### Step 7: Get Meeting Activity

#### HubSpot

```json
{
  "objectType": "meetings",
  "associations": [{ "objectType": "companies", "objectId": "{company_id}" }],
  "properties": ["hs_meeting_title", "hs_meeting_outcome", "hs_createdate", "hs_meeting_start_time", "hubspot_owner_id"],
  "sorts": [{ "propertyName": "hs_createdate", "direction": "DESCENDING" }],
  "limit": 100
}
```

#### Salesforce

```sql
SELECT Id, Subject, ActivityDateTime, DurationInMinutes, OwnerId
FROM Event
WHERE WhatId = '{account_id}'
ORDER BY ActivityDateTime DESC
LIMIT 100
```

### Step 8: Get Notes

#### HubSpot

```json
{
  "objectType": "notes",
  "associations": [{ "objectType": "companies", "objectId": "{company_id}" }],
  "properties": ["hs_note_body", "hs_createdate", "hubspot_owner_id"],
  "sorts": [{ "propertyName": "hs_createdate", "direction": "DESCENDING" }],
  "limit": 50
}
```

### Step 9: Get Key Contacts

#### HubSpot

```json
{
  "objectType": "contacts",
  "associations": [{ "objectType": "companies", "objectId": "{company_id}" }],
  "properties": ["email", "firstname", "lastname", "jobtitle", "phone", "hs_lead_status", "lifecyclestage"],
  "sorts": [{ "propertyName": "createdate", "direction": "DESCENDING" }]
}
```

#### Salesforce

```sql
SELECT Id, Email, FirstName, LastName, Title, Phone
FROM Contact
WHERE AccountId = '{account_id}'
ORDER BY CreatedDate DESC
```

### Step 10: Get Deal History

#### HubSpot

```json
{
  "objectType": "deals",
  "associations": [{ "objectType": "companies", "objectId": "{company_id}" }],
  "properties": ["dealname", "amount", "dealstage", "closedate", "pipeline", "hs_is_closed_won"],
  "sorts": [{ "propertyName": "closedate", "direction": "DESCENDING" }]
}
```

#### Salesforce

```sql
SELECT Id, Name, Amount, StageName, CloseDate, IsWon
FROM Opportunity
WHERE AccountId = '{account_id}'
ORDER BY CloseDate DESC
```

---

## Process

### Step 11: Build Activity Timeline (if include_timeline=true)

Merge all activities into chronological timeline:
1. Emails
2. Calls
3. Meetings
4. Notes
5. Usage spikes (significant event count changes)
6. Health score changes (from historical snapshots)

```python
timeline = []
for email in emails:
    timeline.append({
        "date": email["created_date"],
        "type": "email",
        "description": email["subject"],
        "owner": resolve_owner_name(email["owner_id"])
    })

# Add calls, meetings, notes similarly
# Sort by date descending
timeline.sort(key=lambda x: x["date"], reverse=True)
```

---

## Output Schema

```json
{
  "config": {
    "crm_platform": "string",
    "warehouse_enabled": "boolean"
  },
  "account": {
    "account_id": "string",
    "account_name": "string",
    "crm_company_id": "string",
    "domain": "string"
  },
  "financials": {
    "current_revenue": "number",
    "revenue_type": "ARR | MRR | Annual",
    "tier": "string",
    "industry": "string"
  },
  "health": {
    "health_score": "number",
    "health_status": "string",
    "owner": "string",
    "snapshot_date": "date"
  },
  "product_adoption": {
    "platform": "string",
    "product_tier": "string",
    "features": {
      "feature_name": "boolean"
    },
    "feature_count": "number"
  },
  "usage": {
    "total_events_ytd": "number",
    "unique_users_ytd": "number",
    "monthly_trend": [
      { "month": "date", "events": "number", "users": "number" }
    ],
    "usage_trend": "INCREASING | STABLE | DECLINING"
  },
  "engagement": {
    "emails": {
      "total_sent": "number",
      "total_received": "number",
      "last_email_date": "date"
    },
    "calls": {
      "total_calls": "number",
      "total_duration_minutes": "number",
      "connected_count": "number",
      "last_call_date": "date"
    },
    "meetings": {
      "total_meetings": "number",
      "completed_count": "number",
      "last_meeting_date": "date"
    },
    "notes": {
      "total_notes": "number",
      "last_note_date": "date"
    },
    "total_touchpoints": "number",
    "last_interaction_date": "date",
    "days_since_last_interaction": "number"
  },
  "contacts": [
    {
      "name": "string",
      "email": "string",
      "title": "string",
      "phone": "string",
      "is_primary": "boolean"
    }
  ],
  "deals": [
    {
      "deal_name": "string",
      "amount": "number",
      "stage": "string",
      "close_date": "date",
      "is_closed_won": "boolean"
    }
  ],
  "timeline": [
    {
      "date": "datetime",
      "type": "email | call | meeting | note | usage | health_change",
      "description": "string",
      "owner": "string"
    }
  ],
  "insights": ["string"],
  "risk_indicators": ["string"],
  "opportunities": ["string"]
}
```

---

## Quality Criteria

- [ ] Account successfully resolved from ID or name
- [ ] CRM data retrieved (and warehouse data if enabled)
- [ ] Activity counts match source systems
- [ ] Timeline sorted chronologically
- [ ] All date fields properly formatted
- [ ] Insights derived from actual data patterns

---

## Example Usage

**Get full 360 view for account:**
```
Generate account 360 for account_id="A-12345"
```

**Search by company name:**
```
Create account 360 view for "Uber" with full timeline
```

**Quick view without timeline:**
```
Account overview for A-98765 with include_timeline=false
```

---

## Sample Output

```json
{
  "config": {
    "crm_platform": "hubspot",
    "warehouse_enabled": true
  },
  "account": {
    "account_id": "A-12345",
    "account_name": "Acme Technologies",
    "crm_company_id": "9876543210",
    "domain": "acme.com"
  },
  "financials": {
    "current_revenue": 450000,
    "revenue_type": "ARR",
    "tier": "Enterprise",
    "industry": "Technology"
  },
  "health": {
    "health_score": 72,
    "health_status": "Healthy",
    "owner": "Sarah Johnson",
    "snapshot_date": "2026-01-27"
  },
  "product_adoption": {
    "platform": "Enterprise",
    "product_tier": "Pro",
    "features": {
      "analytics": true,
      "api_access": true,
      "sso": true,
      "custom_integrations": true,
      "advanced_reporting": true
    },
    "feature_count": 5
  },
  "usage": {
    "total_events_ytd": 2450000,
    "unique_users_ytd": 892,
    "monthly_trend": [
      { "month": "2026-01", "events": 245000, "users": 120 },
      { "month": "2025-12", "events": 312000, "users": 145 },
      { "month": "2025-11", "events": 298000, "users": 138 }
    ],
    "usage_trend": "STABLE"
  },
  "engagement": {
    "emails": {
      "total_sent": 1567,
      "total_received": 423,
      "last_email_date": "2026-01-25"
    },
    "calls": {
      "total_calls": 89,
      "total_duration_minutes": 445,
      "connected_count": 67,
      "last_call_date": "2026-01-20"
    },
    "meetings": {
      "total_meetings": 75,
      "completed_count": 68,
      "last_meeting_date": "2026-01-15"
    },
    "notes": {
      "total_notes": 234,
      "last_note_date": "2026-01-25"
    },
    "total_touchpoints": 1965,
    "last_interaction_date": "2026-01-25",
    "days_since_last_interaction": 2
  },
  "contacts": [
    {
      "name": "Jennifer Smith",
      "email": "jsmith@acme.com",
      "title": "VP Marketing",
      "phone": "+1-555-0123",
      "is_primary": true
    },
    {
      "name": "David Lee",
      "email": "dlee@acme.com",
      "title": "Director, Growth",
      "phone": "+1-555-0124",
      "is_primary": false
    }
  ],
  "deals": [
    {
      "deal_name": "Acme - Enterprise Renewal 2026",
      "amount": 450000,
      "stage": "Contract Sent",
      "close_date": "2026-03-15",
      "is_closed_won": false
    },
    {
      "deal_name": "Acme - Initial Contract",
      "amount": 380000,
      "stage": "Closed Won",
      "close_date": "2025-03-15",
      "is_closed_won": true
    }
  ],
  "timeline": [
    {
      "date": "2026-01-25T14:30:00Z",
      "type": "email",
      "description": "Sent renewal proposal follow-up",
      "owner": "Sarah Johnson"
    },
    {
      "date": "2026-01-20T11:00:00Z",
      "type": "call",
      "description": "Renewal discussion - 15 min call, discussed pricing",
      "owner": "Sarah Johnson"
    },
    {
      "date": "2026-01-15T09:00:00Z",
      "type": "meeting",
      "description": "QBR with VP Marketing - product roadmap review",
      "owner": "Sarah Johnson"
    }
  ],
  "insights": [
    "High engagement account with 1,567 emails and 75 meetings over relationship lifetime",
    "Full feature adoption (5/5 features) indicates strong product-market fit",
    "Usage trend stable despite December seasonality",
    "Renewal pending in Q1 - contract sent stage"
  ],
  "risk_indicators": [
    "December usage dip of 21% - monitor for continued decline",
    "Last meeting was 12 days ago - ensure pre-renewal touchpoint scheduled"
  ],
  "opportunities": [
    "API usage high - candidate for enterprise API tier upgrade",
    "Multiple campaigns active - potential expansion opportunity"
  ]
}
```

---

## Context Handling

| Input Size | Strategy | Model |
|------------|----------|-------|
| < 500 activities | Inline processing | Sonnet for synthesis |
| 500-2000 activities | Batch timeline construction | Haiku for extraction |
| > 2000 activities | Sample recent + aggregate old | Haiku + Sonnet |

---

## Client Setup Required

```yaml
# clients/{client_id}/config.yaml
account_360:
  crm_platform: hubspot
  
  warehouse:
    enabled: true
    type: snowflake
    database: ANALYTICS
    schema: REPORTING
    health_scores_table: ACCOUNT_HEALTH_DAILY
    product_adoption_table: PRODUCT_ADOPTION  # optional
    usage_events_table: USER_EVENTS  # optional
  
  crm_field_mapping:
    company_id: hs_object_id
    company_name: name
    domain: domain
    owner_field: hubspot_owner_id
    revenue_field: annualrevenue
    industry: industry
    
  warehouse_field_mapping:
    account_id: account_id
    account_name: account_name
    revenue: annual_revenue
    health_score: health_score
    health_status: health_status
    owner: account_owner
    report_date: snapshot_date
```

---

## Known Limitations

1. **CRM API rate limits** - may need pagination for high-activity accounts
2. **Timeline completeness** - depends on consistent activity logging
3. **Identity mapping** - requires account_id OR crm_company_id linkage
4. **Historical data** - warehouse snapshots may have limited history

---

## Notes

- Essential for EBR preparation - run 1 week before scheduled review
- Export to Google Slides for executive presentations
- Combine with at-risk-detection for health-focused deep dives
- Cache results for 24 hours to avoid duplicate API calls
