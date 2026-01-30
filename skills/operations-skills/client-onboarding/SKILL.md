---
name: client-onboarding
description: |
  Automated client onboarding that discovers tech stack, identifies capability gaps,
  generates required configurations, maps lifecycle stages, and creates custom skills as needed.
  Use when asked to 'onboard new client', 'setup client', 'configure for {company}',
  'analyze client tech stack', or 'map lifecycle stages'.
license: Proprietary
compatibility:
  - skill-builder
  - crm-discovery
  - data-warehouse-discovery
  - lifecycle-audit
  - cohort-retention-analysis
metadata:
  author: mh1-engineering
  version: "1.1.0"
  status: active
  estimated_runtime: "10-30min"
  max_cost: "$3.00"
  client_facing: true
  requires_human_review: true
  tags:
    - onboarding
    - client-setup
    - discovery
    - configuration
    - lifecycle
allowed-tools: Read Write WebSearch WebFetch Shell Grep Glob CallMcpTool Task
stages:
  - stages/02-lifecycle.md
---

# Client Onboarding Skill

Automated discovery and configuration system that prepares MH1 for any new client, regardless of their tech stack.

## When to Use

Use this skill when:
- Onboarding a new marketing agency client
- Setting up MH1 for a new business
- Client has platforms we don't currently support
- Need to audit and configure a client's full tech stack
- Need to map client's lifecycle stages for analysis

---

## Onboarding Process

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│  1. DISCOVER   │────▶│  2. ASSESS     │────▶│ 2.5 LIFECYCLE  │
│  Tech Stack    │     │  Capabilities  │     │   Mapping      │
└────────────────┘     └────────────────┘     └────────────────┘
                                                       │
         ┌─────────────────────────────────────────────┘
         │
         ▼
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│  3. CONFIGURE  │────▶│  4. GENERATE   │────▶│  5. DELIVER    │
│  Client        │     │  Missing Skills│     │  Report        │
└────────────────┘     └────────────────┘     └────────────────┘
```

**Phase 2.5: Lifecycle Mapping** — New phase that captures client's actual funnel stages and maps them to canonical lifecycle stages. See `stages/02-lifecycle.md` for details.

---

## Phase 1: Tech Stack Discovery

### Step 1.1: Client Intake Questionnaire

Ask the client (or analyze their environment) for:

```yaml
client_intake:
  company:
    name: "{company_name}"
    industry: "{industry}"  # SaaS, E-commerce, B2B Services, etc.
    size: "{employee_count}"
    
  crm:
    primary: "{crm_name}"
    secondary: "{optional_secondary_crm}"
    
  data_infrastructure:
    warehouse: "{warehouse_name}"
    analytics: "{analytics_platform}"
    cdp: "{cdp_if_any}"
    
  marketing_stack:
    email: "{email_platform}"
    automation: "{automation_platform}"
    social: "{social_management_tool}"
    ads: ["{ad_platform_1}", "{ad_platform_2}"]
    
  sales_tools:
    outreach: "{outreach_platform}"
    calling: "{calling_platform}"
    scheduling: "{scheduling_tool}"
    
  support:
    helpdesk: "{helpdesk_platform}"
    chat: "{chat_platform}"
    
  custom:
    - name: "{custom_system_1}"
      purpose: "{what_it_does}"
      has_api: true | false
```

### Step 1.2: Automated Discovery

If client provides credentials, automatically discover:

```python
discovery_steps = [
    # CRM Discovery
    {
        "platform": "crm",
        "skill": "crm-discovery",
        "output": "contacts, companies, deals, pipelines, custom objects"
    },
    
    # Data Warehouse Discovery
    {
        "platform": "warehouse", 
        "skill": "data-warehouse-discovery",
        "output": "schemas, tables, row counts, column types"
    },
    
    # Identity Mapping Check
    {
        "platform": "cross-platform",
        "skill": "identity-mapping",
        "output": "join keys, match rates, data gaps"
    }
]
```

---

## Phase 2: Capability Assessment

### Step 2.1: Platform Support Check

For each platform in client's stack, check support status:

```yaml
platform_support_matrix:
  # CRM
  - platform: "{client_crm}"
    category: "CRM"
    supported: true | false | partial
    skills_available:
      - "{skill_1}"
      - "{skill_2}"
    missing_capabilities:
      - "{capability_1}"
      
  # Data Warehouse
  - platform: "{client_warehouse}"
    category: "Data Warehouse"
    supported: true | false | partial
    skills_available:
      - "{skill_1}"
    missing_capabilities:
      - "{capability_1}"
      
  # Marketing
  - platform: "{client_marketing_platform}"
    category: "Marketing Automation"
    supported: true | false | partial
    action_required: "generate_new_skill" | "update_existing" | "none"
