# Research Founder

> Per-founder research for client onboarding - analyzes LinkedIn, public content, and voice patterns.

## Quick Start

```bash
# 1. Verify setup
python skills/research-founder/verify_setup.py

# 2. Run skill
python skills/research-founder/run.py \
  --client_id "abc123" \
  --founder_name "John Smith" \
  --linkedin_url "https://linkedin.com/in/johnsmith"
```

## What It Does

Performs deep research on individual founders/executives by:
- Analyzing LinkedIn profile (career history, education, skills)
- Collecting public content (posts, articles, interviews)
- Detecting voice and style patterns
- Identifying areas of expertise
- Generating interview preparation topics
- Creating a structured Founder Research document

This skill runs once per founder - for companies with multiple executives, run it multiple times.

## Prerequisites

- Python 3.8+
- Firecrawl API key (set `FIRECRAWL_API_KEY` in `.env`)
- Required packages: `pip install -r requirements.txt`

## Usage

### Basic (with LinkedIn URL)

```bash
python skills/research-founder/run.py \
  --client_id "client_abc" \
  --founder_name "John Smith" \
  --linkedin_url "https://linkedin.com/in/johnsmith"
```

### Without LinkedIn (will search)

```bash
python skills/research-founder/run.py \
  --client_id "client_abc" \
  --founder_name "John Smith" \
  --founder_title "CEO" \
  --company_name "Acme Corp"
```

### With Multiple Profiles

```bash
python skills/research-founder/run.py \
  --client_id "client_abc" \
  --founder_name "John Smith" \
  --linkedin_url "https://linkedin.com/in/johnsmith" \
  --twitter_handle "johnsmith" \
  --other_profiles "https://medium.com/@johnsmith"
```

### Programmatic

```python
from skills.research_founder.run import run_research_founder

result = run_research_founder({
    "client_id": "client_abc",
    "founder_name": "John Smith",
    "linkedin_url": "https://linkedin.com/in/johnsmith"
})

if result["status"] == "success":
    print(f"Content pieces analyzed: {result['output']['content_analysis']['total_pieces']}")
    print(f"Voice confidence: {result['output']['voice_patterns']['confidence']}")
```

## Input

```json
{
  "client_id": "abc123",
  "founder_name": "John Smith",
  "founder_title": "CEO & Co-Founder",
  "linkedin_url": "https://linkedin.com/in/johnsmith",
  "twitter_handle": "johnsmith",
  "other_profiles": ["https://medium.com/@johnsmith"],
  "company_name": "Acme Corp"
}
```

## Output

```json
{
  "status": "success",
  "output": {
    "founder_profile": {
      "name": "John Smith",
      "title": "CEO & Co-Founder",
      "company": "Acme Corp",
      "location": "San Francisco, CA",
      "career_history": [...],
      "education": [...],
      "skills": [...]
    },
    "content_analysis": {
      "total_pieces": 25,
      "sources": ["linkedin", "twitter", "medium"],
      "topics": [...],
      "posting_frequency": "weekly"
    },
    "voice_patterns": {
      "confidence": 0.75,
      "tone": ["professional", "conversational"],
      "vocabulary_level": "advanced",
      "common_phrases": [...],
      "sentence_structure": "varied"
    },
    "topics_of_expertise": [
      {"topic": "B2B Sales", "confidence": 0.9},
      {"topic": "Startup Growth", "confidence": 0.85}
    ],
    "interview_prep": {
      "recommended_topics": [...],
      "questions_to_explore": [...],
      "gaps_to_fill": [...]
    },
    "research_doc_path": "clients/abc123/research/founder-john-smith.md"
  },
  "_meta": {
    "founder_name": "John Smith",
    "content_pieces_analyzed": 25,
    "runtime_seconds": 52.3,
    "cost_usd": 0.65
  }
}
```

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `FIRECRAWL_API_KEY` | Yes | Firecrawl API key for content scraping |

## Output Files

The skill generates (one set per founder):
- `clients/{client_id}/research/founder-{slug}.md` - Human-readable research document
- `clients/{client_id}/research/founder-{slug}.json` - Structured data for other skills

## Multiple Founders

For companies with multiple founders:

```bash
# Run for each founder
python skills/research-founder/run.py --client_id abc123 --founder_name "John Smith" ...
python skills/research-founder/run.py --client_id abc123 --founder_name "Jane Doe" ...
```

Or programmatically:

```python
founders = [
    {"name": "John Smith", "linkedin_url": "..."},
    {"name": "Jane Doe", "linkedin_url": "..."}
]

for founder in founders:
    result = run_research_founder({
        "client_id": "abc123",
        "founder_name": founder["name"],
        "linkedin_url": founder["linkedin_url"]
    })
```

## Related Documentation

- [SKILL.md](./SKILL.md) - Full specification
- [examples/](./examples/) - Usage examples

## Troubleshooting

**Error: LinkedIn profile not found**
- Verify the LinkedIn URL is correct
- Try providing `company_name` and `founder_title` for better search
- Some profiles may be private or restricted

**Error: Insufficient content for voice analysis**
- Founder may not have much public content
- Add `twitter_handle` or `other_profiles` for more sources
- Voice analysis will run with low confidence warning

**Error: Wrong person identified**
- Common names may return wrong profile
- Provide `linkedin_url` directly to avoid ambiguity
- Add `company_name` to help disambiguation

## Support

For issues, check:
1. `verify_setup.py` output
2. Telemetry logs in `telemetry/`
3. SKILL.md for expected behavior
