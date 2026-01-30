# Qualify Leads

Transform LinkedIn post engagement into qualified sales leads with personalized outreach messages.

## Overview

This skill:

- **Pulls reactors/commenters** from posts in the past week
- **Qualifies against ICP** criteria to filter out non-targets
- **Enriches lead profiles** with company, role, and engagement data
- **Generates draft messages** personalized to each lead's context

## Quick Start

### CLI

```bash
# Basic run (reads client from active_client.md)
python skills/qualify-leads/run.py --founder_id xyz123

# With explicit client
python skills/qualify-leads/run.py --client_id abc123 --founder_id xyz123

# Custom lookback period (last 14 days instead of 7)
python skills/qualify-leads/run.py --founder_id xyz123 --lookback_days 14

# Without message generation
python skills/qualify-leads/run.py --founder_id xyz123 --no-messages
```

### Programmatic

```python
from skills.qualify_leads.run import run_qualify_leads

result = run_qualify_leads({
    "client_id": "abc123",
    "founder_id": "xyz789",
    "lookback_days": 7,
    "generate_messages": True
})

for lead in result['output']['qualified_leads']:
    print(f"{lead['name']} ({lead['icp_type']}): {lead['reason']}")
```

## Parameters

| Parameter           | Required | Default | Description                              |
|---------------------|----------|---------|------------------------------------------|
| `client_id`         | No*      | -       | Firebase Client ID                       |
| `founder_id`        | Yes      | -       | Founder/profile document ID              |
| `lookback_days`     | No       | 7       | Days to pull reactors from               |
| `icp_definitions`   | No       | -       | Override ICP definitions                 |
| `include_commenters`| No       | true    | Include post commenters                  |
| `include_reactors`  | No       | true    | Include post reactors                    |
| `generate_messages` | No       | true    | Generate draft outreach messages         |

*Required if not in `inputs/active_client.md`

## Output Structure

```json
{
  "summary": {
    "period": "2026-01-20 to 2026-01-27",
    "posts_analyzed": 12,
    "total_engagers": 234,
    "qualified_leads": 28,
    "qualification_rate": 0.12,
    "by_icp_type": {
      "Primary": 12,
      "Secondary": 16
    }
  },
  "qualified_leads": [
    {
      "name": "Sarah Chen",
      "company": "TechCorp Solutions",
      "role": "VP of Marketing",
      "origin_post_url": "https://linkedin.com/posts/founder-123",
      "icp_type": "Primary",
      "reason": "VP-level marketing leader at B2B SaaS company",
      "draft_msg": "Hi Sarah, I noticed you liked my post about...",
      "engagement_type": "reaction",
      "linkedin_url": "https://linkedin.com/in/sarah-chen",
      "confidence": 0.92
    }
  ],
  "disqualified": {
    "total": 206,
    "reasons": {
      "title_mismatch": 89,
      "company_size_mismatch": 54,
      "industry_mismatch": 42,
      "insufficient_data": 21
    }
  },
  "recommendations": [
    "12 high-priority leads (Primary ICP) - reach out within 48h",
    "Post about 'Marketing Automation' generated most qualified leads"
  ]
}
```

## Qualified Lead Fields

| Field             | Type     | Description                                          |
|-------------------|----------|------------------------------------------------------|
| `name`            | string   | Full name                                            |
| `company`         | string   | Company name                                         |
| `role`            | string   | Job title/role                                       |
| `origin_post_url` | string   | LinkedIn post URL they engaged with                  |
| `icp_type`        | string   | ICP segment: "Primary", "Secondary", etc.            |
| `reason`          | string   | Specific qualification criteria matched              |
| `draft_msg`       | string   | Personalized outreach message                        |
| `engagement_type` | string   | "reaction", "comment", or "both"                     |
| `linkedin_url`    | string   | Profile URL (if available)                           |
| `confidence`      | number   | Match confidence (0-1)                               |

## ICP Definitions

ICP matching uses definitions from your client context. Example:

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

## Message Personalization

Generated messages follow this structure:

1. **Hook**: Reference the specific post they engaged with
2. **Connection**: Acknowledge their role and company
3. **Value prop**: Brief mention of relevant solution
4. **CTA**: Soft ask for conversation

Example:
```
Hi Sarah, I noticed you liked my post about marketing automation challenges. 
As VP of Marketing at TechCorp, I imagine you're dealing with similar scaling issues. 
Would love to share how we've helped similar teams — open to a quick chat?
```

## Prerequisites

1. **Posts exist**: Have LinkedIn posts in Firebase
2. **Reactors collected**: Run `social-listening-collect` to gather reactor data
3. **ICP defined**: Have ICP definitions in client context

## Files

```
skills/qualify-leads/
├── SKILL.md           # Full skill specification
├── README.md          # This file
├── run.py             # Main entry point
└── schemas/
    ├── input.json     # Input schema
    └── output.json    # Output schema
```

## Workflow Integration

This skill is typically used in a weekly workflow:

1. `social-listening-collect` - Gather reactor data from LinkedIn posts
2. `icp-historical-analysis` - Analyze overall ICP engagement trends
3. **`qualify-leads`** - Generate actionable lead list with messages
4. Export to CRM or outreach tool

## See Also

- [icp-historical-analysis](../icp-historical-analysis/) - Analyze ICP engagement trends
- [social-listening-collect](../social-listening-collect/) - Collect reactor data
- [ghostwrite-content](../ghostwrite-content/) - Create posts that attract ICP
