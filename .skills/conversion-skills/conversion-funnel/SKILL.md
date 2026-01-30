---
name: conversion-funnel
description: |
  Analyze the customer conversion funnel for an account: impressions → engagements → actions → conversions.
  Use when asked to 'analyze funnel', 'check conversion rates', 'find drop-off points',
  'review engagement to conversion', or 'diagnose funnel leakage'.
license: Proprietary
compatibility:
  - Snowflake MCP
  - BigQuery
  - Salesforce
  - HubSpot MCP
  - Google Analytics
metadata:
  author: mh1-engineering
  version: "2.0.0"
  status: active
  estimated_runtime: "30s-1min"
  max_cost: "$0.25"
  client_facing: true
  requires_human_review: false
  tags:
    - funnel
    - conversion
    - analytics
    - platform-agnostic
allowed-tools: Read Write CallMcpTool
---

# Conversion Funnel Skill

Analyze the event funnel to identify where users drop off between engagement stages.

## When to Use

Use this skill when you need to:
- Identify where users drop off in the funnel
- Calculate stage-to-stage conversion rates
- Diagnose poor conversion performance
- Benchmark account performance against targets
- Recommend optimization strategies

Do NOT use when:
- You need aggregate funnel data across all accounts (use aggregate reports)
- You're analyzing non-event-based conversion flows

---

## Platform Configuration

Configure this skill for your data environment:

```yaml
configuration:
  # Data source settings
  data_source: snowflake | bigquery | salesforce | hubspot | google_analytics
  
  # Events/activity table
  events_table: "{schema}.{events_table}"
  
  # Account identification  
  account_id_field: "account_id" | "org_id" | "customer_id"
  
  # Event tracking
  event_timestamp_field: "created_at" | "event_timestamp"
  event_type_field: "event_type" | "event_name"
  
  # Funnel stages (customize for your business)
  # Define stages in order from top to bottom of funnel
  funnel_stages:
    - name: "impressions"
      event_types: ["impression", "view", "pageview"]
      description: "Initial exposure"
    - name: "engagements"
      event_types: ["click", "tap", "interact"]
      description: "User interaction"
    - name: "actions"
      event_types: ["signup", "add_to_cart", "start_trial"]
      description: "Intent action"
    - name: "conversions"
      event_types: ["purchase", "subscribe", "convert"]
      description: "Goal completion"
    - name: "exits"
      event_types: ["exit", "bounce", "abandon"]
      description: "Drop-off events"
  
  # Analysis period
  lookback_days: 90
  
  # Benchmarks (customize for your industry/product)
  benchmarks:
    impression_to_engagement: 10   # 10% typical
    engagement_to_action: 25       # 25% typical
    action_to_conversion: 40       # 40% typical
    overall_conversion: 1          # 1% typical
  
  # Performance thresholds
  thresholds:
    underperforming_ratio: 0.8    # 80% of benchmark = underperforming
    overperforming_ratio: 1.2     # 120% of benchmark = overperforming
```

---

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `account_id` | string | yes | - | The account ID to analyze |
| `lookback_days` | number | no | config.lookback_days | Days of data to analyze |
| `custom_stages` | array | no | null | Override default funnel stages |

---

## Process

### Step 1: Query Funnel Events

Select the appropriate query based on your data source:

#### Snowflake SQL

```sql
SELECT 
    {account_id_field} AS account_id,
    {event_type_field} AS event_type,
    COUNT(*) AS event_count
FROM {events_table}
WHERE {account_id_field} = :account_id
  AND {event_timestamp_field} > DATEADD(day, -:lookback_days, CURRENT_DATE())
GROUP BY 1, 2;
```

Then aggregate by stage:

```sql
SELECT 
    {account_id_field} AS account_id,
    SUM(CASE WHEN {event_type_field} IN (:impression_types) THEN 1 ELSE 0 END) AS impressions,
    SUM(CASE WHEN {event_type_field} IN (:engagement_types) THEN 1 ELSE 0 END) AS engagements,
    SUM(CASE WHEN {event_type_field} IN (:action_types) THEN 1 ELSE 0 END) AS actions,
    SUM(CASE WHEN {event_type_field} IN (:conversion_types) THEN 1 ELSE 0 END) AS conversions,
    SUM(CASE WHEN {event_type_field} IN (:exit_types) THEN 1 ELSE 0 END) AS exits
FROM {events_table}
WHERE {account_id_field} = :account_id
  AND {event_timestamp_field} > DATEADD(day, -:lookback_days, CURRENT_DATE())
GROUP BY 1;
```

#### BigQuery SQL

