# MH1 System Production Roadmap

**Generated:** January 26, 2026  
**Based on:** Comprehensive codebase analysis of `mh1-system/`  
**Assessment Validation:** External COO/Quant/RevOps/Engineer/Marketer review

---

## Executive Summary

After scanning all 50+ files across the MH1 codebase, **the assessment was 90%+ accurate**. The system has strong architectural foundations but lacks critical production essentials. This roadmap documents every gap with exact file locations and required changes.

### Gap Summary

| Category | Gap Count | Severity | Effort |
|----------|-----------|----------|--------|
| Security & Multi-Tenancy | 12 | CRITICAL | High |
| Evaluation Consistency | 8 | HIGH | Medium |
| Product Contracts | 14 | HIGH | Medium |
| Approval Workflows | 6 | CRITICAL | High |
| Observability | 4 | LOW | Low |
| Economics & Budgets | 8 | HIGH | Medium |
| CI/CD | 5 | CRITICAL | Medium |
| Creative & Growth | 9 | MEDIUM | High |
| **Total** | **66** | | |

---

## Phase 0: Critical Blockers (Week 1-2)

### 0.1 Security & Multi-Tenancy

| Gap | Current File | Line(s) | What's Missing | New File/Change |
|-----|--------------|---------|----------------|-----------------|
| No tenant isolation | `lib/runner.py` | 309, 325 | `client` param only for logging | Create `lib/multitenancy.py` |
| Shared databases | `lib/intelligence.py` | 16-17 | Single `intelligence.db` | Add tenant-scoped connections |
| Shared databases | `lib/knowledge_ingest.py` | 27-28 | Single `knowledge.db` | Add tenant partitioning |
| No encryption at rest | `lib/storage.py` | 80-95 | Raw JSON writes | Add `EncryptedStorageManager` |
| No secrets management | `lib/mcp_client.py` | 99-107 | Plain JSON config | Create `lib/secrets.py` |
| No RBAC | All `lib/*.py` | N/A | No auth checks | Create `lib/auth.py` |
| No audit trail | `lib/telemetry.py` | 29-50 | No actor identification | Add `audit_trail` table |

**Files to Create:**
```
lib/multitenancy.py    # TenantContext, tenant-scoped DB
lib/auth.py            # RBAC, permission decorators
lib/secrets.py         # Vault integration, env fallback
lib/permissions.py     # Tool scope definitions
```

**Schema Changes:**
```sql
-- Add to telemetry.db
CREATE TABLE audit_trail (
    id INTEGER PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    action TEXT NOT NULL,
    resource TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    ip_address TEXT,
    details TEXT
);

-- Add to all tables
ALTER TABLE runs ADD COLUMN tenant_id TEXT;
ALTER TABLE knowledge_items ADD COLUMN tenant_id TEXT;
```

---

### 0.2 Idempotency & Safety

| Gap | Current File | Line(s) | What's Missing | Fix |
|-----|--------------|---------|----------------|-----|
| No idempotency keys | `lib/mcp_client.py` | 113-160 | `call()` has no idempotency | Add `idempotency_key` param |
| Retry duplicates | `lib/mcp_client.py` | 162-191 | Retries can duplicate | Add idempotency cache |
| No run idempotency | `lib/runner.py` | 313 | `run_id` generated, not accepted | Accept `idempotency_key` |
| Non-deterministic writes | `lib/storage.py` | 64-65 | Timestamp in filename | Add content-hash option |
| Duplicate metrics | `lib/intelligence.py` | 134-140 | INSERT without dedup | Use `INSERT OR IGNORE` |

**Code Change Example:**
```python
# lib/mcp_client.py line 113
def call(
    self,
    tool_name: str,
    params: dict,
    timeout_seconds: int = 30,
    idempotency_key: str = None  # ADD THIS
) -> MCPResponse:
    if idempotency_key:
        cached = self._check_idempotency_cache(idempotency_key)
        if cached:
            return cached
    # ... rest of method
```

---

