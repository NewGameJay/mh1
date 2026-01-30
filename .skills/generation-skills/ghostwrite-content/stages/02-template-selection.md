# Stage 2: Template Selection

**Duration**: 2-4 minutes
**Agent**: linkedin-template-selector
**Platform**: LinkedIn only (skip for other platforms)
**Execution**: 4 parallel batches

## Purpose

Match selected topics to optimal LinkedIn templates from the 81-template database. Each topic is matched to a proven template format based on funnel stage, audience resonance, and strategic fit.

## Client Info (from active_client.md)

```
CLIENT_ID = {parsed from inputs/active_client.md}
CLIENT_NAME = {parsed from inputs/active_client.md}
FOLDER_NAME = {parsed from inputs/active_client.md}
```

## Key Change: Context Passed Inline

**Agents receive context INLINE from orchestrator. NO Firestore reads in this stage.**

The template selector receives:
- `selectedTopics` from Stage 1.75 (with inspirationSummary)
- `companyContext` from `context_bundle.json`
- Template CSV path (reads local file only)

## Prerequisites

- Stage 1 complete: `context_bundle.json` exists
- Stage 1.75 complete: `selectedTopics` array available
- Platform is `linkedin`

## Inputs

| Input | Source | Description |
|-------|--------|-------------|
| `selectedTopics` | Stage 1.75 | Topics with scores, funnel stages, inspirationSummary |
| `companyContext` | context_bundle.json | Condensed company context |
| Template CSV | Local file | `inputs/_templates/linkedin-post-templates.csv` |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `template-selections.json` | File | Template matches for all posts |

---

## Execution Pattern: 4 Parallel Batches

Split topics into 4 batches and invoke `linkedin-template-selector` agents IN PARALLEL:

```
Task 1: linkedin-template-selector (topics 1-5)
Task 2: linkedin-template-selector (topics 6-10)
Task 3: linkedin-template-selector (topics 11-15)
Task 4: linkedin-template-selector (topics 16-20)
```

---

## Agent Prompt (Pass Context Inline)

```
Task tool: linkedin-template-selector
Prompt: Select templates for the following topics.

        SELECTED TOPICS (batch {N} of 4):
        {SELECTED_TOPICS_BATCH_JSON}

        COMPANY CONTEXT:
        {COMPANY_CONTEXT_JSON}

        Template CSV path: inputs/_templates/linkedin-post-templates.csv

        Return template selections as JSON.
```

**CRITICAL**: Pass `selectedTopics` and `companyContext` directly in the prompt. The agent reads ONLY the template CSV file; all other context comes inline.

---

## Expected Output

Each batch returns template selections:

```json
{
  "templateSelections": [
    {
      "topicId": "topic-001",
      "templateId": 8,
      "templateName": "Industry hot take V2",
      "templatePattern": "PROMPT from CSV...",
      "funnelStage": "TOFU",
      "matchScore": 8.5,
      "matchRationale": "Strong fit for contrarian angle on funding topic",
      "executionGuidance": ["Step 1", "Step 2", "Step 3"],
      "angle": "Inherited from topic",
      "inspirationSummary": "Inherited from topic",
      "keyPoints": ["Inherited from topic"]
    }
  ],
  "summary": {
    "topicsProcessed": 5,
    "avgMatchScore": 8.2
  }
}
```

---

## Save Template Selections

**Use Python script for reliable JSON writes**:

After all batches complete:

1. **Merge all batch outputs** into single `templateSelections` array
2. **Save using write_json.py**:
```bash
python skills/ghostwrite-content/scripts/write_json.py \
  "{FOLDER_NAME}/campaigns/ghostwrite-{PLATFORM}-{DATE}/source-data/template-selections.json" \
  '{TEMPLATE_SELECTIONS_JSON}'
```
3. **Mark stage complete**:
```bash
python skills/ghostwrite-content/scripts/checkpoint.py "{CAMPAIGN_DIR}" complete "2"
```

---

## Quality Gate (Blocking)

- [ ] `template-selections.json` EXISTS
- [ ] Contains selections for all topics
- [ ] All match scores >= 6.0 (or flagged)
- [ ] All batches completed successfully

**DO NOT proceed to Stage 3 until template-selections.json is verified.**

---

## Error Handling

### Batch Failure
If a batch fails, retry once. If still failing, use fallback templates:
- TOFU -> Template #8
- MOFU -> Template #15
- BOFU -> Template #22

### Template CSV Not Found
Error if `inputs/_templates/linkedin-post-templates.csv` missing. Cannot proceed.

---

## Next Stage

-> [Stage 3: Ghostwriting](./03-ghostwriting.md)
