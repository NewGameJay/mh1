---
name: lifecycle-audit
description: |
  Analyze customer lifecycle stages to identify conversion bottlenecks, churn risks, and upsell opportunities.
  Use when asked to 'audit lifecycle', 'analyze customer journey', 'find churn risks',
  'identify bottlenecks', or 'assess pipeline health'.
license: Proprietary

# Required platform connections (skill will fail without these)
requires_mcp:
  - hubspot  # Required for contact/lifecycle data

# Optional platforms (enhances results if available)
compatibility:
  - snowflake  # Adds usage data enrichment

metadata:
  author: mh1-engineering
  version: "2.0.0"
  status: active
  estimated_runtime: "30s-120s"
  max_cost: "$2.00"
  client_facing: true
  tags:
    - lifecycle
    - hubspot
    - analytics
    - churn
    - pipeline
allowed-tools: Read Write Shell CallMcpTool
---

# Skill: Lifecycle Audit

---

## When to Use

Use this skill when you need to:
- Audit customer lifecycle stage distribution
- Identify conversion bottlenecks between stages
- Find accounts at risk of churning
- Discover upsell opportunities
- Generate actionable recommendations for journey health

## Purpose

Analyzes customer lifecycle stages to identify conversion bottlenecks, accounts at risk of churning, and upsell opportunities. Provides actionable, prioritized recommendations for improving customer journey health.

This skill connects to HubSpot (via MCP) for contact data and optionally enriches with Snowflake usage data to provide deeper engagement insights.

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tenant_id` | string | No | Client/tenant identifier for cost tracking (default: "default") |
| `company_id` | string | No | Specific company to analyze (analyzes all if not provided) |
| `limit` | integer | No | Max accounts to analyze (default: 100, max: 5000) |
| `stages` | array | No | Lifecycle stages to include (default: all) |
| `execution_mode` | string | No | "suggest" \| "preview" \| "execute" (default: "suggest") |
| `data_requirements_override` | object | No | Override data validation settings |

**Input schema:** `schemas/input.json`

---

## Outputs

```json
{
  "summary": {
    "total_accounts": 150,
    "by_stage": { "lead": 45, "mql": 30, "sql": 25, "customer": 50 },
    "health_score": 0.72
  },
  "bottlenecks": [
    { "from_stage": "mql", "to_stage": "sql", "rate": 0.15, "benchmark": 0.25, "severity": "high" }
  ],
  "at_risk": [
    { "email": "user@acme.com", "name": "John Doe", "stage": "customer", "risk_score": 0.85 }
  ],
  "upsell_candidates": [
    { "email": "user@techco.com", "name": "Jane Smith", "stage": "customer", "upsell_score": 0.9 }
  ],
  "recommendations": [
    { "priority": "high", "category": "retention", "action": "...", "impact": "..." }
  ],
  "_meta": {
    "tenant_id": "client_abc",
    "run_id": "d86b2024",
    "execution_mode": "suggest",
    "runtime_seconds": 45.2,
    "cost_usd": 0.35,
    "release_action": "auto_deliver"
  }
}
```

**Output schema:** `schemas/output.json`

---

## Data Requirements

| Requirement | Minimum | Recommended | On Insufficient |
|-------------|---------|-------------|-----------------|
| Record count | 20 | 100+ | warn_and_continue |
| `lifecyclestage` coverage | 100% | 100% | abort |
| `email` coverage | 80% | 95% | warn |
| `company` coverage | 70% | 80% | warn |

**Behavior on insufficient data:**
- Below minimum records (20): Returns error with data quality report
- Missing required fields: Returns error with field coverage report  
- Below recommended: Continues with warning in `_meta.data_quality.warnings`

**Override:** Set `data_requirements_override.skip_validation: true` to bypass (use with caution)

---

## SLA (Service Level Agreement)

| Metric | Target | Maximum | Exceeded Action |
|--------|--------|---------|-----------------|
| Runtime | 30s | 120s | timeout_error |
| Retries | 2 | 3 | human_review |
| Cost per run | $0.50 | $2.00 | warn at 80%, abort at max |

### Runtime breakdown (typical)

| Step | Expected | Notes |
|------|----------|-------|
| Discovery (HubSpot) | 5-10s | Depends on limit |
| Enrichment (Snowflake) | 5-15s | Optional, parallel |
| Analysis | 5-10s | Chunked for large datasets |
| Scoring | 2-5s | Local computation |
| Synthesis | 5-10s | LLM call |
| Evaluation | 2-3s | Schema validation |

---

## Failure Modes

| Mode | Trigger | Output | Escalation |
|------|---------|--------|------------|
| **Partial Success** | 1+ enrichment steps failed | Discovery + analysis results, enrichment skipped | No (continue without enrichment) |
| **Data Unavailable** | HubSpot MCP timeout/error | Cached data if <24h, else error | Only if no cache |
| **Insufficient Data** | <20 records or missing required fields | Error report with data quality details | No |
| **Budget Exceeded** | Tenant over daily/monthly limit | Budget status message | No (blocks run) |
| **Quality Failed** | Eval score < 0.6 | Raw output + UNVALIDATED flag | Yes (human_review) |
| **Complete Failure** | Unrecoverable error | Error report with stack trace | Yes |

### Recovery patterns

```python
# HubSpot unavailable
if not hubspot.is_available():
    # Try cache first
    cached = load_cache(tenant_id, max_age_hours=24)
    if cached:
        return {"output": cached, "source": "cache", "warning": "Using cached data"}
    else:
        return {"status": "failed", "error": "HubSpot unavailable, no cache"}

