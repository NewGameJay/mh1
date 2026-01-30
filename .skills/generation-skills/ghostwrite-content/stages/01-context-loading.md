# Stage 1: Context Loading

**Duration**: 1-2 minutes
**Blocking**: YES - All context must be loaded before proceeding

## Purpose

Load ALL required context in a single Python script call:
- Social listening posts
- Client context documents (brand, messaging, audience, strategy, competitive)
- Founder voice data (profile + posts)
- Voice contract extraction
- Thought leader posts (for topic curation)
- Parallel events (for timely content angles)

## Client Info (from active_client.md)

```
CLIENT_ID = {parsed from inputs/active_client.md}
CLIENT_NAME = {parsed from inputs/active_client.md}
FOLDER_NAME = {parsed from inputs/active_client.md}
```

## Context Loading Priority

**LOCAL-FIRST**: Company context documents are loaded from local files first, with Firestore as fallback.

| Data Type | Source Priority | Notes |
|-----------|-----------------|-------|
| Brand context | LOCAL -> Firestore | `{FOLDER_NAME}/context/brand.md` |
| Messaging context | LOCAL -> Firestore | `{FOLDER_NAME}/context/messaging.md` |
| Audience context | LOCAL -> Firestore | `{FOLDER_NAME}/context/audience.md` |
| Strategy context | LOCAL -> Firestore | `{FOLDER_NAME}/context/strategy.md` |
| Competitive context | LOCAL -> Firestore | `{FOLDER_NAME}/context/competitive.md` |
| Founder profile | Firestore only | `founders/{founderId}` - no local equivalent |
| Founder posts | Firestore only | `founders/{founderId}/posts` - no local equivalent |
| Signals | Firestore only | `signals` - collected data |
| Thought leaders | Firestore only | `thoughtLeaders/*/posts` - collected data |
| Parallel events | Firestore only | `parallelEvents/*` - collected data |

**Why LOCAL-FIRST?**
- Local files may have manual edits/refinements
- Faster loading (no network calls)
- Reduces Firestore read costs
- Collected data (social listening, events) must come from Firestore as that's where collection scripts store it

## Prerequisites

- Stage 0 complete: `CLIENT_ID` (from active_client.md) and `FOUNDER_ID` resolved

## Inputs

| Input | Source | Description |
|-------|--------|-------------|
| `CLIENT_ID` | active_client.md | Firestore Client ID |
| `FOUNDER_ID` | Stage 0 | Firestore founder document ID |
| `CLIENT_NAME` | active_client.md | Client display name |
| `--min-relevance` | Command arg | Minimum relevance score (default: 5) |
| `--max-source-posts` | Command arg | Maximum source posts (default: 25) |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `context_bundle.json` | File | All context for all stages (~22KB) |
| `voice_contract.json` | File | Compact founder voice rules (~2KB) |

---

## Step 1.1: Run preload_all_context.py

**Single script call loads ALL context** (local-first with Firestore fallback):

```bash
python skills/ghostwrite-content/scripts/preload_all_context.py {CLIENT_ID} {FOUNDER_ID} \
  --client-name "{CLIENT_NAME}" \
  --output-dir {FOLDER_NAME}/context-data/
```

**Example**:
```bash
python skills/ghostwrite-content/scripts/preload_all_context.py {CLIENT_ID} rebecca_minkoff_id \
  --client-name "{CLIENT_NAME}" \
  --output-dir {FOLDER_NAME}/context-data/
```

**Optional: Force Firestore-only mode** (skip local files):
```bash
python skills/ghostwrite-content/scripts/preload_all_context.py {CLIENT_ID} {FOUNDER_ID} \
  --firestore-only \
  --output-dir {FOLDER_NAME}/context-data/
```

**Script Output Files**:
- `context_bundle.json` - Full context bundle with per-stage subsets
- `voice_contract.json` - Compact voice rules for ghostwriter

**What the script loads**:

| Document | Local Path | Firestore Path |
|----------|------------|----------------|
| brand | `{FOLDER_NAME}/context/brand.md` | `clients/{CLIENT_ID}/context/brand` |
| messaging | `{FOLDER_NAME}/context/messaging.md` | `clients/{CLIENT_ID}/context/messaging` |
| audience | `{FOLDER_NAME}/context/audience.md` | `clients/{CLIENT_ID}/context/audience` |
| strategy | `{FOLDER_NAME}/context/strategy.md` | `clients/{CLIENT_ID}/context/strategy` |
| competitive | `{FOLDER_NAME}/context/competitive.md` | `clients/{CLIENT_ID}/context/competitive` |
| founder | N/A | `clients/{CLIENT_ID}/founders/{founderId}` |

