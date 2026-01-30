---
name: churn-prediction
description: |
  Identify contacts and accounts at risk of churning using health status analysis and engagement signals.
  Use when asked to 'predict churn', 'find churning accounts', 'identify churn risk',
  'subscription churn report', or 'who is about to churn'.
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
  created: "2026-01-27"
  updated: "2026-01-28"
  estimated_runtime: "2-5min"
  max_runtime: "15min"
  estimated_cost: "$0.30"
  max_cost: "$1.00"
  client_facing: true
  requires_human_review: false
  tags:
    - retention
    - churn
    - customer-intelligence
    - platform-agnostic
allowed-tools: Read Write CallMcpTool
---

# Churn Prediction Skill

Identify contacts and accounts at risk of churning using health status analysis combined with engagement signals.

## When to Use

Use this skill when you need to:
- Find contacts with subscription churn dates approaching
- Identify accounts transitioning to at-risk status
- Build churn risk reports for retention teams
- Prioritize outreach to prevent churn
- Analyze churn patterns over time

Do NOT use when:
- Looking for already churned accounts (use churned account queries instead)
- Analyzing churn reasons without proper data (check field completeness first)

---

## Platform Configuration

Configure this skill for your data environment:

```yaml
configuration:
  # Data source settings
  data_source: snowflake | bigquery | salesforce | hubspot
  
  # Primary tables
  customer_table: "{schema}.{health_table}"
  contact_table: "{schema}.{contacts_table}" | null
  
  # Account fields
  account_id_field: "account_id"
  account_name_field: "account_name"
  
  # Revenue configuration
  revenue_field: "arr" | "mrr" | "revenue"
  revenue_type: "arr" | "mrr"
  
  # Health tracking
  health_score_field: "health_score"
  health_status_field: "health_status"
  at_risk_status_values: ["At-Risk", "Red", "Critical"]
  
  # Churn signals (set null if not available)
  churn_date_field: "churn_date" | "subscription_end_date" | null
  days_to_churn_field: "days_until_churn" | null
  churn_reason_field: "churn_reason" | null  # Often incomplete
  
  # Activity tracking
  last_activity_field: "last_activity_date"
  
  # Owner assignment
  owner_field: "cs_owner" | "account_owner"
  
  # Date filtering
  snapshot_date_field: "report_date" | "snapshot_date"
  
  # Thresholds
  thresholds:
    days_to_churn_warning: 30      # Days until churn to flag
    days_to_churn_critical: 14     # Days for critical alert
    health_score_declining: 10     # Point drop to flag as declining
    lookback_days: 30              # Days for trend comparison
    min_revenue: 10000             # Minimum revenue to prioritize
```

---

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `days_threshold` | number | no | 30 | Days until churn to flag contacts |
| `min_revenue` | number | no | config.thresholds.min_revenue | Minimum revenue for account inclusion |
| `include_health_trends` | boolean | no | true | Include health status transition analysis |
| `limit` | number | no | 100 | Maximum results |

---

## Outputs

| Name | Type | Description |
|------|------|-------------|
| `contacts_at_risk` | array | Contacts with upcoming churn dates |
| `accounts_at_risk` | array | Accounts with declining health |
| `summary` | object | Aggregate risk metrics |
| `recommendations` | array | Action items for retention |

---

## Process

### Step 1: Query Churn Risk Contacts

#### Snowflake SQL

```sql
SELECT 
    c.contact_id,
    c.email,
    c.first_name,
    c.last_name,
    c.company,
    c.{days_to_churn_field} AS days_until_churn,
    c.total_usage_count
FROM {contact_table} c
WHERE c.{days_to_churn_field} IS NOT NULL
  AND c.{days_to_churn_field} <= :days_threshold
  AND c.{days_to_churn_field} > 0
ORDER BY c.{days_to_churn_field} ASC
LIMIT :limit;
```

#### BigQuery SQL

```sql
SELECT 
    c.contact_id,
    c.email,
    c.first_name,
    c.last_name,
    c.company,
    c.{days_to_churn_field} AS days_until_churn,
    c.total_usage_count
FROM `{project}.{dataset}.{contact_table}` c
WHERE c.{days_to_churn_field} IS NOT NULL
  AND c.{days_to_churn_field} <= @days_threshold
  AND c.{days_to_churn_field} > 0
ORDER BY c.{days_to_churn_field} ASC
LIMIT @limit;
```

