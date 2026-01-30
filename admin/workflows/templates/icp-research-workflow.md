# Workflow: ICP Research & Customer Intelligence

Version: v1.0.0
Type: analysis
Author: mh1-engineering
Created: 2026-01-29

---

## Purpose

Enable MH1 to deliver comprehensive ICP (Ideal Customer Profile) research for any universal client. This workflow orchestrates context gathering, freshness validation, quantitative analysis, qualitative synthesis, and deliverable generation to answer: **"Who are we serving and why do they stay?"**

Use this workflow when:
- Onboarding a new client for ICP research
- Refreshing ICP definitions for an existing client
- Validating ICP hypotheses with retention data
- Generating customer intelligence deliverables

---

## Trigger

- **Manual:** `/run-workflow icp-research --client_id {client_id}`
- **Scheduled:** Not applicable (run on-demand)
- **Event:** After client-onboarding completion

---

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `client_id` | string | yes | Client identifier |
| `tenant_id` | string | no | Tenant for cost tracking (default: client_id) |
| `interview_files` | array | no | Paths to interview transcripts |
| `refresh_discovery` | boolean | no | Force re-run of discovery even if fresh (default: false) |
| `ttl_days` | integer | no | Context freshness threshold in days (default: 30) |
| `skip_phases` | array | no | Phases to skip (e.g., ["qualitative"] if no interviews) |

**Input schema:** `schemas/icp-research-input.json`

---

## Outputs

| Name | Type | Description |
|------|------|-------------|
| `icp_definitions` | array | ICP one-pagers per founder segment |
| `retention_analysis` | object | Retention curves with qualitative justification |
| `positioning_matrix` | object | Product offering → segment fit matrix |
| `recommendations` | array | Prioritized recommendations for ICP-driven growth |
| `status` | string | "success" | "partial" | "failed" | "review" |
| `_meta` | object | Workflow metadata (phases, timing, cost) |

**Output schema:** `schemas/icp-research-output.json`

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 0: CONTEXT VALIDATION                                      │
│ Check freshness → Trigger discovery if needed                    │
├─────────────────────────────────────────────────────────────────┤
│ Skills: lib/freshness.py                                         │
│ Outputs: freshness_result, discovery_needed                      │
│ Checkpoint: If discovery needed, confirm with user               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (if discovery needed)
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 0.5: DISCOVERY (conditional)                               │
│ Run discovery skills to refresh context                          │
├─────────────────────────────────────────────────────────────────┤
│ Skills: research-company, research-founder, generate-context-    │
│         summary, client-onboarding (Phase 2.5 if no lifecycle)   │
│ Outputs: company_research, founder_research, context_summary,    │
│          lifecycle_config                                        │
│ Checkpoint: Yes (verify discovery quality)                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: DATA GATHERING                                          │
│ Pull customer data from warehouse and CRM                        │
├─────────────────────────────────────────────────────────────────┤
│ Skills: crm-discovery, data-warehouse-discovery, identity-mapping│
│ Parallel: Yes (all three can run concurrently)                   │
│ Outputs: crm_data, warehouse_data, identity_map                  │
│ Checkpoint: No                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: LIFECYCLE ANALYSIS                                      │
│ Analyze customer journey, retention, engagement                  │
├─────────────────────────────────────────────────────────────────┤
│ Skills: lifecycle-audit, cohort-retention-analysis,              │
│         engagement-velocity, account-360 (sample)                │
│ Sequential: lifecycle-audit first, then parallel for rest        │
│ Outputs: lifecycle_report, retention_curves, engagement_trends,  │
│          account_deep_dives                                      │
│ Checkpoint: Yes (human review if retention < 30%)                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3: QUALITATIVE SYNTHESIS                                   │
│ Process interviews and validate assumptions                      │
├─────────────────────────────────────────────────────────────────┤
│ Skills: incorporate-interview-results                            │
│ Conditional: Skipped if no interview_files provided              │
│ Outputs: interview_synthesis, founder_archetypes, voice_patterns │
│ Checkpoint: Yes (review archetype extraction)                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 4: ICP DEFINITION                                          │
│ Synthesize archetypes and validate against data                  │
├─────────────────────────────────────────────────────────────────┤
│ Skills: extract-audience-persona, qualify-leads                  │
│ Inputs: All outputs from Phases 2-3                              │
│ Outputs: icp_definitions, icp_validation_scores                  │
│ Checkpoint: Yes (human review of ICP definitions)                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 5: DELIVERABLES                                            │
│ Generate final client-ready outputs                              │
├─────────────────────────────────────────────────────────────────┤
│ Outputs: ICP one-pagers, retention analysis, positioning matrix, │
│          recommendations                                         │
│ Delivery: clients/{client_id}/deliverables/icp-research/         │
│ Checkpoint: Yes (final QA before delivery)                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase Details

