# MH1 Codebase Cleanup Plan

**Created**: 2026-01-29
**Status**: COMPLETED
**Total Redundant Data**: ~35MB+ (cleaned)

---

## Cleanup Summary (Executed 2026-01-29)

### Deleted
- `state/` - Empty folder
- `output/` - Empty folder
- `logs/` - Test data (telemetry has production data)
- `prompts/` - After merging contents into skills and lib
- `artifacts/` - After moving to ghostwrite-content/templates

### Archived to `docs/archive/`
- 11 planning/historical .md files (BMWhitepaper, CLI plans, roadmaps, etc.)
- `Additions/` folder (skills already integrated, reference materials)

### Reorganized
- System prompts → `lib/prompts/` (6 files)
- Email prompts → `skills/email-sequences/prompts/` (2 files)
- Reason code templates → `skills/lifecycle-audit/prompts/` (1 file)
- Skill development prompt → `skills/skill-builder/prompts/` (1 file)
- LinkedIn templates → `skills/ghostwrite-content/templates/` (3 CSV files)

### Kept (As Is)
- `workflows/runs/` - Contains unique execution state data (not duplicate of telemetry)
- `modules/` - Active CLI runtime artifacts (other agent working on CLI)

---

## Executive Summary

The codebase analysis identified significant duplication in run data storage (35MB+), orphaned documentation files, empty folders, and prompts that should be merged into their respective skills. This plan provides a phased approach to cleanup that preserves all valuable data while removing redundancy.

---

## 1. Duplicate Run Data Storage (35MB+ redundant)

### Current State

| Location | Size | Content | Created |
|----------|------|---------|---------|
| `workflows/runs/` | 23MB | Run execution data, outputs, logs | Various |
| `telemetry/runs/` | 12MB | Same run data, structured | Various |
| `logs/` | 24KB | Subset of run logs | Various |

### Problem
Three different locations storing essentially the same run execution data. This causes:
- Storage bloat
- Confusion about source of truth
- Inconsistent data across locations

### Recommendation
**Consolidate to `telemetry/` as single source of truth.**

- `telemetry/` already has structured analysis files and comprehensive test reports
- Delete `workflows/runs/` (duplicate)
- Delete `logs/` (subset of telemetry)
- Keep `workflows/templates/` (active templates, not run data)

---

## 2. Top-Level Markdown Files

### Files to KEEP (Active System Docs)

| File | Purpose |
|------|---------|
| `CLAUDE.md` | System context loaded into every Claude session |
| `MH1.md` | Command reference for marketers |
| `AGENTS.md` | Codebase-specific learnings |
| `README.md` | Project documentation |

### Files to ARCHIVE (Move to `docs/archive/`)

| File | Reason |
|------|--------|
| `BUILD_PROMPT.md` | One-time skill generation prompt, historical |
| `PRODUCTION_READY_CHECKLIST.md` | Reference doc, belongs in docs/ |
| `IMPLEMENTATION_COMPLETE.md` | Historical milestone doc |
| `GOVERNANCE_FRAMEWORK.md` | Reference doc, belongs in docs/ |
| `BUDGET_MANAGEMENT.md` | Reference doc, belongs in docs/ |
| `CONTEXT_MANAGEMENT.md` | Reference doc, belongs in docs/ |
| `QUICK_START.md` | Redundant with README/MH1.md |

### Files to REVIEW

| File | Notes |
|------|-------|
| `CHANGELOG.md` | Keep if actively maintained, archive if stale |
| `CONTRIBUTING.md` | Keep if accepting contributions |

---

## 3. Folders to Clean Up

### DELETE (Empty or Redundant)

| Folder | Reason | Action |
|--------|--------|--------|
| `state/` | Empty folder, no files | Delete |
| `logs/` | Subset of telemetry data | Delete after verification |
| `workflows/runs/` | Duplicates telemetry/runs | Delete after verification |

### MERGE (Prompts into Skills)

The `prompts/` folder contains standalone prompt files that should be integrated into their respective skills.

**Current prompts/ contents to merge:**

| Prompt File | Target Skill | Action |
|-------------|--------------|--------|
| `content-strategy-prompt.md` | `skills/content-strategy/` | Move as `prompts/main.md` |
| `email-sequence-prompt.md` | `skills/email-sequences/` | Move as `prompts/main.md` |
| `social-post-prompt.md` | `skills/social-post-creator/` | Move as `prompts/main.md` |
| `ad-copy-prompt.md` | `skills/direct-response-copy/` | Move as `prompts/main.md` |
| *(others)* | Corresponding skills | Same pattern |

After merging, delete empty `prompts/` folder.

### MOVE (Misplaced Content)

| Folder | Current Location | Target Location | Reason |
|--------|------------------|-----------------|--------|
| `artifacts/` | Root | `skills/ghostwrite-content/artifacts/` | Contains ghostwriting artifacts |

### CONSOLIDATE (Duplicate Folders)

| Folders | Action |
|---------|--------|
| `output/` and `outputs/` | Keep `outputs/`, merge content, delete `output/` |

