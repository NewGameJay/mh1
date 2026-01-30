---
name: reactivation-detection
description: |
  Identify churned accounts with reactivation potential using historical usage signals.
  Use when asked to 'find reactivation candidates', 'identify winback opportunities',
  'detect dormant accounts', 'churned account analysis', or 'reactivation list'.
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
  created: "2026-01-28"
  updated: "2026-01-28"
  estimated_runtime: "2-5min"
  max_runtime: "15min"
  estimated_cost: "$0.50"
  max_cost: "$2.00"
  client_facing: true
  requires_human_review: false
  tags:
    - customer-lifecycle
    - reactivation
    - winback
    - churn
    - platform-agnostic
allowed-tools: Read Write CallMcpTool
---

# Reactivation Detection Skill

Identify churned and dormant accounts with potential for reactivation based on historical usage signals, time since churn, and engagement patterns.

## When to Use

Use this skill when you need to:
- Build winback campaign target lists
- Identify dormant accounts before they churn
- Prioritize reactivation outreach by revenue potential
- Analyze reactivation candidates by industry/segment
- Support re-engagement campaigns with data

Do NOT use when:
- You need active at-risk detection (use at-risk-detection skill)
- You need current health scoring (use health-based queries)
- You need pipeline analysis (use pipeline-analysis skill)

---

## Platform Configuration

Configure this skill for your data environment:

```yaml
configuration:
  # Data source settings
  data_source: snowflake | bigquery | salesforce | hubspot
  
  # Primary tables
  customer_table: "{schema}.{customer_health_table}"
  activity_table: "{schema}.{events_table}" | null
  
  # Account fields
  account_id_field: "account_id"
  account_name_field: "account_name"
  
  # Revenue configuration
  revenue_field: "arr" | "mrr" | "revenue" | "total_contract_value"
  revenue_type: "arr" | "mrr"
  
  # Health tracking
  health_score_field: "health_score"
  health_status_field: "health_status"
  churned_status_values: ["Churned", "Cancelled", "Closed Lost", "Lost"]
  at_risk_status_values: ["At-Risk", "Red", "Critical"]
  
  # Activity tracking
  last_activity_field: "last_activity_date" | null
  
  # Segmentation fields
  tier_field: "customer_tier" | "plan_tier" | null
  industry_field: "industry" | "segment" | "vertical" | null
  owner_field: "cs_owner" | "account_owner"
  
  # Date filtering
  snapshot_date_field: "report_date" | "snapshot_date"
  
  # Revenue tiers (customize for your business)
  revenue_tiers:
    enterprise:
      min: 50000
      label: "Enterprise"
    mid_market:
      min: 15000
      label: "Mid-Market"
    smb:
      min: 0
      label: "SMB"
  
  # Thresholds
  thresholds:
    min_revenue: 5000              # Minimum historical revenue
    days_inactive_dormant: 90      # Days for dormant classification
    days_inactive_high_risk: 30    # Days for high-risk classification
    low_health_threshold: 40       # Health score threshold
    
  # Reactivation scoring weights
  scoring_weights:
    recency: 30                    # Max points for recency
    revenue: 30                    # Max points for historical revenue
    health_at_exit: 20             # Max points for exit health
    engagement_history: 20         # Max points for past engagement
```

---

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `min_revenue` | number | no | config.thresholds.min_revenue | Minimum historical revenue |
| `days_inactive_threshold` | number | no | 90 | Days since last activity for dormant flag |
| `include_churned` | boolean | no | true | Include fully churned accounts |
| `include_dormant` | boolean | no | true | Include dormant but active accounts |
| `limit` | number | no | 100 | Maximum accounts to return |

---

## Process

### Step 1: Query Churned High-Revenue Accounts

#### Snowflake SQL

```sql
SELECT 
    {account_id_field} AS account_id,
    {account_name_field} AS account_name,
    {revenue_field} AS last_revenue,
    {health_status_field} AS health_status,
    {health_score_field} AS health_score,
    {owner_field} AS owner,
    {industry_field} AS industry,
    {tier_field} AS tier
FROM {customer_table}
WHERE {snapshot_date_field} = (SELECT MAX({snapshot_date_field}) FROM {customer_table})
  AND {health_status_field} IN (:churned_status_values)
  AND {revenue_field} >= :min_revenue
ORDER BY {revenue_field} DESC
LIMIT :limit;
```

#### BigQuery SQL

