# Flowcode Skills Assessment & Implementation Plan

**Date:** January 28, 2026  
**Status:** Ready for Implementation

---

## Executive Summary

After scanning the Flowcode codebase (`/flowcode`), we found **significant existing infrastructure** that can be leveraged to build the proposed skills. The codebase is ~85% complete with:

- **22 verified query templates** (12 Snowflake, 7 HubSpot, 3 join queries)
- **4 pre-built playbooks** for common workflows
- **MCP servers** for both Snowflake and HubSpot
- **8 reason codes** (RC1-RC8) with content generation templates
- **Artifact storage** with provenance tracking

However, there are gaps that need addressing before some skills can be production-ready.

---

## Skill-by-Skill Assessment

### ✅ = Ready to Build | ⚠️ = Needs Work | ❌ = Not Feasible

---

## 1. Discovery & Intelligence Skills

| Skill | Feasibility | Quality | Useful | Notes |
|-------|-------------|---------|--------|-------|
| `snowflake-discovery` | ✅ Ready | HIGH | YES | 22 queries exist in `templates/queries.json` |
| `hubspot-discovery` | ✅ Ready | HIGH | YES | MCP server has 7 tools, 50+ queries defined |
| `identity-mapping` | ✅ Ready | HIGH | YES | `02_identity_map.sql` verified (98% match rate) |
| `data-quality-audit` | ⚠️ Partial | MEDIUM | YES | Coverage queries exist, need null rate queries |

**Verdict:** All feasible. The infrastructure exists.

---

## 2. Customer Intelligence Skills

| Skill | Feasibility | Quality | Useful | Notes |
|-------|-------------|---------|--------|-------|
| `lifecycle-audit` | ✅ Exists | HIGH | YES | Already in `.mh1-system/skills/` |
| `at-risk-detection` | ✅ Ready | HIGH | YES | `sf_at_risk_high_value` query verified ($3.2M ARR) |
| `upsell-candidates` | ✅ Ready | HIGH | YES | `sf_top_100_f1_upsell` exists (note: returns 50, not 100) |
| `churn-prediction` | ⚠️ Partial | MEDIUM | YES | `hs_churn_risk_contacts` works, but `CHURN_REASON` mostly NULL |
| `dormant-detection` | ⚠️ Partial | MEDIUM | YES | Uses health score proxy (< 40), not actual activity |
| `engagement-velocity` | ✅ Ready | HIGH | YES | `sf_engagement_velocity` week-over-week comparison |
| `conversion-funnel` | ✅ Ready | HIGH | YES | `sf_conversion_funnel` scans → page views → conversions |

**Issues Found:**
- `sf_churned_accounts` uses `HEALTH_STATUS = 'Closed Won'` (incorrect)
- `sf_dormant_high_value` uses health score proxy, not actual activity data
- F1 events are in Databricks, not Snowflake (302 F2 orgs only have events)

---

## 3. Sales Intelligence Skills

| Skill | Feasibility | Quality | Useful | Notes |
|-------|-------------|---------|--------|-------|
| `pipeline-analysis` | ✅ Ready | HIGH | YES | `hs_sales_pipeline_deals` + `hs_renewal_pipeline_deals` |
| `sales-rep-performance` | ✅ Ready | HIGH | YES | `sf_sales_activity_by_rep` with ARR and risk metrics |
| `deal-velocity` | ✅ Ready | HIGH | YES | `sf_deal_velocity_by_rep` win rates by CS owner |
| `account-360` | ⚠️ Partial | MEDIUM | YES | Requires join across Snowflake + HubSpot |
| `renewal-tracker` | ✅ Ready | HIGH | YES | `hs_renewal_pipeline_deals` with amounts |

**Note:** Pipeline IDs are hardcoded (`125254959`, `126693718`) - Flowcode-specific.

---

## 4. Content Generation Skills

