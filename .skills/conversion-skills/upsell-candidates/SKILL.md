---
name: upsell-candidates
description: |
  Identify customers ready for tier upgrade based on feature adoption and engagement signals.
  Use when asked to 'find upsell candidates', 'identify upgrade ready accounts', 
  'tier upgrade opportunities', or 'expansion revenue targets'.
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
  estimated_runtime: "1-2min"
  max_cost: "$0.25"
  client_facing: true
  requires_human_review: false
  tags:
    - sales
    - upsell
    - expansion
    - customer-intelligence
    - platform-agnostic
allowed-tools: Read Write CallMcpTool
---

# Upsell Candidates Skill

Identify customers who are ready for tier upgrade based on feature adoption, engagement patterns, and usage signals.

## When to Use

Use this skill when you need to:
- Find expansion revenue opportunities
- Prioritize accounts for upgrade outreach
- Build upsell campaign lists
- Identify power users ready for premium features

---

## Platform Configuration

Configure this skill for your data environment:

```yaml
configuration:
  # Data source settings
  data_source: snowflake | bigquery | salesforce | hubspot
  
  # Table/object mappings
  customer_table: "{schema}.{customer_table}"
  product_adoption_table: "{schema}.{adoption_table}"  # Optional: separate adoption data
  
  # Account identification
  account_id_field: "account_id"
  account_name_field: "account_name"
  
  # Tier/plan configuration
  current_tier_field: "plan_tier" | "subscription_tier" | "product_tier"
  tier_values:
    entry: ["free", "starter", "basic"]
    mid: ["pro", "professional", "growth"]
    top: ["enterprise", "premium", "unlimited"]
  target_upgrade_from: ["free", "starter", "pro"]  # Tiers eligible for upgrade
  target_upgrade_to: ["pro", "enterprise"]          # Target upgrade tiers
  
  # Revenue configuration
  revenue_field: "arr" | "mrr" | "revenue"
  revenue_type: "arr" | "mrr"
  
  # Feature adoption signals
  feature_count_field: "active_features" | "feature_count"
  feature_flags:
    - field: "has_api_access"
      weight: 20
      premium_indicator: true
    - field: "has_custom_branding"
      weight: 15
      premium_indicator: true
    - field: "has_sso"
      weight: 15
      premium_indicator: true
    - field: "has_analytics"
      weight: 10
      premium_indicator: false
  
  # Health/engagement
  health_score_field: "health_score" | null
  
  # Owner assignment
  owner_field: "cs_owner" | "account_owner"
  
  # Thresholds
  thresholds:
    min_feature_count: 5          # Minimum features to qualify
    min_health_score: 50          # Minimum health for upgrade readiness
    min_revenue_current: 1000     # Minimum current revenue
    upsell_score_threshold: 60    # Minimum score to recommend
```

---

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `min_features` | number | no | config.thresholds.min_feature_count | Minimum feature flags active |
| `current_tier` | string | no | null | Filter by current tier |
| `limit` | number | no | 100 | Maximum results |
| `exclude_demo` | boolean | no | true | Exclude demo/trial accounts |

---

## Upsell Signals

| Signal | Weight | Description |
|--------|--------|-------------|
| Feature count at threshold | High | Using multiple features near plan limit |
| Premium feature usage | High | Using features available in higher tiers |
| High engagement | Medium | Active usage patterns |
| Good health score | Medium | Engaged, not at-risk |
| Recent activity | Medium | Active in last 30 days |
| Usage growth | Medium | Increasing usage over time |

---

## Process

### Step 1: Query Upsell Candidates

Select the appropriate query template based on your configured data source:

#### Snowflake SQL

```sql
SELECT 
    c.{account_id_field} AS account_id,
    c.{account_name_field} AS account_name,
    c.{current_tier_field} AS current_tier,
    pa.{feature_count_field} AS feature_count,
    pa.has_api_access,
    pa.has_custom_branding,
    pa.has_sso,
    pa.has_analytics,
    c.{revenue_field} AS current_revenue,
    c.{health_score_field} AS health_score,
    c.{owner_field} AS owner
FROM {customer_table} c
LEFT JOIN {product_adoption_table} pa 
    ON c.{account_id_field} = pa.{account_id_field}
WHERE c.{current_tier_field} IN (:target_upgrade_from)
  AND pa.{feature_count_field} >= :min_features
  AND c.{health_score_field} >= :min_health_score
ORDER BY pa.{feature_count_field} DESC, c.{revenue_field} DESC
LIMIT :limit;
```

#### BigQuery SQL

```sql
SELECT 
    c.{account_id_field} AS account_id,
    c.{account_name_field} AS account_name,
    c.{current_tier_field} AS current_tier,
    pa.{feature_count_field} AS feature_count,
    pa.has_api_access,
    pa.has_custom_branding,
    c.{revenue_field} AS current_revenue,
    c.{health_score_field} AS health_score,
    c.{owner_field} AS owner
FROM `{project}.{dataset}.{customer_table}` c
LEFT JOIN `{project}.{dataset}.{adoption_table}` pa 
    ON c.{account_id_field} = pa.{account_id_field}
WHERE c.{current_tier_field} IN UNNEST(@target_upgrade_from)
  AND pa.{feature_count_field} >= @min_features
ORDER BY pa.{feature_count_field} DESC, c.{revenue_field} DESC
LIMIT @limit;
```

