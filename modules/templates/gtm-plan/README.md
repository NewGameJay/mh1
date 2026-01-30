# GTM Plan Template

Go-to-market planning and execution support with competitive analysis, personas, and positioning.

## Overview

This template creates modules for developing comprehensive GTM strategies:

- **Competitive Analysis**: Landscape research and SWOT analysis
- **Persona Development**: Target audience definition with pain points
- **Positioning**: Differentiated messaging and value propositions
- **Execution Roadmap**: Phased plan with milestones

## When to Use

Use this template when a client needs:
- New product launch strategy
- Market expansion planning
- Competitive repositioning
- Response to competitive threats
- Marketing strategy foundation

## Prerequisites

### Required
- Company profile and product information
- Target market definition
- Clear GTM objective
- Budget approval ($15-40 estimated)

### Optional (Recommended)
- Existing customer data for persona validation
- Previous competitive intelligence
- Historical campaign performance data
- CRM access for customer insights

## Skills Used

| Skill | Purpose | Required |
|-------|---------|----------|
| `research-company` | Company & market context | Yes |
| `research-competitors` | Competitive landscape | Yes |
| `extract-audience-persona` | Target personas | Yes |
| `positioning-angles` | Messaging framework | Yes |
| `gtm-engineering` | Execution roadmap | No |

## GTM Objectives

| Objective | Focus |
|-----------|-------|
| `new_product_launch` | Awareness, positioning, launch timing |
| `market_expansion` | New segments, localization, partnerships |
| `repositioning` | Messaging pivot, competitive differentiation |
| `competitive_response` | Counter-positioning, feature comparison |

## Outputs

| Output | Format | Description |
|--------|--------|-------------|
| Competitive Analysis | Markdown | SWOT and landscape analysis |
| Persona Profiles | JSON | Target audience definitions |
| Messaging Framework | Markdown | Positioning and value props |
| GTM Roadmap | Markdown | Phased execution plan |

## Usage

### CLI

```bash
# Create module from template
./mh1 module create --template gtm-plan --client acme-corp --name "Q2 Product Launch"

# Run with specific objective
./mh1 module run gtm-plan-abc123 --objective new_product_launch
```

### Programmatic

```python
from lib.template_manager import TemplateManager

tm = TemplateManager()
module = tm.create_module_from_template(
    template_id="gtm-plan",
    client_id="acme-corp",
    name="Q2 Product Launch GTM",
    customizations={
        "gtm_objective": "new_product_launch",
        "competitor_count": 5,
        "persona_count": 3
    }
)
```

## Quality Gates

| Gate | Threshold | Action if Failed |
|------|-----------|------------------|
| Research depth | 5+ competitors | Expand research |
| Persona validation | Data-backed | Cross-ref with CRM |
| Differentiation | Clear unique positioning | Refine messaging |
| Eval score | >= 0.8 | Human review |

## Customization

### Competitor Count

```yaml
customizations:
  competitor_count: 7  # Default is 5
```

### Timeline

```yaml
customizations:
  timeline_weeks: 16  # Default is 12
```

### Focus Areas

```yaml
customizations:
  focus_areas:
    - competitive_differentiation
    - channel_strategy
    - pricing_positioning
```

## Related Templates

- `lifecycle-audit` - Customer analysis for ICP validation
- `content-production` - Execute content from GTM strategy
- `competitive-intel` - Deep competitive analysis

## Changelog

### v1.0.0 (2026-01-29)
- Initial template release
- Core research and positioning skills
- Optional GTM engineering skill
