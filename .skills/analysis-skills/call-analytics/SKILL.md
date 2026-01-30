---
name: call-analytics
description: |
  Track call volume, duration, outcomes by sales rep using CRM call data.
  Use when asked to 'analyze calls', 'call metrics', 'rep call activity',
  'call duration', 'call outcomes', or 'call performance'.
license: Proprietary
compatibility:
  - HubSpot MCP (user-hubspot)
  - Salesforce API
  - Pipedrive API
  - Zoho CRM API
  - Microsoft Dynamics API
metadata:
  author: mh1-engineering
  version: "2.0.0"
  status: active
  created: "2026-01-28"
  updated: "2026-01-28"
  estimated_runtime: "1-3min"
  max_runtime: "10min"
  estimated_cost: "$0.25"
  max_cost: "$1.00"
  client_facing: true
  requires_human_review: false
  tags:
    - sales-intelligence
    - calls
    - rep-performance
    - multi-crm
allowed-tools: Read Write CallMcpTool
---

# Call Analytics Skill

Analyze sales call data to track volume, duration, outcomes, and rep performance patterns across multiple CRM platforms.

## When to Use

Use this skill when you need to:
- Track total call volume over time
- Analyze call activity by sales rep
- Understand average call duration
- Identify best times to make calls
- Measure call outcome rates (connected vs voicemail)
- Correlate call activity with close rates

Do NOT use when:
- You need email metrics (use email analysis skills)
- You need meeting data (use account-360 or meeting analysis)
- You need pipeline-level analysis (use pipeline-analysis skill)

---

## Configuration

```yaml
configuration:
  crm_platform: hubspot | salesforce | pipedrive | zoho | dynamics
  
  field_mapping:
    call_id: "hs_object_id" | "Id" | "id"
    call_title: "hs_call_title" | "Subject" | "subject"
    call_duration: "hs_call_duration" | "CallDurationInSeconds" | "duration"
    call_status: "hs_call_status" | "Status" | "outcome"
    call_date: "hs_createdate" | "CreatedDate" | "add_time"
    owner_field: "hubspot_owner_id" | "OwnerId" | "user_id"
  
  # Status mapping for outcome analysis
  status_mapping:
    connected: ["COMPLETED", "Connected", "connected", "answered"]
    voicemail: ["VOICEMAIL", "Left Voicemail", "voicemail", "left_message"]
    no_answer: ["NO_ANSWER", "No Answer", "no_answer", "missed"]
    busy: ["BUSY", "Busy", "busy"]
  
  # Duration unit (for normalization)
  duration_unit: seconds | milliseconds | minutes
```

---

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `days` | number | no | 30 | Lookback period in days |
| `rep_id` | string | no | null | Owner ID to filter by specific rep |
| `include_outcomes` | boolean | no | true | Include outcome breakdown |
| `include_timing` | boolean | no | false | Include time-of-day analysis |

---

## Platform-Specific Query Patterns

### HubSpot

**Total Call Volume:**
```json
{
  "filterGroups": [{
    "filters": [
      { "propertyName": "hs_createdate", "operator": "GTE", "value": "{start_timestamp}" }
    ]
  }],
  "properties": ["hs_call_title", "hs_createdate", "hs_call_duration", "hs_call_status", "hubspot_owner_id"],
  "sorts": [{ "propertyName": "hs_createdate", "direction": "DESCENDING" }],
  "limit": 100
}
```

**MCP Tool:** `user-hubspot` → `hubspot_search` (object: calls)

### Salesforce

**Total Call Volume:**
```sql
SELECT Id, Subject, CallDurationInSeconds, Status, CreatedDate, OwnerId, Owner.Name
FROM Task
WHERE TaskSubtype = 'Call'
  AND CreatedDate >= LAST_N_DAYS:{days}
ORDER BY CreatedDate DESC
LIMIT 500
```

**Calls by Owner:**
```sql
SELECT OwnerId, Owner.Name,
       COUNT(Id) as TotalCalls,
       SUM(CallDurationInSeconds) as TotalDuration,
       AVG(CallDurationInSeconds) as AvgDuration
FROM Task
WHERE TaskSubtype = 'Call'
  AND CreatedDate >= LAST_N_DAYS:{days}
GROUP BY OwnerId, Owner.Name
ORDER BY TotalCalls DESC
```

**API Endpoint:** `/services/data/v58.0/query?q={SOQL}`

### Pipedrive

