---
name: cohort-email-builder
description: |
  Build batch email campaigns for customer segments using reason codes and lifecycle mapping.
  Use when asked to 'build cohort emails', 'create segment campaign', 'batch email for segment',
  'reason code outreach', or 'lifecycle communication'.
license: Proprietary
compatibility:
  - Any data warehouse (Snowflake, BigQuery, Redshift, Databricks)
  - Any CRM (HubSpot, Salesforce, Marketo, Klaviyo)
metadata:
  author: mh1-engineering
  version: "2.0.0"
  status: active
  created: "2026-01-27"
  updated: "2026-01-28"
  estimated_runtime: "5-15min"
  max_runtime: "30min"
  estimated_cost: "$1.00"
  max_cost: "$3.00"
  client_facing: true
  requires_human_review: true
  tags:
    - email
    - campaigns
    - lifecycle
    - communication
    - segmentation
allowed-tools: Read Write CallMcpTool
---

# Cohort Email Builder Skill

Build personalized batch email campaigns for customer segments using reason codes, lifecycle stages, and communication strategy patterns.

## Supported Platforms

### Data Warehouses

| Platform | Integration | Notes |
|----------|------------|-------|
| Snowflake | MCP (user-snowflake) | Primary support |
| BigQuery | MCP or API | Google Cloud |
| Redshift | API | AWS |
| Databricks | API | Unified analytics |
| PostgreSQL | Direct connection | On-premise option |

### CRM Platforms

| Platform | Integration | Notes |
|----------|------------|-------|
| HubSpot | MCP (user-hubspot) | Contact/Company model |
| Salesforce | MCP or API | Lead/Contact/Account model |
| Marketo | API | Lead model |
| Klaviyo | API | Profile model |
| Custom | Configurable | JSON/CSV export |

---

## Configuration

Configuration is stored in `config/cohort-email-builder.yaml`:

```yaml
# config/cohort-email-builder.yaml
cohort_email_builder:
  # Data warehouse settings
  data_warehouse:
    platform: "snowflake"  # snowflake, bigquery, redshift, databricks, postgres
    
  # CRM settings
  crm:
    platform: "hubspot"  # hubspot, salesforce, marketo, klaviyo, custom
    contact_model: "contact"  # contact, lead, profile
    company_model: "company"  # company, account, organization
    
  # Schema mappings (customize per client data model)
  schema:
    # Customer/Account table
    accounts:
      table: "analytics.accounts"
      fields:
        account_id: "account_id"
        account_name: "name"
        health_score: "health_score"
        health_status: "health_status"
        arr: "annual_revenue"
        owner: "owner_email"
        crm_id: "crm_company_id"
        
    # Contact table
    contacts:
      table: "analytics.contacts"
      fields:
        contact_id: "contact_id"
        email: "email"
        first_name: "first_name"
        last_name: "last_name"
        account_id: "account_id"
        crm_id: "crm_contact_id"
        
    # Activity/Events table
    events:
      table: "analytics.events"
      fields:
        event_id: "event_id"
        account_id: "account_id"
        event_type: "event_type"
        event_date: "event_timestamp"
        
  # Segmentation rules
  segmentation:
    # Define criteria for each reason code
    REENGAGEMENT:
      criteria:
        - field: "days_since_last_activity"
          operator: ">"
          value: 14
        - field: "total_events_90d"
          operator: ">"
          value: 0
    UPSELL:
      criteria:
        - field: "feature_adoption_pct"
          operator: ">="
          value: 60
        - field: "health_score"
          operator: ">="
          value: 70
    # ... additional reason codes
    
  # Communication styles
  communication_styles:
    re_engagement:
      tone: "friendly_reminder"
      urgency: "medium"
      cta_style: "soft_invite"
    retention:
      tone: "consultative"
      urgency: "high"
      cta_style: "meeting_request"
    upsell:
      tone: "value_focused"
      urgency: "medium"
      cta_style: "upgrade_prompt"
    # ... additional styles
```

