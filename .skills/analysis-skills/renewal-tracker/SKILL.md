---
name: renewal-tracker
description: |
  Track and prioritize upcoming customer renewals from CRM pipeline.
  Use when asked to 'check renewals', 'track upcoming renewals', 'review renewal pipeline',
  'find renewals due soon', or 'prioritize renewal outreach'.
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
  max_cost: "$0.30"
  client_facing: true
  requires_human_review: false
  tags:
    - renewals
    - pipeline
    - retention
    - multi-crm
allowed-tools: Read Write CallMcpTool
---

# Renewal Tracker Skill

Track upcoming renewals in the CRM renewal pipeline to prioritize retention activities across multiple CRM platforms.

## When to Use

Use this skill when you need to:
- View renewals due within a specific timeframe
- Prioritize renewal outreach by value
- Identify renewals at risk of lapsing
- Generate renewal forecasts
- Support QBR preparation with renewal data

Do NOT use when:
- You need new sales pipeline data (use pipeline-analysis with sales pipeline)
- You need engagement metrics for renewal accounts (combine with engagement-velocity)

---

## Configuration

```yaml
configuration:
  crm_platform: hubspot | salesforce | pipedrive | zoho | dynamics
  
  pipelines:
    renewal: "{configured_renewal_pipeline_id}"
  
  stage_mapping:
    won: "closedwon" | "Closed Won" | "won"
    lost: "closedlost" | "Closed Lost" | "lost"
    at_risk: "at_risk" | "At Risk" | "churning"
    outreach: "renewal_outreach" | "Renewal Outreach"
    contract_sent: "contract_sent" | "Contract Sent"
    verbal_commit: "verbal_commit" | "Verbal Commit"
  
  field_mapping:
    deal_name: "dealname" | "Name" | "title"
    deal_value: "amount" | "Amount" | "value"
    arr_field: "arr" | "ARR__c" | "annual_value"
    close_date: "closedate" | "CloseDate" | "expected_close_date"
    deal_stage: "dealstage" | "StageName" | "stage"
    owner_field: "hubspot_owner_id" | "OwnerId" | "owner_id"
    days_until_renewal: "days_until_renewal" | "Days_Until_Renewal__c" | "days_to_close"
    is_closed: "hs_is_closed" | "IsClosed" | "status"
  
  # Urgency thresholds (in days)
  urgency_thresholds:
    critical: 7
    high: 14
    medium: 30
```

---

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `days_until` | number | no | 30 | Show renewals due within this many days |
| `limit` | number | no | 100 | Maximum deals to return |
| `pipeline_id` | string | no | from config | Override default renewal pipeline ID |

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
  "sorts": [{ "propertyName": "amount", "direction": "DESCENDING" }],
  "properties": [
    "dealname", "amount", "arr", "dealstage", 
    "closedate", "days_until_renewal", "hubspot_owner_id"
  ],
  "limit": 100
}
```

**MCP Tool:** `user-hubspot` → `hubspot_search` (object: deals)

### Salesforce

```sql
SELECT Id, Name, Amount, ARR__c, StageName, CloseDate, 
       OwnerId, Owner.Name, DATEDIFF(CloseDate, TODAY()) as DaysUntilRenewal
FROM Opportunity
WHERE RecordType.Name = 'Renewal'
  AND IsClosed = false
  AND CloseDate <= NEXT_N_DAYS:{days_until}
ORDER BY Amount DESC
LIMIT 100
```

**API Endpoint:** `/services/data/v58.0/query?q={SOQL}`

### Pipedrive

```
GET /deals
Parameters:
  pipeline_id: {renewal_pipeline_id}
  status: open
  sort: value DESC
  limit: 100
