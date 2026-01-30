---
name: pipeline-analysis
description: |
  Analyze sales and renewal pipelines for deal velocity and revenue forecasting.
  Use when asked to 'analyze pipeline', 'check deals', 'review sales funnel', 
  'forecast revenue', or 'check renewal pipeline'.
license: Proprietary
compatibility:
  - HubSpot MCP (user-hubspot)
  - Salesforce API
  - Pipedrive API
  - Zoho CRM API
  - Microsoft Dynamics API
metadata:
  author: mh1-engineering
  version: "2.0.0"
  status: active
  estimated_runtime: "30s-2min"
  max_cost: "$0.25"
  client_facing: true
  requires_human_review: false
  tags:
    - sales
    - pipeline
    - deals
    - revenue
    - multi-crm
allowed-tools: Read Write CallMcpTool
---

# Pipeline Analysis Skill

Analyze sales and renewal pipelines for deal visibility, velocity metrics, and revenue forecasting across multiple CRM platforms.

## When to Use

Use this skill when you need to:
- View open deals in sales pipeline
- Track renewal pipeline status
- Analyze deals by owner/rep
- Calculate pipeline velocity
- Forecast revenue by close date
- Identify stalled deals

---

## Configuration

Before running this skill, configure the CRM platform and pipeline settings:

```yaml
configuration:
  crm_platform: hubspot | salesforce | pipedrive | zoho | dynamics
  
  pipelines:
    sales: "{configured_pipeline_id}"
    renewal: "{configured_pipeline_id}"
  
  stage_mapping:
    won: "closedwon" | "Closed Won" | "won" | "WON"
    lost: "closedlost" | "Closed Lost" | "lost" | "LOST"
    open: "open" | "Open" | "In Progress"
  
  field_mapping:
    deal_name: "dealname" | "Name" | "title" | "deal_name"
    deal_value: "amount" | "Amount" | "value" | "deal_value"
    close_date: "closedate" | "CloseDate" | "expected_close_date"
    deal_stage: "dealstage" | "StageName" | "stage" | "pipeline_stage"
    owner_field: "hubspot_owner_id" | "OwnerId" | "owner_id" | "user_id"
    is_closed: "hs_is_closed" | "IsClosed" | "status"
    probability: "hs_deal_stage_probability" | "Probability" | "probability"
    created_date: "createdate" | "CreatedDate" | "add_time"
```

---

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `pipeline_type` | string | no | "both" | "sales", "renewal", or "both" |
| `group_by` | string | no | "stage" | "stage", "owner", "month" |
| `include_closed` | boolean | no | false | Include closed won/lost deals |
| `days_lookback` | number | no | 90 | For velocity calculations |
| `pipeline_id` | string | no | from config | Override default pipeline ID |

---

## Platform-Specific Query Patterns

### HubSpot

```json
{
  "filterGroups": [{
    "filters": [
      { "propertyName": "pipeline", "operator": "EQ", "value": "{pipeline_id}" },
      { "propertyName": "hs_is_closed", "operator": "EQ", "value": "false" }
    ]
  }],
  "properties": [
    "dealname", "amount", "closedate", "dealstage", 
    "hubspot_owner_id", "createdate", "hs_deal_stage_probability"
  ],
  "sorts": [{ "propertyName": "amount", "direction": "DESCENDING" }],
  "limit": 100
}
```

**MCP Tool:** `user-hubspot` → `hubspot_search`

### Salesforce

```sql
SELECT Id, Name, Amount, StageName, CloseDate, OwnerId, 
       CreatedDate, Probability, IsClosed, IsWon
FROM Opportunity
WHERE Pipeline__c = '{pipeline_id}'
  AND IsClosed = false
ORDER BY Amount DESC
LIMIT 100
```

**API Endpoint:** `/services/data/v58.0/query?q={SOQL}`

### Pipedrive

```
GET /deals
Parameters:
  pipeline_id: {pipeline_id}
  status: open
  sort: value DESC
  limit: 100
```

**API Endpoint:** `https://api.pipedrive.com/v1/deals`

### Zoho CRM

```json
{
  "module": "Deals",
  "criteria": "(Pipeline:equals:{pipeline_id}) and (Stage:not_equals:Closed Won) and (Stage:not_equals:Closed Lost)",
  "fields": ["Deal_Name", "Amount", "Closing_Date", "Stage", "Owner", "Created_Time"],
  "sort_by": "Amount",
  "sort_order": "desc",
  "per_page": 100
}
```

**API Endpoint:** `https://www.zohoapis.com/crm/v3/Deals/search`

### Microsoft Dynamics

```
GET /opportunities
$filter: _parentaccountid_value eq '{pipeline_id}' and statecode eq 0
$select: name,estimatedvalue,estimatedclosedate,stepname,_ownerid_value,createdon
$orderby: estimatedvalue desc
$top: 100
```

**API Endpoint:** `/api/data/v9.2/opportunities`

---

## Process

### Step 1: Load Configuration

```python
config = load_client_config(client_id)
crm = config["crm_platform"]
sales_pipeline_id = config["pipelines"]["sales"]
renewal_pipeline_id = config["pipelines"]["renewal"]
field_map = config["field_mapping"]
```

