---
name: deal-velocity
description: |
  Analyze account health and win rates by sales owner for performance benchmarking.
  Use when asked to 'check deal velocity', 'compare owner performance', 'benchmark reps',
  'review healthy rates by owner', or 'analyze sales owner effectiveness'.
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
    - velocity
    - performance
    - benchmarking
    - multi-crm
allowed-tools: Read Write CallMcpTool
---

# Deal Velocity Skill

Analyze account health trends and performance rates by sales owner for benchmarking and performance management across multiple CRM platforms.

## When to Use

Use this skill when you need to:
- Benchmark sales owners against each other
- Compare healthy account rates across owners
- Identify top performers by health metrics
- Support performance review conversations
- Set targets based on peer performance

Do NOT use when:
- You need detailed account-level breakdown (use at-risk-detection)
- You need week-over-week engagement trends (use engagement-velocity)
- You need individual deal status (use pipeline-analysis)

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
    health_scores_table: "{table_name}"
  
  # Field mapping
  field_mapping:
    owner_field: "hubspot_owner_id" | "OwnerId" | "owner_id"
    account_id: "account_id" | "AccountId" | "org_id"
    revenue_field: "amount" | "annual_revenue" | "arr"
    health_score: "health_score" | "HealthScore__c"
    health_status: "health_status" | "Status__c"
    report_date: "report_date" | "snapshot_date"
  
  # Health status values
  health_values:
    healthy: ["Healthy", "Green", "Good"]
    at_risk: ["At-Risk", "Yellow", "Concerning"]