```

Filter in application by expected close date:
```python
renewals = [d for d in deals if days_until_close(d) <= days_until]
```

### Zoho CRM

```json
{
  "module": "Deals",
  "criteria": "(Pipeline:equals:{renewal_pipeline_id}) and (Stage:not_in:(Closed Won,Closed Lost)) and (Closing_Date:between:{today},{future_date})",
  "fields": ["Deal_Name", "Amount", "ARR", "Stage", "Closing_Date", "Owner", "Days_Until_Renewal"],
  "sort_by": "Amount",
  "sort_order": "desc",
  "per_page": 100
}
```

### Microsoft Dynamics

```
GET /opportunities
$filter: _transactioncurrencyid_value eq '{renewal_type_id}' 
  and statecode eq 0 
  and estimatedclosedate le {future_date}
$select: name,estimatedvalue,stepname,estimatedclosedate,_ownerid_value
$orderby: estimatedvalue desc
$top: 100
```

---

## Process

### Step 1: Load Configuration

```python
config = load_client_config(client_id)
crm = config["crm_platform"]
renewal_pipeline_id = config["pipelines"]["renewal"]
field_map = config["field_mapping"]
urgency = config["urgency_thresholds"]
```

### Step 2: Query Renewal Pipeline

Execute platform-specific query.

### Step 3: Normalize and Filter by Days Until Renewal

```python
def normalize_renewal(deal, field_map):
    return {
        "deal_name": deal.get(field_map["deal_name"]),
        "amount": float(deal.get(field_map["deal_value"], 0)),
        "arr": float(deal.get(field_map["arr_field"], 0)),
        "stage": deal.get(field_map["deal_stage"]),
        "close_date": deal.get(field_map["close_date"]),
        "days_until_renewal": calculate_days_until(deal, field_map),
        "owner_id": deal.get(field_map["owner_field"])
    }

# Filter to renewals within specified window
upcoming_renewals = [
    deal for deal in deals 
    if deal["days_until_renewal"] is not None 
    and deal["days_until_renewal"] <= days_until
]

# Sort by urgency (days until, then amount)
upcoming_renewals.sort(key=lambda x: (x["days_until_renewal"], -x["amount"]))
```

### Step 4: Categorize by Urgency

```python
for deal in upcoming_renewals:
    days = deal["days_until_renewal"]
    if days <= urgency["critical"]:
        deal["urgency"] = "CRITICAL"
    elif days <= urgency["high"]:
        deal["urgency"] = "HIGH"
    elif days <= urgency["medium"]:
        deal["urgency"] = "MEDIUM"
    else:
        deal["urgency"] = "LOW"
