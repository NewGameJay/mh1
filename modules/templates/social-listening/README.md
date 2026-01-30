# Social Listening Template

Monitor and analyze social media conversations to inform content strategy and surface opportunities.

## Overview

This template creates modules for collecting social signals:

- **Multi-Platform Collection**: LinkedIn, Twitter, Reddit
- **ICP Relevance Scoring**: Prioritize high-value signals
- **Deduplication**: Remove cross-platform duplicates
- **Persistence**: Store to Firebase for ongoing analysis

## When to Use

Use this template when a client needs:
- Fresh signals for content production
- Competitor mention monitoring
- Industry trend tracking
- Building a signal database
- Content inspiration sources

## Prerequisites

### Required
- Keywords file at `clients/{client_id}/social-listening/keywords.md`
- ICP context for relevance scoring
- Firebase MCP configured
- Budget approval ($5-15 estimated)

### Optional (Recommended)
- Thought leader list for boosted scoring
- Competitor handles for SOV analysis
- Historical signal data for comparison

## Skills Used

| Skill | Purpose | Required |
|-------|---------|----------|
| `social-listening-collect` | Main orchestration | Yes |
| `linkedin-keyword-search` | LinkedIn collection | Called by main |
| `twitter-keyword-search` | Twitter collection | Called by main |
| `reddit-keyword-search` | Reddit collection | Called by main |
| `reddit-content-analyzer` | Deep Reddit analysis | No |

## Keywords File Format

Create `clients/{client_id}/social-listening/keywords.md`:

```markdown
# Social Listening Keywords

## Brand Keywords
- "Company Name"
- @companyhandle

## Product Keywords
- "product name"
- feature keywords

## Competitor Keywords
- "Competitor A"
- "Competitor B"

## Industry Keywords
- industry term 1
- industry term 2

## Pain Point Keywords
- "problem statement"
- "how do I..."
```

## Outputs

| Output | Format | Description |
|--------|--------|-------------|
| Scored Posts | JSON | Posts with relevance scores |
| Collection Report | Markdown | Summary with statistics |
| Top Signals | JSON | Highest relevance posts |
| Platform Stats | JSON | Breakdown by platform |

## Usage

### CLI

```bash
# Create module from template
./mh1 module create --template social-listening --client acme-corp --name "Weekly Signals"

# Run with specific date range
./mh1 module run social-listen-abc123 --date_range past-week
```

### Programmatic

```python
from lib.template_manager import TemplateManager

tm = TemplateManager()
module = tm.create_module_from_template(
    template_id="social-listening",
    client_id="acme-corp",
    name="Weekly Signal Collection",
    customizations={
        "platforms": ["linkedin", "twitter"],
        "date_range": "past-week"
    }
)
```

## Quality Gates

| Gate | Threshold | Action if Failed |
|------|-----------|------------------|
| Platform coverage | 100% | Retry failed platforms |
| Relevance scoring | 100% | Score missing posts |
| Minimum volume | 10+ posts | Broaden keywords |

## Customization

### Platforms

```yaml
customizations:
  platforms: ["linkedin"]  # LinkedIn only
```

### Date Range

```yaml
customizations:
  date_range: "past-month"  # Default is past-week
```

### Minimum Relevance

```yaml
customizations:
  min_relevance: 7  # Only high-relevance posts
```

## Related Templates

- `content-production` - Use signals for content
- `competitive-intel` - Deep competitor analysis
- `gtm-plan` - Market intelligence

## Changelog

### v1.0.0 (2026-01-29)
- Initial template release
- Core social-listening-collect integration
- Multi-platform parallel collection
