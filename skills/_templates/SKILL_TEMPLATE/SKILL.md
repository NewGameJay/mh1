---
name: skill-name
description: |
  Brief description of what this skill does and its value.
  Use when asked to 'trigger phrase 1', 'trigger phrase 2', 'trigger phrase 3'.
license: Proprietary
compatibility:
  - Firebase MCP
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  created: "2026-01-28"
  updated: "2026-01-28"
  estimated_runtime: "5-10min"
  max_runtime: "30min"
  estimated_cost: "$0.50"
  max_cost: "$2.00"
  client_facing: false
  requires_human_review: false
  tags:
    - category
    - subcategory
allowed-tools: Read Write Shell CallMcpTool
---

# [Skill Name]

## When to Use

Use this skill when:
- Scenario 1 description
- Scenario 2 description
- Scenario 3 description

Do NOT use when:
- Anti-scenario 1

---

## Inputs

| Name        | Type     | Required | Description                      |
|-------------|----------|----------|----------------------------------|
| `input_1`   | string   | yes      | Description of input_1           |
| `input_2`   | object   | no       | Description of input_2           |

**Input schema:** `schemas/input.json`

---

## Outputs

| Name        | Type     | Description                      |
|-------------|----------|----------------------------------|
| `output_1`  | string   | Description of output_1          |
| `output_2`  | array    | Description of output_2          |

**Output schema:** `schemas/output.json`

---

## Dependencies

| Type | Name | Purpose |
|------|------|---------|
| Skill | [skill-name] | [purpose] |
| MCP | [mcp-name] | [purpose] |
| API | [api-name] | [purpose] |
| Script | [script-path] | [purpose] |

---

## Data Requirements

| Requirement | Minimum | Recommended | On Insufficient |
|-------------|---------|-------------|-----------------|
| Record count | 50 | 500 | warn_and_continue |
| Field coverage | 80% | 95% | warn |

---

## SLA (Service Level Agreement)

| Metric | Target | Maximum | Exceeded Action |
|--------|--------|---------|-----------------|
| Runtime | 5min | 30min | timeout_error |
| Retries | 2 | 3 | human_review |
| Cost | $0.50 | $2.00 | abort |

---

## Context Handling

| Input Size | Strategy | Model |
|------------|----------|-------|
| < 8K tokens | Inline | As per model-routing.yaml |
| 8K-50K tokens | Chunked | Haiku for chunks, Sonnet for synthesis |
| > 50K tokens | ContextManager | Haiku for chunks, Sonnet for synthesis |

**Expected input size:** 50-200 records, ~2K tokens  
**Maximum tested:** 5,000 records, ~40K tokens

---

## Process

1. **Step 1: [Name]**
   - Description of what happens
   - Key considerations

2. **Step 2: [Name]**
   - Description of what happens
   - Key considerations

3. **Quality Check**
   - Validate against output schema
   - Run quality criteria checks

---

## Quality Criteria

This skill's output passes if:
- [ ] Schema validation passes
- [ ] All required fields present and non-empty
- [ ] [Custom criterion 1]
- [ ] [Custom criterion 2]

---

## Failure Modes

| Mode | Trigger | Output | Escalation |
|------|---------|--------|------------|
| Partial Success | 1+ steps failed | Last successful + error | If critical missing |
| Data Unavailable | Source timeout | Cached if <24h, else error | No |
| Quality Failed | Eval score < 0.6 | Raw + UNVALIDATED flag | Yes |
| Complete Failure | Unrecoverable | Error report only | Yes |

---

## Human Review Triggers

| Trigger | Mandatory | Review SLA | Escalation |
|---------|-----------|------------|------------|
| First run for client | Yes | 24h | None |
| Eval score < 0.7 | Yes | 8h | Auto-reject after 24h |

---

## Production Readiness

**Status:** [ ] Not Ready | [ ] Ready | [ ] Deprecated

Before marking as production-ready:
- [ ] All tests pass
- [ ] verify_setup.py runs without errors
- [ ] Documentation complete (README.md, quick_reference.md)
- [ ] Used successfully in 3+ real runs
- [ ] Error handling tested
- [ ] Performance meets SLA

See `PRODUCTION_READY_CHECKLIST.md` for detailed validation.

---

## Examples

See `examples/` for annotated input/output pairs.

---

## Tests

See `tests/` for golden outputs and validation prompts.

```bash
claude /test-skill [skill-name]
```

---

## Setup Verification

```bash
python skills/[skill-name]/verify_setup.py
```

---

## Quick Reference

See `quick_reference.md` for common usage patterns.

---

## Changelog

### v1.0.0 (2026-01-28)
- Initial release

---

## Notes

[Any additional context, gotchas, or tips.]