**Get Activities (Calls):**
```
GET /activities
Parameters:
  type: call
  start_date: {start_date}
  end_date: {end_date}
  done: 1
```

**Get Activities by User:**
```
GET /activities
Parameters:
  type: call
  user_id: {user_id}
  start_date: {start_date}
```

### Zoho CRM

```json
{
  "module": "Calls",
  "criteria": "(Call_Start_Time:greater_equal:{start_date})",
  "fields": ["Subject", "Call_Duration", "Call_Status", "Call_Start_Time", "Owner"],
  "sort_by": "Call_Start_Time",
  "sort_order": "desc",
  "per_page": 200
}
```

### Microsoft Dynamics

```
GET /phonecalls
$filter: createdon ge {start_date}
$select: subject,actualdurationminutes,statecode,statuscode,createdon,_ownerid_value
$orderby: createdon desc
$top: 500
```

---

## Process

### Step 1: Load Configuration

```python
config = load_client_config(client_id)
crm = config["crm_platform"]
field_map = config["field_mapping"]
status_map = config["status_mapping"]
```

### Step 2: Query Call Data

Execute platform-specific queries.

### Step 3: Normalize Call Data

```python
def normalize_call(call, field_map, config):
    duration_raw = call.get(field_map["call_duration"], 0)
    
    # Normalize to minutes
    if config["duration_unit"] == "seconds":
        duration_min = duration_raw / 60
    elif config["duration_unit"] == "milliseconds":
        duration_min = duration_raw / 60000
    else:
        duration_min = duration_raw
    
    return {
        "call_id": call.get(field_map["call_id"]),
        "title": call.get(field_map["call_title"]),
        "duration_minutes": round(duration_min, 1),
        "status": call.get(field_map["call_status"]),
        "date": call.get(field_map["call_date"]),
        "owner_id": call.get(field_map["owner_field"])
    }
```

### Step 4: Calculate Metrics by Rep

```python
by_rep = {}
for call in calls:
    owner = call["owner_id"]
    by_rep.setdefault(owner, {
        "total_calls": 0,
        "total_duration": 0,
        "calls_by_day": {}
    })
    by_rep[owner]["total_calls"] += 1
    by_rep[owner]["total_duration"] += call["duration_minutes"]

for owner, data in by_rep.items():
    data["avg_duration_min"] = data["total_duration"] / data["total_calls"]
    data["calls_per_day"] = data["total_calls"] / days
```

### Step 5: Calculate Duration Distribution

```python
duration_buckets = {
    "quick_under_5min": 0,
    "standard_5_15min": 0,
    "extended_15_30min": 0,
    "long_over_30min": 0
}

for call in calls:
    dur = call["duration_minutes"]
    if dur < 5:
        duration_buckets["quick_under_5min"] += 1
    elif dur < 15:
        duration_buckets["standard_5_15min"] += 1
    elif dur < 30:
        duration_buckets["extended_15_30min"] += 1
    else:
        duration_buckets["long_over_30min"] += 1
```

### Step 6: Calculate Outcomes (if include_outcomes=true)

```python
def categorize_status(status, status_map):
    for category, values in status_map.items():
        if status in values:
            return category
    return "other"

outcomes = {"connected": 0, "voicemail": 0, "no_answer": 0, "busy": 0, "other": 0}
for call in calls:
    category = categorize_status(call["status"], status_map)
    outcomes[category] += 1

total = sum(outcomes.values())
outcome_pcts = {k: round(v / total * 100, 1) for k, v in outcomes.items()}
```

### Step 7: Calculate Timing Patterns (if include_timing=true)

```python
from collections import defaultdict

hourly = defaultdict(lambda: {"total": 0, "connected": 0})
for call in calls:
    hour = parse_hour(call["date"])
    hourly[hour]["total"] += 1
    if categorize_status(call["status"], status_map) == "connected":
        hourly[hour]["connected"] += 1

# Find best hours (highest connection rate with min volume)
best_hours = sorted(
    [(h, d["connected"]/d["total"]) for h, d in hourly.items() if d["total"] >= 10],
    key=lambda x: x[1],
    reverse=True
)[:3]
```

---

## Output Schema

