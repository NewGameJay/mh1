---
name: dormant-detection
description: |
  Find high-value accounts with no recent activity using health score or activity data as signals.
  Use when asked to 'find dormant accounts', 'detect inactive customers', 'identify engagement risk',
  'wake-up campaign targets', or 'accounts not using product'.
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
  estimated_runtime: "1-3min"
  max_runtime: "10min"
  estimated_cost: "$0.25"
  max_cost: "$0.75"
  client_facing: true
  requires_human_review: false
  tags:
    - engagement
    - retention
    - customer-intelligence
    - platform-agnostic
allowed-tools: Read Write CallMcpTool
---

# Dormant Detection Skill

Identify high-value accounts showing signs of inactivity to enable proactive re-engagement campaigns.

## When to Use

Use this skill when you need to:
- Find accounts at engagement risk
- Build re-engagement campaign lists
- Identify accounts for wake-up outreach
- Prioritize CS touchpoints by inactivity
- Prevent silent churn

Do NOT use when:
- Account has already churned (use churned account queries)
- Looking for new leads (use pipeline queries)

---

## Platform Configuration

Configure this skill for your data environment:

```yaml
configuration:
  # Data source settings
  data_source: snowflake | bigquery | salesforce | hubspot
  
  # Primary tables
  customer_table: "{schema}.{health_table}"
  activity_table: "{schema}.{events_table}" | null  # Optional for activity validation
  
  # Account fields
  account_id_field: "account_id"
  account_name_field: "account_name"
  
  # Revenue configuration
  revenue_field: "arr" | "mrr" | "revenue"
  revenue_type: "arr" | "mrr"
  
  # Health/engagement signals
  health_score_field: "health_score" | null
  health_status_field: "health_status"
  churned_status_values: ["Churned", "Cancelled", "Lost"]
  
  # Activity tracking (preferred method)
  last_activity_field: "last_activity_date" | null
  activity_event_field: "event_type" | null  # If using activity table
  
  # Owner assignment
  owner_field: "cs_owner" | "account_owner"
  
  # Date filtering
  snapshot_date_field: "report_date" | "snapshot_date"
  
  # Detection method
  detection_method: "health_score" | "activity_date" | "hybrid"
  # health_score: Use low health as proxy for inactivity
  # activity_date: Use actual last activity date
  # hybrid: Combine both signals
  
  # Thresholds
  thresholds:
    min_revenue: 10000           # Minimum revenue to include
    dormant_health_max: 40       # Max health score to flag (if using health_score method)
    dormant_days_threshold: 30   # Days since last activity (if using activity_date method)
    critical_days_threshold: 60  # Days for critical dormancy
    
  # Severity bands (health score based)
  severity_bands:
    critical: 20   # score < 20
    high: 30       # score < 30
    medium: 40     # score < 40
    
  # Revenue tiers (customize for your business)
  revenue_tiers:
    enterprise: 50000
    mid_market: 20000
    smb: 0
```

---

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `min_revenue` | number | no | config.thresholds.min_revenue | Minimum revenue to include |
| `health_threshold` | number | no | config.thresholds.dormant_health_max | Max health score (lower = more inactive) |
| `days_inactive` | number | no | config.thresholds.dormant_days_threshold | Days since last activity |
| `limit` | number | no | 50 | Maximum accounts to return |
| `exclude_churned` | boolean | no | true | Exclude churned accounts |

---

## Outputs

| Name | Type | Description |
|------|------|-------------|
| `dormant_accounts` | array | High-value accounts with low engagement |
| `summary` | object | Aggregate metrics |
| `recommendations` | array | Re-engagement actions |

---

## Process

### Step 1: Query Dormant High-Value Accounts

Select the appropriate query based on your detection method:

#### Method A: Health Score Proxy (Snowflake)

```sql
SELECT 
    {account_id_field} AS account_id, 
    {account_name_field} AS account_name, 
    {revenue_field} AS revenue, 
    {health_score_field} AS health_score, 
    {health_status_field} AS health_status, 
    {owner_field} AS owner
FROM {customer_table}
WHERE {snapshot_date_field} = (SELECT MAX({snapshot_date_field}) FROM {customer_table})
  AND {revenue_field} >= :min_revenue
  AND {health_status_field} NOT IN (:churned_status_values)
  AND {health_score_field} < :health_threshold
ORDER BY {revenue_field} DESC
LIMIT :limit;
```

#### Method B: Activity Date Based (Snowflake)

