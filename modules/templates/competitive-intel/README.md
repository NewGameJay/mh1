# Competitive Intelligence Template

Deep competitive analysis for strategic differentiation and sales enablement.

## Overview

This template creates modules for comprehensive competitive analysis:

- **Competitor Profiles**: Detailed company research
- **Feature Comparison**: Side-by-side capability matrix
- **Positioning Analysis**: Market positioning and messaging
- **SWOT Analysis**: Strengths, weaknesses, opportunities, threats
- **Battle Cards**: Sales-ready competitive talking points

## When to Use

Use this template when a client needs:
- Updated competitive landscape analysis
- Sales battle cards
- Differentiation strategy
- GTM competitive positioning
- Win/loss context

## Prerequisites

### Required
- List of competitors to analyze (3-7 recommended)
- Company context for baseline comparison
- Budget approval ($15-40 estimated)

### Optional (Recommended)
- Existing competitive intel for validation
- Crunchbase access for funding/hiring data
- LinkedIn access for team research
- Customer win/loss feedback

## Skills Used

| Skill | Purpose | Required |
|-------|---------|----------|
| `research-company` | Competitor research | Yes |
| `research-competitors` | Structured comparison | Yes |
| `positioning-angles` | Differentiation | No |
| `social-listening-collect` | Social monitoring | No |

## Focus Areas

| Area | Description |
|------|-------------|
| positioning | How they position in market |
| features | Product capabilities |
| messaging | Claims and value props |
| pricing | Pricing model and tiers |
| hiring | Team growth signals |
| funding | Investment and runway |
| content_strategy | Content approach |

## Outputs

| Output | Format | Description |
|--------|--------|-------------|
| Competitor Profiles | JSON | Detailed company info |
| Feature Matrix | JSON | Side-by-side comparison |
| Positioning Analysis | Markdown | Market positioning |
| SWOT Analysis | Markdown | Strategic assessment |
| Battle Cards | JSON | Sales-ready cards |

## Usage

### CLI

```bash
# Create module from template
./mh1 module create --template competitive-intel --client acme-corp --name "Q1 Competitive Analysis"

# Run with specific competitors
./mh1 module run comp-intel-abc123 --competitors "Competitor A,Competitor B,Competitor C"
```

### Programmatic

```python
from lib.template_manager import TemplateManager

tm = TemplateManager()
module = tm.create_module_from_template(
    template_id="competitive-intel",
    client_id="acme-corp",
    name="Q1 Competitive Analysis",
    customizations={
        "competitors": ["Competitor A", "Competitor B", "Competitor C"],
        "focus_areas": ["positioning", "features", "messaging"]
    }
)
```

## Quality Gates

| Gate | Threshold | Action if Failed |
|------|-----------|------------------|
| Competitor coverage | 100% | Research missing competitors |
| Data recency | 70% current | Flag stale data |
| Analysis depth | 80% | Expand focus areas |
| Eval score | >= 0.8 | Human review |

## Customization

### Focus Areas

```yaml
customizations:
  focus_areas:
    - positioning
    - pricing
    - features
```

### Competitor Count

```yaml
customizations:
  competitor_count: 7  # Default is 5
```

## Related Templates

- `gtm-plan` - Use intel for GTM strategy
- `content-production` - Competitive content
- `lifecycle-audit` - Customer retention context

## Changelog

### v1.0.0 (2026-01-29)
- Initial template release
- Core research and comparison skills
- Battle card generation
