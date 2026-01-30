---
name: cohort-retention-analysis
description: |
  Build retention curves and compare cohorts statistically for ICP research.
  Use when asked to 'analyze retention', 'compare cohorts', 'build retention curves',
  'measure churn by cohort', or 'identify retention drivers'.
license: Proprietary
compatibility:
  - Snowflake MCP
  - BigQuery
  - Redshift
  - Databricks
  - PostgreSQL
  - HubSpot MCP
  - Salesforce
  - Pipedrive
  - Zoho
  - Dynamics
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  created: "2026-01-29"
  updated: "2026-01-29"
  estimated_runtime: "30s-120s"
  max_runtime: "5min"
  estimated_cost: "$0.75"
  max_cost: "$2.50"
  client_facing: true
  requires_human_review: true
  tags:
    - retention
    - cohort-analysis
    - icp-research
    - lifecycle
    - analytics
    - platform-agnostic
allowed-tools: Read Write Shell CallMcpTool Grep
---

# Cohort Retention Analysis

Build retention curves and compare cohorts statistically to identify what drives customer retention and where different segments churn.

## When to Use

Use this skill when:
- Building retention curves for ICP research
- Comparing retention rates between customer segments
- Identifying characteristics of retained vs churned customers
- Measuring the statistical significance of retention differences
- Validating ICP hypotheses with retention data

Do NOT use when:
- Need real-time churn prediction (use `churn-prediction` instead)
- Analyzing individual account health (use `account-360` instead)
- Simple lifecycle stage distribution (use `lifecycle-audit` instead)

---

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `client_id` | string | yes | Client identifier for loading lifecycle config |
| `tenant_id` | string | no | Tenant ID for cost tracking (default: "default") |
| `cohort_field` | string | no | Field to group by (default: "signup_month") |
| `retention_periods` | array | no | Days to measure retention at (default: [7, 14, 30, 60, 90]) |
| `compare_cohorts` | array | no | Specific cohorts to compare (e.g., ["Jan 2026", "Dec 2025"]) |
| `segment_by` | string | no | Additional segmentation field (e.g., "plan_type", "industry") |
| `min_cohort_size` | integer | no | Minimum cohort size for statistical validity (default: 30) |
| `lookback_months` | integer | no | How many months of cohorts to analyze (default: 12) |
| `data_source` | string | no | "warehouse" or "crm" (default: auto-detect) |

**Input schema:** `schemas/input.json`

---

## Outputs

| Name | Type | Description |
|------|------|-------------|
| `retention_curves` | array | Retention rates at each period for each cohort |
| `cohort_comparison` | object | Statistical comparison between cohorts (if requested) |
| `retention_drivers` | array | Factors correlated with higher retention |
| `churn_analysis` | object | Analysis of when and why customers churn |
| `segment_insights` | array | Retention patterns by segment |
| `recommendations` | array | Actionable recommendations based on findings |
| `_meta` | object | Run metadata (cost, duration, data quality) |

**Output schema:** `schemas/output.json`

### Sample Output

```json
{
  "retention_curves": [
    {
      "cohort": "Jan 2026",
      "cohort_size": 145,
      "retention": {
        "day_0": 1.0,
        "day_7": 0.85,
        "day_14": 0.78,
        "day_30": 0.72,
        "day_60": 0.65,
        "day_90": 0.58
      }
    },
    {
      "cohort": "Dec 2025",
      "cohort_size": 132,
      "retention": {
        "day_0": 1.0,
        "day_7": 0.78,
        "day_14": 0.71,
        "day_30": 0.65,
        "day_60": 0.55,
        "day_90": 0.48
      }
    }
  ],
  "cohort_comparison": {
    "cohort_a": "Jan 2026",
    "cohort_b": "Dec 2025",
    "retention_diff_day_30": 0.07,
    "retention_diff_day_90": 0.10,
    "p_value": 0.03,
    "significant": true,
    "effect_size": 0.21,
    "interpretation": "Jan 2026 cohort has significantly higher 90-day retention (58% vs 48%, p=0.03)"
  },
  "retention_drivers": [
    {
      "factor": "completed_onboarding",
      "correlation": 0.72,
      "retained_rate": 0.82,
      "not_retained_rate": 0.35,
      "significance": "high",
      "recommendation": "Focus on onboarding completion - customers who complete onboarding are 2.3x more likely to retain"
    },
    {
      "factor": "engaged_in_first_week",
      "correlation": 0.65,
      "retained_rate": 0.78,
      "not_retained_rate": 0.42,
      "significance": "high",
      "recommendation": "First-week engagement is critical - implement activation campaigns"
    }
  ],
  "churn_analysis": {
    "median_churn_day": 45,
    "churn_spike_periods": ["day_7_to_14", "day_30_to_45"],
    "primary_churn_reasons": [
      { "reason": "no_activity_after_signup", "percentage": 0.35 },
      { "reason": "incomplete_onboarding", "percentage": 0.28 },
      { "reason": "no_value_realized", "percentage": 0.22 }
    ]
  },
  "recommendations": [
    {
      "priority": "high",
      "category": "activation",
      "action": "Implement 7-day onboarding drip campaign",
      "expected_impact": "+8-12% 30-day retention",
      "based_on": "35% of churned customers had no activity after signup"
    }
  ],
  "_meta": {
    "tenant_id": "client_abc",
    "run_id": "cra_2026012901",
    "runtime_seconds": 45.2,
    "cost_usd": 0.65,
    "data_quality": {
      "total_customers_analyzed": 1250,
      "cohorts_analyzed": 12,
      "min_cohort_size": 85,
      "data_completeness": 0.94
    },
    "lifecycle_config_used": "clients/client_abc/context/lifecycle.yaml"
  }
}
```

