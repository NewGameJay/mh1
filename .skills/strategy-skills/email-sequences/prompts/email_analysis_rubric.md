# Email Analysis Rubric
**Purpose**: Score existing email templates for psychological effectiveness
**Scale**: 1-5 (1 = Poor, 3 = Average, 5 = Excellent)

---

## Customization

To use this rubric for your company:
1. Replace example text with your product/service examples
2. Adjust scoring criteria based on your brand voice
3. Add industry-specific dimensions if needed
4. Customize proof expectations for your market

---

## Scoring Dimensions

### 1. Urgency (1-5)
- **1 (Poor)**: No urgency indicators, no time pressure
- **2**: Minimal urgency ("when you're ready")
- **3 (Average)**: Mild urgency ("don't miss out")
- **4**: Moderate urgency with deadline or scarcity
- **5 (Excellent)**: Strong, justified urgency with specific time pressure

**Industry Examples**:

| Score | B2B SaaS | E-commerce | Marketing Tech |
|-------|----------|------------|----------------|
| 1 | "Check out {product_name}" | "Browse our collection" | "See our platform" |
| 3 | "Don't miss new features" | "Sale ends this week" | "Limited beta spots" |
| 5 | "Your trial expires in 3 days" | "Only 12 left at this price" | "Lock in 2024 pricing by Friday" |

---

### 2. Social Proof (1-5)
- **1 (Poor)**: No social proof, no testimonials or data
- **2**: Generic proof ("thousands of users")
- **3 (Average)**: Specific but not relevant proof
- **4**: Relevant proof with numbers
- **5 (Excellent)**: Specific, relevant proof with context

**Industry Examples**:

| Score | B2B SaaS | E-commerce | Marketing Tech |
|-------|----------|------------|----------------|
| 1 | No proof mentioned | No proof mentioned | No proof mentioned |
| 3 | "Join 10,000+ companies" | "Loved by thousands" | "Used by top marketers" |
| 5 | "Companies like yours saw 45% higher ROI" | "Customers who bought this saved $500/year" | "Teams using this feature see 3x engagement" |

---

### 3. Value Proposition (1-5)
- **1 (Poor)**: Unclear value, generic benefits
- **2**: Vague value proposition
- **3 (Average)**: Clear but generic value
- **4**: Clear, specific value
- **5 (Excellent)**: Clear, personalized value with metrics

**Industry Examples**:

| Score | B2B SaaS | E-commerce | Marketing Tech |
|-------|----------|------------|----------------|
| 1 | "{product_name} is great" | "Great products" | "Powerful marketing" |
| 3 | "Helps you work more efficiently" | "Quality items at great prices" | "Reach more customers" |
| 5 | "You processed 150 tasks last month - here's how to automate 30% more" | "Based on your purchases, save $89 on items you buy monthly" | "Your last campaign had 24% open rate - here's how to hit 35%" |

---

### 4. Personalization (1-5)
- **1 (Poor)**: Name only, no other personalization
- **2**: Basic tokens (name, company)
- **3 (Average)**: Some behavior-based personalization
- **4**: Good personalization with usage stats
- **5 (Excellent)**: Deep behavior-based personalization

**Industry Examples**:

| Score | B2B SaaS | E-commerce | Marketing Tech |
|-------|----------|------------|----------------|
| 1 | "Hi {{firstname}}" | "Hi {{firstname}}" | "Hi {{firstname}}" |
| 3 | "We noticed you haven't logged in" | "We miss you!" | "Your account is waiting" |
| 5 | "Hi {{firstname}}, you completed 150 workflows in Q4 but haven't been active. Here's what you're missing..." | "Hi {{firstname}}, you loved [Product A] - it's back in stock with 20% off" | "Your Q4 campaigns hit 2M impressions. Here's how to double that..." |

---

### 5. Call to Action (1-5)
- **1 (Poor)**: Weak/unclear CTA, buried in text
- **2**: Clear but single, generic CTA
- **3 (Average)**: Clear CTA with some context
- **4**: Strong CTA with multiple options
- **5 (Excellent)**: Strong, multi-option CTA with urgency

**Examples** (Universal):
- 1: "Check it out"
- 3: "Log in now"
- 5: "Log in and explore new features" OR "Schedule a quick call"

---

### 6. Objection Handling (1-5)
- **1 (Poor)**: No objection handling
- **2**: Implicit handling (addresses concerns indirectly)
- **3 (Average)**: Some explicit handling
- **4**: Good objection handling
- **5 (Excellent)**: Explicit, comprehensive objection handling

**Industry Examples**:

| Score | B2B SaaS | E-commerce | Marketing Tech |
|-------|----------|------------|----------------|
| 1 | No objections addressed | No objections addressed | No objections addressed |
| 3 | "We understand you're busy" | "Free returns, no risk" | "No long-term contract" |
| 5 | "We know implementation concerns you. That's why we now offer free onboarding - you can be live in 2 hours" | "Worried about fit? Free returns + free exchanges, and our AI sizing is 95% accurate" | "Concerned about learning curve? New users are productive in 15 minutes with our guided setup" |

---

## Section Analysis

For each section (subject, opener, body, CTA), provide:
- **Text**: The actual text from the template
- **Score**: 1-5 rating
- **Notes**: Specific feedback on what works/doesn't work

---

## Improvement Opportunities

After scoring, identify 3-5 specific improvement opportunities:
1. What's missing?
2. What could be more specific?
3. What could be more personalized?
4. What objections aren't addressed?
5. What proof could be stronger?

---

## Industry-Specific Dimensions (Optional)

Add these dimensions based on your industry:

### B2B SaaS
- **Technical Credibility (1-5)**: Does it demonstrate product expertise?
- **ROI Clarity (1-5)**: Is the business value quantified?

### E-commerce
- **Product Relevance (1-5)**: Are recommended products well-matched?
- **Deal Clarity (1-5)**: Is the offer/discount clear and compelling?

### Marketing Tech
- **Data Insight (1-5)**: Does it use campaign data effectively?
- **Benchmark Comparison (1-5)**: Does it compare to industry standards?

---

## Output Format

### JSON Schema

```json
{
  "template_id": "string",
  "template_name": "string",
  "analysis_date": "ISO8601",
  "overall_score": "number (1-5)",
  "dimensions": {
    "urgency": {
      "score": "number",
      "notes": "string"
    },
    "social_proof": {
      "score": "number",
      "notes": "string"
    },
    "value_proposition": {
      "score": "number",
      "notes": "string"
    },
    "personalization": {
      "score": "number",
      "notes": "string"
    },
    "call_to_action": {
      "score": "number",
      "notes": "string"
    },
    "objection_handling": {
      "score": "number",
      "notes": "string"
    }
  },
  "sections": {
    "subject": {
      "text": "string",
      "score": "number",
      "notes": "string"
    },
    "opener": {
      "text": "string",
      "score": "number",
      "notes": "string"
    },
    "body": {
      "text": "string",
      "score": "number",
      "notes": "string"
    },
    "cta": {
      "text": "string",
      "score": "number",
      "notes": "string"
    }
  },
  "improvement_opportunities": [
    "string"
  ]
}
```
