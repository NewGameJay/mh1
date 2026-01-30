# MRD: {{MODULE_NAME}}

## Metadata
| Field | Value |
|-------|-------|
| Module ID | {{MODULE_ID}} |
| Client | {{CLIENT_ID}} |
| Status | {{STATUS}} |
| Template | gtm-plan |
| Priority | P1 |
| Owner | MH1 Engineering |
| Created | {{CREATED_AT}} |
| Updated | {{CREATED_AT}} |

---

## Executive Summary

{{TASK_DESCRIPTION}}

This module will develop a comprehensive go-to-market strategy for {{CLIENT_ID}} including:
- Competitive landscape analysis
- Target persona definition
- Messaging and positioning framework
- Channel strategy recommendations
- Phased execution roadmap

---

## Problem Statement

### What Changed?
<!-- Examples:
- New product launching Q2
- Entering new market segment
- Competitor launched similar offering
- Need to differentiate positioning
-->

### Why This Matters
<!-- Examples:
- Clear GTM strategy increases launch success by 3x
- Differentiated positioning improves conversion 25-40%
- Coordinated launch captures market share faster
-->

---

## Objectives

### Primary Goal
Deliver a comprehensive, actionable GTM strategy that positions {{CLIENT_ID}} for market success.

### Success Criteria
1. Complete competitive analysis with SWOT for top 5 competitors
2. 2-3 validated target personas with pain points and buying triggers
3. Differentiated positioning with clear value proposition
4. Phased execution roadmap with milestones

---

## Scope

### In Scope
- Competitive landscape research and analysis
- Target market and persona definition
- Messaging framework development
- Positioning strategy
- Channel recommendations
- High-level execution roadmap

### Out of Scope
- Detailed campaign creative
- Media buying and ad spend allocation
- Sales enablement materials
- Product roadmap changes
- Pricing strategy (unless specifically requested)

---

## GTM Objective

**Primary Objective**: {{GTM_OBJECTIVE}}

| Objective | Focus Areas |
|-----------|-------------|
| New Product Launch | Awareness, positioning, launch timing |
| Market Expansion | New segments, localization, partnerships |
| Repositioning | Messaging pivot, competitive differentiation |
| Competitive Response | Counter-positioning, feature comparison |

---

## Approach & Methodology

### Phase 1: Research & Discovery
- Research company context and product details
- Analyze competitive landscape
- Identify market trends and opportunities
- **Checkpoint:** Research complete

### Phase 2: Persona Development
- Define target personas from data and research
- Map pain points and buying triggers
- Validate against existing customer data (if available)
- **Checkpoint:** Personas validated

### Phase 3: Positioning & Messaging
- Develop positioning statement
- Create messaging hierarchy
- Define key differentiators
- **Checkpoint:** Messaging framework complete

### Phase 4: Strategy & Roadmap
- Define channel strategy
- Create phased execution plan
- Set milestones and success metrics
- **Checkpoint:** GTM plan complete

---

## Skills to Execute

```yaml
skills:
  - name: research-company
    inputs:
      company_name: "{{COMPANY_NAME}}"
      include_market_context: true
    checkpoint: true
    required: true

  - name: research-competitors
    depends_on: research-company
    inputs:
      client_id: "{{CLIENT_ID}}"
      competitor_count: 5
    checkpoint: true
    required: true

  - name: extract-audience-persona
    depends_on: research-company
    inputs:
      client_id: "{{CLIENT_ID}}"
      persona_count: 3
    checkpoint: true
    required: true

  - name: positioning-angles
    depends_on: [research-competitors, extract-audience-persona]
    inputs:
      client_id: "{{CLIENT_ID}}"
    checkpoint: true
    required: true

  - name: gtm-engineering
    depends_on: positioning-angles
    inputs:
      client_id: "{{CLIENT_ID}}"
      objective: "{{GTM_OBJECTIVE}}"
    checkpoint: true
    required: false
```

---

## Dependencies & Blockers

### Critical Dependencies
- [ ] Company profile and product information
- [ ] Target market definition
- [ ] GTM objective clarified
- [ ] Budget approved (estimated $15-40)

### Optional Dependencies
- [ ] Existing customer data for persona validation
- [ ] Competitor intelligence already gathered
- [ ] Historical campaign performance data

### Known Blockers
- None

---

## Success Metrics

### Quantitative
- 5+ competitors analyzed
- 2-3 target personas defined
- 1 clear positioning statement
- 4+ week execution roadmap

### Qualitative
- Positioning is differentiated and defensible
- Personas resonate with sales/marketing team
- Roadmap is actionable and realistic
- Strategy addresses competitive threats

---

## Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Insufficient competitor data | High | Medium | Use web research, estimate from public info |
| Personas not validated | Medium | Medium | Cross-reference with CRM data if available |
| Generic positioning | High | Low | Focus on unique capabilities and proof points |
| Roadmap too aggressive | Medium | Medium | Phase milestones realistically |

---

## Timeline & Milestones

| Milestone | Target Date | Status |
|-----------|-------------|--------|
| Module Created | {{CREATED_AT}} | Complete |
| Research Complete | | Pending |
| Personas Defined | | Pending |
| Positioning Complete | | Pending |
| GTM Plan Delivered | | Pending |

---

## Stakeholders

| Role | Person | Responsibility |
|------|--------|----------------|
| Engineering Lead | MH1 Team | Research & analysis |
| Marketing Lead | TBD | Strategy review |
| Product Lead | TBD | Product context |
| Sales Lead | TBD | Persona validation |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {{CREATED_AT}} | MH1 | Initial MRD from gtm-plan template |
