---
name: at-risk-detection
description: |
  Detect at-risk customer accounts with high revenue for proactive retention.
  Use when asked to 'find at-risk accounts', 'detect churn risk', 'identify retention targets',
  'check high-value at-risk', or 'prioritize accounts for outreach'.
license: Proprietary
compatibility:
  - Snowflake MCP
  - BigQuery
  - Salesforce
  - HubSpot MCP
metadata:
  author: mh1-engineering
  version: "2.0.0"
  status: active
  estimated_runtime: "1-3min"
  max_cost: "$0.50"
  client_facing: true
  requires_human_review: false
  tags:
    - retention
    - churn
    - customer-intelligence
    - platform-agnostic
allowed-tools: Read Write CallMcpTool
---

# At-Risk Detection Skill

Identify high-value accounts marked as at-risk for proactive retention outreach.

## When to Use

Use this skill when you need to:
- Find accounts at risk of churning
- Prioritize retention outreach by revenue
- Build at-risk account reports
- Identify patterns in at-risk accounts
- Support CS teams with early warning

---

## Platform Configuration

Configure this skill for your data environment:

```yaml
configuration:
  # Data source settings
  data_source: snowflake | bigquery | salesforce | hubspot
  
  # Table/object mappings
  customer_table: "{schema}.{table}"  # e.g., "analytics.customer_health"
  account_id_field: "account_id"
  account_name_field: "company_name"
  
  # Revenue configuration
  revenue_field: "arr" | "mrr" | "revenue" | "total_contract_value"
  revenue_type: "arr" | "mrr" | "one_time"
  
  # Health score configuration
  health_score_field: "health_score" | null  # null = calculate from signals
  health_status_field: "health_status"
  at_risk_status_value: "At-Risk"  # The value indicating at-risk status
  
  # Owner/assignment fields
  owner_field: "cs_owner" | "account_owner" | "owner_id"
  
  # Activity tracking
  last_activity_field: "last_activity_date" | null
  
  # Configurable thresholds
  thresholds:
    high_value_min: 10000      # Minimum revenue to flag as high-value
    at_risk_score_max: 40      # Max health score to consider at-risk
    inactive_days_warning: 30  # Days inactive to flag
    inactive_days_critical: 60 # Days inactive for critical alert
```

---

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `revenue_threshold` | number | no | config.thresholds.high_value_min | Minimum revenue to include |
| `limit` | number | no | 100 | Maximum accounts to return |
| `include_contacts` | boolean | no | false | Enrich with contact data |
| `date_field` | string | no | "snapshot_date" | Field for point-in-time filtering |

---

## Output Schema

```json
{
  "summary": {
    "total_at_risk_accounts": "number",
    "total_revenue_at_risk": "number",
    "avg_health_score": "number",
    "by_owner": {
      "owner_name": {
        "account_count": "number",
        "total_revenue": "number"
      }
    }
  },
  "accounts": [
    {
      "account_id": "string",
      "account_name": "string",
      "revenue": "number",
      "health_status": "At-Risk",
      "health_score": "number",
      "owner": "string",
      "last_activity_date": "date",
      "days_inactive": "number",
      "contacts": []
    }
  ],
  "recommendations": [
    "string"
  ]
}
```

---

## Process

### Step 1: Query At-Risk Accounts

Select the appropriate query template based on your configured data source:

#### Snowflake SQL

```sql
SELECT 
    {account_id_field} AS account_id,
    {account_name_field} AS account_name,
    {revenue_field} AS revenue,
    {health_status_field} AS health_status,
    {health_score_field} AS health_score,
    {owner_field} AS owner,
    {last_activity_field} AS last_activity_date,
    DATEDIFF(day, {last_activity_field}, CURRENT_DATE) AS days_inactive
FROM {customer_table}
WHERE {date_field} = CURRENT_DATE - 1
  AND {health_status_field} = '{at_risk_status_value}'
  AND {revenue_field} >= :revenue_threshold
ORDER BY {revenue_field} DESC
LIMIT :limit;
```

#### BigQuery SQL

```sql
SELECT 
    {account_id_field} AS account_id,
    {account_name_field} AS account_name,
    {revenue_field} AS revenue,
    {health_status_field} AS health_status,
    {health_score_field} AS health_score,
    {owner_field} AS owner,
    {last_activity_field} AS last_activity_date,
    DATE_DIFF(CURRENT_DATE(), {last_activity_field}, DAY) AS days_inactive
FROM `{project}.{dataset}.{table}`
WHERE {date_field} = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
  AND {health_status_field} = '{at_risk_status_value}'
  AND {revenue_field} >= @revenue_threshold
ORDER BY {revenue_field} DESC
LIMIT @limit;
```