---

## When to Use

Use this skill when you need to:
- Build email campaigns for customer segments
- Map cohorts to appropriate communication types
- Apply reason codes to personalize messaging
- Create lifecycle-appropriate outreach
- Generate batch email lists with copy guidance

Do NOT use when:
- Sending individual one-off emails
- Running automated workflow emails
- Creating non-email communications

---

## Reason Codes Reference

| Code | Name | Signal | Communication Type | Recommended Focus |
|------|------|--------|-------------------|-------------------|
| **REENGAGEMENT** | Usage Decay | days_since_last > 14 AND events_90d > 0 | re_engagement | value_recap, new_features, success_stories |
| **CONVERSION** | Engaged, No Conversion | engagement > 50 AND conversions = 0 | conversion_optimization | conversion_tips, best_practices, case_studies |
| **RETENTION** | At-Risk Signals | health_score declining OR risk_flag = true | retention | value_demonstration, support_offer, qbr_scheduling |
| **UPSELL** | Expansion Ready | feature_adoption >= 60% AND health_score >= 70 | upsell | premium_benefits, roi_demonstration, upgrade_path |
| **ADVOCACY** | Power User | nps >= 9 OR feature_adoption >= 80% | advocacy | case_study_opportunity, referral_program, beta_access |
| **WIN_BACK** | Churned High-Value | status = churned AND lifetime_value > threshold | win_back | special_offer, feedback_request, product_updates |
| **ONBOARDING** | New Customer | days_since_start < 90 | onboarding | 30_60_90_journey, feature_adoption, success_metrics |
| **DISCOVERY** | Needs Classification | health_status IS NULL | data_enrichment | engagement_prompt, survey, call_to_action |

---

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `cohort_type` | string | yes | - | Cohort identifier (e.g., "at_risk", "expansion_ready") |
| `artifact_run_id` | string | no | - | Run ID from artifact store with cohort data |
| `reason_codes` | array | no | [] | Filter to specific reason codes |
| `limit` | number | no | 500 | Maximum contacts per batch |
| `include_personalization` | boolean | no | true | Generate personalization tokens |
| `data_warehouse` | string | no | config default | Override data warehouse platform |
| `crm_platform` | string | no | config default | Override CRM platform |

---

## Outputs

| Name | Type | Description |
|------|------|-------------|
| `email_list` | array | Contacts with copy guidance |
| `communication_strategy` | object | Lifecycle and tone mapping |
| `templates` | array | Recommended email templates |
| `summary` | object | Campaign statistics |

---

## Dependencies

| Type | Name | Purpose |
|------|------|---------|
| MCP | user-snowflake (or configured DW) | Query cohort data |
| MCP | user-hubspot (or configured CRM) | Get contact details |
| Config | `config/cohort-email-builder.yaml` | Schema and segmentation rules |
| Skill | `artifact-manager` | Load cached cohort data |

---

## Process

### Step 1: Load Configuration

```python
import yaml

with open("config/cohort-email-builder.yaml") as f:
    config = yaml.safe_load(f)["cohort_email_builder"]

dw_platform = data_warehouse or config["data_warehouse"]["platform"]
crm_platform = crm_platform or config["crm"]["platform"]
schema = config["schema"]
```

### Step 2: Load Cohort Data

If `artifact_run_id` provided, load from artifact store:

```python
from lib.artifacts import ArtifactStore

store = ArtifactStore(config.get("artifacts_dir", "artifacts"))
cohort_data = store.load_artifact(artifact_run_id)
```

Otherwise, query fresh data based on `cohort_type`:

```sql
-- Generic example: at_risk cohort
SELECT 
    a.{account_id} as account_id,
    a.{account_name} as account_name,
    a.{arr} as arr,
    a.{health_status} as health_status,
    a.{health_score} as health_score,
    a.{owner} as owner
FROM {accounts_table} a
WHERE a.{health_status} = 'At-Risk'
ORDER BY a.{arr} DESC
LIMIT {limit};
```

