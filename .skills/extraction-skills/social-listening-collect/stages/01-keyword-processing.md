# Stage 01: Keyword Processing

## Purpose
Parse the keyword file and build a structured KEYWORDS_DATA object for platform-specific queries.

## Model
`claude-haiku` - Fast extraction of structured data

## Duration
1-2 minutes

## Depends On
Stage 00 (CLIENT_ID resolved)

---

## Inputs Required
- `CLIENT_ID`: From Stage 00
- `keyword_file`: Custom path or default `clients/{CLIENT_ID}/social-listening/keywords.md`

## Process

### 1.1 Determine Keyword File Path

**Decision logic**:
- If `keyword_file` argument provided -> Use that path
- If no file argument -> Use default: `clients/{CLIENT_ID}/social-listening/keywords.md`

### 1.2 Load and Parse Keyword File

```python
keyword_path = Path(keyword_file or f"clients/{CLIENT_ID}/social-listening/keywords.md")
if not keyword_path.exists():
    raise FileNotFoundError(f"Keyword file not found: {keyword_path}")

content = keyword_path.read_text()
```

### Expected Markdown Structure

```markdown
# Social Listening Keywords: {CLIENT_NAME}

## High Priority Keywords (N)

### Brand Keywords
**{keyword_term}**
- **Category:** Brand
- **Search Variants:** variant1, variant2, ...
- **Rationale:** Why this keyword matters
- **Platforms:** LinkedIn, Reddit, Twitter

### Industry Keywords
**{keyword_term}**
- **Category:** Industry
- **Search Variants:** ...

## Medium Priority Keywords (N)
...

## Low Priority Keywords (N)
...

## Platform-Specific Queries
### LinkedIn Queries
1. `query string`

### Reddit Queries
**Subreddits:** subreddit1, subreddit2, ...
1. keyword1
2. keyword2

### Twitter/X Queries
1. `query string`
```

### 1.3 Build KEYWORDS_DATA Object

Parse keywords into structured data:

```json
{
  "keywords": {
    "high": [
      {
        "term": "fractional CMO",
        "category": "Industry",
        "searchVariants": ["fractional marketing", "part-time CMO"],
        "rationale": "Core service term",
        "platforms": ["linkedin", "reddit", "twitter"]
      }
    ],
    "medium": [...],
    "low": [...]
  },
  "competitorKeywords": [
    {"term": "Toptal", "variants": ["Toptal marketing"]},
    {"term": "CMOx", "variants": ["CMO exchange"]}
  ],
  "platformQueries": {
    "linkedin": ["fractional CMO OR fractional marketing"],
    "reddit": {
      "subreddits": ["marketing", "startups", "smallbusiness", "B2B"],
      "queries": ["fractional CMO", "fractional marketing", "AI marketing"]
    },
    "twitter": ["fractional CMO min_faves:5", "AI marketing min_faves:5"]
  },
  "metadata": {
    "totalKeywords": 15,
    "highPriority": 5,
    "mediumPriority": 5,
    "lowPriority": 5,
    "filePath": "clients/{CLIENT_ID}/social-listening/keywords.md"
  }
}
```

### 1.4 Validate Parsed Keywords

| Validation | Minimum | Error Message |
|------------|---------|---------------|
| Total keywords | 3 | "Keyword file has only {N} keywords (minimum 3 recommended)" |
| Platform queries | 1 per requested platform | "No queries found for {platform}" |

### 1.5 Parse Platform Flags

From `--platforms` argument (default: `linkedin,twitter,reddit`):
- Split by comma
- Validate each platform is supported
- Store as `REQUESTED_PLATFORMS` array

### 1.6 Log Collection Parameters

Display configuration summary:

```
Collection Parameters:
- Client: {CLIENT_NAME} ({CLIENT_ID})
- Keyword file: clients/{CLIENT_ID}/social-listening/keywords.md
- Platforms: linkedin, twitter, reddit
- Date range: past-week
- Keywords: {HIGH_COUNT} high / {MEDIUM_COUNT} medium / {LOW_COUNT} low priority
```

---

## Output
- `KEYWORDS_DATA`: Structured keyword object
- `REQUESTED_PLATFORMS`: Array of platforms to scrape
- `keyword_metadata`: Keyword statistics

## Checkpoint
Creates checkpoint at `checkpoints/01-keyword-processing.json`

Can resume from this point if later stages fail.

## Quality Gate

- [ ] Keyword file found and readable
- [ ] At least 3 keywords parsed
- [ ] Platform-specific queries available for requested platforms
- [ ] `KEYWORDS_DATA` object built successfully
- [ ] Parameters logged

## Error Handling

### Keyword File Not Found

```
Error: Keyword file not found.

Expected path: clients/{CLIENT_ID}/social-listening/keywords.md

Solutions:
1. Verify the keyword file exists
2. Provide a custom path: /social-listening-collect --keyword-file path/to/keywords.md
3. Run keyword generation skill first
```

### Invalid Keyword Format

```
Warning: Some keywords could not be parsed.

Skipped entries:
- Line 45: Missing category
- Line 67: Invalid platform list

Continuing with {N} valid keywords...
```

---

**Next Stage**: [Stage 02: Social Scraping](./02-social-scraping.md)
