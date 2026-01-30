---
name: icp-historical-analysis
description: |
  Analyze historical LinkedIn post engagement to measure ICP engagement rates.
  Use when asked to 'analyze ICP engagement', 'measure ICP performance', 
  'run ICP analysis', 'check ICP engagement rates', or 'weekly ICP report'.
license: Proprietary
compatibility: [Firebase]
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: experimental
  estimated_runtime: "45-180s"
  client_facing: true
  tags:
    - icp
    - analytics
    - engagement
    - linkedin
    - weekly-trigger
allowed-tools: Read Write Shell CallMcpTool
---

# Skill: ICP Historical Analysis

## When to Use

- Analyze ICP (Ideal Customer Profile) engagement on LinkedIn posts
- Measure week-over-week ICP engagement trends
- Identify content themes with highest ICP engagement
- Run weekly engagement analysis reports
- Compare ICP engagement rates across different time periods

---

## Purpose

Analyze historical LinkedIn post engagement to measure ICP (Ideal Customer Profile) engagement rates and identify themes with the highest ICP engagement. This skill runs on a weekly trigger to analyze the past 14 days of posts, comparing average ICP engagement between the two weeks, tracking average reactors per post, and surfacing content themes that resonate most with target audiences.

---

## Inputs

| Name              | Type     | Required | Description                                          |
|-------------------|----------|----------|------------------------------------------------------|
| `client_id`       | string   | yes*     | Firebase Client ID (or from active_client.md)        |
| `founder_id`      | string   | yes      | Founder/profile ID for posts                         |
| `lookback_days`   | integer  | no       | Days to analyze (default: 14)                        |
| `icp_definitions` | array    | no       | Override ICP definitions from client context         |
| `min_engagement`  | integer  | no       | Minimum engagement threshold to include post         |

**Input schema:** `schemas/input.json`

---

## Data Requirements

| Requirement       | Minimum | Recommended | On Insufficient |
|-------------------|---------|-------------|-----------------|
| Posts analyzed    | 4       | 20          | warn_and_continue |
| Reactors per post | 1       | 10          | warn_and_continue |
| ICP matches       | 0       | 5           | warn_and_continue |

**Behavior:** Returns partial analysis with warnings if data requirements aren't met. No abort.

---

## Outputs

| Name                      | Type     | Description                                        |
|---------------------------|----------|----------------------------------------------------|
| `summary`                 | object   | High-level metrics summary                         |
| `week1_analysis`          | object   | Metrics for days 1-7 (most recent)                 |
| `week2_analysis`          | object   | Metrics for days 8-14                              |
| `comparison`              | object   | Week-over-week comparison                          |
| `theme_analysis`          | array    | Themes ranked by ICP engagement                    |
| `top_performing_posts`    | array    | Posts with highest ICP engagement                  |
| `historical_baseline`     | object   | All-time averages for comparison                   |
| `recommendations`         | array    | Content strategy recommendations                   |

**Output schema:** `schemas/output.json`

---

## SLA (Service Level Agreement)

| Metric  | Target   | Maximum   | Exceeded Action   |
|---------|----------|-----------|-------------------|
| Runtime | 60s      | 180s      | abort_partial     |
| Retries | 2        | 3         | human_review      |
| Cost    | $0.10    | $0.50     | warn              |

## Failure Modes

| Mode              | Trigger                    | Output                        | Escalation |
|-------------------|----------------------------|-------------------------------|------------|
| Partial Success   | Some posts missing data    | Available data + warnings     | No         |
| Data Unavailable  | Firebase timeout           | Cached if <24h, else error    | No         |
| Quality Failed    | Eval score < 0.6           | Raw output + UNVALIDATED flag | Yes        |
| Complete Failure  | No posts found             | Error report only             | Yes        |

## Human Review Triggers

| Trigger                    | Mandatory | Review SLA | Escalation           |
|----------------------------|-----------|------------|----------------------|
| First run for client       | Yes       | 24h        | None                 |
| Eval score < 0.7           | Yes       | 8h         | Auto-reject after 24h|
| ICP match rate < 5%        | No        | 48h        | Suggest ICP refinement|

---

## Dependencies

- **Skills:** None
- **MCPs:** Firebase (for post and reactor data)
- **APIs:** LinkedIn (reactor profile enrichment via stored data)
- **Scripts:** None
- **Lib:** `lib/client.py`, `lib/firebase_client.py`, `lib/evaluator.py`, `lib/telemetry.py`

---

## Runtime Expectations