### Phase 0: Context Validation

**Purpose:** Check if client context is fresh enough for analysis. Prevents stale data from corrupting ICP definitions.

**Agent:** orchestrator
**Model:** claude-haiku (fast validation)

**Actions:**
```python
from lib.freshness import check_context_freshness, ensure_context_fresh

# Check freshness
result = check_context_freshness(
    client_id=inputs["client_id"],
    ttl_days=inputs.get("ttl_days", 30),
    require_lifecycle=True
)

if inputs.get("refresh_discovery") or result["action"] == "run_discovery":
    # Trigger Phase 0.5
    discovery_needed = True
    discovery_skills = result.get("missing_items", []) + result.get("stale_items", [])
else:
    discovery_needed = False
```

**On success:** Proceed to Phase 1 (or Phase 0.5 if discovery needed)
**On failure:** Return error with freshness details

---

### Phase 0.5: Discovery (Conditional)

**Purpose:** Refresh client context if stale or missing.

**Agent:** worker-researcher
**Skills:**
- `research-company` — Brand, positioning, products
- `research-founder` — Founder profile, voice patterns
- `generate-context-summary` — Consolidate all context
- `client-onboarding` (Phase 2.5 only) — Lifecycle mapping if missing

**Execution:**
```python
# Run in sequence (each depends on previous)
if "company_research" in discovery_skills:
    await run_skill("research-company", {"client_id": client_id})

if "founder_research" in discovery_skills:
    await run_skill("research-founder", {"client_id": client_id})

if "context_summary" in discovery_skills:
    await run_skill("generate-context-summary", {"client_id": client_id})

if "lifecycle_mapping" in discovery_skills:
    await run_skill("client-onboarding", {
        "client_id": client_id,
        "phase": "2.5"  # Lifecycle mapping only
    })
```

**Checkpoint:** Verify discovery quality before proceeding

---

### Phase 1: Data Gathering

**Purpose:** Extract customer data from configured data sources.

**Agent:** worker-extractor
**Skills:**
- `crm-discovery` — Contacts, deals, activity
- `data-warehouse-discovery` — Health, revenue, engagement
- `identity-mapping` — Link warehouse ↔ CRM

**Execution:**
```python
# Run in parallel (no dependencies between these)
results = await asyncio.gather(
    run_skill("crm-discovery", {"client_id": client_id, "limit": 5000}),
    run_skill("data-warehouse-discovery", {"client_id": client_id}),
    run_skill("identity-mapping", {"client_id": client_id})
)

crm_data, warehouse_data, identity_map = results
```

**On success:** Proceed to Phase 2
**On failure:** Continue with partial data, log warning

---

### Phase 2: Lifecycle Analysis

**Purpose:** Analyze customer journey, retention patterns, and engagement.

**Agent:** worker-analyzer
**Skills:**
- `lifecycle-audit` — Bottlenecks, at-risk, upsell
- `cohort-retention-analysis` — Retention curves, comparisons
- `engagement-velocity` — Trend detection, early warnings
- `account-360` (sample) — Deep dive on 3-5 accounts

