# Execution Plan: Additions Integration

**Plan ID:** additions-001
**Created:** 2026-01-29
**Status:** PENDING_APPROVAL

---

## Overview

This plan integrates new capabilities from the Additions folder into the MH1 system:
- **Part 1:** Port 15 new skills into the skills registry
- **Part 1B:** Rename "plans" to "modules" with MRD template
- **Part 2:** Review learnings from PDFs and apply improvements
- **Part 3:** Agent School - extract insights from MKT1 resources

---

## Phase 1: New Skills Integration

### 1.1 Vibe-Skills Claude Code Skills (11 skills)

| Skill | Domain | Description | Priority |
|-------|--------|-------------|----------|
| `brand-voice` | content | Define/extract brand voice profiles | P0 |
| `positioning-angles` | content | Find differentiated positioning angles | P0 |
| `orchestrator` | meta | Marketing skill routing/orchestration | P0 |
| `keyword-research` | campaign | SEO keyword strategy and clusters | P1 |
| `seo-content` | content | SEO-optimized content creation | P1 |
| `direct-response-copy` | content | Conversion copy (landing pages, ads) | P1 |
| `email-sequences` | content | Email sequence building | P1 |
| `lead-magnet` | content | Lead magnet concept creation | P1 |
| `newsletter` | content | Newsletter edition creation | P1 |
| `content-atomizer` | content | Repurpose content across platforms | P2 |
| `bright-data` | campaign | Web scraping via Bright Data | P2 |

### 1.2 API Integration Skills (4 skills)

| Skill | Domain | Description | Priority |
|-------|--------|-------------|----------|
| `cold-email-personalization` | campaign | Research-driven cold email drafting | P1 |
| `foreplay-ads` | campaign | Ad intelligence from Foreplay API | P1 |
| `gtm-engineering-proposal` | research | TAM/decision-maker data from Crustdata | P1 |
| `dataforseo-data` | research | SEO data from DataForSEO API | P2 |

### 1.3 Implementation Steps

**Step 1: Create skill directory structure**
```
skills/
  brand-voice/
    SKILL.md
    references/      # Copy from source
    workflows/       # If exists
    templates/       # If exists
```

**Step 2: Adapt SKILL.md to template format**
- Add required frontmatter (metadata, version, SLA)
- Add inputs/outputs tables
- Add quality criteria
- Add production readiness checklist

**Step 3: Update skill_domains.yaml**
- Add all 15 new skills to appropriate domains
- Update domain_config if needed

**Step 4: Create integration tests**
- Verify each skill loads correctly
- Test CLI invocation
- Validate output schemas

---

## Phase 1B: Plans → Modules Rename + MRD Template

### 1B.1 Directory Restructure

**Current:**
```
plans/
  {client}/
    {plan-name}.plan.md
```

**New:**
```
modules/
  {client}/
    {module-name}/
      PLAN.md          # Execution plan (current format)
      MRD.md           # Module Requirements Document
      outputs/         # Generated outputs
```

### 1B.2 MRD Template (Markdown)

Create `templates/MRD_TEMPLATE.md` with sections:

```markdown
# MRD: {Module Name}

## Metadata
| Field | Value |
|-------|-------|
| Status | Not Started / In Progress / Complete |
| Priority | P0 / P1 / P2 |
| Owner | {team/person} |
| Sprint | {duration} |
| Created | {date} |
| Updated | {date} |
| Client | {client_id} |

---

## Executive Summary
{2-3 paragraph overview of the module}

---

## Problem Statement

### Why This Matters
{Business impact and urgency}

---

## Objectives

### Primary Goal
{One sentence}

### Success Criteria
1. {Measurable outcome 1}
2. {Measurable outcome 2}
3. {Measurable outcome 3}

---

## Scope

### In Scope
- {Item 1}
- {Item 2}

### Out of Scope
- {Item 1}
- {Item 2}

---

## Approach & Methodology

### Phase 1: {Name} (Days X-Y)
{Activities and deliverables}

### Phase 2: {Name} (Days X-Y)
{Activities and deliverables}

---

## Dependencies & Blockers

### Critical Dependencies
- [ ] {Dependency 1}
- [ ] {Dependency 2}

### Known Blockers
- {Blocker and mitigation}

---

## Success Metrics

### Quantitative
- {Metric 1}
- {Metric 2}

### Qualitative
- {Criterion 1}
- {Criterion 2}

---

## Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| {Risk 1} | High/Med/Low | High/Med/Low | {Action} |

---

## Timeline & Milestones

| Milestone | Target Date | Status |
|-----------|-------------|--------|
| {Milestone 1} | {date} | Pending |

---

## Stakeholders

| Role | Person | Responsibility |
|------|--------|----------------|
| Owner | {name} | {responsibility} |
| Builder | {name} | {responsibility} |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {date} | {author} | Initial |
```

### 1B.3 Migration Steps

1. Rename `plans/` directory to `modules/`
2. Create MRD template at `templates/MRD_TEMPLATE.md`
3. Update `lib/planner.py` to use `modules/` path
4. Update CLI references in `mh1`
5. Migrate existing plans to new structure

---

## Phase 2: Learnings Integration

### 2.1 PDF Review Queue

| PDF | Topic | Expected Learnings |

|-----|-------|-------------------|
| AGENTS.md outperforms skills - Vercel | Agent architecture | AGENTS.md file patterns, skill vs agent tradeoffs |
| Hightouch long-running agent harness | Agent orchestration | Long-running task patterns, state management |
| Case Study - Nazeem | Implementation case study | Real-world agent deployment |

### 2.2 Review Process

