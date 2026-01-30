# MH1 CLI Implementation Plan

**Date:** 2026-01-30
**Target:** AI-first CLI with Rich TUI

---

## Phase 1: Core Shell

### 1.1 Entry Point (`mh1`)
- [x] Shebang and imports
- [x] Rich console setup
- [x] Main loop structure
- [x] Menu rendering
- [x] Input handling
- [x] Graceful exit

### 1.2 Display Module (`lib/cli/display.py`)
- [x] `render_header()` - MH1 branding
- [x] `render_client_context()` - Current client sidebar
- [x] `render_menu()` - Main menu bar
- [x] `render_chat()` - Conversation window
- [x] `render_submenu()` - Nested menu options
- [x] `render_progress()` - Skill execution progress
- [x] `render_skill_list()` - Skill catalog display
- [x] `render_agent_list()` - Agent roster display

### 1.3 State Module (`lib/cli/state.py`)
- [x] `SessionState` dataclass
- [x] Current client tracking
- [x] Chat history buffer
- [x] Mode tracking (chat/menu/executing)
- [x] Save/load session state

---

## Phase 2: Menu System

### 2.1 Main Menu Actions
Each menu option routes to Claude with specific context:

| Key | Action | Claude Prompt |
|-----|--------|---------------|
| 1 | Ask | "User wants to chat: {input}" |
| 2 | Modules | "User wants to view/create modules" |
| 3 | Skills | "User wants to browse/run skills" |
| 4 | Agents | "User wants to interact with agents" |
| 5 | Data | "User wants to query data or refresh connections" |
| 6 | Client | "User wants to view client details" |
| 7 | History | "User wants to see past runs" |
| s | Switch | "User wants to switch clients" |
| h | Health | "User wants system health check" |
| q | Quit | Exit gracefully |

### 2.2 Sub-menus
All sub-menus render options, then pass selection to Claude.

---

## Phase 3: Claude Integration

### 3.1 Tool Definitions
Claude needs these tools exposed:

```python
# Context loading
load_client_context(client_id: str) -> ClientContext
list_clients() -> List[ClientSummary]
switch_client(client_id: str) -> bool

# Skills
list_skills(category: Optional[str] = None) -> List[SkillSummary]
get_skill(skill_name: str) -> SkillDefinition
run_skill(skill_name: str, inputs: Dict) -> SkillResult

# Agents
list_agents(type: Optional[str] = None) -> List[AgentSummary]
get_agent(agent_name: str) -> AgentDefinition
talk_to_agent(agent_name: str, message: str) -> AgentResponse

# Modules
list_modules() -> List[ModuleSummary]
create_module(name: str, goal: str) -> ModulePath
get_module(module_path: str) -> ModuleDetails

# Data
query_crm(query: str) -> QueryResult
query_warehouse(query: str) -> QueryResult
refresh_connections() -> ConnectionStatus

# Firebase
get_firebase_doc(collection: str, doc_id: str) -> Dict
query_firebase(collection: str, filters: List) -> List[Dict]
set_firebase_doc(collection: str, doc_id: str, data: Dict) -> bool

# Evaluation
evaluate_output(output: Any, schema: Optional[str] = None) -> EvaluationResult

# Telemetry
get_recent_runs(limit: int = 20) -> List[RunSummary]
get_run_details(run_id: str) -> RunDetails
get_cost_summary(period: str = "week") -> CostSummary
```

### 3.2 Claude Session Setup
When CLI starts:
1. Load CLAUDE.md for system context
2. Load current client context (if exists)
3. Set tool definitions
4. Begin conversation loop

---

## Phase 4: Implementation Files

### File 1: `mh1` (Entry Point)
```
~200 lines
- argparse for --client flag
- Rich Live display
- Main event loop
- Menu key handling
- Claude message routing
```

### File 2: `lib/cli/__init__.py`
```
Exports:
- SessionState
- Display functions
- Input handlers
```

### File 3: `lib/cli/display.py`
```
~150 lines
- All render_* functions
- Rich Panel/Table/Layout usage
- Color scheme constants
```

### File 4: `lib/cli/state.py`
```
~80 lines
- SessionState dataclass
- Load/save to .mh1/session.json
- Chat history management
```

---

## Phase 5: Testing

### Manual Test Scenarios

1. **Fresh start (no client)**
   - CLI prompts to create or select client
   - Onboarding flow works

2. **Returning with client**
   - Context loads automatically
   - Chat resumes seamlessly

3. **Natural language task**
   - "Run a lifecycle audit"
   - Claude interprets, confirms, executes

4. **Menu navigation**
   - All menus render correctly
   - Sub-menus work
   - Back navigation works

5. **Skill execution**
   - Progress displays
   - Results render
   - Errors handled gracefully

6. **Client switch**
   - Context swaps cleanly
   - No state bleed

---

## Success Criteria

- [ ] CLI starts in < 2 seconds
- [ ] All menu options accessible
- [ ] Claude responds to natural language
- [ ] Skills execute with progress
- [ ] Client context persists across sessions
- [ ] Errors display gracefully (no stack traces)
- [ ] Quit works cleanly

---

## Dependencies to Install

```bash
pip install rich prompt-toolkit
```

---

## Let's Build It

Starting with the core files in order:
1. `lib/cli/__init__.py`
2. `lib/cli/state.py`
3. `lib/cli/display.py`
4. `mh1` (entry point)
