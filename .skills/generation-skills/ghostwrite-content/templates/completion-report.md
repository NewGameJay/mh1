# Completion Report Template

This template defines the format for the final presentation message in Stage 6.

## Client Info (from active_client.md)

```
CLIENT_ID = {parsed from inputs/active_client.md}
CLIENT_NAME = {parsed from inputs/active_client.md}
FOLDER_NAME = {parsed from inputs/active_client.md}
FOUNDER = {resolved from founders subcollection}
```

## Variables

| Variable | Description |
|----------|-------------|
| `{PLATFORM}` | Target platform |
| `{POST_COUNT}` | Total posts generated |
| `{MIN_RELEVANCE}` | Minimum relevance filter used |
| `{SOURCE_POSTS_COUNT}` | Number of source posts used |
| `{TOFU_COUNT}` | TOFU posts count |
| `{MOFU_COUNT}` | MOFU posts count |
| `{BOFU_COUNT}` | BOFU posts count |
| `{AVG_VOICE}` | Average voice authenticity score |
| `{QA_STATUS}` | QA pass status |
| `{CAMPAIGN_DIR}` | Full campaign directory path |
| `{POSTS_PER_WEEK}` | Recommended posting frequency |
| `{WEEKS}` | Number of weeks of content |
| `{START_DATE}` | First scheduled date |
| `{END_DATE}` | Last scheduled date |

## Standard Completion Template

```markdown
## CONTENT CALENDAR COMPLETE

**Platform**: {PLATFORM}
**Client**: MH-1
**Founder**: {FOUNDER_NAME}
**Posts Generated**: {POST_COUNT}

### Campaign Summary
- Source: {SOURCE_POSTS_COUNT} high-relevance social listening posts (score >= {MIN_RELEVANCE})
- Funnel mix: {TOFU_COUNT} TOFU, {MOFU_COUNT} MOFU, {BOFU_COUNT} BOFU
- Voice authenticity: {AVG_VOICE}/10 average
- QA status: {QA_STATUS}

### Campaign Location
`clients/{clientId}/campaigns/ghostwrite-{PLATFORM}-{DATE}/`

### Files Generated
| File | Description |
|------|-------------|
| CONTENT_CALENDAR_FINAL.md | Client-ready content calendar |
| CONTENT_CALENDAR_FINAL.json | Structured calendar data |
| README.md | Campaign overview |
| source-data/ | Supporting research data |

### Firestore
| Path | Description |
|------|-------------|
| `clients/{CLIENT_ID}/posts/` | {POST_COUNT} post documents uploaded |
| `clients/{CLIENT_ID}/contentCalendar/{RUN_ID}` | Updated with postIds array |

**Post IDs**: `{RUN_ID}-001` through `{RUN_ID}-{POST_COUNT:03d}`

### Recommended Schedule
{POSTS_PER_WEEK} posts/week over {WEEKS} weeks
- Start: {START_DATE}
- End: {END_DATE}

### Next Steps
1. Review posts in campaign folder
2. Approve and schedule in {PLATFORM} scheduler
3. Monitor engagement
4. Run `/social-listening-collect` to gather fresh data for next batch
```

## With Manual Review Warning

Add this section if any posts require manual review:

```markdown
### Manual Review Required

{MANUAL_REVIEW_COUNT} posts require manual review due to QA issues:

| Post | Issue |
|------|-------|
{MANUAL_REVIEW_TABLE}

These posts are included in the calendar with warning banners.
Please review and edit before publishing.
```

## With Missing Data Note

Add this section if optional data sources were empty:

```markdown
### Note: Limited Source Data

The following data sources were not available:
- Thought leader posts: {TL_COUNT} (0 = none found)
- Parallel events: {EVENTS_COUNT} (0 = none found)

Consider running:
- `/thought-leader-discover` to add thought leaders
- `/parallel-monitor-collect` to collect industry news
```

## Context-Only Mode Completion

Use this template when `--context-only` flag was set:

```markdown
## Context Window Analysis Complete

**Client**: MH-1
**Founder**: {FOUNDER_NAME}
**Timestamp**: {TIMESTAMP}
**Mode**: --context-only (agents ran, no posts generated)

### Context Files Generated

| File | Agent/Stage | Description |
|------|-------------|-------------|
| 00-ORCHESTRATOR_CONTEXT_{TIMESTAMP}.md | Orchestrator | All data loaded by command (master context) |
| 01-TOPIC_CURATOR_CONTEXT_{TIMESTAMP}.md | linkedin-topic-curator | Thought leaders, events, social posts, moderate company context |
| 02-TEMPLATE_SELECTOR_CONTEXT_{TIMESTAMP}.md | linkedin-template-selector | Selected topics, template database, full client context |
| 03-GHOSTWRITER_CONTEXT_{TIMESTAMP}.md | linkedin-ghostwriter | Template selections, topic summaries, founder voice, full context |

**Location**: `clients/{clientId}/context-snapshots/`

### Context Isolation Verification

| Agent | External Posts Received | Company Context | Founder Data |
|-------|------------------------|-----------------|--------------|
| Topic Curator | {TL_COUNT} TL + {EVENTS_COUNT} events + {SOURCE_POSTS_COUNT} social | Moderate (4 fields) | topThemes only |
| Template Selector | None (topics only) | Full (5 docs) | None |
| Ghostwriter | None (inspirationSummary only) | Full (5 docs) | Full (profile + {FOUNDER_POSTS_COUNT} posts) |

### Token Reduction Achieved

- **Without isolation**: ~40K tokens (all external posts to ghostwriter)
- **With isolation**: ~15K tokens (only summaries to ghostwriter)
- **Reduction**: ~60%

### Workflow Results

- **Topics Selected**: {TOPICS_COUNT} topics ({TOTAL_POSTS_ALLOCATED} posts allocated)
- **Templates Matched**: {TEMPLATES_COUNT} template selections
- **Posts Generated**: 0 (context-only mode)

### Next Steps

1. Review context files in `clients/{clientId}/context-snapshots/`
2. Verify each agent received appropriate context
3. Check that ghostwriter context has topic summaries (not raw posts)
4. If context looks complete, run without --context-only:
   `/ghostwrite-content`
```

## Usage

Stage 6 (Final Presentation) selects the appropriate template based on:
1. Standard completion (default)
2. With manual review warning (if QA flagged posts)
3. With missing data note (if thought leaders or events empty)
4. Context-only mode (if `--context-only` flag was set)
