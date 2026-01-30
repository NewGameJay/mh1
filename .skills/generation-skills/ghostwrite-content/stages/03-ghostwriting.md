# Stage 3: Ghostwriting

**Duration**: 8-15 minutes
**Agent**: linkedin-ghostwriter (or platform-specific agent)
**Execution**: 4 parallel batches

## Purpose

Generate authentic social media posts in the founder's voice using template recommendations and voice contract. This is the core content generation stage.

## Client Info (from active_client.md)

```
CLIENT_ID = {parsed from inputs/active_client.md}
CLIENT_NAME = {parsed from inputs/active_client.md}
FOLDER_NAME = {parsed from inputs/active_client.md}
FOUNDER = {resolved from founders subcollection}
```

## CRITICAL: Incremental Save Pattern

**Each batch MUST be saved to disk immediately after the agent returns, BEFORE processing the next batch.**

This prevents data loss if context is exhausted mid-stage. The consolidation into `final-{platform}-posts.json` happens only AFTER all batch files are persisted.

### Save Order
```
Agent returns batch 1 -> IMMEDIATELY save batch-1-posts.json -> Update checkpoint
Agent returns batch 2 -> IMMEDIATELY save batch-2-posts.json -> Update checkpoint
Agent returns batch 3 -> IMMEDIATELY save batch-3-posts.json -> Update checkpoint
Agent returns batch 4 -> IMMEDIATELY save batch-4-posts.json -> Update checkpoint
All batches saved -> Consolidate into final-{platform}-posts.json
```

## Key Change: Context Passed Inline

**Agents receive context INLINE from orchestrator. NO Firestore reads in this stage.**

The ghostwriter receives:
- `voiceContract` from `voice_contract.json` (~3KB with post-type distribution)
- `companyContext` from `context_bundle.json`
- `founderHistoricalPosts` from `context_bundle.json` - **ALL founder posts** (up to 50) for voice matching
- `templateSelections` from Stage 2 (batch subset)
- `batchNumber` and `postsInBatch`

**Voice Matching Priority**: The ghostwriter now receives all founder posts to pattern-match against real examples. This increases token usage by ~12-15K but significantly improves voice authenticity.

## Prerequisites

- Stage 1 complete: `context_bundle.json` and `voice_contract.json` exist
- Stage 2 complete: `template-selections.json` exists

## Inputs

| Input | Source | Description |
|-------|--------|-------------|
| `voiceContract` | voice_contract.json | Compact voice rules + post-type distribution (~3KB) |
| `companyContext` | context_bundle.json | Condensed company context |
| `founderHistoricalPosts` | context_bundle.json | All founder posts for voice matching (up to 50) |
| `templateSelections` | Stage 2 | Template matches (batch subset) |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `batch-{N}-posts.json` | File | Posts from each batch |
| `final-{PLATFORM}-posts-{DATE}.json` | File | Consolidated final posts |

---

## Execution Pattern: 4 Parallel Batches

```
Task 1: linkedin-ghostwriter (posts 1-5)
Task 2: linkedin-ghostwriter (posts 6-10)
Task 3: linkedin-ghostwriter (posts 11-15)
Task 4: linkedin-ghostwriter (posts 16-20)
```

---

## Agent Prompt (Pass Context Inline)

```
Task tool: linkedin-ghostwriter
Prompt: Generate LinkedIn posts using the following context.

        VOICE CONTRACT:
        {VOICE_CONTRACT_JSON}

        COMPANY CONTEXT:
        {COMPANY_CONTEXT_JSON}

        FOUNDER HISTORICAL POSTS (study these for voice patterns):
        {FOUNDER_POSTS_JSON}

        IMPORTANT VOICE MATCHING INSTRUCTIONS:
        Before writing ANY posts, carefully analyze the founder's historical posts above.
        Study and replicate:
        - Opening sentence patterns (length, style, punch)
        - Paragraph structure and flow
        - Vocabulary and phrase choices
        - Post length variety (short takes vs deep dives)
        - Enthusiasm markers and personality
        - How they end posts (questions vs statements)

        The voice contract provides rules. The historical posts provide EXAMPLES.
        When in doubt, match the examples over the rules.

        Post Type Distribution (from voice contract):
        {POST_TYPE_DISTRIBUTION_JSON}
        Vary your post types to match the founder's natural distribution.

        TEMPLATE SELECTIONS (batch {N} of 4):
        {TEMPLATE_SELECTIONS_BATCH_JSON}

        Batch {N} of 4. Generate {postsInBatch} posts.

        Return posts as JSON array with voiceContractApplied metadata.
```

**CRITICAL**: Pass ALL context directly in the prompt. The agent does NOT read from Firestore or call any external data sources.

---

## Context Passed (Voice-First Approach)

