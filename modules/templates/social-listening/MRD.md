# MRD: {{MODULE_NAME}}

## Metadata
| Field | Value |
|-------|-------|
| Module ID | {{MODULE_ID}} |
| Client | {{CLIENT_ID}} |
| Status | {{STATUS}} |
| Template | social-listening |
| Priority | P2 |
| Owner | MH1 Engineering |
| Created | {{CREATED_AT}} |
| Updated | {{CREATED_AT}} |

---

## Executive Summary

{{TASK_DESCRIPTION}}

This module will collect and analyze social media signals for {{CLIENT_ID}} including:
- LinkedIn, Twitter, and Reddit posts matching keywords
- ICP relevance scoring for prioritization
- Top signals for content inspiration
- Collection statistics and trend analysis

---

## Problem Statement

### What Changed?
<!-- Examples:
- Need fresh signals for content production
- Monitoring competitor mentions
- Tracking industry trends
- Building signal database for ongoing analysis
-->

### Why This Matters
<!-- Examples:
- Social signals inform 60%+ of content topics
- Early trend detection enables thought leadership
- Competitor monitoring reveals market shifts
-->

---

## Objectives

### Primary Goal
Collect and score social media signals to inform content strategy and surface engagement opportunities.

### Success Criteria
1. Collect posts from all specified platforms
2. Score posts for ICP relevance (1-10 scale)
3. Surface top 25+ high-relevance signals
4. Generate collection report with statistics

---

## Scope

### In Scope
- LinkedIn post collection (via keyword search)
- Twitter post collection (via keyword search)
- Reddit post collection (via keyword search)
- ICP relevance scoring
- Deduplication
- Firebase persistence

### Out of Scope
- Real-time monitoring (batch collection only)
- Sentiment analysis (separate module)
- Engagement/response to posts
- Historical trend analysis (> 30 days)

---

## Keywords

Keywords are loaded from: `clients/{{CLIENT_ID}}/social-listening/keywords.md`

### Keyword Categories
<!-- From keywords.md file -->
| Category | Keywords |
|----------|----------|
| Brand | |
| Product | |
| Competitors | |
| Industry | |
| Pain Points | |

---

## Approach & Methodology

### Phase 1: Keyword Processing
- Load keywords from keywords.md
- Build KEYWORDS_DATA structure
- Validate keyword count and format
- **Checkpoint:** Keywords ready

### Phase 2: Platform Scraping
- Execute platform searches in parallel
- LinkedIn keyword search
- Twitter keyword search
- Reddit keyword search
- **Checkpoint:** Raw posts collected

### Phase 3: Scoring & Enrichment
- Score posts for ICP relevance
- Add metadata (engagement, author profile)
- Deduplicate across platforms
- **Checkpoint:** Posts scored

### Phase 4: Persistence & Reporting
- Upload to Firebase
- Generate collection report
- Surface top signals
- **Checkpoint:** Collection complete

---

## Skills to Execute

```yaml
skills:
  - name: social-listening-collect
    inputs:
      client_id: "{{CLIENT_ID}}"
      platforms: ["linkedin", "twitter", "reddit"]
      date_range: "past-week"
    checkpoint: true
    required: true
```

---

## Dependencies & Blockers

### Critical Dependencies
- [ ] Keywords file exists at `clients/{{CLIENT_ID}}/social-listening/keywords.md`
- [ ] ICP context available for relevance scoring
- [ ] Firebase MCP configured
- [ ] Budget approved (estimated $5-15)

### Optional Dependencies
- [ ] Thought leader list for boosted relevance
- [ ] Competitor handles for SOV analysis

### Known Blockers
- None

---

## Success Metrics

### Quantitative
- Posts collected per platform
- Average relevance score
- High-relevance posts (score >= 7)
- Deduplication rate

### Qualitative
- Signals are relevant to ICP
- Good mix of topics covered
- Actionable for content production

---

## Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Low post volume | Medium | Low | Broaden keywords or date range |
| API rate limits | Medium | Medium | Parallel processing with delays |
| Spam/irrelevant posts | Low | Medium | Relevance scoring filters noise |
| Platform unavailable | Medium | Low | Continue with available platforms |

---

## Timeline & Milestones

| Milestone | Target Date | Status |
|-----------|-------------|--------|
| Module Created | {{CREATED_AT}} | Complete |
| Keywords Validated | | Pending |
| Collection Complete | | Pending |
| Report Generated | | Pending |

---

## Stakeholders

| Role | Person | Responsibility |
|------|--------|----------------|
| Engineering Lead | MH1 Team | Collection execution |
| Content Lead | TBD | Signal prioritization |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {{CREATED_AT}} | MH1 | Initial MRD from social-listening template |
