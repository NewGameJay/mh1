<required_reading>
- references/variable-schema.md (full variable reference)
</required_reading>

<objective>
Find 1-2 custom signals unique to this prospect in 10 minutes or less. Custom signals prove you did your homework and dramatically increase reply rates.
</objective>

<mindset>
**Bad research:** "Let me find their role and company size so I can plug them into my template."

**Good research:** "What is happening in their world RIGHT NOW that makes my solution urgent?"

The best signals are:
1. **Specific** (not "you're growing" but "you hired 12 SDRs in Q4")
2. **Recent** (last 90 days ideally, last 6 months max)
3. **Directionally aligned** with the pain your product solves
</mindset>

<process>
<step_1>
**Define Your Perfect Signal (1 minute)**

Complete this sentence before researching:
> "The ideal prospect would show evidence of **[specific behavior/change/problem]** because it means they're experiencing **[pain]** right now."

Examples:
- Data enrichment: "...evidence of **manual data entry** because it means they're **losing deals to bad data**"
- Sales coaching: "...evidence of **high new-hire counts** because it means **ramp time is killing pipeline**"
- Marketing ops: "...evidence of **fragmented tech stack** because they're **making decisions on gut, not data**"
</step_1>

<step_2>
**Tier 1: Hunt Case Studies (3 minutes)**

Go to company website → case studies/customers page

Extract:
- Customer type they serve
- Problem they solved
- Metric/outcome
- Timeframe

Variables to capture:
- {{case_study_company}}
- {{case_study_result}}
- {{case_study_metric}}
- {{case_study_timeframe}}

**If you find a strong case study signal → Stop here and draft the email.**
</step_2>

<step_3>
**Tier 2: Hunt Custom Signals (6-7 minutes)**

Based on who you're selling to:

| Selling To | Signals to Hunt | Where to Find |
|------------|-----------------|---------------|
| Sales teams | Hiring velocity, G2 reviews of their tools, quota mentions in job posts | LinkedIn jobs, G2, Glassdoor |
| Marketing | Competitor insights, pricing page, ad creative | SimilarWeb, Facebook Ad Library, their site |
| Ops | GitHub repos, Zapier templates, manual processes in job posts | GitHub, Zapier, job descriptions |
| Local businesses | Google reviews (negative = opportunity), follower counts | Serper/Google CID |
| SaaS | Pricing tiers, LinkedIn posts, funding news | Claygent + ZenRows, LinkedIn, Crunchbase |

**Tools:**
- **Claygent:** AI web scraper - find pricing pages, case studies, news
- **ZenRows:** Full page scraper - get complete text from any page
- **Serper:** Google search API - Google Places CID, reviews
- **SimilarWeb:** Competitor traffic, keyword overlap
- **LinkedIn:** Recent posts, hiring, follower counts

**If you find a Tier 2 signal → Draft the email.**
</step_3>

<step_4>
**Tier 3: Standard Variables (3-4 minutes - BACKUP)**

If no custom signals found, gather:
- LinkedIn: role, tenure, recent posts, follower count
- Company site: blog, press, events
- Hiring page: open roles, department growth
- Tech stack: footer badges, BuiltWith, job descriptions

**Decision point:**
- If Tier 3 only → Consider **whole-offer strategy** instead of custom signal
- If nothing after 10 min → Skip this prospect or use fallback campaign
</step_4>
</process>

<signal_hunt_queries>
**For hiring signals:**
- `site:linkedin.com/jobs "[company]" [role keywords]`
- `"[company name]" hiring [department]` (last 90 days filter)

**For tech stack:**
- `site:github.com "[company]"` or `"[domain]"`
- `site:zapier.com "[company]"` (templates = DIY solutions)
- Footer of their site → "powered by" badges

**For competitive pressure:**
- `site:g2.com "[product name]" review` (read 3-star reviews for pain)
- `"[company]" alternative` or `"switching from [their tool]"`
- `site:reddit.com "[company name]" problem`

**For content/messaging shifts:**
- Wayback Machine → compare homepage 6 months ago vs now
- LinkedIn posts by execs → themes, urgency
- Their email nurture (sign up!)
</signal_hunt_queries>

<so_what_test>
Before using a signal, ask:
1. **Is it recent?** (Older than 6 months = stale, skip it)
2. **Does it connect to MY offer?** (Hiring engineers ≠ relevant for sales tool)
3. **Would THEY care that I noticed?** (Public info everyone has = not impressive)

**Good:** "You posted about pipeline review taking 4 hours last week"
**Bad:** "I saw you have 200 employees" (everyone knows that)
</so_what_test>

<output>
Return the signals found:

```
Company: [name]
Time spent: [X minutes]

Tier 1 (Case Studies):
- {{case_study_company}}: [value]
- {{case_study_result}}: [value]

Tier 2 (Custom Signals):
- Signal found: [description]
- Variable: {{custom_signal}}: [value]
- Source: [where you found it]

Tier 3 (Standard):
- {{role_title}}: [value]
- {{tenure_years}}: [value]
- {{recent_post_topic}}: [value]

Recommended strategy: [Custom Signal | Whole Offer | Skip]
```
</output>

<success_criteria>
- Found at least 1 custom signal in under 10 minutes
- Signal is specific, recent, and aligned with offer
- Clear recommendation on which campaign strategy to use
</success_criteria>