| Skill | Feasibility | Quality | Useful | Notes |
|-------|-------------|---------|--------|-------|
| `email-template-analysis` | ✅ Ready | HIGH | YES | `prompts/analysis_rubric.md` exists |
| `email-copy-generator` | ✅ Ready | HIGH | YES | `copy_generator.py` with RC1-RC8 templates |
| `cohort-email-builder` | ✅ Ready | HIGH | YES | Full pipeline in `communication_strategy.py` |

**Existing RC Templates:**
- RC1: Usage Decay → Re-engagement
- RC2: High Scans, No Conversion → Conversion tips
- RC3: High Exit Rate → Content improvement
- RC4: F1 Upsell Ready → F2 upgrade pitch
- RC5: Power User → Advocacy
- RC6: At-Risk High Value → Urgent retention
- RC7: New Implementation → Onboarding
- RC8: Needs Classification → Discovery

---

## 5. Automation & Writeback Skills

| Skill | Feasibility | Quality | Useful | Notes |
|-------|-------------|---------|--------|-------|
| `hubspot-tag-contact` | ⚠️ Partial | MEDIUM | YES | PATCH exists, no dedicated tagging |
| `hubspot-tag-company` | ❌ Missing | - | YES | Company PATCH not implemented |
| `hubspot-create-task` | ❌ Missing | - | YES | Task POST not implemented |
| `hubspot-update-stage` | ⚠️ Partial | MEDIUM | YES | Contact PATCH exists |
| `hubspot-writeback-copy` | ✅ Ready | HIGH | YES | `hubspot_writeback.py` with `ai_*` properties |

**Critical Gap:** Only contact property updates implemented. Need:
- `POST /crm/v3/objects/tasks` for task creation
- `PATCH /crm/v3/objects/companies/{id}` for company updates
- `POST /crm/v3/objects/deals` for deal creation

---

## 6. Orchestration Skills

| Skill | Feasibility | Quality | Useful | Notes |
|-------|-------------|---------|--------|-------|
| `playbook-executor` | ✅ Ready | HIGH | YES | `StrictCopilotOrchestrator` exists |
| `intent-mapper` | ⚠️ Partial | MEDIUM | YES | Keyword matching only, no LLM |
| `artifact-manager` | ✅ Ready | HIGH | YES | `ArtifactStore` with checksums |

**Gap:** Orchestrator is initialized but `process_chat()` doesn't consistently call `execute_plan()`.

---

## Quality Summary

| Category | Ready | Partial | Missing | Total |
|----------|-------|---------|---------|-------|
| Discovery & Intelligence | 3 | 1 | 0 | 4 |
| Customer Intelligence | 4 | 3 | 0 | 7 |
| Sales Intelligence | 4 | 1 | 0 | 5 |
| Content Generation | 3 | 0 | 0 | 3 |
| Automation & Writeback | 2 | 2 | 2 | 6 |
| Orchestration | 2 | 1 | 0 | 3 |
| **TOTAL** | **18** | **8** | **2** | **28** |

**Verdict:** 64% ready, 29% partial (need fixes), 7% missing (need new implementation)

---

## Implementation Plan

### Phase 1: Foundation Skills (Week 1-2)
**Goal:** Create MH1 skills wrapping existing Flowcode capabilities

| Skill | Source | Priority | Effort |
|-------|--------|----------|--------|
| `snowflake-discovery` | `templates/queries.json` | P1 | Low |
| `hubspot-discovery` | `mcp_server_hubspot.py` | P1 | Low |
| `identity-mapping` | `02_identity_map.sql` | P1 | Low |
| `at-risk-detection` | `sf_at_risk_high_value` | P1 | Low |
| `upsell-candidates` | `sf_top_100_f1_upsell` | P1 | Low |
| `pipeline-analysis` | `hs_sales_pipeline_deals` | P1 | Low |

### Phase 2: Intelligence Skills (Week 2-3)
**Goal:** Build customer and sales intelligence capabilities

| Skill | Source | Priority | Effort |
|-------|--------|----------|--------|
| `engagement-velocity` | `sf_engagement_velocity` | P1 | Low |
| `conversion-funnel` | `sf_conversion_funnel` | P1 | Low |
| `sales-rep-performance` | `sf_sales_activity_by_rep` | P1 | Low |
| `deal-velocity` | `sf_deal_velocity_by_rep` | P1 | Low |
| `renewal-tracker` | `hs_renewal_pipeline_deals` | P1 | Low |