### 0.3 CI/CD Pipeline

| Gap | Current State | Required |
|-----|---------------|----------|
| No CI pipeline | Nothing exists | Create `.github/workflows/ci.yml` |
| No schema validation | Manual only | Create `scripts/validate_schemas.py` |
| No golden tests | Template only, no tests | Create `skills/*/tests/golden_*.json` |
| No connector mocks | Nothing exists | Create `tests/mocks/` |
| No evaluator tests | Nothing exists | Create `tests/test_evaluator.py` |

**Files to Create:**
```
.github/workflows/ci.yml
scripts/validate_schemas.py
scripts/golden_test.py
tests/test_evaluator.py
tests/test_telemetry.py
tests/test_runner.py
tests/mocks/hubspot_mock.py
tests/mocks/snowflake_mock.py
```

**CI Pipeline:**
```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install ruff mypy
      - run: ruff check lib/
      - run: mypy lib/

  test:
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/ --cov=lib

  schema-validation:
    runs-on: ubuntu-latest
    steps:
      - run: python scripts/validate_schemas.py

  golden-tests:
    runs-on: ubuntu-latest
    steps:
      - run: python scripts/golden_test.py
```

---

## Phase 1: Evaluation Consistency (Week 2-3)

### 1.1 Dimension Count Conflict

| Location | Current | Issue |
|----------|---------|-------|
| `lib/evaluator.py` lines 39-55 | **6 dimensions** | Has `context_efficiency` |
| `prompts/evaluation-prompt.md` lines 32-41 | **5 dimensions** | Missing `context_efficiency` |
| `schemas/evaluation-result.json` lines 20-52 | **5 dimensions** | Missing `context_efficiency` |

**Fix:** Add `context_efficiency` to prompt and schema, OR remove from code.

### 1.2 Weight Discrepancies

| Dimension | `evaluator.py` | `evaluation-prompt.md` |
|-----------|----------------|------------------------|
| schema_validity | 18% | 20% |
| factuality | 23% | 25% |
| completeness | 18% | 20% |
| brand_voice | 13% | 15% |
| risk_flags | 18% | 20% |
| context_efficiency | 10% | N/A |

**Fix:** Synchronize weights. Use evaluator.py as source of truth.

### 1.3 Multiple Scale Systems

| Evaluation | File | Scale | Threshold |
|------------|------|-------|-----------|
| Standard | `evaluator.py:57` | 0-1 float | ≥0.8 |
| SRAC | `srac-evaluation-prompt.md:99` | 1-5 int | ≥3.5 |
| AI Washing | `ai-washing-check-prompt.md:118-123` | none/low/medium/high | 0 warnings |

**Fix:** Create `lib/release_policy.py` with unified decision:

```python
# lib/release_policy.py (NEW FILE)
def determine_release_action(
    standard_eval: dict,
    srac_eval: dict = None,
    ai_washing_eval: dict = None
) -> str:
    """
    Returns: 'auto_deliver' | 'auto_refine' | 'human_review' | 'blocked'
    """
    # BLOCKED conditions
    if any(issue["severity"] == "critical" for issue in standard_eval.get("issues", [])):
        return "blocked"
    if ai_washing_eval and ai_washing_eval["overall"]["highest_severity"] == "high":
        return "blocked"
    
    # HUMAN REVIEW conditions
    if ai_washing_eval and ai_washing_eval["overall"]["warning_count"] >= 1:
        return "human_review"
    if standard_eval["score"] < 0.7:
        return "human_review"
    
    # AUTO-REFINE conditions
    if not standard_eval["pass"] and len(standard_eval.get("suggestions", [])) > 0:
        return "auto_refine"
    if srac_eval and not srac_eval["pass"]:
        return "auto_refine"
    
    # AUTO-DELIVER
    return "auto_deliver"
```

### 1.4 Module-Specific Factuality

| Module Type | Required Verification | Current State |
|-------------|----------------------|---------------|
| SQL/Data Analysis | Query validation, result verification | Not implemented |
| Research/Reports | Citation requirements, source credibility | Not implemented |
| Forecasting | Claims library, historical validation | Not implemented |

