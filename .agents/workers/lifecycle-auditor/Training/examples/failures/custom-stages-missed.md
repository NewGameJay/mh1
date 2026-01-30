# Failure Analysis: Custom Lifecycle Stages Missed

## Context

**Client**: MedDevCo (B2B Medical Devices, Salesforce CRM)
**Date**: 2024-09-18
**Agent**: lifecycle-auditor v1.0.0
**Severity**: High

## User Request

```
Run a full lifecycle audit for MedDevCo. They use Salesforce and want to see where deals are getting stuck.
```

## What Went Wrong

### Failure Point
Step 1: Data Discovery - Agent queried for standard HubSpot lifecycle stages but client uses Salesforce with a custom lifecycle model including regulatory-specific stages.

### Root Cause
Agent assumed standard lifecycle stages without discovering the client's actual stage definitions. MedDevCo's healthcare sales process includes stages like "Clinical Evaluation" and "Regulatory Review" that don't exist in standard models.

### Impact
- Audit returned "No data found" for most stages
- 45 minutes wasted on investigation
- Client questioned competence of the system
- Required manual intervention to complete audit

## The Interaction

### Agent's Initial Analysis
```
Intent: Full lifecycle audit for Salesforce client
Confidence: 0.85
Selected approach: Standard Funnel Analysis (using standard stages)
```

### What Actually Happened

1. **Step 1: Data Discovery**
   - Expected: Query Salesforce for standard lifecycle stages
   - Actual: Query returned minimal results
   - Issue: Standard stages don't match MedDevCo's custom model

2. **Step 2: Investigation**
   - Expected: Agent should have discovered custom stages
   - Actual: Agent reported "insufficient data" error
   - Issue: No stage discovery step in process

3. **Step 3: User Confusion**
   - Expected: Meaningful audit results
   - Actual: Error message claiming no lifecycle data
   - Issue: Client knows they have 500+ contacts in CRM

### Query Attempted (Incorrect)

```sql
SELECT Id, Email, Lifecycle_Stage__c, CreatedDate
FROM Contact
WHERE Lifecycle_Stage__c IN ('Prospect', 'Lead', 'MQL', 'SQL', 'Opportunity', 'Customer')
```

**Result:** 23 contacts returned (only contacts that happened to match standard names)

### MedDevCo's Actual Stages

| Stage | Description | Standard Equivalent |
|-------|-------------|---------------------|
| Initial Interest | First contact | Subscriber/Lead |
| Discovery Meeting | Qualification call | MQL |
| Clinical Evaluation | Product trial at hospital | (No equivalent) |
| Procurement Review | Purchasing evaluation | SQL |
| Regulatory Review | Compliance check | (No equivalent) |
| Contract Negotiation | Deal in progress | Opportunity |
| Active Customer | Closed-won | Customer |
| Reference Account | Willing to refer | Evangelist |

### User's Response
```
"This can't be right. We have over 500 contacts in Salesforce with lifecycle stages.
Our stages are different from standard ones - we have Clinical Evaluation, Regulatory Review, etc.
Did you check for those?"
```

## Analysis

### Contributing Factors

1. **No stage discovery step**
   - How it contributed: Agent jumped directly to querying with assumed stage values
   - Warning signs missed: Should always discover actual field values first

2. **Platform assumption**
   - How it contributed: Applied HubSpot stage names to Salesforce query
   - Warning signs missed: Salesforce reference doc notes custom stages are common

3. **Insufficient error handling**
   - How it contributed: Low results interpreted as "insufficient data" not "wrong stages"
   - Warning signs missed: Client context indicated established CRM usage

### Detection Opportunities

| Checkpoint | Signal | Why Missed |
|------------|--------|------------|
| Platform detection | Salesforce (not HubSpot) | Noted but didn't trigger stage discovery |
| Data discovery | Only 23 results from 500+ CRM | Interpreted as data quality, not stage mismatch |
| Client context | "Established CRM" in profile | Should have prompted custom stage check |
| Query results | Most stages returned 0 | Should have triggered investigation |

## Correct Approach

### What Should Have Happened

1. **Recognition**: Detect Salesforce CRM and trigger stage discovery:
   ```python
   # ALWAYS discover stages before querying
   if platform == "salesforce":
       stages = discover_lifecycle_stages(client_id)
       if stages != STANDARD_STAGES:
           log.info(f"Custom stages detected: {stages}")
   ```

