<required_reading>
- references/examples.md (see real campaigns with annotations)
- references/variable-schema.md (full variable reference)
</required_reading>

<objective>
Draft 3 email variants with subject lines for Email 1 of a cold campaign. Target 50-90 words, score 85+ on the rubric.
</objective>

<process>
<step_1>
**Gather Context**

Confirm you have:
- Company name and what they do
- Your offer (what you're selling)
- Research signals (from research-prospect workflow OR provided by user)
- Target role/persona

If missing research signals → Run workflows/research-prospect.md first OR use whole-offer strategy.
</step_1>

<step_2>
**Choose Campaign Strategy**

| Strategy | When to Use | First Line |
|----------|-------------|------------|
| Custom Signal | You have specific, recent signal | Lead with {{variable}} |
| Whole Offer | Limited data, self-selecting offer | Subject + preview = full value prop |
| Creative Ideas | Can generate specific ideas | "Had some ideas for you..." |
| Fallback | Unsure if right person | "Let me know if {{employee}} would be better..." |
</step_2>

<step_3>
**Draft Structure**

```
Subject: [2-4 words OR whole offer]

{{First_name}}—[Situation recognition with specific signal]

[Value prop + proof in 1-2 sentences]

[Optional: "Specifically, it looks like you're trying to sell to {{customer_type}}..."]

[Low-effort CTA]
```

**Target:** 50-90 words total (not including signature)
</step_3>

<step_4>
**Generate 3 Variants**

Each variant should use a different:
- Opener pattern (classic, status pressure, efficiency, risk-based, binary)
- Value prop angle (save time, save money, make money)
- CTA style (confirmation, value-exchange, resource offer)

**Variant 1:** Lead with strongest signal + best case study
**Variant 2:** Different opener pattern + different value prop
**Variant 3:** Tightest possible version (aim for 50 words)
</step_4>

<step_5>
**Generate 3 Subject Lines**

**Approach A: 2-4 Words (Intrigue)**
- "Partnership?"
- "Quick question"
- "Competitor insights"
- "Saw your post"

**Approach B: Whole Offer** (only if using whole-offer strategy)
- "Ever chase renters to pay on time?"
- Full value prop in subject + preview

**Test:** Could a colleague or customer send this? If yes, good.
</step_5>

<step_6>
**Run Punchiness Check**

For each variant, do 3 cutting passes:

**Pass 1: Delete fluff (cut 20%)**
- Remove greetings ("I hope this finds you well")
- Remove "I wanted to" / "I was wondering"
- Remove hedging ("perhaps", "maybe", "I think")

**Pass 2: Compress sentences (cut 15%)**
- Replace clauses with periods
- "We built a platform that can do X" → "We do X"

**Pass 3: Cut adjectives (cut 10%)**
- Keep only specific data ("4.7x", "23%")
- Delete vague adjectives ("great", "amazing", "powerful")
</step_6>

<step_7>
**Score Each Variant**

| Dimension | Weight | V1 | V2 | V3 |
|-----------|--------|----|----|----|
| Situation Recognition | 25 | | | |
| Value Clarity | 25 | | | |
| Personalization Quality | 20 | | | |
| CTA Effort | 15 | | | |
| Punchiness | 10 | | | |
| Subject Line | 5 | | | |
| **Total** | 100 | | | |

**85+ = Ship it** | **70-84 = One more pass** | **<70 = Start over**
</step_7>
</process>

<output_format>
```json
{
  "v1": "email text here",
  "v2": "email text here",
  "v3": "email text here",
  "subject_lines": ["option 1", "option 2", "option 3"],
  "notes": "V1 leads with hiring signal, V2 uses competitor angle, V3 is ultra-tight 52 words",
  "used_variables": ["{{first_name}}", "{{company_name}}", "{{hiring_spike}}"],
  "missing_variables": ["{{tenure_years}}", "{{recent_post_topic}}"],
  "scores": {"v1": 87, "v2": 82, "v3": 91},
  "recommended_variant": "v3"
}
```
</output_format>

<example_transformation>
**Before (112 words):**
"Hey Sarah, I hope this email finds you well! I wanted to reach out because I was on your website and I noticed that you seem to be selling to sales leaders and marketing executives. It looked like you're trying to help them improve their outbound processes and increase their pipeline generation. I had to assume you are probably using some outbound tactics considering I saw that John Smith is a BDR on your team based on his LinkedIn profile. I was wondering if you're thinking about how your team could be leveraging better data enrichment and GPT-4 technology to help streamline their prospecting efforts?"

**After (64 words):**
"{{First_name}}—saw you sell to {{job_titles}}.

Noticed {{SDR_name}} is a BDR on the team. Have you figured out how they could leverage better data and GPT-4 for prospecting, or still manual?

Most teams we work with save 10 min per prospect and 3x volume without adding headcount.

Worth a look?"

**What was cut:**
- All pleasantries (18 words)
- All "I wanted to" phrases (12 words)
- Redundant explanations (10 words)
- Total: 43% shorter
</example_transformation>

<success_criteria>
- All variants under 90 words
- At least one variant scores 85+
- Each variant uses different opener/value prop/CTA
- Variables properly formatted in {{double_braces}}
- No banned phrases present
</success_criteria>