#### Salesforce SOQL

```sql
SELECT 
    Id,
    Name,
    AnnualRevenue,
    Health_Status__c,
    Health_Score__c,
    OwnerId,
    Owner.Name,
    Last_Activity_Date__c
FROM Account
WHERE Health_Status__c = 'At-Risk'
  AND AnnualRevenue >= :revenueThreshold
ORDER BY AnnualRevenue DESC
LIMIT :recordLimit
```

#### HubSpot API Filter

```json
{
  "filterGroups": [{
    "filters": [
      {
        "propertyName": "health_status",
        "operator": "EQ",
        "value": "At-Risk"
      },
      {
        "propertyName": "annualrevenue",
        "operator": "GTE",
        "value": "{revenue_threshold}"
      }
    ]
  }],
  "properties": [
    "name", "annualrevenue", "health_status", 
    "health_score", "hubspot_owner_id", "notes_last_updated"
  ],
  "sorts": [{"propertyName": "annualrevenue", "direction": "DESCENDING"}],
  "limit": 100
}
```

### Step 2: Calculate Summary Statistics

```python
summary = {
    "total_at_risk_accounts": len(accounts),
    "total_revenue_at_risk": sum(a["revenue"] for a in accounts),
    "avg_health_score": sum(a["health_score"] for a in accounts) / len(accounts) if accounts else 0,
    "by_owner": group_by_owner(accounts)
}
```

### Step 3: Enrich with Contacts (Optional)

If `include_contacts=true`, fetch associated contacts from your CRM:

```python
for account in accounts:
    contacts = fetch_contacts_for_account(account["account_id"])
    account["contacts"] = contacts
```

### Step 4: Generate Recommendations

Based on patterns detected:
- Accounts with 0 activity in `inactive_days_warning`+ days → "Urgent: Re-engagement needed"
- Accounts with owner changes → "Review: Recent ownership change"
- Accounts with declining health score → "Monitor: Health trending down"
- High concentration with one owner → "Alert: Owner portfolio at risk"

---

## Example Usage

**Find at-risk accounts with revenue >= $50K:**
```
Use the at-risk-detection skill with revenue_threshold=50000
```

**Full at-risk report with contacts:**
```
Detect at-risk accounts with revenue >= $10K, include contacts
```

---

## Quality Criteria

- [ ] Query executes without error
- [ ] Revenue threshold correctly applied
- [ ] Summary statistics accurate
- [ ] Recommendations relevant to patterns
- [ ] No PII in output (use account IDs, not emails)

---

## Sample Output

```json
{
  "summary": {
    "total_at_risk_accounts": 240,
    "total_revenue_at_risk": 3200000,
    "avg_health_score": 32,
    "by_owner": {
      "Sarah Johnson": { "account_count": 45, "total_revenue": 890000 },
      "Mike Chen": { "account_count": 38, "total_revenue": 720000 }
    }
  },
  "accounts": [
    {
      "account_id": "A-12345",
      "account_name": "Acme Corp",
      "revenue": 156000,
      "health_status": "At-Risk",
      "health_score": 28,
      "owner": "Sarah Johnson",
      "last_activity_date": "2026-01-15",
      "days_inactive": 13
    }
  ],
  "recommendations": [
    "45 accounts have 0 activity in 30+ days - prioritize for immediate outreach",
    "Top 10 accounts represent $1.2M revenue - schedule executive reviews"
  ]
}
```

---

## Field Mapping Examples

### SaaS Company (Snowflake)
```yaml
configuration:
  data_source: snowflake
  customer_table: "analytics.customer_health_daily"
  account_id_field: "customer_id"
  revenue_field: "mrr"
  revenue_type: "mrr"
  health_score_field: "engagement_score"
  thresholds:
    high_value_min: 5000  # $5K MRR
```

### Enterprise Sales (Salesforce)
```yaml
configuration:
  data_source: salesforce
  customer_table: "Account"
  account_id_field: "Id"
  revenue_field: "AnnualRevenue"
  revenue_type: "arr"
  health_score_field: "Health_Score__c"
  thresholds:
    high_value_min: 100000  # $100K ARR
```

### Marketing Platform (HubSpot)
```yaml
configuration:
  data_source: hubspot
  account_id_field: "hs_object_id"
  revenue_field: "annualrevenue"
  health_score_field: "health_score"
  thresholds:
    high_value_min: 24000
```

---

## Notes

- Run weekly for retention planning
- Export to CSV for CS team distribution
- Integrate with Slack alerts for new at-risk flags
- Adjust thresholds based on your business model and customer segments