**Execution:**
```python
# Sequential start, then parallel
lifecycle_report = await run_skill("lifecycle-audit", {
    "client_id": client_id,
    "tenant_id": tenant_id
})

# Parallel analysis using lifecycle context
retention, engagement, accounts = await asyncio.gather(
    run_skill("cohort-retention-analysis", {
        "client_id": client_id,
        "lookback_months": 12
    }),
    run_skill("engagement-velocity", {
        "client_id": client_id
    }),
    run_skill("account-360", {
        "client_id": client_id,
        "accounts": select_representative_accounts(lifecycle_report, n=5)
    })
)
```

**Checkpoint:** Human review if:
- Retention < 30% at day 30
- Health score < 0.5
- Data quality issues detected

---

### Phase 3: Qualitative Synthesis

**Purpose:** Process interview transcripts and extract founder archetypes.

**Agent:** worker-synthesizer
**Skills:**
- `incorporate-interview-results` — Process 10-15 interviews

**Conditional:** Skipped if `skip_phases` includes "qualitative" or no `interview_files` provided.

**Execution:**
```python
if "qualitative" in inputs.get("skip_phases", []):
    interview_synthesis = None
else:
    interview_synthesis = await run_skill("incorporate-interview-results", {
        "client_id": client_id,
        "interview_files": inputs.get("interview_files", []),
        "extract_archetypes": True,
        "validate_assumptions": True,
        "extract_voice_patterns": True
    })
```

**Outputs:**
- Founder archetypes (3-5 distinct profiles)
- Validated/invalidated assumptions
- Voice patterns for messaging
- Research gaps to fill

---

### Phase 4: ICP Definition

**Purpose:** Synthesize quantitative and qualitative findings into ICP definitions.

**Agent:** worker-synthesizer
**Model:** claude-sonnet-4 (complex reasoning)

**Skills:**
- `extract-audience-persona` — Structure ICP definitions
- `qualify-leads` — Validate ICPs against actual customers

**Process:**
1. Combine retention drivers with interview archetypes
2. Generate ICP hypotheses per segment
3. Validate each ICP against customer data
4. Score fit between ICP and best customers

**Execution:**
```python
# Synthesize archetypes from all sources
icp_input = {
    "retention_drivers": retention_analysis["retention_drivers"],
    "interview_archetypes": interview_synthesis.get("archetypes", []),
    "engagement_patterns": engagement_trends["patterns"],
    "lifecycle_segments": lifecycle_report["segments"]
}

icp_definitions = await run_skill("extract-audience-persona", {
    "client_id": client_id,
    "sources": icp_input
})

# Validate against actual customers
validation = await run_skill("qualify-leads", {
    "client_id": client_id,
    "icp_definitions": icp_definitions,
    "validate_against": "top_customers"
})
```

**Checkpoint:** Human review of ICP definitions

---

### Phase 5: Deliverables

**Purpose:** Generate final client-ready outputs.

**Agent:** worker-formatter
**Model:** claude-sonnet-4 (coherent writing)

**Deliverables:**
1. **ICP One-Pagers** (per segment)
   - Demographics & firmographics
   - Pain points & motivations
   - Buying triggers & objections
   - Messaging recommendations

2. **Retention Analysis Report**
   - Retention curves by cohort
   - Statistical comparisons
   - Qualitative justification from interviews
   - Churn risk factors

3. **Product Positioning Matrix**
   - Offering → Segment fit scores
   - Value proposition per segment
   - Feature prioritization

4. **Recommendations**
   - Prioritized by impact
   - Linked to data/interview evidence
   - Actionable next steps

**Delivery location:** `clients/{client_id}/deliverables/icp-research/`

---

## Error Handling

| Error Type | Phase | Action |
|------------|-------|--------|
| Context stale | 0 | Trigger discovery, continue after refresh |
| Discovery failed | 0.5 | Return error, cannot proceed without context |
| CRM unavailable | 1 | Continue with warehouse data only |
| Warehouse unavailable | 1 | Continue with CRM data only (limited) |
| Both unavailable | 1 | Return error, cannot proceed |
| Low retention detected | 2 | Continue but flag for human review |
| No interviews | 3 | Skip phase, note limitation in output |
| ICP validation < 0.6 | 4 | Retry with stricter constraints |
| Formatting failed | 5 | Return raw output with warning |

