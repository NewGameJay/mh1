---
name: incorporate-interview-results
description: |
  Process interview transcripts to update and enhance research documents.
  Use when asked to 'add interview notes', 'incorporate interview results',
  'update research from interview', 'process interview transcript', or 'merge interview insights'.
license: Proprietary
compatibility: []
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  estimated_runtime: "30-120s"
  client_facing: true
  tags:
    - interview
    - research
    - onboarding
    - voice
    - transcripts
allowed-tools: Read Write Shell
---

# Skill: Incorporate Interview Results

## When to Use

- Process interview transcripts from client onboarding calls
- Update research documents with interview insights
- Validate or correct research assumptions based on interview
- Extract founder voice data from interview content
- Merge interview findings into existing research

---

## Purpose

Processes interview transcripts and notes from client onboarding calls to update and enhance research documents with new information. This skill extracts key insights, validates/corrects assumptions, fills research gaps, and enriches founder voice data.

The skill is the final step in the onboarding research process, producing validated and complete research documents ready for content production.

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | string | Yes | Unique client identifier |
| `interview_transcript` | string | No | Full interview transcript text |
| `interview_notes` | string | No | Interview notes (if no transcript) |
| `interview_file` | string | No | Path to transcript/notes file |
| `interviewee_name` | string | No | Name of person interviewed |
| `validate_only` | boolean | No | Only validate, don't update docs (default: false) |
| `tenant_id` | string | No | Tenant identifier for cost tracking |
| `execution_mode` | string | No | "suggest" \| "preview" \| "execute" (default: "suggest") |

**Input schema:** `schemas/input.json`

---

## Data Requirements

| Requirement | Minimum | Recommended | On Insufficient |
|-------------|---------|-------------|-----------------|
| Interview content | 500 words | 2000+ words | warn_and_continue |
| Prior research docs | Yes | Yes | error (nothing to update) |
| Interview questions doc | No | Yes | skip gap matching |

**Behavior:** Requires at least interview content (transcript or notes) and existing research documents to update.

---

## Outputs

| Name | Type | Description |
|------|------|-------------|
| `extracted_insights` | array | Key insights from interview |
| `assumptions_validated` | array | Assumptions confirmed/corrected |
| `gaps_filled` | array | Research gaps addressed |
| `docs_updated` | array | List of documents updated |
| `voice_updates` | object | New voice data extracted |
| `update_summary` | string | Markdown summary of updates |
| `_meta` | object | Execution metadata |

**Output schema:** `schemas/output.json`

---

## SLA (Service Level Agreement)

| Metric | Target | Maximum | Exceeded Action |
|--------|--------|---------|-----------------|
| Runtime | 45s | 120s | timeout_error |
| Retries | 2 | 3 | human_review |
| Cost | $0.75 | $2.50 | warn at 80%, abort at max |

## Failure Modes

| Mode | Trigger | Output | Escalation |
|------|---------|--------|------------|
| No Research Found | No prior research docs | Error - run research first | No |
| Insufficient Interview | < 500 words | Warning, partial extraction | No |
| Conflict Detected | Interview contradicts research | Flag for review | Yes |
| Quality Failed | Eval score < 0.6 | Raw output + UNVALIDATED flag | Yes |

## Human Review Triggers

| Trigger | Mandatory | Review SLA | Escalation |
|---------|-----------|------------|------------|
| First run for client | Yes | 24h | None |
| Eval score < 0.7 | Yes | 8h | Auto-reject after 24h |
| Conflicts detected | Yes | 4h | Manual resolution required |
| Major assumption invalidated | Yes | 8h | Research may need rerun |

---

## Dependencies

- **Skills:** `research-company`, `research-founder`, `generate-interview-questions` (all should be run first)
- **MCPs:** None
- **APIs:** None
- **Scripts:** None

---

## Runtime Expectations

| Metric | Typical | Maximum |
|--------|---------|---------|
| Execution time | 30s | 120s |
| Retries on failure | 2 | 3 |

---

## Context Handling

| Input size | Strategy | Model |
|------------|----------|-------|
| < 8K tokens | Inline (direct prompt) | claude-sonnet-4 |
| 8K-50K tokens | Chunked processing | Haiku for chunks, Sonnet for synthesis |
| > 50K tokens | Context offloading | Use ContextManager |

### Expected input size

- **Typical:** 1-hour interview ~8K-15K tokens + research docs ~20K tokens
- **Maximum tested:** 2-hour interview ~30K tokens + research ~50K tokens
- **Strategy for large inputs:** Chunk transcript by topic/speaker turns

---

## Process

1. **Load context** - Load all prior research docs and interview questions
2. **Parse interview** - Extract structured content from transcript/notes
3. **Extract insights** - Identify key information mentioned
4. **Match to gaps** - Map insights to known research gaps
5. **Validate assumptions** - Check assumptions against interview content
6. **Extract voice data** - Pull phrases, tone, style from founder speech
7. **Detect conflicts** - Flag contradictions with existing research
8. **Update documents** - Merge new information into research docs
9. **Generate summary** - Create update summary document
10. **Quality check** - Validate updates against schema
11. **Save outputs** - Store updated docs and summary

---

## Constraints

- Cannot delete existing research, only augment
- Must flag conflicts rather than overwrite silently
- Voice updates are additive (increase confidence, don't replace)
- Must preserve source attribution (interview vs. research)

---

## Quality Criteria

This skill's output passes if:
- [ ] Schema validation passes
- [ ] At least 3 insights extracted
- [ ] No unresolved conflicts
- [ ] Updated docs maintain valid schema
- [ ] Update summary generated
- [ ] Source attribution preserved

---

## Examples

See `/examples/` for annotated input/output pairs.

---

## Tests

See `/tests/` for golden outputs and validation prompts.

To run tests:
```bash
python -m pytest skills/incorporate-interview-results/tests/
```

---

## Production Readiness

**Status:** [ ] Not Ready | [x] Ready | [ ] Deprecated

---

## Changelog

### v1.0.0 (2026-01-27)
- Initial release
- Interview transcript processing
- Research document updates
- Assumption validation
- Voice data extraction
- Conflict detection

---

## Notes

- **Run after interview:** This skill processes the results of the onboarding interview
- **Preserves history:** Updates are tracked, original research preserved
- **Voice refinement:** Voice data from interview is highly valuable for ghostwriting
- **Conflict handling:** Conflicts flag for human review, not auto-resolved
- **Output location:** Updates saved to existing research docs + summary in `clients/{client_id}/research/interview-results.md`