**Platform-specific query generation:**

```python
def build_cohort_query(config: dict, cohort_type: str, limit: int) -> str:
    """Generate platform-appropriate SQL for cohort selection"""
    schema = config["schema"]["accounts"]
    table = schema["table"]
    fields = schema["fields"]
    
    # Build field mappings
    select_fields = [
        f"{fields['account_id']} as account_id",
        f"{fields['account_name']} as account_name",
        f"{fields['arr']} as arr",
        f"{fields['health_status']} as health_status",
        f"{fields['health_score']} as health_score",
        f"{fields['owner']} as owner",
        f"{fields['crm_id']} as crm_company_id"
    ]
    
    # Build WHERE clause based on cohort_type
    where_clause = get_cohort_where_clause(cohort_type, config)
    
    return f"""
    SELECT {', '.join(select_fields)}
    FROM {table}
    WHERE {where_clause}
    ORDER BY {fields['arr']} DESC
    LIMIT {limit}
    """
```

### Step 3: Assign Reason Codes

Apply reason code logic based on configuration:

```python
def assign_reason_codes(accounts: list, config: dict) -> list:
    """Assign reason codes based on configured segmentation rules"""
    segmentation = config["segmentation"]
    
    for account in accounts:
        codes = []
        
        for code, rules in segmentation.items():
            if evaluate_criteria(account, rules["criteria"]):
                codes.append(code)
        
        # Select primary reason code (first match by priority)
        account["reason_codes"] = codes
        account["primary_reason_code"] = codes[0] if codes else "DISCOVERY"
    
    return accounts

def evaluate_criteria(account: dict, criteria: list) -> bool:
    """Evaluate if account matches all criteria"""
    for criterion in criteria:
        field = criterion["field"]
        operator = criterion["operator"]
        value = criterion["value"]
        
        account_value = account.get(field)
        if account_value is None:
            return False
            
        if operator == ">" and not (account_value > value):
            return False
        elif operator == ">=" and not (account_value >= value):
            return False
        elif operator == "=" and not (account_value == value):
            return False
        # ... additional operators
    
    return True
```

### Step 4: Get Communication Strategy

```python
def get_communication_strategy(cohort_type: str, config: dict) -> dict:
    """Get communication strategy based on cohort type and config"""
    
    # Map cohort type to lifecycle stage
    lifecycle_mapping = {
        "at_risk": "renewal_at_risk",
        "expansion_ready": "expansion_eligible",
        "onboarding": "new_customer",
        "churned": "win_back_eligible"
    }
    
    lifecycle_stage = lifecycle_mapping.get(cohort_type, "general")
    
    # Get communication style
    comm_styles = config["communication_styles"]
    
    return {
        "cohort_type": cohort_type,
        "lifecycle_stage": lifecycle_stage,
        "marketing_goal": get_marketing_goal(lifecycle_stage),
        "copy_style": comm_styles.get(lifecycle_stage, comm_styles["re_engagement"])
    }
```

**Communication Styles:**

| Type | Tone | Urgency | CTA Style |
|------|------|---------|-----------|
| re_engagement | friendly_reminder | medium | soft_invite |
| conversion_optimization | helpful_expert | low | educational |
| retention | consultative | high | meeting_request |
| upsell | value_focused | medium | upgrade_prompt |
| advocacy | celebratory | low | partnership |
| win_back | empathetic | medium | special_offer |
| onboarding | welcoming | medium | next_step |
| data_enrichment | curious | low | survey |

### Step 5: Enrich with CRM Contacts

**HubSpot:**
```json
{
  "filterGroups": [{
    "filters": [{
      "propertyName": "associatedcompanyid",
      "operator": "EQ",
      "value": "{crm_company_id}"
    }]
  }],
  "properties": [
    "email", "firstname", "lastname", "jobtitle",
    "hubspot_owner_id", "hs_email_last_open_date"
  ],
  "limit": 10
}
```

