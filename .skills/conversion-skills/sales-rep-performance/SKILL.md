---
name: sales-rep-performance
description: |
  Generate sales rep leaderboards with account metrics, revenue, and risk distribution.
  Use when asked to 'check rep performance', 'generate sales leaderboard', 'compare reps',
  'review account distribution', or 'analyze rep portfolio health'.
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
  estimated_runtime: "30s-1min"
  max_cost: "$0.25"
  client_facing: true
  requires_human_review: false
  tags:
    - sales
    - performance
    - leaderboard
    - multi-crm
    - data-warehouse
allowed-tools: Read Write CallMcpTool
---

# Sales Rep Performance Skill

Analyze sales rep and account owner performance by account distribution, revenue, and portfolio health across multiple CRM platforms and data warehouses.

## When to Use

Use this skill when you need to:
- Generate rep performance leaderboards
- Compare account distribution across reps
- Identify reps with high at-risk portfolios
- Analyze revenue concentration by owner
- Support territory planning decisions

Do NOT use when:
- You need individual deal-level analysis (use pipeline-analysis)
- You need engagement metrics at org level (use engagement-velocity)

---

## Configuration

```yaml
configuration:
  # Data source options
  data_source: crm | data_warehouse
  
  # CRM platform (if data_source = crm)
  crm_platform: hubspot | salesforce | pipedrive | zoho | dynamics
  
  # Data warehouse (if data_source = data_warehouse)
  warehouse:
    type: snowflake | bigquery | redshift
    database: "{database_name}"
    schema: "{schema_name}"
    health_scores_table: "{table_name}"  # Table with account health data
  
  # Field mapping
  field_mapping:
    owner_field: "hubspot_owner_id" | "OwnerId" | "owner_id" | "user_id"
    account_id: "company_id" | "AccountId" | "org_id" | "account_id"
    revenue_field: "amount" | "annual_revenue" | "arr" | "mrr"
    health_score: "health_score" | "HealthScore__c" | "score"
    health_status: "health_status" | "Status__c" | "risk_level"
  
  # Health status mapping
  health_mapping:
    healthy: ["Healthy", "Green", "Good", "Low Risk"]
    at_risk: ["At-Risk", "Yellow", "Medium Risk", "Concerning"]
    critical: ["Critical", "Red", "High Risk", "Churning"]
```

---

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `days` | number | no | 30 | Lookback period (for trend analysis) |
| `owner_id` | string | no | null | Filter to specific rep |
| `min_accounts` | number | no | 1 | Minimum accounts to include rep |

---

## Platform-Specific Query Patterns

### Data Warehouse - Generic SQL

```sql
SELECT 
    {owner_field} as SALES_REP,
    COUNT(DISTINCT {account_id}) as ACCOUNTS_MANAGED,
    SUM({revenue_field}) as TOTAL_REVENUE,
    AVG({health_score}) as AVG_HEALTH_SCORE,
    SUM(CASE WHEN {health_status} IN ('{at_risk_values}') THEN 1 ELSE 0 END) as AT_RISK_COUNT,
    SUM(CASE WHEN {health_status} IN ('{healthy_values}') THEN 1 ELSE 0 END) as HEALTHY_COUNT
FROM {database}.{schema}.{health_scores_table}
WHERE report_date = (SELECT MAX(report_date) FROM {database}.{schema}.{health_scores_table})
  AND {owner_field} IS NOT NULL
GROUP BY 1
ORDER BY TOTAL_REVENUE DESC
```

### HubSpot (CRM-based)

```json
{
  "filterGroups": [{
    "filters": [
      { "propertyName": "hubspot_owner_id", "operator": "HAS_PROPERTY" }
    ]
  }],
  "properties": [
    "hubspot_owner_id", "annualrevenue", "hs_lead_status",
    "lifecyclestage", "hs_object_id"
  ],
  "limit": 100
}
```

**MCP Tool:** `user-hubspot` → `hubspot_search` (object: companies)

Aggregate in application:
```python
by_owner = {}
for company in companies:
    owner = company["hubspot_owner_id"]
    by_owner.setdefault(owner, {"accounts": 0, "revenue": 0})
    by_owner[owner]["accounts"] += 1
    by_owner[owner]["revenue"] += float(company.get("annualrevenue", 0))
```

### Salesforce

```sql
SELECT OwnerId, Owner.Name,
       COUNT(Id) as AccountCount,
       SUM(AnnualRevenue) as TotalRevenue,
       AVG(Health_Score__c) as AvgHealth
FROM Account
WHERE OwnerId != null
GROUP BY OwnerId, Owner.Name
ORDER BY TotalRevenue DESC
```

**API Endpoint:** `/services/data/v58.0/query?q={SOQL}`

### Pipedrive

```
GET /persons
Parameters:
  filter_id: {owner_filter}
  
GET /organizations  
Parameters:
  owner_id: {owner_id}
```

Aggregate deals by owner:
```
GET /deals/summary
Parameters:
  user_id: {owner_id}
  status: open
```

### Zoho CRM

```json
{
  "module": "Accounts",
  "criteria": "(Owner:not_equals:null)",
  "fields": ["Account_Name", "Owner", "Annual_Revenue", "Health_Score"],
  "group_by": "Owner",
  "aggregate": ["COUNT(Account_Name)", "SUM(Annual_Revenue)", "AVG(Health_Score)"]
}
```

### Microsoft Dynamics

```
GET /accounts
$apply: groupby((ownerid), aggregate(annualrevenue with sum as totalrevenue, $count as accountcount))
$filter: _ownerid_value ne null
$orderby: totalrevenue desc
```

---

## Process

### Step 1: Load Configuration and Query Data