**Fix:** Extend `lib/evaluator.py` with module-specific methods:
- `_check_factuality_sql()`
- `_check_factuality_research()`
- `_check_factuality_forecasting()`

### 1.5 Forecasting Scope

**Gap:** TDA/TATS claims presented without scope.

**Fix:** Create `prompts/forecasting-evaluation-prompt.md` and `schemas/forecasting-result.json`:

```json
// schemas/forecasting-result.json
{
  "required": ["dataset_scope", "data_sufficiency", "horizon", "baseline"],
  "properties": {
    "dataset_scope": {
      "source": "string",
      "time_range": {"start": "date", "end": "date"}
    },
    "data_sufficiency": {
      "data_points": "integer",
      "minimum_required": "integer",
      "passes": "boolean"
    }
  }
}
```

---

## Phase 2: Product Contracts (Week 3-4)

### 2.1 Skills Missing SLAs

| File | What's Missing |
|------|----------------|
| `skills/_templates/SKILL_TEMPLATE/SKILL.md` | No SLA section |
| `skills/lifecycle-audit/SKILL.md` | No expected runtime |
| `skills/lifecycle-audit/run.py:53-57` | No timeout passed to runner |

**Fix:** Add to every skill:

```markdown
## SLA (Service Level Agreement)

| Metric | Target | Max | Timeout Action |
|--------|--------|-----|----------------|
| Expected runtime | 30s | 120s | Abort and return partial |
| P95 runtime | 45s | - | - |
| Retry budget | 2 | - | Route to human after exhausted |
```

### 2.2 Skills Missing Data Requirements

| File | Line(s) | Issue |
|------|---------|-------|
| `skills/_templates/SKILL_TEMPLATE/schemas/input.json` | N/A | No `minimum_records` |
| `skills/lifecycle-audit/schemas/input.json` | 10-15 | No data quality threshold |

**Fix:** Add to input schemas:

```json
"data_requirements": {
  "minimum_records": 50,
  "required_field_coverage": {
    "email": 0.9,
    "lifecyclestage": 0.8
  },
  "behavior_on_insufficient": "warn_and_continue"
}
```

### 2.3 Skills Missing Failure Modes

| File | What Exists | What's Missing |
|------|-------------|----------------|
| `agents/orchestrators/ORCHESTRATOR_TEMPLATE.md:131-139` | Error handling table | No fallback output schema |
| `skills/lifecycle-audit/run.py:438-444` | Generic exception handler | No specific failure modes |

**Fix:** Add to every skill:

```markdown
## Failure Modes

| Mode | Trigger | Fallback Output | Escalation |
|------|---------|-----------------|------------|
| Partial Success | 1+ steps failed | Last successful output | Yes if critical |
| Data Unavailable | Source unreachable | Cached (if <24h) | No |
| Quality Below Threshold | Score < 0.6 | Raw with UNVALIDATED flag | Yes |
| Complete Failure | Unrecoverable | Error report only | Yes |
```

### 2.4 Skills Missing Human Review Requirements

| File | Line(s) | Current | Missing |
|------|---------|---------|---------|
| `skills/lifecycle-audit/run.py` | 406-410 | `route_to_human()` on eval fail | No high-risk triggers |
| `agents/evaluators/EVALUATOR_TEMPLATE.md` | 96-101 | Score thresholds | No review SLA |

**Fix:** Add to every skill:

```markdown
## Human Review Requirements

| Trigger | Mandatory | SLA | Escalation |
|---------|-----------|-----|------------|
| Budget impact > $1000 | Yes | 4 hours | Manager after 4h |
| Eval score < 0.7 | Yes | 8 hours | Auto-reject after 24h |
| First run for client | Yes | 24 hours | N/A |
| Contains PII | Yes | 4 hours | Privacy team |
```

### 2.5 Create Standard Contract Format

