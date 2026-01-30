# Stage 02: Social Media Scraping

## Purpose
Execute platform-specific scraping skills in parallel to collect social posts matching client keywords.

## Model
None (executes external skills)

## Duration
3-8 minutes

## Depends On
Stage 01 (KEYWORDS_DATA built)

---

## Inputs Required
- `KEYWORDS_DATA`: Structured keyword object from Stage 01
- `REQUESTED_PLATFORMS`: Platforms to scrape
- `date_range`: Time window for collection

## Process

### 2.1 Create Output Directory

Before invoking scraping skills, create the output directory:

```bash
mkdir -p clients/{CLIENT_ID}/social-listening/collection-data
```

### 2.2 Invoke Scraping Skills (PARALLEL)

Execute scraping skills **IN PARALLEL** for all requested platforms:

```
[Skill: linkedin-keyword-search] (if linkedin in REQUESTED_PLATFORMS)
[Skill: twitter-keyword-search] (if twitter in REQUESTED_PLATFORMS)
[Skill: reddit-keyword-search] (if reddit in REQUESTED_PLATFORMS)
```

### Per-Platform Configuration

#### LinkedIn

**Skill**: `linkedin-keyword-search`
**API**: Crustdata
**Parameters**:
- Queries: Use `KEYWORDS_DATA.platformQueries.linkedin`
- Date range: `{DATE_RANGE}`
- Max posts: 100
- Collect: post content, author info, engagement metrics, post URL
- **Track which query returned each post**

**Rate Limit**: 10 requests/minute

#### Twitter/X

**Skill**: `twitter-keyword-search`
**API**: Twitter API v2
**Parameters**:
- Queries: Use `KEYWORDS_DATA.platformQueries.twitter`
- Date range: `{DATE_RANGE}`
- Max posts: 100
- Collect: tweet content, author info, engagement metrics, tweet URL
- **Track which query returned each post**

**Rate Limit**: 20 requests/minute

#### Reddit

**Skill**: `reddit-keyword-search`
**API**: PRAW (Python Reddit API Wrapper)
**Parameters**:
- Queries: Use `KEYWORDS_DATA.platformQueries.reddit.queries`
- Subreddits: Use `KEYWORDS_DATA.platformQueries.reddit.subreddits`
- Max posts: 100
- Collect: post/comment content, author, engagement metrics, URL
- **Track which query returned each post**

**Rate Limit**: 30 requests/minute

### 2.3 Post-Collection Keyword Matching

After scraping completes, **enrich each post with `matchedKeywords`**:

#### Process

1. For each collected post, scan content against all keywords in `KEYWORDS_DATA.keywords`
2. Build `matchedKeywords` array with all matching keywords

#### matchedKeywords Structure

```json
{
  "matchedKeywords": [
    {
      "term": "female founder",
      "category": "Industry",
      "priority": "high",
      "matchType": "content"
    }
  ]
}
```

### 2.4 Save Raw Posts

Save collected posts to local JSON files:

```
clients/{CLIENT_ID}/social-listening/collection-data/linkedin_posts.json
clients/{CLIENT_ID}/social-listening/collection-data/twitter_posts.json
clients/{CLIENT_ID}/social-listening/collection-data/reddit_posts.json
clients/{CLIENT_ID}/social-listening/collection-data/all_posts_combined.json
```

---

## Output
- `all_posts`: Combined array of posts from all platforms
- `platform_results`: Per-platform collection status and counts
- Platform-specific JSON files

## Checkpoint
Creates checkpoint at `checkpoints/02-social-scraping.json`

Can resume from this point if later stages fail.

## Quality Gate

- [ ] At least one platform returned data
- [ ] Total collected posts >= 10
- [ ] Each post has `matchedKeywords` array populated

## Error Handling

### Platform Skill Failure

If a platform skill fails:
1. Log the error with details
2. **Continue with other platforms**
3. Report partial success in collection summary
4. **Do NOT fail entire workflow for one platform**

### No Data Collected

If total posts < 10 across all platforms:

```
Warning: Only {N} posts collected (minimum 10 recommended).

Possible causes:
- Keywords too specific/narrow
- Date range too short
- Low activity on selected platforms

Suggestions:
1. Broaden keywords or add more variants
2. Extend date range to past-month
3. Check API credentials are valid

Continuing with available data...
```

### API Rate Limiting

```
Warning: {platform} API rate limited.

Collected {N} of {max} posts before limit.
Will retry remaining in next collection cycle.

Continuing with partial data...
```

## Platform Status Tracking

Track and report platform status:

```json
{
  "platformStatus": {
    "linkedin": { "status": "success", "postsCollected": 45, "queriesRun": 3 },
    "twitter": { "status": "failed", "error": "API rate limit exceeded", "postsCollected": 0 },
    "reddit": { "status": "success", "postsCollected": 32, "queriesRun": 5 }
  },
  "totalPosts": 77
}
```

## Context Management

- If data > 8000 tokens: Posts will be processed in batches in Stage 03
- No LLM calls in this stage - pure data collection
- All posts saved to files before proceeding

---

**Next Stage**: [Stage 03: Scoring & Enrichment](./03-scoring-enrichment.md)
