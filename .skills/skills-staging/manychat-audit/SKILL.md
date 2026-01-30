---
name: manychat-audit
description: |
  Audit ManyChat flows for optimization opportunities, engagement metrics, and automation health.
  Use when asked to 'audit ManyChat', 'review chat flows', 'analyze ManyChat performance',
  'optimize chatbot flows', or 'check ManyChat automation'.
license: Proprietary
compatibility:
  - ManyChat API
  - Browser Automation (fallback)
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: experimental
  created: "2026-01-28"
  estimated_runtime: "5-15min"
  max_cost: "$0.50"
  client_facing: true
  requires_human_review: true
  tags:
    - manychat
    - chatbot
    - automation
    - audit
    - messaging
allowed-tools: Read Write Shell WebFetch
---

# ManyChat Audit Skill

Audit ManyChat flows to identify optimization opportunities, measure engagement metrics, and assess automation health.

## When to Use

Use this skill when you need to:
- Audit existing ManyChat flows for performance
- Identify underperforming or abandoned flows
- Analyze subscriber engagement patterns
- Find optimization opportunities
- Benchmark flow performance
- Prepare recommendations for flow improvements

Do NOT use when:
- You need to create new flows (use ManyChat UI)
- You need real-time messaging (use ManyChat directly)
- ManyChat access is not configured

---

## Platform Access

### Option 1: ManyChat API (Preferred)

ManyChat provides a REST API for flow and subscriber data:

```yaml
manychat_api:
  base_url: "https://api.manychat.com"
  auth_type: "bearer"
  token_env: "MANYCHAT_API_TOKEN"

  endpoints:
    flows: "/fb/page/getFlows"
    flow_stats: "/fb/page/getFlowStats"
    subscribers: "/fb/subscriber/getInfo"
    tags: "/fb/page/getTags"
    custom_fields: "/fb/page/getCustomFields"
```

### Option 2: Browser Automation (Fallback)

If API access is unavailable, use browser automation:

```python
from lib.browser_automation import MH1BrowserClient

with MH1BrowserClient(session="manychat-audit") as browser:
    browser.open("https://manychat.com/login")
    # Navigate to flows page and extract data
    snapshot = browser.snapshot()
```

---

## Configuration

Configure ManyChat access in `clients/{clientId}/config/integrations.yaml`:

```yaml
manychat:
  # API Configuration
  api_token: "${MANYCHAT_API_TOKEN}"
  page_id: "{facebook_page_id}"

  # Or Browser Automation (fallback)
  browser_auth:
    email: "${MANYCHAT_EMAIL}"
    password: "${MANYCHAT_PASSWORD}"

  # Audit thresholds
  thresholds:
    low_engagement_rate: 0.20      # Below 20% = low engagement
    high_bounce_rate: 0.50         # Above 50% = high bounce
    inactive_flow_days: 30         # Unused for 30+ days = inactive
    low_completion_rate: 0.30      # Below 30% = low completion
```

---

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `client_id` | string | yes | - | Client identifier |
| `audit_scope` | string | no | "all" | "all", "active_only", "inactive_only" |
| `lookback_days` | number | no | 30 | Days of data to analyze |
| `include_recommendations` | boolean | no | true | Generate optimization recommendations |
| `compare_to_benchmarks` | boolean | no | true | Compare against industry benchmarks |

---

## ManyChat Data Model

### Key Entities

| Entity | Description | Key Metrics |
|--------|-------------|-------------|
| **Flows** | Automation sequences | triggers, steps, completion rate |
| **Subscribers** | Users in the system | total, active, engaged |
| **Tags** | Subscriber classifications | usage, distribution |
| **Custom Fields** | Subscriber attributes | coverage, usage |
| **Broadcasts** | One-time messages | sent, opened, clicked |
| **Growth Tools** | Acquisition widgets | impressions, conversions |

### Flow Types

| Type | Description | Typical Use Case |
|------|-------------|------------------|
| `default_reply` | Auto-reply to unmatched messages | Fallback handling |
| `keyword` | Triggered by specific keywords | FAQ, support |
| `sequence` | Multi-step drip campaigns | Onboarding, nurture |
| `broadcast` | One-time bulk messages | Announcements |
| `growth_tool` | Widget-triggered flows | Acquisition |
| `api` | Externally triggered | Integrations |

