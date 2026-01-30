# Social Listening Collection Report

## Collection Summary

**Client**: {CLIENT_NAME}
**Collection Date**: {TIMESTAMP}
**Date Range Searched**: {DATE_RANGE}
**Keyword File**: {KEYWORD_FILE_PATH}

---

## Posts Collected

| Platform | Raw Posts | Scored | High (>=7) | Medium (5-6) |
|----------|-----------|--------|------------|--------------|
| LinkedIn | {LINKEDIN_RAW} | {LINKEDIN_SCORED} | {LINKEDIN_HIGH} | {LINKEDIN_MEDIUM} |
| Twitter | {TWITTER_RAW} | {TWITTER_SCORED} | {TWITTER_HIGH} | {TWITTER_MEDIUM} |
| Reddit | {REDDIT_RAW} | {REDDIT_SCORED} | {REDDIT_HIGH} | {REDDIT_MEDIUM} |
| **Total** | {TOTAL_RAW} | {TOTAL_SCORED} | {TOTAL_HIGH} | {TOTAL_MEDIUM} |

---

## Storage Results

- **New posts added**: {NEW_POSTS}
- **Existing posts updated**: {UPDATED_POSTS}
- **Total posts in database**: {TOTAL_IN_DB}

---

## Signal Tag Distribution

| Signal | Count | % of Total |
|--------|-------|------------|
{SIGNAL_TAG_ROWS}

---

## Top Keywords by Volume

{TOP_KEYWORDS_LIST}

---

## Persona Distribution

| Persona | Posts | % of Total |
|---------|-------|------------|
{PERSONA_ROWS}

---

## Data Quality for Reporting

| Metric | Value | Status |
|--------|-------|--------|
| Total posts with scores | {SCORED_COUNT} | {SCORED_STATUS} |
| Posts with sentiment | {SENTIMENT_COUNT} | {SENTIMENT_STATUS} |
| Posts with signal tags | {SIGNAL_TAG_COUNT} | {SIGNAL_STATUS} |
| **Report-ready?** | - | {REPORT_READY} |

---

## Next Steps

- High-relevance posts ready for ghostwriting
- Run `/ghostwrite-content` to generate content in the founder's voice
- Next scheduled collection: {NEXT_COLLECTION_RECOMMENDATION}

---

## Firestore Path

Posts stored at:
```
clients/{CLIENT_ID}/signals/
```