- All founder posts (up to 50) for voice pattern matching
- Voice contract with post-type distribution analysis
- Company context (condensed)
- Template selections with inspiration summaries
- NOT Thought leader posts (handled by topic curator)
- NOT Parallel events (handled by topic curator)

The ghostwriter prioritizes matching the founder's actual writing style over strict template adherence.

---

## Expected Output

Each batch returns posts with metadata:

```json
{
  "posts": [
    {
      "postId": "batch-1-post-1",
      "content": "Full post text...",
      "metadata": {
        "templateId": 8,
        "templateName": "Industry hot take",
        "funnelStage": "TOFU",
        "characterCount": 1250,
        "voiceConfidence": 9,
        "topicId": "topic-001",
        "angle": "Female founder funding challenges"
      },
      "voiceContractApplied": {
        "sentenceAvgLength": 11,
        "signaturePhrasesUsed": ["Breaking barriers"],
        "constraintsValidated": ["no em dashes", "no rhetorical questions", "under 12 word opener"]
      }
    }
  ],
  "batchSummary": {
    "batchNumber": 1,
    "postsGenerated": 5,
    "avgVoiceConfidence": 8.6
  }
}
```

---

## Save Batch Outputs

**Use Python script for reliable JSON writes** (avoids Bash heredoc truncation):

```bash
# Save batch file using write_json.py
python skills/ghostwrite-content/scripts/write_json.py \
  "{FOLDER_NAME}/campaigns/ghostwrite-{PLATFORM}-{DATE}/posts/batch-{N}-posts.json" \
  '{BATCH_JSON}'
```

For large payloads, pipe via stdin:
```bash
echo '{BATCH_JSON}' | python skills/ghostwrite-content/scripts/write_json.py \
  "{FOLDER_NAME}/campaigns/ghostwrite-{PLATFORM}-{DATE}/posts/batch-{N}-posts.json"
```

### After Each Batch Save

1. **Verify write succeeded**: Check script output shows bytes written
2. **Update checkpoint**: Record batch as completed
   ```bash
   python skills/ghostwrite-content/scripts/checkpoint.py \
     "{CAMPAIGN_DIR}" save "3" "[1]"  # After batch 1
   ```
3. **Do NOT proceed to next batch until current batch is persisted**

---

## Consolidate Final Posts

**Only after ALL 4 batch files are saved to disk**:

1. Read all 4 `batch-{N}-posts.json` files
2. Merge `posts` arrays into single array
3. Sort by postId (maintain order)
4. Save consolidated file:
```bash
python skills/ghostwrite-content/scripts/write_json.py \
  "{FOLDER_NAME}/campaigns/ghostwrite-{PLATFORM}-{DATE}/final-{PLATFORM}-posts-{DATE}.json" \
  '{CONSOLIDATED_JSON}'
```
5. Mark stage complete:
```bash
python skills/ghostwrite-content/scripts/checkpoint.py "{CAMPAIGN_DIR}" complete "3"
```

---

## Quality Gate

- [ ] All 4 batch files saved (`batch-1-posts.json` through `batch-4-posts.json`)
- [ ] **REQUIRED**: Consolidated file created (`final-{PLATFORM}-posts-{DATE}.json`)
- [ ] All posts generated for batch count
- [ ] Average voice confidence >= 8/10 (raised from 7/10 with historical posts available)
- [ ] All voiceContract.antiPatterns avoided
- [ ] All posts within length range (or flagged)
- [ ] MOFU/BOFU posts have MH-1 tie-back
- [ ] Post variety matches the founder's distribution
- [ ] Opening styles match the founder's historical patterns

**CRITICAL**: Do NOT proceed to Stage 4 without creating the consolidated file. Stage 4 expects `final-{PLATFORM}-posts-{DATE}.json` as input.

---

## Error Handling

### Batch Failure
If a batch fails:
1. Retry batch once
2. If still failing, log error and continue with other batches
3. Report incomplete batch in Stage 6

### Low Voice Confidence
If average voiceConfidence < 7/10:
- Log warning
- Continue to QA stage
- Report in final summary

---

## Resume Behavior

If resuming from checkpoint with partial Stage 3 completion:

1. **Check checkpoint**: `python checkpoint.py "{CAMPAIGN_DIR}" load`
2. **Identify completed batches**: Look at `batchesCompleted["3"]` array
3. **Skip completed batches**: Only run agents for missing batches
4. **Example**: If batches `[1, 2]` completed, only run agents for batches 3 and 4
5. **Continue incremental saves** for remaining batches

```bash
# Example: Resume from batch 3
checkpoint = {"batchesCompleted": {"3": [1, 2]}}
# Run only: batch 3, batch 4
# Save each immediately after agent returns
```

---

## Next Stage

-> [Stage 4: QA Review](./04-qa-review.md)
