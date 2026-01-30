---
name: research-founder
description: |
  Perform deep founder research from LinkedIn, social media, and public content.
  Use when asked to 'research founder', 'analyze founder background', 'find founder content'.
license: Proprietary
compatibility:
  - firecrawl
  - linkedin-scraper
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  estimated_runtime: "1-3min"
  client_facing: false
  tags:
    - research
    - founder
    - voice-analysis
allowed-tools: Read Write Shell CallMcpTool
---

# Skill: Research Founder

## When to Use

Use this skill when you need to:
- Research a founder or executive during client onboarding
- Analyze a founder's public content and voice patterns
- Build a founder profile for ghostwriting preparation
- Generate interview preparation questions for a founder

## Purpose

Performs deep research on individual founders/executives during client onboarding to understand their background, expertise, content style, and voice patterns. This skill analyzes LinkedIn profiles, public content, interviews, and social media to build a comprehensive Founder Research document.

This is a per-founder skill - run once for each founder/executive who will be creating or approving content. The output feeds directly into voice extraction and ghostwriting skills.

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | string | Yes | Unique client identifier |
| `founder_name` | string | Yes | Founder's full name |
| `founder_title` | string | No | Founder's role/title |
| `linkedin_url` | string | No | LinkedIn profile URL |
| `twitter_handle` | string | No | Twitter/X handle |
| `other_profiles` | array | No | Other social/content profile URLs |
| `company_name` | string | No | Company name for context |
| `tenant_id` | string | No | Tenant identifier for cost tracking |
| `execution_mode` | string | No | "suggest" \| "preview" \| "execute" (default: "suggest") |

**Input schema:** `schemas/input.json`

---

## Data Requirements

| Requirement | Minimum | Recommended | On Insufficient |
|-------------|---------|-------------|-----------------|
| LinkedIn profile found | Yes | Yes | warn_and_continue |
| Public content pieces | 5 | 20+ | warn_and_continue |
| Content for voice analysis | 1000 words | 5000+ words | warn (low confidence) |

**Behavior:** The skill can run with minimal data but will flag low confidence. LinkedIn is the primary source; other platforms add depth.

---

## Outputs

| Name | Type | Description |
|------|------|-------------|
| `founder_profile` | object | Background, experience, expertise |
| `content_analysis` | object | Analysis of public content |
| `voice_patterns` | object | Detected voice and style patterns |
| `topics_of_expertise` | array | Areas of demonstrated expertise |
| `interview_prep` | object | Suggested interview focus areas |
| `research_doc` | string | Markdown-formatted research document |
| `_meta` | object | Execution metadata |

**Output schema:** `schemas/output.json`

---

## SLA (Service Level Agreement)

| Metric | Target | Maximum | Exceeded Action |
|--------|--------|---------|-----------------|
| Runtime | 60s | 180s | timeout_error |
| Retries | 2 | 3 | human_review |
| Cost | $0.75 | $2.00 | warn at 80%, abort at max |

## Failure Modes

| Mode | Trigger | Output | Escalation |
|------|---------|--------|------------|
| Partial Success | Some profiles inaccessible | Available data + warnings | No |
| No Profile Found | LinkedIn not found | Error with search suggestions | Yes |
| Insufficient Content | < 5 content pieces | Low confidence warning | No |
| Quality Failed | Eval score < 0.6 | Raw output + UNVALIDATED flag | Yes |

## Human Review Triggers

| Trigger | Mandatory | Review SLA | Escalation |
|---------|-----------|------------|------------|
| First run for founder | Yes | 24h | None |
| Eval score < 0.7 | Yes | 8h | Auto-reject after 24h |
| No LinkedIn found | Yes | 4h | Manual profile identification |
| Multiple profiles with same name | Yes | 4h | Disambiguation required |

---

## Dependencies

- **Skills:** `research-company` (optional, for context)
- **MCPs:** `linkedin-scraper` (profile data), `firecrawl` (content scraping)
- **APIs:** LinkedIn API (if available), Firecrawl API
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

- **Typical:** 10-30 content pieces, ~10-25K tokens
- **Maximum tested:** 100 content pieces, ~100K tokens
- **Strategy for large inputs:** Chunked by content source

---

## Process

1. **Validate inputs** - Ensure founder name provided
2. **Find LinkedIn** - Search for LinkedIn profile if URL not provided
3. **Scrape profiles** - Extract data from LinkedIn and other profiles
4. **Collect content** - Gather public posts, articles, interviews
5. **Analyze background** - Extract career history, education, expertise
6. **Analyze voice** - Detect writing style, tone, vocabulary patterns
7. **Identify topics** - Categorize areas of expertise and interest
8. **Generate interview prep** - Suggest areas to explore in interview
9. **Generate document** - Create Founder Research doc
10. **Quality check** - Validate against output schema
11. **Save outputs** - Store in `clients/{client_id}/research/founder-{name}.md`

---

## Constraints

- One founder per run (run multiple times for multiple founders)
- Output must be under 8,000 words
- Must respect LinkedIn terms of service
- No access to private/connection-only content
- Must verify correct person (disambiguation)

---

## Quality Criteria

This skill's output passes if:
- [ ] Schema validation passes
- [ ] Founder name and title extracted
- [ ] Career history identified
- [ ] At least 3 content pieces analyzed
- [ ] Voice patterns detected (even if low confidence)
- [ ] Topics of expertise identified

---

## Examples

See `/examples/` for annotated input/output pairs.

---

## Tests

See `/tests/` for golden outputs and validation prompts.

To run tests:
```bash
python -m pytest skills/research-founder/tests/
```

---

## Production Readiness

**Status:** [ ] Not Ready | [x] Ready | [ ] Deprecated

---

## Changelog

### v1.0.0 (2026-01-27)
- Initial release
- LinkedIn profile extraction
- Public content analysis
- Voice pattern detection
- Interview prep suggestions

---

## Notes

- **Per-founder skill:** Run once per founder; creates separate research docs
- **LinkedIn dependency:** LinkedIn is primary source; skill works without it but with lower quality
- **Voice patterns:** Initial detection; refined by `extract-founder-voice` skill with more content
- **Output location:** Research doc saved to `clients/{client_id}/research/founder-{slug}.md`
- **Multiple founders:** Run skill multiple times, once per founder
