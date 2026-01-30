# MH1 CLI Architecture & Implementation Guide

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            USER INTERFACE                                   │
│                                                                             │
│   CLI Entry Point (./mh1)                                                   │
│   ├── Welcome Menu (no client selected)                                     │
│   │   ├── [1] Continue (Select Client) → select_or_onboard()               │
│   │   ├── [2] Create New Client → create_client_wizard()                   │
│   │   ├── [3] Browse Skills → show_skills_browser()                        │
│   │   ├── [4] Browse Agents → show_agents_browser()                        │
│   │   └── [5] Chat Mode → run_chat_mode()                                  │
│   │                                                                         │
│   └── Client Menu (client selected)                                         │
│       ├── [1] Ask (NL) → handle_plan_request()                             │
│       ├── [2] Plans → show_plans_menu()                                    │
│       ├── [3] Skills → show_skills_browser()                               │
│       ├── [4] Agents → show_agents_browser()                               │
│       ├── [5] Query/Refresh → process_with_plan()                          │
│       ├── [6] Details → show_client_details()                              │
│       └── [7] History → show_status_screen()                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         REQUEST PROCESSING                                  │
│                                                                             │
│   handle_plan_request(request, client, components)                         │
│   │                                                                         │
│   ├── Check for plan_generator (new) vs copilot_planner (legacy)           │
│   │                                                                         │
│   ├── NEW FLOW (with intelligence):                                         │
│   │   └── PlanGenerator.generate(request, client_id)                       │
│   │       ├── IntentParser: NL → ParsedIntent                              │
│   │       ├── ContextOrchestrator.load_for_planning()                      │
│   │       │   ├── Level 1: Client profile + voice contract                 │
│   │       │   └── Level 2: Matched skills + agents                         │
│   │       ├── SkillMatcher: Intent → Skills sequence                       │
│   │       ├── AgentMatcher: Skills → Agent assignments                     │
│   │       ├── ModuleAssembler: Skills → Modules with guardrails            │
│   │       └── PlanWriter: Generate .plan.md file                           │
│   │                                                                         │
│   └── LEGACY FLOW (without intelligence):                                   │
│       └── process_with_plan(request, client, components)                   │
│           ├── CopilotPlanner.analyze_request()                             │
│           ├── Clarifier.needs_clarification()                              │
│           └── Execute steps sequentially                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PLAN EXECUTION                                      │
│                                                                             │
│   execute_plan(plan_path, client, components)                              │
│   │                                                                         │
│   For each step in plan.steps:                                              │
│   │                                                                         │
│   ├── 1. IntelligenceBridge.get_skill_guidance()                           │
│   │      → Returns: parameters, confidence, patterns                        │
│   │                                                                         │
│   ├── 2. IntelligenceBridge.start_tracking()                               │
│   │      → Registers prediction, returns tracking_id                        │
│   │                                                                         │
│   ├── 3. ContextOrchestrator.load_for_execution()                          │
│   │      ├── Level 1: Client profile (always)                              │
│   │      ├── Level 2: Skill metadata + agents                              │
│   │      └── Level 3: Full skill content + patterns                        │
│   │                                                                         │
│   ├── 4. Execute skill via subprocess                                       │
│   │      → claude -p "Run skill: skills/{name}/SKILL.md"                   │
│   │                                                                         │
│   ├── 5. IntelligenceBridge.complete_tracking()                            │
│   │      → Updates memory: episodic → semantic → procedural                 │
│   │                                                                         │
│   └── 6. WorkflowState.update_workflow_phase()                             │
│          → Advances phase, updates metrics                                  │
│                                                                             │
│   After all steps: IntelligenceBridge.consolidate()                        │
│   → Decay memories, promote patterns                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                         │
│                                                                             │
│   FirebaseClient (lib/firebase_client.py)                                   │
│   ├── set_document(collection, doc_id, data, subcollection, subdoc_id)     │
│   ├── get_document(collection, doc_id, subcollection, subdoc_id)           │
│   ├── get_collection(collection, filters, order_by, limit)                 │
│   └── batch_write(operations)                                              │
│                                                                             │
│   ContextSync (lib/context_sync.py)                                        │
│   ├── sync_to_local() - Pull from Firebase                                 │
│   ├── sync_to_firebase() - Push to Firebase                                │
│   └── check_status() - Compare local vs remote                             │
│                                                                             │
│   InteractionStore (lib/interaction_store.py)                              │
│   ├── log_interaction() - Store session data                               │
│   └── get_recent_interactions() - Retrieve history                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Dependencies