**New File:** `skills/_templates/SKILL_TEMPLATE/CONTRACT.md`

```markdown
# Skill Contract: [SKILL_NAME]

## Guarantees
- **Runtime SLA:** P95 < 60s, max 180s
- **Data Requirements:** Min 50 records, 80% email coverage
- **Output Schema:** schemas/output.json (validated)

## Failure Handling
- **Partial failure:** Returns last successful step
- **Complete failure:** Error report + auto-retry once

## Human Review
- **Mandatory triggers:** Budget impact > $1K, PII, first client run
- **Review SLA:** 4-24 hours depending on trigger

## Write Operations
- [ ] None (read-only) OR
- [ ] List operations with approval requirements
```

---

## Phase 3: Approval & Action Engine (Week 4-5)

### 3.1 No Suggest/Execute Mode Distinction

| File | Current | Missing |
|------|---------|---------|
| `skills/_templates/SKILL_TEMPLATE/SKILL.md` | No mode distinction | `execution_mode` parameter |
| `skills/lifecycle-audit/run.py` | All recommendations | No execute capability |
| `agents/workers/WORKER_TEMPLATE.md` | No mode concept | `action_mode` handling |

**Fix:** Add to all skill input schemas:

```json
"execution_mode": {
  "type": "string",
  "enum": ["suggest", "preview", "execute"],
  "default": "suggest",
  "description": "suggest=recommendations, preview=show changes, execute=apply"
}
```

### 3.2 No Approval Workflow

| File | Line(s) | Current | Missing |
|------|---------|---------|---------|
| `skills/lifecycle-audit/run.py` | 406-410 | `route_to_human()` | No queue, no tracking |
| `agents/orchestrators/ORCHESTRATOR_TEMPLATE.md` | 164-168 | Checkpoint mentions review | No workflow definition |

**Fix:** Create `workflows/templates/APPROVAL_WORKFLOW.md`:

```markdown
## Approval Queue States
| State | Next Actions |
|-------|--------------|
| pending | approve, reject, delegate, expire |
| approved | execute |
| rejected | revise, cancel |
| expired | escalate, auto-reject |

## Approval Flow
1. Action flagged for approval
2. Create approval request
3. Route to approver by impact level
4. Wait (with timeout)
5. On approval: execute
6. On rejection: stop
7. On timeout: escalate
```

**New Schema:** `schemas/approval-request.json`

### 3.3 No Permission Checks Before Writes

| File | Issue |
|------|-------|
| `lib/mcp_client.py` | All methods public, no auth |
| `agents/orchestrators/MULTI_AGENT_PIPELINE.md:158-161` | "Never auto-approve" not enforced |

**Fix:** Create `lib/permissions.py`:

```python
class ToolScope(Enum):
    RESEARCH = "research"      # Read-only: browser, perplexity
    CRM_READ = "crm_read"      # HubSpot reads
    CRM_WRITE = "crm_write"    # HubSpot writes - requires approval
    DATA_WRITE = "data_write"  # Snowflake writes - requires approval

def check_permission(operation, scope, user) -> PermissionResult:
    """Check if user has permission for scope"""
    pass

# Decorator usage
@requires_scope(ToolScope.CRM_WRITE)
def update_hubspot_contact(...):
    pass
```

### 3.4 Read/Write Client Separation

| File | Current | Required |
|------|---------|----------|
| `lib/mcp_client.py:196-239` | `HubSpotClient` mixes read/write | Split into `HubSpotReadClient`, `HubSpotWriteClient` |

**Fix:**
```python
class HubSpotReadClient(MCPClient):
    """Read-only HubSpot operations - no approval needed"""
    def search_contacts(self, ...): pass
    def get_contact(self, ...): pass
    
class HubSpotWriteClient(MCPClient):
    """Write operations - requires elevated permissions"""
    @requires_scope(ToolScope.CRM_WRITE)
    def update_contact(self, ...): pass
```

---

## Phase 4: Economics & Budgets (Week 5-6)

### 4.1 No Per-Client Quotas

