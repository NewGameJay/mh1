# Module: Lifecycle Audit

Version: v1.0.0  
Type: lifecycle  
Author: Josh / MH1  
Created: 2026-01-23  
Last updated: 2026-01-23

---

## Overview

The Lifecycle Audit module analyzes a company's customer lifecycle marketing operations to identify gaps, opportunities, and optimization strategies. It combines CRM data analysis, email performance scoring, and semantic analysis of sales communications.

**Value proposition:** Understand your customer lifecycle in 1 week, with actionable recommendations to improve retention and revenue.

---

## Target clients

- B2B SaaS companies with HubSpot
- E-commerce with lifecycle email programs
- Companies with 10K+ contacts in CRM

**Ideal client profile:**
- Using HubSpot (CRM + Marketing Hub)
- Has Snowflake or similar data warehouse
- Sends lifecycle emails (onboarding, nurture, win-back)
- Wants to improve customer retention metrics

---

## Deliverables

| Deliverable              | Format        | Description                      |
|--------------------------|---------------|----------------------------------|
| Discovery Report         | Markdown/PDF  | Data landscape and quality assessment |
| Lifecycle Analysis       | Markdown/PDF  | Stage-by-stage performance analysis |
| Email Performance Matrix | CSV/Airtable  | Email-level metrics and scores   |
| Recommendations Report   | Markdown/PDF  | Prioritized recommendations      |
| 90-Day Roadmap           | Markdown/PDF  | Implementation plan              |
| Executive Summary        | Markdown/PDF  | C-level overview (2 pages)       |

---

## Inputs required

| Input                    | Source        | Required | Description                      |
|--------------------------|---------------|----------|----------------------------------|
| HubSpot access           | API token     | Yes      | Read access to contacts, deals, emails |
| Snowflake access         | Credentials   | No       | Event data for deeper analysis   |
| Lifecycle stage mapping  | Document      | Yes      | Definition of customer stages    |
| Brand guidelines         | Document      | No       | Voice/tone for recommendations   |
| Business context         | Interview     | Yes      | Goals, priorities, constraints   |

---

## Process phases

### Phase 1: Discovery (Days 1-2)

**Objective:** Understand current state and data landscape.

**Activities:**
- [ ] Connect to HubSpot via MCP
- [ ] Connect to Snowflake (if available)
- [ ] Run discovery queries (table inventory, field mapping)
- [ ] Identify data quality issues
- [ ] Map customer journey stages to HubSpot properties
- [ ] Document data gaps

**Skills used:**
- `hubspot-discovery`
- `snowflake-explorer`
- `data-quality-checker`
- `lifecycle-mapper`

**Output:** Discovery summary document

---

### Phase 2: Lifecycle Analysis (Days 3-5)

**Objective:** Deep analysis of customer lifecycle performance.

**Activities:**
- [ ] Build cohort analysis by lifecycle stage
- [ ] Calculate stage conversion rates
- [ ] Identify time-in-stage distributions
- [ ] Analyze drop-off points
- [ ] Segment by customer attributes (industry, size, source)
- [ ] Compare against benchmarks

**Skills used:**
- `cohort-builder`
- `lifecycle-analyzer`
- `benchmark-comparator`

**Output:** Lifecycle analysis report with visualizations

---

### Phase 3: Email Performance Analysis (Days 4-5)

**Objective:** Evaluate email program effectiveness.

**Activities:**
- [ ] Pull email performance metrics from HubSpot
- [ ] Calculate open rates, click rates, unsubscribes by campaign type
- [ ] Semantic analysis of email copy (tone, clarity, CTA strength)
- [ ] Identify top and bottom performers
- [ ] Compare to industry benchmarks

**Skills used:**
- `email-performance-scorer`
- `copy-analyzer`
- `benchmark-comparator`

**Output:** Email performance matrix (CSV/Airtable)

---

### Phase 4: Sales Communication Analysis (Day 5)

**Objective:** Analyze sales team communication patterns.

