# MRD: {{MODULE_NAME}}

## Metadata
| Field | Value |
|-------|-------|
| Module ID | {{MODULE_ID}} |
| Client | {{CLIENT_ID}} |
| Status | {{STATUS}} |
| Template | competitive-intel |
| Priority | P1 |
| Owner | MH1 Engineering |
| Created | {{CREATED_AT}} |
| Updated | {{CREATED_AT}} |

---

## Executive Summary

{{TASK_DESCRIPTION}}

This module will deliver comprehensive competitive intelligence for {{CLIENT_ID}} including:
- Detailed competitor profiles
- Feature comparison matrix
- Positioning and messaging analysis
- SWOT analysis
- Strategic recommendations
- Sales-ready battle cards

---

## Problem Statement

### What Changed?
<!-- Examples:
- New competitor entered market
- Competitor changed positioning
- Need updated battle cards for sales
- Strategic planning requires competitive context
-->

### Why This Matters
<!-- Examples:
- Clear competitive intel improves win rates 20-30%
- Battle cards enable consistent competitive positioning
- Differentiation gaps lead to lost deals
-->

---

## Objectives

### Primary Goal
Deliver actionable competitive intelligence that enables clear differentiation and supports sales/marketing execution.

### Success Criteria
1. Complete profiles for all specified competitors
2. Feature comparison matrix with all focus areas
3. SWOT analysis identifying key threats and opportunities
4. 3+ actionable differentiation recommendations
5. Battle cards ready for sales use

---

## Scope

### In Scope
- Competitor company research
- Feature/capability comparison
- Positioning and messaging analysis
- SWOT analysis
- Strategic recommendations
- Battle card creation
- Social presence monitoring (optional)

### Out of Scope
- Pricing intelligence (unless specifically requested)
- Win/loss analysis from CRM data
- Customer interview synthesis
- Ongoing monitoring setup

---

## Competitors to Analyze

| # | Competitor | Website | Focus |
|---|------------|---------|-------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

---

## Focus Areas

- [ ] Positioning - How they position in market
- [ ] Features - Product capabilities comparison
- [ ] Messaging - Claims, value props, taglines
- [ ] Pricing - Pricing model and tiers (if available)
- [ ] Hiring - Team growth and focus areas
- [ ] Funding - Investment and runway signals
- [ ] Content Strategy - Content themes and approach

---

## Approach & Methodology

### Phase 1: Research
- Research each competitor company
- Gather public information (website, social, press)
- Enrich with external data (Crunchbase, LinkedIn)
- **Checkpoint:** Research complete

### Phase 2: Analysis
- Compare features and capabilities
- Analyze positioning and messaging
- Identify strengths and weaknesses
- **Checkpoint:** Analysis complete

### Phase 3: Strategic Synthesis
- Create SWOT analysis
- Identify differentiation opportunities
- Develop strategic recommendations
- **Checkpoint:** Strategy complete

### Phase 4: Deliverables
- Create feature comparison matrix
- Build battle cards
- Compile final report
- **Checkpoint:** Deliverables ready

---

## Skills to Execute

```yaml
skills:
  - name: research-company
    inputs:
      company_names: "{{COMPETITORS}}"
      depth: "detailed"
    checkpoint: true
    required: true
    loop: true  # Run for each competitor

  - name: research-competitors
    depends_on: research-company
    inputs:
      client_id: "{{CLIENT_ID}}"
      competitors: "{{COMPETITORS}}"
      focus_areas: ["positioning", "features", "messaging"]
    checkpoint: true
    required: true

  - name: positioning-angles
    depends_on: research-competitors
    inputs:
      client_id: "{{CLIENT_ID}}"
      competitive_context: true
    checkpoint: true
    required: false
```

---

## Dependencies & Blockers

### Critical Dependencies
- [ ] Competitor list defined (3-7 recommended)
- [ ] Company context available for baseline comparison
- [ ] Budget approved (estimated $15-40)

### Optional Dependencies
- [ ] Crunchbase API for funding/hiring data
- [ ] LinkedIn access for team research
- [ ] Existing competitive intel for validation

### Known Blockers
- None

---

## Success Metrics

### Quantitative
- All competitors profiled
- Feature matrix covers 10+ capabilities
- 3+ strategic recommendations
- Battle cards for each competitor

### Qualitative
- Analysis is accurate and current
- Recommendations are actionable
- Battle cards are sales-ready
- Differentiation opportunities are clear

---

## Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Limited public info | Medium | Medium | Use multiple sources, note gaps |
| Outdated information | Medium | Low | Cross-reference sources, date stamp |
| Competitor changed | Low | Medium | Flag for follow-up monitoring |
| Biased analysis | Medium | Low | Focus on objective comparisons |

---

## Timeline & Milestones

| Milestone | Target Date | Status |
|-----------|-------------|--------|
| Module Created | {{CREATED_AT}} | Complete |
| Research Complete | | Pending |
| Analysis Complete | | Pending |
| Deliverables Ready | | Pending |

---

## Stakeholders

| Role | Person | Responsibility |
|------|--------|----------------|
| Engineering Lead | MH1 Team | Research & analysis |
| Sales Lead | TBD | Battle card review |
| Marketing Lead | TBD | Positioning review |
| Product Lead | TBD | Feature comparison review |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {{CREATED_AT}} | MH1 | Initial MRD from competitive-intel template |
