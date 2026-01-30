# Quick Reference: Cohort Retention Analysis

## Usage

```bash
# Basic usage - analyze all cohorts for a client
claude /run-skill cohort-retention-analysis --client_id FFC

# Compare specific cohorts
claude /run-skill cohort-retention-analysis --client_id FFC --compare_cohorts "Jan 2026,Dec 2025"

# Custom retention periods
claude /run-skill cohort-retention-analysis --client_id FFC --retention_periods "7,30,90,180"

# Segment by a field
claude /run-skill cohort-retention-analysis --client_id FFC --segment_by plan_type
```

---

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--client_id` | string | required | Client identifier |
| `--tenant_id` | string | default | Tenant for cost tracking |
| `--cohort_field` | string | signup_month | Field to group by |
| `--retention_periods` | array | 7,14,30,60,90 | Days to measure |
| `--compare_cohorts` | array | none | Two cohorts to compare |
| `--segment_by` | string | none | Additional segmentation |
| `--lookback_months` | int | 12 | Months of history |
| `--min_cohort_size` | int | 30 | Minimum for validity |

---

## Common Patterns

### Pattern 1: Monthly Retention Report
```bash
# Generate retention curves for all monthly cohorts in the past year
claude /run-skill cohort-retention-analysis --client_id FFC --lookback_months 12
```

### Pattern 2: A/B Cohort Comparison
```bash
# Compare retention between two specific cohorts with statistical significance
claude /run-skill cohort-retention-analysis --client_id FFC --compare_cohorts "Jan 2026,Dec 2025"
```

### Pattern 3: Segment Analysis
```bash
# Analyze retention by customer segment (e.g., plan type, industry)
claude /run-skill cohort-retention-analysis --client_id FFC --segment_by industry
```

### Pattern 4: Extended Retention Windows
```bash
# Measure retention at longer intervals for SaaS annual contracts
claude /run-skill cohort-retention-analysis --client_id FFC --retention_periods "30,90,180,365"
```

---

## Input Format

```json
{
  "client_id": "FFC",
  "cohort_field": "signup_month",
  "retention_periods": [7, 14, 30, 60, 90],
  "compare_cohorts": ["Jan 2026", "Dec 2025"],
  "lookback_months": 12,
  "min_cohort_size": 30
}
```

---

## Output Format

```json
{
  "retention_curves": [
    {
      "cohort": "Jan 2026",
      "cohort_size": 145,
      "retention": {"day_0": 1.0, "day_7": 0.85, "day_30": 0.72}
    }
  ],
  "cohort_comparison": {
    "cohort_a": "Jan 2026",
    "cohort_b": "Dec 2025",
    "p_value": 0.03,
    "significant": true
  },
  "retention_drivers": [...],
  "recommendations": [...],
  "_meta": {
    "cost_usd": 0.65,
    "runtime_seconds": 45.2
  }
}
```

---

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `Missing lifecycle config` | No lifecycle.yaml | Run client-onboarding Phase 2.5 |
| `Cohort too small` | < min_cohort_size | Lower min_cohort_size or wait for more data |
| `No customer data` | Empty warehouse/CRM | Check data source configuration |
| `Statistical test failed` | Insufficient variance | Need more diverse cohorts |

---

## Prerequisites

1. **Lifecycle Config**: Client must have `clients/{client_id}/context/lifecycle.yaml`
   - Run `client-onboarding` Phase 2.5 if missing

2. **Data Source**: Either warehouse or CRM must be configured
   - Check `clients/{client_id}/config/datasources.yaml`

3. **Minimum Data**:
   - 100+ total customers
   - 30+ customers per cohort
   - 3+ cohorts to analyze

---

## Related Skills

- `client-onboarding` - Creates lifecycle.yaml (Phase 2.5)
- `lifecycle-audit` - Stage distribution analysis
- `churn-prediction` - Real-time churn prediction
- `account-360` - Individual account deep dive
- `incorporate-interview-results` - Qualitative validation

---

## Tips

1. **Start with defaults**: Run without custom params first to see what data looks like
2. **Check data quality**: Look at `_meta.data_quality` for warnings
3. **Statistical significance**: p < 0.05 = significant difference between cohorts
4. **Retention drivers**: Focus on high-correlation factors for quick wins
5. **Use lifecycle config**: Ensures output uses client's terminology
