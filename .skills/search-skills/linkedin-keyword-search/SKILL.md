---
name: linkedin-keyword-search
description: |
  Search LinkedIn for posts matching keywords and collect signals using Crustdata API.
  Use when asked to 'search LinkedIn', 'find LinkedIn posts', 'collect LinkedIn signals',
  'monitor LinkedIn mentions', or 'track LinkedIn conversations'.
license: Proprietary
compatibility:
  - Crustdata API
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  estimated_runtime: "2-5min"
  client_facing: false
  tags:
    - social-listening
    - linkedin
    - signals
    - crustdata
allowed-tools: Read Write Shell
---

# LinkedIn Keyword Search Skill

Search LinkedIn for posts containing specific keywords using the Crustdata API.

## When to Use

Use this skill when you need to:
- Search LinkedIn for posts containing specific keywords or phrases
- Collect LinkedIn signals for social listening campaigns
- Monitor LinkedIn mentions for a client's brand or competitors
- Find LinkedIn posts about specific topics or industries
- Build a collection of LinkedIn content for analysis

## Usage

1. Copy and customize `linkedin_collection_template.py`
2. Modify KEYWORD, DATE_POSTED, and LIMIT variables
3. Run with `python linkedin_collection.py --json` for JSON output
4. Pipe output to `upload_mentions.py` for Firestore upload

## Client Configuration

Client ID is read from `inputs/active_client.md` for Firestore upload.
No hardcoded CLIENT_ID in scripts.

## API Key

Crustdata API key is pre-configured in the template.

## Example

```bash
# Run collection with JSON output
python skills/linkedin-keyword-search/linkedin_collection_template.py --json --limit 100 > linkedin_posts.json

# Upload to Firestore (reads client from active_client.md)
python skills/firebase-bulk-upload/upload_mentions.py linkedin_posts.json --platform linkedin
```

## Query Operators

- Boolean: `OR`, `AND` (implicit)
- Phrases: `"exact phrase"`
- Author: Use MEMBER filter for specific LinkedIn profiles
- Company: Use COMPANY or AUTHOR_COMPANY filters

## Credit Costs

- Standard search: 1 credit/post
- Exact match: 3 credits/post
- Reactors data: +5 credits/post
- Comments data: +5 credits/post

## Output Directory

Output files are written to:
```
clients/{CLIENT_ID}/social-listening/collection-data/
```
