# Phase 0: Context Preload

**Purpose:** Load ALL context files ONCE at the start. Passed inline to all subsequent stages.

---

## Input

```json
{
  "--founder-distribution": "{founder-name}:5",
  "--post-count": 5
}
```

---

## Output

```json
{
  "loaded_at": "2026-01-19T12:00:00Z",
  "context_summary": "...",
  "company_profile": {...},
  "audience_personas": [...],
  "writing_guidelines": {...},
  "pov_data": {...},
  "templates": {
    "prompts": [...]
  },
  "founders": {
    "{founder-name}": {
      "founder_analysis_path": "context/writing-analysis/{founder-name}-founder-analysis.json",
      "voice_contract_path": "context/writing-analysis/{founder-name}-voice-contract.json",
      "files_saved": true
    }
  },
  "validation": {
    "all_files_loaded": true,
    "founders_loaded": ["{founder-name}"],
    "ready_for_phase_1": true
  }
}
```

---

## Process

### Step 1: Load Core Context Files

Read and store each file:

| File | Key | Format |
|------|-----|--------|
| `context/context_summary.md` | `context_summary` | string |
| `context/company-profile.json` | `company_profile` | object |
| `context/audience-persona.json` | `audience_personas` | array |
| `context/writing-guideline.json` | `writing_guidelines` | object |
| `context/pov.json` | `pov_data` | object |

If any file missing, STOP with error.

---

### Step 2: Load Template Prompts

```
Read: artifacts/linkedin-post-templates-prompts.csv
```

Parse CSV into array. Do NOT load examples CSV here (loaded in Stage 2 for selected template only).

---

### Step 3: Identify Founders

Parse `--founder-distribution` argument:
- `{founder-1}:5` → founders: `["{founder-1}"]`
- `{founder-1}:3,{founder-2}:2` → founders: `["{founder-1}", "{founder-2}"]`

---

### Step 4: Load Founder Voice Profiles

For each founder:

1. **Check if JSON files exist:**
   - `context/writing-analysis/{founder}-founder-analysis.json`
   - `context/writing-analysis/{founder}-voice-contract.json`

2. **If either missing:** Run `skills/extract-founder-voice/SKILL.md` with `founder_slug={founder}`

3. **Store file paths** (NOT content) in CONTEXT_BUNDLE:
   ```json
   {
     "founders": {
       "{founder}": {
         "founder_analysis_path": "context/writing-analysis/{founder}-founder-analysis.json",
         "voice_contract_path": "context/writing-analysis/{founder}-voice-contract.json",
         "files_saved": true
       }
     }
   }
   ```

**Note:** Stage 3 will READ these JSON files before writing.

---

## Validation (Must Pass Before Phase 1)

| Check | Requirement |
|-------|-------------|
| Core files loaded | All 5 context files read successfully |
| Templates loaded | Prompts CSV parsed with entries |
| Founders identified | At least one founder from arguments |
| Voice files exist | Both JSON files exist for each founder |

**If any check fails, STOP and report error.**

---

## Error Handling

| Error | Action |
|-------|--------|
| Context file not found | STOP with file path |
| Context file parse error | STOP with parse details |
| No founders specified | Use default founder |
| Voice files missing after extraction | STOP with founder name |