#### Salesforce SOQL

```sql
SELECT 
    Id,
    Name,
    Plan_Tier__c,
    Feature_Count__c,
    Has_API_Access__c,
    Has_Custom_Branding__c,
    AnnualRevenue,
    Health_Score__c,
    OwnerId,
    Owner.Name
FROM Account
WHERE Plan_Tier__c IN :targetUpgradeFrom
  AND Feature_Count__c >= :minFeatures
  AND Health_Score__c >= :minHealthScore
ORDER BY Feature_Count__c DESC, AnnualRevenue DESC
LIMIT :recordLimit
```

#### HubSpot API Filter

```json
{
  "filterGroups": [{
    "filters": [
      {
        "propertyName": "plan_tier",
        "operator": "IN",
        "values": ["starter", "pro"]
      },
      {
        "propertyName": "feature_count",
        "operator": "GTE",
        "value": "5"
      },
      {
        "propertyName": "health_score",
        "operator": "GTE",
        "value": "50"
      }
    ]
  }],
  "properties": [
    "name", "plan_tier", "feature_count", "annualrevenue",
    "health_score", "hubspot_owner_id", "has_api_access"
  ],
  "sorts": [{"propertyName": "feature_count", "direction": "DESCENDING"}],
  "limit": 100
}
```

### Step 2: Score Candidates

```python
def calculate_upsell_score(candidate, config):
    score = 0
    
    # Feature adoption score (0-40 points)
    feature_count = candidate.get("feature_count", 0)
    score += min(feature_count * 5, 40)
    
    # Health bonus (0-20 points)
    health_score = candidate.get("health_score", 0)
    score += (health_score / 100) * 20
    
    # Premium feature usage (0-40 points from config weights)
    for feature_flag in config["feature_flags"]:
        if candidate.get(feature_flag["field"]):
            score += feature_flag["weight"]
    
    return min(score, 100)  # Cap at 100

for candidate in candidates:
    candidate["upsell_score"] = calculate_upsell_score(candidate, config)
```

### Step 3: Generate Recommendations

Based on patterns:
- High feature count + premium feature usage → "Ready for enterprise tier"
- High usage + no premium features → "Premium feature upsell opportunity"
- Good health + hitting limits → "Plan upgrade candidate"

---

## Output Schema

```json
{
  "summary": {
    "total_candidates": "number",
    "avg_feature_count": "number",
    "total_current_revenue": "number",
    "estimated_upsell_revenue": "number"
  },
  "candidates": [
    {
      "account_id": "string",
      "account_name": "string",
      "current_tier": "string",
      "feature_count": "number",
      "current_revenue": "number",
      "health_score": "number",
      "owner": "string",
      "upsell_score": "number",
      "top_features": ["string"],
      "recommendation": "string",
      "suggested_tier": "string"
    }
  ],
  "by_owner": [
    {
      "owner": "string",
      "candidate_count": "number",
      "total_potential_revenue": "number"
    }
  ]
}
```

---

## Example Usage

**Find top 50 upsell candidates:**
```
Find upsell candidates with at least 5 features, limit 50
```

**Power users ready for enterprise:**
```
Identify upsell candidates using API access on starter tier
```

---

## Sample Output

```json
{
  "summary": {
    "total_candidates": 127,
    "avg_feature_count": 6.8,
    "total_current_revenue": 890000,
    "estimated_upsell_revenue": 445000
  },
  "candidates": [
    {
      "account_id": "ACCT-12345",
      "account_name": "TechStartup Inc",
      "current_tier": "pro",
      "feature_count": 8,
      "current_revenue": 24000,
      "health_score": 78,
      "owner": "Sarah Johnson",
      "upsell_score": 95,
      "top_features": ["custom_branding", "analytics", "api_access"],
      "recommendation": "Ready for enterprise tier - using 8 features including API",
      "suggested_tier": "enterprise"
    }
  ]
}
```

---

## Field Mapping Examples

### SaaS Product (Snowflake)
```yaml
configuration:
  data_source: snowflake
  customer_table: "analytics.customers"
  product_adoption_table: "analytics.feature_usage"
  current_tier_field: "subscription_plan"
  tier_values:
    entry: ["free", "starter"]
    mid: ["professional"]
    top: ["enterprise", "enterprise_plus"]
  thresholds:
    min_feature_count: 4
    min_health_score: 60
```

### B2B Platform (Salesforce)
```yaml
configuration:
  data_source: salesforce
  customer_table: "Account"
  current_tier_field: "Plan_Tier__c"
  revenue_field: "AnnualRevenue"
  feature_flags:
    - field: "Has_API_Integration__c"
      weight: 25
    - field: "Has_SSO__c"
      weight: 20
```

---

## Quality Criteria

- [ ] Only accounts on upgrade-eligible tiers included
- [ ] Feature count threshold applied
- [ ] Scores calculated consistently
- [ ] Recommendations relevant to usage patterns

---

## Notes

- Run weekly for expansion revenue planning
- Coordinate with sales on outreach timing
- Track conversion rates to refine scoring weights
- Consider seasonal patterns in upgrade propensity