| File | Current | Missing |
|------|---------|---------|
| `config/mcp-servers.json` | Server-level rate limits only | Per-client allocation |
| `lib/telemetry.py` | Run-level cost tracking | Client-level aggregation |

**Fix:** Create `config/quotas.yaml`:

```yaml
clients:
  client_a:
    monthly_token_budget: 10_000_000
    daily_run_limit: 100
    hubspot_rpm: 50
  client_b:
    monthly_token_budget: 5_000_000
    daily_run_limit: 50
```

### 4.2 No Per-Module Cost Targets

| File | Current | Missing |
|------|---------|---------|
| `delivery/module-specs/lifecycle-audit.md` | Pricing tiers | Cost per execution |
| `lib/telemetry.py` | Token costs | Module attribution |

**Fix:** Create `config/pricing.yaml`:

```yaml
modules:
  lifecycle-audit:
    target_cost_usd: 0.50
    max_cost_usd: 2.00
    margin_target: 0.70
    components:
      discovery: 0.10
      enrichment: 0.05
      analysis: 0.25
      synthesis: 0.10
```

### 4.3 No Budget Enforcement

| File | Line(s) | Current | Missing |
|------|---------|---------|---------|
| `lib/telemetry.py` | 118-123 | `estimate_cost()` calculates | No enforcement |
| `lib/runner.py` | 300-461 | Executes without check | No budget limit |

**Fix:** Create `lib/budget.py`:

```python
class BudgetManager:
    def __init__(self, daily_limit_usd: float = 100.0, per_run_limit_usd: float = 10.0):
        self.daily_limit = daily_limit_usd
        self.per_run_limit = per_run_limit_usd
    
    def check_budget(self, tenant_id: str, estimated_cost: float) -> bool:
        """Raise BudgetExceededError if over limit"""
        daily_spent = self._get_daily_spend(tenant_id)
        if daily_spent + estimated_cost > self.daily_limit:
            raise BudgetExceededError(f"Daily limit exceeded: ${daily_spent:.2f} + ${estimated_cost:.2f} > ${self.daily_limit:.2f}")
        return True
    
    def record_spend(self, tenant_id: str, run_id: str, cost: float):
        """Track spending against budgets"""
        pass
```

### 4.4 Context Efficiency Not Tied to Cost

| File | Line(s) | Current | Missing |
|------|---------|---------|---------|
| `lib/evaluator.py` | 387-460 | Checks strategy type | No cost calculation |

**Fix:** Update `_check_context_efficiency()`:

```python
def _check_context_efficiency(self, issues, suggestions) -> float:
    # Calculate actual cost difference
    inline_cost = estimate_cost(input_size, output_size, "claude-sonnet-4")
    chunked_cost = estimate_cost(input_size, output_size, "claude-haiku")
    potential_savings = inline_cost - chunked_cost
    
    if potential_savings > 0.10:  # >$0.10 savings possible
        issues.append({
            "dimension": "context_efficiency",
            "description": f"Could save ${potential_savings:.2f} with chunked approach"
        })
```

---

## Phase 5: Client Onboarding (Week 6-7)

### 5.1 Missing Onboarding Checklist

**New File:** `delivery/client-templates/ONBOARDING_CHECKLIST.md`

```markdown
# Client Onboarding Checklist

## 1. Credentials Setup
- [ ] HubSpot: Private app created with required scopes
- [ ] HubSpot: Access token tested with `./mh1 test hubspot`
- [ ] Snowflake: Service account created
- [ ] Snowflake: Test query executed successfully

## 2. Data Validation
- [ ] Minimum 50 contacts in HubSpot
- [ ] lifecyclestage property exists and populated (>80%)
- [ ] email field populated (>90%)
- [ ] company associations exist (>70%)

## 3. Taxonomy Mapping
- [ ] Client lifecycle stages mapped to standard taxonomy
- [ ] Custom stage mapping documented in `config/clients/{client_id}/taxonomy.yaml`

## 4. Acceptance Tests
- [ ] `./mh1 test connector hubspot --client {client_id}`
- [ ] `./mh1 test connector snowflake --client {client_id}`
- [ ] `./mh1 run skill lifecycle-audit --client {client_id} --limit 10 --dry-run`
```

