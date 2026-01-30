# lib/ Directory Inventory (Post-Cleanup)

**Date:** 2026-01-30
**Status:** CLEANED - Ready for AI-first CLI

---

## Current State: 16 Core Files

After cleanup, we kept only the essential infrastructure modules:

| File | Size | Purpose |
|------|------|---------|
| `__init__.py` | - | Module exports |
| `agent_council.py` | 40KB | Orchestrator/worker/evaluator coordination |
| `budget.py` | 21KB | Cost tracking per tenant |
| `client_selector.py` | 30KB | Client selection/fuzzy matching |
| `context_orchestrator.py` | 55KB | 3-level progressive context loading |
| `evaluator.py` | 27KB | Quality checks (6 dimensions) |
| `firebase_client.py` | 29KB | Thread-safe Firebase client |
| `idempotency.py` | 47KB | Prevent duplicate work |
| `intelligence_bridge.py` | 43KB | Interface to learning/memory system |
| `mcp_client.py` | 10KB | MCP server connections |
| `multimodal.py` | 2KB | Image/video analysis |
| `persona_builder.py` | 24KB | Build personas from client data |
| `registry.py` | 4KB | Skill discovery |
| `release_policy.py` | 5KB | Release decisions |
| `storage.py` | 4KB | Artifact management |
| `telemetry.py` | 22KB | Run logging to SQLite |

**Plus subdirectories:**
- `lib/intelligence/` - Memory and learning systems
- `lib/cli/` - NEW: AI-first CLI module

---

## New CLI Module (`lib/cli/`)

Created as part of the v2.0 rebuild:

| File | Purpose |
|------|---------|
| `__init__.py` | Module exports |
| `state.py` | Session state management (client, chat history) |
| `display.py` | Rich terminal rendering (menus, chat, panels) |

---

## Deleted (28 files, ~750KB)

All CLI-specific code that was hardcoded:

- `planner.py` - Hardcoded planning logic
- `copilot_planner.py` - Discovery steps
- `cli_menus.py` - Old menu system
- `module_manager.py` - Complex state machine
- `skill_runner.py` - Old execution
- `runner.py` - Old workflow runner
- `executor.py` - Broken hybrid executor
- `mh1_executor.py` - Broken unified executor
- `browser_automation.py` - Not needed for v2
- `browser_rate_limiter.py` - Not needed for v2
- ... and 18 more files

---

## Design Philosophy

The remaining lib/ modules are **tool providers**, not logic controllers:

1. **Claude decides** what to do (reads skills, picks agents)
2. **lib/ modules provide** capabilities (Firebase, MCP, evaluation)
3. **CLI displays** results (Rich terminal UI)

No hardcoded workflows. No scripted pipelines. AI-first.

---

## Integration Map

```
User Input
    │
    ▼
┌─────────────────┐
│   CLI (mh1)     │  ← Presentation layer
└─────────────────┘
    │
    ▼
┌─────────────────┐
│    Claude       │  ← Decision layer (reads skills, picks tools)
└─────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│              lib/ modules                │
├─────────────────────────────────────────┤
│ context_orchestrator → Load context     │
│ agent_council → Coordinate agents       │
│ persona_builder → Build personas        │
│ firebase_client → Data persistence      │
│ mcp_client → External tools             │
│ evaluator → Quality gates               │
│ release_policy → Delivery decisions     │
│ budget → Cost tracking                  │
│ telemetry → Run logging                 │
└─────────────────────────────────────────┘
```

---

## What Claude Needs

For the AI-first CLI to work, Claude needs these tool capabilities:

### Context Loading
- `load_client_context(client_id)` → Uses context_orchestrator
- `list_clients()` → Uses firebase_client
- `switch_client(client_id)` → Updates session state

### Skill Execution
- `list_skills()` → Uses registry
- `get_skill(name)` → Reads SKILL.md
- `run_skill(name, inputs)` → Follows SKILL.md instructions

### Agent Coordination
- `list_agents()` → Reads agent definitions
- `talk_to_agent(name, message)` → Adopts agent persona
- `assemble_council(task)` → Uses agent_council

### Data Operations
- `query_crm(query)` → Uses mcp_client (HubSpot/Salesforce)
- `query_warehouse(query)` → Uses mcp_client (Snowflake/BigQuery)
- `get_firebase_doc()` → Uses firebase_client
- `set_firebase_doc()` → Uses firebase_client

### Quality & Delivery
- `evaluate_output(output)` → Uses evaluator
- `check_release_policy(output)` → Uses release_policy
- `log_run(details)` → Uses telemetry

All logic is Claude reading files and calling these tools. No scripts.