For each PDF:
1. Extract key concepts and patterns
2. Compare to current MH1 architecture
3. Identify applicable improvements
4. Document in `knowledge/knowledge_base/concepts/`
5. Create tickets for actionable changes

### 2.3 Potential Improvement Areas

Based on PDF titles, likely learnings:
- **AGENTS.md pattern:** Consider if we should adopt AGENTS.md files alongside SKILL.md
- **Long-running harness:** Improve our async task handling, checkpointing
- **Agent evaluation:** Better metrics for skill vs agent performance

---

## Phase 3: Agent School - MKT1 Resource Extraction

### 3.1 Resource Categories (90 links)

| Category | Count | Type | Access Method |
|----------|-------|------|---------------|
| Marketing Strategy | 8 | Google Docs/Sheets | WebFetch/Browser |
| Planning | 12 | Google Docs/Sheets | WebFetch/Browser |
| Growth Marketing | 7 | Google Docs/Sheets/Figma | WebFetch/Browser |
| Product Marketing | 9 | Google Docs/Sheets/Figma | WebFetch/Browser |
| Content Marketing | 9 | Google Docs/Sheets | WebFetch/Browser |
| Brand and Creative | 7 | Google Docs/Sheets/Figma | WebFetch/Browser |
| Campaign Planning | 6 | Google Docs/Sheets | WebFetch/Browser |
| Analytics and Ops | 6 | Google Docs/Sheets | WebFetch/Browser |
| Web | 3 | Google Docs/Figma | WebFetch/Browser |
| Team Building | 3 | Google Docs/Figma | WebFetch/Browser |
| Hiring | 6 | Google Docs | WebFetch/Browser |
| Microtools | 5 | Various | WebFetch/Browser |

### 3.2 Extraction Strategy

**Challenge:** Many resources require authentication (Google Docs, Figma)

**Approach:**
1. **Public resources:** Use WebFetch directly
2. **Google Docs/Sheets:** Use browser automation with login
3. **Figma boards:** Use browser automation with login
4. **Loom videos:** Extract transcripts via API/browser

### 3.3 Storage Architecture

```
knowledge/
  knowledge_base/
    mkt1-library/
      marketing-strategy/
        {resource-slug}.md
      planning/
        {resource-slug}.md
      growth-marketing/
        {resource-slug}.md
      ... (each category)
```

### 3.4 Knowledge Node Format

Each extracted resource becomes a knowledge node:
```yaml
---
name: {resource-name}
type: template
lifecycle: validated
confidence: 0.9
source: MKT1 Template Library
source_url: {original_url}
category: {category}
related_concepts: []
---

# {Resource Name}

## Summary
{AI-generated summary}

## Key Insights
{Extracted insights}

## Template/Framework
{The actual content}

## Application Notes
{How to use in MH1 context}
```

### 3.5 Intelligence System Integration

After extraction:
1. Store in Firebase via `intelligence_bridge.py`
2. Index for semantic search
3. Link to relevant skills
4. Track usage and effectiveness

---

## Execution Order

### Week 1: Foundation

| Day | Task | Dependencies |
|-----|------|--------------|
| 1-2 | Phase 1B: Plans → Modules rename | None |
| 1-2 | Phase 1B: MRD template creation | None |
| 2-3 | Phase 1: Port P0 skills (brand-voice, positioning-angles, orchestrator) | 1B |
| 3-4 | Phase 1: Update skill_domains.yaml | P0 skills |
| 4-5 | Phase 2: Review PDFs and document learnings | None |

### Week 2: Expansion

| Day | Task | Dependencies |
|-----|------|--------------|
| 1-2 | Phase 1: Port P1 skills (6 content skills) | Week 1 |
| 2-3 | Phase 1: Port P1 API skills (cold-email, foreplay, gtm) | Week 1 |
| 3-4 | Phase 3: Set up MKT1 extraction pipeline | None |
| 4-5 | Phase 3: Extract priority resources (top 20) | Pipeline |

### Week 3: Integration & Testing

| Day | Task | Dependencies |
|-----|------|--------------|
| 1-2 | Phase 1: Port P2 skills (content-atomizer, bright-data, dataforseo) | Week 2 |
| 2-3 | Phase 3: Complete MKT1 extraction | Week 2 |
| 3-4 | Integration testing: All skills through CLI | All phases |
| 4-5 | Documentation and cleanup | Testing |

---

## Success Criteria

### Phase 1: Skills
- [ ] All 15 new skills in `skills/` directory
- [ ] All skills in `skill_domains.yaml`
- [ ] All skills loadable via CLI
- [ ] Integration tests pass

### Phase 1B: Modules
- [ ] `plans/` renamed to `modules/`
- [ ] MRD template created
- [ ] Existing plans migrated
- [ ] CLI updated

### Phase 2: Learnings
- [ ] All 3 PDFs reviewed
- [ ] Key concepts documented
- [ ] Applicable improvements identified
- [ ] At least 2 improvements implemented

### Phase 3: Agent School
- [ ] Extraction pipeline working
- [ ] 50+ resources extracted
- [ ] Stored in knowledge base
- [ ] Indexed in intelligence system

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Google Docs auth fails | High | Use manual extraction fallback |
| Skill format incompatibility | Medium | Adapt template during port |
| PDF content not actionable | Low | Document as research |
| MKT1 resources outdated | Low | Validate freshness dates |

---

## Approval

To approve this plan:
- Change `Status:` above to `APPROVED`
- Run: `./mh1 execute-plan additions-001`

---

## Notes

- New skills from Vibe-Skills have excellent reference materials and examples
- MKT1 library is a gold mine for marketing frameworks
- Consider creating a "marketing-orchestrator" agent that uses the orchestrator skill
- Phase 3 may require setting up persistent browser sessions for authenticated access
