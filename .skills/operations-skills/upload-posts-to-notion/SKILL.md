---
name: upload-posts-to-notion
description: |
  Upload LinkedIn post files to a Notion database for review and scheduling.
  Use when asked to 'upload posts to Notion', 'sync posts to Notion',
  'push posts to Notion', 'add posts to Notion database', or 'export posts to Notion'.
license: Proprietary
compatibility: [Notion]
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  estimated_runtime: "10-60s"
  client_facing: false
  tags:
    - notion
    - upload
    - sync
    - content-calendar
    - linkedin
allowed-tools: Read Write Shell
---

# Upload Posts to Notion

## When to Use

- Upload completed LinkedIn posts to Notion for review
- Sync local post files with Notion content calendar
- Push ghostwritten content to Notion database
- Export posts from local directory to Notion
- Update Notion with newly created posts

---

Upload LinkedIn post files from the local `posts/` directory to a Notion database.

## Overview

This skill uploads markdown post files to Notion, mapping frontmatter properties to database columns and adding the post content as page body.

## Prerequisites

1. **Notion Integration Token** - Add to `.env`:
   ```
   NOTION_API_TOKEN=secret_xxx
   ```

2. **Notion Database ID** - Must be stored in Firebase at:
   ```
   ClientData/{clientId}/modules/linkedin-ghostwriter.notionDatabaseId
   ```

3. **npm Dependencies**:
   ```bash
   npm install @notionhq/client dotenv
   ```

## Notion Database Schema

The database should have these properties:

| Property | Type | Frontmatter Field |
|----------|------|-------------------|
| Name | Title | `title` |
| Post ID | Rich Text | `id` |
| Content | Rich Text | *(post body)* |
| Founder | Rich Text | `founder` |
| Content Pillar | Select | `content_pillar` |
| Funnel Stage | Select | `funnel_stage` |
| Status | Status | `status` |
| Target Persona | Select | `target_persona` |
| POV | Rich Text | `pov` |
| Source Brief | Rich Text | `source_brief` |
| Word Count | Number | `word_count` |
| Created At | Date | `created_at` |
| Uploaded At | Date | *(auto-generated)* |
| Signals Used | Rich Text | `signals_used` |
| Template ID | Rich Text | `template.id` |
| Template Name | Rich Text | `template.name` |
| Citations | Rich Text | `citations` |
| Best Posting Time | Rich Text | *(from Distribution Notes)* |
| Comment Links | URL | *(from Distribution Notes)* |
| Tags | Rich Text | *(from Distribution Notes)* |

## Usage

### Upload a Single Post

```bash
node tools/upload-posts-to-notion.js "posts/2026-01-22-post-abc123.md"
```

### Upload All Posts

```bash
node tools/upload-posts-to-notion.js --all
```

### Dry Run (Preview Without Uploading)

```bash
node tools/upload-posts-to-notion.js --all --dry-run
```

## Output

The tool outputs JSON with upload results:

```json
{
  "success": true,
  "dry_run": false,
  "database_id": "abc123...",
  "total_files": 3,
  "uploaded": [
    {
      "success": true,
      "post_id": "2026-01-22-post-abc123",
      "title": "Post Title",
      "notion_page_id": "xxx",
      "notion_url": "https://notion.so/..."
    }
  ],
  "skipped": [
    {
      "success": true,
      "skipped": true,
      "post_id": "2026-01-22-existing-post",
      "reason": "Already exists in Notion"
    }
  ],
  "failed": []
}
```

## Property Mapping Details

### Select Field Mappings

**Status** (maps to Notion Status type):
- `draft` → Draft
- `published` → Published
- `scheduled` → Scheduled
- `in_review` → In Review

**Target Persona** (maps to Notion Select):
- `founder` → Founder
- `business-leader` → Operator
- `product-leader` → Operator
- `investor` → Investor

**Funnel Stage** (maps to Notion Select):
- TOFU, MOFU, BOFU (passed through as-is)

### Distribution Notes Extraction

The tool extracts these fields from the `## Distribution Notes` section in the post body:
- **Best Posting Time** - from `**Best posting time:**`
- **Comment Links** - from `**Post in comments:**` (first URL)
- **Tags** - from `**Tags:**`

## Idempotency

The tool checks if a post with the same `Post ID` already exists in Notion before uploading. If it exists, the post is skipped (not duplicated or updated).

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `NOTION_API_TOKEN not found` | Missing env var | Add token to `.env` |
| `notionDatabaseId not found` | Missing in Firebase | Add field to client document |
| `Could not find property` | Missing Notion column | Add the property to database |
| `File not found` | Invalid path | Check file exists in `posts/` |

## Integration with Ghostwrite Workflow

After running `/ghostwrite-content`, upload the created posts to Notion:

```bash
# Upload all newly created posts
node tools/upload-posts-to-notion.js --all
```

This syncs your local posts with the Notion content calendar for review and scheduling.
