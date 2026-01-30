# Reason Code Email Copy Templates
**Purpose**: Complete reference for all 8 reason codes with copy variants
**Version**: v3.0 (Company-Agnostic)

---

## Customization

To use these templates for your company:
1. Replace `{company_name}` with your company name
2. Replace `{product_name}` with your product/service name
3. Replace `{feature_name}` with specific features (e.g., "automated workflows", "analytics dashboard")
4. Customize the proof blocks with your specific metrics
5. Adjust tone based on your brand voice guide
6. Map to your CRM's property naming convention

### Industry Configuration Examples

| Industry | `{product_name}` | Primary Metrics | Key Features |
|----------|------------------|-----------------|--------------|
| **B2B SaaS** | "DataFlow Pro" | Users, API calls, automations | "workflows", "integrations", "dashboards" |
| **E-commerce Platform** | "ShopBoost" | Orders, GMV, conversion rate | "product feeds", "cart recovery", "recommendations" |
| **Marketing Tech** | "CampaignHub" | Sends, opens, conversions | "campaigns", "A/B tests", "segments" |
| **FinTech** | "PayStream" | Transactions, volume, approval rate | "payments", "fraud detection", "reporting" |
| **HR Tech** | "TalentFlow" | Applicants, hires, time-to-fill | "job postings", "screening", "scheduling" |

---

## Overview

Each reason code represents a behavioral signal that triggers a specific type of communication. The templates below provide modular copy blocks that can be assembled into complete emails.

### Reason Code Mapping

| Code | Semantic Name | Use Case | Trigger Signal |
|------|---------------|----------|----------------|
| RC1 | REENGAGEMENT | Re-activate dormant users | Usage decay over time |
| RC2 | CONVERSION | Convert engaged non-buyers | High engagement, no conversion |
| RC3 | RETENTION | Reduce churn signals | High exit/bounce rate |
| RC4 | UPSELL | Expand account value | High adoption, expansion ready |
| RC5 | ADVOCACY | Activate promoters | Power user, high satisfaction |
| RC6 | WIN_BACK | Save at-risk accounts | Declining engagement, high value |
| RC7 | ONBOARDING | Accelerate time-to-value | New customer, early stage |
| RC8 | DISCOVERY | Qualify and classify | Insufficient data, unclear intent |

### Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{company_name}` | Your company/product brand | "Acme Corp" |
| `{product_name}` | Product or service name | "DataFlow Pro" |
| `{contact_name}` | Contact first name | "John" |
| `{feature_name}` | Specific feature reference | "automated workflows" |
| `{feature_count}` | Number of features used | "several" |
| `{vertical}` | Industry vertical | "retail" |
| `{proof_company}` | Similar company for social proof | "companies like yours" |
| `{primary_metric}` | Main usage metric | "API calls" |
| `{secondary_metric}` | Supporting metric | "automations created" |
| `{tier_name}` | Premium tier name | "Enterprise", "Pro", "Growth" |

---

## REENGAGEMENT: Usage Decay

### Signal/Trigger
Low recent activity vs prior period. Events in last 14 days < 30% of events in prior 76 days.

### Communication Type
Re-engagement email for dormant users

### Subject Line Variants
1. "We noticed you haven't been active lately - here's what you're missing"
2. "Your {product_name} account is waiting - new features to explore"
3. "{contact_name}, come back and see what's new"

### Opener Variants
1. "Hi {contact_name}, we noticed you haven't been using {product_name} as much recently. We wanted to check in and share some exciting updates."
2. "It's been a while since we've seen activity from your account. We've been busy building features that could make a real difference for your business."

### Body Block
"Since your last visit, we've launched several improvements:
- {feature_update_1}
- {feature_update_2}
- {feature_update_3}

We'd love to help you get back to achieving great results."

### Proof Block
"Companies that re-engaged saw a 45% increase in conversion rates within 30 days of returning to active usage."

