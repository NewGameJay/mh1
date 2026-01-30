# Stage 05: Collection Report

## Purpose
Generate a human-readable collection summary with aggregations, quality assessment, and recommendations.

## Model
`claude-sonnet-4` - Report synthesis (optional)

## Duration
~1 minute

## Depends On
Stage 04 (stats extracted)

---

## Inputs Required
- `stats`: Statistics object from Stage 04
- `CLIENT_NAME`, `CLIENT_ID`: Client identifiers
- `date_range`: Collection date range used
- `KEYWORDS_DATA`: Keyword metadata
- `templates/collection-report.md`: Report template

## Process

### 5.1 Generate Collection Report

Use the template from `templates/collection-report.md` and populate with collected data.

#### Data Sources for Report

| Placeholder | Source |
|-------------|--------|
| `{CLIENT_NAME}` | From `inputs/active_client.md` |
| `{TIMESTAMP}` | Current datetime (ISO8601) |
| `{DATE_RANGE}` | Input argument or default |
| `{KEYWORD_FILE_PATH}` | Resolved path from Stage 01 |
| `{LINKEDIN_*}` | Platform status from Stage 02 |
| `{TWITTER_*}` | Platform status from Stage 02 |
| `{REDDIT_*}` | Platform status from Stage 02 |
| `{NEW_POSTS}` | Created count from Stage 03 |
| `{UPDATED_POSTS}` | Updated count from Stage 03 |
| `{TOTAL_IN_DB}` | From summary document (incremented total) |
| `{SIGNAL_TAG_ROWS}` | Aggregated from scored posts |
| `{TOP_KEYWORDS_LIST}` | Top 3 by volume from matchedKeywords |
| `{PERSONA_ROWS}` | Aggregated from personaMatch |
| `{SCORED_COUNT}` | Count of posts with relevanceScore |
| `{REPORT_READY}` | "Yes" if high-relevance >= 5, else "Needs more data" |
| `{NEXT_COLLECTION_RECOMMENDATION}` | Based on date-range |

### 5.2 Calculate Aggregations

#### Signal Tag Distribution

Aggregate `signalTags` across all posts:

```markdown
| Signal | Count | % of Total |
|--------|-------|------------|
| founder-story | 25 | 32% |
| women-business | 18 | 23% |
```

#### Top Keywords by Volume

Count keyword occurrences in `matchedKeywords`:

```markdown
1. "female founder" (Industry) - 28 posts
2. "women entrepreneur" (Industry) - 15 posts
3. "funding" (Industry) - 12 posts
```

#### Persona Distribution

Aggregate `personaMatch` across all posts:

```markdown
| Persona | Posts | % of Total |
|---------|-------|------------|
| Female Founder | 45 | 58% |
| Growth-Stage Entrepreneur | 28 | 36% |
```

### 5.3 Determine Data Quality Status

| Metric | Threshold | Status |
|--------|-----------|--------|
| Posts with scores | >= 80% of total | Good |
| Posts with sentiment | >= 80% of total | Good |
| Posts with signal tags | >= 50% of total | Good |

**Report-ready determination**:
- "Yes" if high-relevance posts >= 5 AND all metrics at "Good" status
- "Needs more data" otherwise

### 5.4 Next Collection Recommendation

Based on `--date-range` used:
- `past-24h` -> "Tomorrow (daily monitoring)"
- `past-week` -> "In 7 days (weekly monitoring)"
- `past-month` -> "In 30 days (monthly monitoring)"

### 5.5 Save Report to Local File

```bash
clients/{CLIENT_ID}/social-listening/collection-data/collection_report.md
```

### 5.6 Display Report to User

Present the full report to the user in the terminal/chat.

---

## Output
- `report`: Full markdown report content
- `report_file`: Path to saved report file

## Checkpoint
Final stage - no checkpoint (output is the checkpoint)

## Quality Gate

- [ ] Report generated with all sections populated
- [ ] Aggregations calculated correctly
- [ ] Data quality assessment included
- [ ] Next steps and recommendations provided
- [ ] Report saved to local file

## Next Steps (Include in Report)

Recommend based on collection results:

**If high-relevance posts >= 10**:
```
Ready for content generation:
- Run /ghostwrite-content to generate posts in the founder's voice

Ready for analysis:
- Review scored posts for content inspiration
```

**If high-relevance posts < 10**:
```
Need more data before content generation:
- Run again with broader date range: /social-listening-collect --date-range=past-month
- Add more keywords to the keyword file
- Wait for more social activity and re-collect
```

---

## Success Criteria Summary

The collection workflow is complete when:

- [x] CLIENT_ID parsed from `inputs/active_client.md` (Stage 00)
- [ ] Keyword file loaded and parsed into KEYWORDS_DATA (Stage 01)
- [ ] At least one platform returned data (Stage 02)
- [ ] Posts enriched with matchedKeywords (Stage 02)
- [ ] Posts scored and enriched by competitive-intelligence-analyst (Stage 03)
- [ ] All posts stored to Firestore with deduplication (Stage 03)
- [ ] Statistics extracted for report (Stage 04)
- [ ] Collection report presented (Stage 05)

## Error Handling

### Template Not Found

If template file doesn't exist:
```python
if not template_path.exists():
    # Use fallback inline template
    template = """# Collection Report

## Summary
Client: {CLIENT_NAME}
Date: {TIMESTAMP}
Posts collected: {TOTAL_POSTS}
"""
```

### Report Generation Failure

```
Warning: Could not generate full report.

Minimal stats:
- Posts collected: {N}
- High relevance: {N}
- New signals: {N}

Full data saved at:
clients/{CLIENT_ID}/social-listening/collection-data/scored_posts_{timestamp}.json
```
