# Social Listening Collection Report

## Collection Summary

**Client**: test_client
**Collection Date**: 2026-01-30T01:16:36.771469+00:00
**Date Range Searched**: {DATE_RANGE}
**Keyword File**: {KEYWORD_FILE_PATH}

---

## Posts Collected

| Platform | Raw Posts | Scored | High (>=7) | Medium (5-6) |
|----------|-----------|--------|------------|--------------|
| LinkedIn | 100 | 100 | - | - |
| Twitter | 0 | 0 | - | - |
| Reddit | 0 | 0 | - | - |
| **Total** | 100 | 100 | 0 | 100 |

---

## Storage Results

- **New posts added**: 0
- **Existing posts updated**: 0
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
