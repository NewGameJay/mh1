# Create Post Stage 1: Brief Extraction & Context Merge

**Steps:** 1-4 (Brief Path, Read Brief, Idempotency Check, Context Loading)

---

## Input

```json
{
  "brief_path": "assignment-briefs/2026-01-15-example-abc123.md",
  "founder": "{founder-name}",
  "funnel_stage": "TOFU",
  "CONTEXT_BUNDLE": { /* from Phase 0 - passed inline, NOT re-read */ }
}
```

---

## Output

```json
{
  "success": true,
  "stage": 1,
  "brief_path": "assignment-briefs/...",
  "brief_data": {
    "id": "...",
    "title": "...",
    "founder": "...",
    "content_pillar": "...",
    "funnel_stage": "TOFU|MOFU|BOFU",
    "pov": "...",
    "target_persona": "...",
    "hook": "...",
    "angle": "...",
    "key_takeaway": "...",
    "objective": "...",
    "typical_themes": "...",
    "pillar_guardrails": "...",
    "hashtags": "...",
    "distribution_notes": "...",
    "signals": ["https://..."]
  },
  "context": {
    "context_summary": "...",
    "company_profile": {...},
    "audience_personas": [...],
    "writing_guidelines": {...},
    "pov_data": {...},
    "founders": {
      "{founder}": {
        "founder_analysis_path": "context/writing-analysis/{founder}-founder-analysis.json",
        "voice_contract_path": "context/writing-analysis/{founder}-voice-contract.json"
      }
    }
  },
  "signals": [{"title": "...", "url": "...", "content": "...", "author": "...", "source": "..."}],
  "error": null
}
```

---

## Process

### Step 1: Read Assignment Brief

```
Read: {brief_path}
```

Extract from YAML frontmatter: `id`, `title`, `founder`, `content_pillar`, `funnel_stage`, `pov`, `target_persona`, `hook`, `angle`, `key_takeaway`, `objective`, `typical_themes`, `pillar_guardrails`, `hashtags`, `distribution_notes`, `signals`

**Required fields:** `id`, `title`, `founder`, `funnel_stage`, `pov`, `content_pillar`, `hashtags`

**Fields needed for Firestore (must be captured):**
- `id` → becomes `source_brief` in post
- `pov` → stored directly
- `content_pillar` → stored directly
- `hashtags` → becomes `distribution_notes.hashtags`
- `target_persona` → stored directly

---

### Step 2: Check Idempotency

```bash
node tools/check-post-exists.js "{brief_data.id}"
```

- If `{"exists": true}`: Return `{"success": false, "skip": true}` - skip this brief
- If `{"exists": false}`: Continue

---

### Step 3: Fetch Signals

**Use ONLY the CLI tool. DO NOT use WebFetch.**

```bash
node tools/get-signal-by-url.js "{signals[0]}" "{signals[1]}" ...
```

If fetch fails, continue with empty signals array.

---

### Step 4: Merge Context

Combine brief data with CONTEXT_BUNDLE. Pass **file paths** for voice data (Stage 3 reads the files):

```json
{
  "founders": {
    "{founder}": {
      "founder_analysis_path": "context/writing-analysis/{founder}-founder-analysis.json",
      "voice_contract_path": "context/writing-analysis/{founder}-voice-contract.json"
    }
  }
}
```

---

## Validation (Must Pass Before Stage 2)

| Check | Requirement |
|-------|-------------|
| Brief file readable | File exists and frontmatter parses |
| Required fields present | `id`, `title`, `founder`, `funnel_stage`, `pov`, `content_pillar`, `hashtags` |
| Idempotency check passed | `node tools/check-post-exists.js` returned `{"exists": false}` |
| Voice files exist | Both JSON files exist at the paths |
| Founder in CONTEXT_BUNDLE | `CONTEXT_BUNDLE.founders[founder]` exists |

**If any check fails, return error and do not proceed to Stage 2.**

---

## Error Handling

| Error | Action |
|-------|--------|
| Brief file not found | Return `{success: false, error: "Brief not found"}` |
| Required field missing | Return `{success: false, error: "Missing field: {field}"}` |
| Post already exists | Return `{success: false, skip: true}` |
| Signal fetch fails | Log warning, continue with empty signals |
| Founder not in CONTEXT_BUNDLE | Return `{success: false, error: "Founder not loaded"}` |
