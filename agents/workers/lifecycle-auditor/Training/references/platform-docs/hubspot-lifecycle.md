# Platform Reference: HubSpot Lifecycle Stages

## Overview

**Platform**: HubSpot CRM
**Connection Method**: MCP Server (hubspot)
**Rate Limits**: 100 requests/10 seconds (Private App)

## Authentication

```yaml
# Required credentials
credentials:
  - name: HUBSPOT_ACCESS_TOKEN
    type: private_app_token
    source: environment
    scopes:
      - crm.objects.contacts.read
      - crm.objects.contacts.write
      - crm.objects.companies.read
      - crm.objects.deals.read
```

## Lifecycle Stage Model

### Default Stages (in order)

| Stage | Internal Value | Description |
|-------|----------------|-------------|
| Subscriber | subscriber | Opted in to communications |
| Lead | lead | Showed interest, not yet qualified |
| Marketing Qualified Lead | marketingqualifiedlead | Met marketing criteria |
| Sales Qualified Lead | salesqualifiedlead | Accepted by sales |
| Opportunity | opportunity | Active deal in pipeline |
| Customer | customer | Closed-won deal |
| Evangelist | evangelist | Active promoter/referrer |
| Other | other | Does not fit standard stages |

### Custom Stages

HubSpot allows custom lifecycle stages in Enterprise. Check for custom values:

```python
# Discover all lifecycle stage values in use
stages = mcp.hubspot.get_property_values("lifecyclestage")
# Returns: ["subscriber", "lead", "marketingqualifiedlead", "custom_stage_1", ...]
```

## Key Endpoints/Operations

### Operation 1: Get Contacts by Lifecycle Stage

**Purpose**: Retrieve contacts filtered by lifecycle stage for analysis

**Request**:
```python
# Via MCP
result = mcp.hubspot.search_contacts(
    filters=[
        {
            "propertyName": "lifecyclestage",
            "operator": "EQ",
            "value": "customer"
        }
    ],
    properties=["email", "firstname", "lastname", "company", "lifecyclestage", "createdate"],
    limit=100
)
```

**Response**:
```json
{
  "results": [
    {
      "id": "12345",
      "properties": {
        "email": "jane@acme.com",
        "firstname": "Jane",
        "lastname": "Doe",
        "company": "Acme Corp",
        "lifecyclestage": "customer",
        "createdate": "2024-03-15T10:30:00.000Z"
      }
    }
  ],
  "paging": {
    "next": {
      "after": "100"
    }
  }
}
```

**Common Errors**:
| Code | Meaning | Solution |
|------|---------|----------|
| 401 | Unauthorized | Check token, refresh if needed |
| 429 | Rate limited | Implement exponential backoff |
| 400 | Invalid filter | Check property names and operators |

### Operation 2: Get Lifecycle Stage Distribution

**Purpose**: Count contacts in each lifecycle stage

**Request**:
```python
# Aggregate query via search
stages = ["subscriber", "lead", "marketingqualifiedlead", "salesqualifiedlead", "opportunity", "customer"]
distribution = {}

for stage in stages:
    count = mcp.hubspot.search_contacts(
        filters=[{"propertyName": "lifecyclestage", "operator": "EQ", "value": stage}],
        properties=["email"],
        limit=0,  # We only need the count
        count_only=True
    )
    distribution[stage] = count["total"]
```

**Response**:
```json
{
  "subscriber": 450,
  "lead": 320,
  "marketingqualifiedlead": 180,
  "salesqualifiedlead": 120,
  "opportunity": 85,
  "customer": 95
}
```

### Operation 3: Update Contact Lifecycle Stage

**Purpose**: Progress a contact to a new lifecycle stage (execute mode)

**Request**:
```python
# Update single contact
mcp.hubspot.update_contact(
    contact_id="12345",
    properties={
        "lifecyclestage": "salesqualifiedlead",
        "hs_lifecyclestage_salesqualifiedlead_date": "2024-06-15T10:30:00.000Z"
    }
)

# Batch update (more efficient)
mcp.hubspot.batch_update_contacts(
    inputs=[
        {"id": "12345", "properties": {"lifecyclestage": "salesqualifiedlead"}},
        {"id": "12346", "properties": {"lifecyclestage": "salesqualifiedlead"}}
    ]
)
```

**Important**: Lifecycle stages can only progress forward by default. Going backward requires removing the stage first (API limitation).

## Data Models

### Contact Object (Lifecycle-relevant fields)

```json
{
  "id": "string",
  "properties": {
    "email": "string (required)",
    "firstname": "string",
    "lastname": "string",
    "company": "string",
    "lifecyclestage": "enum (see stages above)",
    "createdate": "datetime",
    "hs_lifecyclestage_subscriber_date": "datetime",
    "hs_lifecyclestage_lead_date": "datetime",
    "hs_lifecyclestage_marketingqualifiedlead_date": "datetime",
    "hs_lifecyclestage_salesqualifiedlead_date": "datetime",
    "hs_lifecyclestage_opportunity_date": "datetime",
    "hs_lifecyclestage_customer_date": "datetime",
    "hs_analytics_source": "string (original source)",
    "hs_analytics_last_visit_timestamp": "datetime"
  },
  "associations": {
    "companies": ["string (company IDs)"],
    "deals": ["string (deal IDs)"]
  }
}
```

### Stage Transition Timestamps

HubSpot automatically tracks when a contact entered each stage:

