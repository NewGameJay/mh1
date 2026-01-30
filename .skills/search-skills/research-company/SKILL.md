---
name: research-company
version: 1.1.0
description: |
  Perform deep company research via website scraping and analysis for client onboarding.
  Use when asked to 'research company', 'analyze company website', 'build company profile from scratch'.

category: research
license: Proprietary
author: MH1
created: 2024-01-27
updated: 2024-01-28

compatibility:
  - firecrawl
  - serpapi

metadata:
  status: active
  estimated_runtime: "1-3min"
  client_facing: false
  tags:
    - research
    - company
    - onboarding

# Stage configuration
stages:
  - id: "00-setup"
    name: "Setup & Validation"
    description: "Validate inputs, check website accessibility, prepare environment"
    required: true
    file: stages/00-setup.md
  - id: "01-extract"
    name: "Data Extraction"
    description: "Scrape website content using Firecrawl MCP"
    checkpoint: true
    model: claude-haiku
    file: stages/01-extract.md
  - id: "02-transform"
    name: "Transform & Process"
    description: "Analyze content, extract structured company intelligence"
    checkpoint: true
    model: claude-sonnet-4
    file: stages/02-transform.md
  - id: "03-output"
    name: "Generate Output"
    description: "Create research document and structured output"
    model: claude-sonnet-4
    file: stages/03-output.md

# Input/output definitions
inputs:
  - name: client_id
    type: string
    required: true
    description: "Unique client identifier"
  - name: company_name
    type: string
    required: true
    description: "Official company name"
  - name: website_url
    type: string
    required: true
    format: uri
    description: "Primary company website URL"
  - name: additional_urls
    type: array
    required: false
    description: "Additional URLs to analyze (blog, docs, etc.)"
  - name: industry
    type: string
    required: false
    description: "Industry vertical (auto-detected if not provided)"
  - name: tenant_id
    type: string
    required: false
    description: "Tenant identifier for cost tracking (default: client_id)"
  - name: execution_mode
    type: string
    required: false
    enum: ["suggest", "preview", "execute"]
    default: "suggest"
    description: "Execution mode"
  - name: depth
    type: string
    required: false
    enum: ["quick", "standard", "deep"]
    default: "standard"
    description: "Research depth: quick (5 pages), standard (20 pages), deep (50+ pages)"

outputs:
  - name: company_profile
    type: object
    description: "Structured company information"
  - name: market_positioning
    type: object
    description: "How the company positions itself"
  - name: products_services
    type: array
    description: "Products and services offered"
  - name: brand_voice
    type: object
    description: "Detected brand voice attributes"
  - name: key_messages
    type: array
    description: "Core messaging themes"
  - name: research_doc
    type: markdown
    template: templates/report-template.md
    description: "Human-readable research document"
  - name: _meta
    type: object
    description: "Execution metadata"

# Dependencies
requires_skills: []
requires_context: []
requires_mcp:
  - firecrawl
optional_mcp:
  - serpapi

# Execution settings
timeout_minutes: 3
max_retries: 3
cost_estimate: "~$1.00 per run"
config_file: config/defaults.yaml

# Quality gates
quality_gates:
  - name: schema_validation
    type: schema
    schema: templates/output-schema.json
  - name: company_profile
    type: checklist
    items:
      - "Company name extracted"
      - "Company description present"
  - name: products_identified
    type: checklist
    items:
      - "At least 1 product/service identified"
  - name: voice_detected
    type: checklist
    items:
      - "Brand voice attributes detected"
  - name: sources_cited
    type: source_check
    required_sources: 3

allowed-tools: Read Write Shell CallMcpTool
---

# Skill: Research Company

## When to Use

Use this skill when you need to:
- Research a new client company during onboarding
- Build a comprehensive company profile from public sources
- Analyze a company's website for positioning and messaging
- Extract brand voice patterns from website content

## Purpose

Performs deep company research during client onboarding to build a comprehensive understanding of the company's business, market positioning, products/services, and brand voice. This skill scrapes and analyzes the company website, searches for public information, and synthesizes findings into a structured Company Research document.

This is the foundational research skill that feeds into competitor research, founder research, and interview preparation.

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | string | Yes | Unique client identifier |
| `company_name` | string | Yes | Official company name |
| `website_url` | string | Yes | Primary company website URL |
| `additional_urls` | array | No | Additional URLs to analyze (blog, docs, etc.) |
| `industry` | string | No | Industry vertical (auto-detected if not provided) |
| `tenant_id` | string | No | Tenant identifier for cost tracking (default: client_id) |
| `execution_mode` | string | No | "suggest" \| "preview" \| "execute" (default: "suggest") |
| `depth` | string | No | Research depth: "quick" (5 pages) \| "standard" (20 pages) \| "deep" (50+ pages) |

**Input schema:** `schemas/input.json`

---

## Data Requirements

| Requirement | Minimum | Recommended | On Insufficient |
|-------------|---------|-------------|-----------------|
| Website accessible | Yes | Yes | abort |
| Pages scraped | 3 | 20+ | warn_and_continue |
| Content extracted | 5KB | 50KB+ | warn_and_continue |

**Behavior:** If the primary website is inaccessible, returns error. If few pages are scraped, continues with warning and lower confidence score.

---

## Outputs

| Name | Type | Description |
|------|------|-------------|
| `company_profile` | object | Structured company information |
| `market_positioning` | object | How the company positions itself |
| `products_services` | array | Products and services offered |
| `brand_voice` | object | Detected brand voice attributes |
| `key_messages` | array | Core messaging themes |
| `research_doc` | string | Markdown-formatted research document |
| `_meta` | object | Execution metadata |

**Output schema:** `schemas/output.json`
**Report template:** `templates/report-template.md`