**Salesforce:**
```python
def get_salesforce_contacts(account_id: str) -> list:
    """Query contacts from Salesforce"""
    return salesforce_api.query(f"""
        SELECT Id, Email, FirstName, LastName, Title, OwnerId
        FROM Contact
        WHERE AccountId = '{account_id}'
        LIMIT 10
    """)
```

### Step 6: Build Email List with Copy Guidance

```python
def build_email_list(accounts: list, config: dict, limit: int) -> list:
    """Build email list with personalization and copy guidance"""
    email_list = []
    comm_styles = config["communication_styles"]
    
    for account in accounts:
        contacts = get_contacts_for_account(account["crm_company_id"])
        reason_code = account["primary_reason_code"]
        
        for contact in contacts:
            email_list.append({
                "email": contact["email"],
                "first_name": contact["first_name"],
                "last_name": contact["last_name"],
                "company_name": account["account_name"],
                "arr": account["arr"],
                "health_score": account["health_score"],
                "reason_code": reason_code,
                "reason_name": get_reason_name(reason_code),
                "communication_type": get_communication_type(reason_code),
                "recommended_focus": get_recommended_focus(reason_code),
                "copy_style": comm_styles.get(
                    get_communication_type(reason_code), 
                    comm_styles["re_engagement"]
                ),
                "personalization_tokens": {
                    "{{first_name}}": contact["first_name"],
                    "{{company_name}}": account["account_name"],
                    "{{reason_context}}": generate_reason_context(reason_code, account),
                    "{{cta}}": generate_cta(reason_code)
                }
            })
    
    return email_list[:limit]
```

### Step 7: Generate Campaign Summary

```python
def generate_summary(email_list: list, strategy: dict) -> dict:
    """Generate campaign summary statistics"""
    return {
        "total_contacts": len(email_list),
        "unique_companies": len(set(e["company_name"] for e in email_list)),
        "total_arr_covered": sum(e.get("arr", 0) for e in email_list),
        "by_reason_code": group_by("reason_code", email_list),
        "by_communication_type": group_by("communication_type", email_list),
        "recommended_send_time": get_optimal_send_time(strategy["copy_style"]["urgency"]),
        "estimated_open_rate": estimate_open_rate(strategy.get("communication_type"))
    }
```

---

## Output Schema

```json
{
  "communication_strategy": {
    "cohort_type": "string",
    "lifecycle_stage": "string",
    "lifecycle_label": "string",
    "marketing_goal": "string",
    "communication_type": "string",
    "copy_style": {
      "tone": "string",
      "urgency": "low | medium | high",
      "cta_style": "string"
    },
    "validation": {
      "is_valid": "boolean",
      "reason": "string"
    }
  },
  "email_list": [
    {
      "email": "string",
      "first_name": "string",
      "last_name": "string",
      "company_name": "string",
      "arr": "number",
      "health_score": "number",
      "reason_code": "string",
      "reason_name": "string",
      "communication_type": "string",
      "recommended_focus": ["string"],
      "copy_style": {
        "tone": "string",
        "urgency": "string",
        "cta_style": "string"
      },
      "personalization_tokens": {
        "{{first_name}}": "string",
        "{{company_name}}": "string",
        "{{reason_context}}": "string",
        "{{cta}}": "string"
      }
    }
  ],
  "templates": [
    {
      "template_name": "string",
      "reason_codes": ["string"],
      "subject_line": "string",
      "preview_text": "string",
      "body_structure": ["string"]
    }
  ],
  "summary": {
    "total_contacts": "number",
    "unique_companies": "number",
    "total_arr_covered": "number",
    "by_reason_code": {
      "REENGAGEMENT": "number",
      "UPSELL": "number"
    },
    "by_communication_type": {
      "retention": "number",
      "upsell": "number"
    },
    "recommended_send_time": "string",
    "estimated_open_rate": "number"
  },
  "metadata": {
    "data_warehouse": "string",
    "crm_platform": "string",
    "generated_at": "ISO timestamp"
  }
}
```

