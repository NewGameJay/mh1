<required_reading>
- templates/creative-ideas-email.md (output structure)
</required_reading>

<objective>
Generate 3 specific, credible ideas for a prospect that demonstrate your capabilities. Each idea must use ONE feature from your constraint box—never hallucinate capabilities you don't have.
</objective>

<why_this_works>
Creative Ideas campaigns are one of the highest-performing campaign types because:
- **Shows > Tells** (you're demonstrating capability, not claiming it)
- **Tailored to them** (not a template)
- **Low commitment** (they're evaluating ideas, not buying)
- **Sparks curiosity** ("Hmm, how would they do that?")
</why_this_works>

<critical_constraint>
**The Problem:** If you let AI generate ideas without constraints, it will hallucinate capabilities you don't have.

**The Solution:** Define 3-5 specific features you ACTUALLY offer (the "constraint box"), then generate ideas using ONLY those features.

**Bad (Unconstrained):**
```
"Generate 3 marketing ideas"
→ Build a referral program, start a podcast, launch TikTok campaign
→ Problem: You don't do any of these.
```

**Good (Constrained):**
```
"Generate 3 marketing ideas using ONLY: SEO content, paid social, email nurture"
→ SEO series around keyword gaps, paid campaign targeting [audience], email nurture for [segment]
→ Result: All credible, all deliverable.
```
</critical_constraint>

<process>
<step_1>
**Define Constraint Box**

List 3-5 specific features/capabilities you offer:

**Marketing Agency:**
- Paid social ads (Meta, LinkedIn, Google)
- SEO content creation
- Email marketing automation
- Landing page optimization

**Outbound Agency:**
- Multi-channel sequences (email, LinkedIn, calls)
- Data enrichment from 40+ sources
- AI-personalized first lines
- List building by ICP

**Product/Dev Shop:**
- API integrations
- Custom dashboards
- Workflow automation
- Product videos

**Content/Creative:**
- Product videos
- Case study creation
- Thought leadership content
- Email copywriting

**Your constraint box:**
1. _______________
2. _______________
3. _______________
4. _______________
5. _______________
</step_1>

<step_2>
**Research Their Company (5-7 min)**

Gather context:
- **What they sell** (product/service, who buys it)
- **Current approach** (based on website, LinkedIn, ads)
- **Gaps/opportunities** (what they're NOT doing, or doing poorly)
- **Competitive landscape** (who else is in their space)

Variables to capture:
- {{industry}}
- {{target_customer}}
- {{competitor}}
- {{content_gap}}
- {{keyword_cluster}}
- {{customer_segment}}
</step_2>

<step_3>
**Generate Ideas (One Per Feature)**

**Formula:**
```
[Action verb] + [Feature from constraint box] + [Specific to their company] + [Why it would help]
```

**Template:**
```
• [Do X] using [Feature Y] targeting [their specific thing]—would help with [their pain/goal]
```

**Example - Marketing Agency → SaaS Company:**

Constraint box: Paid social, SEO content, Email nurture

Research: Target customer = sales leaders, Competitor = HubSpot, Gap = no case studies

Ideas:
```
• Paid social campaign targeting sales leaders using LinkedIn's "job function" targeting—would help reach decision-makers directly instead of relying on organic only

• SEO content series around "CRM alternatives" and "[competitor] vs [your product]" based on keyword gaps—could capture high-intent searches

• Email nurture sequence for trial users who haven't converted, addressing objections from G2 reviews—would improve trial-to-paid conversion
```
</step_3>

<step_4>
**Quality Check**

Before including any idea, verify:

**✅ Uses ONE feature from constraint box?**
- If not → Rewrite to use actual capability

**✅ Specific to THEIR company?**
- Generic: "Create content for social media"
- Specific: "Product videos for your [category] showing use in different settings"

**✅ Explains the benefit?**
- Bad: "Run paid ads"
- Good: "Run paid ads targeting [audience]—would help with [goal]"

**✅ Credible (not hallucinated)?**
- Test: Could you actually deliver this?
- If no → It's hallucinated, remove it
</step_4>

<step_5>
**Format the Email**

**Subject:** 2-4 words ("Marketing ideas", "Quick ideas")

**Structure:**
```
{{First name}} – I was back on your site today and had some [marketing/creative/product] ideas for you.

{{Creative Ideas}}
• Idea 1: [Action using Feature X]—would help with [benefit]
• Idea 2: [Action using Feature Y]—could improve [goal]
• Idea 3: [Action using Feature Z]—might address [challenge]

But of course, I wrote this without knowing anything about your current bottlenecks and goals.

If it's interesting, we could hop on a call and I'd be happy to share what's working in the {{industry}} industry.
```
</step_5>
</process>

<examples>
**Example 1: Content Shop → E-commerce Brand**

Constraint box: Product videos, UGC creation, Email copy

Research: Fashion-conscious men, Static photos only, No video content

```
{{First name}},

I was on your site and had a few creative ideas for [Company]:

• Product videos showing your [product category] in different settings (office, weekend, travel)—we helped similar brands increase add-to-cart rates by 23% when buyers could see products in context

• UGC campaign collecting customer photos/videos—creates social proof and gives you content for Instagram/email without in-house production

• Email sequences segmented by style preference (classic vs modern vs casual) based on browsing behavior—would make campaigns feel personalized instead of one-size-fits-all

These are just initial thoughts without knowing your priorities.

Would it make sense to chat about what could move the needle for [Company]?
```

**Example 2: Dev Shop → B2B SaaS (Pricing Page Insight)**

Constraint box: Product videos, Interactive calculators, API integrations

Research: Starter vs Pro plans, Pro has API access, G2 says "setup confusing"

```
Subject: Starter vs. Professional plan

{{First name}} – had a question about Starter vs. Pro.

Starter is for platform access, Pro is for API integrations.

Do you have a product video showing how easy those integrations are and how much more sales leaders get if they upgrade?

Some other ideas that could help with upgrades:
• Interactive ROI calculator on pricing page showing time saved with Pro features—helps justify cost to decision-makers
• Custom onboarding flow for Pro trials highlighting integration benefits in first 3 days—reduces "I don't see the value" churn

We've attributed 4.7x increase in upgrades after adding product videos.

Worth a chat?
```
</examples>

<common_mistakes>
**Mistake 1: Unconstrained Ideas**
- "Launch TikTok, start podcast, build affiliate program"
- Problem: You don't do these. When they say yes, you're stuck.

**Mistake 2: Generic Ideas**
- "Improve your SEO, run paid ads, send more emails"
- Problem: Could apply to anyone. Not impressive.

**Mistake 3: No Benefit Explanation**
- "Create product videos"
- Problem: Why would they care? Add the "so what."

**Mistake 4: Too Many Ideas**
- "Here are 7 ideas..."
- Problem: Overwhelming. 3 ideas maximum.
</common_mistakes>

<output_format>
```json
{
  "constraint_box": ["Feature 1", "Feature 2", "Feature 3"],
  "research": {
    "target_customer": "value",
    "current_approach": "value",
    "gap_opportunity": "value"
  },
  "ideas": [
    {
      "feature_used": "Feature 1",
      "idea": "Full idea text with benefit"
    },
    {
      "feature_used": "Feature 2",
      "idea": "Full idea text with benefit"
    },
    {
      "feature_used": "Feature 3",
      "idea": "Full idea text with benefit"
    }
  ],
  "email": "Full formatted email",
  "subject_lines": ["Option 1", "Option 2"]
}
```
</output_format>

<success_criteria>
- Each idea uses ONE feature from constraint box
- Each idea is specific to their company
- Each idea explains the benefit
- Disclaimer included ("wrote without knowing bottlenecks")
- No hallucinated capabilities
</success_criteria>