---

## SLA (Service Level Agreement)

| Metric | Target | Maximum | Exceeded Action |
|--------|--------|---------|-----------------|
| Runtime | 60s | 180s | timeout_error |
| Retries | 2 | 3 | human_review |
| Cost | $1.00 | $3.00 | warn at 80%, abort at max |

## Failure Modes

| Mode | Trigger | Output | Escalation |
|------|---------|--------|------------|
| Partial Success | Some URLs failed | Available data + warnings | No |
| Website Unavailable | Primary URL 404/timeout | Error with suggestions | Yes |
| Scraping Blocked | Cloudflare/CAPTCHA | Manual research required | Yes |
| Quality Failed | Eval score < 0.6 | Raw output + UNVALIDATED flag | Yes |
| Complete Failure | Unrecoverable | Error report only | Yes |

## Human Review Triggers

| Trigger | Mandatory | Review SLA | Escalation |
|---------|-----------|------------|------------|
| First run for client | Yes | 24h | None |
| Eval score < 0.7 | Yes | 8h | Auto-reject after 24h |
| Industry auto-detected | No | - | Flag for verification |
| Scraping blocked | Yes | 4h | Manual research required |

---

## Dependencies

- **Skills:** None
- **MCPs:** `firecrawl` (website scraping), optionally `serpapi` (search results)
- **APIs:** Firecrawl API for web scraping
- **Scripts:** None

---

## Runtime Expectations

| Metric | Typical | Maximum |
|--------|---------|---------|
| Execution time | 45s | 180s |
| Retries on failure | 2 | 3 |

---

## Context Handling

| Input size | Strategy | Model |
|------------|----------|-------|
| < 8K tokens | Inline (direct prompt) | claude-sonnet-4 |
| 8K-50K tokens | Chunked processing | Haiku for chunks, Sonnet for synthesis |
| > 50K tokens | Context offloading | Use ContextManager |

### Expected input size

- **Typical:** 20-50 pages scraped, ~20-40K tokens
- **Maximum tested:** 100 pages, ~150K tokens
- **Strategy for large inputs:** Chunked with page-level processing

---

## Process

This skill executes in 4 stages. See individual stage files for detailed instructions.

### Stage 0: Setup & Validation
See `stages/00-setup.md`

- Validate inputs (client_id, company_name, website_url)
- Check website accessibility
- Verify Firecrawl MCP connection
- Load depth configuration
- Initialize client directory

### Stage 1: Data Extraction
See `stages/01-extract.md`

- Scrape website using Firecrawl MCP
- Prioritize key pages (home, about, products, pricing)
- Extract structured content from HTML
- Process additional URLs if provided
- Create checkpoint for resumability

### Stage 2: Transform & Process
See `stages/02-transform.md`

- Build company profile (name, description, mission, vision)
- Analyze market positioning (target audience, ICP, value props)
- Extract products/services with features and pricing
- Detect brand voice (tone, personality, key terms)
- Extract key messages and themes
- Auto-detect industry if not provided
- Create checkpoint for resumability

### Stage 3: Generate Output
See `stages/03-output.md`

- Build structured JSON output
- Generate research document from template
- Validate against output schema
- Apply quality gates
- Save to client directory
- Determine release action

---

## Constraints

- Output must be under 10,000 words
- All claims must include source URLs
- Must respect robots.txt
- No scraping of login-required content
- Must not make assumptions about pricing if not publicly available

---

## Quality Criteria

This skill's output passes if:
- [ ] Schema validation passes
- [ ] Company name and description extracted
- [ ] At least 1 product/service identified
- [ ] Target audience identified
- [ ] Brand voice attributes detected
- [ ] All source URLs included

---

## Configuration

Default configuration is in `config/defaults.yaml`. Key settings:

| Setting | Default | Description |
|---------|---------|-------------|
| `default_depth` | standard | Research depth level |
| `min_confidence` | 0.6 | Minimum quality threshold |
| `cost_max` | 3.00 | Maximum cost per run |
| `cache_ttl_hours` | 24 | Cache validity period |

---

## Examples

See `references/` for annotated input/output pairs.

---

## Tests

See `/tests/` for golden outputs and validation prompts.

To run tests:
```bash
python -m pytest skills/research-company/tests/
```

---

## Production Readiness

**Status:** [ ] Not Ready | [x] Ready | [ ] Deprecated

Before marking as production-ready:
- [x] All tests pass
- [x] verify_setup.py runs without errors
- [x] Documentation complete (README.md, quick_reference.md)
- [ ] Used successfully in 3+ real runs
- [x] Error handling tested
- [x] Performance meets SLA

---

## Changelog

### v1.1.0 (2026-01-28)
- Migrated to new folder structure with stages
- Added config/defaults.yaml for configuration
- Added individual stage files (00-setup, 01-extract, 02-transform, 03-output)
- Added templates/output-schema.json and report-template.md
- Added references folder for examples
- Enhanced frontmatter with stage configuration
- Improved documentation structure

### v1.0.0 (2026-01-27)
- Initial release
- Website scraping via Firecrawl MCP
- Structured company profile extraction
- Brand voice detection
- Research document generation

---

## Related Skills

- [research-competitor](../research-competitor/SKILL.md) - Competitor analysis
- [research-founder](../research-founder/SKILL.md) - Founder research
- [client-onboarding](../client-onboarding/SKILL.md) - Full onboarding workflow

---

## Notes

- **First-time setup:** Ensure Firecrawl API key is configured in `.env`
- **Rate limits:** Firecrawl has rate limits; deep scans may take longer
- **JavaScript sites:** Firecrawl handles JavaScript rendering automatically
- **Output location:** Research doc saved to `clients/{client_id}/research/company-research.md`
