# Content Production Template

Create marketing content including LinkedIn posts, email sequences, and social media calendars.

## Overview

This template creates modules for producing authentic marketing content:

- **LinkedIn Posts**: Ghostwritten in the founder's voice
- **Email Sequences**: Nurture and campaign emails
- **Newsletters**: Curated content digests
- **Content Calendar**: Organized publishing schedule

## When to Use

Use this template when a client needs:
- Weekly/monthly LinkedIn content production
- Founder thought leadership content
- Email nurture sequences
- Content calendar planning
- Consistent brand voice across channels

## Prerequisites

### Required
- Voice contract for the founder/author
- Brand context documents (messaging, audience, positioning)
- Minimum 10 founder posts for voice analysis
- Firebase access for content storage

### Optional (Recommended)
- Fresh social signals (< 7 days old)
- Thought leader posts for trending topics
- Historical high-performing content

## Skills Used

| Skill | Purpose | Required |
|-------|---------|----------|
| `ghostwrite-content` | LinkedIn post generation | Yes |
| `social-listening-collect` | Content inspiration | No |
| `email-sequences` | Email campaign creation | No |
| `newsletter-builder` | Newsletter compilation | No |
| `content-atomizer` | Long-form breakdown | No |

## Voice Contract

Content quality depends on a well-defined voice contract:

```yaml
voice_contract:
  characteristics:
    tone: conversational, direct
    vocabulary: accessible, no jargon
    sentence_length: short to medium
    formality: professional casual

  signature_phrases:
    - "Here's what I learned..."
    - "Let me be direct..."

  anti_patterns:
    - em_dashes
    - rhetorical_questions
    - structures_of_three
    - corporate_buzzwords
```

## Outputs

| Output | Format | Description |
|--------|--------|-------------|
| Content Calendar | JSON/Markdown | Scheduled posts with dates |
| LinkedIn Posts | JSON | Ready-to-publish posts |
| Voice Analysis | JSON | Confidence scores per post |
| QA Report | Markdown | AI tells check results |

## Usage

### CLI

```bash
# Create module from template
./mh1 module create --template content-production --client acme-corp --name "February LinkedIn"

# Run with specific founder
./mh1 module run content-prod-abc123 --founder_id xyz789 --post_count 20
```

### Programmatic

```python
from lib.template_manager import TemplateManager

tm = TemplateManager()
module = tm.create_module_from_template(
    template_id="content-production",
    client_id="acme-corp",
    name="February LinkedIn Content",
    customizations={
        "founder_id": "founder-xyz",
        "post_count": 20,
        "include_email": True
    }
)
```

## Quality Gates

| Gate | Threshold | Action if Failed |
|------|-----------|------------------|
| Voice confidence | >= 7/10 avg | Regenerate with stricter constraints |
| AI tells | Zero | QA review and fix |
| Completeness | 100% | Retry failed posts |
| Eval score | >= 0.8 | Human review |

## Customization

### Post Count

```yaml
customizations:
  post_count: 30  # Override default 20
```

### Platform

```yaml
customizations:
  platform: twitter  # Default is linkedin
```

### Include Optional Skills

```yaml
customizations:
  include_email: true
  include_newsletter: true
  run_social_listening: true
```

## Related Templates

- `social-listening` - Collect signals before production
- `gtm-plan` - Strategic content planning
- `competitive-intel` - Differentiation insights

## Changelog

### v1.0.0 (2026-01-29)
- Initial template release
- Core ghostwrite-content integration
- Optional email and newsletter support
