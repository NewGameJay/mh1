# Staged Ghostwrite Content Orchestrator (V3)

Sequential execution of LinkedIn post creation with context preloading.

---

## Architecture

```
Phase 0: Context Preload (ONCE)
    └── Load all context files, verify voice JSON files
    └── Output: CONTEXT_BUNDLE

Phase 1: Select Briefs (inline)
    └── Output: SELECTED_BRIEFS[]

Phase 2: Sequential Brief Processing
    For each brief:
    ├── Stage 1: Brief + Context Merge
    ├── Stage 2: Template + Outline
    ├── Stage 3: Write Post (INLINE)
    ├── Stage 4: QA + Save (Task agent)
    └── Stage 5: Upload + Finalize

Phase 3: Compile Calendar (inline)
```

---

## Tool Requirements

**DO NOT use Firebase MCP tools.** Use CLI tools:
- `node tools/upload-post-to-firestore.js "{file_path}"`
- `node tools/upload-posts-to-notion.js "{file_path}"`
- `node tools/update-brief-status.js "{brief_id}" --status used`

---

## Invocation

```
/ghostwrite-content --post-count=5 --founder-distribution={founder-name}:5
```

**Arguments:**
- `--post-count`: Posts to generate (default: 5)
- `--funnel-distribution`: TOFU:MOFU:BOFU ratio (default: 2:2:1)
- `--founder-distribution`: Posts per founder

---

## Phase 0: Context Preload

**Execute:** `skills/ghostwrite-content/stages/staged-v3/phase-0-context-preload.md`

Loads all context ONCE. Output is `CONTEXT_BUNDLE` containing:
- Core context files (context_summary, company_profile, etc.)
- Template prompts
- Founder voice file PATHS (not content)

**Quality Gate:** All files loaded, voice JSON files exist for each founder.

---

## Phase 1: Brief Selection

**Execute:** `skills/ghostwrite-content/stages/01-select-briefs-for-posts.md`

**Output:** `SELECTED_BRIEFS[]` with path, founder, funnel_stage for each brief.

**Quality Gate:** At least 1 brief selected.

---

## Phase 2: Sequential Processing

**Process briefs ONE AT A TIME.** For each brief:

### Stage 1: Brief Extraction & Context Merge

**Execute:** `skills/ghostwrite-content/stages/staged-v3/create-post-stage-1.md`

- Read brief file
- Check idempotency: `node tools/check-post-exists.js "{brief_id}"`
- Fetch signals: `node tools/get-signal-by-url.js "{urls}"`
- Merge with CONTEXT_BUNDLE (pass voice file paths)

### Stage 2: Template Selection & Outline

**Execute:** `skills/ghostwrite-content/stages/staged-v3/create-post-stage-2.md`

- Filter templates by funnel_stage
- Select template
- Create OPENING/BODY/CLOSE outline

### Stage 3: Write the Post (INLINE)

**Execute:** `skills/ghostwrite-content/stages/staged-v3/create-post-stage-3.md` **INLINE (no Task agent)**

- **MUST READ** voice JSON files first:
  - `context/writing-analysis/{founder}-founder-analysis.json`
  - `context/writing-analysis/{founder}-voice-contract.json`
- Apply voice contract rules
- Write post matching founder's voice

### Stage 4: QA Review & File Save

**Execute:** `skills/ghostwrite-content/stages/staged-v3/create-post-stage-4.md` **via Task agent**

Agent: `agents/workers/linkedin-qa-reviewer-agent.md`

- Run QA checks
- If FAIL, revise (up to 2x)
- **QA must PASS before file save**
- Save to `posts/{filename}.md`

### Stage 5: Upload & Finalization

**Execute:** `skills/ghostwrite-content/stages/staged-v3/create-post-stage-5.md`

- Upload to Firestore
- Upload to Notion
- Update brief status to "used"

---

## Phase 3: Calendar Compilation

**Execute:** `skills/ghostwrite-content/stages/03-compile-calendar.md`

Build calendar from completed posts, save to `calendars/`.

---

## Data Flow Summary

```
Phase 0 → CONTEXT_BUNDLE
├── Core context (summary, company, audience, guidelines, pov)
├── templates[]
└── founders[].founder_analysis_path, voice_contract_path

Stage 1 → Stage 2:
├── brief_data (id, title, founder, funnel_stage, pov, etc.)
├── context (with voice file paths preserved)
└── signals[]

Stage 2 → Stage 3:
├── [All Stage 1 data]
├── template (id, prompt, example_text)
└── outline (opening, body, close)

Stage 3 → Stage 4:
├── [All Stage 2 data]
├── post_text
├── voice_confidence, voice_elements_used
└── distribution_notes

Stage 4 → Stage 5:
├── qa_result
├── post_id, file_path
└── file_saved: true

Stage 5 → Final:
├── firestore_upload, notion_upload
├── brief_status_update
└── completed_at
```

---

## Error Handling

| Stage | Error | Action |
|-------|-------|--------|
| Phase 0 | Context/voice files missing | STOP |
| Stage 1 | Brief not found | STOP |
| Stage 1 | Post exists | Skip brief, continue |
| Stage 2 | Template selection fails | STOP |
| Stage 3 | Voice file missing | STOP |
| Stage 4 | QA fails after 2 retries | WARNING, continue |
| Stage 4 | File save fails | STOP |
| Stage 5 | Upload fails | WARNING, continue |

**Key principle:** If any stage fails (except uploads), STOP immediately. Do not continue to next brief.

---

## Stage Files

```
skills/ghostwrite-content/stages/staged-v3/
├── orchestrator.md
├── phase-0-context-preload.md
├── create-post-stage-1.md
├── create-post-stage-2.md
├── create-post-stage-3.md (INLINE execution)
├── create-post-stage-4.md (Task agent for QA)
└── create-post-stage-5.md
```