```
mh1 (CLI Entry)
├── lib/client_selector.py      # Client selection & persistence
│   └── lib/firebase_client.py  # Firebase storage
│   └── lib/workflow_state.py   # Phase tracking
│
├── lib/copilot_planner.py      # LEGACY: User-approved planning
│   └── lib/command_router.py   # Command → Skill mapping
│   └── lib/client_selector.py
│
├── lib/planner.py              # NEW: .plan.md generation
│   └── lib/context_orchestrator.py  # Progressive context
│   └── lib/intelligence_bridge.py   # Learning interface
│
├── lib/clarifier.py            # Clarification questions
│   └── lib/copilot_planner.py
│
├── lib/interaction_store.py    # Session logging
│   └── lib/firebase_client.py
│
├── lib/improvement_engine.py   # Feedback processing
│
└── lib/context_sync.py         # Local ↔ Firebase sync
    └── lib/firebase_client.py
```

## Bug Analysis

### Bug 1: Firebase `db` Attribute Error

**Location:** `lib/context_sync.py` lines 131, 146
**Symptom:** `'FirebaseClient' object has no attribute 'db'`

**Root Cause:**
```python
# context_sync.py tries to access:
self.firebase.db.document(path).get()
self.firebase.db.document(path).set(data)

# But FirebaseClient doesn't expose .db - it uses internal methods
```

**Fix:** Add `db` property to FirebaseClient or use existing methods:
```python
# Option A: Add property to FirebaseClient
@property
def db(self):
    with self._get_client() as client:
        return client

# Option B: Use existing methods in context_sync
self.firebase.get_document(collection, doc_id)
self.firebase.set_document(collection, doc_id, data)
```

### Bug 2: Interaction Logging Path Error

**Location:** `lib/interaction_store.py` line 249-254
**Symptom:** `A document must have an even number of path elements`

**Root Cause:**
```python
fb.set_document(
    "system",
    "copilot",
    interaction.to_dict(),
    subcollection=f"interactions/{tenant_id}",  # BUG: slash in collection name!
    subdoc_id=interaction.interaction_id
)
```

Firestore paths must be: `collection/document/collection/document/...`
The `subcollection` parameter should be just `"interactions"`, not `f"interactions/{tenant_id}"`

**Fix:**
```python
fb.set_document(
    f"clients/{tenant_id}",  # Collection path
    "interactions",           # Document (parent for subcollection)
    {"_placeholder": True},   # Placeholder if needed
    subcollection="entries",
    subdoc_id=interaction.interaction_id
)
# Or better: use add_document for auto-ID
fb.add_document(
    f"clients/{tenant_id}/interactions",
    interaction.to_dict()
)
```

## CLI Improvements

### Phase 1: Critical Fixes

1. **Add argparse for CLI arguments**
   - `--help`, `--version` flags
   - `--client` to pre-select client
   - `--non-interactive` for scripting

2. **Fix Firebase bugs**
   - Add `db` property or refactor context_sync
   - Fix interaction logging paths

3. **Better error handling**
   - Catch Firebase errors gracefully
   - Show user-friendly messages

### Phase 2: UX Improvements

1. **Unified menu with breadcrumbs**
2. **Progress persistence**
3. **Shell completion**
4. **Config file support**

### Phase 3: Headless/API Mode

Two execution strategies:

**Strategy A: Claude Code CLI (current)**
```python
subprocess.run(['claude', '-p', prompt, '--output-format', 'text'])
```
- Pros: MCP tools available, full Claude Code features
- Cons: Requires Claude Code installed

**Strategy B: Direct Anthropic API (fallback)**
```python
from anthropic import Anthropic
client = Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": prompt}]
)
```
- Pros: Truly headless, no external dependencies
- Cons: No MCP tools, manual tool handling

**Recommended: Hybrid approach**
```python
def execute_prompt(prompt: str, needs_tools: bool = False):
    if needs_tools and shutil.which('claude'):
        return execute_via_claude_code(prompt)
    return execute_via_api(prompt)
```