---

## Process

### Step 1: Connect and Authenticate

**Via API:**
```python
import requests

def connect_manychat(api_token):
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    # Test connection
    response = requests.get(
        "https://api.manychat.com/fb/page/getInfo",
        headers=headers
    )

    if response.status_code == 200:
        return {"status": "connected", "page_info": response.json()}
    else:
        return {"status": "error", "message": response.text}
```

**Via Browser (fallback):**
```python
from lib.browser_automation import MH1BrowserClient

def connect_manychat_browser(email, password):
    with MH1BrowserClient(session="manychat") as browser:
        browser.open("https://manychat.com/login")
        browser.fill("input[name='email']", email)
        browser.fill("input[name='password']", password)
        browser.click("button[type='submit']")

        # Wait for dashboard
        browser.wait_for_selector(".dashboard")

        return {"status": "connected"}
```

### Step 2: Retrieve Flow Data

**API Method:**
```python
def get_flows(api_token):
    response = requests.get(
        "https://api.manychat.com/fb/page/getFlows",
        headers={"Authorization": f"Bearer {api_token}"}
    )

    flows = response.json().get("data", [])

    return [
        {
            "flow_id": f["id"],
            "name": f["name"],
            "type": f["type"],
            "status": f["status"],  # active, draft, archived
            "created_at": f["created_at"],
            "updated_at": f["updated_at"],
            "trigger_count": f.get("trigger_count", 0)
        }
        for f in flows
    ]
```

### Step 3: Get Flow Statistics

```python
def get_flow_stats(api_token, flow_id, lookback_days):
    response = requests.get(
        f"https://api.manychat.com/fb/page/getFlowStats",
        headers={"Authorization": f"Bearer {api_token}"},
        params={
            "flow_id": flow_id,
            "date_from": (datetime.now() - timedelta(days=lookback_days)).isoformat(),
            "date_to": datetime.now().isoformat()
        }
    )

    stats = response.json().get("data", {})

    return {
        "flow_id": flow_id,
        "triggered": stats.get("triggered", 0),
        "completed": stats.get("completed", 0),
        "completion_rate": safe_divide(stats.get("completed", 0), stats.get("triggered", 0)),
        "unique_users": stats.get("unique_users", 0),
        "messages_sent": stats.get("messages_sent", 0),
        "clicks": stats.get("clicks", 0),
        "click_rate": safe_divide(stats.get("clicks", 0), stats.get("messages_sent", 0))
    }
```

### Step 4: Analyze Subscriber Data

```python
def analyze_subscribers(api_token):
    response = requests.get(
        "https://api.manychat.com/fb/page/getSubscribers",
        headers={"Authorization": f"Bearer {api_token}"},
        params={"limit": 1000}  # Paginate for full list
    )

    subscribers = response.json().get("data", [])

    total = len(subscribers)
    active_30d = sum(1 for s in subscribers if is_active_recent(s, 30))
    engaged = sum(1 for s in subscribers if s.get("messages_count", 0) > 5)

    return {
        "total_subscribers": total,
        "active_last_30d": active_30d,
        "active_rate": safe_divide(active_30d, total),
        "engaged_subscribers": engaged,
        "engagement_rate": safe_divide(engaged, total),
        "by_acquisition_source": group_by_source(subscribers),
        "by_tag": group_by_tag(subscribers)
    }
```

### Step 5: Identify Issues and Opportunities