```python
config = load_client_config(client_id)

if config["data_source"] == "data_warehouse":
    query = build_warehouse_query(config)
    results = execute_warehouse_query(query)
else:
    results = query_crm_and_aggregate(config)
```

### Step 2: Calculate Performance Metrics

```python
for rep in reps:
    # Risk ratio
    rep["at_risk_ratio"] = rep["at_risk_count"] / rep["accounts_managed"] * 100
    
    # Revenue per account
    rep["revenue_per_account"] = rep["total_revenue"] / rep["accounts_managed"]
    
    # Portfolio health score
    rep["portfolio_health"] = (rep["healthy_count"] / rep["accounts_managed"]) * 100
    
    # Performance tier
    if rep["avg_health_score"] >= 70 and rep["at_risk_ratio"] < 15:
        rep["tier"] = "TOP_PERFORMER"
    elif rep["at_risk_ratio"] > 30:
        rep["tier"] = "NEEDS_ATTENTION"
    else:
        rep["tier"] = "ON_TRACK"
```

### Step 3: Generate Rankings

```python
# Rank by different dimensions
by_revenue = sorted(reps, key=lambda x: x["total_revenue"], reverse=True)
by_health = sorted(reps, key=lambda x: x["avg_health_score"], reverse=True)
by_risk = sorted(reps, key=lambda x: x["at_risk_ratio"])  # Lower is better

# Identify outliers
avg_accounts = sum(r["accounts_managed"] for r in reps) / len(reps)
overloaded_reps = [r for r in reps if r["accounts_managed"] > avg_accounts * 1.5]
at_risk_concentrated = [r for r in reps if r["at_risk_ratio"] > 30]
```

### Step 4: Generate Recommendations

Based on analysis:
- Reps with >30% at-risk ratio → Need support or account redistribution
- Reps with high revenue but low health → Prioritize retention coaching
- Reps with >50% more accounts than average → Consider load balancing

---

## Output Schema

```json
{
  "config": {
    "data_source": "string",
    "platform": "string"
  },
  "summary": {
    "total_reps": "number",
    "total_revenue_managed": "number",
    "total_accounts": "number",
    "avg_accounts_per_rep": "number",
    "avg_health_score": "number"
  },
  "leaderboard": [
    {
      "rank": "number",
      "sales_rep": "string",
      "accounts_managed": "number",
      "total_revenue": "number",
      "revenue_per_account": "number",
      "avg_health_score": "number",
      "at_risk_count": "number",
      "healthy_count": "number",
      "at_risk_ratio_pct": "number",
      "portfolio_health_pct": "number",
      "tier": "TOP_PERFORMER | ON_TRACK | NEEDS_ATTENTION"
    }
  ],
  "insights": {
    "top_performers": ["string"],
    "needs_attention": ["string"],
    "overloaded": ["string"]
  },
  "recommendations": ["string"]
}
```

---

## Example Usage

**Generate rep leaderboard:**
```
Generate sales rep performance leaderboard
```

**Identify reps needing support:**
```
Use sales-rep-performance skill to find reps with high at-risk portfolios
```

---

## Sample Output

```json
{
  "config": {
    "data_source": "data_warehouse",
    "platform": "snowflake"
  },
  "summary": {
    "total_reps": 8,
    "total_revenue_managed": 4500000,
    "total_accounts": 320,
    "avg_accounts_per_rep": 40,
    "avg_health_score": 58.5
  },
  "leaderboard": [
    {
      "rank": 1,
      "sales_rep": "Sarah Johnson",
      "accounts_managed": 45,
      "total_revenue": 890000,
      "revenue_per_account": 19778,
      "avg_health_score": 72,
      "at_risk_count": 5,
      "healthy_count": 32,
      "at_risk_ratio_pct": 11.1,
      "portfolio_health_pct": 71.1,
      "tier": "TOP_PERFORMER"
    },
    {
      "rank": 2,
      "sales_rep": "Mike Chen",
      "accounts_managed": 52,
      "total_revenue": 720000,
      "revenue_per_account": 13846,
      "avg_health_score": 54,
      "at_risk_count": 18,
      "healthy_count": 20,
      "at_risk_ratio_pct": 34.6,
      "portfolio_health_pct": 38.5,
      "tier": "NEEDS_ATTENTION"
    }
  ],
  "insights": {
    "top_performers": ["Sarah Johnson"],
    "needs_attention": ["Mike Chen"],
    "overloaded": ["Mike Chen (52 accounts vs avg 40)"]
  },
  "recommendations": [
    "Mike Chen has 34.6% at-risk accounts - consider targeted retention coaching",
    "Mike Chen is overloaded with 52 accounts (30% above average) - evaluate account redistribution",
    "Sarah Johnson demonstrates best practices - document approach for team enablement"
  ]
}
```

---

## Quality Criteria

- [ ] Query executes without error
- [ ] All reps with accounts included
- [ ] Ratios calculated correctly
- [ ] Tiers assigned based on thresholds
- [ ] Rankings consistent with data

---

## Client Setup Required

```yaml
# clients/{client_id}/config.yaml
sales_rep_performance:
  data_source: data_warehouse  # or crm
  
  # For data warehouse
  warehouse:
    type: snowflake
    database: ANALYTICS
    schema: REPORTING
    health_scores_table: ACCOUNT_HEALTH_SCORES
    
  # For CRM
  crm_platform: hubspot
  
  field_mapping:
    owner_field: owner_id
    account_id: account_id
    revenue_field: annual_revenue
    health_score: health_score
    health_status: health_status
```

---

## Known Limitations

1. **Point-in-time snapshot** - uses latest report date only
2. **No historical trending** - cannot show improvement over time
3. **Owner field required** - accounts without owner not included

---

## Notes

- Run weekly for management reviews
- Export to spreadsheet for team meetings
- Combine with deal-velocity for comprehensive rep analysis