#### Salesforce SOQL

```sql
SELECT 
    Id,
    Email,
    FirstName,
    LastName,
    Account.Name,
    Days_Until_Churn__c,
    Total_Usage__c
FROM Contact
WHERE Days_Until_Churn__c != null
  AND Days_Until_Churn__c <= :daysThreshold
  AND Days_Until_Churn__c > 0
ORDER BY Days_Until_Churn__c ASC
LIMIT :recordLimit
```

#### HubSpot API Filter

```json
{
  "filterGroups": [{
    "filters": [{
      "propertyName": "days_until_subscription_churn",
      "operator": "LTE",
      "value": "{days_threshold}"
    }]
  }],
  "properties": [
    "email", "firstname", "lastname", "company",
    "days_until_subscription_churn", "total_usage_count"
  ],
  "limit": 100
}
```

### Step 2: Query Health Status Transitions

Identify accounts moving TO at-risk status:

#### Snowflake SQL

```sql
SELECT 
    h.{account_id_field} AS account_id,
    h.{account_name_field} AS account_name,
    h.{health_status_field} AS health_status,
    h.{health_score_field} AS health_score,
    h.{revenue_field} AS revenue,
    h.{owner_field} AS owner,
    h.{snapshot_date_field} AS report_date
FROM {customer_table} h
WHERE h.{snapshot_date_field} >= CURRENT_DATE - 7
  AND h.{health_status_field} IN (:at_risk_status_values)
  AND h.{revenue_field} >= :min_revenue
ORDER BY h.{revenue_field} DESC
LIMIT :limit;
```

#### BigQuery SQL

```sql
SELECT 
    h.{account_id_field} AS account_id,
    h.{account_name_field} AS account_name,
    h.{health_status_field} AS health_status,
    h.{health_score_field} AS health_score,
    h.{revenue_field} AS revenue,
    h.{owner_field} AS owner,
    h.{snapshot_date_field} AS report_date
FROM `{project}.{dataset}.{health_table}` h
WHERE h.{snapshot_date_field} >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
  AND h.{health_status_field} IN UNNEST(@at_risk_status_values)
  AND h.{revenue_field} >= @min_revenue
ORDER BY h.{revenue_field} DESC
LIMIT @limit;
```

### Step 3: Identify Health Score Decline Patterns

```sql
-- Compare current vs lookback period health scores
WITH current_scores AS (
    SELECT {account_id_field}, {health_score_field}, {health_status_field}, {revenue_field}
    FROM {customer_table}
    WHERE {snapshot_date_field} = (SELECT MAX({snapshot_date_field}) FROM {customer_table})
),
past_scores AS (
    SELECT {account_id_field}, {health_score_field} AS prev_health_score
    FROM {customer_table}
    WHERE {snapshot_date_field} = (SELECT MAX({snapshot_date_field}) FROM {customer_table}) - :lookback_days
)
SELECT 
    c.{account_id_field} AS account_id,
    c.{health_score_field} AS current_score,
    p.prev_health_score,
    (c.{health_score_field} - p.prev_health_score) AS score_change,
    c.{health_status_field} AS health_status,
    c.{revenue_field} AS revenue
FROM current_scores c
JOIN past_scores p ON c.{account_id_field} = p.{account_id_field}
WHERE c.{health_score_field} < p.prev_health_score
  AND (c.{health_score_field} - p.prev_health_score) <= -:health_score_declining
ORDER BY c.{revenue_field} DESC
LIMIT 50;
```

### Step 4: Merge and Deduplicate

```python
# Combine contacts and accounts, dedup, prioritize
churn_risk = {
    "contacts_at_risk": hubspot_or_crm_results,
    "accounts_at_risk": warehouse_results,
    "health_declining": health_trend_results
}

# Remove duplicates based on account_id
# Prioritize by: revenue (desc), days until churn (asc)
```

### Step 5: Generate Summary and Recommendations