```sql
SELECT 
    {account_id_field} AS account_id,
    {account_name_field} AS account_name,
    {revenue_field} AS last_revenue,
    {health_status_field} AS health_status,
    {health_score_field} AS health_score,
    {owner_field} AS owner,
    {industry_field} AS industry,
    {tier_field} AS tier
FROM `{project}.{dataset}.{customer_table}`
WHERE {snapshot_date_field} = (SELECT MAX({snapshot_date_field}) FROM `{project}.{dataset}.{customer_table}`)
  AND {health_status_field} IN UNNEST(@churned_status_values)
  AND {revenue_field} >= @min_revenue
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
    Industry,
    Customer_Tier__c
FROM Account
WHERE Health_Status__c IN :churnedStatusValues
  AND AnnualRevenue >= :minRevenue
ORDER BY AnnualRevenue DESC
LIMIT :recordLimit
```

#### HubSpot API Filter

```json
{
  "filterGroups": [{
    "filters": [
      {
        "propertyName": "lifecyclestage",
        "operator": "IN",
        "values": ["churned", "lost"]
      },
      {
        "propertyName": "annualrevenue",
        "operator": "GTE",
        "value": "{min_revenue}"
      }
    ]
  }],
  "properties": [
    "name", "annualrevenue", "health_status", "health_score",
    "hubspot_owner_id", "industry", "customer_tier"
  ],
  "sorts": [{"propertyName": "annualrevenue", "direction": "DESCENDING"}],
  "limit": 100
}
```

### Step 2: Query Dormant Active Accounts

```sql
SELECT 
    {account_id_field} AS account_id,
    {account_name_field} AS account_name,
    {revenue_field} AS revenue,
    {health_score_field} AS health_score,
    {health_status_field} AS health_status,
    {owner_field} AS owner,
    {industry_field} AS industry
FROM {customer_table}
WHERE {snapshot_date_field} = (SELECT MAX({snapshot_date_field}) FROM {customer_table})
  AND {revenue_field} > 0
  AND {health_score_field} < :low_health_threshold
  AND {health_status_field} NOT IN (:churned_status_values)
ORDER BY {revenue_field} DESC
LIMIT :limit;
```

### Step 3: Calculate Time Since Last Activity

```sql
WITH last_activity AS (
    SELECT 
        {account_id_field},
        MAX({activity_timestamp_field}) AS last_event
    FROM {activity_table}
    GROUP BY 1
)
SELECT 
    CASE 
        WHEN DATEDIFF('day', l.last_event, CURRENT_DATE()) <= 7 THEN 'Active (0-7 days)'
        WHEN DATEDIFF('day', l.last_event, CURRENT_DATE()) <= 30 THEN 'Recent (8-30 days)'
        WHEN DATEDIFF('day', l.last_event, CURRENT_DATE()) <= 90 THEN 'Dormant (31-90 days)'
        ELSE 'Inactive (90+ days)'
    END AS activity_status,
    COUNT(DISTINCT c.{account_id_field}) AS accounts,
    SUM(c.{revenue_field}) AS total_revenue
FROM {customer_table} c
LEFT JOIN last_activity l ON c.{account_id_field} = l.{account_id_field}
WHERE c.{snapshot_date_field} = (SELECT MAX({snapshot_date_field}) FROM {customer_table})
  AND c.{revenue_field} > 0
GROUP BY 1
ORDER BY 1;
```

### Step 4: Analyze by Industry/Segment

```sql
SELECT 
    COALESCE({industry_field}, 'Unassigned') AS industry,
    COUNT(CASE WHEN {health_status_field} IN (:at_risk_status_values) OR {health_status_field} IN (:churned_status_values) THEN 1 END) AS reactivation_candidates,
    SUM(CASE WHEN {health_status_field} IN (:at_risk_status_values) OR {health_status_field} IN (:churned_status_values) THEN {revenue_field} ELSE 0 END) AS potential_revenue
FROM {customer_table}
WHERE {snapshot_date_field} = (SELECT MAX({snapshot_date_field}) FROM {customer_table})
  AND {revenue_field} > 0
GROUP BY 1
ORDER BY potential_revenue DESC;
```

### Step 5: Analyze by Revenue Tier

