---
name: cold-email-personalization
description: Craft research-driven cold emails with bracketed-variable personalization, "poke the bear" openers, custom signal hunting, follow-up sequences, and strict QA. Use for cold outbound email ideation, drafting, variant testing, campaign review, or follow-up sequences.
version: "1.0.0"
status: active
---

<essential_principles>
<philosophy>
**Shorter & Punchier > Longer**
- Target: 50-90 words (not 60-120)
- Every word must earn its place
- Cut 3 times: fluff (20%), compress (15%), adjectives (10%)
- Should read aloud in under 20 seconds

**Research IS the Personalization**
- Custom signals > clever copy
- 10-minute research method max
- If no signal found after 10 min → use whole-offer strategy OR skip

**Earn Replies, Not Just Meetings**
- Confirm situation before selling
- Low-effort CTAs (5 words or less to reply)
- Value-exchange when asking for meetings

**Two Valid Paths**
- **Path A:** Custom signal research (when you have time/data)
- **Path B:** Whole offer strategy (when data is limited)
- Both work—choose based on situation
</philosophy>

<email_structure>
**Line 1: Situation Recognition** (1 sentence)
Describe THEIR exact situation. Be direct.
- "Saw you posted about {{ai_generation}}—seems like it was {{days_ago}} days since the one before that."
- "Noticed you sell to {{job_titles}}."

**Line 2: Value Prop + Proof** (1-2 sentences MAX)
What you do + metric. No fluff.
- "We helped companies like Lemlist double down on social with our scheduling tool."
- "We've attributed a 4.7x increase in upgrades after adding product videos."

**Optional: The "Specifically" Line**
> "Specifically, it looks like you're trying to sell to {{customer_type}}, and we can help with that."

**Line 3: Low-Effort CTA** (1 sentence)
- "Worth a look?"
- "Is this still the case?"
- "Just confirm Vanta is a good example and I can send the engagers."
</email_structure>

<campaign_types>
| Type | When to Use | Key Feature |
|------|-------------|-------------|
| Custom Signal | Strong research data (case studies, pricing, reviews) | Lead with {{variable}} in first line |
| Creative Ideas | Can generate specific, credible ideas | 3 bullets, feature-constrained |
| Whole Offer | Limited data, self-selecting offer | Subject + preview = entire value prop |
| Fallback | Unsure if right person | "Let me know if {{employee_1}} or {{employee_2}} would be better..." |
</campaign_types>

<variable_schema_quick>
**Core:** {{first_name}}, {{company_name}}, {{role_title}}

**High-Signal:** {{tenure_years}}, {{recent_post_topic}}, {{competitor}}, {{stack_crm}}, {{hiring_roles}}

**AI-Generated:** {{ai_customer_description}}, {{ai_customer_type}}, {{ai_generation}}

**Case Study:** {{case_study_company}}, {{case_study_result}}, {{case_study_metric}}

**Format:** Always use `{{double_braces}}` - never invent facts
</variable_schema_quick>

<banned_phrases>
Delete these if found:
- "I hope this email finds you well"
- "I wanted to reach out"
- "We help companies..." (unless followed by case study proof)
- "Would love to schedule..."
- "Can I get 15 minutes?"
</banned_phrases>

<qa_quick_check>
Before sending:
1. First line = specific signal or AI insight?
2. 50-90 words?
3. CTA answerable in 5 words or less?
4. "Would I reply?" = YES?

If any NO → fix before sending.
</qa_quick_check>
</essential_principles>

<intake>
What would you like to do?

1. **Research a prospect** - Find custom signals for personalization
2. **Draft an email campaign** - Create Email 1 with variants
3. **Create follow-up sequence** - Email 2→3→4 with value rotation
4. **Generate creative ideas** - Feature-constrained ideas campaign
5. **QA before sending** - Run 11-point checklist

**Provide context:** Company name, your offer, any research you have.
</intake>

