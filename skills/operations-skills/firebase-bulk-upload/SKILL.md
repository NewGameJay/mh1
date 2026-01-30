---
name: firebase-bulk-upload
description: |
  Bulk upload data to Firebase using the Admin SDK for batch operations.
  Use when asked to 'bulk upload to Firebase', 'batch upload mentions',
  'upload social data to Firestore', 'mass upload to Firebase', or 'sync data to Firebase'.
license: Proprietary
compatibility: [Firebase]
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  estimated_runtime: "10-120s"
  client_facing: false
  tags:
    - firebase
    - bulk-upload
    - firestore
    - social-listening
    - batch
allowed-tools: Read Write Shell
---

# Firebase Bulk Upload Skill

## When to Use

- Upload large batches of data to Firebase (10+ documents)
- Bulk upload social listening mentions to Firestore
- Batch update existing Firestore documents with scores
- Mass upload data faster than individual MCP calls
- Sync collected social data to Firebase

---

Efficiently uploads data to Firebase using the Admin SDK for batch operations.

## Available Scripts

| Script | Purpose |
|--------|---------|
| `upload_mentions.py` | Upload social listening mentions with platform transformation |
| `update_post_scores.py` | Update existing social listening posts with relevance scores |

## Client Configuration

Client ID can be provided as a command-line argument or read from `inputs/active_client.md`.
No hardcoded CLIENT_ID in scripts.

## Why Use This Instead of MCP

The Firebase MCP server works well for individual operations, but when uploading 10+ files/documents, making individual MCP calls is slow. This skill uses the Firebase Admin SDK directly via Python with batch writes, which is much faster for bulk operations.

## Requirements

- Python 3
- Firebase Admin SDK credentials file in project root or MH-1 Platform root
  - File should match pattern: `*firebase-adminsdk*.json`
- Internet connection

## Script 1: upload_mentions.py

Uploads social listening mentions to Firestore with platform-specific transformation.

### Usage

```bash
# With explicit client_id
python skills/firebase-bulk-upload/upload_mentions.py <json_file> <client_id> --platform <platform>

# Read client_id from active_client.md
python skills/firebase-bulk-upload/upload_mentions.py <json_file> --platform <platform>
```

### Arguments

- `json_file`: JSON file from collection script (or `-` for stdin)
- `client_id`: Firestore client document ID (optional if active_client.md exists)
- `--platform`: Required. One of: `reddit`, `linkedin`, `twitter`
- `--limit`: Max posts to upload (default: reddit=200, linkedin=100, twitter=50)
- `--report-id`: Report identifier (default: `initial-onboarding`)

## Script 2: update_post_scores.py

Updates existing social listening posts with relevance scoring data.

### Usage

```bash
# With explicit client_id
python skills/firebase-bulk-upload/update_post_scores.py <json_file> <client_id> [options]

# Read client_id from active_client.md
python skills/firebase-bulk-upload/update_post_scores.py <json_file> [options]
```

### Arguments

- `json_file`: JSON file with scored posts (or `-` for stdin)
- `client_id`: Firestore client document ID (optional if active_client.md exists)
- `--upsert`: Create posts if they don't exist (default: update only)
- `--min-score`: Only process posts with relevanceScore >= this value (default: 0)

## Firestore Paths

Signals are stored at:
```
clients/{CLIENT_ID}/signals/{signalId}
```

## Example Workflow

```bash
# 1. Collect posts
python skills/linkedin-keyword-search/linkedin_collection_template.py --json > linkedin_posts.json

# 2. Upload to Firestore (client read from active_client.md)
python skills/firebase-bulk-upload/upload_mentions.py linkedin_posts.json --platform linkedin

# 3. After scoring, update with scores
python skills/firebase-bulk-upload/update_post_scores.py scored_posts.json --upsert
```