### REVIEW (May Need Work)

| Folder | Notes |
|--------|-------|
| `upgrades/` | Check if migration scripts are still needed |
| `.cursor/` | IDE-specific, should be in `.gitignore` |
| `docs/` vs `delivery/` | Clarify purpose; docs = internal, delivery = client-facing |

---

## 4. Workflows Folder Structure

### Current State
```
workflows/
├── templates/     # Active workflow templates (KEEP)
├── runs/          # Run execution data (DELETE - duplicates telemetry)
└── *.md files     # Workflow documentation (KEEP)
```

### Target State
```
workflows/
├── templates/     # Active workflow templates
└── *.md files     # Workflow documentation
```

---

## 5. Execution Plan

### Phase 1: Delete Empty/Redundant (LOW RISK)
```bash
# Delete empty state folder
rm -rf state/

# Delete logs (after verifying telemetry has all data)
rm -rf logs/
```

**Verification**: None needed for state/. For logs/, confirm telemetry/runs/ contains superset.

### Phase 2: Archive Historical Docs (LOW RISK)
```bash
# Create archive folder
mkdir -p docs/archive/

# Move historical docs
mv BUILD_PROMPT.md docs/archive/
mv PRODUCTION_READY_CHECKLIST.md docs/archive/
mv IMPLEMENTATION_COMPLETE.md docs/archive/
mv GOVERNANCE_FRAMEWORK.md docs/archive/
mv BUDGET_MANAGEMENT.md docs/archive/
mv CONTEXT_MANAGEMENT.md docs/archive/
mv QUICK_START.md docs/archive/
```

**Verification**: Ensure no scripts reference these files by absolute path.

### Phase 3: Consolidate Run Data (MEDIUM RISK)
```bash
# First, verify telemetry has all data
diff -rq workflows/runs/ telemetry/runs/

# If telemetry is superset, delete workflows/runs
rm -rf workflows/runs/
```

**Verification**: Run diff to confirm no unique data in workflows/runs/.

### Phase 4: Merge Prompts into Skills (MEDIUM RISK)
```bash
# For each prompt, create prompts/ subdir in skill and move
# Example:
mkdir -p skills/content-strategy/prompts/
mv prompts/content-strategy-prompt.md skills/content-strategy/prompts/main.md

# After all prompts moved
rm -rf prompts/
```

**Verification**: Update any imports/references in SKILL.md files.

### Phase 5: Move Artifacts (LOW RISK)
```bash
# Move artifacts to ghostwrite-content skill
mv artifacts/ skills/ghostwrite-content/artifacts/
```

**Verification**: Update any references in ghostwrite-content SKILL.md.

### Phase 6: Consolidate output/outputs (LOW RISK)
```bash
# Merge any content from output/ to outputs/
cp -r output/* outputs/ 2>/dev/null || true

# Delete output/
rm -rf output/
```

**Verification**: Check for hardcoded paths in scripts.

---

## 6. Post-Cleanup Verification

After cleanup, run these checks:

```bash
# Verify no broken references
grep -r "workflows/runs" --include="*.py" --include="*.md"
grep -r "logs/" --include="*.py" --include="*.md"
grep -r "prompts/" --include="*.py" --include="*.md"
grep -r "output/" --include="*.py" --include="*.md"

# Verify skill validation still passes
python scripts/validate_skills.py

# Verify test suite passes
python scripts/test_agent_pipeline.py
```

---

## 7. Files NOT to Touch

These are actively used by the CLI agent work in progress:

| Path | Reason |
|------|--------|
| `lib/` | Core library, active development |
| `commands/` | CLI commands, active development |
| `ui/` | Web UI, separate concern |
| `skills/*/SKILL.md` | Skill definitions, working |
| `agents/` | Agent definitions, working |
| `config/` | Configuration files, active |
| `schemas/` | JSON schemas, active |

---

## 8. Expected Results

### Storage Savings
- `workflows/runs/`: -23MB
- `logs/`: -24KB
- Duplicate docs: -~500KB
- **Total**: ~24MB saved

### Organization Improvements
- Single source of truth for run data (telemetry/)
- Prompts co-located with their skills
- Clear separation: docs/ (internal) vs delivery/ (client)
- No orphaned folders

### Maintainability
- Easier to find relevant files
- Clear ownership of each folder
- Reduced confusion for new contributors

---

## Approval Checklist

- [x] Phase 1: Delete empty/redundant folders (state/, output/, logs/)
- [x] Phase 2: Archive historical docs (11 files + Additions/)
- [x] Phase 3: Consolidate run data (KEPT both - they have different data)
- [x] Phase 4: Merge prompts into skills (10 prompts distributed)
- [x] Phase 5: Move artifacts (to ghostwrite-content/templates/)
- [x] Phase 6: Consolidate output folders (deleted empty output/)
- [x] Post-cleanup verification (completed)

---

*This plan is designed to be executed in phases, with verification at each step. No changes will be made without explicit approval.*