**Activities:**
- [ ] Pull email logs and meeting transcripts (if available)
- [ ] Semantic analysis of sales conversations
- [ ] Identify common objections and responses
- [ ] Score communication quality by salesperson
- [ ] Find correlation with deal outcomes

**Skills used:**
- `transcript-analyzer`
- `objection-extractor`
- `salesperson-scorer`

**Output:** Sales communication insights

---

### Phase 5: Recommendations (Days 6-7)

**Objective:** Synthesize findings into actionable recommendations.

**Activities:**
- [ ] Prioritize findings by impact and effort
- [ ] Generate specific recommendations for each stage
- [ ] Create 90-day implementation roadmap
- [ ] Build executive summary
- [ ] Quality review (evaluation agent)

**Skills used:**
- `recommendation-generator`
- `roadmap-builder`
- `executive-summarizer`

**Output:** Final report package

---

## Pricing

| Tier        | Scope                          | Price       | Timeline    |
|-------------|--------------------------------|-------------|-------------|
| Starter     | HubSpot only, up to 50K contacts | $3,500    | 1 week      |
| Standard    | HubSpot + Snowflake, full analysis | $7,500   | 2 weeks     |
| Enterprise  | Full analysis + implementation support | $15,000 | 4 weeks     |

---

## Client handoff options

### Option A: Report package

- All deliverables as PDF/Markdown
- 1-hour walkthrough call
- 30-day Q&A support

### Option B: Report + Airtable dashboard

- All deliverables
- Interactive Airtable base with filters
- Self-serve exploration
- 60-day Q&A support

### Option C: Full implementation

- All deliverables
- HubSpot workflow setup (top 3 recommendations)
- Email template creation
- 90-day implementation support

---

## Success metrics

| Metric                   | Target        | How measured                     |
|--------------------------|---------------|----------------------------------|
| Insights delivered       | 10+           | Count in final report            |
| Recommendations          | 5-10          | Prioritized list                 |
| Data coverage            | 80%+          | Fields analyzed vs total         |
| Client satisfaction      | >= 4.5/5      | Post-engagement survey           |
| Time to delivery         | <= 7 days     | Calendar days                    |

---

## Dependencies

**Skills:**
- `hubspot-discovery`
- `snowflake-explorer`
- `data-quality-checker`
- `lifecycle-mapper`
- `cohort-builder`
- `lifecycle-analyzer`
- `email-performance-scorer`
- `copy-analyzer`
- `transcript-analyzer`
- `recommendation-generator`
- `roadmap-builder`

**Workflows:**
- `lifecycle-audit-workflow`

**MCPs:**
- `hubspot`
- `snowflake`

**APIs:**
- HubSpot API (contacts, companies, deals, emails)
- Snowflake (event data)

---

## Quality checklist

Before delivery, verify:
- [ ] Discovery report complete
- [ ] Lifecycle analysis with visualizations
- [ ] Email performance matrix populated
- [ ] Recommendations prioritized
- [ ] Roadmap with specific actions
- [ ] Executive summary (2 pages max)
- [ ] Evaluation agent passed (score >= 0.8)
- [ ] All data sources cited
- [ ] No placeholder text
- [ ] Human review completed

---

## Example engagement

**Client:** Flowcode  
**Tier:** Standard  
**Duration:** 2 weeks

**Key findings:**
1. 32M+ events in Snowflake with rich engagement data
2. Email performance varied significantly by salesperson
3. Onboarding sequence had 40% drop-off at stage 3
4. Top performers used specific language patterns

**Recommendations delivered:**
1. Revamp onboarding sequence with better stage 3 content
2. Standardize sales email templates based on top performers
3. Implement lifecycle stage triggers in HubSpot
4. Add intent scoring based on event data

**Client feedback:** "The insights were eye-opening. We're already seeing improvements from implementing the first recommendation."

---

## Changelog

### v1.0.0 (2026-01-23)
- Initial module definition
- Core skills identified
- Pricing established
- Quality checklist added

---

## Notes

- Requires at least 3 months of historical data for meaningful analysis
- Snowflake connection significantly improves analysis depth
- Sales transcript analysis requires explicit permission from client
- Allow 1-2 days buffer for data quality issues
