# Create Post Stage 4: QA Review & File Save

**Steps:** 6-8 (QA Review, File Save, Checkpoint)

---

## CRITICAL: Use Task Tool for QA

**DO NOT perform QA checks yourself.** You MUST spawn a Task agent to review the post.

- **Agent file:** `agents/workers/linkedin-qa-reviewer-agent.md`
- **subagent_type:** `general-purpose`

---

## Input

Stage 3 output.

---

## Output

```json
{
  "success": true,
  "stage": 4,
  "brief_path": "[from stage 3]",
  "brief_data": "[from stage 3]",
  "context": "[from stage 3]",
  "signals": "[from stage 3]",
  "template": "[from stage 3]",
  "outline": "[from stage 3]",
  "post_text": "[from stage 3 OR revised]",
  "word_count": "[updated if revised]",
  "hook_length": "[updated if revised]",
  "voice_confidence": "[updated if revised]",
  "voice_elements_used": "[from stage 3]",
  "constraints_verified": "[from stage 3]",
  "distribution_notes": "[from stage 3]",
  "qa_result": {
    "verdict": "PASS",
    "critical_violations": [],
    "medium_violations": [],
    "low_violations": [],
    "voice_authenticity_score": 8,
    "revision_count": 0
  },
  "post_id": "2026-01-19-culture-is-the-founders-shadow-d64b11",
  "file_path": "posts/2026-01-19-culture-is-the-founders-shadow-d64b11.md",
  "file_saved": true,
  "error": null
}
```

---

## Process

### Step 6: Spawn QA Agent

Use the Task tool:

```
Task {
  subagent_type: "general-purpose",
  description: "QA Review: {brief_title}",
  prompt: "You are the linkedin-qa-reviewer agent.

    FIRST: Read your instructions from agents/workers/linkedin-qa-reviewer-agent.md

    THEN: Review this post:

    {post_text}

    Metadata: {brief_data, voice_elements_used, word_count, hook_length}

    Return JSON with: verdict, critical_violations, medium_violations, low_violations, voice_authenticity_score"
}
```

### Handle QA Verdict

| Verdict | Action |
|---------|--------|
| `PASS` | Proceed to Step 7 |
| `NEEDS REVISION` / `FAIL` | Go to revision loop (max 2 attempts) |

### Revision Loop (if needed)

1. Extract required fixes from QA response
2. Revise post to fix violations
3. Re-run QA (back to Step 6)
4. Max 2 revision attempts; if still failing, proceed with warning

---

### Step 7: Generate Post ID

```
Format: YYYY-MM-DD-{slug}-{hash}
Example: 2026-01-19-culture-is-the-founders-shadow-d64b11
```

- `slug`: Title lowercased, non-alphanumeric replaced with `-`, max 40 chars
- `hash`: 6-char random hex

---

### Step 8: Save Post File

**Save IMMEDIATELY. Do not defer to Stage 5.**

#### Frontmatter (use exact field names for Firestore):

**CRITICAL: ALL fields below are REQUIRED for Firestore sync. Empty values cause sync failures.**

```yaml
---
id: "{post_id}"
title: "{brief_data.title}"
source_brief: "{brief_data.id}"
founder: "{brief_data.founder}"
content_pillar: "{brief_data.content_pillar}"
funnel_stage: "{brief_data.funnel_stage}"
pov: "{brief_data.pov}"
target_persona: "{brief_data.target_persona}"
signals_used:
  - "{signals[0].url}"
  - "{signals[1].url}"
citations:
  - "{signals[0].url}"
  - "{signals[1].url}"
template:
  id: "{template.id}"
  name: "{template.name}"
distribution_notes:
  hashtags: "{brief_data.hashtags}"
  best_time: "Tuesday-Thursday, 8-10am"
  post_in_comments:
    - "{signals[0].url}"
word_count: {actual_word_count}
hook_length: {actual_hook_length}
voice_confidence: {voice_confidence}
qa_verdict: "{qa_result.verdict}"
revision_count: {qa_result.revision_count}
created_at: "{YYYY-MM-DD}"
status: "draft"
---
```

**Required Field Sources:**

| Field | Source | Notes |
|-------|--------|-------|
| `source_brief` | `brief_data.id` | NOT post_id |
| `pov` | `brief_data.pov` | Full POV text |
| `template.id` | `template.id` from Stage 2 | e.g., "6" |
| `template.name` | `template.name` from Stage 2 | e.g., "Culture Building" |
| `signals_used` | `signals[].url` array | Can be empty `[]` |
| `citations` | Same as `signals_used` | Can be empty `[]` |
| `distribution_notes.hashtags` | `brief_data.hashtags` | e.g., "#AI #GPUCloud" |

#### Body:

```markdown
{post_text}

---

## Distribution Notes

**Post in comments:**
- {signal URLs}

**Best posting time:** {best_time}

**Tags:** {hashtags}

---

## Metadata

**Voice Elements:**
- Opening style: {opening_style}
- Signature phrases: {signature_phrases}

**QA Summary:**
- Verdict: {verdict}
- Voice score: {score}/10
```

#### Write file:

```
Write: posts/{post_id}.md
```

Verify file exists and is non-empty.

---

## Validation (Must Pass Before Stage 5)

| Check | Requirement |
|-------|-------------|
| Task tool used for QA | Did NOT perform inline QA checks |
| QA verdict received | `PASS`, `FAIL`, or `NEEDS REVISION` |
| Critical violations | Empty array (for PASS verdict) |
| Post ID generated | Format `YYYY-MM-DD-{slug}-{hash}` |
| File saved | `posts/{post_id}.md` exists with content |
| Context preserved | All Stage 3 fields passed through |

**Frontmatter Field Validation (CRITICAL):**

| Field | Check |
|-------|-------|
| `source_brief` | Non-empty (must be `brief_data.id`) |
| `pov` | Non-empty (must be `brief_data.pov`) |
| `template.id` | Non-empty (from Stage 2) |
| `template.name` | Non-empty (from Stage 2) |
| `distribution_notes.hashtags` | Non-empty |
| `signals_used` | Array (can be empty `[]`) |
| `citations` | Array (can be empty `[]`) |

**If any required field is empty string, STOP and fix before saving.**

---

## Auto-Fail Patterns (from QA Agent)

| Pattern | Status |
|---------|--------|
| Em dashes (—) | REJECT |
| Rhetorical questions / "The X? Answer." | REJECT |
| Structures of 3 (exactly 3 items) | REJECT |
| "It's not X, it's Y" | REJECT |
| "Here's X" language | REJECT |
| "Let me X" intros | REJECT |
| Fabricated anecdotes/quotes | REJECT |

---

## Error Handling

| Error | Action |
|-------|--------|
| QA agent returns malformed JSON | Try to parse, if fails return error |
| QA fails after 2 revisions | Log warning, proceed with best version |
| File save fails | Return `{success: false, error: "File save failed"}` |
