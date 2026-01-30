# Stage 0: ID Resolution (Parse active_client.md)

**Duration**: INSTANT (no Firestore query needed)
**Blocking**: YES - All subsequent stages require CLIENT_ID and FOUNDER_ID

## Purpose

Read client configuration from `inputs/active_client.md`, then resolve founder ID from Firestore.

## Step 0.0: Parse active_client.md

**Read client configuration from `inputs/active_client.md`:**

```
CLIENT_ID = {Firestore Client ID from file}
CLIENT_NAME = {Client Name from file}
FOLDER_NAME = {Folder Name from file}
DEFAULT_FOUNDER = {Default Ghostwrite Founder from file}
```

---

## FIRST: Check for Existing Checkpoint

Before resolving founder ID, check if a previous run was interrupted:

```bash
python skills/ghostwrite-content/scripts/checkpoint.py "{CAMPAIGN_DIR}" load
```

If checkpoint exists with `completedStages` array:
1. **Prompt user**: "Previous run found at stage {currentStage}. Resume? [Y/n]"
2. **If yes**: Skip to first incomplete stage, reuse stored IDs
3. **If no**: Start fresh, overwrite checkpoint

---

## Step 0.1: Client ID (INSTANT)

**No Firestore query needed.**

```
CLIENT_ID = "{CLIENT_ID}"
CLIENT_NAME = "{CLIENT_NAME}"
```

Display:
```
Client resolved (hardcoded): {CLIENT_NAME} -> {CLIENT_ID}
```

---

## Step 0.2: Resolve Founder ID from Founder Name

Query the `founders` subcollection within the {CLIENT_NAME} client:

```
mcp__firebase-mcp__firestore_list_documents
Collection: clients/{CLIENT_ID}/founders
```

**Default Founder**: If no founder name is provided, use "Raaja Nemani" (President).
**Alternate Founder**: "Chris Toy" (CEO) can be specified as an argument.

Search for a document where:
- `name` matches `{FOUNDER_NAME}` (case-insensitive)

**Matching Logic**:
- Normalize both search term and field values (lowercase, trim whitespace)
- Partial matching allowed: "Raaja" matches "Raaja Nemani" if only one Raaja exists
- If multiple partial matches, require exact match or report ambiguity

**On Success**: Store the document ID as `FOUNDER_ID` for use in all subsequent stages.

**On Failure**:
```
Error: Founder not found.

Searched for: "{FOUNDER_NAME}" in {CLIENT_NAME}
No matching founder found in founders subcollection.

Available founders for this client:
- Raaja Nemani (President) - default
- Chris Toy (CEO)

Solutions:
1. Check spelling and try again
2. Run founder-post-ingest agent to collect founder content first
```

---

## Step 0.3: Display Resolution Results

After successful resolution, display:

```
Client resolved (hardcoded): {CLIENT_NAME} -> {CLIENT_ID}
Founder resolved: {FOUNDER_NAME} -> {FOUNDER_ID}

Proceeding to Stage 1: Context Loading...
```

---

## Step 0.4: Initialize Checkpoint

Create checkpoint for this run:

```bash
python skills/ghostwrite-content/scripts/checkpoint.py "{CAMPAIGN_DIR}" init "{CLIENT_ID}" "{FOUNDER_ID}"
```

Then mark Stage 0 complete:

```bash
python skills/ghostwrite-content/scripts/checkpoint.py "{CAMPAIGN_DIR}" complete "0"
```

---

## Quality Gate

- [x] CLIENT_ID parsed from `inputs/active_client.md`
- [ ] FOUNDER_ID resolved from founders subcollection
- [ ] Both IDs confirmed to exist in Firestore

**DO NOT proceed to Stage 1 until FOUNDER_ID is resolved.**

---

## Next Stage

-> [Stage 1: Context Loading](./01-context-loading.md)
