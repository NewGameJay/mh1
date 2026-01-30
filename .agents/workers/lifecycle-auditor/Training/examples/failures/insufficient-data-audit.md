# Failure Analysis: Insufficient Data Audit

## Context

**Client**: NovaTech (Early-stage B2B SaaS)
**Date**: 2024-10-22
**Agent**: lifecycle-auditor v1.0.0
**Severity**: Medium

## User Request

```
Run a lifecycle audit for NovaTech. We want to understand our conversion funnel and get recommendations.
```

## What Went Wrong

### Failure Point
Step 3: Funnel Analysis - Generated conversion rates from insufficient sample sizes, leading to misleading conclusions.

### Root Cause
Agent proceeded with analysis despite having only 47 total contacts, with some stages having <5 contacts. Calculated conversion rates were statistically meaningless but presented with false confidence.

### Impact
- Client made process changes based on unreliable data
- Wasted 2 weeks on "fixing" a non-existent MQL-to-SQL bottleneck
- Lost trust required extensive follow-up to repair

## The Interaction

### Agent's Initial Analysis
```
Intent: Lifecycle audit with conversion analysis
Confidence: 0.88
Selected approach: Standard Funnel Analysis
```

### What Actually Happened

1. **Step 1: Data Discovery**
   - Expected: 100+ contacts
   - Actual: 47 contacts retrieved
   - Issue: Should have triggered data quality warning

2. **Step 2: Data Validation**
   - Expected: Warn about small sample size
   - Actual: Passed validation (minimum is 20)
   - Issue: 20 record minimum too low for meaningful conversion analysis

3. **Step 3: Funnel Analysis**
   - Expected: Note statistical limitations
   - Actual: Generated conversion rates without caveats
   - Issue: Calculated rates from stages with <5 contacts

### Output Produced (Problematic)

```json
{
  "summary": {
    "total_accounts": 47,
    "health_score": 0.58
  },
  "by_stage": {
    "subscriber": 12,
    "lead": 18,
    "marketingqualifiedlead": 8,
    "salesqualifiedlead": 3,
    "opportunity": 2,
    "customer": 4
  },
  "conversion_rates": {
    "lead_to_mql": 0.44,
    "mql_to_sql": 0.38,
    "sql_to_opportunity": 0.67,
    "opportunity_to_customer": 2.0
  },
  "bottlenecks": [
    {
      "from_stage": "mql",
      "to_stage": "sql",
      "rate": 0.38,
      "benchmark": 0.25,
      "severity": "low",
      "note": "Above benchmark - performing well"
    }
  ]
}
```

**Problems with this output:**
1. "MQL-to-SQL: 38%" = 3 out of 8. One more SQL would make it 50%. Completely unreliable.
2. "Opportunity-to-Customer: 200%" is mathematically impossible to interpret meaningfully (4 customers from 2 opportunities suggests historical data mix)
3. Health score of 0.58 presented as meaningful when sample is too small

### User's Response
```
"Great, so our MQL-to-SQL is actually good at 38%? We thought that was our problem. Let me redirect the team to focus on subscriber-to-lead instead."
```

**Follow-up (2 weeks later):**
```
"We spent two weeks optimizing subscriber-to-lead and it made no difference. Looking at this again, these numbers don't make sense. How can we have 200% opportunity-to-customer conversion?"
```

## Analysis

### Contributing Factors

1. **Minimum threshold too low**
   - How it contributed: 20 record minimum passed validation but is insufficient for conversion analysis
   - Warning signs missed: Per-stage counts <10 should have triggered escalation

2. **No per-stage minimum**
   - How it contributed: Calculated rates from stages with 2-3 contacts
   - Warning signs missed: Should require minimum 10 per stage for rate calculations

3. **No confidence intervals**
   - How it contributed: Rates presented as precise when margin of error was enormous
   - Warning signs missed: Should flag when variance makes rate unreliable

### Detection Opportunities

When should we have caught this?

