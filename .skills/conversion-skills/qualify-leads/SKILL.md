---
name: qualify-leads
description: |
  Qualify LinkedIn post reactors and commenters against ICP definitions.
  Use when asked to 'qualify leads', 'find qualified leads', 'ICP lead qualification',
  'identify leads from posts', or 'generate outreach messages'.
license: Proprietary
compatibility: [Firebase]
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: experimental
  estimated_runtime: "60-300s"
  client_facing: true
  tags:
    - leads
    - qualification
    - icp
    - outreach
    - linkedin
allowed-tools: Read Write Shell CallMcpTool
---

# Skill: Qualify Leads

## When to Use

- Qualify LinkedIn post reactors against ICP criteria
- Filter and score leads from recent post engagement
- Generate personalized outreach messages for qualified leads
- Identify high-value leads from LinkedIn engagement
- Build lead lists from post commenters and reactors

---

## Purpose

Pull LinkedIn post reactors and commenters from the past week, qualify them against ICP definitions, filter out unqualified leads, and output a list of qualified leads with enriched profiles, origin post information, ICP classification, qualification reason, and a personalized draft outreach message.

---

## Inputs

| Name              | Type     | Required | Description                                          |
|-------------------|----------|----------|------------------------------------------------------|
| `client_id`       | string   | yes*     | Firebase Client ID (or from active_client.md)        |
| `founder_id`      | string   | yes      | Founder/profile ID for posts                         |
| `lookback_days`   | integer  | no       | Days to pull reactors from (default: 7)              |
| `icp_definitions` | array    | no       | Override ICP definitions from client context         |
| `min_posts`       | integer  | no       | Minimum posts to analyze (default: 1)                |
| `include_commenters` | boolean | no     | Include post commenters (default: true)              |
| `include_reactors`   | boolean | no     | Include post reactors (default: true)                |
| `generate_messages`  | boolean | no     | Generate draft outreach messages (default: true)     |

**Input schema:** `schemas/input.json`

---

## Data Requirements

| Requirement       | Minimum | Recommended | On Insufficient |
|-------------------|---------|-------------|-----------------|
| Posts analyzed    | 1       | 10          | warn_and_continue |
| Reactors fetched  | 5       | 50          | warn_and_continue |
| ICP matches       | 1       | 10          | warn_and_continue |

**Behavior:** Returns partial results with warnings if data requirements aren't met.

---

## Outputs

| Name              | Type     | Description                                          |
|-------------------|----------|------------------------------------------------------|
| `qualified_leads` | array    | List of qualified leads with enriched data           |
| `summary`         | object   | Summary statistics                                   |
| `disqualified`    | object   | Breakdown of disqualified leads                      |
| `recommendations` | array    | Follow-up action recommendations                     |

### Qualified Lead Structure

Each lead in `qualified_leads` contains:

| Field             | Type     | Description                                          |
|-------------------|----------|------------------------------------------------------|
| `name`            | string   | Full name                                            |
| `company`         | string   | Company name                                         |
| `role`            | string   | Job title/role                                       |
| `origin_post_url` | string   | URL of the LinkedIn post they engaged with           |
| `icp_type`        | string   | ICP segment matched (e.g., "Primary", "Secondary")   |
| `reason`          | string   | Why they qualified (specific criteria matched)       |
| `draft_msg`       | string   | Personalized draft outreach message                  |
| `engagement_type` | string   | How they engaged: "reaction", "comment", "both"      |
| `linkedin_url`    | string   | LinkedIn profile URL (if available)                  |
| `confidence`      | number   | Confidence score for ICP match (0-1)                 |

**Output schema:** `schemas/output.json`

---

## SLA (Service Level Agreement)

| Metric  | Target   | Maximum   | Exceeded Action   |
|---------|----------|-----------|-------------------|
| Runtime | 90s      | 300s      | abort_partial     |
| Retries | 2        | 3         | human_review      |
| Cost    | $0.15    | $0.75     | warn              |

## Failure Modes

| Mode              | Trigger                    | Output                        | Escalation |
|-------------------|----------------------------|-------------------------------|------------|
| Partial Success   | Some posts missing data    | Available leads + warnings    | No         |
| Data Unavailable  | Firebase timeout           | Cached if <24h, else error    | No         |
| Quality Failed    | Eval score < 0.6           | Raw output + UNVALIDATED flag | Yes        |
| Complete Failure  | No reactors found          | Error report only             | Yes        |

## Human Review Triggers

| Trigger                    | Mandatory | Review SLA | Escalation           |
|----------------------------|-----------|------------|----------------------|
| First run for client       | Yes       | 24h        | None                 |
| Eval score < 0.7           | Yes       | 8h         | Auto-reject after 24h|
| High-value leads detected  | No        | 4h         | Notify immediately   |

---

## Dependencies

- **Skills:** None
- **MCPs:** Firebase (for post and reactor data)
- **APIs:** None (uses stored reactor data)
- **Scripts:** None
- **Lib:** `lib/client.py`, `lib/firebase_client.py`, `lib/evaluator.py`, `lib/telemetry.py`

---

## Runtime Expectations

| Metric            | Typical | Maximum |
|-------------------|---------|---------|
| Execution time    | 60s     | 300s    |
| Retries on failure| 2       | 3       |

