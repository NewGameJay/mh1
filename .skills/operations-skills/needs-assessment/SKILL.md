---
name: needs-assessment
description: |
  Analyzes a client's current capabilities vs requirements and identifies what 
  needs to be built, configured, or integrated. Use when asked to 'assess needs',
  'what do we need to support {client}', 'capability gap analysis', or 
  'what's missing for {use case}'.
license: Proprietary
compatibility:
  - skill-builder
  - client-onboarding
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  estimated_runtime: "5-15min"
  max_cost: "$1.00"
  client_facing: true
  requires_human_review: true
  tags:
    - assessment
    - gap-analysis
    - requirements
    - planning
allowed-tools: Read Write Grep Glob WebSearch
---

# Needs Assessment Skill

Analyzes what MH1 can and cannot do for a specific client or use case, and creates an actionable plan to fill gaps.

## When to Use

Use this skill when:
- Evaluating if MH1 can support a potential client
- Scoping work for a new engagement
- Identifying what skills need to be built
- Planning platform integrations
- Auditing current capabilities

---

## Assessment Framework

### Input: Client Requirements

Gather requirements in this format:

```yaml
assessment_request:
  client_name: "{name}"
  
  # What platforms do they use?
  platforms:
    crm: "{crm_name}"
    warehouse: "{warehouse_name}"
    marketing: "{marketing_platform}"
    custom: ["{system_1}", "{system_2}"]
    
  # What do they want to accomplish?
  use_cases:
    - name: "At-risk account detection"
      priority: high
      description: "Identify accounts likely to churn"
      
    - name: "Automated email campaigns"
      priority: medium
      description: "Generate and send personalized emails"
      
    - name: "Sales performance tracking"
      priority: low
      description: "Dashboard of rep performance"
      
  # What data do they have?
  data_available:
    - type: "Customer data"
      location: "{warehouse/crm}"
      fields: ["revenue", "health_score", "activity"]
      
    - type: "Event data"
      location: "{analytics_platform}"
      fields: ["page_views", "clicks", "conversions"]
      
  # Any special requirements?
  constraints:
    - "HIPAA compliance required"
    - "No PII in logs"
    - "EU data residency"
```

---

## Assessment Process

### Step 1: Platform Compatibility Check

```bash
# Check if their platforms are supported
for platform in {crm} {warehouse} {marketing}; do
  grep -r "$platform" skills/*/SKILL.md
done
```

Generate compatibility matrix:

| Platform | Category | Status | Skills | Notes |
|----------|----------|--------|--------|-------|
| {platform} | CRM | ✅ Supported | crm-discovery, pipeline-analysis | Full support |
| {platform} | Warehouse | ⚠️ Partial | data-warehouse-discovery | Missing advanced features |
| {platform} | Marketing | ❌ Not supported | - | Needs skill generation |

### Step 2: Use Case Feasibility

For each use case, check skill availability:

```yaml
use_case_analysis:
  - use_case: "At-risk account detection"
    feasibility: "ready"  # ready, partial, not_possible
    required_skills:
      - name: "at-risk-detection"
        status: "available"
        platform_support: "full"
    required_data:
      - "health_score or activity data"
      - "revenue data"
    gaps: []
    
  - use_case: "Automated email campaigns"
    feasibility: "partial"
    required_skills:
      - name: "email-copy-generator"
        status: "available"
        platform_support: "partial"  # Missing Braze
      - name: "cohort-email-builder"
        status: "available"
    required_data:
      - "contact data"
      - "segmentation criteria"
    gaps:
      - "Braze integration not supported"
      - "Need email template configuration"
```

### Step 3: Data Requirements Check

```yaml
data_assessment:
  required_for_use_cases:
    - field: "health_score"
      required_by: ["at-risk-detection", "churn-prediction"]
      available: true | false
      source: "{warehouse/crm}"
      alternative: "Can calculate from activity signals"
      
    - field: "revenue"
      required_by: ["at-risk-detection", "upsell-candidates"]
      available: true
      source: "{warehouse}"
      format: "monthly recurring (MRR)"
      
    - field: "activity_events"
      required_by: ["engagement-velocity", "dormant-detection"]
      available: true
      source: "{analytics_platform}"
      join_key: "user_id → account_id"
```

---

## Output: Needs Assessment Report