```json
{
  "config": {
    "crm_platform": "string",
    "days_analyzed": "number"
  },
  "summary": {
    "total_calls": "number",
    "total_duration_minutes": "number",
    "avg_duration_minutes": "number",
    "calls_per_day": "number",
    "unique_reps": "number",
    "date_range": {
      "start": "date",
      "end": "date"
    }
  },
  "by_rep": [
    {
      "owner_id": "string",
      "owner_name": "string",
      "total_calls": "number",
      "total_duration_min": "number",
      "avg_duration_min": "number",
      "calls_per_day": "number",
      "rank": "number"
    }
  ],
  "duration_distribution": {
    "quick_under_5min": "number",
    "standard_5_15min": "number",
    "extended_15_30min": "number",
    "long_over_30min": "number"
  },
  "outcomes": {
    "connected": { "count": "number", "pct": "number" },
    "voicemail": { "count": "number", "pct": "number" },
    "no_answer": { "count": "number", "pct": "number" },
    "busy": { "count": "number", "pct": "number" }
  },
  "timing": {
    "best_hours": ["number"],
    "best_days": ["string"],
    "hourly_distribution": {}
  },
  "correlations": {
    "avg_calls_per_closed_deal": "number",
    "optimal_call_count": "string"
  },
  "recommendations": ["string"]
}
```

---

## Quality Criteria

- [ ] Query executes without error
- [ ] All reps with calls included in by_rep list
- [ ] Duration calculations in correct units (minutes)
- [ ] Percentages sum to ~100% for outcomes
- [ ] Recommendations relevant to patterns observed
- [ ] Date range correctly applied

---

## Example Usage

**Get call metrics for last 30 days:**
```
Use call-analytics skill with default settings
```

**Get call metrics for specific rep:**
```
Analyze calls for rep_id=12345 over last 60 days
```

**Full call analysis with timing:**
```
Run call-analytics with include_timing=true for last 90 days
```

---

## Sample Output

```json
{
  "config": {
    "crm_platform": "hubspot",
    "days_analyzed": 30
  },
  "summary": {
    "total_calls": 2847,
    "total_duration_minutes": 14235,
    "avg_duration_minutes": 5.0,
    "calls_per_day": 94.9,
    "unique_reps": 12,
    "date_range": {
      "start": "2025-12-28",
      "end": "2026-01-27"
    }
  },
  "by_rep": [
    {
      "owner_id": "234567",
      "owner_name": "Sarah Johnson",
      "total_calls": 412,
      "total_duration_min": 2060,
      "avg_duration_min": 5.0,
      "calls_per_day": 13.7,
      "rank": 1
    },
    {
      "owner_id": "345678",
      "owner_name": "Mike Chen",
      "total_calls": 385,
      "total_duration_min": 1925,
      "avg_duration_min": 5.0,
      "calls_per_day": 12.8,
      "rank": 2
    }
  ],
  "duration_distribution": {
    "quick_under_5min": 1423,
    "standard_5_15min": 997,
    "extended_15_30min": 341,
    "long_over_30min": 86
  },
  "outcomes": {
    "connected": { "count": 1708, "pct": 60.0 },
    "voicemail": { "count": 712, "pct": 25.0 },
    "no_answer": { "count": 342, "pct": 12.0 },
    "busy": { "count": 85, "pct": 3.0 }
  },
  "correlations": {
    "avg_calls_per_closed_deal": 8.5,
    "optimal_call_count": "6-10"
  },
  "recommendations": [
    "Sarah Johnson leads in call volume - consider documenting her call scripts for team training",
    "60% connected rate is strong - focus on converting voicemails to callbacks",
    "Best call times: Tuesday-Thursday, 10am-12pm and 2pm-4pm"
  ]
}
```

---

## Client Setup Required

```yaml
# clients/{client_id}/config.yaml
call_analytics:
  crm_platform: hubspot
  
  field_mapping:
    call_id: hs_object_id
    call_title: hs_call_title
    call_duration: hs_call_duration
    call_status: hs_call_status
    call_date: hs_createdate
    owner_field: hubspot_owner_id
    
  status_mapping:
    connected: ["COMPLETED", "Connected"]
    voicemail: ["VOICEMAIL", "Left Voicemail"]
    no_answer: ["NO_ANSWER", "No Answer"]
    busy: ["BUSY", "Busy"]
    
  duration_unit: milliseconds  # HubSpot uses milliseconds
```

---

## Known Limitations

1. **CRM data only** - does not include calls logged outside CRM
2. **Call status mapping** - depends on correct status values in CRM
3. **Owner name resolution** - requires owner lookup API call
4. **Duration accuracy** - relies on call logging completeness

---

## Notes

- Run weekly for sales team reviews
- Combine with email-analysis for full activity picture
- Export to Google Sheets for management dashboards
- Set alerts for reps below activity thresholds