---

## Context handling

| Input size       | Strategy                | Model                              |
|------------------|-------------------------|-----------------------------------|
| < 8K tokens      | Inline (direct prompt)  | claude-haiku                      |
| 8K-50K tokens    | Chunked processing      | Haiku for chunks, Sonnet for synthesis |
| > 50K tokens     | Context offloading      | Use ContextManager                |

### Expected input size

- **Typical:** 50-200 reactors, ~3K tokens
- **Maximum tested:** 1000 reactors, ~30K tokens
- **Strategy for large inputs:** chunked

### Large input handling (if applicable)

```python
from lib.runner import ContextManager, ContextConfig, get_model_for_subtask

def run_skill(inputs):
    reactors = inputs.get("reactors", [])
    ctx = ContextManager(reactors, ContextConfig(max_inline_tokens=8000))
    
    if ctx.should_offload():
        for chunk in ctx.chunk(size=100):  # 100 reactors per chunk
            model_config = get_model_for_subtask("chunk_processing")
            result = qualify_reactor_chunk(chunk, model=model_config["model"])
            ctx.aggregate_buffer("qualified", result)
        
        model_config = get_model_for_subtask("synthesis")
        final = compile_leads(ctx.get_aggregated("qualified"), model=model_config["model"])
    else:
        final = qualify_directly(reactors)
    
    return {"output": final, "context_telemetry": ctx.get_telemetry()}
```

---

## Process

1. **Resolve client**: Load client_id from active_client.md or parameter
2. **Load ICP definitions**: From client context or parameter override
3. **Fetch posts**: Pull posts from past `lookback_days` from Firebase
4. **Fetch reactors**: For each post, get reactors from Firebase
5. **Fetch commenters**: If enabled, get commenters from Firebase
6. **Qualify leads**: For each reactor/commenter:
   - Match against ICP criteria
   - Calculate confidence score
   - Record reason for qualification
   - Note origin post
7. **Filter unqualified**: Remove non-matching leads
8. **Deduplicate**: Merge duplicate appearances (same person, multiple posts)
9. **Generate messages**: If enabled, create personalized outreach drafts
10. **Compile output**: Build qualified_leads array with all fields
11. **Quality check**: Validate against output schema

---

## Constraints

- No live LinkedIn API calls (uses stored reactor data)
- Messages must reference the specific post they engaged with
- One lead entry per person (deduplicated across posts)
- Maximum 100 qualified leads per run (paginate for more)

---

## Quality criteria

This skill's output passes if:
- [ ] Schema validation passes
- [ ] All qualified leads have required fields
- [ ] Messages are personalized (not generic templates)
- [ ] ICP type matches defined segments
- [ ] Reason field explains specific qualification criteria

---

## Examples

See `/examples/` for annotated input/output pairs.

### Example Qualified Lead

```json
{
  "name": "Sarah Chen",
  "company": "TechCorp Solutions",
  "role": "VP of Marketing",
  "origin_post_url": "https://linkedin.com/posts/founder-123",
  "icp_type": "Primary",
  "reason": "VP-level marketing leader at B2B SaaS company (50-500 employees)",
  "draft_msg": "Hi Sarah, I noticed you engaged with my post about marketing automation challenges. As VP of Marketing at TechCorp, I imagine you're dealing with similar scaling issues. Would love to share how we've helped similar teams — open to a quick chat?",
  "engagement_type": "reaction",
  "linkedin_url": "https://linkedin.com/in/sarah-chen",
  "confidence": 0.92
}
```

---

## Tests

See `/tests/` for golden outputs and validation prompts.

To run tests:
```bash
claude /test-skill qualify-leads
```

---

## Production Readiness

**Status:** [ ] Not Ready | [x] Ready | [ ] Deprecated

Before marking as production-ready:
- [ ] All tests pass
- [ ] verify_setup.py runs without errors
- [ ] Documentation complete (README.md, quick_reference.md)
- [ ] Used successfully in 3+ real runs
- [ ] Error handling tested
- [ ] Performance meets SLA

---

## Setup Verification

Run `verify_setup.py` to validate environment:
```bash
python skills/qualify-leads/verify_setup.py
```

This checks:
- Firebase credentials configured
- Client context accessible
- ICP definitions present
- Reactor data available

---

## Message Generation

Outreach messages are generated using the following template structure:

1. **Hook**: Reference specific post they engaged with
2. **Connection**: Acknowledge their role/company
3. **Value prop**: Brief mention of relevant solution
4. **CTA**: Soft ask for conversation

Example template:
```
Hi {name}, I noticed you {engagement_verb} my post about {post_topic}. 
As {role} at {company}, I imagine {relevant_challenge}. 
{value_proposition} — open to a quick chat?
```

---

## Changelog

### v1.0.0 (2026-01-27)
- Initial release
- Reactor and commenter qualification
- ICP matching with confidence scores
- Draft message generation
- Deduplication across posts

---

## Notes

- ICP definitions should be maintained in client context
- Reactor data must be collected by social-listening-collect skill first
- Messages should be reviewed before sending (not fully automated)
- High-confidence leads (>0.9) are prioritized in output