```python
def identify_issues(flows_with_stats, thresholds):
    issues = []

    for flow in flows_with_stats:
        # Low completion rate
        if flow["completion_rate"] < thresholds["low_completion_rate"]:
            issues.append({
                "flow_id": flow["flow_id"],
                "flow_name": flow["name"],
                "issue_type": "LOW_COMPLETION",
                "severity": "high" if flow["completion_rate"] < 0.15 else "medium",
                "current_value": flow["completion_rate"],
                "threshold": thresholds["low_completion_rate"],
                "recommendation": "Review flow steps for friction points. Consider shortening or simplifying."
            })

        # Low click rate
        if flow["click_rate"] < thresholds["low_engagement_rate"]:
            issues.append({
                "flow_id": flow["flow_id"],
                "flow_name": flow["name"],
                "issue_type": "LOW_ENGAGEMENT",
                "severity": "medium",
                "current_value": flow["click_rate"],
                "threshold": thresholds["low_engagement_rate"],
                "recommendation": "Improve CTA copy and button placement. Test different message formats."
            })

        # Inactive flow
        days_since_trigger = days_since(flow.get("last_triggered"))
        if days_since_trigger > thresholds["inactive_flow_days"]:
            issues.append({
                "flow_id": flow["flow_id"],
                "flow_name": flow["name"],
                "issue_type": "INACTIVE",
                "severity": "low",
                "current_value": f"{days_since_trigger} days",
                "threshold": f"{thresholds['inactive_flow_days']} days",
                "recommendation": "Consider archiving or promoting this flow if still relevant."
            })

    return sorted(issues, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["severity"]])
```

### Step 6: Generate Recommendations

```python
def generate_recommendations(issues, subscriber_analysis, flow_stats):
    recommendations = []

    # Priority 1: High-severity issues
    high_severity = [i for i in issues if i["severity"] == "high"]
    if high_severity:
        recommendations.append({
            "priority": "P0",
            "category": "Critical Issues",
            "action": f"Address {len(high_severity)} flows with critical performance issues",
            "flows": [i["flow_name"] for i in high_severity[:5]],
            "expected_impact": "Significant improvement in conversion rates"
        })

    # Priority 2: Engagement opportunities
    if subscriber_analysis["engagement_rate"] < 0.30:
        recommendations.append({
            "priority": "P1",
            "category": "Engagement",
            "action": "Launch re-engagement campaign for dormant subscribers",
            "target_audience": f"{subscriber_analysis['total_subscribers'] - subscriber_analysis['engaged_subscribers']} disengaged subscribers",
            "expected_impact": "Reactivate 10-20% of dormant audience"
        })

    # Priority 3: Inactive flow cleanup
    inactive = [i for i in issues if i["issue_type"] == "INACTIVE"]
    if len(inactive) > 5:
        recommendations.append({
            "priority": "P2",
            "category": "Maintenance",
            "action": f"Archive or reactivate {len(inactive)} inactive flows",
            "flows": [i["flow_name"] for i in inactive[:10]],
            "expected_impact": "Cleaner automation environment, easier management"
        })

    return recommendations
```

---

## Output Schema

```json
{
  "audit_summary": {
    "total_flows": "number",
    "active_flows": "number",
    "inactive_flows": "number",
    "total_subscribers": "number",
    "engagement_rate": "number",
    "overall_health_score": "number (0-100)"
  },
  "flow_analysis": [
    {
      "flow_id": "string",
      "name": "string",
      "type": "string",
      "status": "active | draft | archived",
      "metrics": {
        "triggered": "number",
        "completed": "number",
        "completion_rate": "number",
        "click_rate": "number"
      },
      "health": "healthy | warning | critical",
      "issues": ["string"]
    }
  ],
  "subscriber_analysis": {
    "total": "number",
    "active_30d": "number",
    "active_rate": "number",
    "engaged": "number",
    "engagement_rate": "number",
    "by_source": {},
    "by_tag": {}
  },
  "issues": [
    {
      "flow_id": "string",
      "flow_name": "string",
      "issue_type": "LOW_COMPLETION | LOW_ENGAGEMENT | INACTIVE | HIGH_BOUNCE",
      "severity": "high | medium | low",
      "current_value": "string",
      "threshold": "string",
      "recommendation": "string"
    }
  ],
  "recommendations": [
    {
      "priority": "P0 | P1 | P2 | P3",
      "category": "string",
      "action": "string",
      "expected_impact": "string"
    }
  ],
  "_meta": {
    "client_id": "string",
    "audit_date": "ISO timestamp",
    "lookback_days": "number",
    "access_method": "api | browser"
  }
}
```

---

## Industry Benchmarks