---

## Dependencies

| Type | Name | Purpose |
|------|------|---------|
| Skill | lifecycle-audit | Provides lifecycle stage definitions |
| MCP | snowflake / bigquery | Data warehouse queries |
| MCP | hubspot / salesforce | CRM customer data |
| Lib | lib/freshness.py | Check lifecycle config freshness |
| Config | clients/{client_id}/context/lifecycle.yaml | Client's lifecycle stage mapping |

---

## Data Requirements

| Requirement | Minimum | Recommended | On Insufficient |
|-------------|---------|-------------|-----------------|
| Customers per cohort | 30 | 100+ | warn_and_continue |
| Total customers | 100 | 500+ | warn_and_continue |
| Cohorts to analyze | 3 | 6+ | warn |
| Customer creation date | 100% | 100% | abort |
| Churn/retention status | 80% | 95% | warn |

---

## SLA (Service Level Agreement)

| Metric | Target | Maximum | Exceeded Action |
|--------|--------|---------|-----------------|
| Runtime | 30s | 5min | timeout_error |
| Retries | 2 | 3 | human_review |
| Cost | $0.75 | $2.50 | abort |

---

## Context Handling

| Input Size | Strategy | Model |
|------------|----------|-------|
| < 1K customers | Inline | claude-sonnet-4 |
| 1K-10K customers | Chunked aggregation | claude-haiku for aggregation, claude-sonnet-4 for synthesis |
| > 10K customers | Pre-aggregated in warehouse | SQL aggregation, claude-sonnet-4 for interpretation |

**Expected input size:** 500-2000 customers, ~5-20K tokens
**Maximum tested:** 50,000 customers (using warehouse pre-aggregation)

---

## Process

1. **Load Client Lifecycle Config**
   - Read `clients/{client_id}/context/lifecycle.yaml`
   - Map client's retention/churn stages to canonical stages
   - Use client's stage names in output

2. **Data Extraction**
   - Query warehouse or CRM for customer data
   - Include: signup date, current status, key engagement events
   - Apply lookback window filter

3. **Cohort Assignment**
   - Group customers by `cohort_field` (default: signup month)
   - Filter cohorts with < `min_cohort_size`
   - Calculate cohort age (days since signup)

4. **Retention Calculation**
   - For each cohort and retention period:
     - Count customers still active at that period
     - Calculate retention rate = active / total
   - Build retention curve array