```sql
SELECT 
    c.{account_id_field} AS account_id, 
    c.{account_name_field} AS account_name, 
    c.{revenue_field} AS revenue, 
    c.{health_score_field} AS health_score,
    c.{last_activity_field} AS last_activity_date,
    DATEDIFF(day, c.{last_activity_field}, CURRENT_DATE) AS days_inactive,
    c.{owner_field} AS owner
FROM {customer_table} c
WHERE c.{snapshot_date_field} = (SELECT MAX({snapshot_date_field}) FROM {customer_table})
  AND c.{revenue_field} >= :min_revenue
  AND c.{health_status_field} NOT IN (:churned_status_values)
  AND DATEDIFF(day, c.{last_activity_field}, CURRENT_DATE) > :days_inactive
ORDER BY c.{revenue_field} DESC
LIMIT :limit;
```

#### BigQuery SQL (Activity Based)

```sql
SELECT 
    c.{account_id_field} AS account_id, 
    c.{account_name_field} AS account_name, 
    c.{revenue_field} AS revenue, 
    c.{health_score_field} AS health_score,
    c.{last_activity_field} AS last_activity_date,
    DATE_DIFF(CURRENT_DATE(), c.{last_activity_field}, DAY) AS days_inactive,
    c.{owner_field} AS owner
FROM `{project}.{dataset}.{table}` c
WHERE c.{snapshot_date_field} = (SELECT MAX({snapshot_date_field}) FROM `{project}.{dataset}.{table}`)
  AND c.{revenue_field} >= @min_revenue
  AND c.{health_status_field} NOT IN UNNEST(@churned_status_values)
  AND DATE_DIFF(CURRENT_DATE(), c.{last_activity_field}, DAY) > @days_inactive
ORDER BY c.{revenue_field} DESC
LIMIT @limit;
```

#### Salesforce SOQL

```sql
SELECT 
    Id,
    Name,
    AnnualRevenue,
    Health_Score__c,
    Health_Status__c,
    Last_Activity_Date__c,
    OwnerId,
    Owner.Name
FROM Account
WHERE AnnualRevenue >= :minRevenue
  AND Health_Status__c NOT IN :churnedStatuses
  AND (
    Health_Score__c < :healthThreshold
    OR Last_Activity_Date__c < :inactivityDate
  )
ORDER BY AnnualRevenue DESC
LIMIT :recordLimit
```

#### HubSpot API Filter

```json
{
  "filterGroups": [{
    "filters": [
      {
        "propertyName": "annualrevenue",
        "operator": "GTE",
        "value": "{min_revenue}"
      },
      {
        "propertyName": "health_score",
        "operator": "LT",
        "value": "{health_threshold}"
      },
      {
        "propertyName": "lifecyclestage",
        "operator": "NOT_IN",
        "values": ["churned", "lost"]
      }
    ]
  }],
  "properties": [
    "name", "annualrevenue", "health_score", 
    "health_status", "hubspot_owner_id", "notes_last_updated"
  ],
  "sorts": [{"propertyName": "annualrevenue", "direction": "DESCENDING"}],
  "limit": 50
}
```

### Step 2: Validate Activity (Optional High-Fidelity Mode)

If using activity table for validation:

```sql
SELECT 
    a.{account_id_field} AS account_id,
    MAX(e.created_at) AS last_event_date,
    DATEDIFF(day, MAX(e.created_at), CURRENT_DATE) AS true_days_inactive,
    COUNT(*) AS total_events_90d
FROM {customer_table} a
LEFT JOIN {activity_table} e 
    ON a.{account_id_field} = e.{account_id_field}
    AND e.created_at > DATEADD(day, -90, CURRENT_DATE())
WHERE a.{account_id_field} IN (:dormant_account_ids)
GROUP BY a.{account_id_field};
```

### Step 3: Calculate Dormancy Severity

```python
def calculate_severity(account, config):
    severity_bands = config["severity_bands"]
    revenue_tiers = config["revenue_tiers"]
    
    # Severity based on health score bands
    health_score = account.get("health_score", 0)
    if health_score < severity_bands["critical"]:
        account["dormancy_severity"] = "critical"
    elif health_score < severity_bands["high"]:
        account["dormancy_severity"] = "high"
    elif health_score < severity_bands["medium"]:
        account["dormancy_severity"] = "medium"
    else:
        account["dormancy_severity"] = "low"
    
    # Revenue tier
    revenue = account.get("revenue", 0)
    if revenue >= revenue_tiers["enterprise"]:
        account["revenue_tier"] = "enterprise"
    elif revenue >= revenue_tiers["mid_market"]:
        account["revenue_tier"] = "mid_market"
    else:
        account["revenue_tier"] = "smb"
    
    return account

for account in dormant_accounts:
    calculate_severity(account, config)
```

### Step 4: Generate Summary

