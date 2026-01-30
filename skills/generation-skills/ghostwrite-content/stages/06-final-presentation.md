# Stage 6: Final Presentation

**Duration**: < 1 minute

## Purpose

Present the completion summary to the user with campaign overview, file locations, and recommended next steps.

## Client Info (from active_client.md)

```
CLIENT_ID = {parsed from inputs/active_client.md}
CLIENT_NAME = {parsed from inputs/active_client.md}
FOLDER_NAME = {parsed from inputs/active_client.md}
FOUNDER = {resolved from founders subcollection}
```

## Prerequisites

- Stage 5 complete: All output files created
- Stage 5.5 complete: Posts uploaded to Firestore

## Inputs

| Input | Source | Description |
|-------|--------|-------------|
| Campaign metrics | Stage 5 | Post counts, quality scores |
| File paths | Stage 5 | Output file locations |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| Completion message | Display | Summary shown to user |

---

## Completion Message

Display the following summary:

```markdown
## CONTENT CALENDAR COMPLETE

**Platform**: {--platform}
**Client**: {CLIENT_NAME}
**Founder**: {FOUNDER_NAME}
**Posts Generated**: {--post-count}

### Campaign Summary
- Source: {n} high-relevance social listening posts (score >= {--min-relevance})
- Funnel mix: {x} TOFU, {y} MOFU, {z} BOFU
- Voice authenticity: {avg}/10 average
- QA status: All posts passed

### Campaign Location
`{FOLDER_NAME}/campaigns/ghostwrite-{PLATFORM}-{DATE}/`

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
| `clients/{CLIENT_ID}/posts/` | {--post-count} post documents uploaded |
| `clients/{CLIENT_ID}/contentCalendar/{RUN_ID}` | Updated with postIds array |

**Post IDs**: `{RUN_ID}-001` through `{RUN_ID}-{post-count:03d}`

### Recommended Schedule
{X} posts/week over {Y} weeks
- Start: {start_date}
- End: {end_date}

### Next Steps
1. Review posts in campaign folder
2. Approve and schedule in {platform scheduler}
3. Monitor engagement
4. Run `/social-listening-collect` to gather fresh data for next batch
```

---

## Conditional Messages

### Posts Requiring Manual Review

If any posts were flagged as `needs-manual-review`:

```markdown
### Manual Review Required

{n} posts require manual review due to QA issues:
- Post {X}: {issue summary}
- Post {Y}: {issue summary}

These posts are included in the calendar with warning banners.
Please review and edit before publishing.
```

### Missing Optional Data

If thought leaders or events were empty:

```markdown
### Note: Limited Source Data

The following data sources were not available:
- Thought leader posts: {0 if empty}
- Parallel events: {0 if empty}

Consider running:
- `/thought-leader-discover` to add thought leaders
- `/parallel-monitor-collect` to collect industry news
```

### Twitter Platform Note

If `--platform=twitter` was requested:

```markdown
### Platform Note

Twitter ghostwriting was requested but is not yet available.
Posts were generated for LinkedIn instead.

Twitter support is coming soon.
```

---

## Success Criteria

- [ ] Completion message displayed
- [ ] Campaign location clearly shown
- [ ] File list provided
- [ ] Schedule recommendation included
- [ ] Next steps outlined
- [ ] Any warnings/notes displayed
- [ ] Workflow complete

---

## Workflow Complete

This is the final stage of the ghostwrite-content workflow.

### Summary of Stages Completed

| Stage | Description | Status |
|-------|-------------|--------|
| 0 | ID Resolution | Done |
| 1 | Context Loading | Done |
| 1.5 | Context-Only (if flag) | Skipped or Done |
| 1.75 | Topic Curation | Done |
| 2 | Template Selection | Done |
| 3 | Ghostwriting | Done |
| 4 | QA Review | Done |
| 5 | Calendar Compilation | Done |
| 5.5 | Post Persistence | Done |
| 6 | Final Presentation | Done |