| Checkpoint | Signal | Why Missed |
|------------|--------|------------|
| Data validation | 47 total records | Passed 20 minimum but below "recommended 100" |
| Funnel analysis | Stages with <5 | No per-stage minimum enforced |
| Quality gates | 200% conversion | Anomaly not flagged |
| Output review | High variance rates | No confidence bounds included |

## Correct Approach

### What Should Have Happened

1. **Recognition**: After retrieving 47 contacts, agent should have noted:
   ```
   WARNING: Dataset has 47 contacts. This is above the minimum (20) but well below
   the recommended 100 for reliable conversion analysis. Findings should be treated
   as directional only.
   ```

2. **Clarification**: Should have asked:
   ```
   With only 47 contacts across 6 stages, statistical analysis will be limited.
   Options:
   1. Proceed with directional analysis (clearly labeled as preliminary)
   2. Wait until dataset reaches 100+ contacts
   3. Focus on qualitative review of individual accounts instead

   Which would you prefer?
   ```

3. **Execution**: If proceeding, should have used Individual Account Review approach:
   - Review each of the 47 contacts individually
   - Identify patterns qualitatively
   - Note specific accounts stuck at each stage
   - Avoid calculating conversion percentages

4. **Validation**: Output should have included:
   ```json
   {
     "data_quality": {
       "confidence_level": "low",
       "reason": "Sample size (47) insufficient for statistical analysis",
       "recommendation": "Treat findings as preliminary hypotheses to validate"
     }
   }
   ```

### Example Correct Output

```json
{
  "summary": {
    "total_accounts": 47,
    "analysis_type": "qualitative_review",
    "confidence_level": "low"
  },
  "by_stage": {
    "subscriber": 12,
    "lead": 18,
    "marketingqualifiedlead": 8,
    "salesqualifiedlead": 3,
    "opportunity": 2,
    "customer": 4
  },
  "observations": [
    "Funnel is top-heavy with 64% in subscriber/lead stages",
    "MQL stage has 8 contacts - insufficient for conversion rate analysis",
    "4 customers exist but historical context needed to understand journey"
  ],
  "account_level_insights": [
    {
      "segment": "Stuck Leads",
      "count": 8,
      "description": "Leads with no activity in 30+ days - review for qualification issues"
    },
    {
      "segment": "Quick Wins",
      "count": 3,
      "description": "SQLs close to opportunity - prioritize sales outreach"
    }
  ],
  "recommendations": [
    {
      "priority": "high",
      "action": "Focus on progressing 3 SQLs to opportunity before analyzing conversion rates",
      "rationale": "Dataset too small for statistical recommendations"
    },
    {
      "priority": "medium",
      "action": "Re-run audit when dataset reaches 100+ contacts for reliable analysis"
    }
  ],
  "caveats": [
    "Conversion rates NOT calculated due to insufficient sample size",
    "Stage-level counts too small for percentage-based analysis",
    "Findings are observational, not statistically validated"
  ]
}
```

## Prevention Measures

### Immediate Fixes
- [x] Add per-stage minimum (10 contacts) for conversion rate calculations
- [x] Add warning when total records <100 ("directional only")
- [x] Flag anomalies like >100% conversion rates

### Systemic Improvements
- [x] Create "Individual Account Review" approach for <50 contacts
- [x] Add confidence intervals to all rate calculations
- [ ] Implement automatic approach switching based on data size
- [ ] Add explicit "statistical reliability" score to output

### Added to Training
- [x] Added to decision tree: Data size routing
- [x] Added to anti-patterns: Small sample rate calculations
- [x] Created test case: `tests/small_dataset_handling.py`

## Related Failures

- [Missing Stage Data](./missing-stage-data.md) - Similar data quality issue
- [Generic Recommendations](./generic-recommendations.md) - Output quality issue

## Follow-up Actions

| Action | Owner | Status |
|--------|-------|--------|
| Add per-stage minimum to validation | Engineering | [x] Complete |
| Update decision tree for small datasets | Training | [x] Complete |
| Client remediation call | Account team | [x] Complete |
| Create small dataset test suite | QA | [x] Complete |
