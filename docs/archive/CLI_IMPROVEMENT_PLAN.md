# MH1 CLI Improvement Plan

## Status: Phase 3 Complete ✅

**Last Updated:** 2026-01-29

### Sprint 1: Foundation Fixes ✅
- ✅ Fixed Firebase `db` attribute error in `lib/context_sync.py`
- ✅ Fixed interaction logging path error in `lib/interaction_store.py`
- ✅ Added argparse CLI argument parsing with `--help`, `--version` flags
- ✅ Added `--client` flag for pre-selecting client
- ✅ Added `--non-interactive` flag for scripting
- ✅ Created comprehensive architecture documentation in `docs/CLI_ARCHITECTURE.md`

### Sprint 3: Packaging for Distribution ✅
- ✅ Updated `pyproject.toml` with complete dependencies and optional extras
- ✅ Improved `src/mh1_copilot/cli.py` bootstrap with better UX
  - Added `--check` command for system requirements
  - Added `--init`, `--update`, `--where` commands
  - Progress indicators during installation
  - Better error messages
- ✅ Created `lib/executor.py` - Hybrid execution module
  - Claude Code CLI support (full MCP tools)
  - Anthropic API fallback (headless mode)
  - Auto-detection of available methods
- ✅ Created `INSTALL.md` with comprehensive installation guide

### Remaining Work
- Phase 2: UX improvements (unified menus, progress persistence)
- Phase 4: Shell completion, config files

---

## Executive Summary

After thorough analysis of the MH1 CLI system, this document outlines:
1. Current state and what's working
2. Issues and bugs discovered
3. User experience gaps
4. Comprehensive improvement plan

---

## Current CLI Architecture

```
mh1 (main script)
├── src/mh1_copilot/cli.py    # pip installer stub (clones full repo)
├── lib/
│   ├── client_selector.py     # Client selection/persistence
│   ├── copilot_planner.py     # Legacy planning system
│   ├── planner.py             # New plan generator (Phase 3)
│   ├── context_orchestrator.py # Progressive context loading
│   ├── firebase_client.py     # Firebase integration
│   ├── workflow_state.py      # Phase tracking
│   ├── clarifier.py           # Clarification questions
│   ├── interaction_store.py   # Session logging
│   └── improvement_engine.py  # Feedback processing
└── skills/                    # 65+ available skills
```

---

## What's Currently Working

### 1. Direct Commands
| Command | Status | Description |
|---------|--------|-------------|
| `./mh1 status` | ✅ Working | Shows client workflow phase and pipeline |
| `./mh1 connections` | ✅ Working | Shows platform connection status |
| `./mh1 sync --status` | ⚠️ Partial | Shows sync status (with errors) |
| `./mh1 sync --pull` | ⚠️ Partial | Pull from Firebase |
| `./mh1 sync --push` | ⚠️ Partial | Push to Firebase |
| `./mh1 help` | ✅ Working | Shows help screen |

### 2. Interactive Menu System
| Menu | Status | Description |
|------|--------|-------------|
| Welcome Menu (no client) | ✅ Working | 5 options + help/quit |
| Client Menu (client selected) | ✅ Working | 7 options + switch/back/quit |
| Skills Browser | ✅ Working | Categorized skill listing |
| Agents Browser | ✅ Working | Agent type listing |
| Platform Setup Guides | ✅ Working | HubSpot, Salesforce, Notion, etc. |

### 3. Database Connections
| Platform | Status | Notes |
|----------|--------|-------|
| Firebase | ✅ Connected | Firestore for client data |
| HubSpot MCP | ✅ Configured | Via .mcp.json |
| Notion MCP | ✅ Configured | Via .mcp.json |
| Salesforce | ❌ Not configured | Guide available |
| LinkedIn | ❌ Not configured | Browser fallback exists |
| Twitter | ❌ Not configured | Guide available |

---

## Issues Discovered

### Critical Bugs

1. **Firebase Sync Attribute Error**
   ```
   Error: 'FirebaseClient' object has no attribute 'db'
   ```
   - Location: `lib/context_sync.py` line calling `firebase_client.db`
   - Impact: Context sync partially fails but shows as "synced"

2. **Firebase Logging Path Error**
   ```
   A document must have an even number of path elements
   ```
   - Location: `lib/interaction_store.py`
   - Impact: Non-fatal, but logs every execution

3. **No CLI Argument Parsing**
   - `./mh1 --help` treated as natural language query
   - `./mh1 --version` not recognized
   - No standard CLI conventions

### User Experience Issues