5. **Statistical Comparison** (if `compare_cohorts` provided)
   - Run chi-square test between specified cohorts
   - Calculate effect size (Cohen's h)
   - Determine statistical significance (p < 0.05)

6. **Driver Identification**
   - Analyze characteristics of retained vs churned
   - Calculate correlation coefficients
   - Rank factors by predictive power

7. **Synthesis & Recommendations**
   - Generate human-readable insights
   - Prioritize recommendations by impact
   - Link to client's lifecycle stages

8. **Quality Check**
   - Validate output schema
   - Check statistical validity
   - Verify recommendations are actionable

---

## Quality Criteria

This skill's output passes if:
- [ ] Schema validation passes
- [ ] At least 3 cohorts analyzed
- [ ] All cohorts have minimum size (30+)
- [ ] Retention rates are between 0 and 1
- [ ] Statistical tests have valid p-values
- [ ] At least 1 retention driver identified
- [ ] At least 1 actionable recommendation generated

---

## Failure Modes

| Mode | Trigger | Output | Escalation |
|------|---------|--------|------------|
| Partial Success | 1+ cohorts too small | Results for valid cohorts + warning | No |
| Data Unavailable | Warehouse/CRM timeout | Cached if <24h, else error | No |
| Insufficient Data | <100 total customers | Error with data requirements | No |
| Quality Failed | Invalid statistical results | Raw data + UNVALIDATED flag | Yes |
| Complete Failure | No customer data found | Error report only | Yes |

---

## Human Review Triggers

| Trigger | Mandatory | Review SLA | Escalation |
|---------|-----------|------------|------------|
| First run for client | Yes | 24h | None |
| Cohort sizes very uneven | Yes | 8h | None |
| Retention < 20% at day 30 | Yes | 4h | Alert team |
| Statistical anomalies detected | Yes | 8h | Auto-flag for review |

---

## Platform-Specific Configuration

### Snowflake

```sql
-- Cohort retention query template
WITH cohorts AS (
  SELECT
    customer_id,
    DATE_TRUNC('month', created_at) AS cohort_month,
    created_at,
    churned_at,
    CASE WHEN churned_at IS NULL OR churned_at > DATEADD(day, {period}, created_at)
         THEN 1 ELSE 0 END AS retained_day_{period}
  FROM {schema}.{customers_table}
  WHERE created_at >= DATEADD(month, -{lookback_months}, CURRENT_DATE)
)
SELECT
  cohort_month,
  COUNT(*) AS cohort_size,
  SUM(retained_day_7) / COUNT(*) AS retention_day_7,
  SUM(retained_day_30) / COUNT(*) AS retention_day_30,
  SUM(retained_day_90) / COUNT(*) AS retention_day_90
FROM cohorts
GROUP BY cohort_month
ORDER BY cohort_month;
```

### HubSpot

```python
# HubSpot contact cohort extraction
def get_hubspot_cohorts(client, lookback_months=12):
    contacts = client.get_all_contacts(
        properties=["createdate", "lifecyclestage", "hs_lifecyclestage_customer_date"]
    )
    # Group by signup month
    # Calculate retention based on current lifecycle stage
```

### BigQuery

```sql
-- BigQuery cohort analysis
SELECT
  FORMAT_DATE('%Y-%m', DATE(created_at)) AS cohort_month,
  COUNT(*) AS cohort_size,
  COUNTIF(DATE_DIFF(CURRENT_DATE(), DATE(created_at), DAY) >= 30
          AND (churned_at IS NULL OR DATE(churned_at) > DATE_ADD(DATE(created_at), INTERVAL 30 DAY)))
    / COUNT(*) AS retention_day_30
FROM `{project}.{dataset}.{table}`
WHERE created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL {lookback_months} MONTH)
GROUP BY cohort_month
ORDER BY cohort_month;
```

---

## Production Readiness

**Status:** [x] Ready

Before marking as production-ready:
- [x] All tests pass
- [x] verify_setup.py runs without errors
- [x] Documentation complete
- [x] Used successfully in 3+ real runs
- [x] Error handling tested
- [x] Performance meets SLA

See `PRODUCTION_READY_CHECKLIST.md` for detailed validation.

---

## Integration with ICP Research Workflow

This skill is Phase 2 of the ICP Research workflow:

```
Phase 1: Context Validation (freshness check)
Phase 2: Data Gathering
  └── cohort-retention-analysis ← YOU ARE HERE
Phase 3: Qualitative Synthesis
Phase 4: ICP Definition
Phase 5: Deliverables
```

The retention analysis feeds into:
- ICP validation (do our best customers match ICP definitions?)
- Segment identification (which segments retain best?)
- Recommendations (what drives retention for our ICP?)

---

## Examples

See `examples/` for annotated input/output pairs.

---

## Tests

See `tests/` for golden outputs and validation prompts.

```bash
claude /test-skill cohort-retention-analysis
```

---

## Setup Verification

```bash
python skills/cohort-retention-analysis/verify_setup.py
```

---

## Quick Reference

See `quick_reference.md` for common usage patterns.

---

## Changelog

### v1.0.0 (2026-01-29)
- Initial release
- Support for Snowflake, BigQuery, Redshift, PostgreSQL, Databricks
- Support for HubSpot, Salesforce, Pipedrive, Zoho, Dynamics
- Statistical comparison with chi-square tests
- Retention driver identification
- Integration with client lifecycle configuration

---

## Notes

- **Lifecycle Config Required**: This skill reads `clients/{client_id}/context/lifecycle.yaml` to use client-specific stage names. Run `client-onboarding` Phase 2.5 first if not configured.
- **Statistical Significance**: Cohort comparisons require minimum 30 customers per cohort for valid chi-square tests.
- **Warehouse vs CRM**: Auto-detects data source based on client config. Warehouse provides more accurate historical data; CRM provides richer customer attributes.
- **Retention Definition**: Uses client's lifecycle config to define "retained" vs "churned" based on their terminology.
