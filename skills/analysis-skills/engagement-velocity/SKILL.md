---
name: engagement-velocity
description: |
  Detect engagement velocity changes by comparing period-over-period activity for accounts.
  Use when asked to 'check engagement velocity', 'detect engagement drop', 'compare weekly activity',
  'find engagement spikes', or 'monitor engagement trends'.
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
  estimated_runtime: "30s-1min"
  max_cost: "$0.25"
  client_facing: true
  requires_human_review: false
  tags:
    - engagement
    - velocity
    - early-warning
    - platform-agnostic
allowed-tools: Read Write CallMcpTool
---

# Engagement Velocity Skill

Compare current period vs previous period engagement to detect early warning signs of engagement drop-off or positive spikes.

## When to Use

Use this skill when you need to:
- Detect early warning signs of engagement decline
- Identify positive engagement spikes worth investigating
- Compare period-over-period activity for a specific account
- Prioritize accounts needing proactive outreach
- Monitor engagement health for key accounts

Do NOT use when:
- You need aggregate engagement across all accounts (use health status distribution)
- You need long-term trend analysis (use session patterns)

---

## Platform Configuration

Configure this skill for your data environment:

```yaml
configuration:
  # Data source settings
  data_source: snowflake | bigquery | salesforce | hubspot
  
  # Activity/events table
  activity_table: "{schema}.{events_table}"
  
  # Account identification
  account_id_field: "account_id" | "org_id" | "customer_id"
  
  # Activity tracking
  activity_timestamp_field: "created_at" | "event_timestamp" | "activity_date"
  activity_type_field: "event_type" | null  # Optional: filter by event type
  activity_types_to_count: ["login", "feature_use", "api_call"] | null  # null = count all
  
  # Comparison settings
  comparison_period: "week" | "month" | "day"
  current_period_days: 7      # Days in current period
  previous_period_days: 7     # Days in previous period
  
  # Velocity thresholds
  thresholds:
    critical_drop_pct: -50    # Percentage drop for critical alert
    declining_pct: -25        # Percentage drop for warning
    growing_pct: 25           # Percentage growth for positive flag
    spike_pct: 50             # Percentage growth for spike alert
    
  # Alert configuration
  alert_levels:
    critical_drop: "critical"
    declining: "warning"
    stable: "none"
    growing: "info"
    spike: "info"
```

---

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `account_id` | string | yes | - | The account ID to analyze |
| `period_days` | number | no | config.current_period_days | Days per comparison period |
| `event_types` | array | no | null | Filter to specific event types |

---

## Process

### Step 1: Query Activity Data for Velocity Calculation

Select the appropriate query based on your data source:

#### Snowflake SQL

```sql
SELECT 
    {account_id_field} AS account_id,
    SUM(CASE 
        WHEN {activity_timestamp_field} > DATEADD(day, -:current_period_days, CURRENT_DATE()) 
        THEN 1 ELSE 0 
    END) AS events_current_period,
    SUM(CASE 
        WHEN {activity_timestamp_field} BETWEEN 
            DATEADD(day, -(:current_period_days + :previous_period_days), CURRENT_DATE()) 
            AND DATEADD(day, -:current_period_days, CURRENT_DATE()) 
        THEN 1 ELSE 0 
    END) AS events_previous_period
FROM {activity_table}
WHERE {account_id_field} = :account_id
  AND {activity_timestamp_field} > DATEADD(day, -(:current_period_days + :previous_period_days), CURRENT_DATE())
  -- Optional event type filter
  AND ({activity_type_field} IN (:event_types) OR :event_types IS NULL)
GROUP BY 1;
```

#### BigQuery SQL

```sql
SELECT 
    {account_id_field} AS account_id,
    COUNTIF({activity_timestamp_field} > DATE_SUB(CURRENT_DATE(), INTERVAL @current_period_days DAY)) AS events_current_period,
    COUNTIF({activity_timestamp_field} BETWEEN 
        DATE_SUB(CURRENT_DATE(), INTERVAL (@current_period_days + @previous_period_days) DAY)
        AND DATE_SUB(CURRENT_DATE(), INTERVAL @current_period_days DAY)
    ) AS events_previous_period
FROM `{project}.{dataset}.{activity_table}`
WHERE {account_id_field} = @account_id
  AND {activity_timestamp_field} > DATE_SUB(CURRENT_DATE(), INTERVAL (@current_period_days + @previous_period_days) DAY)
GROUP BY 1;
```

#### Salesforce SOQL

```sql
SELECT 
    WhatId,
    COUNT(Id) eventCount,
    CALENDAR_WEEK(ActivityDate) week
FROM Task
WHERE WhatId = :accountId
  AND ActivityDate >= LAST_N_DAYS:14
GROUP BY WhatId, CALENDAR_WEEK(ActivityDate)
```

Note: Salesforce requires post-processing to calculate period comparison.

#### HubSpot API (Engagements Endpoint)

```json
{
  "filters": [
    {
      "propertyName": "associations.company",
      "operator": "EQ", 
      "value": "{account_id}"
    }
  ],
  "dateRange": {
    "startDate": "{14_days_ago}",
    "endDate": "{today}"
  }
}
```

Note: HubSpot requires aggregation in post-processing.

### Step 2: Calculate Velocity Metrics

