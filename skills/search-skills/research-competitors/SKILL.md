---
name: research-competitors
description: |
  Perform comprehensive competitor analysis with positioning matrix and market gap identification.
  Use when asked to 'research competitors', 'find competitors', 'analyze competitive landscape'.
license: Proprietary
compatibility:
  - firecrawl
  - serpapi
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  estimated_runtime: "2-5min"
  client_facing: false
  tags:
    - research
    - competitors
    - market-analysis
allowed-tools: Read Write Shell CallMcpTool
---

# Skill: Research Competitors

## When to Use

Use this skill when you need to:
- Identify and analyze competitors during client onboarding
- Build a competitive positioning matrix
- Find market gaps and differentiation opportunities
- Analyze competitor content strategies

## Purpose

Performs comprehensive competitor analysis during client onboarding to identify top 5-10 competitors, analyze their positioning, features, pricing, and content strategies. This skill builds on the company research to understand the competitive landscape and identify differentiation opportunities.

The output is a structured Competitor Research document that informs content strategy and messaging.

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | string | Yes | Unique client identifier |
| `company_name` | string | Yes | Client company name |
| `industry` | string | Yes | Industry vertical for competitor identification |
| `known_competitors` | array | No | Known competitor names/URLs to include |
| `competitor_count` | integer | No | Number of competitors to analyze (default: 5, max: 10) |
| `company_research_path` | string | No | Path to company research JSON (auto-detected if not provided) |
| `tenant_id` | string | No | Tenant identifier for cost tracking |
| `execution_mode` | string | No | "suggest" \| "preview" \| "execute" (default: "suggest") |

**Input schema:** `schemas/input.json`

---

## Data Requirements

| Requirement | Minimum | Recommended | On Insufficient |
|-------------|---------|-------------|-----------------|
| Competitors found | 3 | 5-10 | warn_and_continue |
| Competitor websites accessible | 2 | 5+ | warn_and_continue |
| Company research available | No | Yes | continue without context |

**Behavior:** If fewer than 3 competitors found, returns warning. Can run without prior company research but results are better with context.

---

## Outputs

| Name | Type | Description |
|------|------|-------------|
| `competitors` | array | List of analyzed competitors |
| `positioning_matrix` | object | Feature/positioning comparison matrix |
| `market_gaps` | array | Identified gaps and opportunities |
| `content_strategies` | array | Competitor content approaches |
| `research_doc` | string | Markdown-formatted research document |
| `_meta` | object | Execution metadata |

**Output schema:** `schemas/output.json`

---

## SLA (Service Level Agreement)

| Metric | Target | Maximum | Exceeded Action |
|--------|--------|---------|-----------------|
| Runtime | 90s | 300s | timeout_error |
| Retries | 2 | 3 | human_review |
| Cost | $1.50 | $5.00 | warn at 80%, abort at max |

## Failure Modes

| Mode | Trigger | Output | Escalation |
|------|---------|--------|------------|
| Partial Success | Some competitors inaccessible | Available competitors + warnings | No |
| No Competitors Found | Search returns no results | Error with suggestions | Yes |
| Scraping Blocked | Multiple sites blocked | Manual research required | Yes |
| Quality Failed | Eval score < 0.6 | Raw output + UNVALIDATED flag | Yes |

## Human Review Triggers

| Trigger | Mandatory | Review SLA | Escalation |
|---------|-----------|------------|------------|
| First run for client | Yes | 24h | None |
| Eval score < 0.7 | Yes | 8h | Auto-reject after 24h |
| < 3 competitors found | Yes | 8h | Manual competitor identification |
| Industry mismatch | Yes | 4h | Verify industry classification |

---

## Dependencies

- **Skills:** `research-company` (optional, for context)
- **MCPs:** `firecrawl` (website scraping), `serpapi` (search results)
- **APIs:** Firecrawl API, SerpAPI for competitor discovery
- **Scripts:** None

---

## Runtime Expectations

| Metric | Typical | Maximum |
|--------|---------|---------|
| Execution time | 90s | 300s |
| Retries on failure | 2 | 3 |

---

## Context Handling

| Input size | Strategy | Model |
|------------|----------|-------|
| < 8K tokens | Inline (direct prompt) | claude-sonnet-4 |
| 8K-50K tokens | Chunked processing | Haiku for chunks, Sonnet for synthesis |
| > 50K tokens | Context offloading | Use ContextManager |

### Expected input size

- **Typical:** 5-10 competitors × 10 pages each = ~50-100 pages, ~40-80K tokens
- **Maximum tested:** 10 competitors × 20 pages = 200 pages, ~150K tokens
- **Strategy for large inputs:** Per-competitor chunking with synthesis

---

## Process

1. **Load context** - Load company research if available
2. **Discover competitors** - Search for competitors via SerpAPI
3. **Validate list** - Merge known competitors, dedupe, verify URLs
4. **Scrape competitors** - Crawl each competitor's website (5 pages each)
5. **Extract profiles** - For each competitor:
   - Company overview
   - Products/services
   - Pricing (if public)
   - Target audience
   - Key differentiators
   - Content strategy
6. **Build comparison** - Create positioning matrix
7. **Identify gaps** - Find market opportunities
8. **Generate document** - Create Competitor Research doc
9. **Quality check** - Validate against output schema
10. **Save outputs** - Store in `clients/{client_id}/research/competitor-research.md`

---

## Constraints

- Maximum 10 competitors per run
- Output must be under 15,000 words
- All claims must include source URLs
- Must respect robots.txt
- Pricing data marked as "public" or "estimated"

---

## Quality Criteria

This skill's output passes if:
- [ ] Schema validation passes
- [ ] At least 3 competitors analyzed
- [ ] Each competitor has name, description, and positioning
- [ ] Positioning matrix generated
- [ ] At least 1 market gap identified
- [ ] All source URLs included

---

## Examples

See `/examples/` for annotated input/output pairs.

---

## Tests

See `/tests/` for golden outputs and validation prompts.

To run tests:
```bash
python -m pytest skills/research-competitors/tests/
```

---

## Production Readiness

**Status:** [ ] Not Ready | [x] Ready | [ ] Deprecated

---

## Changelog

### v1.0.0 (2026-01-27)
- Initial release
- Competitor discovery via SerpAPI
- Website scraping via Firecrawl
- Positioning matrix generation
- Market gap analysis

---

## Notes

- **Dependencies:** Best results when run after `research-company`
- **Rate limits:** SerpAPI and Firecrawl have rate limits; 10 competitors may take 3-5 minutes
- **Pricing data:** Often not publicly available; marked as "Not public" when not found
- **Output location:** Research doc saved to `clients/{client_id}/research/competitor-research.md`