```sql
SELECT 
    {account_id_field} AS account_id,
    COUNTIF({event_type_field} IN UNNEST(@impression_types)) AS impressions,
    COUNTIF({event_type_field} IN UNNEST(@engagement_types)) AS engagements,
    COUNTIF({event_type_field} IN UNNEST(@action_types)) AS actions,
    COUNTIF({event_type_field} IN UNNEST(@conversion_types)) AS conversions,
    COUNTIF({event_type_field} IN UNNEST(@exit_types)) AS exits
FROM `{project}.{dataset}.{events_table}`
WHERE {account_id_field} = @account_id
  AND {event_timestamp_field} > DATE_SUB(CURRENT_DATE(), INTERVAL @lookback_days DAY)
GROUP BY 1;
```

#### Salesforce (Campaign/Opportunity based)

```sql
SELECT 
    AccountId,
    COUNT(CASE WHEN StageName = 'Awareness' THEN 1 END) AS impressions,
    COUNT(CASE WHEN StageName = 'Interest' THEN 1 END) AS engagements,
    COUNT(CASE WHEN StageName = 'Decision' THEN 1 END) AS actions,
    COUNT(CASE WHEN StageName = 'Closed Won' THEN 1 END) AS conversions,
    COUNT(CASE WHEN StageName = 'Closed Lost' THEN 1 END) AS exits
FROM Opportunity
WHERE AccountId = :accountId
  AND CreatedDate >= LAST_N_DAYS:90
GROUP BY AccountId
```

#### HubSpot API

```json
{
  "filterGroups": [{
    "filters": [
      {
        "propertyName": "associations.company",
        "operator": "EQ",
        "value": "{account_id}"
      }
    ]
  }],
  "properties": ["hs_analytics_source", "hs_analytics_source_data_1"]
}
```

Note: HubSpot requires aggregation by lifecycle stage in post-processing.

### Step 2: Calculate Conversion Rates

```python
def calculate_funnel_rates(funnel_data, config):
    stages = config["funnel_stages"]
    
    # Extract counts (use 0 if missing)
    impressions = funnel_data.get("impressions", 0)
    engagements = funnel_data.get("engagements", 0)
    actions = funnel_data.get("actions", 0)
    conversions = funnel_data.get("conversions", 0)
    exits = funnel_data.get("exits", 0)
    
    # Stage-to-stage rates
    rates = {
        "impression_to_engagement_pct": safe_divide(engagements, impressions) * 100,
        "engagement_to_action_pct": safe_divide(actions, engagements) * 100,
        "action_to_conversion_pct": safe_divide(conversions, actions) * 100,
        "overall_conversion_pct": safe_divide(conversions, impressions) * 100,
        "exit_rate_pct": safe_divide(exits, engagements) * 100 if engagements > 0 else 0
    }
    
    return rates

def safe_divide(numerator, denominator):
    return (numerator / denominator) if denominator > 0 else 0
```

### Step 3: Identify Bottlenecks

```python
def identify_bottlenecks(rates, benchmarks, thresholds):
    bottlenecks = []
    
    stage_mappings = [
        ("impression_to_engagement_pct", "impression_to_engagement", "Impression → Engagement"),
        ("engagement_to_action_pct", "engagement_to_action", "Engagement → Action"),
        ("action_to_conversion_pct", "action_to_conversion", "Action → Conversion")
    ]
    
    for rate_key, benchmark_key, stage_name in stage_mappings:
        actual = rates[rate_key]
        benchmark = benchmarks[benchmark_key]
        
        if actual < benchmark * thresholds["underperforming_ratio"]:
            bottlenecks.append({
                "stage": stage_name,
                "actual": actual,
                "benchmark": benchmark,
                "gap_pct": ((benchmark - actual) / benchmark) * 100
            })
    
    return bottlenecks
```

### Step 4: Generate Recommendations

```python
def generate_recommendations(bottlenecks, rates, funnel_data):
    recommendations = []
    
    for bottleneck in bottlenecks:
        stage = bottleneck["stage"]
        actual = bottleneck["actual"]
        benchmark = bottleneck["benchmark"]
        
        if "Impression → Engagement" in stage:
            recommendations.append(
                f"Impression to engagement rate ({actual:.1f}%) is below benchmark ({benchmark}%). "
                "Consider: improving creative quality, targeting refinement, or landing page optimization."
            )
        elif "Engagement → Action" in stage:
            recommendations.append(
                f"Engagement to action rate ({actual:.1f}%) is below benchmark ({benchmark}%). "
                "Review: CTA clarity, value proposition, friction points in the user journey."
            )
        elif "Action → Conversion" in stage:
            recommendations.append(
                f"Action to conversion rate ({actual:.1f}%) is below benchmark ({benchmark}%). "
                "Optimize: checkout/signup flow, reduce form fields, add trust signals, improve mobile UX."
            )
    
    # Check exit rate
    if rates.get("exit_rate_pct", 0) > 40:
        recommendations.append(
            f"Exit rate is {rates['exit_rate_pct']:.1f}% - consider adding engaging content "
            "or secondary CTAs to reduce bounces."
        )
    
    return recommendations
```