```python
summary = {
    "total_contacts_at_risk": len(contacts_at_risk),
    "total_accounts_at_risk": len(accounts_at_risk),
    "total_revenue_at_risk": sum(a["revenue"] for a in accounts_at_risk),
    "avg_days_to_churn": avg(c["days_until_churn"] for c in contacts_at_risk if c.get("days_until_churn")),
    "by_owner": group_by_owner(accounts_at_risk)
}

recommendations = []
if summary["total_revenue_at_risk"] > config["thresholds"]["min_revenue"] * 10:
    recommendations.append(f"URGENT: ${summary['total_revenue_at_risk']:,} revenue at risk - escalate to leadership")

for account in accounts_at_risk[:5]:
    recommendations.append(f"Schedule call with {account['account_name']} (${account['revenue']:,} revenue)")
```

---

## Output Schema

```json
{
  "summary": {
    "total_contacts_at_risk": "number",
    "total_accounts_at_risk": "number",
    "total_revenue_at_risk": "number",
    "avg_days_to_churn": "number",
    "by_owner": {
      "owner_name": {
        "contact_count": "number",
        "account_count": "number",
        "total_revenue": "number"
      }
    }
  },
  "contacts_at_risk": [
    {
      "email": "string",
      "name": "string",
      "company": "string",
      "days_until_churn": "number",
      "total_usage_count": "number"
    }
  ],
  "accounts_at_risk": [
    {
      "account_id": "string",
      "account_name": "string",
      "health_status": "string",
      "health_score": "number",
      "revenue": "number",
      "owner": "string",
      "score_change_30d": "number"
    }
  ],
  "recommendations": ["string"]
}
```

---

## Quality Criteria

- [ ] Query executes without error on configured data sources
- [ ] Revenue threshold correctly applied
- [ ] No duplicates between contact and account lists
- [ ] Recommendations are actionable
- [ ] No PII in summary output

---

## Example Usage

**Find contacts churning in 14 days:**
```
Use churn-prediction with days_threshold=14
```

**High-value churn risk report:**
```
Predict churn for accounts with revenue >= $50K
```

---

## Sample Output

```json
{
  "summary": {
    "total_contacts_at_risk": 45,
    "total_accounts_at_risk": 32,
    "total_revenue_at_risk": 890000,
    "avg_days_to_churn": 18,
    "by_owner": {
      "Sarah Johnson": { "contact_count": 12, "account_count": 8, "total_revenue": 245000 },
      "Mike Chen": { "contact_count": 10, "account_count": 7, "total_revenue": 198000 }
    }
  },
  "contacts_at_risk": [
    {
      "email": "j.smith@acme.com",
      "name": "John Smith",
      "company": "Acme Corp",
      "days_until_churn": 7,
      "total_usage_count": 1250
    }
  ],
  "accounts_at_risk": [
    {
      "account_id": "A-12345",
      "account_name": "Acme Corp",
      "health_status": "At-Risk",
      "health_score": 28,
      "revenue": 156000,
      "owner": "Sarah Johnson",
      "score_change_30d": -22
    }
  ],
  "recommendations": [
    "URGENT: $890K revenue at risk - escalate to leadership",
    "Schedule call with Acme Corp ($156,000 revenue)",
    "7 accounts have declined >20 points in 30 days - immediate outreach required"
  ]
}
```

---

## Known Limitations & Workarounds

### Issue: Churn reason field often incomplete

Instead of relying on churn_reason, use these proxy signals:
1. **Health Status Transitions**: Track accounts moving Healthy → At-Risk
2. **Health Score Decline**: Flag accounts with significant point drops
3. **Activity Gaps**: Use dormant-detection to find inactive accounts
4. **CRM Churn Date**: Reactive but reliable for imminent churn

### Issue: Missing Churn Attribution

Create manual churn reason tracking:
1. When account churns, CS team adds note with reason code
2. Aggregate notes via CRM API for pattern analysis
3. Use engagement notes as proxy for churn indicators

---

## Notes

- Run weekly for retention planning
- Prioritize high-revenue accounts for executive attention
- Combine with at-risk-detection skill for comprehensive view
- Export to CSV for CS team distribution
- Consider Slack/email alerts for new at-risk flags