| Metric | Poor | Average | Good | Excellent |
|--------|------|---------|------|-----------|
| Completion Rate | <20% | 20-40% | 40-60% | >60% |
| Click Rate | <10% | 10-25% | 25-40% | >40% |
| Subscriber Active Rate | <15% | 15-30% | 30-50% | >50% |
| Engagement Rate | <10% | 10-25% | 25-40% | >40% |

---

## Quality Criteria

- [ ] All active flows are analyzed
- [ ] Metrics are calculated correctly
- [ ] Issues are prioritized by severity
- [ ] Recommendations are actionable
- [ ] No sensitive subscriber data exposed (use aggregates)

---

## Example Usage

**Full ManyChat audit:**
```
Audit ManyChat flows for client_id=ffc
```

**Audit with specific focus:**
```
Audit ManyChat for ffc, focus on inactive_only flows
```

**Audit with custom thresholds:**
```
ManyChat audit for ffc with low_engagement_rate=0.15
```

---

## Sample Output

```json
{
  "audit_summary": {
    "total_flows": 24,
    "active_flows": 18,
    "inactive_flows": 6,
    "total_subscribers": 8450,
    "engagement_rate": 0.28,
    "overall_health_score": 62
  },
  "flow_analysis": [
    {
      "flow_id": "flow_12345",
      "name": "Welcome Sequence",
      "type": "sequence",
      "status": "active",
      "metrics": {
        "triggered": 1250,
        "completed": 750,
        "completion_rate": 0.60,
        "click_rate": 0.35
      },
      "health": "healthy",
      "issues": []
    },
    {
      "flow_id": "flow_67890",
      "name": "Event Registration",
      "type": "keyword",
      "status": "active",
      "metrics": {
        "triggered": 320,
        "completed": 45,
        "completion_rate": 0.14,
        "click_rate": 0.08
      },
      "health": "critical",
      "issues": ["LOW_COMPLETION", "LOW_ENGAGEMENT"]
    }
  ],
  "issues": [
    {
      "flow_id": "flow_67890",
      "flow_name": "Event Registration",
      "issue_type": "LOW_COMPLETION",
      "severity": "high",
      "current_value": "14%",
      "threshold": "30%",
      "recommendation": "Review flow steps for friction points. The registration form may be too long or confusing."
    }
  ],
  "recommendations": [
    {
      "priority": "P0",
      "category": "Critical Issues",
      "action": "Fix Event Registration flow - only 14% completion rate",
      "expected_impact": "Could recover 100+ registrations per month"
    },
    {
      "priority": "P1",
      "category": "Engagement",
      "action": "Launch re-engagement campaign for 6,084 dormant subscribers",
      "expected_impact": "Reactivate 10-20% of dormant audience"
    },
    {
      "priority": "P2",
      "category": "Maintenance",
      "action": "Archive 6 unused flows to simplify management",
      "expected_impact": "Cleaner automation environment"
    }
  ],
  "_meta": {
    "client_id": "ffc",
    "audit_date": "2026-01-28T10:00:00Z",
    "lookback_days": 30,
    "access_method": "api"
  }
}
```

---

## Known Limitations

1. **API Rate Limits**: ManyChat API has rate limits; large accounts may require pagination
2. **Browser Auth**: Browser automation requires stored credentials (security consideration)
3. **Historical Data**: ManyChat retains limited historical data; deep analysis may be restricted
4. **Real-time Data**: Some metrics may have 24-48 hour delay

---

## Human Review Required

This skill requires human review for:
- [ ] Flow optimization recommendations
- [ ] Subscriber segmentation strategy
- [ ] Re-engagement campaign approval
- [ ] Archive/delete decisions

---

## Notes

- **API Token**: Get from ManyChat Settings > API > Create Token
- **Permissions**: Token needs read access to Flows, Subscribers, Tags
- **Output location**: `clients/{client_id}/audits/manychat-audit.md`
- **Frequency**: Run monthly for ongoing optimization

---

## Changelog

### v1.0.0 (2026-01-28)
- Initial release
- Flow performance analysis
- Subscriber engagement metrics
- Issue identification with severity
- Recommendation engine
- Browser automation fallback