1. **Confusing Navigation**
   - Two different planning systems (legacy + new)
   - Inconsistent menu numbering
   - No breadcrumb indication of where you are

2. **Interactive-Only Features**
   - Many features require TTY
   - Non-interactive mode auto-approves plans
   - No batch/scripting support

3. **Error Handling**
   - Firebase errors shown during normal operation
   - No retry prompts on failure
   - Stack traces shown to end users

4. **Missing Features**
   - No `--version` flag
   - No proper exit codes
   - No shell completion
   - No config file support

---

## Comprehensive Improvement Plan

### Phase 1: Foundation Fixes (Priority: Critical)

#### 1.1 Fix Firebase Client Bug
```python
# In lib/firebase_client.py - ensure db property exists
@property
def db(self):
    """Get Firestore database instance."""
    if self._db is None:
        self._db = self._firestore.client()
    return self._db
```

#### 1.2 Add Proper CLI Argument Parsing
```python
# Add to top of mh1 script
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        prog='mh1',
        description='MH1 - AI-Powered Marketing Copilot'
    )
    parser.add_argument('--version', action='version', version='%(prog)s 0.5.0')
    parser.add_argument('--client', '-c', help='Select client by ID or name')
    parser.add_argument('--non-interactive', '-n', action='store_true',
                        help='Run in non-interactive mode')

    subparsers = parser.add_subparsers(dest='command')

    # Status command
    subparsers.add_parser('status', help='Show current client status')

    # Connections command
    subparsers.add_parser('connections', help='Check platform connections')

    # Sync command
    sync = subparsers.add_parser('sync', help='Sync context with Firebase')
    sync.add_argument('--pull', action='store_true', help='Pull from Firebase only')
    sync.add_argument('--push', action='store_true', help='Push to Firebase only')
    sync.add_argument('--status', action='store_true', help='Show sync status')

    # Run command
    run = subparsers.add_parser('run', help='Run a skill or workflow')
    run.add_argument('skill', help='Skill name to run')
    run.add_argument('--input', '-i', help='Input file path')

    return parser.parse_args()
```

#### 1.3 Fix Interaction Logging Path
```python
# In lib/interaction_store.py
def _get_interaction_path(self, interaction_id: str) -> str:
    # Ensure proper path structure: collection/document
    return f"interactions/{self.tenant_id}_{interaction_id}"
```

### Phase 2: User Experience Improvements

#### 2.1 Unified Menu System
```
MH1 Copilot v0.5.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

● Client: Swimply (B0bCCLkqvFhK7JCWKNR1)
  Phase: Onboarded | /discover recommended

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Quick Actions:
  [1] Ask (natural language)     [s] Switch client
  [2] Plans                      [c] Connections
  [3] Skills                     [h] Help
  [4] Agents                     [q] Quit
  [5] Refresh data

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
> _
```

#### 2.2 Progress Persistence
- Store workflow progress in `~/.mh1/state.json`
- Resume interrupted workflows
- Track skill execution history

#### 2.3 Better Error Handling
```python
def handle_error(error: Exception, context: str = ""):
    """User-friendly error handling."""
    if isinstance(error, FirebaseError):
        print(f"{C.YELLOW}Firebase connection issue. Working offline.{C.END}")
        logger.debug(f"Firebase error: {error}")
    elif isinstance(error, subprocess.TimeoutExpired):
        print(f"{C.YELLOW}Operation timed out. Try again?{C.END}")
    else:
        print(f"{C.RED}Error: {str(error)[:100]}{C.END}")
        logger.exception(f"Unexpected error in {context}")
```

### Phase 3: Packaging for Distribution

#### 3.1 Restructure for pip Install
```
mh1-copilot/
├── pyproject.toml
├── src/
│   └── mh1_copilot/
│       ├── __init__.py
│       ├── cli.py           # Main CLI entry point
│       ├── core/
│       │   ├── client.py    # Client management
│       │   ├── planner.py   # Plan generation
│       │   ├── runner.py    # Skill execution
│       │   └── firebase.py  # Firebase integration
│       ├── skills/          # Bundled essential skills
│       │   └── ...
│       └── config/
│           └── defaults.yaml
└── tests/
```

#### 3.2 Two Installation Modes

**Option A: Standalone (pip install mh1-copilot)**
- Core CLI functionality
- Essential skills bundled
- Uses Claude API directly (no Claude Code dependency)

**Option B: Full (git clone)**
- Complete skill library
- Development tools
- Claude Code integration

### Phase 4: Claude Integration Options

