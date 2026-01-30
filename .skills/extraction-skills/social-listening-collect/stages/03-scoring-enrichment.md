# Stage 03: Scoring & Enrichment

## Purpose
Score collected posts for relevance using the competitive-intelligence-analyst agent and enrich with sentiment, ICP fit, and signal tags.

## Model
`claude-sonnet-4` - Complex reasoning for relevance scoring

## Duration
5-10 minutes

## Depends On
Stage 02 (posts collected with matchedKeywords)

---

## Inputs Required
- `all_posts`: Combined posts from Stage 02
- `CLIENT_ID`: Client identifier
- `config/signal-tags.json`: Signal tag taxonomy

## Process

### 3.1 Load Client Context

Load context from **LOCAL files** (not Firestore):

```python
audience_path = f"clients/{CLIENT_ID}/context/audience.md"
strategy_path = f"clients/{CLIENT_ID}/context/strategy.md"
competitive_path = f"clients/{CLIENT_ID}/context/competitive.md"

# Read files
audience_context = read_file(audience_path) if exists(audience_path) else None
strategy_context = read_file(strategy_path) if exists(strategy_path) else None
```

**Extract for scoring agent:**
- `targetAudience` - Persona definitions from audience.md
- `contentThemes` - Theme list from strategy.md
- `competitors` - From competitive.md (optional)

Pass these values INLINE to the competitive-intelligence-analyst agent.
Fallback: Use generic B2B marketing context if files don't exist.

### 3.2 Invoke Scoring Agent

Launch `competitive-intelligence-analyst` agent to score and enrich posts.

#### Agent Input

Provide the agent with:
1. All collected posts from Stage 2 (with `matchedKeywords` already populated)
2. Client audience context (loaded from context files)
3. Signal tag reference from `config/signal-tags.json`

#### Agent Scoring Prompt

```
You are scoring social listening posts for {CLIENT_NAME}.

Use the client context loaded from LOCAL files to inform scoring decisions.
Target audience and mission should be extracted from audience.md and strategy.md.

For each post, provide:

1. **relevanceScore** (0-10): How relevant is this to the client's audience?
   - 9-10: Directly about client's core topics with high engagement
   - 7-8: Strong relevance to target audience
   - 5-6: General relevance to client's space
   - 3-4: Tangentially relevant
   - 1-2: Not relevant

2. **icpFit**: How well does this align with the client's target audience?

3. **contentPotential**: Rate as High/Medium/Low - could this inspire content?

4. **sentiment**: Overall tone - positive/negative/neutral/mixed

5. **sentimentContext**: Why this sentiment? (1 sentence)

6. **personaMatch**: Which personas would care? Pick from:
   - CMO/VP Marketing
   - Startup Founder
   - Marketing Manager
   - Growth Marketer
   - Agency Leader

7. **signalTags**: Which strategic signals are present? Pick from:
   - founder-story
   - funding-news
   - hiring-growth
   - challenge-lesson
   - ai-marketing
   - b2b-marketing
   - leadership
   - demand-gen
   - industry-trend
   - success-milestone
   - buying-signal

Output as JSON array.
```

### 3.3 Filter and Tag Results

After agent returns scores:
- Mark posts with `relevanceScore >= 7` as "high-relevance"
- Mark posts with `relevanceScore 5-6` as "medium-relevance"
- Include all posts in storage (even low-scoring for future analysis)

### 3.4 Save Scored Posts to JSON

Save to local file for upload:

```bash
clients/{CLIENT_ID}/social-listening/collection-data/scored_posts_{TIMESTAMP}.json
```

#### Scored Post Structure

```json
{
  "posts": [
    {
      "postId": "linkedin_abc123",
      "platform": "linkedin",
      "postUrl": "https://...",
      "content": "...",
      "author": {...},
      "engagement": {...},
      "matchedKeywords": [
        {"term": "female founder", "category": "Industry", "priority": "high", "matchType": "content"}
      ],
      "relevanceScore": 8.5,
      "icpFit": "Strong - Female founder sharing funding journey",
      "contentPotential": "High - Unique perspective on rejection before success",
      "sentiment": "positive",
      "sentimentContext": "Celebratory tone about overcoming obstacles",
      "personaMatch": ["Female Founder", "Growth-Stage Entrepreneur"],
      "signalTags": ["founder-story", "funding-news", "challenge-lesson"],
      "scoredAt": "2026-01-24T10:30:00Z",
      "source": "social-listening-collect"
    }
  ]
}
```

### 3.5 Sync to Firestore

Use the bulk upload script:

```bash
python skills/firebase-bulk-upload/update_post_scores.py \
  "clients/{CLIENT_ID}/social-listening/collection-data/scored_posts_{TIMESTAMP}.json" \
  {CLIENT_ID} --upsert

# Writes to: clients/{CLIENT_ID}/signals/{signalId}
```

The `--upsert` flag ensures:
- **Existing posts**: Only mutable fields updated (found via legacyId/externalId)
- **New posts**: Full document created with auto-generated UUID and legacyId for lookup

---

## Output
- `scored_posts`: Array of posts with scores and enrichment
- `scored_posts_file`: Path to saved JSON file
- `upload_stats`: Firestore upload results

## Checkpoint
Creates checkpoint at `checkpoints/03-scoring-enrichment.json`

## Quality Gate

- [ ] All posts have `relevanceScore` assigned
- [ ] All posts have `sentiment` assigned
- [ ] Signal tags assigned where applicable
- [ ] At least 5 posts scored >= 5
- [ ] Scored posts JSON file created
- [ ] `update_post_scores.py` executed successfully

## Context Management

- If > 200 posts: Process in batches of 50-100
- Use Haiku for per-post extraction if needed
- Use Sonnet for final synthesis and quality check

## Error Handling

### Scoring Agent Failure

If competitive-intelligence-analyst fails:
1. Store posts WITHOUT scores (`relevanceScore: null`)
2. Flag posts as "unscored" in metadata
3. Log error details
4. Continue to Stage 04 with partial data

### Firestore Upload Failure

```
Warning: Firestore upload failed.

Error: {error_message}

Data saved locally at:
clients/{CLIENT_ID}/social-listening/collection-data/scored_posts_{timestamp}.json

You can retry upload manually:
python skills/firebase-bulk-upload/update_post_scores.py "path/to/file.json" {CLIENT_ID} --upsert
```

---

**Next Stage**: [Stage 04: Stats Extraction](./04-stats-extraction.md)
