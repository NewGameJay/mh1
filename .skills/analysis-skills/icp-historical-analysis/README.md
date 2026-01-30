# ICP Historical Analysis

Analyze LinkedIn post engagement to measure ICP (Ideal Customer Profile) engagement rates and identify high-performing content themes.

## Overview

This skill provides weekly analysis of:

- **ICP Engagement Rate**: What percentage of your post reactors match your ideal customer profile?
- **Week-over-Week Trends**: Is your ICP engagement improving or declining?
- **Theme Performance**: Which content themes resonate most with your ICP?
- **Historical Baseline**: How does recent performance compare to your all-time averages?

## Quick Start

### CLI

```bash
# Basic run (reads client from active_client.md)
python skills/icp-historical-analysis/run.py --founder_id xyz123

# With explicit client
python skills/icp-historical-analysis/run.py --client_id abc123 --founder_id xyz123

# Custom lookback period
python skills/icp-historical-analysis/run.py --founder_id xyz123 --lookback_days 30
```

### Programmatic

```python
from skills.icp_historical_analysis.run import run_icp_historical_analysis

result = run_icp_historical_analysis({
    "client_id": "abc123",
    "founder_id": "xyz789",
    "lookback_days": 14
})

print(f"ICP Engagement Rate: {result['output']['summary']['icp_engagement_rate']:.0%}")
```

## Parameters

| Parameter        | Required | Default | Description                              |
|------------------|----------|---------|------------------------------------------|
| `client_id`      | No*      | -       | Firebase Client ID                       |
| `founder_id`     | Yes      | -       | Founder/profile document ID              |
| `lookback_days`  | No       | 14      | Days to analyze                          |
| `icp_definitions`| No       | -       | Override ICP definitions                 |
| `min_engagement` | No       | 0       | Minimum engagement to include post       |

*Required if not in `inputs/active_client.md`

## Output Structure

```json
{
  "summary": {
    "period": "2026-01-13 to 2026-01-27",
    "total_posts": 18,
    "total_reactors": 342,
    "avg_reactors_per_post": 19.0,
    "icp_engagement_rate": 0.23,
    "week_over_week_change": "+12%"
  },
  "week1_analysis": {
    "posts": 10,
    "reactors": 198,
    "avg_reactors": 19.8,
    "icp_matches": 48,
    "icp_rate": 0.24
  },
  "week2_analysis": {
    "posts": 8,
    "reactors": 144,
    "avg_reactors": 18.0,
    "icp_matches": 31,
    "icp_rate": 0.22
  },
  "theme_analysis": [
    {
      "theme": "Product Updates",
      "posts": 5,
      "icp_rate": 0.31,
      "recommendation": "high_performer"
    }
  ],
  "recommendations": [
    "Increase Product Update posts - 31% ICP engagement vs 23% average"
  ]
}
```

## ICP Definitions

ICP matching uses definitions from your client context. Example structure:

```markdown
# ICP Definition

## Primary ICP
- Title: VP/Director of Marketing, CMO
- Company Size: 50-500 employees
- Industry: B2B SaaS, Technology
- Seniority: Director+

## Secondary ICP  
- Title: Growth Manager, Demand Gen Manager
- Company Size: 20-200 employees
- Industry: B2B SaaS
- Seniority: Manager+
```

## Prerequisites

1. **Posts collected**: Run `ghostwrite-content` or have historical posts
2. **Reactors collected**: Run `social-listening-collect` to gather reactor data
3. **ICP defined**: Have ICP definitions in client context

## Scheduled Execution

This skill is designed to run weekly. Configure in your scheduler:

```yaml
# cron or workflow trigger
schedule: "0 9 * * 1"  # Every Monday at 9 AM
```

## Files

```
skills/icp-historical-analysis/
├── SKILL.md           # Full skill specification
├── README.md          # This file
├── run.py             # Main entry point
└── schemas/
    ├── input.json     # Input schema
    └── output.json    # Output schema
```

## See Also

- [qualify-leads](../qualify-leads/) - Use ICP analysis to qualify individual leads
- [social-listening-collect](../social-listening-collect/) - Collect reactor data
- [ghostwrite-content](../ghostwrite-content/) - Generate content based on themes