| Metric            | Typical | Maximum |
|-------------------|---------|---------|
| Execution time    | 45s     | 180s    |
| Retries on failure| 2       | 3       |

---

## Context handling

| Input size       | Strategy                | Model                              |
|------------------|-------------------------|-----------------------------------|
| < 8K tokens      | Inline (direct prompt)  | claude-haiku                      |
| 8K-50K tokens    | Chunked processing      | Haiku for chunks, Sonnet for synthesis |
| > 50K tokens     | Context offloading      | Use ContextManager                |

### Expected input size

- **Typical:** 20-100 posts with reactors, ~5K tokens
- **Maximum tested:** 500 posts with full reactor lists, ~40K tokens
- **Strategy for large inputs:** chunked

### Large input handling (if applicable)

```python
from lib.runner import ContextManager, ContextConfig, get_model_for_subtask

def run_skill(inputs):
    posts = inputs.get("posts", [])
    ctx = ContextManager(posts, ContextConfig(max_inline_tokens=8000))
    
    if ctx.should_offload():
        for chunk in ctx.chunk(size=50):  # 50 posts per chunk
            model_config = get_model_for_subtask("chunk_processing")
            result = analyze_engagement_chunk(chunk, model=model_config["model"])
            ctx.aggregate_buffer("results", result)
        
        model_config = get_model_for_subtask("synthesis")
        final = synthesize_analysis(ctx.get_aggregated("results"), model=model_config["model"])
    else:
        final = analyze_directly(posts)
    
    return {"output": final, "context_telemetry": ctx.get_telemetry()}
```

---

## Process

1. **Resolve client**: Load client_id from active_client.md or parameter
2. **Fetch posts**: Pull posts from past `lookback_days` from Firebase (`clients/{clientId}/posts`)
3. **Fetch reactors**: For each post, get reactors from Firebase (`clients/{clientId}/posts/{postId}/reactors`)
4. **Load ICP definitions**: From client context or parameter override
5. **Match reactors to ICP**: Classify each reactor against ICP criteria
6. **Calculate week 1 metrics**: Posts from days 1-7
   - Total posts
   - Total reactors
   - Average reactors per post
   - ICP matches
   - ICP engagement rate (ICP reactors / total reactors)
7. **Calculate week 2 metrics**: Posts from days 8-14 (same metrics)
8. **Calculate comparison**: Week-over-week changes
9. **Analyze themes**: Group posts by topic/theme, calculate ICP engagement per theme
10. **Calculate historical baseline**: All-time averages from past posts
11. **Generate recommendations**: Based on theme performance
12. **Quality check**: Validate against output schema

---

## Constraints

- Output must include both weekly breakdowns
- ICP matching uses stored reactor profile data (no live LinkedIn API calls)
- Themes derived from post topics/tags or content analysis
- Historical baseline limited to past 90 days for performance

---

## Quality criteria

This skill's output passes if:
- [ ] Schema validation passes
- [ ] Both week analyses are present
- [ ] At least one theme analysis returned
- [ ] ICP match logic documented in output
- [ ] Recommendations are actionable (specific themes/topics)

---

## Examples

See `/examples/` for annotated input/output pairs.

### Example Output Summary

```json
{
  "summary": {
    "period": "2026-01-13 to 2026-01-27",
    "total_posts": 18,
    "total_reactors": 342,
    "avg_reactors_per_post": 19.0,
    "icp_engagement_rate": 0.23,
    "week_over_week_change": "+12%"
  }
}
```

---

## Tests

See `/tests/` for golden outputs and validation prompts.

To run tests:
```bash
claude /test-skill icp-historical-analysis
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
python skills/icp-historical-analysis/verify_setup.py
```

This checks:
- Firebase credentials configured
- Client context accessible
- ICP definitions present

---

## Trigger Schedule

This skill is designed to run on a **weekly trigger** (e.g., every Monday at 9:00 AM).

Configuration in `config/triggers.yaml`:
```yaml
icp-historical-analysis:
  schedule: "0 9 * * 1"  # Every Monday at 9 AM
  enabled: true
  parameters:
    lookback_days: 14
```

---

## Changelog

### v1.0.0 (2026-01-27)
- Initial release
- Weekly analysis of past 14 days
- ICP engagement tracking
- Theme-based analysis

---

## Notes

- ICP definitions should be maintained in client context (`clients/{clientId}/context/audience.md`)
- Reactor data must be collected by social-listening-collect skill first
- Theme extraction uses post tags when available, falls back to content analysis