---

## Output Schema

```json
{
  "account_id": "string",
  "period": "string (e.g., 'last 90 days')",
  "funnel": {
    "impressions": "number",
    "engagements": "number",
    "actions": "number",
    "conversions": "number",
    "exits": "number"
  },
  "conversion_rates": {
    "impression_to_engagement_pct": "number",
    "engagement_to_action_pct": "number",
    "action_to_conversion_pct": "number",
    "overall_conversion_pct": "number",
    "exit_rate_pct": "number"
  },
  "benchmarks": {
    "impression_to_engagement": "number",
    "engagement_to_action": "number",
    "action_to_conversion": "number"
  },
  "bottlenecks": [
    {
      "stage": "string",
      "actual": "number",
      "benchmark": "number",
      "gap_pct": "number"
    }
  ],
  "recommendations": ["string"]
}
```

---

## Example Usage

**Analyze funnel for specific account:**
```
Analyze conversion funnel for account_id="ACCT-12345"
```

**Diagnose low conversions:**
```
Use conversion-funnel skill to find drop-off points for account ACCT-12345
```

**Custom lookback period:**
```
Analyze funnel for ACCT-12345 with lookback_days=30
```

---

## Quality Criteria

- [ ] Query executes without error
- [ ] All funnel stages populated
- [ ] Conversion rates calculated correctly (handle div by zero)
- [ ] Bottlenecks identified against benchmarks
- [ ] Recommendations specific to bottleneck type

---

## Sample Output

```json
{
  "account_id": "ACCT-12345",
  "period": "last 90 days",
  "funnel": {
    "impressions": 10000,
    "engagements": 950,
    "actions": 280,
    "conversions": 84,
    "exits": 420
  },
  "conversion_rates": {
    "impression_to_engagement_pct": 9.5,
    "engagement_to_action_pct": 29.5,
    "action_to_conversion_pct": 30.0,
    "overall_conversion_pct": 0.84,
    "exit_rate_pct": 44.2
  },
  "benchmarks": {
    "impression_to_engagement": 10,
    "engagement_to_action": 25,
    "action_to_conversion": 40
  },
  "bottlenecks": [
    {
      "stage": "Action → Conversion",
      "actual": 30.0,
      "benchmark": 40,
      "gap_pct": 25.0
    }
  ],
  "recommendations": [
    "Action to conversion rate (30.0%) is below benchmark (40%). Optimize: checkout/signup flow, reduce form fields, add trust signals, improve mobile UX.",
    "Exit rate is 44.2% - consider adding engaging content or secondary CTAs to reduce bounces."
  ]
}
```

---

## Funnel Stage Examples by Industry

### E-commerce
```yaml
funnel_stages:
  - name: "visits"
    event_types: ["page_view", "session_start"]
  - name: "product_views"
    event_types: ["product_view", "item_view"]
  - name: "add_to_cart"
    event_types: ["add_to_cart"]
  - name: "purchases"
    event_types: ["purchase", "transaction"]
```

### SaaS Trial
```yaml
funnel_stages:
  - name: "visitors"
    event_types: ["page_view"]
  - name: "signups"
    event_types: ["signup", "register"]
  - name: "activations"
    event_types: ["first_use", "onboarding_complete"]
  - name: "conversions"
    event_types: ["subscribe", "upgrade"]
```

### Lead Generation
```yaml
funnel_stages:
  - name: "impressions"
    event_types: ["ad_view", "content_view"]
  - name: "clicks"
    event_types: ["click", "cta_click"]
  - name: "form_starts"
    event_types: ["form_start", "lead_form_open"]
  - name: "submissions"
    event_types: ["form_submit", "lead_submit"]
```

---

## Known Limitations

1. **Configurable lookback** - defaults to 90 days
2. **Event type names must match** - ensure config matches your event taxonomy
3. **Single account only** - cannot compare across accounts in one call

---

## Related Skills

- `engagement-velocity` - Period-over-period engagement changes
- `at-risk-detection` - Account health monitoring
- `churn-prediction` - Conversion to churn risk

---

## Notes

- Run monthly for campaign performance reviews
- Combine with engagement-velocity for holistic account health
- Export recommendations for client QBRs
- Adjust benchmarks based on industry and product type
