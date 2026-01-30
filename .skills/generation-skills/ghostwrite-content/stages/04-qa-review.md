# Stage 4: QA Review

**Duration**: 3-5 minutes
**Agent**: linkedin-qa-reviewer (or platform-specific QA agent)

## Purpose

Validate generated posts for AI tells and quality issues. This stage applies zero-tolerance rules for common AI writing patterns and verifies citations.

## Client Info (from active_client.md)

```
CLIENT_ID = {parsed from inputs/active_client.md}
CLIENT_NAME = {parsed from inputs/active_client.md}
FOLDER_NAME = {parsed from inputs/active_client.md}
FOUNDER = {resolved from founders subcollection}
```

## Prerequisites

- Stage 3 complete: `final-{PLATFORM}-posts-{DATE}.json` exists

## Inputs

| Input | Source | Description |
|-------|--------|-------------|
| `final-{PLATFORM}-posts-{DATE}.json` | Stage 3 | All generated posts |
| Context files | Stage 1 | For citation verification |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `qa-report.json` | File | QA results per post |
| Regenerated posts | Memory | If QA failed (max 2 attempts) |

---

## Platform-Specific QA

### LinkedIn (`--platform=linkedin`)

Invoke `linkedin-qa-reviewer` agent on all generated posts.

### Twitter (`--platform=twitter`)

When implemented: Use platform-specific QA rules.

---

## Zero-Tolerance Patterns

The QA reviewer checks for CRITICAL violations. Any of these cause automatic failure:

| Pattern | Description | Action |
|---------|-------------|--------|
| Em dashes (`--`) | Common AI writing tell | FAIL - Replace with comma or period |
| Rhetorical questions | Unless founder uses them naturally | FAIL - Remove or rephrase |
| Structures of 3 | "A, B, and C" lists | FAIL - Vary list lengths |
| "It's not X, it's Y" | Overused AI pattern | FAIL - Rephrase |
| Fabricated anecdotes | No citation in context_files_used | FAIL - Remove or cite |

---

## Agent Invocation

**Option A: Pass Content Inline (Recommended)**

Pass the actual post content directly in the prompt to avoid file discovery issues:

```
Task tool: linkedin-qa-reviewer
Prompt: Review generated posts for AI tells and quality.
        Apply zero-tolerance rules.

        POSTS TO REVIEW:
        {FINAL_POSTS_JSON}

        Context files available: {CONTEXT_FILES_LIST}
```

**Option B: Pass Explicit File Paths**

If passing file paths instead of content, provide the EXACT paths (the agent has Glob but explicit paths are faster):

```
Task tool: linkedin-qa-reviewer
Prompt: Review all LinkedIn posts for AI tells and quality.
        Apply zero-tolerance rules.

        Post files to review:
        - {FOLDER_NAME}/campaigns/ghostwrite-linkedin-{DATE}/final-linkedin-posts-{DATE}.json

        OR if reviewing batch files:
        - {FOLDER_NAME}/campaigns/ghostwrite-linkedin-{DATE}/posts/batch-1-posts.json
        - {FOLDER_NAME}/campaigns/ghostwrite-linkedin-{DATE}/posts/batch-2-posts.json
        - {FOLDER_NAME}/campaigns/ghostwrite-linkedin-{DATE}/posts/batch-3-posts.json
        - {FOLDER_NAME}/campaigns/ghostwrite-linkedin-{DATE}/posts/batch-4-posts.json

        Context files available: {CONTEXT_FILES_LIST}
```

**IMPORTANT**: The agent has `Glob` tool access, so it CAN discover files if given a directory pattern. However, explicit paths or inline content are more reliable.

---

## Expected Output

```json
{
  "reviewed_at": "2026-01-04T10:30:00Z",
  "total_posts": 20,
  "passed": 18,
  "failed": 2,
  "results": [
    {
      "post_id": "post-001",
      "status": "PASS",
      "voice_authenticity": 8.5,
      "citations_verified": true,
      "issues": []
    },
    {
      "post_id": "post-005",
      "status": "FAIL",
      "voice_authenticity": 6.0,
      "citations_verified": false,
      "issues": [
        {
          "type": "em_dash",
          "severity": "critical",
          "location": "line 3",
          "text": "...the solution -- and it's",
          "fix": "Replace with comma or period"
        },
        {
          "type": "structure_of_3",
          "severity": "critical",
          "location": "line 7",
          "text": "funding, community, and mentorship",
          "fix": "Vary list length or remove"
        }
      ],
      "regeneration_required": true
    }
  ]
}
```

---

## Failure Handling

If failures detected:

### Step 1: Log Violations
Document specific violations per post with:
- Issue type
- Location in post
- Problematic text
- Suggested fix

### Step 2: Regenerate Failed Posts
For each failed post:
1. Send back to ghostwriter with explicit constraint reminders
2. Include original post and QA feedback
3. Request regeneration fixing specific issues

```
Task tool: linkedin-ghostwriter
Prompt: Regenerate the following post fixing QA issues.
        Original post: {FAILED_POST}
        Issues found: {ISSUES_LIST}
        CRITICAL: Avoid em dashes, rhetorical questions, structures of 3.
```

### Step 3: Re-run QA
QA the regenerated post:
- If PASS: Update final posts file
- If FAIL: Attempt one more regeneration (max 2 attempts total)

### Step 4: Handle Persistent Failures
If a post fails QA after 2 regeneration attempts:
- Flag post as `needs-manual-review`
- Include in calendar with warning banner
- Continue with remaining posts
- Report in final summary

---

## Citation Verification

For each `context_files_used` citation:
1. Verify the referenced document exists
2. Verify the claim is supported by the document
3. Mark citation as verified or disputed

---

## Save QA Report

After QA review completes:

```bash
python skills/ghostwrite-content/scripts/write_json.py \
  "{CAMPAIGN_DIR}/qa-report.json" '{QA_REPORT_JSON}'
```

Mark stage complete:

```bash
python skills/ghostwrite-content/scripts/checkpoint.py "{CAMPAIGN_DIR}" complete "4"
```

---

## Quality Gate

- [ ] Zero critical violations (after regeneration)
- [ ] All citations verified
- [ ] Voice authenticity confirmed (average >= 7/10)
- [ ] All posts either PASS or flagged as `needs-manual-review`
- [ ] qa-report.json saved
- [ ] Checkpoint saved

---

## Error Handling

### All Posts Fail
If all posts fail QA:
- Log detailed issue report
- Suggest reviewing ghostwriter constraints
- Consider voice data quality (is Rebecca's voice clear enough?)
- Allow user to proceed with flagged posts or abort

### QA Agent Failure
If QA agent itself fails:
- Log error
- Proceed to Stage 5 with warning
- Note that QA was not completed in final report

---

## Next Stage

-> [Stage 5: Calendar Compilation](./05-calendar-compilation.md)