### Phase 3: Content Generation Skills (Week 3-4)
**Goal:** Leverage Flowcode's copy generation for MH1

| Skill | Source | Priority | Effort |
|-------|--------|----------|--------|
| `email-copy-generator` | `copy_generator.py` | P1 | Medium |
| `email-template-analysis` | `prompts/analysis_rubric.md` | P2 | Low |
| `cohort-email-builder` | `communication_strategy.py` | P2 | Medium |

### Phase 4: Fixes & Missing Capabilities (Week 4-5)
**Goal:** Fix partial implementations and add missing pieces

| Task | Type | Priority | Effort |
|------|------|----------|--------|
| Fix `sf_churned_accounts` query | Fix | P1 | Low |
| Fix `sf_dormant_high_value` to use activity | Fix | P2 | Medium |
| Add HubSpot task creation | New | P1 | Medium |
| Add HubSpot company update | New | P2 | Low |
| Add rate limiting to HubSpot calls | Fix | P1 | Low |
| Wire orchestrator in `process_chat()` | Fix | P2 | Medium |

### Phase 5: Advanced Orchestration (Week 5-6)
**Goal:** Full playbook execution and writeback

| Skill | Source | Priority | Effort |
|-------|--------|----------|--------|
| `playbook-executor` | `StrictCopilotOrchestrator` | P1 | Medium |
| `artifact-manager` | `ArtifactStore` | P2 | Low |
| `hubspot-writeback-copy` | `hubspot_writeback.py` | P1 | Low |

---

## Files to Create

### New Skills (in `skills/`)

```
skills/
├── snowflake-discovery/SKILL.md
├── hubspot-discovery/SKILL.md
├── identity-mapping/SKILL.md
├── at-risk-detection/SKILL.md
├── upsell-candidates/SKILL.md
├── engagement-velocity/SKILL.md
├── conversion-funnel/SKILL.md
├── pipeline-analysis/SKILL.md
├── sales-rep-performance/SKILL.md
├── deal-velocity/SKILL.md
├── renewal-tracker/SKILL.md
├── email-copy-generator/SKILL.md
├── cohort-email-builder/SKILL.md
├── playbook-executor/SKILL.md
└── hubspot-writeback-copy/SKILL.md
```

### Updates to Existing Files

| File | Change |
|------|--------|
| `flowcode/templates/queries.json` | Fix `sf_churned_accounts`, `sf_top_100_f1_upsell` limit |
| `flowcode/backend/lib/runners.py` | Add rate limiting |
| `flowcode/scripts/mcp_server_hubspot.py` | Add task/company endpoints |
| `flowcode/backend/main.py` | Wire orchestrator execution |

---

## Dependencies

| Dependency | Required For | Status |
|------------|--------------|--------|
| Snowflake MCP | Discovery skills | ✅ Available (`user-snowflake`) |
| HubSpot MCP | HubSpot skills | ✅ Available (`user-hubspot`) |
| PyYAML | Skill parsing | ✅ In requirements.txt |
| Snowflake credentials | Live queries | ⚠️ Env vars needed |
| HubSpot PAT | API access | ⚠️ Env vars needed |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Hardcoded Flowcode pipeline IDs | Skills won't work for other clients | Parameterize IDs |
| CHURN_REASON mostly NULL | Churn prediction unreliable | Use health status transitions |
| F1 events in Databricks | Limited event data (302 F2 orgs) | Document limitation |
| No rate limiting | HubSpot API blocking | Implement rate limiter |
| Demo mode fallback | Stale data in development | Clear DEMO_MODE flag |

---

## Recommended First Action

Start with **Phase 1** skills that wrap existing, verified queries:

```bash
# Create first skill
mkdir -p skills/snowflake-discovery
# Use SKILL.md template with Flowcode queries
```

These skills can be created immediately with low effort and high value.