```

---

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `min_accounts` | number | no | 5 | Minimum accounts to include owner |
| `include_benchmarks` | boolean | no | true | Include team benchmark comparisons |

---

## Platform-Specific Query Patterns

### Data Warehouse - Generic SQL

```sql
SELECT 
    {owner_field} as OWNER_NAME,
    COUNT(*) as TOTAL_ACCOUNTS,
    SUM({revenue_field}) as TOTAL_REVENUE,
    ROUND(SUM(CASE WHEN {health_status} IN ('{healthy_values}') THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as HEALTHY_RATE,
    ROUND(AVG({health_score}), 1) as AVG_HEALTH
FROM {database}.{schema}.{health_scores_table}
WHERE {report_date} = (SELECT MAX({report_date}) FROM {database}.{schema}.{health_scores_table})
  AND {owner_field} IS NOT NULL
GROUP BY 1
ORDER BY TOTAL_REVENUE DESC
```

### HubSpot

```json
{
  "filterGroups": [{
    "filters": [
      { "propertyName": "hubspot_owner_id", "operator": "HAS_PROPERTY" },
      { "propertyName": "hs_analytics_source", "operator": "HAS_PROPERTY" }
    ]
  }],
  "properties": [
    "hubspot_owner_id", "annualrevenue", "hs_lead_status", 
    "lifecyclestage", "hs_analytics_source"
  ],
  "limit": 100
}
```

**MCP Tool:** `user-hubspot` → `hubspot_search` (object: companies)

Post-process to calculate healthy rates:
```python
healthy_statuses = config["health_values"]["healthy"]
for owner_id, accounts in grouped_accounts.items():
    healthy_count = sum(1 for a in accounts if a["lifecyclestage"] in healthy_statuses)
    owner_data["healthy_rate"] = (healthy_count / len(accounts)) * 100
```

### Salesforce

```sql
SELECT OwnerId, Owner.Name,
       COUNT(Id) as TotalAccounts,
       SUM(AnnualRevenue) as TotalRevenue,
       AVG(Health_Score__c) as AvgHealth,
       SUM(CASE WHEN Health_Status__c = 'Healthy' THEN 1 ELSE 0 END) * 100.0 / COUNT(Id) as HealthyRate
FROM Account
WHERE OwnerId != null
GROUP BY OwnerId, Owner.Name
HAVING COUNT(Id) >= {min_accounts}
ORDER BY TotalRevenue DESC
```

### Pipedrive

Aggregate via deals endpoint:
```
GET /deals/summary
Parameters:
  user_id: {owner_id}
  status: won
  
GET /deals/summary  
Parameters:
  user_id: {owner_id}
  status: open
```

Calculate win rates from summaries.

### Zoho CRM

```json
{
  "module": "Accounts",
  "criteria": "(Owner:not_equals:null)",
  "fields": ["Owner", "Annual_Revenue", "Health_Score", "Account_Status"],
  "group_by": "Owner"
}
```

### Microsoft Dynamics

```
GET /accounts
$apply: groupby((_ownerid_value), 
  aggregate(annualrevenue with sum as totalrevenue, 
            healthscore with average as avghealth,
            $count as accountcount))
$filter: _ownerid_value ne null
```

---

## Process

### Step 1: Query Data by Owner

Execute platform-specific query.

### Step 2: Calculate Benchmarks

```python
# Team-wide benchmarks
avg_healthy_rate = sum(o["healthy_rate"] for o in owners) / len(owners)
avg_health_score = sum(o["avg_health"] for o in owners) / len(owners)
total_team_revenue = sum(o["total_revenue"] for o in owners)

# Percentile rankings
owners_by_health = sorted(owners, key=lambda x: x["healthy_rate"], reverse=True)
for i, owner in enumerate(owners_by_health):
    owner["health_percentile"] = round((1 - i / len(owners)) * 100)
```

### Step 3: Classify Performance Tiers

```python
for owner in owners:
    # Performance tier based on healthy rate vs team average
    if owner["healthy_rate"] >= avg_healthy_rate * 1.2:
        owner["performance_tier"] = "ABOVE_BENCHMARK"
    elif owner["healthy_rate"] <= avg_healthy_rate * 0.8:
        owner["performance_tier"] = "BELOW_BENCHMARK"
    else:
        owner["performance_tier"] = "AT_BENCHMARK"
    
    # Revenue weight (% of team portfolio)
    owner["revenue_weight_pct"] = (owner["total_revenue"] / total_team_revenue) * 100
```

### Step 4: Generate Insights

Based on analysis:
- Identify owners beating benchmark by >20%
- Flag owners below benchmark with high revenue weight
- Calculate potential revenue impact of improving below-benchmark owners

---

## Output Schema

```json
{
  "config": {
    "data_source": "string",
    "platform": "string"
  },
  "benchmarks": {
    "team_avg_healthy_rate": "number",
    "team_avg_health_score": "number",
    "total_team_revenue": "number",
    "total_accounts": "number"
  },
  "owners": [
    {
      "owner_name": "string",
      "total_accounts": "number",
      "total_revenue": "number",
      "revenue_weight_pct": "number",
      "healthy_rate": "number",
      "avg_health": "number",
      "health_percentile": "number",
      "performance_tier": "ABOVE_BENCHMARK | AT_BENCHMARK | BELOW_BENCHMARK"
    }
  ],
  "top_performers": [
    {
      "owner_name": "string",
      "healthy_rate": "number",
      "delta_vs_avg": "number"
    }
  ],
  "improvement_opportunities": [
    {
      "owner_name": "string",
      "healthy_rate": "number",
      "revenue_at_risk": "number",
      "potential_revenue_save": "number"
    }
  ],
  "recommendations": ["string"]
}
```

---

## Example Usage

**Generate velocity benchmarks:**
```
Analyze deal velocity by rep for benchmarking
```

**Identify performance gaps:**
```
Use deal-velocity skill to compare sales owner effectiveness
```

---

## Sample Output

```json
{
  "config": {
    "data_source": "data_warehouse",
    "platform": "snowflake"
  },
  "benchmarks": {
    "team_avg_healthy_rate": 55.2,
    "team_avg_health_score": 58.5,
    "total_team_revenue": 4500000,
    "total_accounts": 320
  },
  "owners": [
    {
      "owner_name": "Sarah Johnson",
      "total_accounts": 45,
      "total_revenue": 890000,
      "revenue_weight_pct": 19.8,
      "healthy_rate": 71.1,
      "avg_health": 72,
      "health_percentile": 100,
      "performance_tier": "ABOVE_BENCHMARK"
    },
    {
      "owner_name": "Mike Chen",
      "total_accounts": 52,
      "total_revenue": 720000,
      "revenue_weight_pct": 16.0,
      "healthy_rate": 38.5,
      "avg_health": 54,
      "health_percentile": 25,
      "performance_tier": "BELOW_BENCHMARK"
    }
  ],
  "top_performers": [
    {
      "owner_name": "Sarah Johnson",
      "healthy_rate": 71.1,
      "delta_vs_avg": 15.9
    }
  ],
  "improvement_opportunities": [
    {
      "owner_name": "Mike Chen",
      "healthy_rate": 38.5,
      "revenue_at_risk": 442800,
      "potential_revenue_save": 110700
    }
  ],
  "recommendations": [
    "Sarah Johnson is 29% above team benchmark - document best practices for team enablement",
    "Mike Chen manages $720K revenue but has 38.5% healthy rate vs team avg of 55.2% - prioritize coaching",
    "Improving Mike Chen to team average could reduce at-risk revenue by ~$110K"
  ]
}
```

---

## Quality Criteria

- [ ] Query executes without error
- [ ] All owners with minimum accounts included
- [ ] Benchmarks calculated from full dataset
- [ ] Percentiles ranked correctly
- [ ] Performance tiers assigned consistently

---

## Client Setup Required

```yaml
# clients/{client_id}/config.yaml
deal_velocity:
  data_source: data_warehouse
  
  warehouse:
    type: snowflake
    database: ANALYTICS
    schema: REPORTING
    health_scores_table: ACCOUNT_HEALTH_DAILY
    
  field_mapping:
    owner_field: account_owner
    account_id: account_id
    revenue_field: annual_revenue
    health_score: health_score
    health_status: health_status
    report_date: snapshot_date
    
  health_values:
    healthy: ["Healthy", "Good"]
    at_risk: ["At-Risk", "Concerning"]
```

---

## Known Limitations

1. **Healthy rate as proxy** - actual deal win rates require pipeline data
2. **Point-in-time** - no historical velocity trending
3. **No activity metrics** - only health status outcomes

---

## Notes

- Run monthly for performance reviews
- Combine with sales-rep-performance for complete picture
- Use for setting quarterly targets and OKRs