```markdown
# Needs Assessment Report
## Client: {client_name}
## Date: {date}

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Use Cases Requested | {count} |
| Immediately Feasible | {count} ({%}) |
| Require Configuration | {count} ({%}) |
| Require New Skills | {count} ({%}) |
| Not Feasible | {count} ({%}) |

**Recommendation**: {proceed / proceed_with_caveats / not_recommended}

---

## Platform Compatibility

### Fully Supported ✅
{List platforms with full skill support}

### Requires Configuration ⚙️
{Platforms supported but need setup}

### Requires New Skills 🔧
{Platforms needing skill generation}

### Not Supported ❌
{Platforms with no path to support}

---

## Use Case Breakdown

### Ready to Deploy ✅

| Use Case | Skills Needed | Est. Setup Time |
|----------|---------------|-----------------|
| {use_case} | {skills} | {time} |

### Requires Work ⚠️

| Use Case | Missing | Effort | Recommendation |
|----------|---------|--------|----------------|
| {use_case} | {gaps} | {effort} | {recommendation} |

### Not Feasible ❌

| Use Case | Blocker | Alternative |
|----------|---------|-------------|
| {use_case} | {blocker} | {alternative} |

---

## Implementation Plan

### Phase 1: Quick Wins (Week 1)
{Use cases that can be deployed immediately}

### Phase 2: Configuration (Week 2)
{Use cases needing setup but no new code}

### Phase 3: Development (Weeks 3-4)
{Use cases requiring new skills}

### Phase 4: Custom (If needed)
{Use cases requiring significant custom work}

---

## Resource Requirements

### Skills to Generate
| Skill | Platform | Complexity | Est. Time |
|-------|----------|------------|-----------|
| {skill} | {platform} | Medium | 4 hours |

### Configuration Needed
| Config | Type | Effort |
|--------|------|--------|
| {config} | {type} | {effort} |

### Data Preparation
| Task | Owner | Dependency |
|------|-------|------------|
| {task} | {client/mh1} | {dependency} |

---

## Cost Estimate

| Item | Hours | Rate | Total |
|------|-------|------|-------|
| Setup & Configuration | {hours} | ${rate} | ${total} |
| Skill Generation | {hours} | ${rate} | ${total} |
| Testing & Validation | {hours} | ${rate} | ${total} |
| **Total** | {hours} | - | **${total}** |

---

## Next Steps

1. [ ] Client approves assessment
2. [ ] Gather API credentials
3. [ ] Begin Phase 1 deployment
4. [ ] Schedule skill generation sprints
```

---

## Quick Assessment Queries

### Check Platform Support

```bash
# Is {platform} supported?
grep -l "{platform}" skills/*/SKILL.md | head -5

# What skills mention {platform}?
grep -r "compatibility:" skills/*/SKILL.md | grep -i "{platform}"
```

### Check Use Case Coverage

```bash
# Skills for churn/retention
grep -l "churn\|retention\|at-risk" skills/*/SKILL.md

# Skills for email/content
grep -l "email\|content\|copy" skills/*/SKILL.md

# Skills for sales
grep -l "pipeline\|deal\|sales" skills/*/SKILL.md
```

### Check Data Requirements

```bash
# What data does {skill} need?
grep -A 20 "required_data:" skills/{skill}/SKILL.md

# What fields are used?
grep -E "field_mapping|revenue|health_score|account" skills/{skill}/SKILL.md
```

---

## Platform Priority Matrix

When deciding whether to support a new platform:

| Factor | Weight | Score 1-5 | Notes |
|--------|--------|-----------|-------|
| Market share | 25% | | How common is this platform? |
| API quality | 20% | | How good are the docs/API? |
| Client demand | 25% | | How many clients need it? |
| Strategic value | 15% | | Does it open new markets? |
| Complexity | 15% | | How hard to integrate? |

**Score Thresholds**:
- 4.0+: High priority, build immediately
- 3.0-3.9: Medium priority, build when requested
- 2.0-2.9: Low priority, build only if paid
- <2.0: Don't build, suggest alternatives

---

## Output Format

```json
{
  "assessment_complete": true,
  "client": "{client_name}",
  "recommendation": "proceed" | "proceed_with_caveats" | "not_recommended",
  "summary": {
    "total_use_cases": 5,
    "ready": 2,
    "needs_config": 2,
    "needs_development": 1,
    "not_feasible": 0
  },
  "platforms": {
    "supported": ["HubSpot", "Snowflake"],
    "needs_skill": ["Braze"],
    "not_supported": []
  },
  "estimated_effort": {
    "setup_hours": 8,
    "development_hours": 16,
    "total_cost": 2400
  },
  "report_path": "assessments/{client_id}/needs-assessment.md"
}
```