---

## Quality Criteria

- [ ] All contacts have valid email addresses
- [ ] Reason codes correctly assigned per configuration
- [ ] Communication type matches lifecycle stage
- [ ] Copy style appropriate for urgency level
- [ ] Personalization tokens populated
- [ ] No duplicate contacts in list

---

## Example Usage

**Build at-risk retention campaign:**
```
Build cohort email for at_risk cohort with reason code RETENTION
```

**Upsell campaign from artifact:**
```
Build email campaign using artifact run_id=upsell_20260127 for UPSELL expansion ready
```

**Multi-segment outreach:**
```
Create batch email for cohort_type=retention_risk, include REENGAGEMENT and RETENTION codes
```

---

## Sample Output

```json
{
  "communication_strategy": {
    "cohort_type": "at_risk",
    "lifecycle_stage": "renewal_at_risk",
    "lifecycle_label": "Renewal At-Risk",
    "marketing_goal": "Prevent churn, demonstrate value",
    "communication_type": "retention",
    "copy_style": {
      "tone": "consultative",
      "urgency": "high",
      "cta_style": "meeting_request"
    }
  },
  "email_list": [
    {
      "email": "ceo@acme.com",
      "first_name": "John",
      "last_name": "Smith",
      "company_name": "Acme Corp",
      "arr": 156000,
      "health_score": 28,
      "reason_code": "RETENTION",
      "reason_name": "At Risk - High Value",
      "communication_type": "retention",
      "recommended_focus": ["executive_outreach", "value_demonstration", "qbr_scheduling"],
      "copy_style": {
        "tone": "consultative",
        "urgency": "high",
        "cta_style": "meeting_request"
      },
      "personalization_tokens": {
        "{{first_name}}": "John",
        "{{company_name}}": "Acme Corp",
        "{{reason_context}}": "We noticed some recent changes in your team's engagement and wanted to check in personally.",
        "{{cta}}": "I'd love to schedule a 15-minute call to discuss how we can better support your goals."
      }
    }
  ],
  "templates": [
    {
      "template_name": "Executive Check-In",
      "reason_codes": ["RETENTION"],
      "subject_line": "{{first_name}}, let's connect",
      "preview_text": "I wanted to personally reach out...",
      "body_structure": [
        "Personal greeting with name",
        "Acknowledge partnership value",
        "Soft reference to engagement change",
        "Offer executive-level support",
        "Meeting request CTA"
      ]
    }
  ],
  "summary": {
    "total_contacts": 127,
    "unique_companies": 45,
    "total_arr_covered": 2340000,
    "by_reason_code": {
      "RETENTION": 45,
      "REENGAGEMENT": 82
    },
    "by_communication_type": {
      "retention": 45,
      "re_engagement": 82
    },
    "recommended_send_time": "Tuesday 10am local",
    "estimated_open_rate": 0.35
  },
  "metadata": {
    "data_warehouse": "snowflake",
    "crm_platform": "hubspot",
    "generated_at": "2026-01-28T10:30:00Z"
  }
}
```

---

## Human Review Required

This skill requires human review for:
- [ ] Email list validation (check for opt-outs)
- [ ] Copy tone appropriateness
- [ ] Personalization token accuracy
- [ ] Brand voice alignment
- [ ] Legal compliance (CAN-SPAM, GDPR)

---

## Notes

- Always check CRM subscription status before sending
- RETENTION (high-value at-risk) should be reviewed by CS leadership
- ONBOARDING communications should coordinate with onboarding team
- Export to CRM list for campaign execution
- Schema mappings must be configured per client data model

---

## Changelog

### v2.0.0 (2026-01-28)
- Converted to platform-agnostic framework
- Added multi-data-warehouse support
- Added multi-CRM support
- Replaced RC1-RC8 with semantic reason codes
- Added configurable schema mappings
- Added configurable segmentation rules

### v1.0.0 (2026-01-27)
- Initial release
