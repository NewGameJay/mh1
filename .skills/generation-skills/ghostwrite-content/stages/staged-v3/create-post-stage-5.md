# Create Post Stage 5: Upload & Finalization

**Steps:** 9-11 (Firestore Upload, Notion Upload, Brief Status Update)

---

## CRITICAL: Use CLI Tools, NOT Firebase MCP

**DO NOT use Firebase MCP tools.** Use these CLI tools:

- `node tools/upload-post-to-firestore.js` - Upload posts to Firestore
- `node tools/upload-posts-to-notion.js` - Upload posts to Notion
- `node tools/update-brief-status.js` - Update brief status

---

## Input

Stage 4 output.

---

## Output

```json
{
  "success": true,
  "stage": 5,
  "brief_path": "[from stage 4]",
  "brief_data": "[from stage 4]",
  "post_id": "[from stage 4]",
  "file_path": "[from stage 4]",
  "post_text": "[from stage 4]",
  "word_count": "[from stage 4]",
  "voice_confidence": "[from stage 4]",
  "qa_verdict": "[from stage 4]",
  "firestore_upload": {
    "success": true,
    "post_id": "...",
    "firestore_path": "clients/{clientId}/modules/linkedin-ghostwriter/posts/{postId}"
  },
  "notion_upload": {
    "success": true,
    "post_id": "...",
    "notion_page_id": "...",
    "notion_url": "https://notion.so/..."
  },
  "brief_status_update": {
    "success": true,
    "brief_id": "...",
    "new_status": "used",
    "local_updated": true,
    "firestore_updated": true
  },
  "completed_at": "2026-01-19T12:00:00Z",
  "error": null
}
```

---

## Process

### Step 9: Upload to Firestore

```bash
node tools/upload-post-to-firestore.js "{file_path}"
```

**Example:**
```bash
node tools/upload-post-to-firestore.js "posts/2026-01-19-culture-is-the-founders-shadow-d64b11.md"
```

| Result | Action |
|--------|--------|
| Success | Record `firestore_path`, continue |
| Failure | Log warning, continue (local file preserved) |

---

### Step 10: Upload to Notion

```bash
node tools/upload-posts-to-notion.js "{file_path}"
```

| Result | Action |
|--------|--------|
| Success | Record `notion_page_id` and `notion_url`, continue |
| Skipped | Post already in Notion, continue |
| Failure | Log warning, continue (not blocking) |

---

### Step 11: Update Brief Status

```bash
node tools/update-brief-status.js "{brief_data.id}" --status used
```

Updates both local file frontmatter and Firestore document.

| Result | Action |
|--------|--------|
| Success | Record success, continue |
| Failure | Log warning, continue (not blocking) |

---

## Validation (Must Pass Before Completion)

| Check | Requirement |
|-------|-------------|
| Stage 4 input valid | `success: true`, `file_saved: true` |
| Post file exists | `ls {file_path}` succeeds |
| All CLI tools executed | All three commands were run |
| `completed_at` set | Valid ISO timestamp |

**Note:** Firestore/Notion/Brief status failures are NOT blocking. The post file exists from Stage 4.

---

## Error Handling

| Error | Blocking? | Action |
|-------|-----------|--------|
| Firestore upload fails | NO | Log warning, continue |
| Notion upload fails | NO | Log warning, continue |
| Brief status update fails | NO | Log warning, continue |
| All operations fail | NO | Return success (post file exists) |

**Key Principle:** Stage 5 operations are "nice to have" for cloud sync. The critical work (post file save) was done in Stage 4.

---

## Integration with Orchestrator

After Stage 5 completes:

1. Orchestrator checks for more briefs in SELECTED_BRIEFS
2. If more briefs: Proceed to Stage 1 for next brief
3. If no more briefs: Proceed to Phase 3 (Calendar Compilation)