```python
summary = {
    "total_dormant_accounts": len(dormant_accounts),
    "total_revenue_at_risk": sum(a["revenue"] for a in dormant_accounts),
    "avg_health_score": sum(a["health_score"] for a in dormant_accounts) / len(dormant_accounts) if dormant_accounts else 0,
    "by_severity": {
        "critical": len([a for a in dormant_accounts if a["dormancy_severity"] == "critical"]),
        "high": len([a for a in dormant_accounts if a["dormancy_severity"] == "high"]),
        "medium": len([a for a in dormant_accounts if a["dormancy_severity"] == "medium"])
    },
    "by_owner": group_by_owner(dormant_accounts)
}
```

### Step 5: Generate Re-engagement Recommendations

```python
recommendations = []

# Critical severity accounts
critical = [a for a in dormant_accounts if a["dormancy_severity"] == "critical"]
if critical:
    recommendations.append(f"{len(critical)} critical dormant accounts need immediate outreach")

# Enterprise tier
enterprise = [a for a in dormant_accounts if a["revenue_tier"] == "enterprise"]
if enterprise:
    total_revenue = sum(a["revenue"] for a in enterprise)
    recommendations.append(f"${total_revenue:,} enterprise revenue at dormancy risk - schedule exec reviews")

# Owner concentration
top_owners = get_top_owners_by_count(dormant_accounts, 3)
for owner in top_owners:
    if owner["count"] > 5:
        recommendations.append(f"{owner['name']} has {owner['count']} dormant accounts - review portfolio")
```

---

## Output Schema

```json
{
  "summary": {
    "total_dormant_accounts": "number",
    "total_revenue_at_risk": "number",
    "avg_health_score": "number",
    "by_severity": {
      "critical": "number",
      "high": "number",
      "medium": "number"
    },
    "by_owner": {
      "owner_name": {
        "account_count": "number",
        "total_revenue": "number",
        "avg_health_score": "number"
      }
    }
  },
  "dormant_accounts": [
    {
      "account_id": "string",
      "account_name": "string",
      "revenue": "number",
      "health_score": "number",
      "health_status": "string",
      "owner": "string",
      "dormancy_severity": "critical | high | medium",
      "revenue_tier": "enterprise | mid_market | smb",
      "days_inactive": "number (if available)"
    }
  ],
  "recommendations": ["string"]
}
```

---

## Quality Criteria

- [ ] Query executes without error
- [ ] Revenue threshold correctly applied
- [ ] Churned accounts excluded
- [ ] Severity classifications accurate
- [ ] Recommendations actionable and specific

---

## Example Usage

**Find all dormant high-value accounts:**
```
Detect dormant accounts with revenue >= $10K
```

**Critical dormant enterprise accounts:**
```
Find dormant accounts with revenue >= $50K and health score < 30
```

**CS owner portfolio review:**
```
Show dormant accounts grouped by owner
```

---

## Sample Output

```json
{
  "summary": {
    "total_dormant_accounts": 47,
    "total_revenue_at_risk": 1250000,
    "avg_health_score": 28,
    "by_severity": {
      "critical": 12,
      "high": 18,
      "medium": 17
    },
    "by_owner": {
      "Sarah Johnson": { "account_count": 11, "total_revenue": 320000, "avg_health_score": 25 },
      "Mike Chen": { "account_count": 9, "total_revenue": 275000, "avg_health_score": 31 }
    }
  },
  "dormant_accounts": [
    {
      "account_id": "A-98765",
      "account_name": "TechGiant Inc",
      "revenue": 156000,
      "health_score": 18,
      "health_status": "At-Risk",
      "owner": "Sarah Johnson",
      "dormancy_severity": "critical",
      "revenue_tier": "enterprise"
    }
  ],
  "recommendations": [
    "12 critical dormant accounts need immediate outreach",
    "$580,000 enterprise revenue at dormancy risk - schedule exec reviews",
    "Sarah Johnson has 11 dormant accounts - review portfolio"
  ]
}
```

---

## Detection Method Guidance

### When to use `health_score` method:
- No direct activity tracking available
- Health score incorporates engagement signals
- Quick approximation needed

### When to use `activity_date` method:
- Direct last_activity_date available
- Need precise inactivity measurement
- Activity table accessible

### When to use `hybrid` method:
- Both signals available
- Need validation of health score proxy
- High-value accounts requiring precision

---

## Related Skills

- `at-risk-detection` - Focuses on at-risk status, not dormancy
- `churn-prediction` - Imminent churn vs engagement drop
- `engagement-velocity` - Week-over-week engagement changes

---

## Notes

- Run bi-weekly for proactive engagement
- Critical severity accounts should trigger alerts
- Consider automated re-engagement email sequences
- Track re-activation success rates by severity tier
