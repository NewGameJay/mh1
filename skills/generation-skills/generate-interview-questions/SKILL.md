---
name: generate-interview-questions
description: |
  Generate targeted interview questions based on research gaps for client onboarding calls.
  Use when asked to 'generate interview questions', 'create onboarding questions', 'prepare client interview'.
license: Proprietary
compatibility: []
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  estimated_runtime: "30s-2min"
  client_facing: false
  tags:
    - generation
    - interview
    - onboarding
allowed-tools: Read Write Shell
---

# Skill: Generate Interview Questions

## When to Use

Use this skill when you need to:
- Prepare interview questions for a client onboarding call
- Identify research gaps that need validation
- Generate voice/style preference questions for founders
- Create a structured interview guide from prior research

## Purpose

Generates targeted interview questions for client onboarding calls based on research gaps identified during company, competitor, and founder research. This skill synthesizes all prior research to create a structured interview guide that validates assumptions, fills information gaps, and gathers voice/preference data.

The output is an Interview Questions document designed to be used during the client onboarding call.

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | string | Yes | Unique client identifier |
| `founder_names` | array | No | Names of founders to include (uses all if not specified) |
| `focus_areas` | array | No | Specific areas to focus questions on |
| `question_count` | integer | No | Target number of questions (default: 20, max: 50) |
| `include_voice_questions` | boolean | No | Include voice/style preference questions (default: true) |
| `tenant_id` | string | No | Tenant identifier for cost tracking |
| `execution_mode` | string | No | "suggest" \| "preview" \| "execute" (default: "suggest") |

**Input schema:** `schemas/input.json`

---

## Data Requirements

| Requirement | Minimum | Recommended | On Insufficient |
|-------------|---------|-------------|-----------------|
| Company research exists | No | Yes | generate generic questions |
| Founder research exists | No | Yes | skip founder-specific questions |
| Competitor research exists | No | Yes | skip competitive questions |

**Behavior:** The skill can run with no prior research (generates generic onboarding questions) but produces much better results with research context.

---

## Outputs

| Name | Type | Description |
|------|------|-------------|
| `questions` | array | Structured list of interview questions |
| `research_gaps` | array | Identified gaps from prior research |
| `assumptions_to_validate` | array | Assumptions needing confirmation |
| `interview_guide` | string | Markdown interview guide document |
| `_meta` | object | Execution metadata |

**Output schema:** `schemas/output.json`

---

## SLA (Service Level Agreement)

| Metric | Target | Maximum | Exceeded Action |
|--------|--------|---------|-----------------|
| Runtime | 30s | 90s | timeout_error |
| Retries | 2 | 3 | human_review |
| Cost | $0.30 | $1.00 | warn at 80%, abort at max |

## Failure Modes

| Mode | Trigger | Output | Escalation |
|------|---------|--------|------------|
| No Research Found | No prior research docs | Generic questions + warning | No |
| Partial Research | Some research missing | Available context + gap questions | No |
| Quality Failed | Eval score < 0.6 | Raw output + UNVALIDATED flag | Yes |

## Human Review Triggers

| Trigger | Mandatory | Review SLA | Escalation |
|---------|-----------|------------|------------|
| First run for client | Yes | 24h | None |
| Eval score < 0.7 | Yes | 8h | Auto-reject after 24h |
| No research context | No | - | Flag for review |

---

## Dependencies

- **Skills:** `research-company`, `research-competitors`, `research-founder` (all optional but recommended)
- **MCPs:** None
- **APIs:** None
- **Scripts:** None

---

## Runtime Expectations

| Metric | Typical | Maximum |
|--------|---------|---------|
| Execution time | 20s | 90s |
| Retries on failure | 2 | 3 |

---

## Context Handling

| Input size | Strategy | Model |
|------------|----------|-------|
| < 8K tokens | Inline (direct prompt) | claude-sonnet-4 |
| 8K-50K tokens | Chunked processing | Haiku for chunks, Sonnet for synthesis |
| > 50K tokens | Context offloading | Use ContextManager |

### Expected input size

- **Typical:** 3-5 research docs, ~15-30K tokens
- **Maximum tested:** 10 research docs, ~100K tokens
- **Strategy for large inputs:** Summarize each research doc first

---

## Process

1. **Load research** - Load all available research docs for client
2. **Identify gaps** - Extract information gaps from each doc
3. **Identify assumptions** - Find assumptions that need validation
4. **Generate categories** - Organize questions by category:
   - Company & Strategy
   - Target Audience & ICP
   - Content & Voice Preferences
   - Competitive Positioning
   - Goals & Metrics
   - Founder-Specific
5. **Generate questions** - Create targeted questions for each gap
6. **Prioritize** - Order questions by importance
7. **Generate guide** - Create interview guide document
8. **Quality check** - Validate question quality and coverage
9. **Save outputs** - Store in `clients/{client_id}/research/interview-questions.md`

---

## Constraints

- Maximum 50 questions per run
- Questions must be open-ended (not yes/no)
- Must cover all research gaps identified
- Must include voice/style questions if enabled
- Questions must be specific enough to be actionable

---

## Quality Criteria

This skill's output passes if:
- [ ] Schema validation passes
- [ ] At least 10 questions generated
- [ ] All major categories covered
- [ ] Questions are open-ended
- [ ] Research gaps addressed
- [ ] Questions are specific and actionable

---

## Examples

See `/examples/` for annotated input/output pairs.

---

## Tests

See `/tests/` for golden outputs and validation prompts.

To run tests:
```bash
python -m pytest skills/generate-interview-questions/tests/
```

---

## Production Readiness

**Status:** [ ] Not Ready | [x] Ready | [ ] Deprecated

---

## Changelog

### v1.0.0 (2026-01-27)
- Initial release
- Research gap analysis
- Assumption validation
- Categorized question generation
- Interview guide document generation

---

## Notes

- **Best with research:** Run after company, competitor, and founder research for best results
- **Can run standalone:** Will generate generic onboarding questions without prior research
- **Voice questions:** Enabled by default; critical for ghostwriting preparation
- **Output location:** Interview guide saved to `clients/{client_id}/research/interview-questions.md`
- **Interview flow:** Questions are ordered for natural conversation flow