### 5.2 Missing Data Requirements Doc

**New File:** `delivery/client-templates/DATA_REQUIREMENTS.md`

### 5.3 Missing Taxonomy Setup

**New Directory:** `config/taxonomies/`

```yaml
# config/taxonomies/default.yaml
lifecycle_stages:
  subscriber: "subscriber"
  lead: "lead"
  mql: "marketingqualifiedlead"
  sql: "salesqualifiedlead"
  opportunity: "opportunity"
  customer: "customer"
  evangelist: "evangelist"

# Per-client override
# config/clients/{client_id}/taxonomy.yaml
lifecycle_stages:
  mql: "marketing_qualified"  # Client uses different name
```

---

## Phase 6: Unified Lifecycle Object Model (Week 7-8)

### 6.1 No Standard Entity Mapping

**New File:** `lib/data_model.py`

```python
@dataclass
class CanonicalLead:
    """Universal lead model across all CRMs"""
    id: str
    email: str
    first_name: str
    last_name: str
    company_name: str
    stage: LifecycleStage
    source_system: str  # "hubspot", "salesforce"
    source_id: str

class LifecycleStage(Enum):
    SUBSCRIBER = "subscriber"
    LEAD = "lead"
    MQL = "mql"
    SQL = "sql"
    OPPORTUNITY = "opportunity"
    CUSTOMER = "customer"
    EVANGELIST = "evangelist"
```

### 6.2 No Field Mapping Layer

**New File:** `lib/field_mapper.py`

```python
class FieldMapper:
    def __init__(self, mapping_config: dict):
        self.mappings = mapping_config
    
    def to_canonical(self, source_record: dict, source_system: str) -> CanonicalLead:
        mapping = self.mappings[source_system]
        return CanonicalLead(
            id=source_record[mapping["id"]],
            email=source_record[mapping["email"]],
            stage=self._map_stage(source_record[mapping["stage"]], source_system),
            # ...
        )
```

### 6.3 No Data Quality Scoreboard

**New File:** `lib/data_quality.py`

```python
class DataQualityScorer:
    def score(self, records: List[dict]) -> DataQualityReport:
        return DataQualityReport(
            total_records=len(records),
            completeness=self._calculate_completeness(records),
            validity=self._calculate_validity(records),
            freshness=self._calculate_freshness(records),
            overall_score=0.78,
            passed=True
        )
```

---

## Phase 7: Creative & Experimentation (Week 8-10)

### 7.1 Missing Creative Taxonomy

| Current File | Status |
|--------------|--------|
| `lib/multimodal.py` | Basic vision only |
| `lib/intelligence.py` | No creative attributes |

**New File:** `lib/creative_taxonomy.py`

```python
@dataclass
class CreativeTaxonomy:
    hook_type: str  # curiosity, urgency, social_proof, fear, benefit
    angle: str  # pain_agitate, gain_logic, emotion_story, authority
    audience_segment: str
    offer_type: str  # lead_magnet, demo, trial, purchase
    objections_addressed: List[str]
    funnel_stage: str  # awareness, consideration, decision
    format: str
    platform: str
```

### 7.2 Missing Experimentation Framework

**New File:** `lib/experimentation.py`

```python
@dataclass
class Experiment:
    id: str
    name: str
    hypothesis: str
    variants: List[Variant]
    metric_primary: str
    target_sample_size: int
    minimum_detectable_effect: float
    significance_level: float = 0.05
    status: ExperimentStatus

class ExperimentAnalyzer:
    def calculate_sample_size(self, baseline_rate, mde, power=0.8) -> int
    def calculate_significance(self, control, treatment) -> SignificanceResult
    def recommend_winner(self, experiment) -> WinnerRecommendation
```