#### 4.1 Current: Claude Code CLI Dependency
```python
# Current approach - calls claude CLI
result = subprocess.run(
    ['claude', '-p', prompt, '--output-format', 'text'],
    capture_output=True
)
```
- Pros: Leverages full Claude Code capabilities
- Cons: Requires Claude Code installed, not headless-friendly

#### 4.2 Alternative: Anthropic API Direct
```python
# Direct API approach
from anthropic import Anthropic

client = Anthropic()
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    messages=[{"role": "user", "content": prompt}]
)
```
- Pros: Truly headless, no CLI dependency
- Cons: Loses MCP integrations, tool use requires manual setup

#### 4.3 Recommended Hybrid Approach
```python
def execute_with_claude(prompt: str, use_tools: bool = False):
    """Execute with Claude, preferring Code CLI if available."""

    # Try Claude Code first (for tool use)
    if use_tools and shutil.which('claude'):
        return _execute_claude_code(prompt)

    # Fall back to direct API
    return _execute_anthropic_api(prompt)
```

### Phase 5: Feature Additions

#### 5.1 Configuration File Support
```yaml
# ~/.mh1/config.yaml
default_client: swimply
model:
  default: claude-sonnet-4
  extraction: claude-haiku
firebase:
  project_id: ${FIREBASE_PROJECT_ID}
mcp_servers:
  hubspot: true
  notion: true
```

#### 5.2 Shell Completion
```bash
# Generate completions
mh1 completion bash > ~/.mh1/completions.bash
source ~/.mh1/completions.bash
```

#### 5.3 Skill Execution Progress
```
Running: lifecycle-audit

[1/4] Extract HubSpot contacts...     ✓ 1,234 contacts (2.3s)
[2/4] Analyze engagement patterns...   ⟳ Processing... (15s)
[3/4] Identify lifecycle stages...     ○ Pending
[4/4] Generate report...               ○ Pending

Estimated remaining: ~45 seconds
```

---

## Implementation Priority

### Sprint 1 (Week 1-2): Foundation ✅ COMPLETE
- [x] Fix Firebase client `db` attribute bug
- [x] Fix interaction logging path
- [x] Add argparse CLI parsing
- [x] Add --version and --help flags
- [x] Add --client flag for client selection
- [x] Add --non-interactive flag for scripting
- [ ] Better error handling (partial - basic improvement)

### Sprint 2 (Week 3-4): UX
- [ ] Unified menu system
- [ ] Progress persistence
- [ ] Offline mode graceful degradation
- [ ] Execution progress display

### Sprint 3 (Week 5-6): Packaging ✅ COMPLETE
- [x] Updated pyproject.toml with proper dependencies and optional extras
- [x] Improved cli.py bootstrap with system checks and progress indicators
- [x] Create standalone mode with API fallback (lib/executor.py)
- [x] Write installation docs (INSTALL.md)
- [ ] Bundle essential skills (deferred - download approach works well)

### Sprint 4 (Week 7-8): Polish
- [ ] Shell completion
- [ ] Config file support
- [ ] Performance optimization
- [ ] End-to-end testing

---

## Testing the Current CLI

### Quick Test Commands
```bash
# Test basic functionality
./mh1 status          # Should show client status
./mh1 connections     # Should show platform connections
./mh1 help            # Should show help screen

# Test sync (may have errors)
./mh1 sync --status   # Shows sync status

# Interactive mode
./mh1                 # Enters interactive menu
```

### Expected Issues
1. Firebase sync will show "db attribute" errors
2. `--help` and `--version` won't work as flags
3. Plan execution may log Firebase path errors

---

## Architecture for Headless/API Mode

For users who want to run MH1 without Claude Code:

```
┌─────────────────────────────────────────────────────────────┐
│                       MH1 CLI                                │
├─────────────────────────────────────────────────────────────┤
│  Command Parser (argparse)                                   │
│     ↓                                                        │
│  Client Selector → Firebase (optional)                       │
│     ↓                                                        │
│  Plan Generator                                              │
│     ↓                                                        │
│  Execution Engine                                            │
│     ├─→ Claude Code CLI (if available + tools needed)        │
│     └─→ Anthropic API (fallback / headless)                  │
│           └─→ Tool calls handled manually                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary

The MH1 CLI has solid foundations but needs:
1. **Bug fixes** for Firebase integration
2. **Standard CLI conventions** (argparse, --help, --version)
3. **Better packaging** for pip install distribution
4. **Dual execution mode** (Claude Code + API fallback)

With these improvements, MH1 can be:
- Downloaded via `pip install mh1-copilot`
- Run immediately with `mh1` command
- Work in both interactive and headless modes
- Function with or without Claude Code installed