```sql
SELECT 
    CASE 
        WHEN {revenue_field} >= :enterprise_min THEN 'Enterprise'
        WHEN {revenue_field} >= :mid_market_min THEN 'Mid-Market'
        ELSE 'SMB'
    END AS tier,
    COUNT(CASE WHEN {health_score_field} < :low_health_threshold THEN 1 END) AS low_health_count,
    SUM(CASE WHEN {health_score_field} < :low_health_threshold THEN {revenue_field} ELSE 0 END) AS low_health_revenue
FROM {customer_table}
WHERE {snapshot_date_field} = (SELECT MAX({snapshot_date_field}) FROM {customer_table})
  AND {revenue_field} > 0
GROUP BY 1
ORDER BY 1;
```

### Step 6: Calculate Reactivation Likelihood Score

```python
def calculate_reactivation_score(account, config):
    weights = config["scoring_weights"]
    revenue_tiers = config["revenue_tiers"]
    thresholds = config["thresholds"]
    
    score = 0
    
    # Recency score (0-30 points)
    days_since = account.get("days_since_activity", 365)
    if days_since <= 30:
        score += weights["recency"]
    elif days_since <= 90:
        score += weights["recency"] * 0.67
    elif days_since <= 180:
        score += weights["recency"] * 0.33
    
    # Historical revenue score (0-30 points)
    revenue = account.get("last_revenue", 0)
    if revenue >= revenue_tiers["enterprise"]["min"]:
        score += weights["revenue"]
    elif revenue >= revenue_tiers["mid_market"]["min"]:
        score += weights["revenue"] * 0.75
    else:
        score += weights["revenue"] * 0.25
    
    # Health at exit score (0-20 points)
    # Higher exit health = likely external factors, more reactivatable
    health_at_exit = account.get("health_score", 0)
    if health_at_exit >= 50:
        score += weights["health_at_exit"]
    elif health_at_exit >= 30:
        score += weights["health_at_exit"] * 0.5
    
    # Engagement history (0-20 points)
    # Based on total historical engagement or tenure
    engagement_score = account.get("engagement_percentile", 50)
    score += (engagement_score / 100) * weights["engagement_history"]
    
    # Determine likelihood category
    if score >= 70:
        likelihood = "HIGH"
    elif score >= 40:
        likelihood = "MEDIUM"
    else:
        likelihood = "LOW"
    
    return {
        "reactivation_score": round(score),
        "reactivation_likelihood": likelihood
    }
```

### Step 7: Generate Priority List and Recommendations

```python
def generate_recommendations(summary, priority_list, config):
    recommendations = []
    
    # Enterprise dormant accounts
    enterprise_dormant = [a for a in priority_list 
                         if a["tier"] == "Enterprise" 
                         and a.get("days_since_activity", 0) > 30]
    if enterprise_dormant:
        total_rev = sum(a["last_revenue"] for a in enterprise_dormant)
        recommendations.append(
            f"{len(enterprise_dormant)} Enterprise accounts dormant 30+ days "
            f"represent ${total_rev:,} recovery potential - prioritize outreach"
        )
    
    # Industry concentration
    if summary.get("top_industry"):
        recommendations.append(
            f"{summary['top_industry']['name']} vertical has highest concentration - "
            "consider industry-specific winback messaging"
        )
    
    # Long-inactive accounts
    long_inactive = [a for a in priority_list if a.get("days_since_activity", 0) > 90]
    if long_inactive:
        total_rev = sum(a["last_revenue"] for a in long_inactive)
        recommendations.append(
            f"{len(long_inactive)} accounts inactive 90+ days (${total_rev:,}) "
            "may require new champion identification"
        )
    
    # Top account concentration
    top_10_rev = sum(a["last_revenue"] for a in priority_list[:10])
    total_rev = sum(a["last_revenue"] for a in priority_list)
    if total_rev > 0 and (top_10_rev / total_rev) > 0.3:
        recommendations.append(
            f"Top 10 accounts represent {(top_10_rev/total_rev)*100:.0f}% of potential revenue - "
            "assign to senior CSMs"
        )
    
    return recommendations
```

---

## Output Schema