### Step 2: Query Sales Pipeline

Execute platform-specific query using the appropriate pattern above.

### Step 3: Query Renewal Pipeline (if pipeline_type != "sales")

Execute platform-specific query for renewal pipeline.

### Step 4: Normalize Field Names

```python
def normalize_deal(deal, field_map):
    return {
        "deal_name": deal.get(field_map["deal_name"]),
        "amount": float(deal.get(field_map["deal_value"], 0)),
        "close_date": deal.get(field_map["close_date"]),
        "stage": deal.get(field_map["deal_stage"]),
        "owner_id": deal.get(field_map["owner_field"]),
        "created_date": deal.get(field_map["created_date"]),
        "probability": float(deal.get(field_map["probability"], 0))
    }
```

### Step 5: Calculate Metrics

```python
# Pipeline totals
total_sales_value = sum(d["amount"] for d in sales_deals)
total_renewal_value = sum(d["amount"] for d in renewal_deals)

# Weighted pipeline (by probability)
weighted_value = sum(d["amount"] * d["probability"] for d in deals)

# By stage
by_stage = group_and_sum(deals, "stage", "amount")

# By owner
by_owner = group_and_sum(deals, "owner_id", "amount")

# Velocity (avg days in pipeline)
avg_age = sum(days_since_create(d) for d in deals) / len(deals)
```

### Step 6: Generate Report

---

## Output Schema

```json
{
  "config": {
    "crm_platform": "string",
    "sales_pipeline_id": "string",
    "renewal_pipeline_id": "string"
  },
  "summary": {
    "sales_pipeline": {
      "total_deals": "number",
      "total_value": "number",
      "weighted_value": "number",
      "avg_deal_size": "number"
    },
    "renewal_pipeline": {
      "total_deals": "number", 
      "total_value": "number",
      "due_this_month": "number",
      "due_next_month": "number"
    },
    "velocity": {
      "avg_days_in_pipeline": "number",
      "deals_over_90_days": "number"
    }
  },
  "by_stage": [
    { "stage": "string", "deal_count": "number", "total_value": "number" }
  ],
  "by_owner": [
    { "owner": "string", "deal_count": "number", "total_value": "number" }
  ],
  "top_deals": [
    {
      "deal_name": "string",
      "amount": "number",
      "close_date": "date",
      "stage": "string",
      "owner": "string",
      "days_open": "number"
    }
  ],
  "alerts": [
    "string"
  ]
}
```

---

## Example Usage

**Full pipeline analysis:**
```
Analyze both sales and renewal pipelines, group by owner
```

**Renewal focus:**
```
Check renewal pipeline, show deals closing this month
```

**Stalled deals:**
```
Find deals that have been open for more than 60 days
```

---

## Sample Output

```json
{
  "config": {
    "crm_platform": "hubspot",
    "sales_pipeline_id": "default",
    "renewal_pipeline_id": "renewals"
  },
  "summary": {
    "sales_pipeline": {
      "total_deals": 47,
      "total_value": 1300000,
      "weighted_value": 845000,
      "avg_deal_size": 27659
    },
    "renewal_pipeline": {
      "total_deals": 23,
      "total_value": 1270000,
      "due_this_month": 320000,
      "due_next_month": 450000
    }
  },
  "by_owner": [
    { "owner": "Sarah Johnson", "deal_count": 12, "total_value": 456000 },
    { "owner": "Mike Chen", "deal_count": 8, "total_value": 312000 }
  ],
  "top_deals": [
    {
      "deal_name": "Enterprise Client - Annual Renewal",
      "amount": 748800,
      "close_date": "2026-02-15",
      "stage": "Contract Sent",
      "owner": "Sarah Johnson",
      "days_open": 45
    }
  ],
  "alerts": [
    "5 deals over 90 days old - review for stall",
    "$320K in renewals due this month - ensure coverage"
  ]
}
```

---

## Quality Criteria

- [ ] Configuration loaded correctly for CRM platform
- [ ] Both pipelines queried successfully (if applicable)
- [ ] Amounts sum correctly
- [ ] Owner mapping resolves to names
- [ ] Close dates parsed correctly
- [ ] Alerts relevant to data

---

## Client Setup Required

Before first use, ensure client configuration exists at `clients/{client_id}/config.yaml`:

```yaml
crm:
  platform: hubspot  # or salesforce, pipedrive, zoho, dynamics
  credentials_key: "{client_id}_crm"
  
pipelines:
  sales:
    id: "your-sales-pipeline-id"
    name: "Sales Pipeline"
  renewal:
    id: "your-renewal-pipeline-id"
    name: "Renewal Pipeline"

stage_mapping:
  won: ["closedwon", "Closed Won"]
  lost: ["closedlost", "Closed Lost"]
  
field_overrides: {}  # Optional custom field mappings
```

---

## Notes

- Pipeline IDs must be configured per client
- Owner ID to name mapping varies by CRM platform
- Deal stages vary by pipeline configuration
- For Salesforce, Pipeline__c may be a custom field - adjust query accordingly
