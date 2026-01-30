---
name: skill-builder
description: |
  Meta-skill that analyzes client requirements, identifies capability gaps, and generates 
  new skills or updates existing ones. Use when asked to 'add platform support', 'create 
  new skill', 'support new CRM', 'add integration', or when onboarding a new client with 
  unsupported platforms.
license: Proprietary
compatibility:
  - WebSearch
  - WebFetch
  - Read
  - Write
  - Shell
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  estimated_runtime: "5-30min"
  max_cost: "$2.00"
  client_facing: false
  requires_human_review: true
  tags:
    - meta-skill
    - skill-generation
    - platform-integration
    - self-evolving
allowed-tools: Read Write WebSearch WebFetch Shell Grep Glob
---

# Skill Builder (Meta-Skill)

A self-evolving system that identifies capability gaps and generates new skills or updates existing ones to support any platform, business model, or client requirement.

## When to Use

Use this skill when:
- Onboarding a new client with unsupported platforms
- A client requests integration with a new CRM/database/tool
- Existing skills don't cover a specific use case
- Platform APIs have changed and skills need updating
- Creating industry-specific skill variants

---

## Process Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  1. ANALYZE     │────▶│  2. RESEARCH     │────▶│  3. GENERATE    │
│  Requirements   │     │  Platform Docs   │     │  Skill Code     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                         │
┌─────────────────┐     ┌──────────────────┐            │
│  5. DEPLOY      │◀────│  4. VALIDATE     │◀───────────┘
│  to Skills Dir  │     │  & Test          │
└─────────────────┘     └──────────────────┘
```

---

## Phase 1: Requirements Analysis

### Step 1.1: Gather Client Context

Collect information about the client's tech stack:

```yaml
client_requirements:
  client_id: "{client_id}"
  
  # Current platforms
  crm:
    name: "{crm_name}"  # e.g., "Monday.com", "Copper", "Freshsales"
    api_docs: "{api_documentation_url}"
    authentication: "api_key" | "oauth2" | "basic"
    
  data_warehouse:
    name: "{warehouse_name}"  # e.g., "ClickHouse", "SingleStore", "Firebolt"
    connection_type: "jdbc" | "native" | "rest"
    
  marketing_automation:
    name: "{platform_name}"  # e.g., "ActiveCampaign", "Braze", "Iterable"
    api_docs: "{api_documentation_url}"
    
  e_commerce:
    name: "{platform_name}"  # e.g., "Shopify", "WooCommerce"
    api_type: "rest" | "graphql"
    
  support:
    name: "{platform_name}"  # e.g., "Zendesk", "Intercom", "Freshdesk"
    
  custom_systems:
    - name: "{system_name}"
      api_docs: "{documentation_url}"
      purpose: "{what_it_does}"
```

### Step 1.2: Identify Capability Gaps

Compare client requirements against existing skills:

```bash
# List all existing skills
ls skills/*/SKILL.md

# Search for platform support
grep -r "compatibility:" skills/*/SKILL.md | grep -i "{platform_name}"
```

Generate a gap analysis:

```yaml
gap_analysis:
  supported:
    - platform: "HubSpot"
      skills: ["crm-discovery", "pipeline-analysis", "deal-velocity"]
      
  partially_supported:
    - platform: "{platform_name}"
      missing_features:
        - "{feature_1}"
        - "{feature_2}"
      skills_to_update: ["{skill_name}"]
      
  not_supported:
    - platform: "{platform_name}"
      required_skills:
        - "{new_skill_1}"
        - "{new_skill_2}"
      priority: high | medium | low
```

---

## Phase 2: Platform Research

### Step 2.1: API Documentation Research

For each unsupported platform, research:

```markdown
## Platform: {platform_name}

### API Overview
- Base URL: {api_base_url}
- Authentication: {auth_method}
- Rate Limits: {rate_limit_info}
- Pagination: {pagination_pattern}

### Key Endpoints

| Entity | Endpoint | Method | Description |
|--------|----------|--------|-------------|
| Contacts | /api/v1/contacts | GET | List all contacts |
| Deals | /api/v1/deals | GET | List all deals |
| Activities | /api/v1/activities | GET | Activity history |

### Data Model Mapping

| Generic Concept | Platform Field | Notes |
|-----------------|----------------|-------|
| account_id | {platform_field} | |
| contact_email | {platform_field} | |
| deal_value | {platform_field} | Currency in cents |
| stage | {platform_field} | Custom values |

### Authentication Example