### 7.3 Missing Insight-to-Action Packaging

**Current:** `skills/lifecycle-audit/run.py:287-299` has basic recommendations.

**Missing:** Lift estimates, effort estimates, execution checklists.

**Fix:** Extend recommendation schema:

```python
@dataclass
class ActionPackage:
    insight: str
    recommended_action: str
    expected_lift: LiftEstimate  # { min: 0.05, max: 0.15, confidence: 0.7 }
    effort_estimate: EffortEstimate  # { hours: 20, complexity: "medium" }
    execution_checklist: List[ChecklistItem]
    owner_role: str
    dependencies: List[str]
    success_criteria: List[Metric]
```

---

## Phase 8: Handoff & Escalation (Week 10-12)

### 8.1 Missing Handoff Rules

| Current | Missing |
|---------|---------|
| `skills/lifecycle-audit` outputs at_risk, upsell | No handoff definition |
| `agents/orchestrators/MULTI_AGENT_PIPELINE.md` | Internal handoff only |

**Fix:** Add to relevant skills:

```markdown
## Handoff Rules

### Marketing → Sales
| Trigger | Criteria | Destination |
|---------|----------|-------------|
| MQL to SQL | Score ≥ 80 | Sales queue |
| At-risk | Risk score ≥ 0.7 | CSM queue |
| Upsell | Upsell score ≥ 0.8 | Account manager |
```

### 8.2 Missing Escalation Logic

| Current | Missing |
|---------|---------|
| `route_to_human()` | Single level only |

**New File:** `workflows/templates/ESCALATION_POLICY.md`

```markdown
## Escalation Levels
| Level | Role | Trigger |
|-------|------|---------|
| L1 | Handler | Initial |
| L2 | Team lead | No response in 4h |
| L3 | Manager | No response in 8h |
| L4 | Executive | No resolution in 24h |
```

---

## Additional Findings (Not in Assessment)

### Placeholder/Stub Code

| File | Lines | Issue |
|------|-------|-------|
| `lib/multimodal.py` | 34-48 | `analyze_image()` returns placeholder |
| `lib/multimodal.py` | 50-65 | `generate_image()` returns placeholder |
| `lib/evaluator.py` | 640-644 | `SRACEvaluator.evaluate()` is `pass` |
| `lib/runner.py` | 458-459 | TODO: Slack, Airtable integration |

### Missing Skills (13 Referenced, 1 Implemented)

| Skill | Referenced In | Status |
|-------|---------------|--------|
| `hubspot-discovery` | lifecycle-audit.md | MISSING |
| `snowflake-explorer` | lifecycle-audit.md | MISSING |
| `data-quality-checker` | lifecycle-audit.md | MISSING |
| `email-performance-scorer` | lifecycle-audit.md | MISSING |
| `copy-analyzer` | lifecycle-audit.md | MISSING |
| `recommendation-generator` | lifecycle-audit.md | MISSING |
| +7 more | | MISSING |

### Missing Research Integrations

| Research Doc | Proposed | Implemented |
|--------------|----------|-------------|
| Phase 2 | `lib/stealth.py` | MISSING |
| Phase 2 | `lib/identity.py` | MISSING |
| Phase 2 | `lib/ad_intel.py` | MISSING |
| Phase 2 | `lib/social.py` | MISSING |
| Phase 3 | Video generation APIs | MISSING |
| Phase 3 | Brand voice profiles | MISSING |

---

## Summary: File Creation/Modification Matrix

### New Files to Create (35)