```python
def calculate_velocity(events_current, events_previous, config):
    thresholds = config["thresholds"]
    
    # Calculate week-over-week change
    if events_previous > 0:
        velocity_pct = ((events_current - events_previous) / events_previous) * 100
    else:
        velocity_pct = 100 if events_current > 0 else 0
    
    # Determine status based on thresholds
    if velocity_pct <= thresholds["critical_drop_pct"]:
        status = "CRITICAL_DROP"
        alert_level = config["alert_levels"]["critical_drop"]
    elif velocity_pct <= thresholds["declining_pct"]:
        status = "DECLINING"
        alert_level = config["alert_levels"]["declining"]
    elif velocity_pct >= thresholds["spike_pct"]:
        status = "SPIKE"
        alert_level = config["alert_levels"]["spike"]
    elif velocity_pct >= thresholds["growing_pct"]:
        status = "GROWING"
        alert_level = config["alert_levels"]["growing"]
    else:
        status = "STABLE"
        alert_level = config["alert_levels"]["stable"]
    
    return {
        "events_current_period": events_current,
        "events_previous_period": events_previous,
        "change_pct": round(velocity_pct, 1),
        "status": status,
        "alert_level": alert_level
    }
```

### Step 3: Generate Recommendations

```python
def generate_recommendation(velocity_result, config):
    status = velocity_result["status"]
    change_pct = abs(velocity_result["change_pct"])
    
    recommendations = {
        "CRITICAL_DROP": f"Critical engagement drop detected ({change_pct}% decrease). Immediate outreach required to understand if there are issues or changes in usage patterns.",
        "DECLINING": f"Engagement declining ({change_pct}% decrease). Schedule a check-in to address potential concerns.",
        "STABLE": "Engagement stable. No immediate action needed, continue monitoring.",
        "GROWING": f"Positive engagement growth ({change_pct}% increase). Investigate what's working and consider case study opportunity.",
        "SPIKE": f"Significant engagement spike ({change_pct}% increase). Investigate potential new use case or campaign success."
    }
    
    return recommendations.get(status, "Monitor engagement.")
```

---

## Output Schema

```json
{
  "account_id": "string",
  "period": {
    "current_days": "number",
    "previous_days": "number",
    "comparison_type": "week | month | day"
  },
  "velocity": {
    "events_current_period": "number",
    "events_previous_period": "number",
    "change_pct": "number",
    "status": "CRITICAL_DROP | DECLINING | STABLE | GROWING | SPIKE"
  },
  "recommendation": "string",
  "alert_level": "none | info | warning | critical"
}
```

---

## Example Usage

**Check velocity for specific account:**
```
Check engagement velocity for account_id="ACCT-12345"
```

**Detect engagement drops:**
```
Use engagement-velocity skill to detect drop-off for account ACCT-12345
```

**Monthly comparison:**
```
Check engagement velocity for ACCT-12345 with period_days=30
```

---

## Quality Criteria

- [ ] Query executes without error
- [ ] Both period values returned
- [ ] Velocity percentage calculated correctly
- [ ] Status mapped to appropriate threshold
- [ ] Recommendation actionable and relevant

---

## Sample Output

```json
{
  "account_id": "ACCT-12345",
  "period": {
    "current_days": 7,
    "previous_days": 7,
    "comparison_type": "week"
  },
  "velocity": {
    "events_current_period": 45,
    "events_previous_period": 120,
    "change_pct": -62.5,
    "status": "CRITICAL_DROP"
  },
  "recommendation": "Critical engagement drop detected (62.5% decrease). Immediate outreach required to understand if there are issues or changes in usage patterns.",
  "alert_level": "critical"
}
```

---

## Batch Analysis Extension

To analyze multiple accounts at once:

```sql
-- Top accounts with velocity drops
WITH velocity AS (
    SELECT 
        {account_id_field} AS account_id,
        SUM(CASE WHEN {activity_timestamp_field} > DATEADD(day, -7, CURRENT_DATE()) THEN 1 ELSE 0 END) AS current_events,
        SUM(CASE WHEN {activity_timestamp_field} BETWEEN DATEADD(day, -14, CURRENT_DATE()) AND DATEADD(day, -7, CURRENT_DATE()) THEN 1 ELSE 0 END) AS previous_events
    FROM {activity_table}
    WHERE {activity_timestamp_field} > DATEADD(day, -14, CURRENT_DATE())
    GROUP BY 1
)
SELECT 
    account_id,
    current_events,
    previous_events,
    CASE 
        WHEN previous_events > 0 THEN ROUND(((current_events - previous_events) * 100.0 / previous_events), 1)
        ELSE 0 
    END AS change_pct
FROM velocity
WHERE previous_events > 10  -- Minimum baseline activity
  AND current_events < previous_events * 0.5  -- 50%+ drop
ORDER BY change_pct ASC
LIMIT 50;
```

---

## Known Limitations

1. **Only compares two periods** - does not show longer trends
2. **Event count only** - does not weight by event type importance
3. **Single account per call** - use batch query for multiple accounts

---

## Related Skills

- `at-risk-detection` - Status-based risk identification
- `dormant-detection` - Long-term inactivity detection
- `conversion-funnel` - Funnel-specific engagement analysis

---

## Notes

- Run weekly for all key accounts
- Combine with at-risk-detection for comprehensive monitoring
- Consider automated alerting for CRITICAL_DROP status
- Adjust thresholds based on your product's typical usage patterns