### CTA Variants
1. "Log in and explore new features"
2. "Schedule a quick check-in call"
3. "See what's new in your dashboard"

---

## CONVERSION: High Engagement, No Conversion

### Signal/Trigger
High engagement volume but zero conversions. (engagement_events + click_events) > 50 AND conversion_events = 0

### Communication Type
Conversion optimization tips

### Subject Line Variants
1. "You're getting great engagement - here's how to convert more"
2. "Turn your {primary_metric} into conversions with these tips"
3. "From engagement to results: your next step"

### Opener Variants
1. "We noticed you're generating excellent engagement, but conversions aren't following. Let's change that."
2. "Your {product_name} content is getting attention! Here's how to turn that engagement into measurable results."

### Body Block
"You're clearly creating content that people want to interact with. Here's how to optimize for conversions:
1. **Clear value proposition**: Make sure your landing page immediately communicates what visitors get
2. **Low-friction forms**: Reduce form fields to only what's essential
3. **Strong CTAs**: Use action-oriented language that creates urgency"

### Proof Block
"Companies that optimized their conversion flow after high engagement saw an average 3x increase in form submissions within 60 days."

### CTA Variants
1. "Get conversion optimization tips"
2. "Book a free conversion audit"
3. "See conversion best practices"

---

## RETENTION: High Exit Rate

### Signal/Trigger
High exit rate relative to engagement. exit_events > 30% of (page_view_events + engagement_events)

### Communication Type
Content improvement suggestions

### Subject Line Variants
1. "Quick win: improve your content to reduce bounce rate"
2. "Your visitors are leaving too soon - here's why"
3. "Keep visitors engaged longer"

### Opener Variants
1. "We noticed that while you're getting good traffic, visitors are leaving quickly. Let's fix that."
2. "Your links are getting clicks, but visitors aren't staying. Here's what might be causing it."

### Body Block
"Your exit rate is higher than optimal. Common causes:
- **Mismatched messaging**: Your promotional content doesn't match landing page experience
- **Slow load times**: Mobile visitors need fast-loading pages
- **Poor mobile experience**: Most traffic is mobile - is your experience optimized?

We can help you audit and improve your content flow."

### Proof Block
"Companies that reduced exit rates by 20% saw a 35% increase in conversions and 50% increase in time on site."

### CTA Variants
1. "Get a free content audit"
2. "See content improvement examples"
3. "Request optimization tips"

---

## UPSELL: Expansion Ready

### Signal/Trigger
High feature adoption, strong engagement patterns, and consistent usage indicating readiness for premium tier.

### Communication Type
Upsell / expansion opportunity

### Subject Line Variants
1. "You're ready for the next level"
2. "Unlock {tier_name} features for your team"
3. "Your usage shows you're ready for more"

### Opener Variants
1. "You've been crushing it with {product_name}. Your feature adoption and engagement patterns show you're ready for {tier_name} capabilities."
2. "Based on how you're using {product_name}, we think you'd benefit significantly from our {tier_name} features."

### Body Block
"You're already using {feature_count} features effectively. Here's what {tier_name} would unlock:
- **Advanced Analytics**: Deeper attribution and ROI tracking
- **API Access**: Integrate {product_name} into your existing systems
- **Custom Branding**: White-label experience for your brand
- **Dedicated Support**: Priority access to our success team"

### Proof Block
"Companies like {proof_company} upgraded to {tier_name} and saw 2x improvement in efficiency and 40% time savings."

### CTA Variants
1. "See {tier_name} features"
2. "Schedule an upgrade consultation"
3. "Get a custom ROI estimate"

---

## ADVOCACY: Power User

### Signal/Trigger
Top 10% of users by engagement, high feature adoption, consistent activity.

### Communication Type
Recognition / loyalty program / advocacy

### Subject Line Variants
1. "You're a {product_name} power user!"
2. "Thank you for being one of our top users"
3. "Exclusive: Early access for power users like you"

