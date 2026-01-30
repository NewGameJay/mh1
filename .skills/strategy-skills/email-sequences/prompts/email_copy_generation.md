# Email Copy Generation Prompt
**Purpose**: Generate modular email copy blocks for each reason code
**Target**: Re-engagement emails for stalled companies

---

## Customization

To use these templates for your company:
1. Replace `{company_name}` with your company name
2. Replace `{product_name}` with your product/service name
3. Replace `{feature_name}` with specific features relevant to your product
4. Customize the proof blocks with your specific metrics
5. Adjust tone based on your brand voice guide

### Industry Examples

| Industry | `{product_name}` | `{feature_name}` | Key Metrics |
|----------|------------------|------------------|-------------|
| B2B SaaS | "DataFlow Pro" | "automated workflows", "API integrations" | Users, API calls, automations |
| E-commerce | "ShopBoost" | "product recommendations", "cart recovery" | Orders, GMV, conversion rate |
| Marketing Tech | "CampaignHub" | "multi-channel campaigns", "A/B testing" | Sends, opens, conversions |
| FinTech | "PayStream" | "payment processing", "fraud detection" | Transactions, volume, approval rate |

---

## Copy Generation Framework

For each reason code, generate:
- 2 subject line variants
- 2 opener variants  
- 1 body block (main value proposition)
- 1 proof block (social proof or data point)
- 2 CTA variants

---

## Reason Code: REENGAGEMENT (Usage Decay)

**Signal**: Low recent activity vs prior period (events_14d < 0.3 * events_prior_76d)
**Copy Angle**: Re-engage dormant users
**Tone**: Friendly, acknowledging absence, offering value

### Subject Variants
1. "We noticed you haven't been active lately - here's what you're missing"
2. "Your {product_name} account is waiting - new features to explore"

### Opener Variants
1. "Hi {{contact.firstname}}, we noticed you haven't been using {product_name} as much recently. We wanted to check in and share some exciting updates that might rekindle your interest."
2. "{{contact.firstname}}, it's been a while since we've seen you on {product_name}. We've been busy building features that could make a real difference for your business."

### Body Block
"You were one of our most active users earlier this year, generating [X] {primary_metric} and [Y] {secondary_metric}. Since then, we've launched several improvements that could help you achieve even better results:
- {feature_update_1}
- {feature_update_2}
- {feature_update_3}
We'd love to help you get back to that level of engagement."

### Proof Block
"Companies similar to yours that re-engaged saw a 45% increase in conversion rates within 30 days of returning to active usage."

### CTA Variants
1. "Log in and explore new features"
2. "Schedule a quick check-in call"

---

## Reason Code: CONVERSION (High Engagement, No Conversion)

**Signal**: High engagement volume but zero conversions ((engagement_events + click_events) > 50 AND conversion_events = 0)
**Copy Angle**: Conversion optimization tips
**Tone**: Helpful, educational, solution-focused

### Subject Variants
1. "You're getting great engagement - here's how to convert more"
2. "Turn your {engagement_type} into conversions with these tips"

### Opener Variants
1. "Hi {{contact.firstname}}, we noticed you're generating excellent engagement with [X] {primary_metric} and [Y] {secondary_metric}, but you haven't seen conversions yet. Let's change that."
2. "{{contact.firstname}}, your {product_name} content is getting attention - [X] {engagements} in the last 90 days! Here's how to turn that engagement into measurable results."

### Body Block
"You're clearly creating content that people want to interact with. The next step is optimizing for conversions. Here are three proven strategies:
1. **Clear value proposition**: Make sure your landing page immediately communicates what visitors get
2. **Low-friction forms**: Reduce form fields to only what's essential
3. **Strong CTAs**: Use action-oriented language that creates urgency
We can help you implement these changes quickly."

### Proof Block
"Companies that optimized their conversion flow after high engagement saw an average 3x increase in form submissions within 60 days."

### CTA Variants
1. "Get conversion optimization tips"
2. "Book a free conversion audit"

---

## Reason Code: RETENTION (High Exit Rate)

**Signal**: High exit rate relative to engagement (exit_events > 0.3 * (page_view_events + engagement_events))
**Copy Angle**: Content improvement suggestions
**Tone**: Constructive, data-driven, improvement-focused

