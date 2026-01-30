# Research Competitors

> Competitor analysis for client onboarding - identifies top competitors and compares positioning, features, and content strategies.

## Quick Start

```bash
# 1. Verify setup
python skills/research-competitors/verify_setup.py

# 2. Run skill
python skills/research-competitors/run.py \
  --client_id "abc123" \
  --company_name "Acme Corp" \
  --industry "B2B SaaS"
```

## What It Does

Performs comprehensive competitor analysis during client onboarding by:
- Discovering top 5-10 competitors via search
- Scraping and analyzing competitor websites
- Comparing positioning, features, and pricing
- Identifying market gaps and opportunities
- Analyzing competitor content strategies
- Generating a structured Competitor Research document

This skill builds on company research to understand the competitive landscape and inform content strategy.

## Prerequisites

- Python 3.8+
- Firecrawl API key (set `FIRECRAWL_API_KEY` in `.env`)
- SerpAPI key (set `SERPAPI_KEY` in `.env`)
- Required packages: `pip install -r requirements.txt`

## Usage

### Basic

```bash
python skills/research-competitors/run.py \
  --client_id "client_abc" \
  --company_name "Acme Corp" \
  --industry "B2B SaaS"
```

### With Known Competitors

```bash
python skills/research-competitors/run.py \
  --client_id "client_abc" \
  --company_name "Acme Corp" \
  --industry "B2B SaaS" \
  --known_competitors "Competitor1,https://competitor2.com" \
  --competitor_count 8
```

### Programmatic

```python
from skills.research_competitors.run import run_research_competitors

result = run_research_competitors({
    "client_id": "client_abc",
    "company_name": "Acme Corp",
    "industry": "B2B SaaS",
    "competitor_count": 5
})

if result["status"] == "success":
    print(f"Competitors analyzed: {len(result['output']['competitors'])}")
    print(f"Market gaps found: {len(result['output']['market_gaps'])}")
```

## Input

```json
{
  "client_id": "abc123",
  "company_name": "Acme Corp",
  "industry": "B2B SaaS",
  "known_competitors": ["Competitor1", "https://competitor2.com"],
  "competitor_count": 5
}
```

## Output

```json
{
  "status": "success",
  "output": {
    "competitors": [
      {
        "name": "Competitor1",
        "website": "https://competitor1.com",
        "description": "...",
        "products": [...],
        "pricing": {...},
        "target_audience": "...",
        "differentiators": [...],
        "content_approach": {...}
      }
    ],
    "positioning_matrix": {
      "features": [...],
      "comparison": {...}
    },
    "market_gaps": [
      {"gap": "...", "opportunity": "...", "priority": "high"}
    ],
    "content_strategies": [...],
    "research_doc_path": "clients/abc123/research/competitor-research.md"
  },
  "_meta": {
    "competitors_analyzed": 5,
    "runtime_seconds": 95.2,
    "cost_usd": 1.25
  }
}
```

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `FIRECRAWL_API_KEY` | Yes | Firecrawl API key for web scraping |
| `SERPAPI_KEY` | Yes | SerpAPI key for competitor discovery |

## Competitor Discovery

The skill discovers competitors through:
1. Search queries like "[company_name] competitors" and "[industry] companies"
2. Known competitors provided in input
3. Links found on industry directory sites

Results are deduplicated and validated before analysis.

## Output Files

The skill generates:
- `clients/{client_id}/research/competitor-research.md` - Human-readable research document
- `clients/{client_id}/research/competitor-research.json` - Structured data for other skills

## Related Documentation

- [SKILL.md](./SKILL.md) - Full specification
- [examples/](./examples/) - Usage examples

## Troubleshooting

**Error: No competitors found**
- Verify industry classification is correct
- Try providing known competitors manually
- Check if SerpAPI key is valid

**Error: Insufficient competitor data**
- Some competitor sites may block scraping
- Try with different competitors
- Increase `competitor_count` to compensate

**Error: Timeout**
- Reduce `competitor_count`
- Some competitor sites may be slow
- Check network connectivity

## Support

For issues, check:
1. `verify_setup.py` output
2. Telemetry logs in `telemetry/`
3. SKILL.md for expected behavior