```

### Step 2.2: Gap Identification

Generate gap report:

```markdown
## Client: {company_name}
## Gap Analysis Report

### Fully Supported ✅
| Platform | Category | Skills Available |
|----------|----------|------------------|
| HubSpot | CRM | crm-discovery, pipeline-analysis, ... |
| Snowflake | Warehouse | data-warehouse-discovery, ... |

### Partially Supported ⚠️
| Platform | Category | Missing Features | Action |
|----------|----------|------------------|--------|
| {platform} | {category} | {features} | Update {skill} |

### Not Supported ❌
| Platform | Category | Priority | Action |
|----------|----------|----------|--------|
| {platform} | {category} | High | Generate new skill |
| {platform} | {category} | Medium | Generate new skill |

### Custom Systems 🔧
| System | Has API | Complexity | Recommendation |
|--------|---------|------------|----------------|
| {system} | Yes | Medium | Generate custom integration |
| {system} | No | N/A | Manual process or Zapier |
```

---

## Phase 3: Client Configuration

### Step 3.1: Generate Configuration Files

Create client-specific config directory:

```bash
mkdir -p clients/{client_id}/config
```

Generate `datasources.yaml`:

```yaml
# clients/{client_id}/config/datasources.yaml
# Auto-generated by client-onboarding skill
# Generated: {timestamp}

client:
  id: "{client_id}"
  name: "{company_name}"
  industry: "{industry}"

warehouse:
  type: "{warehouse_type}"  # snowflake, bigquery, etc.
  database: "{database_name}"
  schema: "{schema_name}"
  
  # Table mappings (discovered or configured)
  tables:
    customers: "{actual_customer_table}"
    events: "{actual_events_table}"
    health_scores: "{actual_health_table}"  # or null if not available
    
  # Field mappings
  field_mapping:
    account_id: "{actual_field}"
    customer_name: "{actual_field}"
    revenue: "{actual_field}"  # arr, mrr, or revenue
    health_score: "{actual_field}"  # or null
    owner: "{actual_field}"
    created_at: "{actual_field}"

crm:
  type: "{crm_type}"  # hubspot, salesforce, etc.
  
  # Pipeline configuration (discovered)
  pipelines:
    sales: "{sales_pipeline_id}"
    renewal: "{renewal_pipeline_id}"  # if applicable
    
  # Stage mappings
  stage_mapping:
    won: "{platform_won_value}"
    lost: "{platform_lost_value}"
    open: ["{stage_1}", "{stage_2}", "{stage_3}"]
    
  # Custom properties to use
  properties:
    health_status: "{custom_property_name}"
    tier: "{custom_property_name}"
    
thresholds:
  # Business-specific thresholds
  high_value_min: {amount}  # What counts as "high value"
  at_risk_score_max: {score}  # Health score threshold
  dormant_days: {days}  # Days without activity = dormant
  churn_lookback_days: {days}

# Additional platforms
marketing:
  type: "{marketing_platform}"
  # Platform-specific config...
  
support:
  type: "{support_platform}"
  # Platform-specific config...
```

### Step 3.2: Generate Semantic Layer

Copy and customize semantic layer:

```bash
cp -r config/semantic_layer/ clients/{client_id}/config/semantic_layer/
```

Customize for client's:
- Event types
- Lifecycle stages
- Industry-specific mappings

---

## Phase 4: Skill Generation (if needed)

### Step 4.1: Invoke Skill Builder

For unsupported platforms, invoke the skill-builder:

```yaml
skill_generation_queue:
  - platform: "{unsupported_platform_1}"
    priority: high
    type: new_skill
    template_base: "{similar_existing_skill}"
    
  - platform: "{unsupported_platform_2}"
    priority: medium
    type: update_existing
    skill_to_update: "{skill_name}"
    features_to_add:
      - "{feature_1}"
      - "{feature_2}"