<routing>
| User Intent | Workflow | Required Reading |
|-------------|----------|------------------|
| "research", "find signals", "prospect" | workflows/research-prospect.md | references/variable-schema.md |
| "draft", "write", "create email", "campaign" | workflows/draft-campaign.md | references/examples.md |
| "follow-up", "sequence", "email 2", "email 3" | workflows/create-follow-ups.md | references/examples.md |
| "ideas", "creative", "bullets" | workflows/generate-creative-ideas.md | templates/creative-ideas-email.md |
| "qa", "check", "review", "before sending" | workflows/qa-before-send.md | - |

**If user provides company + offer without specifying:** Default to workflows/draft-campaign.md

**After routing:** Read the workflow file and follow it exactly.
</routing>

<cta_patterns>
**Confirmation (Earn Reply)**
- "Is this still the case?"
- "Curious—are you already doing X?"
- "Worth exploring?"

**Value-Exchange (Why Meet)**
- "...so I can understand the situation and plead your case to Google"
- "...to walk you through 3 custom ideas for {{company}}"
- "...so I can show you the engagers of your competitor's last 10 posts"

**Resource Offer (Low Commitment)**
- "Could I send you access to try it out?"
- "Would it be useful if I sent those over?"
</cta_patterns>

<opener_patterns>
**Classic:** "How are you currently handling {{process}}?"

**Status Pressure:** "Have you solved {{problem}} yet or is it still manual?"

**Efficiency:** "How are you doing {{task}} without adding headcount?"

**Risk-Based:** "How are you avoiding {{negative_outcome}} as you scale?"

**Binary:** "Is your process for {{area}} where you want it?"

**Redirect:** "Let me know if {{employee_1}} or {{employee_2}} would be better..."
</opener_patterns>

<output_format>
When drafting emails, return:
```json
{
  "v1": "email text",
  "v2": "email text",
  "v3": "email text",
  "subject_lines": ["option 1", "option 2", "option 3"],
  "notes": "Explanation of angles and why they should work",
  "used_variables": ["{{first_name}}", "{{ai_generation}}"],
  "missing_variables": ["{{tenure_years}}"],
  "score": 85,
  "recommended_variant": "v2"
}
```
</output_format>

<scoring_rubric>
| Dimension | Weight | What's Measured |
|-----------|--------|-----------------|
| Situation Recognition | 25 pts | Specific data about them? |
| Value Clarity | 25 pts | Clear offer + proof? |
| Personalization Quality | 20 pts | Custom signal OR AI insight? |
| CTA Effort | 15 pts | 5 words or less to reply? |
| Punchiness | 10 pts | 50-90 words? No fluff? |
| Subject Line | 5 pts | 2-4 words OR whole offer? |

**85+ = Ship it** | **70-84 = One more pass** | **<70 = Start over**
</scoring_rubric>

<reference_index>
**Workflows** (step-by-step procedures):
- workflows/research-prospect.md - 10-minute research method
- workflows/draft-campaign.md - Email generation workflow
- workflows/create-follow-ups.md - Email 2→4 sequences
- workflows/generate-creative-ideas.md - Feature-constrained ideas
- workflows/qa-before-send.md - 11-point QA checklist

**References** (domain knowledge):
- references/examples.md - 10 annotated real campaigns
- references/icp-objection-mapping.md - Role-play skeptical ICP
- references/opener-patterns.md - "Poke the bear" openers
- references/variable-schema.md - Full {{variable}} reference

**Templates** (output structures):
- templates/custom-signal-email.md
- templates/creative-ideas-email.md
- templates/whole-offer-email.md
- templates/icp-worksheet.md
</reference_index>

<success_criteria>
A good cold email:
- Opens with specific signal proving you did research
- Under 90 words (tighter is better)
- Has a CTA they can answer in 5 words or less
- Scores 85+ on the rubric
- Passes the "Would I reply?" test
</success_criteria>