2. **Clarification**: Before querying, present discovered stages:
   ```
   I've discovered MedDevCo uses custom lifecycle stages in Salesforce:

   1. Initial Interest
   2. Discovery Meeting
   3. Clinical Evaluation
   4. Procurement Review
   5. Regulatory Review
   6. Contract Negotiation
   7. Active Customer
   8. Reference Account

   Shall I proceed with the audit using these stages? I'll map them to standard
   funnel positions for benchmarking where applicable.
   ```

3. **Execution**: Use discovered stages with mapping:
   ```python
   stage_mapping = {
       "Initial Interest": "lead",
       "Discovery Meeting": "mql",
       "Clinical Evaluation": "custom_clinical",  # Flag as industry-specific
       "Procurement Review": "sql",
       "Regulatory Review": "custom_regulatory",  # Flag as industry-specific
       "Contract Negotiation": "opportunity",
       "Active Customer": "customer",
       "Reference Account": "evangelist"
   }
   ```

4. **Validation**: Note custom stages in output:
   ```json
   {
     "platform": "salesforce",
     "custom_stages": true,
     "stage_model": {
       "standard_mappable": 6,
       "industry_specific": 2,
       "notes": "Clinical Evaluation and Regulatory Review are healthcare-specific stages without standard benchmarks"
     }
   }
   ```

### Example Correct Output

```json
{
  "summary": {
    "total_accounts": 523,
    "platform": "salesforce",
    "stage_model": "custom_healthcare",
    "health_score": 0.68
  },
  "by_stage": {
    "initial_interest": 142,
    "discovery_meeting": 98,
    "clinical_evaluation": 87,
    "procurement_review": 64,
    "regulatory_review": 52,
    "contract_negotiation": 38,
    "active_customer": 34,
    "reference_account": 8
  },
  "custom_stage_notes": {
    "clinical_evaluation": {
      "description": "Hospital product evaluation phase",
      "avg_duration_days": 45,
      "benchmark": "No industry benchmark available - tracking internal trend"
    },
    "regulatory_review": {
      "description": "Compliance and approval process",
      "avg_duration_days": 30,
      "benchmark": "Medical device industry avg: 25-40 days"
    }
  },
  "bottlenecks": [
    {
      "from_stage": "clinical_evaluation",
      "to_stage": "procurement_review",
      "rate": 0.74,
      "severity": "medium",
      "note": "26% drop-off during clinical evaluation - investigate trial outcomes"
    }
  ],
  "recommendations": [
    {
      "priority": "high",
      "action": "Review clinical evaluation outcomes for the 22 contacts who dropped off",
      "rationale": "Clinical trial failure is expensive - understanding root causes critical"
    }
  ]
}
```

## Prevention Measures

### Immediate Fixes
- [x] Add mandatory stage discovery step for all Salesforce audits
- [x] Create stage discovery function for all supported CRMs
- [x] Add "stage mismatch" error type distinct from "insufficient data"

### Systemic Improvements
- [x] Update platform reference docs with common custom stages by industry
- [x] Add client industry to context loading (triggers industry-specific checks)
- [ ] Build stage mapping library for common verticals (healthcare, finance, etc.)
- [ ] Implement automatic stage discovery in data validation step

### Added to Training
- [x] Added to decision tree: Platform-specific stage discovery
- [x] Added to anti-patterns: Assuming standard stages
- [x] Updated Salesforce reference doc with custom stage handling
- [x] Created test case: `tests/custom_stage_discovery.py`

## Related Failures

- [Insufficient Data Audit](./insufficient-data-audit.md) - Similar "no data" misdiagnosis
- [Platform Mismatch](./platform-mismatch.md) - Related platform assumption issue

## Follow-up Actions

| Action | Owner | Status |
|--------|-------|--------|
| Add stage discovery to all CRM queries | Engineering | [x] Complete |
| Build healthcare vertical stage template | Industry SME | [x] Complete |
| Client apology and re-run audit | Account team | [x] Complete |
| Update training with industry examples | Training | [x] Complete |
| Add vertical selection to client onboarding | Product | [ ] In Progress |
