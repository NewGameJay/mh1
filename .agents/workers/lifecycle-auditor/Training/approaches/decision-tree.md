# Decision Tree: Lifecycle Audit Approach Selection

Use this decision tree to select the appropriate audit methodology for a given situation.

## Quick Reference

```
START
  |
  +-- Is data quality sufficient? ------------------- No --> Data Quality Assessment
  |   (lifecyclestage 100%, email 80%, 20+ records)         (report gaps, recommend fixes)
  |
  +-- Dataset size?
  |   |
  |   +-- <50 contacts ---------------------------------> Individual Account Review
  |   |
  |   +-- 50-500 contacts ------------------------------> Standard Funnel Analysis
  |   |
  |   +-- 500-2000 contacts ----------------------------> Funnel + Sampling
  |   |
  |   +-- >2000 contacts -------------------------------> Cohort-Based with Chunking
  |
  +-- Time dimension needed? ----------------------- Yes --> Cohort-Based Audit
  |   (trends, improvement tracking, seasonal)
  |
  +-- Specific concern identified? ----------------- Yes --> Targeted Analysis
      (e.g., "MQL-to-SQL is broken")                       (focus on problem area)
```

## Approach Selection Matrix

| Scenario | Best Approach | Why |
|----------|---------------|-----|
| First audit, general health | Funnel Analysis | Establishes baseline |
| Quarterly review | Cohort-Based | Shows trends |
| "Conversion is broken" complaint | Targeted Analysis | Direct to problem |
| New client, small dataset | Individual Review | Need qualitative insights |
| Executive dashboard | Funnel + Trends | Balance depth and clarity |
| Pre-investment due diligence | Comprehensive (all) | Maximum rigor required |

## Data Requirements Decision

```
DATA QUALITY CHECK
  |
  +-- lifecyclestage populated?
  |   |
  |   +-- <100% coverage ------------------------------> ABORT
  |   |   Return error: "Cannot audit without lifecycle stages on all records"
  |   |
  |   +-- 100% coverage --------------------------------> Continue
  |
  +-- email field populated?
  |   |
  |   +-- <80% coverage -------------------------------> WARN
  |   |   "Contact identification limited - some accounts may be duplicated"
  |   |
  |   +-- 80%+ coverage -------------------------------> Continue
  |
  +-- company association?
  |   |
  |   +-- <70% coverage -------------------------------> WARN
  |   |   "Account-level analysis limited - recommend enriching company data"
  |   |
  |   +-- 70%+ coverage -------------------------------> Continue
  |
  +-- record count?
      |
      +-- <20 records ---------------------------------> ABORT
      |   Return error: "Insufficient data for statistical analysis"
      |
      +-- 20-100 records ------------------------------> WARN
      |   "Limited sample size - results should be treated as directional"
      |
      +-- 100+ records --------------------------------> Continue
```

## Platform-Specific Considerations

### HubSpot
```
HUBSPOT AUDIT
  |
  +-- Using default lifecycle stages? ---------------- Yes --> Standard approach
  |                                                    No ---> Discover custom stages first
  |
  +-- Deal pipeline integrated? ---------------------- Yes --> Include revenue metrics
  |                                                    No ---> Contact-only analysis
  |
  +-- Marketing Hub tier?
      |
      +-- Free/Starter --------------------------------> Limited automation data
      |
      +-- Professional/Enterprise ---------------------> Full campaign attribution
```

### Salesforce
```
SALESFORCE AUDIT
  |
  +-- Using Lead or Contact model? ------------------- Lead --> Map Lead Status to stages
  |                                                    Contact --> Use custom lifecycle field
  |
  +-- Opportunity data available? -------------------- Yes --> Include win rate analysis
  |                                                    No ---> Contact journey only
  |
  +-- Multiple record types? ------------------------- Yes --> Segment analysis by type
                                                       No ---> Standard approach
```

## Context Loading Decision

```
CONTEXT REQUIRED
  |
  +-- First audit for this client? ------------------- Yes --> Load full context
  |   (company research, industry benchmarks,                  (~15 min setup)
  |    competitor data)
  |
  +-- Repeat audit? ---------------------------------- Yes --> Load delta context
  |   (previous audit results, recent changes)                 (~5 min setup)
  |
  +-- Specific question? ----------------------------- Yes --> Minimal context
      (e.g., "what's our MQL-to-SQL rate?")                    (~2 min setup)
```

## Confidence Thresholds

| Decision Point | Required Confidence | Action if Below |
|----------------|---------------------|-----------------|
| Approach selection | 0.7 | Present alternatives, ask user |
| Data quality assessment | 0.8 | Request data review before proceeding |
| Bottleneck identification | 0.7 | Flag as "directional" finding |
| Recommendation generation | 0.8 | Include caveats, suggest validation |
| Risk scoring | 0.6 | Do not include in high-priority list |

## Execution Mode Selection

```
EXECUTION MODE
  |
  +-- What should happen with results?
      |
      +-- "Just analyze" -------------------------------> suggest mode
      |   Output: analysis + recommendations only
      |
      +-- "Show me what you'd do" ---------------------> preview mode
      |   Output: analysis + specific actions with dry-run
      |
      +-- "Fix it" ------------------------------------> execute mode
          Output: analysis + actions applied to CRM
          NOTE: Requires approval if >10 changes
```

## Escalation Triggers

Always escalate to human review when:
- Confidence < 0.5 on any major finding
- Data quality score < 0.6
- First audit for a new client (always)
- Findings contradict client's stated understanding
- Execution mode with significant changes (>10 contacts)

## Time and Budget Guidelines

| Approach | Expected Runtime | Estimated Cost |
|----------|------------------|----------------|
| Individual Review (<50) | 15-30s | $0.20-0.40 |
| Funnel Analysis (50-500) | 30-60s | $0.30-0.60 |
| Funnel + Sampling (500-2000) | 60-90s | $0.50-1.00 |
| Cohort-Based (>2000) | 90-120s | $1.00-2.00 |
| Comprehensive (all approaches) | 180-300s | $2.00-4.00 |

Budget limit per run: $2.00 (abort if exceeded)