```

### Step 4.2: Generate Custom Integrations

For custom systems with APIs:

```yaml
custom_integration:
  name: "{system_name}"
  api_docs: "{documentation_url}"
  
  # Analyzed endpoints
  endpoints:
    - path: "/api/v1/{resource}"
      method: "GET"
      use_case: "{what_we_need_it_for}"
      
  # Generated skill
  generated_skill: "skills/{client_id}-{system_name}/SKILL.md"
```

---

## Phase 5: Onboarding Report

### Final Deliverable

Generate comprehensive onboarding report:

```markdown
# Client Onboarding Report
## {Company Name}
Generated: {timestamp}

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Platforms Discovered | {count} |
| Fully Supported | {count} ({percentage}%) |
| Skills Generated | {count} |
| Configuration Files | {count} |
| Estimated Setup Time | {time} |

---

## Tech Stack Overview

{Visual diagram or table of all platforms}

---

## Support Status

### Ready to Use ✅
{List of fully supported platforms with available skills}

### Configured with Limitations ⚠️
{Platforms with partial support and workarounds}

### Skills Generated 🆕
{New skills created for this client}

### Manual Setup Required 🔧
{Platforms requiring manual configuration}

---

## Configuration Summary

### Files Created
- `clients/{client_id}/config/datasources.yaml`
- `clients/{client_id}/config/semantic_layer/`
- `clients/{client_id}/config/thresholds.yaml`

### Skills Added/Updated
- `skills/{new_skill_1}/SKILL.md` (NEW)
- `skills/{updated_skill}/SKILL.md` (UPDATED)

---

## Next Steps

1. [ ] Review and approve generated configurations
2. [ ] Provide API credentials for configured platforms
3. [ ] Test discovery skills against live data
4. [ ] Validate field mappings are correct
5. [ ] Confirm threshold values for alerts/triggers

---

## Quick Start Commands

```bash
# Test CRM connection
mh1 crm-discovery --client {client_id}

# Test warehouse connection
mh1 data-warehouse-discovery --client {client_id}

# Run first pipeline analysis
mh1 pipeline-analysis --client {client_id}
```
```

---

## Supported Industries

Pre-configured templates for common industries:

| Industry | Default Thresholds | Lifecycle Model | Key Metrics |
|----------|-------------------|-----------------|-------------|
| **B2B SaaS** | ARR $10k+, 40 health | 8-stage | ARR, NRR, Health Score |
| **E-commerce** | LTV $500+, 90-day | Purchase funnel | AOV, Frequency, Recency |
| **Marketing Agency** | MRR $5k+, NPS 7+ | Retainer lifecycle | MRR, Churn, NPS |
| **FinTech** | AUM $50k+, risk score | Regulatory stages | AUM, Risk, Compliance |
| **Healthcare** | Patient value, HIPAA | Care continuum | Visits, Outcomes, HIPAA |
| **Real Estate** | Deal value $100k+ | Transaction pipeline | Volume, Days on Market |

---

## Client Directory Structure

After onboarding:

```
clients/{client_id}/
├── config/
│   ├── datasources.yaml      # Main configuration
│   ├── thresholds.yaml       # Business thresholds
│   ├── semantic_layer/       # Event mappings
│   │   ├── lifecycle_steps.yml
│   │   ├── event_dictionary.yml
│   │   └── company_event_semantics.yml
│   └── integrations/         # Platform-specific
│       ├── crm.yaml
│       ├── warehouse.yaml
│       └── marketing.yaml
├── credentials/              # Encrypted credentials (gitignored)
│   └── .env
├── artifacts/                # Stored query results
└── reports/                  # Generated reports
```

---

## Output

```json
{
  "onboarding_complete": true,
  "client_id": "{client_id}",
  "platforms_configured": {count},
  "skills_generated": {count},
  "skills_updated": {count},
  "config_files_created": ["{file_1}", "{file_2}"],
  "requires_human_review": true,
  "next_steps": ["{step_1}", "{step_2}"],
  "report_path": "clients/{client_id}/reports/onboarding-report.md"
}
```