```

### Step 5: Generate Summary Statistics

```python
summary = {
    "total_renewals": len(upcoming_renewals),
    "total_value": sum(d["amount"] for d in upcoming_renewals),
    "total_arr": sum(d["arr"] for d in upcoming_renewals),
    "by_urgency": {
        "critical": {"count": count, "value": sum_value},
        "high": {"count": count, "value": sum_value},
        "medium": {"count": count, "value": sum_value},
        "low": {"count": count, "value": sum_value}
    },
    "by_stage": group_by("stage")
}
```

### Step 6: Generate Recommendations

Based on renewal status:
- **CRITICAL** renewals → Escalate immediately, executive outreach
- **HIGH** renewals → Schedule renewal calls this week
- **MEDIUM** renewals → Begin renewal conversations
- **Stalled stages** → Flag deals not progressing

---

## Output Schema

```json
{
  "config": {
    "crm_platform": "string",
    "renewal_pipeline_id": "string"
  },
  "query_params": {
    "days_until": "number",
    "as_of_date": "date"
  },
  "summary": {
    "total_renewals": "number",
    "total_value": "number",
    "total_arr": "number",
    "by_urgency": {
      "critical": { "count": "number", "value": "number" },
      "high": { "count": "number", "value": "number" },
      "medium": { "count": "number", "value": "number" },
      "low": { "count": "number", "value": "number" }
    },
    "by_stage": [
      { "stage": "string", "count": "number", "value": "number" }
    ]
  },
  "renewals": [
    {
      "deal_name": "string",
      "amount": "number",
      "arr": "number",
      "stage": "string",
      "close_date": "date",
      "days_until_renewal": "number",
      "urgency": "CRITICAL | HIGH | MEDIUM | LOW",
      "owner_id": "string",
      "owner_name": "string"
    }
  ],
  "alerts": ["string"],
  "recommendations": ["string"]
}
```

---

## Example Usage

**Check renewals due this month:**
```
Track renewals due within 30 days
```

**Urgent renewals only:**
```
Use renewal-tracker skill with days_until=7 to find critical renewals
```

**Quarterly renewal forecast:**
```
Show all renewals due within 90 days
```

---

## Sample Output

```json
{
  "config": {
    "crm_platform": "hubspot",
    "renewal_pipeline_id": "renewals"
  },
  "query_params": {
    "days_until": 30,
    "as_of_date": "2026-01-27"
  },
  "summary": {
    "total_renewals": 23,
    "total_value": 1270000,
    "total_arr": 1270000,
    "by_urgency": {
      "critical": { "count": 3, "value": 185000 },
      "high": { "count": 5, "value": 320000 },
      "medium": { "count": 15, "value": 765000 },
      "low": { "count": 0, "value": 0 }
    },
    "by_stage": [
      { "stage": "Renewal Outreach", "count": 8, "value": 450000 },
      { "stage": "Contract Sent", "count": 6, "value": 380000 },
      { "stage": "Verbal Commit", "count": 5, "value": 290000 },
      { "stage": "At Risk", "count": 4, "value": 150000 }
    ]
  },
  "renewals": [
    {
      "deal_name": "Enterprise Client - Annual Renewal",
      "amount": 748800,
      "arr": 748800,
      "stage": "Contract Sent",
      "close_date": "2026-02-15",
      "days_until_renewal": 19,
      "urgency": "MEDIUM",
      "owner_id": "12345678",
      "owner_name": "Sarah Johnson"
    },
    {
      "deal_name": "Acme Corp - Q1 Renewal",
      "amount": 85000,
      "arr": 85000,
      "stage": "At Risk",
      "close_date": "2026-02-01",
      "days_until_renewal": 5,
      "urgency": "CRITICAL",
      "owner_id": "23456789",
      "owner_name": "Mike Chen"
    }
  ],
  "alerts": [
    "3 renewals worth $185K are CRITICAL (due within 7 days)",
    "4 renewals in 'At Risk' stage totaling $150K need immediate attention"
  ],
  "recommendations": [
    "Escalate CRITICAL renewals to leadership for executive outreach",
    "Schedule renewal calls for HIGH urgency deals this week",
    "Review 'At Risk' deals with account owners - develop save plans",
    "$1.27M in renewals due within 30 days - ensure adequate coverage"
  ]
}
```

---

## Quality Criteria

- [ ] CRM query executes without error
- [ ] Deals filtered correctly by days_until
- [ ] Urgency levels assigned correctly per configured thresholds
- [ ] Summary totals match detail records
- [ ] Alerts relevant to data patterns

---

## Client Setup Required

```yaml
# clients/{client_id}/config.yaml
renewal_tracker:
  crm_platform: hubspot
  
  pipelines:
    renewal: "your-renewal-pipeline-id"
  
  field_mapping:
    deal_name: dealname
    deal_value: amount
    arr_field: arr
    close_date: closedate
    deal_stage: dealstage
    owner_field: hubspot_owner_id
    days_until_renewal: days_until_renewal
    is_closed: hs_is_closed
    
  stage_mapping:
    won: closedwon
    lost: closedlost
    at_risk: at_risk
    
  urgency_thresholds:
    critical: 7
    high: 14
    medium: 30
```

---

## Known Limitations

1. **days_until_renewal field** - if not available, calculated from close_date
2. **No health score context** - combine with at-risk-detection for full picture
3. **Owner name resolution** - requires separate API call on most platforms

---

## Notes

- Run weekly for renewal planning meetings
- Export to spreadsheet for CS team distribution
- Combine with at-risk-detection to correlate health scores
- Set up Slack alerts for new CRITICAL renewals