# Snowflake enrichment fails
try:
    usage_data = snowflake.execute_query(query)
except Exception:
    # Continue without enrichment
    usage_data = None
    warnings.append("Snowflake enrichment unavailable")
```

---

## Human Review Triggers

| Trigger | Mandatory | Review SLA | Escalation |
|---------|-----------|------------|------------|
| First run for tenant | Yes | 24h | None (wait for approval) |
| Eval score < 0.7 | Yes | 8h | Auto-reject after 24h |
| Eval score 0.7-0.8 | No | - | Auto-refine attempted |
| Execute mode with >10 changes | Yes | 4h | Auto-reject after 12h |
| Critical data quality issues | Yes | 8h | Block future runs |

### Review context

When routed to human review, the following context is provided:
- Full output (recommendations, at-risk, upsell)
- Evaluation results with dimension scores
- Data quality report
- Run telemetry (tokens, cost, duration)

---

## Execution Modes

| Mode | Description | Side Effects | Approval Required |
|------|-------------|--------------|-------------------|
| `suggest` | Generate recommendations only | None (read-only) | No |
| `preview` | Show what changes would be made | None (dry-run) | No |
| `execute` | Apply changes to HubSpot/Snowflake | Tags contacts, creates lists | Yes (if >10 changes) |

### Execute mode actions

When `execution_mode: "execute"`:
1. Tags at-risk contacts with `at_risk: true` property in HubSpot
2. Creates "At-Risk Accounts" active list
3. Logs all changes in `_meta.execution.changes`

**Approval threshold:** If >10 contacts would be modified, requires human approval before execution.

---

## Dependencies

- **MCP Servers:** 
  - `hubspot` (required) - Contact data
  - `snowflake` (optional) - Usage/engagement enrichment
  
- **Models:**
  - `claude-sonnet-4` - Main analysis and synthesis
  - `claude-haiku` - Chunk processing for large datasets
  
- **Other Skills:** None

- **Lib modules:**
  - `runner.py` - WorkflowRunner, ContextManager
  - `evaluator.py` - Output evaluation
  - `release_policy.py` - Release decisions
  - `budget.py` - Per-tenant cost tracking
  - `mcp_client.py` - HubSpot/Snowflake clients

---

## Context Handling

| Input size | Strategy | Model |
|------------|----------|-------|
| < 8K tokens (~200 contacts) | Inline | claude-sonnet-4 |
| 8K-50K tokens (~200-1000 contacts) | Chunked | Haiku for chunks, Sonnet for synthesis |
| > 50K tokens (~1000+ contacts) | Full context offload | Haiku for chunks, Sonnet for synthesis |

### Expected input size

- **Typical:** 50-200 records, ~2-8K tokens
- **Maximum tested:** 5,000 records, ~200K tokens
- **Strategy for large inputs:** Chunked with 500 records per chunk

### Large input handling

```python
from lib.runner import ContextManager, ContextConfig

