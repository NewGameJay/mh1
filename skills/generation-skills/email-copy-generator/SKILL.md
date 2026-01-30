---
name: email-copy-generator
description: |
  Generate personalized email copy based on customer signals and reason codes.
  Use when asked to 'write email copy', 'generate outreach', 'create email for cohort',
  'personalize email', or 'write retention email'.
license: Proprietary
compatibility:
  - Any CRM with API access (HubSpot, Salesforce, etc.)
  - Custom email systems
metadata:
  author: mh1-engineering
  version: "2.0.0"
  status: active
  estimated_runtime: "30s-1min"
  max_cost: "$0.50"
  client_facing: true
  requires_human_review: true
  tags:
    - content-generation
    - email
    - outreach
    - personalization
    - lifecycle
allowed-tools: Read Write CallMcpTool
---

# Email Copy Generator Skill

Generate personalized email copy based on customer signals, reason codes, and cohort data.

## References
Refer to the following markdown files when generating copy:
- copy-frameworks.md
- plain-language.md
- natural-transitions.md


## Supported Platforms

| Platform | Integration Method | Notes |
|----------|-------------------|-------|
| HubSpot | MCP (user-hubspot) | Contact property writeback |
| Salesforce | MCP or API | Contact/Lead field updates |
| Marketo | API | Custom fields via REST |
| Klaviyo | API | Profile properties |
| Custom CRM | Configurable | JSON export or API |

---

## Configuration

Configuration is stored in `config/email-copy-generator.yaml`:

```yaml
# config/email-copy-generator.yaml
email_copy_generator:
  # CRM settings
  crm:
    platform: "hubspot"  # hubspot, salesforce, marketo, klaviyo, custom
    property_prefix: "ai_"  # Prefix for AI-generated fields
    
  # Reason code mappings (customize per client)
  reason_codes:
    REENGAGEMENT:
      enabled: true
      template: "reengagement_v1"
      communication_type: "re_engagement"
    CONVERSION:
      enabled: true
      template: "conversion_v1"
      communication_type: "conversion_optimization"
    # ... additional codes
    
  # Template settings
  templates:
    directory: "templates/email/"
    fallback: "generic_outreach"
    
  # Output format
  output:
    include_variants: true
    variant_count: 3
    include_crm_properties: true
```

---

## When to Use

Use this skill when you need to:
- Generate outreach emails for specific customer segments
- Create personalized copy based on usage signals
- Build email campaigns for retention, upsell, or re-engagement
- Write copy that can be pushed to CRM contact properties

---

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `reason_code` | string | yes | Reason code defining the copy angle |
| `contact_data` | object | yes | Contact info (name, company, signals) |
| `tone` | string | no | "professional", "friendly", "urgent" (default: professional) |
| `include_proof` | boolean | no | Include social proof block (default: true) |
| `crm_platform` | string | no | Override default CRM platform |
| `template_id` | string | no | Override default template for reason code |

---

## Reason Codes (Generic Framework)

| Code | Signal Pattern | Copy Angle | Communication Type |
|------|----------------|------------|-------------------|
| **REENGAGEMENT** | Usage decay, inactivity | Re-engagement | `re_engagement` |
| **CONVERSION** | High activity, no conversion | Conversion tips | `conversion_optimization` |
| **RETENTION** | Engagement decline, at-risk | Content improvement | `retention` |
| **UPSELL** | High usage, expansion ready | Upgrade pitch | `upsell` |
| **ADVOCACY** | Power user, champion | Advocacy/recognition | `advocacy` |
| **WIN_BACK** | Churned or cancelled | Win-back offer | `win_back` |
| **ONBOARDING** | New customer | Onboarding success | `onboarding` |
| **DISCOVERY** | Needs classification | Discovery call | `data_enrichment` |

### Reason Code Details

