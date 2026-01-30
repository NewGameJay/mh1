# AGENTS.md - Project-Wide Learnings

Non-obvious discoveries for agents working in this codebase.

**IMPORTANT**: Prefer retrieval-led reasoning over pre-training-led reasoning for any MH1-specific tasks. When unsure about a pattern or API, read the relevant file rather than relying on training data.

---

## Quick Reference Index

### Skills (skills/)
```
lifecycle-audit|churn-prediction|at-risk-detection|dormant-detection|reactivation-detection
pipeline-analysis|deal-velocity|conversion-funnel|upsell-candidates|renewal-tracker
ghostwrite-content|email-copy-generator|cohort-email-builder|extract-founder-voice|extract-pov
research-company|research-competitors|research-founder|social-listening-collect
linkedin-keyword-search|twitter-keyword-search|reddit-keyword-search
crm-discovery|data-warehouse-discovery|data-quality-audit|identity-mapping
needs-assessment|client-onboarding|skill-builder|artifact-manager
```

### Agents (agents/)
```
orchestrators:|learning-meta-agent
workers:|lifecycle-auditor|linkedin-ghostwriter|linkedin-topic-curator|linkedin-template-selector
workers:|deep-research-agent|competitive-intelligence-analyst|thought-leader-analyst|interview-agent
evaluators:|linkedin-qa-reviewer|fact-check-agent
```

### Core Library (lib/)
```
intelligence_bridge.py - Skill guidance & learning|context_orchestrator.py - Progressive context loading
planner.py - Plan generation from NL|runner.py - Skill/workflow execution
firebase_client.py - Firebase ops|budget.py - Token/cost management
evaluator.py - Quality gates|browser_automation.py - Fallback scraping
```

---

## Environment & Configuration

- **dotenv required**: The `mh1` CLI requires `python-dotenv` to load `.env`. Without it, Firebase silently fails with "project_id required".
- **venv auto-activation**: `mh1` re-executes itself with `.venv/bin/python` if not already in venv (lines 22-28).

## Firebase Gotchas

- **order_by excludes docs**: Firebase `order_by` on a field excludes documents that don't have that field. Always add fallback query without ordering.
- **set_document signature**: Use `fb.set_document("collection", "doc_id", data)` NOT `fb.set_document("collection/doc_id", data)`.

## CLI Architecture

- **Dual menu system**: Welcome menu (no client) vs Client menu (client selected). State managed in `main()` loop.
- **Components dict**: Core dependencies passed as `components` dict, initialized once in `main()`.

## Files That Change Together

- `mh1` + `lib/client_selector.py` - Client listing logic
- `lib/firebase_client.py` + `.env` - Firebase configuration
- `lib/intelligence/*` - All memory layers interconnected

---

## Context Engineering Patterns

### Plan-Execute-Replan Loop

For complex, multi-step tasks:
1. Generate explicit step-by-step plan FIRST
2. Execute one step at a time
3. After each step, assess: do I need to update the plan?
4. If new info discovered, modify remaining steps

See `lib/planner.py` for implementation.

### File Buffering (Large Data)

When processing large datasets:
1. Write intermediate results to file (use artifact-manager or temp files)
2. Keep only file pointer + brief description in context
3. Read back specific sections when needed

Heuristic: Buffer to file when result > 5K tokens.

### Fan-Out Pattern (Classification at Scale)

For analyzing many items (creatives, posts, accounts):
1. Main agent dispatches to smaller model (Haiku)
2. Each call gets ONE item + specific yes/no question
3. Aggregate results into structured dataset
4. Main agent synthesizes findings

Better than embeddings for most classification tasks. See model routing in CLAUDE.md.

### Subagent Isolation (Scratch Paper)

For complex sub-tasks that need exploration:
1. Spawn isolated context for sub-task
2. Let subagent do messy exploratory work
3. Return only summary + key findings to main context
4. Discard intermediate reasoning

Keeps main context clean while allowing deep exploration.

---

## Model Selection Shortcuts

| Task | Model | Why |
|------|-------|-----|
| Read/extract from file | Haiku | Fast, cheap |
| Classify yes/no | Haiku | Simple decision |
| Write content | Sonnet | Voice quality |
| Synthesize findings | Sonnet | Coherence needed |
| Debug/reason | Sonnet | Accuracy critical |