def process_contacts(contacts):
    ctx = ContextManager(contacts, ContextConfig(max_inline_tokens=8000))
    
    if ctx.should_offload():
        for chunk in ctx.chunk(size=500):
            result = process_chunk(chunk, model="claude-haiku")
            ctx.aggregate_buffer("results", result)
        
        final = synthesize(ctx.get_aggregated("results"), model="claude-sonnet-4")
    else:
        final = process_directly(contacts, model="claude-sonnet-4")
    
    return final
```

---

## Process

1. **Budget Check** - Verify tenant has remaining budget
2. **Discovery** - Fetch contacts from HubSpot by lifecycle stage
3. **Validation** - Check data requirements (record count, field coverage)
4. **Enrichment** - Join with Snowflake usage data (if available)
5. **Analysis** - Calculate conversion rates, identify bottlenecks
6. **Scoring** - Risk score and upsell score per account
7. **Synthesis** - Generate recommendations with LLM
8. **Evaluation** - Run quality checks (6 dimensions)
9. **Release Decision** - Determine auto_deliver/refine/review/blocked

---

## Constraints

- Maximum 5,000 records per run (for performance)
- Maximum $2.00 cost per run (budget limit)
- Maximum 120 seconds runtime (timeout)
- All outputs must include `_meta` object
- All claims must be data-backed (no hallucinated statistics)
- Must pass evaluation score ≥ 0.8 for auto-delivery

---

## Quality Criteria

This skill's output passes if:
- [ ] Schema validation passes (input and output)
- [ ] All required fields present (summary, recommendations, _meta)
- [ ] At least 1 actionable recommendation generated
- [ ] Health score calculated (0-1 range)
- [ ] Data quality metrics included in _meta
- [ ] Evaluation score ≥ 0.8 (for auto-delivery)

---

## Usage

```bash
# From CLI
./mh1 run skill lifecycle-audit --tenant_id client_abc --limit 100

# Preview mode
./mh1 run skill lifecycle-audit --tenant_id client_abc --execution_mode preview

# Execute mode (with approval if needed)
./mh1 run skill lifecycle-audit --tenant_id client_abc --execution_mode execute

# Programmatic
python -m skills.lifecycle-audit.run --tenant_id client_abc --output results.json
```

```python
# Python API
from skills.lifecycle_audit.run import run_lifecycle_audit

result = run_lifecycle_audit({
    "tenant_id": "client_abc",
    "limit": 100,
    "execution_mode": "suggest"
})

if result["status"] == "success":
    print(f"Health score: {result['output']['summary']['health_score']}")
    print(f"At-risk accounts: {len(result['output']['at_risk'])}")
    print(f"Cost: ${result['output']['_meta']['cost_usd']}")
```

---

## Examples

See `/examples/` for annotated input/output pairs.

---

## Tests

See `/tests/` for golden outputs and validation prompts.

To run tests:
```bash
python -m pytest skills/lifecycle-audit/tests/
```

---

## Changelog

### v2.0.0 (2026-01-26)
- **BREAKING:** Added required `_meta` object to output
- Added `tenant_id` for per-client cost tracking
- Added `execution_mode` (suggest/preview/execute)
- Added budget enforcement via BudgetManager
- Added release policy integration (auto_deliver/refine/review/blocked)
- Added context handling for large datasets (RLM pattern)
- Added `data_requirements_override` input option
- Improved data quality validation and reporting
- Added Snowflake enrichment (optional)

### v1.0.0 (2026-01-23)
- Initial release
- Basic HubSpot integration
- Conversion analysis and recommendations

---

## Notes

- **First-time setup:** Ensure HubSpot MCP is configured in `config/mcp-servers.json`
- **Snowflake:** Optional but significantly improves analysis depth with usage data
- **Budget:** Default limits are $100/day, $2000/month per tenant (see `config/quotas.yaml`)
- **Performance:** For >1000 contacts, expect 60-90 second runtime due to chunked processing
- **Cache:** HubSpot data is cached for 24 hours to reduce API calls