### Opener Variants
1. "You're in the top 10% of {product_name} users by engagement. We wanted to recognize that and share some exclusive opportunities."
2. "Your usage of {product_name} is exceptional. As a power user, you get early access to new features and programs."

### Body Block
"As a power user, here's what's available to you:
- **Beta Access**: Try new features before general release
- **Case Study Opportunity**: Share your success (with incentives)
- **Referral Program**: Earn credits by introducing colleagues
- **Direct Product Input**: Shape our roadmap based on your needs"

### Proof Block
"Power users like {proof_company} have helped shape features that now benefit thousands of customers."

### CTA Variants
1. "Join the power user program"
2. "Share your {product_name} story"
3. "Refer a colleague"

---

## WIN_BACK: At Risk - High Value

### Signal/Trigger
High-value customer with declining engagement, significant revenue at risk.

### Communication Type
Executive outreach / strategic review

### Subject Line Variants
1. "Let's connect this week"
2. "Important: Your {product_name} partnership"
3. "Scheduling a strategic review"

### Opener Variants
1. "I'm reaching out because you're an important partner, and I want to ensure you're getting maximum value from {product_name}."
2. "As one of our valued customers, I wanted to personally check in and understand how we can better support your team."

### Body Block
"I've noticed some changes in your usage patterns and want to make sure everything is working well for your team. I'd like to:
- Review your current {product_name} implementation
- Understand any challenges you're facing
- Discuss optimizations specific to {vertical}
- Ensure you're leveraging all available features"

### Proof Block
"Our customers who participate in regular strategic reviews report 30% higher satisfaction and identify significant additional value on average."

### CTA Variants
1. "Schedule a strategic review"
2. "Let's connect this week"
3. "Request executive briefing"

---

## ONBOARDING: New Implementation

### Signal/Trigger
New customer, recently onboarded, in early activation phase.

### Communication Type
Onboarding / success planning

### Subject Line Variants
1. "Welcome to {product_name}!"
2. "Your 30-day success plan is ready"
3. "Let's make your first month amazing"

### Opener Variants
1. "Welcome to {product_name}! We're excited to partner with you. Here's your personalized onboarding plan."
2. "Congratulations on choosing {product_name}! Let's make sure you see value quickly."

### Body Block
"Your 30/60/90 day success plan:
**Day 1-30**: Foundation
- Complete initial setup and configuration
- Configure tracking and analytics
- Train your team on the basics

**Day 31-60**: Optimization
- Launch your first {use_case}
- Analyze performance data
- Iterate based on results

**Day 61-90**: Scale
- Expand to additional use cases
- Integrate with your existing tools
- Measure ROI and plan growth"

### Proof Block
"Teams that follow this 30/60/90 plan achieve proficiency 2x faster and report 40% higher satisfaction with their {product_name} investment."

### CTA Variants
1. "Start your onboarding journey"
2. "Schedule kickoff call"
3. "Access training resources"

---

## DISCOVERY: Needs Classification

### Signal/Trigger
Insufficient data to classify. New account with limited activity or unclear use case.

### Communication Type
Discovery / qualification

### Subject Line Variants
1. "How can we help?"
2. "Let's find the right fit for your needs"
3. "Quick question about your goals"

### Opener Variants
1. "We'd love to understand your goals better so we can tailor our support."
2. "To help you get the most from {product_name}, we'd like to learn more about your use case."

### Body Block
"Every organization uses {product_name} differently. To provide the best support, we'd like to know:
- What's your primary use case? (e.g., marketing, operations, customer engagement)
- What outcomes are most important? (e.g., lead generation, analytics, efficiency)
- What's your team size using {product_name}?

A quick 10-minute call could help us customize your experience."

### Proof Block
"Teams that complete our quick discovery call see 60% faster time-to-value and higher feature adoption."