| Property | Description |
|----------|-------------|
| `hs_lifecyclestage_subscriber_date` | When became subscriber |
| `hs_lifecyclestage_lead_date` | When became lead |
| `hs_lifecyclestage_marketingqualifiedlead_date` | When became MQL |
| `hs_lifecyclestage_salesqualifiedlead_date` | When became SQL |
| `hs_lifecyclestage_opportunity_date` | When became opportunity |
| `hs_lifecyclestage_customer_date` | When became customer |

Use these for velocity calculations:
```python
velocity_mql_to_sql = (
    contact["hs_lifecyclestage_salesqualifiedlead_date"] -
    contact["hs_lifecyclestage_marketingqualifiedlead_date"]
).days
```

## Query Patterns

### Pattern 1: Funnel Distribution Query

```python
# Get stage distribution for lifecycle audit
def get_funnel_distribution(limit=5000):
    stages = ["subscriber", "lead", "marketingqualifiedlead",
              "salesqualifiedlead", "opportunity", "customer"]

    distribution = {}
    for stage in stages:
        result = mcp.hubspot.search_contacts(
            filters=[{"propertyName": "lifecyclestage", "operator": "EQ", "value": stage}],
            properties=["email"],
            limit=0,
            count_only=True
        )
        distribution[stage] = result.get("total", 0)

    return distribution
```

### Pattern 2: Cohort Query by Create Date

```python
# Get contacts created in a specific date range (for cohort analysis)
def get_cohort(start_date, end_date, limit=1000):
    return mcp.hubspot.search_contacts(
        filters=[
            {"propertyName": "createdate", "operator": "GTE", "value": start_date},
            {"propertyName": "createdate", "operator": "LTE", "value": end_date}
        ],
        properties=[
            "email", "lifecyclestage", "createdate",
            "hs_lifecyclestage_marketingqualifiedlead_date",
            "hs_lifecyclestage_salesqualifiedlead_date",
            "hs_lifecyclestage_customer_date"
        ],
        limit=limit
    )
```

### Pattern 3: At-Risk Customer Identification

```python
# Find customers with no recent activity (potential churn)
def get_at_risk_customers(inactive_days=45):
    cutoff_date = datetime.now() - timedelta(days=inactive_days)

    return mcp.hubspot.search_contacts(
        filters=[
            {"propertyName": "lifecyclestage", "operator": "EQ", "value": "customer"},
            {"propertyName": "hs_analytics_last_visit_timestamp", "operator": "LTE",
             "value": cutoff_date.isoformat()}
        ],
        properties=["email", "firstname", "lastname", "company",
                   "hs_analytics_last_visit_timestamp"],
        limit=500
    )
```

## Best Practices

1. **Always paginate** - HubSpot limits results to 100 per request; use `after` cursor
2. **Use batch operations** - Group updates to reduce API calls (max 100 per batch)
3. **Request only needed properties** - Reduces response size and improves speed
4. **Handle rate limits gracefully** - Implement exponential backoff (10s burst limit)
5. **Cache stage values** - Lifecycle stages rarely change; cache for 24 hours

## MH1-Specific Usage

### Via MCP

```python
# Standard lifecycle audit query
from lib.mcp_client import HubSpotClient

hubspot = HubSpotClient()

# Get all contacts with lifecycle data
contacts = hubspot.get_all_contacts(
    properties=[
        "email", "lifecyclestage", "createdate",
        "hs_lifecyclestage_lead_date",
        "hs_lifecyclestage_marketingqualifiedlead_date",
        "hs_lifecyclestage_customer_date",
        "hs_analytics_last_visit_timestamp"
    ],
    limit=5000  # Max for audit
)
```

### Caching Strategy

```python
# Check cache before API call
from lib.cache import get_cached, set_cached

def get_contacts_for_audit(tenant_id, max_age_hours=24):
    cache_key = f"hubspot_contacts_{tenant_id}"

    cached = get_cached(cache_key, max_age_hours=max_age_hours)
    if cached:
        return {"data": cached, "source": "cache"}

    fresh = hubspot.get_all_contacts(...)
    set_cached(cache_key, fresh)
    return {"data": fresh, "source": "api"}
```

## Troubleshooting

### Issue: Missing lifecycle stage data

**Symptoms**: Many contacts have null `lifecyclestage`

**Cause**: Contacts imported without stage assignment, or created via non-HubSpot forms

**Solution**:
1. Check import history for contacts without stages
2. Set default lifecycle stage in HubSpot settings
3. Use workflow to auto-assign based on source

### Issue: Stage progression blocked

**Symptoms**: Cannot move contact backward in lifecycle

**Cause**: HubSpot enforces forward-only progression by default

**Solution**:
1. Go to Settings > Properties > Contact Properties > Lifecycle Stage
2. Uncheck "Only allow lifecycle stage to move forward"
3. Or: Clear the stage first, then set new value

### Issue: Inconsistent stage timestamps

**Symptoms**: Stage date is later than current date or illogical sequence

**Cause**: Manual stage changes don't always update timestamp properties

**Solution**:
1. Always update stage via API with explicit timestamp
2. Use workflow to sync stage and timestamp on change

## Changelog

| Date | Change | Impact |
|------|--------|--------|
| 2024-01 | Added `other` as default stage option | May appear in distribution |
| 2024-06 | Rate limit increased to 100/10s | Faster queries possible |
| 2025-01 | Custom stage support expanded | Check for non-standard stages |
