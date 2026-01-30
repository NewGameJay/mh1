# MRD: {{MODULE_NAME}}

## Metadata
| Field | Value |
|-------|-------|
| Module ID | {{MODULE_ID}} |
| Client | {{CLIENT_ID}} |
| Status | {{STATUS}} |
| Template | content-production |
| Priority | P1 |
| Owner | MH1 Engineering |
| Created | {{CREATED_AT}} |
| Updated | {{CREATED_AT}} |

---

## Executive Summary

{{TASK_DESCRIPTION}}

This module will produce marketing content for {{CLIENT_ID}} including:
- LinkedIn posts in the founder's authentic voice
- Email sequences (optional)
- Content calendar for planned publishing
- Quality-assured content ready for review

---

## Problem Statement

### What Changed?
<!-- Examples:
- Client needs weekly LinkedIn content for founder
- Email nurture sequence required for new product
- Content calendar gap needs filling
- Thought leadership campaign launching
-->

### Why This Matters
<!-- Examples:
- Consistent LinkedIn presence drives 3x more inbound
- Email sequences convert 25% better than one-off sends
- Content calendar ensures consistent brand presence
-->

---

## Objectives

### Primary Goal
Deliver publication-ready content that authentically represents the founder's voice and supports marketing goals.

### Success Criteria
1. All requested content pieces generated
2. Voice confidence score >= 7/10 on average
3. Zero AI tells (em dashes, structures of 3, rhetorical questions)
4. Content calendar compiled and ready for scheduling

---

## Scope

### In Scope
- LinkedIn post generation (ghostwriting)
- Email sequence creation (if requested)
- Content calendar compilation
- Voice confidence scoring
- QA review for AI tells

### Out of Scope
- Actual publishing to social platforms
- Design/graphics creation
- Video content production
- Paid ad copy (use `direct-response-copy` skill)

---

## Content Requirements

| Content Type | Count | Platform | Notes |
|--------------|-------|----------|-------|
| LinkedIn Posts | {{POST_COUNT}} | LinkedIn | Founder voice |
| Email Sequence | {{EMAIL_COUNT}} | Email | If requested |
| Newsletter | {{NEWSLETTER_COUNT}} | Email | If requested |

---

## Voice Contract

The founder's voice is defined by:

### Voice Characteristics
<!-- From voice contract - will be populated -->
- Tone:
- Vocabulary level:
- Sentence structure:
- Formality:

### Signature Phrases
<!-- From voice contract -->
-
-

### Anti-Patterns (NEVER DO)
- No em dashes (-)
- No rhetorical questions (unless founder uses them)
- No structures of 3
- No corporate buzzwords

---

## Approach & Methodology

### Phase 1: Context Loading
- Load voice contract and brand context
- Fetch founder posts for pattern analysis
- Load social signals (if available)
- **Checkpoint:** Context validated

### Phase 2: Topic Curation
- Analyze social signals for trending topics
- Match topics to founder expertise
- Select template formats
- **Checkpoint:** Topics selected

### Phase 3: Content Generation
- Generate posts in batches
- Apply voice contract constraints
- Score for voice confidence
- **Checkpoint:** Draft posts ready

### Phase 4: QA Review
- Check for AI tells
- Verify citations
- Score overall quality
- **Checkpoint:** QA complete

### Phase 5: Calendar Compilation
- Organize posts by date
- Create publishing schedule
- Generate final deliverables
- **Checkpoint:** Calendar ready

---

## Skills to Execute

```yaml
skills:
  - name: social-listening-collect
    inputs:
      client_id: "{{CLIENT_ID}}"
      platforms: ["linkedin", "twitter"]
    checkpoint: true
    required: false
    condition: "needs_fresh_signals"

  - name: ghostwrite-content
    inputs:
      client_id: "{{CLIENT_ID}}"
      founder_id: "{{FOUNDER_ID}}"
      post_count: {{POST_COUNT}}
      platform: "linkedin"
    checkpoint: true
    required: true

  - name: email-sequences
    depends_on: ghostwrite-content
    inputs:
      client_id: "{{CLIENT_ID}}"
      sequence_type: "nurture"
    checkpoint: true
    required: false
    condition: "include_email"
```

---

## Dependencies & Blockers

### Critical Dependencies
- [ ] Voice contract exists for founder
- [ ] Brand context documents available
- [ ] Minimum 10 founder posts collected
- [ ] Firebase access configured

### Optional Dependencies
- [ ] Social signals collected (< 7 days old)
- [ ] Thought leader posts available

### Known Blockers
- None

---

## Success Metrics

### Quantitative
- Voice confidence average >= 7/10
- All requested posts generated
- Zero critical QA failures
- Turnaround within 6 hours

### Qualitative
- Posts feel authentic to founder's voice
- Topics are relevant and timely
- Content is engaging and actionable

---

## Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Voice doesn't match | High | Medium | More founder posts, refine contract |
| AI tells detected | High | Medium | QA review, regeneration |
| Stale signals | Medium | Low | Run social-listening-collect first |
| Topic fatigue | Medium | Medium | Rotate topic categories |

---

## Timeline & Milestones

| Milestone | Target Date | Status |
|-----------|-------------|--------|
| Module Created | {{CREATED_AT}} | Complete |
| Context Loaded | | Pending |
| Posts Generated | | Pending |
| QA Complete | | Pending |
| Calendar Delivered | | Pending |

---

## Stakeholders

| Role | Person | Responsibility |
|------|--------|----------------|
| Engineering Lead | MH1 Team | Content generation |
| Founder | TBD | Voice source & approval |
| Marketing Lead | TBD | Calendar review |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {{CREATED_AT}} | MH1 | Initial MRD from content-production template |