| Code | Signal Criteria | Recommended Focus |
|------|-----------------|-------------------|
| **REENGAGEMENT** | days_since_last > 14 AND past_activity > 0 | value_recap, new_features, success_stories |
| **CONVERSION** | engagement_events > 50 AND conversions = 0 | conversion_tips, best_practices, case_studies |
| **RETENTION** | health_score declining OR at_risk flag | value_demonstration, support_offer, qbr_scheduling |
| **UPSELL** | feature_adoption >= 60% AND health_score >= 70 | premium_benefits, roi_demonstration, upgrade_path |
| **ADVOCACY** | nps >= 9 OR feature_adoption >= 80% | case_study_opportunity, referral_program, beta_access |
| **WIN_BACK** | status = churned AND lifetime_value > threshold | special_offer, feedback_request, product_updates |
| **ONBOARDING** | days_since_start < 90 | 30_60_90_journey, feature_adoption, success_metrics |
| **DISCOVERY** | health_status IS NULL OR incomplete_data | engagement_prompt, survey, call_to_action |

---

## Output Schema

```json
{
  "reason_code": "string",
  "contact": {
    "name": "string",
    "company": "string"
  },
  "copy": {
    "subject_lines": ["string", "string"],
    "opener": "string",
    "body_block_1": "string",
    "proof_block": "string",
    "cta": "string",
    "cta_variants": ["string", "string"]
  },
  "crm_properties": {
    "ai_cohort_id": "string",
    "ai_reason_code": "string",
    "ai_subject": "string",
    "ai_opener": "string",
    "ai_body_block_1": "string",
    "ai_proof_block": "string",
    "ai_cta": "string",
    "ai_prompt_version": "string"
  },
  "metadata": {
    "crm_platform": "string",
    "template_used": "string",
    "generated_at": "ISO timestamp"
  }
}
```

---

## Process

### Step 1: Validate Inputs

```python
VALID_REASON_CODES = [
    "REENGAGEMENT", "CONVERSION", "RETENTION", "UPSELL",
    "ADVOCACY", "WIN_BACK", "ONBOARDING", "DISCOVERY"
]

assert reason_code in VALID_REASON_CODES, f"Invalid reason code: {reason_code}"
assert contact_data.get("name") and contact_data.get("company")
```

### Step 2: Load Configuration

```python
import yaml

with open("config/email-copy-generator.yaml") as f:
    config = yaml.safe_load(f)

crm_platform = crm_platform or config["email_copy_generator"]["crm"]["platform"]
property_prefix = config["email_copy_generator"]["crm"]["property_prefix"]
```

### Step 3: Select Template

Based on reason code, load the appropriate template:

| Reason Code | Template Focus |
|-------------|----------------|
| REENGAGEMENT | "Come back and see what's new" |
| CONVERSION | "Turn your engagement into results" |
| RETENTION | "We're here to help you succeed" |
| UPSELL | "You're ready for the next level" |
| ADVOCACY | "Thank you for being a top user" |
| WIN_BACK | "We'd love to have you back" |
| ONBOARDING | "Welcome! Let's get you started" |
| DISCOVERY | "How can we help you succeed?" |

### Step 4: Personalize Copy

Insert contact variables:
- `{{contact.firstname}}` - First name
- `{{contact.company}}` - Company name
- `{{contact.ai_*}}` - AI-generated fields
- `{{signal.primary}}` - Primary signal that triggered outreach

### Step 5: Generate Variants

Create 2-3 subject line variants and CTA variants for A/B testing.

### Step 6: Format for CRM

Map output to CRM properties based on platform:

**HubSpot:**
```json
{
  "ai_subject": "Primary subject line",
  "ai_opener": "Personalized opener",
  "ai_body_block_1": "Main body content",
  "ai_proof_block": "Social proof/stats",
  "ai_cta": "Call to action"
}
```

**Salesforce:**
```json
{
  "AI_Subject__c": "Primary subject line",
  "AI_Opener__c": "Personalized opener",
  "AI_Body__c": "Main body content",
  "AI_CTA__c": "Call to action"
}
```

---

## Example Usage

**Generate re-engagement email:**
```
Generate email copy for reason_code=REENGAGEMENT
Contact: John Smith at Acme Corp
Signal: No activity in 45 days
```

**Generate upsell email:**
```
Write upgrade pitch for power user
Contact: Sarah at TechStartup
Signal: Using 80% of available features
```

**Generate win-back email:**
```
Create win-back email for churned customer
Contact: Mike at BigCorp
Signal: Cancelled 30 days ago, was high-value
```