### Subject Variants
1. "Quick win: improve your content to reduce bounce rate"
2. "Your visitors are leaving too soon - here's why"

### Opener Variants
1. "Hi {{contact.firstname}}, we noticed that while you're getting good traffic ([X] page views), visitors are leaving quickly. Let's fix that."
2. "{{contact.firstname}}, your {product_name} links are getting clicks, but visitors aren't staying. Here's what might be causing it and how to fix it."

### Body Block
"Your exit rate is [X]% higher than optimal, which suggests visitors aren't finding what they expect. Common causes:
- **Mismatched messaging**: Your promotional content doesn't match landing page experience
- **Slow load times**: Mobile visitors especially need fast-loading pages
- **Poor mobile experience**: Most traffic is mobile - is your experience mobile-optimized?
We can help you audit and improve your content flow."

### Proof Block
"Companies that reduced exit rates by 20% saw a corresponding 35% increase in conversions and 50% increase in time on site."

### CTA Variants
1. "Get a free content audit"
2. "See content improvement examples"

---

## Template Structure

When using in your CRM template, structure as:

```
Subject: {{contact.generated_subject}}

{{contact.generated_opener}}

{{contact.generated_body}}

{{contact.generated_proof}}

[CTA Button: {{contact.generated_cta}}]
```

---

## CRM Property Mapping

### Generic Pattern
Map generated copy to CRM contact/lead properties for personalized sending.

| Copy Block | Semantic Property | HubSpot | Salesforce | Marketo |
|------------|-------------------|---------|------------|---------|
| Subject | `generated_subject` | `ai_subject` | `Generated_Subject__c` | `generatedSubject` |
| Opener | `generated_opener` | `ai_opener` | `Generated_Opener__c` | `generatedOpener` |
| Body | `generated_body` | `ai_body_block_1` | `Generated_Body__c` | `generatedBody` |
| Proof | `generated_proof` | `ai_proof_block` | `Generated_Proof__c` | `generatedProof` |
| CTA | `generated_cta` | `ai_cta` | `Generated_CTA__c` | `generatedCta` |
| Reason Code | `reason_code` | `ai_reason_code` | `Reason_Code__c` | `reasonCode` |
| Cohort ID | `cohort_id` | `ai_cohort_id` | `Cohort_Id__c` | `cohortId` |

### Property Naming Conventions

| CRM | Convention | Example |
|-----|------------|---------|
| HubSpot | Snake case with prefix | `ai_subject`, `ai_reason_code` |
| Salesforce | Pascal case with `__c` suffix | `Generated_Subject__c` |
| Marketo | Camel case | `generatedSubject` |
| Dynamics | Pascal case | `GeneratedSubject` |
| Generic/API | Snake case | `generated_subject` |

---

## Personalization Tokens

### Cross-Platform Token Syntax

| Data Point | HubSpot | Salesforce | Marketo | Generic |
|------------|---------|------------|---------|---------|
| First name | `{{contact.firstname}}` | `{!Lead.FirstName}` | `{{lead.First Name}}` | `{contact_name}` |
| Company | `{{contact.company}}` | `{!Lead.Company}` | `{{lead.Company Name}}` | `{company_name}` |
| Reason code | `{{contact.ai_reason_code}}` | `{!Lead.Reason_Code__c}` | `{{lead.reasonCode}}` | `{reason_code}` |

---

## Generation Instructions

For each company in the cohort:
1. Identify reason code(s) - a company can have multiple
2. Select primary reason code (most severe or most actionable)
3. Generate copy blocks using the templates above
4. Fill in specific metrics where available (usage counts, event counts, etc.)
5. Store in CopySpec JSON format for CRM writeback

### Output JSON Schema

```json
{
  "contact_id": "string",
  "reason_code": "REENGAGEMENT|CONVERSION|RETENTION|UPSELL|ADVOCACY|WIN_BACK|ONBOARDING|DISCOVERY",
  "generated_copy": {
    "subject": "string",
    "opener": "string",
    "body": "string",
    "proof": "string",
    "cta": "string"
  },
  "personalization_data": {
    "primary_metric": "number",
    "secondary_metric": "number",
    "metric_labels": {
      "primary": "string",
      "secondary": "string"
    }
  }
}
```