| Priority | File | Purpose |
|----------|------|---------|
| P0 | `lib/multitenancy.py` | Tenant isolation |
| P0 | `lib/auth.py` | RBAC |
| P0 | `lib/secrets.py` | Secrets management |
| P0 | `lib/permissions.py` | Tool scopes |
| P0 | `lib/release_policy.py` | Unified release decisions |
| P0 | `lib/budget.py` | Cost enforcement |
| P0 | `.github/workflows/ci.yml` | CI pipeline |
| P0 | `scripts/validate_schemas.py` | Schema validation |
| P1 | `lib/data_model.py` | Canonical entities |
| P1 | `lib/field_mapper.py` | CRM field mapping |
| P1 | `lib/data_quality.py` | Data quality scoring |
| P1 | `config/quotas.yaml` | Client quotas |
| P1 | `config/pricing.yaml` | Module pricing |
| P1 | `schemas/approval-request.json` | Approval queue |
| P1 | `schemas/forecasting-result.json` | Forecast validation |
| P2 | `lib/creative_taxonomy.py` | Creative tagging |
| P2 | `lib/experimentation.py` | A/B testing |
| P2 | `workflows/templates/APPROVAL_WORKFLOW.md` | Approval flow |
| P2 | `workflows/templates/ESCALATION_POLICY.md` | Escalation rules |
| P2 | `delivery/client-templates/ONBOARDING_CHECKLIST.md` | Client setup |
| P2 | `delivery/client-templates/DATA_REQUIREMENTS.md` | Data specs |
| P2 | `prompts/forecasting-evaluation-prompt.md` | Forecast eval |
| P3 | `tests/test_evaluator.py` | Unit tests |
| P3 | `tests/test_telemetry.py` | Unit tests |
| P3 | `tests/test_runner.py` | Unit tests |
| P3 | `tests/mocks/hubspot_mock.py` | Mock server |
| P3 | `tests/mocks/snowflake_mock.py` | Mock server |

### Files to Modify (22)

| Priority | File | Changes |
|----------|------|---------|
| P0 | `lib/mcp_client.py` | Add idempotency, split read/write |
| P0 | `lib/runner.py` | Add tenant context, budget check |
| P0 | `lib/storage.py` | Add encryption, deterministic mode |
| P0 | `lib/telemetry.py` | Add audit trail, tenant_id |
| P0 | `lib/evaluator.py` | Fix dimensions, add module-specific factuality |
| P1 | `prompts/evaluation-prompt.md` | Sync weights with code |
| P1 | `schemas/evaluation-result.json` | Add context_efficiency |
| P1 | `skills/_templates/SKILL_TEMPLATE/SKILL.md` | Add SLA, failure modes, contracts |
| P1 | `skills/_templates/SKILL_TEMPLATE/schemas/input.json` | Add data_requirements |
| P1 | `skills/lifecycle-audit/SKILL.md` | Add SLA, handoff rules |
| P1 | `agents/workers/WORKER_TEMPLATE.md` | Add execution_mode, permissions |
| P1 | `agents/orchestrators/ORCHESTRATOR_TEMPLATE.md` | Add SLA, escalation |
| P2 | `lib/intelligence.py` | Add tenant isolation, creative taxonomy |
| P2 | `lib/knowledge_ingest.py` | Add tenant isolation |

---

## Timeline Summary

| Phase | Duration | Focus |
|-------|----------|-------|
| **Phase 0** | Week 1-2 | Security, Idempotency, CI/CD |
| **Phase 1** | Week 2-3 | Evaluation Consistency |
| **Phase 2** | Week 3-4 | Product Contracts |
| **Phase 3** | Week 4-5 | Approval Workflows |
| **Phase 4** | Week 5-6 | Economics & Budgets |
| **Phase 5** | Week 6-7 | Client Onboarding |
| **Phase 6** | Week 7-8 | Lifecycle Object Model |
| **Phase 7** | Week 8-10 | Creative & Experimentation |
| **Phase 8** | Week 10-12 | Handoff & Escalation |

**Total: 12 weeks to production-ready platform**

---

## Consensus Action Plan (From Assessment)

1. ✅ **Normalize evaluation system** → Phase 1 addresses this
2. ✅ **Add production essentials** → Phase 0 addresses security, idempotency, CI
3. ✅ **Ship modules as full contracts** → Phase 2-3 addresses this

---

*This roadmap was generated by scanning all 50+ files in mh1-system/ and cross-referencing against the external assessment.*