```python
# {platform_name} Authentication
headers = {
    "Authorization": "Bearer {api_key}",
    "Content-Type": "application/json"
}
```

### Sample Queries

```python
# List contacts with pagination
def list_contacts(api_key, page=1, limit=100):
    response = requests.get(
        f"{BASE_URL}/contacts",
        headers={"Authorization": f"Bearer {api_key}"},
        params={"page": page, "limit": limit}
    )
    return response.json()
```
```

### Step 2.2: Research Sources

Use these sources for platform documentation:

```python
research_sources = [
    # Official docs
    "{platform}.com/api",
    "{platform}.com/developers",
    "developers.{platform}.com",
    
    # API references
    "api.{platform}.com/docs",
    "docs.{platform}.com/api",
    
    # Community resources
    "github.com/{platform}",
    "postman.com/collections/{platform}",
    
    # Integration guides
    "zapier.com/apps/{platform}/integrations",
    "segment.com/docs/connections/destinations/{platform}",
]
```

---

## Phase 3: Skill Generation

### Step 3.1: Choose Generation Strategy

| Scenario | Strategy |
|----------|----------|
| New platform, similar to existing | Clone & adapt existing skill |
| New platform, unique API | Generate from template |
| Existing skill, add platform | Update compatibility section |
| Industry-specific variant | Create wrapper skill |

### Step 3.2: Generate Skill from Template

Use the skill template as a base:

```bash
# Copy template
cp -r skills/_templates/SKILL_TEMPLATE skills/{new-skill-name}
```

Then customize:

```yaml
---
name: {new-skill-name}
description: |
  {Description of what this skill does}
  Use when asked to '{trigger phrase 1}', '{trigger phrase 2}', 
  or '{trigger phrase 3}'.
license: Proprietary
compatibility:
  - {Platform 1}
  - {Platform 2}
  - {Platform 3}
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: experimental  # Start as experimental
  estimated_runtime: "{time}"
  max_cost: "${cost}"
  client_facing: {true|false}
  requires_human_review: {true|false}
  tags:
    - {tag1}
    - {tag2}
    - platform-agnostic
allowed-tools: {tools}
---

# {Skill Name}

{Brief description}

## When to Use

Use this skill when you need to:
- {Use case 1}
- {Use case 2}
- {Use case 3}

---

## Configuration

```yaml
configuration:
  platform: {platform_type}
  # Platform-specific settings
  {platform_name}:
    api_key_env: "{ENV_VAR_NAME}"
    base_url: "{api_base_url}"
    # Field mappings
    field_mapping:
      account_id: "{platform_field}"
      contact_email: "{platform_field}"
```

---

## Supported Platforms

| Platform | API Type | Status | Notes |
|----------|----------|--------|-------|
| {Platform 1} | REST | ✅ Supported | |
| {Platform 2} | GraphQL | ✅ Supported | |
| {Platform 3} | SOAP | ⚠️ Partial | Legacy API |

---

## Platform-Specific Queries

### {Platform 1}

```python
# {Platform 1} implementation
def query_{platform_1}(config):
    # Implementation
    pass
```

### {Platform 2}

```python
# {Platform 2} implementation  
def query_{platform_2}(config):
    # Implementation
    pass
```

---

## Output Format

```json
{
  "status": "success",
  "platform": "{platform}",
  "results": [],
  "metadata": {
    "query_time_ms": 0,
    "record_count": 0
  }
}
```
```

### Step 3.3: Update Existing Skill

When adding platform support to existing skill:

1. **Add to compatibility list:**
```yaml
compatibility:
  - Existing Platform 1
  - Existing Platform 2
  - NEW: {New Platform}  # Add new platform
```

2. **Add platform configuration:**
```yaml
## Platform Configuration

### {New Platform}

```yaml
{new_platform}:
  api_base: "{url}"
  auth_type: "bearer" | "api_key" | "oauth2"
  rate_limit: {requests_per_minute}
  field_mapping:
    account_id: "{platform_field}"
```
```

3. **Add query templates:**
```python
### {New Platform} Query