### CTA Variants
1. "Schedule a discovery call"
2. "Take a quick survey"
3. "Tell us about your goals"

---

## Usage Notes

### Selecting Templates
1. **Signal Detection**: Use behavioral data to identify which reason code applies
2. **Primary Code**: If multiple codes apply, select the most actionable or highest-value signal
3. **Variant Selection**: Rotate through subject/CTA variants for A/B testing

### Personalization
1. Replace all `{variable}` placeholders with actual data
2. Use your CRM's token syntax for contact-level personalization
3. Pull metrics from your data warehouse for specific numbers

---

## CRM Property Mapping

### Generic Pattern
Map generated copy to CRM contact/lead properties for personalized sending.

| Copy Block | Semantic Name | Description |
|------------|---------------|-------------|
| Subject | `generated_subject` | AI-generated subject line |
| Opener | `generated_opener` | Personalized opening paragraph |
| Body | `generated_body` | Main content block |
| Proof | `generated_proof` | Social proof / data point |
| CTA | `generated_cta` | Call-to-action text |
| Reason Code | `reason_code` | Semantic code (REENGAGEMENT, etc.) |
| Cohort ID | `cohort_id` | Batch/cohort identifier |

### CRM-Specific Mapping

#### HubSpot
```json
{
  "ai_subject": "generated_subject",
  "ai_opener": "generated_opener",
  "ai_body_block_1": "generated_body",
  "ai_proof_block": "generated_proof",
  "ai_cta": "generated_cta",
  "ai_reason_code": "reason_code",
  "ai_cohort_id": "cohort_id"
}
```

#### Salesforce
```json
{
  "Generated_Subject__c": "generated_subject",
  "Generated_Opener__c": "generated_opener",
  "Generated_Body__c": "generated_body",
  "Generated_Proof__c": "generated_proof",
  "Generated_CTA__c": "generated_cta",
  "Reason_Code__c": "reason_code",
  "Cohort_Id__c": "cohort_id"
}
```

#### Marketo
```json
{
  "generatedSubject": "generated_subject",
  "generatedOpener": "generated_opener",
  "generatedBody": "generated_body",
  "generatedProof": "generated_proof",
  "generatedCta": "generated_cta",
  "reasonCode": "reason_code",
  "cohortId": "cohort_id"
}
```

#### Microsoft Dynamics
```json
{
  "mh1_generatedsubject": "generated_subject",
  "mh1_generatedopener": "generated_opener",
  "mh1_generatedbody": "generated_body",
  "mh1_generatedproof": "generated_proof",
  "mh1_generatedcta": "generated_cta",
  "mh1_reasoncode": "reason_code",
  "mh1_cohortid": "cohort_id"
}
```

### Creating Custom Properties

When setting up your CRM, create these properties:

| Property | Type | Description |
|----------|------|-------------|
| Subject | Single-line text | Max 200 chars |
| Opener | Multi-line text | Max 1000 chars |
| Body | Multi-line text | Max 5000 chars |
| Proof | Multi-line text | Max 1000 chars |
| CTA | Single-line text | Max 100 chars |
| Reason Code | Dropdown/Enum | REENGAGEMENT, CONVERSION, RETENTION, UPSELL, ADVOCACY, WIN_BACK, ONBOARDING, DISCOVERY |
| Cohort ID | Single-line text | Format: YYYY-MM-DD_[identifier] |

---

## Quality Checks

Before sending, verify:
- [ ] All placeholders are replaced with actual values
- [ ] Metrics are accurate and up-to-date
- [ ] Subject line is under 50 characters
- [ ] Proof block cites realistic, defensible statistics
- [ ] CTA matches the communication type
- [ ] Tone aligns with brand voice guide

---

## Related Files
- `prompts/email_copy_generation.md` - Generation instructions
- `prompts/email_analysis_rubric.md` - Scoring rubric for email quality
- `skills/email-copy-generator/SKILL.md` - Skill definition for automated generation
