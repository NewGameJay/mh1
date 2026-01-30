# MRD Execution Plan

**Generated**: 2026-01-28
**Orchestrator**: skill-development-from-mrd.md
**Status**: Ready for Execution

---

## Summary

| Metric | Value |
|--------|-------|
| Total MRDs Analyzed | 3 |
| Active MRDs | 2 |
| Superseded MRDs | 1 (MRD #1 Original) |
| Total Requirements | 12 |
| Requirements with ≥70% Match | 10 (83%) |
| New Skills Created | 2 |

---

## Phase 1: Analysis Complete

All MRDs have been analyzed and requirements mapped to existing skills:

- **MRD #1 Original (FFC - Product Packaging)**: SUPERSEDED - Skip
- **MRD #1 v2 (FFC - ICP Research)**: 6 requirements identified
- **MRD #2 (Flowcode - Lifecycle Marketing)**: 6 requirements identified

Full analysis available in: `MRD_ANALYSIS_SUMMARY.yaml`

---

## Phase 2: Execute Existing Skills

The following skills should be executed for each active MRD:

### Flowcode (MRD #2) - Priority: High

| Requirement | Skill | Match | Config |
|-------------|-------|-------|--------|
| FC-REQ-001: Data Audit | `crm-discovery` | 95% | `crm.type: hubspot` |
| FC-REQ-001: Data Audit | `data-warehouse-discovery` | 95% | `warehouse.type: snowflake` |
| FC-REQ-001: Data Audit | `data-quality-audit` | 90% | Standard config |
| FC-REQ-002: Lifecycle Audit | `lifecycle-audit` | 98% | `tenant_id: flowcode` |
| FC-REQ-003: Segmentation | `cohort-email-builder` | 80% | Segmentation rules |
| FC-REQ-003: Segmentation | `at-risk-detection` | 75% | Health thresholds |
| FC-REQ-004: Prototype Flow | `playbook-executor` | 70% | Custom playbook |
| FC-REQ-004: Prototype Flow | `cohort-email-builder` | 75% | Reason codes |
| FC-REQ-005: AI Personalization | `email-copy-generator` | 80% | Personalization enabled |
| FC-REQ-006: F1→F2 Migration | `cohort-email-builder` | 85% | CONVERSION reason code |
| FC-REQ-006: F1→F2 Migration | `upsell-candidates` | 80% | Product: F2 |

**Recommended Execution Order (Flowcode):**
1. `crm-discovery` + `data-warehouse-discovery` (parallel)
2. `data-quality-audit`
3. `lifecycle-audit`
4. `at-risk-detection`
5. `cohort-email-builder` with segmentation
6. `upsell-candidates`
7. `email-copy-generator`

### FFC (MRD #1 v2) - Priority: High

| Requirement | Skill | Match | Config |
|-------------|-------|-------|--------|
| FFC-REQ-001: Customer Research | `generate-interview-questions` | 85% | `client_id: ffc` |
| FFC-REQ-001: Customer Research | `incorporate-interview-results` | 75% | After interviews |
| FFC-REQ-002: Retention Analysis | `at-risk-detection` | 90% | HubSpot config |
| FFC-REQ-002: Retention Analysis | `churn-prediction` | 85% | `days_threshold: 30` |
| FFC-REQ-002: Retention Analysis | `dormant-detection` | 75% | Optional |
| FFC-REQ-003: ICP Documentation | `extract-audience-persona` | 70% | Interview transcripts |
| FFC-REQ-004: Positioning Matrix | **NEW: `product-positioning-matrix`** | - | In skills-staging/ |
| FFC-REQ-005: Newsletter Automation | `cohort-email-builder` | 75% | Newsletter cohort |
| FFC-REQ-005: Newsletter Automation | `email-copy-generator` | 70% | Newsletter templates |
| FFC-REQ-006: ManyChat Audit | **NEW: `manychat-audit`** | - | In skills-staging/ |

**Recommended Execution Order (FFC):**
1. `generate-interview-questions`
2. [Conduct 10-15 interviews]
3. `incorporate-interview-results`
4. `at-risk-detection` + `churn-prediction` (parallel)
5. `extract-audience-persona`
6. `product-positioning-matrix` (from skills-staging/)
7. `cohort-email-builder` + `email-copy-generator`
8. `manychat-audit` (from skills-staging/)

---

## Phase 3: New Skills Created

Two new skills have been created in `skills-staging/`:

### 1. product-positioning-matrix

**Location**: `skills-staging/product-positioning-matrix/SKILL.md`
**Purpose**: Generate product positioning matrices for competitive differentiation
**Fulfills**: FFC-REQ-004 (Product Positioning Matrix)
**Status**: Experimental - Requires human review

**Key Features**:
- Multi-tier product positioning
- Competitive matrix generation
- Segment-to-tier mapping
- Sample messaging generation

**Dependencies**:
- `research-competitors` (recommended)
- `extract-audience-persona` (recommended)
- `extract-pov` (optional)

### 2. manychat-audit

**Location**: `skills-staging/manychat-audit/SKILL.md`
**Purpose**: Audit ManyChat flows for optimization opportunities
**Fulfills**: FFC-REQ-006 (ManyChat Audit)
**Status**: Experimental - Requires human review

**Key Features**:
- Flow performance analysis
- Subscriber engagement metrics
- Issue identification with severity
- Recommendation engine
- Browser automation fallback

**Dependencies**:
- ManyChat API access OR browser credentials

---

## Skill Execution Commands

### Flowcode Execution Sequence

```bash
# Step 1: Data Audit
mh1 run skill crm-discovery --client flowcode --crm.type hubspot
mh1 run skill data-warehouse-discovery --client flowcode --warehouse.type snowflake

# Step 2: Data Quality
mh1 run skill data-quality-audit --client flowcode

# Step 3: Lifecycle Audit
mh1 run skill lifecycle-audit --tenant_id flowcode --limit 1000 --execution_mode suggest

# Step 4: Retention Analysis
mh1 run skill at-risk-detection --client flowcode --data_source snowflake

# Step 5: Segmentation
mh1 run skill cohort-email-builder --client flowcode --cohort_type at_risk

# Step 6: Upsell Identification
mh1 run skill upsell-candidates --client flowcode

# Step 7: AI Personalization
mh1 run skill email-copy-generator --client flowcode --personalization true
```

### FFC Execution Sequence

```bash
# Step 1: Interview Prep
mh1 run skill generate-interview-questions --client_id ffc --include_voice_questions true

# [Conduct interviews - manual step]

# Step 2: Interview Analysis
mh1 run skill incorporate-interview-results --client_id ffc --source interview_transcripts

# Step 3: Retention Analysis
mh1 run skill at-risk-detection --client ffc --data_source hubspot
mh1 run skill churn-prediction --client ffc --days_threshold 30

# Step 4: Persona Extraction
mh1 run skill extract-audience-persona --client_id ffc --source interviews

# Step 5: Positioning Matrix (from staging)
mh1 run skill-staging/product-positioning-matrix --client_id ffc

# Step 6: Newsletter Automation
mh1 run skill cohort-email-builder --client ffc --cohort_type newsletter_subscriber

# Step 7: ManyChat Audit (from staging)
mh1 run skill-staging/manychat-audit --client_id ffc
```

---

## Gaps and Workarounds

### Heap Integration (FC-REQ-001)
- **Gap**: Heap not yet in `data-warehouse-discovery`
- **Workaround**: Heap provides a Postgres-compatible SQL interface. Use `data-warehouse-discovery` with `warehouse.type: postgresql` pointed at Heap's SQL endpoint.

### HubSpot Workflow Creation (FC-REQ-004)
- **Gap**: HubSpot workflow creation not fully automated
- **Workaround**: Use `cohort-email-builder` to generate lists and copy guidance, then manually create workflows in HubSpot UI.

### ManyChat API Access (FFC-REQ-006)
- **Gap**: May not have API credentials configured
- **Workaround**: `manychat-audit` skill includes browser automation fallback for when API is unavailable.

---

## Success Criteria

### Flowcode (MRD #2)
- [ ] Data quality report complete with remediation plan
- [ ] Lifecycle stages mapped with conversion rates
- [ ] 2-3 behavioral segments defined
- [ ] One prototype automation live
- [ ] F1→F2 migration playbook delivered

### FFC (MRD #1 v2)
- [ ] 10-15 customer interviews completed
- [ ] 2-3 ICP segments defined with behavioral criteria
- [ ] Retention cohort analysis complete
- [ ] Newsletter automation active in HubSpot
- [ ] Product positioning matrix documented
- [ ] ManyChat audit report delivered

---

## Next Steps

1. **Configure Client Integrations**
   - Verify HubSpot MCP access for both clients
   - Verify Snowflake MCP access for Flowcode
   - Configure ManyChat API token for FFC

2. **Execute Flowcode Skills** (Priority: Week 1)
   - Run data audit skills in parallel
   - Run lifecycle-audit
   - Generate segmentation and recommendations

3. **Execute FFC Skills** (Priority: Week 1-2)
   - Generate interview questions
   - Schedule and conduct interviews
   - Run retention analysis
   - Generate positioning matrix

4. **Validate New Skills**
   - Test `product-positioning-matrix` with FFC data
   - Test `manychat-audit` with FFC credentials
   - Review outputs and iterate if needed

5. **Promote Staging Skills**
   - If validation passes, move from `skills-staging/` to `skills/`
   - Update skill version to stable (remove "experimental" status)

---

## Files Created

| File | Purpose |
|------|---------|
| `.cursor/plans/MRDs/MRD_ANALYSIS_SUMMARY.yaml` | Full MRD analysis with skill matching matrix |
| `.cursor/plans/MRDs/EXECUTION_PLAN.md` | This execution plan |
| `skills-staging/product-positioning-matrix/SKILL.md` | New skill for positioning matrices |
| `skills-staging/manychat-audit/SKILL.md` | New skill for ManyChat audits |
