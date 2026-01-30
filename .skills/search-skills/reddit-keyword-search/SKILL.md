---
name: reddit-keyword-search
description: |
  Search Reddit for posts matching keywords across subreddits using PRAW library.
  Use when asked to 'search Reddit', 'find Reddit posts', 'collect Reddit signals',
  'monitor Reddit mentions', or 'track Reddit conversations'.
license: Proprietary
compatibility:
  - Reddit API (PRAW)
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  estimated_runtime: "3-10min"
  client_facing: false
  tags:
    - social-listening
    - reddit
    - signals
    - praw
allowed-tools: Read Write Shell
---

# Reddit Keyword Search Skill

Search Reddit for posts containing specific keywords across targeted subreddits.

## When to Use

Use this skill when you need to:
- Search Reddit for posts containing specific keywords or phrases
- Collect Reddit signals for social listening campaigns
- Monitor Reddit mentions for a client's brand or competitors
- Find Reddit discussions about specific topics or industries
- Build a collection of Reddit content for analysis

## Usage

1. Copy and customize `reddit_collection_template.py`
2. Modify KEYWORDS, SUBREDDITS, and MONTHS_BACK variables
3. Run with `python reddit_search.py --json` for JSON output
4. Pipe output to `upload_mentions.py` for Firestore upload

## Client Configuration

Client ID is read from `inputs/active_client.md` for Firestore upload.
No hardcoded CLIENT_ID in scripts.

## API Credentials

Reddit API credentials are pre-configured in the template.

## Rate Limits

- ~60 requests/minute
- Scripts include automatic delays

## Example

```bash
# Run collection with JSON output
python skills/reddit-keyword-search/reddit_collection_template.py --json > reddit_posts.json

# Upload to Firestore (reads client from active_client.md)
python skills/firebase-bulk-upload/upload_mentions.py reddit_posts.json --platform reddit
```

## Example Subreddits

Common subreddits for B2B marketing topics (customize based on client's audience):

- r/marketing
- r/startups
- r/smallbusiness
- r/B2B
- r/Entrepreneur

## Output Directory

Output files are written to:
```
clients/{CLIENT_ID}/social-listening/collection-data/
```
