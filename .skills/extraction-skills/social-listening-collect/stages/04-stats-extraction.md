# Stage 04: Stats Extraction

## Purpose
Parse upload results from Stage 03 and extract statistics for the collection report.

## Model
None (data aggregation only)

## Duration
Instant

## Depends On
Stage 03 (posts uploaded)

---

## Inputs Required
- Upload results from `update_post_scores.py`
- `scored_posts`: Array of scored posts

## Process

### 4.1 Parse Upload Results

Extract statistics from `update_post_scores.py` output:

```python
upload_stats = {
    "created": result.get("created", 0),
    "updated": result.get("updated", 0),
    "errors": result.get("errors", 0)
}
```

### 4.2 Calculate Score Distribution

Aggregate scores from `scored_posts`:

```python
score_distribution = {
    "high": len([p for p in scored_posts if p.get("relevanceScore", 0) >= 7]),
    "medium": len([p for p in scored_posts if 5 <= p.get("relevanceScore", 0) < 7]),
    "low": len([p for p in scored_posts if p.get("relevanceScore", 0) < 5])
}
```

### 4.3 Calculate Signal Tag Distribution

Aggregate `signalTags` across all posts:

```python
from collections import Counter

all_tags = []
for post in scored_posts:
    all_tags.extend(post.get("signalTags", []))

tag_distribution = Counter(all_tags)
```

### 4.4 Calculate Persona Distribution

Aggregate `personaMatch` across all posts:

```python
all_personas = []
for post in scored_posts:
    all_personas.extend(post.get("personaMatch", []))

persona_distribution = Counter(all_personas)
```

### 4.5 Calculate Top Keywords

Count keyword occurrences in `matchedKeywords`:

```python
keyword_counts = Counter()
for post in scored_posts:
    for kw in post.get("matchedKeywords", []):
        keyword_counts[kw["term"]] += 1

top_keywords = keyword_counts.most_common(10)
```

### 4.6 Build Stats Object

Compile all statistics for Stage 05:

```python
stats = {
    "upload": upload_stats,
    "scores": score_distribution,
    "total_posts": len(scored_posts),
    "platforms": {
        "linkedin": len([p for p in scored_posts if p["platform"] == "linkedin"]),
        "twitter": len([p for p in scored_posts if p["platform"] == "twitter"]),
        "reddit": len([p for p in scored_posts if p["platform"] == "reddit"])
    },
    "signal_tags": dict(tag_distribution.most_common(10)),
    "personas": dict(persona_distribution.most_common(5)),
    "top_keywords": top_keywords,
    "data_quality": {
        "scored_count": len([p for p in scored_posts if p.get("relevanceScore") is not None]),
        "sentiment_count": len([p for p in scored_posts if p.get("sentiment")]),
        "tagged_count": len([p for p in scored_posts if p.get("signalTags")])
    }
}
```

---

## Output
- `stats`: Complete statistics object for report generation
- `NEW_POSTS`: Created count from upload
- `UPDATED_POSTS`: Updated count from upload

## Checkpoint
This stage does not create a checkpoint (instant computation).

## Quality Gate

- [ ] Upload results parsed successfully
- [ ] Created/updated counts extracted
- [ ] Score distribution available for report
- [ ] Tag and persona distributions calculated

## Error Handling

### Parse Failure

If upload results cannot be parsed:
1. Log warning
2. Use placeholder values (0) for upload stats
3. Continue to Stage 05 with partial data

```python
if upload_result is None:
    upload_stats = {"created": 0, "updated": 0, "errors": 0}
    warnings.append("Could not parse upload results - using defaults")
```

### Missing Score Data

If posts don't have scores:
```python
if stats["data_quality"]["scored_count"] < len(scored_posts) * 0.8:
    warnings.append(f"Only {scored_count}/{total} posts have scores")
```

---

**Note**: The new data structure does not maintain a summary document.
Aggregated stats are computed on-demand from query results.

---

**Next Stage**: [Stage 05: Collection Report](./05-collection-report.md)
