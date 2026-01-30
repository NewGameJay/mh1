---
name: twitter-keyword-search
description: |
  Search X (Twitter) for tweets matching keywords and collect signals using X API v2.
  Use when asked to 'search Twitter', 'find Twitter posts', 'collect Twitter signals',
  'search X', 'monitor Twitter mentions', or 'track Twitter conversations'.
license: Proprietary
compatibility:
  - X API v2 (Basic tier or higher)
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  estimated_runtime: "2-5min"
  client_facing: false
  tags:
    - social-listening
    - twitter
    - x
    - signals
allowed-tools: Read Write Shell
---

# X (Twitter) Keyword Search Skill

Search X (Twitter) for tweets containing specific keywords using X API v2.

## When to Use

Use this skill when you need to:
- Search Twitter/X for tweets containing specific keywords or phrases
- Collect Twitter signals for social listening campaigns
- Monitor Twitter mentions for a client's brand or competitors
- Find tweets about specific topics, hashtags, or users
- Build a collection of Twitter content for analysis

## Usage

1. Copy and customize `twitter_collection_template.py`
2. Modify SEARCH_QUERY, DAYS_BACK, and MAX_TWEETS variables
3. Run with `python twitter_search.py --json` for JSON output
4. Pipe output to `upload_mentions.py` for Firestore upload

## Client Configuration

Client ID is read from `inputs/active_client.md` for Firestore upload.
No hardcoded CLIENT_ID in scripts.

## API Credentials

X API credentials are pre-configured in the template.

## Rate Limits (Basic Tier)

- 450 requests per 15-minute window
- 10,000 tweets per month

## Example

```bash
# Run collection with JSON output
python skills/twitter-keyword-search/twitter_collection_template.py --json > twitter_posts.json

# Upload to Firestore (reads client from active_client.md)
python skills/firebase-bulk-upload/upload_mentions.py twitter_posts.json --platform twitter
```

## Query Operators

- Boolean: `OR`, `AND` (implicit), `-` (exclude)
- User: `from:username`, `to:username`, `mentions:username`
- Engagement: `min_faves:N`, `min_retweets:N`, `min_replies:N`
- Content: `has:links`, `has:images`, `has:videos`, `lang:en`
- Date: `since:2025-01-01`, `until:2025-01-07`

## Output Directory

Output files are written to:
```
clients/{CLIENT_ID}/social-listening/collection-data/
```
