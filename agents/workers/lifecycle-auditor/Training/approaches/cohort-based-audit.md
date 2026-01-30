# Approach: Cohort-Based Audit

## Overview

Analyzes lifecycle progression by grouping contacts into time-based cohorts. Essential for detecting trends, measuring improvement over time, and identifying seasonal patterns. More sophisticated than static funnel analysis.

## When to Use

Use this approach when:
- Client wants to measure improvement over time
- Seasonal patterns may affect conversion
- Dataset spans 6+ months of contacts
- Need to evaluate impact of past changes
- Large dataset (1000+ contacts) requires sampling

Do NOT use when:
- Dataset has <6 months of history
- Fewer than 50 contacts per cohort
- Client needs a quick snapshot only
- No `createdate` or equivalent timestamp available

## Process

### Step 1: Define Cohorts

Group contacts by their entry date into the CRM.

**Common Cohort Definitions:**
```
Monthly: All contacts created in January 2024
Quarterly: All contacts created in Q1 2024
Weekly: All contacts created in week of Jan 1-7, 2024
```

**Example Cohort Definition:**
```python
cohorts = {
    "2024-Q1": contacts.filter(createdate >= "2024-01-01" AND createdate < "2024-04-01"),
    "2024-Q2": contacts.filter(createdate >= "2024-04-01" AND createdate < "2024-07-01"),
    "2024-Q3": contacts.filter(createdate >= "2024-07-01" AND createdate < "2024-10-01"),
    "2024-Q4": contacts.filter(createdate >= "2024-10-01" AND createdate < "2025-01-01")
}
```

### Step 2: Calculate Per-Cohort Metrics

For each cohort, calculate:
- Stage distribution at time T (e.g., 90 days after entry)
- Conversion rates through funnel
- Velocity (average days to progress)

**Example:**
```json
{
  "cohort": "2024-Q2",
  "contacts": 342,
  "at_90_days": {
    "reached_mql": 0.45,
    "reached_sql": 0.22,
    "reached_customer": 0.08
  },
  "avg_days_to_customer": 67
}
```

### Step 3: Compare Across Cohorts

Identify trends by comparing equivalent metrics.

**Trend Analysis:**
```json
{
  "metric": "lead_to_mql_conversion",
  "by_cohort": {
    "2024-Q1": 0.38,
    "2024-Q2": 0.42,
    "2024-Q3": 0.45,
    "2024-Q4": 0.51
  },
  "trend": "improving",
  "slope": "+0.043 per quarter"
}
```

### Step 4: Maturity Adjustment

Newer cohorts haven't had time to progress. Adjust expectations accordingly.

**Maturity Rules:**
```
Cohort age < 30 days: Only measure subscriber -> lead
Cohort age 30-60 days: Can measure through MQL
Cohort age 60-90 days: Can measure through SQL
Cohort age 90+ days: Can measure full funnel to customer
```

**Example Adjustment:**
```json
{
  "cohort": "2024-Q4",
  "age_days": 45,
  "maturity": "partial",
  "measurable_stages": ["subscriber", "lead", "mql"],
  "note": "Customer conversion not yet measurable - cohort too new"
}
```

### Step 5: Identify Anomalies

Flag cohorts that deviate significantly from trend.

**Anomaly Detection:**
```
IF cohort_rate < (trend_average - 2 * std_dev):
    FLAG as "underperforming"
    INVESTIGATE external factors (campaign changes, market events)
ELIF cohort_rate > (trend_average + 2 * std_dev):
    FLAG as "outperforming"
    INVESTIGATE success factors to replicate
```

## Expected Outcomes

When executed correctly, this approach produces:
- Cohort-by-cohort conversion metrics
- Trend lines for key metrics over time
- Velocity metrics (time to convert)
- Anomaly identification with investigation prompts
- Seasonal pattern detection
- Impact assessment of historical changes

## Quality Indicators

**Good execution looks like:**
- Cohorts have minimum 50 contacts each
- Maturity adjustments are applied correctly
- Trends include confidence intervals
- Anomalies are explained with context

**Warning signs:**
- Comparing immature cohorts on metrics they can't show yet
- Cohorts with <20 contacts used for rate calculations
- No consideration of external factors for anomalies
- Missing velocity metrics

## Real Example

### Input
```json
{
  "tenant_id": "techstartup_inc",
  "limit": 2000,
  "analysis_type": "cohort",
  "cohort_period": "quarterly",
  "cohorts_to_analyze": 4
}
```

### Output
```json
{
  "summary": {
    "total_contacts": 1847,
    "cohorts_analyzed": 4,
    "trend_direction": "improving",
    "health_score": 0.78
  },
  "cohorts": [
    {
      "period": "2024-Q1",
      "contacts": 423,
      "mql_rate": 0.38,
      "sql_rate": 0.18,
      "customer_rate": 0.06,
      "avg_velocity_days": 78
    },
    {
      "period": "2024-Q2",
      "contacts": 512,
      "mql_rate": 0.42,
      "sql_rate": 0.21,
      "customer_rate": 0.08,
      "avg_velocity_days": 71
    },
    {
      "period": "2024-Q3",
      "contacts": 498,
      "mql_rate": 0.47,
      "sql_rate": 0.24,
      "customer_rate": 0.09,
      "avg_velocity_days": 64
    },
    {
      "period": "2024-Q4",
      "contacts": 414,
      "mql_rate": 0.51,
      "sql_rate": null,
      "customer_rate": null,
      "maturity_note": "Cohort age 45 days - full funnel not yet measurable"
    }
  ],
  "trends": {
    "mql_rate": {
      "direction": "improving",
      "change": "+34% (Q1 to Q4)",
      "quarterly_growth": "+8.5%"
    },
    "velocity": {
      "direction": "improving",
      "change": "-18% faster (78 to 64 days)",
      "quarterly_improvement": "-4.7 days"
    }
  },
  "anomalies": [],
  "insights": [
    "Q3 process changes (sales enablement training) appear to have accelerated velocity significantly",
    "MQL conversion improvement correlates with lead scoring model update in April 2024"
  ]
}
```

### Why This Works
The example demonstrates good execution because:
1. Each cohort has 400+ contacts (well above 50 minimum)
2. Q4 metrics correctly marked as partial due to maturity
3. Trends quantified with specific percentages
4. Insights link metrics to known historical changes

## Common Mistakes

1. **Mistake**: Comparing full-funnel metrics for cohorts of different ages
   **Fix**: Only compare metrics appropriate to cohort maturity

2. **Mistake**: Using calendar months when sales cycle is 90+ days
   **Fix**: Use quarterly cohorts for long sales cycles

3. **Mistake**: Ignoring statistical significance in trend claims
   **Fix**: Note when cohort sizes or variance make trends uncertain

## Related Approaches

- [Funnel Analysis](./funnel-analysis.md) - Use for quick snapshot without trend context
- [Decision Tree](./decision-tree.md) - For choosing between approaches
