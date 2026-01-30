# Research Company

> Deep company research for client onboarding - analyzes website content, market positioning, and brand voice.

## Quick Start

```bash
# 1. Verify setup
python skills/research-company/verify_setup.py

# 2. Run skill
python skills/research-company/run.py \
  --client_id "abc123" \
  --company_name "Acme Corp" \
  --website_url "https://acme.com"
```

## What It Does

Performs comprehensive company research during client onboarding by:
- Scraping and analyzing the company website
- Extracting company profile, products/services, and value propositions
- Detecting brand voice patterns and key messaging themes
- Generating a structured Company Research document

This is typically the first research skill run during onboarding, providing foundational context for competitor research, founder research, and interview preparation.

## Prerequisites

- Python 3.8+
- Firecrawl API key (set `FIRECRAWL_API_KEY` in `.env`)
- Required packages: `pip install -r requirements.txt`

## Usage

### Basic

```bash
python skills/research-company/run.py \
  --client_id "client_abc" \
  --company_name "Acme Corp" \
  --website_url "https://acme.com"
```

### With Options

```bash
python skills/research-company/run.py \
  --client_id "client_abc" \
  --company_name "Acme Corp" \
  --website_url "https://acme.com" \
  --depth deep \
  --additional_urls "https://blog.acme.com,https://docs.acme.com" \
  --output results.json
```

### Programmatic

```python
from skills.research_company.run import run_research_company

result = run_research_company({
    "client_id": "client_abc",
    "company_name": "Acme Corp",
    "website_url": "https://acme.com",
    "depth": "standard"
})

if result["status"] == "success":
    print(f"Research complete!")
    print(f"Products found: {len(result['output']['products_services'])}")
    print(f"Research doc: {result['output']['research_doc_path']}")
```

## Input

```json
{
  "client_id": "abc123",
  "company_name": "Acme Corp",
  "website_url": "https://acme.com",
  "additional_urls": ["https://blog.acme.com"],
  "industry": "B2B SaaS",
  "depth": "standard"
}
```

## Output

```json
{
  "status": "success",
  "output": {
    "company_profile": {
      "name": "Acme Corp",
      "description": "...",
      "founded": "2020",
      "headquarters": "San Francisco, CA",
      "size": "50-200 employees"
    },
    "market_positioning": {
      "target_audience": "...",
      "value_proposition": "...",
      "differentiators": ["..."]
    },
    "products_services": [
      {"name": "Product A", "description": "...", "pricing": "..."}
    ],
    "brand_voice": {
      "tone": ["professional", "innovative"],
      "personality": "...",
      "key_terms": ["..."]
    },
    "key_messages": ["..."],
    "research_doc_path": "clients/abc123/research/company-research.md"
  },
  "_meta": {
    "client_id": "abc123",
    "runtime_seconds": 45.2,
    "cost_usd": 0.85,
    "pages_scraped": 25
  }
}
```

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `FIRECRAWL_API_KEY` | Yes | Firecrawl API key for web scraping |

## Research Depth Levels

| Level | Pages | Use Case |
|-------|-------|----------|
| `quick` | 5 | Fast overview, time-sensitive |
| `standard` | 20 | Normal onboarding (default) |
| `deep` | 50+ | Complex enterprise clients |

## Output Files

The skill generates:
- `clients/{client_id}/research/company-research.md` - Human-readable research document
- `clients/{client_id}/research/company-research.json` - Structured data for other skills

## Related Documentation

- [SKILL.md](./SKILL.md) - Full specification
- [examples/](./examples/) - Usage examples

## Troubleshooting

**Error: Website unreachable**
- Verify URL is correct and accessible
- Check if site blocks automated access (Cloudflare, etc.)
- Try with a different URL (e.g., blog or docs subdomain)

**Error: Insufficient content**
- Some sites have minimal text content
- Try increasing `depth` parameter
- Add `additional_urls` for more content sources

**Error: Firecrawl API error**
- Verify `FIRECRAWL_API_KEY` is set correctly
- Check Firecrawl rate limits
- Run `verify_setup.py` to diagnose

## Support

For issues, check:
1. `verify_setup.py` output
2. Telemetry logs in `telemetry/`
3. SKILL.md for expected behavior