**Always from Firestore** (no local equivalent):
- Founder profile and posts (founders subcollection)
- Signals (fetch_source_posts.py)
- Thought leader posts (fetch_thought_leader_posts.py)
- Parallel events (fetch_parallel_events.py)

---

## Step 1.2: Validate Output

Check script output for validation:

```json
{
  "success": true,
  "outputs": {
    "contextBundle": "{FOLDER_NAME}/context-data/context_bundle.json",
    "voiceContract": "{FOLDER_NAME}/context-data/voice_contract.json"
  },
  "metadata": {
    "localContextDocs": 5,
    "firestoreContextDocs": 0,
    "totalFirestoreReads": 1,
    "contextBundleSizeKB": 22.5,
    "voiceContractSizeKB": 2.1,
    "founderPostsAnalyzed": 100,
    "voiceConfidence": 0.85
  },
  "sources": {
    "brand": "local:{FOLDER_NAME}/context/brand.md",
    "messaging": "local:{FOLDER_NAME}/context/messaging.md",
    "audience": "local:{FOLDER_NAME}/context/audience.md",
    "strategy": "local:{FOLDER_NAME}/context/strategy.md",
    "competitive": "local:{FOLDER_NAME}/context/competitive.md"
  }
}
```

### Required (workflow STOPS if missing)
- [ ] `validation.brandVoicePresent` = true
- [ ] `validation.founderPostsMinimum` = true (10+ posts)
- [ ] `validation.sourcePostsMinimum` = true (5+ posts)

### Optional (workflow continues if missing)
- [ ] `statistics.thoughtLeaderPostsLoaded` > 0
- [ ] `statistics.parallelEventsLoaded` > 0

**If ANY required validation fails, STOP and report to user.**

---

## Step 1.3: Context Bundle Structure

The `context_bundle.json` contains:

```json
{
  "version": "1.0",
  "clientId": "{CLIENT_ID}",
  "founderId": "...",
  "loadedAt": "ISO timestamp",

  "fullContext": {
    "brand": { "brandVoice": {...}, "companyProfile": {...} },
    "messaging": { "valuePropositions": {...}, "positioning": {...} },
    "audience": { "personas": [...], "icpTargets": [...] },
    "strategy": { "positioning": {...}, "differentiators": {...} },
    "competitive": { "competitors": [...] }
  },

  "companyContext": {
    "overview": "MH-1 is a 501(c)(3) nonprofit...",
    "positioning": "Elevating women on a mission to break barriers",
    "valuePropositions": ["Community", "Resources", "Network"],
    "contentThemes": ["Female entrepreneurship", "Breaking barriers", "Community"]
  },

  "voiceContract": { "..." },

  "stageContexts": {
    "topicCurator": { "..." },
    "templateSelector": { "..." },
    "ghostwriter": { "..." }
  }
}
```

---

## Save Checkpoint

After context loading completes successfully:

```bash
python skills/ghostwrite-content/scripts/checkpoint.py "{CAMPAIGN_DIR}" complete "1"
```

---

## Quality Gate

- [ ] `context_bundle.json` created successfully
- [ ] `voice_contract.json` created successfully
- [ ] All required validations pass
- [ ] Checkpoint saved
- [ ] Ready for topic selection (Stage 1.75) or context-only mode (Stage 1.5)

---

## Next Stage

**If `--context-only` flag is set**:
-> [Stage 1.5: Context-Only Mode](./01.5-context-only.md)

**Otherwise**:
-> [Stage 1.75: Topic Curation](./01.75-topic-curation.md)

---

## Passing Context to Agents

After this stage, context is passed INLINE to agents. Agents do NOT read from Firestore.

**Stage 1.75 (Topic Curator)** receives:
- `stageContexts.topicCurator` (includes source posts, thought leaders, events)
- `companyContext`
- `voiceContract.topThemes` (for content gap analysis)

**Stage 2 (Template Selector)** receives:
- `stageContexts.templateSelector`
- `companyContext`
- `selectedTopics` (from Stage 1.75)

**Stage 3 (Ghostwriter)** receives:
- `stageContexts.ghostwriter`
- `companyContext`
- `voiceContract`
- `templateSelections` (from Stage 2)