## Data Flow Examples

### Example 1: "Write LinkedIn posts about AI"

```
1. CLI receives: "write linkedin posts about AI"
   └── handle_plan_request()

2. PlanGenerator.generate()
   ├── IntentParser → ParsedIntent(type="content", domain="linkedin", topic="AI")
   ├── ContextOrchestrator.load_for_planning()
   │   ├── Level 1: Client profile, voice contract
   │   └── Level 2: Skills [ghostwrite-content, social-listening-collect]
   ├── SkillMatcher → [social-listening-collect, create-assignment-brief, ghostwrite-content]
   ├── AgentMatcher → {ghostwrite-content: linkedin-ghostwriter}
   └── PlanWriter → modules/client-id/20260129-write-linkedin-posts.plan.md

3. User reviews and approves plan

4. execute_plan()
   For each step:
   ├── IntelligenceBridge.get_skill_guidance()
   ├── IntelligenceBridge.start_tracking()
   ├── ContextOrchestrator.load_for_execution()
   ├── subprocess: claude -p "Run skill: skills/ghostwrite-content/SKILL.md"
   └── IntelligenceBridge.complete_tracking()

5. Results shown, feedback collected
   └── ImprovementEngine.process_feedback()
```

### Example 2: Context Loading Budget

```
Request: "Lifecycle analysis of HubSpot contacts"
Budget: 100K tokens (4K output, 2K system reserved = 94K available)

Level 1 (always loaded): ~2,500 tokens
  - clients/{id}/config/datasources.yaml: 500 tokens
  - clients/{id}/context/voice-contract.json: 1,500 tokens
  - clients/{id}/metadata/profile.json: 500 tokens

Level 2 (planning phase): ~4,000 tokens
  - skills/lifecycle-audit/SKILL.md frontmatter: 800 tokens
  - skills/churn-prediction/SKILL.md frontmatter: 600 tokens
  - agents/workers/lifecycle-auditor.md: 1,200 tokens
  - agents/workers/data-auditor.md: 1,400 tokens

Level 3 (execution phase): ~15,000 tokens
  - skills/lifecycle-audit/SKILL.md full: 8,000 tokens
  - Historical patterns for lifecycle-audit: 4,000 tokens
  - Sample outputs: 3,000 tokens

Total used: ~21,500 tokens (23% of budget)
Remaining: ~72,500 tokens for execution output
```

## File Locations Summary

| Component | File | Purpose |
|-----------|------|---------|
| CLI Entry | `./mh1` | Main executable, menu system |
| CLI pip stub | `src/mh1_copilot/cli.py` | Downloads full system |
| Client Selector | `lib/client_selector.py` | Client CRUD, persistence |
| Legacy Planner | `lib/copilot_planner.py` | User-approved planning |
| New Planner | `lib/planner.py` | .plan.md generation |
| Context Orchestrator | `lib/context_orchestrator.py` | 3-level context loading |
| Intelligence Bridge | `lib/intelligence_bridge.py` | Learning interface |
| Intelligence Core | `lib/intelligence.py` | SQLite market data |
| Firebase Client | `lib/firebase_client.py` | Firestore operations |
| Context Sync | `lib/context_sync.py` | Local ↔ Firebase sync |
| Workflow State | `lib/workflow_state.py` | 7-phase tracking |
| Command Router | `lib/command_router.py` | Command → Skill mapping |
| Clarifier | `lib/clarifier.py` | Clarification questions |
| Interaction Store | `lib/interaction_store.py` | Session logging |
| Improvement Engine | `lib/improvement_engine.py` | Feedback processing |
| Runner | `lib/runner.py` | Skill/workflow execution |

## Testing Checklist

```bash
# Basic CLI commands
./mh1 status          # Should show client status
./mh1 connections     # Should show platform status
./mh1 help            # Should show help screen
./mh1 sync --status   # Should show sync status (may have errors)

# Interactive mode
./mh1                 # Should show welcome menu
# Select option 1 → Should list clients
# Select option 2 → Should start client wizard

# With client selected
./mh1                 # Client menu should appear
# Option 1 → Should prompt for natural language
# Option 2 → Should show plans menu
# Option 3 → Should browse skills
```