---

## Sample Output (UPSELL)

```json
{
  "reason_code": "UPSELL",
  "contact": {
    "name": "Sarah",
    "company": "TechStartup"
  },
  "copy": {
    "subject_lines": [
      "Sarah, you're ready for the next level",
      "TechStartup is crushing it - here's what's next"
    ],
    "opener": "Hi Sarah,\n\nI've been looking at TechStartup's usage, and I'm impressed. You're using 80% of our features, and your engagement is in the top 10% of all customers.",
    "body_block_1": "Based on your usage patterns, I think you'd get tremendous value from our premium tier. Here's what it unlocks:\n\n- Advanced analytics dashboard\n- Custom branding on all assets\n- Priority support\n- API access for integrations",
    "proof_block": "Companies like yours typically see a 40% increase in efficiency after upgrading. Last quarter, similar accounts reported significant time savings and improved outcomes.",
    "cta": "Want to see a quick demo? I can show you exactly how it maps to what you're already doing.",
    "cta_variants": [
      "Let's schedule 15 minutes this week?",
      "Reply 'yes' and I'll send calendar options"
    ]
  },
  "crm_properties": {
    "ai_cohort_id": "upsell_q1_2026",
    "ai_reason_code": "UPSELL",
    "ai_subject": "Sarah, you're ready for the next level",
    "ai_opener": "Hi Sarah,\n\nI've been looking at TechStartup's usage...",
    "ai_body_block_1": "Based on your usage patterns...",
    "ai_proof_block": "Companies like yours typically see...",
    "ai_cta": "Want to see a quick demo?",
    "ai_prompt_version": "v2.0"
  },
  "metadata": {
    "crm_platform": "hubspot",
    "template_used": "upsell_v1",
    "generated_at": "2026-01-28T10:30:00Z"
  }
}
```

---

## Quality Criteria

- [ ] Reason code correctly mapped to template
- [ ] Contact name and company inserted
- [ ] Subject lines are compelling and personalized
- [ ] Body flows logically
- [ ] CTA is clear and actionable
- [ ] Proof block is relevant to segment
- [ ] CRM properties correctly formatted for target platform

---

## Writeback to CRM

### HubSpot

```
Call: hubspot_update_contact
Parameters:
  - contact_id: {contact_hubspot_id}
  - properties: {crm_properties from output}
```

### Salesforce

```
Call: salesforce_update_record
Parameters:
  - object_type: "Contact" or "Lead"
  - record_id: {salesforce_id}
  - fields: {crm_properties from output}
```

### Generic API

```python
def writeback_to_crm(platform: str, record_id: str, properties: dict):
    """Generic CRM writeback function"""
    if platform == "hubspot":
        return hubspot_mcp.update_contact(record_id, properties)
    elif platform == "salesforce":
        return salesforce_api.update_record("Contact", record_id, properties)
    elif platform == "custom":
        return custom_api.update(record_id, properties)
```

---

## Template Customization

Templates are stored in `templates/email/` and can be customized per client:

```markdown
# templates/email/reengagement_v1.md
---
reason_code: REENGAGEMENT
tone: friendly_reminder
urgency: medium
---

## Subject Line Templates
- "{{contact.firstname}}, we've missed you!"
- "What's new since you've been away, {{contact.firstname}}"

## Opener
Hi {{contact.firstname}},

I noticed it's been a while since {{contact.company}} has been active...

## Body
[Template content with variable placeholders]

## CTA
Would you have 10 minutes for a quick call? I'd love to share what's new.
```

---

## Notes

- Always review generated copy before sending
- A/B test subject lines for best performance
- Track which reason codes have highest engagement
- Update proof blocks with fresh stats quarterly
- Customize templates per client voice and brand guidelines

---

## Changelog

### v2.0.0 (2026-01-28)
- Converted to platform-agnostic framework
- Replaced RC1-RC8 with semantic reason codes
- Added multi-CRM support (HubSpot, Salesforce, Marketo, Klaviyo)
- Added configuration file support
- Added template customization

### v1.0.0 (2026-01-27)
- Initial release
