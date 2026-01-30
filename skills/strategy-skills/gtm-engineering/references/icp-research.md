<deprecated>
**This reference has been incorporated into the `gtm-strategy-consultant` agent.**

ICP research requires strategic analysis and professional expertise that belongs in an agent context.
The agent contains full ICP research frameworks, persona development guidelines, and trigger event mapping.
</deprecated>

<objective>
This reference provides guidelines for researching a company's Ideal Customer Profile (ICP) and buyer personas to inform watcher recommendations.
</objective>

<research_sources>
## Research Sources

**Primary Sources (Most Reliable):**
1. Company website - About, Customers, Case Studies, Pricing pages
2. LinkedIn company page - Description, employee count, industry
3. G2/Capterra - Product category, customer reviews, company size segments
4. Crunchbase - Funding, investors, company stage, employee count

**Secondary Sources:**
5. Recent news/press releases - Strategic direction, new markets
6. Job postings - Roles they're hiring indicate priorities
7. Executive LinkedIn profiles - Background reveals target market insights
8. Competitor analysis - Similar companies reveal market positioning
</research_sources>

<icp_framework>
## ICP Research Framework

Analyze these dimensions:

<dimension name="target_company_profile">
### Target Company Profile

**Firmographics:**
- Industry/vertical (e.g., SaaS, FinTech, Healthcare)
- Company size (employee count ranges)
- Revenue range (if available)
- Geography (regions they serve)
- Company stage (startup, growth, enterprise)

**Technographics:**
- Tech stack signals (what technologies do their customers use?)
- Integration requirements
- Platform dependencies

**Indicators to look for:**
- Customer logos on website
- Case study companies
- Pricing tier names (Startup, Growth, Enterprise)
- "Built for X" messaging
</dimension>

<dimension name="buyer_personas">
### Buyer Personas

**Primary Buyer:**
- Job title(s) that typically buy
- Department (Sales, Marketing, Engineering, etc.)
- Seniority level
- Key responsibilities

**Economic Buyer:**
- Who signs the check?
- Budget holder title
- Approval process indicators

**Influencers:**
- Technical evaluators
- End users
- Champions

**Indicators to look for:**
- "Book a demo" form fields (role, company size)
- Customer testimonials (who's quoted?)
- Content topics (what roles would care?)
- Pricing page language
</dimension>

<dimension name="sales_motion">
### Sales Motion

**Product-Led Growth (PLG):**
- Free trial/freemium
- Self-serve signup
- Low touch initial sale
- Signals: "Start free", "No credit card", usage-based pricing

**Sales-Led (Enterprise):**
- Demo request required
- Custom pricing
- Multi-stakeholder process
- Signals: "Contact sales", "Request demo", "Enterprise" tier

**Hybrid:**
- PLG for SMB, sales-led for enterprise
- Land and expand model
- Signals: Mix of self-serve and "Talk to sales"

**Why this matters for watchers:**
- PLG companies benefit from volume signals (market watchers)
- Enterprise companies need specific account signals (account watchers)
</dimension>

<dimension name="trigger_events">
### Trigger Events

What events indicate someone needs this product?

**Growth Triggers:**
- Hiring in specific roles (need the product to scale)
- Funding announcement (budget unlocked)
- Headcount growth (operational complexity)

**Change Triggers:**
- Leadership changes (new priorities)
- M&A activity (integration needs)
- Office expansion (new markets)

**Pain Triggers:**
- Competitor activity (competitive pressure)
- Industry news (regulatory changes)
- Tech stack changes (migration needs)

**Questions to answer:**
- When does their ICP suddenly need this solution?
- What events precede typical buying cycles?
- What signals indicate budget availability?
</dimension>
</icp_framework>

<mapping_to_watchers>
## Mapping ICP to Watcher Types

<mapping scenario="sales_team_target">
### For Companies Selling to Sales Teams

**ICP Characteristics:**
- Target: Sales leaders, RevOps, SDR managers
- Need: Lead intelligence, prospect signals

**Recommended Watchers:**
1. `linkedin-person-profile-updates` - Track when champions change jobs
2. `company-watch-linkedin-job-postings` - Hiring SDRs/AEs = sales team investment
3. `company-watch-funding-milestones` - Funded companies have budget
</mapping>

<mapping scenario="marketing_target">
### For Companies Selling to Marketing Teams

**ICP Characteristics:**
- Target: CMOs, Growth leads, Content marketers
- Need: Competitive intelligence, market trends

**Recommended Watchers:**
1. `company-watch-linkedin-posts` - Monitor competitor content
2. `company-watch-press-mentions` - Industry news tracking
3. `job-posting-with-keyword-and-location` - Market-wide hiring trends
</mapping>

<mapping scenario="enterprise_sales">
### For Enterprise Sales Motions

**ICP Characteristics:**
- Long sales cycles, multi-stakeholder
- Need: Specific account intelligence

**Recommended Watchers:**
1. `company-watch-linkedin-job-postings` - Track hiring at target accounts
2. `linkedin-person-profile-updates` - Monitor key contacts
3. `company-watch-headcount-growth` - Identify scaling accounts
</mapping>

<mapping scenario="smb_volume">
### For SMB/Volume Sales

**ICP Characteristics:**
- Short sales cycles, high volume
- Need: Market-wide signals to find ready buyers

**Recommended Watchers:**
1. `job-posting-with-keyword-and-location` - Market hiring signals
2. `company-watch-funding-milestones` - Newly funded startups
3. `company-watch-headcount-growth` - Growing companies by criteria
</mapping>
</mapping_to_watchers>

<persona_analysis>
## Persona Analysis Questions

**For Sales Leaders:**
- What are their quota pressures?
- How do they currently find leads?
- What signals would indicate a hot lead?

**For Marketing Leaders:**
- How do they track competitors?
- What metrics do they report on?
- How do they identify content opportunities?

**For RevOps/Growth:**
- What data feeds their scoring models?
- How automated is their pipeline?
- What integrations matter?

**For Executives:**
- What strategic decisions need market data?
- How do they track competitive landscape?
- What board metrics need real-time signals?
</persona_analysis>

<research_checklist>
## Research Checklist

Before recommending watchers, verify:

- [ ] Identified primary industry/vertical
- [ ] Determined company size targets
- [ ] Identified 2-3 key buyer personas
- [ ] Understood sales motion (PLG vs enterprise)
- [ ] Identified top 3 trigger events
- [ ] Mapped triggers to specific watcher types
- [ ] Considered both account and lead-level needs
- [ ] Identified any unique use cases for their business
</research_checklist>
