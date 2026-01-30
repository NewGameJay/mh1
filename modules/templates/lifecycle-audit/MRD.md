# MRD: {{MODULE_NAME}}

## Metadata
| Field | Value |
|-------|-------|
| Module ID | {{MODULE_ID}} |
| Client | {{CLIENT_ID}} |
| Status | {{STATUS}} |
| Template | lifecycle-audit |
| Priority | P1 |
| Owner | MH1 Engineering |
| Created | {{CREATED_AT}} |
| Updated | {{CREATED_AT}} |

---

## Executive Summary

{{TASK_DESCRIPTION}}

This module will analyze the customer lifecycle for {{CLIENT_ID}} to identify:
- Conversion bottlenecks between lifecycle stages
- Accounts at risk of churning
- Upsell and expansion opportunities
- Actionable recommendations for journey health improvement

---

## Problem Statement

### What Changed?
<!-- Examples:
- Increased churn rate observed in Q4
- New product launch requires customer segmentation
- Board requested customer health metrics
- Sales team needs prioritized lead lists
-->

### Why This Matters
<!-- Examples:
- 10% increase in churn = $X revenue at risk
- Better lifecycle management can improve conversion by 15-25%
- Customer health visibility enables proactive retention
-->

---

## Objectives

### Primary Goal
Deliver a comprehensive lifecycle audit with actionable recommendations to improve customer journey health.

### Success Criteria
1. Complete lifecycle stage distribution analysis with health score
2. Identify top 10 at-risk accounts with specific risk factors
3. Surface upsell opportunities with prioritized recommendations
4. Provide 5+ actionable recommendations with expected impact

---

## Scope

### In Scope
- Lifecycle stage distribution analysis
- Conversion rate calculation between stages
- At-risk account identification
- Upsell candidate scoring
- Recommendation generation
- Cohort retention analysis (if warehouse data available)

### Out of Scope
- Manual data cleanup or transformation
- CRM configuration changes
- Implementation of recommendations
- Real-time monitoring setup

---

## Data Requirements

| Data Type | Source | Required | Notes |
|-----------|--------|----------|-------|
| Contact records | CRM | Yes | Min 20 records |
| Lifecycle stages | CRM | Yes | All contacts must have stage |
| Email addresses | CRM | Yes | For identification |
| Company/Account | CRM | Recommended | For account-level analysis |
| Usage data | Warehouse | Optional | Improves risk scoring |
| Engagement metrics | Warehouse | Optional | Improves recommendations |

---

## Approach & Methodology

### Phase 1: Discovery & Validation
- Connect to CRM via MCP
- Validate data requirements (record count, field coverage)
- Generate data quality report
- **Checkpoint:** Data validated, proceed or request remediation

### Phase 2: Core Analysis
- Calculate lifecycle stage distribution
- Compute conversion rates between stages
- Identify bottlenecks (below-benchmark conversion)
- **Checkpoint:** Stage analysis complete

### Phase 3: Risk & Opportunity Scoring
- Score accounts for churn risk
- Score accounts for upsell potential
- Rank and prioritize findings
- **Checkpoint:** Scoring complete

### Phase 4: Synthesis & Recommendations
- Generate health score (0-1 scale)
- Create prioritized recommendations
- Compile final report
- **Checkpoint:** Draft report ready for review

### Phase 5: Validation & Delivery
- Run quality gates
- Human review (if required)
- Deliver final outputs
- **Checkpoint:** Module complete

---

## Skills to Execute

```yaml
skills:
  - name: lifecycle-audit
    inputs:
      tenant_id: "{{CLIENT_ID}}"
      limit: 1000
      execution_mode: "suggest"
    checkpoint: true
    required: true

  - name: cohort-retention-analysis
    depends_on: lifecycle-audit
    inputs:
      client_id: "{{CLIENT_ID}}"
      lookback_months: 12
    checkpoint: true
    required: false
    condition: "warehouse_available"

  - name: churn-prediction
    depends_on: lifecycle-audit
    inputs:
      client_id: "{{CLIENT_ID}}"
      threshold_days: 30
    checkpoint: true
    required: false
```

---

## Dependencies & Blockers

### Critical Dependencies
- [ ] CRM access configured (HubSpot/Salesforce/etc.)
- [ ] Minimum 20 records with lifecycle stage
- [ ] Budget approved for estimated cost ($5-15)

### Optional Dependencies
- [ ] Data warehouse access for enrichment
- [ ] Historical data for trend analysis

### Known Blockers
- None

---

## Success Metrics

### Quantitative
- Health score calculated (0-1 range)
- At-risk accounts identified with scores
- Conversion rates calculated for all stage transitions
- Upsell candidates scored and ranked

### Qualitative
- Recommendations are actionable and specific
- Report is clear and digestible
- Findings align with business context

---

## Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Insufficient data | High | Medium | Check data requirements early, adjust scope |
| CRM connection issues | High | Low | Use cached data if <24h old |
| Low data quality | Medium | Medium | Include data quality warnings in report |
| Analysis timeout | Medium | Low | Use chunked processing for large datasets |

---

## Timeline & Milestones

| Milestone | Target Date | Status |
|-----------|-------------|--------|
| Module Created | {{CREATED_AT}} | Complete |
| Data Validation | | Pending |
| Analysis Complete | | Pending |
| Review Complete | | Pending |
| Delivery | | Pending |

---

## Stakeholders

| Role | Person | Responsibility |
|------|--------|----------------|
| Engineering Lead | MH1 Team | Implementation |
| Client Contact | TBD | Requirements & Review |
| CS Owner | TBD | Action on recommendations |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {{CREATED_AT}} | MH1 | Initial MRD from lifecycle-audit template |