```json
{
  "summary": {
    "total_candidates": "number",
    "total_potential_revenue": "number",
    "churned_accounts": "number",
    "dormant_accounts": "number",
    "avg_days_since_activity": "number"
  },
  "by_tier": {
    "Enterprise": { "count": "number", "revenue": "number" },
    "Mid-Market": { "count": "number", "revenue": "number" },
    "SMB": { "count": "number", "revenue": "number" }
  },
  "by_industry": [
    {
      "industry": "string",
      "candidate_count": "number",
      "potential_revenue": "number"
    }
  ],
  "activity_distribution": {
    "active_0_7_days": { "accounts": "number", "revenue": "number" },
    "recent_8_30_days": { "accounts": "number", "revenue": "number" },
    "dormant_31_90_days": { "accounts": "number", "revenue": "number" },
    "inactive_90_plus_days": { "accounts": "number", "revenue": "number" }
  },
  "priority_list": [
    {
      "account_id": "string",
      "account_name": "string",
      "last_revenue": "number",
      "health_status": "string",
      "health_score": "number",
      "days_since_activity": "number",
      "reactivation_score": "number (0-100)",
      "reactivation_likelihood": "HIGH | MEDIUM | LOW",
      "owner": "string",
      "industry": "string",
      "tier": "string",
      "recommended_action": "string"
    }
  ],
  "recommendations": ["string"]
}
```

---

## Quality Criteria

- [ ] Query executes without error
- [ ] All candidates meet min_revenue threshold
- [ ] Reactivation scores calculated correctly
- [ ] Priority list ordered by potential value
- [ ] Recommendations actionable and specific
- [ ] No duplicate accounts in results

---

## Example Usage

**Find reactivation candidates with revenue >= $10K:**
```
Use reactivation-detection skill with min_revenue=10000
```

**Focus on dormant accounts only:**
```
Detect reactivation candidates with include_churned=false, include_dormant=true
```

**Enterprise reactivation priority list:**
```
Run reactivation-detection with min_revenue=50000, limit=50
```

---

## Sample Output

```json
{
  "summary": {
    "total_candidates": 156,
    "total_potential_revenue": 2450000,
    "churned_accounts": 42,
    "dormant_accounts": 114,
    "avg_days_since_activity": 67
  },
  "by_tier": {
    "Enterprise": { "count": 28, "revenue": 1120000 },
    "Mid-Market": { "count": 45, "revenue": 720000 },
    "SMB": { "count": 83, "revenue": 610000 }
  },
  "by_industry": [
    { "industry": "Retail", "candidate_count": 38, "potential_revenue": 680000 },
    { "industry": "Technology", "candidate_count": 29, "potential_revenue": 520000 },
    { "industry": "Healthcare", "candidate_count": 24, "potential_revenue": 410000 }
  ],
  "activity_distribution": {
    "active_0_7_days": { "accounts": 12, "revenue": 180000 },
    "recent_8_30_days": { "accounts": 28, "revenue": 340000 },
    "dormant_31_90_days": { "accounts": 67, "revenue": 890000 },
    "inactive_90_plus_days": { "accounts": 49, "revenue": 1040000 }
  },
  "priority_list": [
    {
      "account_id": "A-98765",
      "account_name": "BigRetail Co",
      "last_revenue": 156000,
      "health_status": "At-Risk",
      "health_score": 28,
      "days_since_activity": 45,
      "reactivation_score": 75,
      "reactivation_likelihood": "HIGH",
      "owner": "Sarah Johnson",
      "industry": "Retail",
      "tier": "Enterprise",
      "recommended_action": "Executive outreach - recent dormancy with high historical value"
    },
    {
      "account_id": "A-87654",
      "account_name": "MediaGroup Inc",
      "last_revenue": 89000,
      "health_status": "Churned",
      "health_score": 0,
      "days_since_activity": 120,
      "reactivation_score": 55,
      "reactivation_likelihood": "MEDIUM",
      "owner": "Mike Chen",
      "industry": "Media",
      "tier": "Mid-Market",
      "recommended_action": "Winback campaign - 4 months since churn, assess new use cases"
    }
  ],
  "recommendations": [
    "28 Enterprise accounts dormant 31-90 days represent $890K recovery potential - prioritize outreach",
    "Retail vertical has highest concentration - consider industry-specific winback messaging",
    "49 accounts inactive 90+ days ($1.04M) may require new champion identification",
    "Top 10 accounts represent 42% of potential revenue - assign to senior CSMs"
  ]
}
```

---

## Known Limitations

1. **Point-in-time snapshot** - uses latest report date only
2. **Activity data completeness** - depends on event tracking
3. **Churn reason not always captured** - manual enrichment may be needed
4. **Reactivation score is heuristic** - not ML-based prediction

---

## Related Skills

- `at-risk-detection` - Active at-risk identification
- `dormant-detection` - Engagement-based dormancy
- `churn-prediction` - Imminent churn signals

---

## Notes

- Run monthly for winback campaign planning
- Combine with at-risk-detection for full lifecycle view
- Export to CRM for outreach campaigns
- Track reactivation success rate to refine scoring weights