---

## Telemetry

Log for each run:
```json
{
  "workflow_id": "icp_research_2026012901",
  "workflow_name": "icp-research",
  "client_id": "{client_id}",
  "start_time": "2026-01-29T10:00:00Z",
  "end_time": "2026-01-29T10:45:00Z",
  "phases": {
    "context_validation": {"status": "success", "duration_seconds": 5},
    "discovery": {"status": "skipped", "reason": "context_fresh"},
    "data_gathering": {"status": "success", "duration_seconds": 120},
    "lifecycle_analysis": {"status": "success", "duration_seconds": 180},
    "qualitative_synthesis": {"status": "success", "duration_seconds": 300},
    "icp_definition": {"status": "success", "duration_seconds": 240},
    "deliverables": {"status": "success", "duration_seconds": 120}
  },
  "total_duration_seconds": 965,
  "total_cost_usd": 4.50,
  "skills_invoked": [
    {"skill": "crm-discovery", "cost": 0.35},
    {"skill": "cohort-retention-analysis", "cost": 0.75},
    {"skill": "incorporate-interview-results", "cost": 1.20}
  ],
  "status": "success",
  "human_reviews_required": 2,
  "deliverables_generated": 4
}
```

---

## Example Run

**Input:**
```json
{
  "client_id": "FFC",
  "tenant_id": "FFC",
  "interview_files": [
    "clients/FFC/interviews/founder-interview-01.md",
    "clients/FFC/interviews/founder-interview-02.md"
  ],
  "ttl_days": 30
}
```

**Command:**
```bash
claude /run-workflow icp-research --client_id FFC --interview_files "interviews/*.md"
```

**Output:**
```json
{
  "icp_definitions": [
    {
      "segment": "Technical First-Time Founders",
      "fit_score": 0.85,
      "retention_rate": 0.72,
      "description": "...",
      "pain_points": ["..."],
      "messaging": ["..."]
    }
  ],
  "retention_analysis": {
    "overall_30_day": 0.68,
    "best_segment": "Technical First-Time Founders",
    "worst_segment": "Non-Technical Serial Entrepreneurs",
    "key_insight": "..."
  },
  "positioning_matrix": {
    "cohort_program": {
      "Technical First-Time Founders": 0.9,
      "Non-Technical Serial Entrepreneurs": 0.5
    }
  },
  "recommendations": [
    {
      "priority": "high",
      "action": "Focus acquisition on technical first-time founders",
      "evidence": "72% retention vs 48% for other segments",
      "expected_impact": "+15% overall retention"
    }
  ],
  "status": "success",
  "_meta": {
    "workflow_id": "icp_research_2026012901",
    "total_cost_usd": 4.50,
    "phases_completed": 6,
    "human_reviews": 2
  }
}
```

---

## MRD Deliverable Mapping

| MRD Deliverable | How Generated | Phase |
|-----------------|---------------|-------|
| ICP one-pagers per segment | `extract-audience-persona` + synthesis | 4, 5 |
| Retention analysis with qualitative justification | `cohort-retention-analysis` + `incorporate-interview-results` | 2, 3 |
| Product positioning matrix | Lifecycle upsell analysis + segment mapping | 2, 4 |
| Pricing intelligence | `account-360` basket analysis | 2 |
| Customer research repository | All outputs stored in `clients/{client_id}/` | 5 |

---

## Notes

- **First Run:** Expect 30-60 minutes for a new client (discovery + full analysis)
- **Refresh Run:** Expect 15-30 minutes if context is fresh
- **Interviews:** Quality of ICP definitions significantly improves with 10+ interviews
- **Data Requirements:** Minimum 100 customers, 6 months history for meaningful retention curves
- **Human Reviews:** Plan for 2-3 review checkpoints per run
- **Cost:** Typical run costs $3-6 depending on data volume and interview count
