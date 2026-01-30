# Lifecycle Audit Template

Comprehensive analysis of customer lifecycle stages, engagement patterns, and churn risk.

## Overview

This template creates modules for analyzing customer lifecycle health. It examines:

- **Stage Distribution**: How customers are distributed across lifecycle stages
- **Conversion Bottlenecks**: Where customers get stuck in the journey
- **Churn Risk**: Which accounts are at risk of leaving
- **Upsell Opportunities**: Which accounts are ready for expansion
- **Recommendations**: Actionable steps to improve journey health

## When to Use

Use this template when a client needs:
- Customer health assessment
- Churn risk analysis
- Pipeline conversion analysis
- Retention strategy input
- ICP validation with lifecycle data

## Prerequisites

### Required
- CRM access (HubSpot, Salesforce, Pipedrive, Zoho, or Dynamics)
- Minimum 20 customer records with lifecycle stage assigned
- Budget approval ($5-15 estimated)

### Optional (Recommended)
- Data warehouse access for usage/engagement enrichment
- Historical data (12+ months) for trend analysis
- Revenue data for prioritization

## Skills Used

| Skill | Purpose | Required |
|-------|---------|----------|
| `lifecycle-audit` | Core stage analysis | Yes |
| `cohort-retention-analysis` | Retention curves | No |
| `churn-prediction` | Risk scoring | No |
| `at-risk-detection` | Engagement decline | No |

## Configuration

The template uses client configuration from `clients/{client_id}/config/`:

```yaml
# datasources.yaml
crm:
  type: hubspot  # or salesforce, pipedrive, zoho, dynamics

warehouse:
  type: snowflake  # optional, for enrichment

thresholds:
  high_value_min: 10000  # Minimum ARR for high-value accounts
```

## Outputs

| Output | Format | Description |
|--------|--------|-------------|
| Stage Distribution | JSON | Customer counts by lifecycle stage |
| Health Score | Number | Overall journey health (0-1) |
| At-Risk List | JSON | Accounts flagged for churn risk |
| Upsell Candidates | JSON | Accounts ready for expansion |
| Recommendations | Markdown | Prioritized action items |

## Usage

### CLI

```bash
# Create module from template
./mh1 module create --template lifecycle-audit --client acme-corp --name "Q1 Lifecycle Audit"

# Run the module
./mh1 module run lifecycle-audit-abc123
```

### Programmatic

```python
from lib.template_manager import TemplateManager

tm = TemplateManager()
module = tm.create_module_from_template(
    template_id="lifecycle-audit",
    client_id="acme-corp",
    name="Q1 Lifecycle Audit",
    customizations={
        "limit": 500,  # Override default limit
        "include_retention": True  # Enable optional cohort analysis
    }
)

print(f"Created module: {module.module_id}")
```

## Customization

### Skill Selection

Modify `.plan.md` to enable/disable optional skills:

```yaml
skills:
  - name: cohort-retention-analysis
    required: true  # Changed from false
```

### Thresholds

Override in MRD.md or module meta:

```yaml
customizations:
  thresholds:
    at_risk_score: 0.7  # Lower threshold for risk detection
    high_value_min: 5000  # Lower revenue threshold
```

## Quality Gates

| Gate | Threshold | Action if Failed |
|------|-----------|------------------|
| Data completeness | 80% | Warn and continue |
| Eval score | 0.8 | Human review |
| Recommendation count | >= 3 | Regenerate |

## Related Templates

- `competitive-intel` - Competitor analysis
- `content-production` - Marketing content creation
- `gtm-plan` - Go-to-market planning

## Changelog

### v1.0.0 (2026-01-29)
- Initial template release
- Core lifecycle-audit skill integration
- Optional cohort and churn analysis