```{language}
# {New Platform} specific query
{query_code}
```
```

---

## Phase 4: Validation

### Step 4.1: Schema Validation

Validate the generated skill against the schema:

```bash
python3 scripts/validate_skill.py skills/{new-skill-name}/SKILL.md
```

### Step 4.2: Linting Check

Check for common issues:

```python
validation_checklist = [
    "✓ YAML frontmatter is valid",
    "✓ All required fields present",
    "✓ compatibility is array format",
    "✓ metadata.tags is array format",
    "✓ version follows semver",
    "✓ No hardcoded credentials",
    "✓ No company-specific references",
    "✓ Configuration section present",
    "✓ Platform queries use placeholders",
]
```

### Step 4.3: Integration Test (if possible)

```yaml
test_cases:
  - name: "API connectivity"
    type: "integration"
    requires: ["API_KEY"]
    
  - name: "Field mapping"
    type: "unit"
    input: {sample_data}
    expected: {mapped_data}
    
  - name: "Error handling"
    type: "unit"
    input: {invalid_data}
    expected: {error_response}
```

---

## Phase 5: Deployment

### Step 5.1: File Structure

Ensure proper structure:

```
skills/{new-skill-name}/
├── SKILL.md           # Required: Main skill definition
├── README.md          # Optional: Detailed documentation
├── examples/          # Optional: Usage examples
│   └── example-01.md
├── schemas/           # Optional: Input/output schemas
│   ├── input.json
│   └── output.json
└── tests/             # Optional: Test cases
    └── test-01.md
```

### Step 5.2: Update Index

Add to skill discovery:

```bash
# The skill is auto-discovered from the skills/ directory
# No manual index update needed
```

### Step 5.3: Document Changes

Create changelog entry:

```markdown
## [{version}] - {date}

### Added
- New skill: `{skill-name}` for {platform} integration
- Support for {features}

### Changed
- Updated `{existing-skill}` to support {new-platform}
```

---

## Platform Support Matrix

### Currently Supported

| Category | Platforms |
|----------|-----------|
| CRM | HubSpot, Salesforce, Pipedrive, Zoho, Dynamics |
| Data Warehouse | Snowflake, BigQuery, Redshift, Databricks, PostgreSQL |
| Analytics | Segment, Amplitude, Mixpanel, GA4 |
| Email | HubSpot, Salesforce MC, Marketo, Klaviyo |

### Commonly Requested (Priority Queue)

| Platform | Category | Complexity | Research Links |
|----------|----------|------------|----------------|
| Monday.com | CRM/PM | Medium | [API Docs](https://developer.monday.com/api-reference/) |
| Airtable | Database | Medium | [API Docs](https://airtable.com/developers/web/api) |
| Notion | Database/PM | Medium | [API Docs](https://developers.notion.com/) |
| Shopify | E-commerce | Medium | [API Docs](https://shopify.dev/docs/api) |
| Zendesk | Support | Medium | [API Docs](https://developer.zendesk.com/) |
| Intercom | Support | Medium | [API Docs](https://developers.intercom.com/) |
| ActiveCampaign | Marketing | Medium | [API Docs](https://developers.activecampaign.com/) |
| Mailchimp | Email | Low | [API Docs](https://mailchimp.com/developer/) |
| ClickUp | PM | Medium | [API Docs](https://clickup.com/api) |
| Copper | CRM | Medium | [API Docs](https://developer.copper.com/) |

---

## Quick Commands

```bash
# Analyze client requirements
mh1 skill-builder analyze --client {client_id}

# Research new platform
mh1 skill-builder research --platform {platform_name}

# Generate new skill
mh1 skill-builder generate --platform {platform} --type {skill_type}

# Update existing skill
mh1 skill-builder update --skill {skill_name} --add-platform {platform}

# Validate generated skill
mh1 skill-builder validate --skill {skill_name}
```

---

## Human Review Checklist

Before deploying generated skills, verify:

- [ ] API authentication patterns are correct
- [ ] Rate limiting is handled appropriately  
- [ ] Error messages are helpful
- [ ] Field mappings are accurate
- [ ] No sensitive data is logged
- [ ] Platform-specific quirks are documented
- [ ] Examples work with real API
- [ ] Configuration is complete

---

## Output

After running this skill, you will have:

1. **Gap Analysis Report**: What's missing for the client
2. **Platform Research Notes**: API documentation summary
3. **Generated/Updated Skills**: New or modified skill files
4. **Validation Report**: Schema and lint check results
5. **Deployment Checklist**: Steps for human review

```json
{
  "skill_builder_output": {
    "gap_analysis": "{path_to_gap_analysis}",
    "research_notes": "{path_to_research}",
    "generated_skills": ["{skill_1}", "{skill_2}"],
    "updated_skills": ["{skill_3}"],
    "validation_status": "passed" | "failed",
    "requires_human_review": true
  }
}
```
