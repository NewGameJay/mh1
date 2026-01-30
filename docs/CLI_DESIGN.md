# MH1 CLI Design: AI-First Architecture

**Date:** 2026-01-30
**Version:** 2.0.0
**Philosophy:** Claude controls everything. No scripts, no automation. Tools only.

---

## Core Principle

The CLI is a **thin presentation layer**. All logic lives in Claude's tool calls:
- No Python workflow scripts
- No hardcoded routing
- No automated pipelines

Claude reads skills, agents, and context → decides what to do → executes via tools.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         MH1 CLI                                  │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    CHAT WINDOW                           │    │
│  │  User: Run a lifecycle audit for Acme Corp              │    │
│  │  Claude: I'll run the lifecycle-audit skill...          │    │
│  │  [Progress indicators, results, follow-ups]             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    MENU BAR                              │    │
│  │  [1] Ask  [2] Modules  [3] Skills  [4] Agents           │    │
│  │  [5] Data  [6] Client  [7] History  [s] Switch  [q] Quit│    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                 CONTEXT SIDEBAR                          │    │
│  │  Client: Acme Corp                                       │    │
│  │  Industry: SaaS B2B                                      │    │
│  │  CRM: HubSpot | Warehouse: Snowflake                    │    │
│  │  Last Run: lifecycle-audit (2h ago)                     │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CLAUDE (AI Layer)                          │
│  - Reads user input                                             │
│  - Loads context via tools                                      │
│  - Decides which skills/agents to invoke                        │
│  - Executes via MCP tools                                       │
│  - Evaluates outputs                                            │
│  - Returns results to CLI                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        TOOLS LAYER                              │
│  Firebase | HubSpot | Snowflake | Firecrawl | File System      │
│  Skills (66) | Agents (20+) | Evaluators | Context Loader      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Menu Structure

### [1] Ask (Natural Language)
Opens freeform chat. Claude interprets and routes.

**Examples:**
- "Run a lifecycle audit"
- "What's our churn risk?"
- "Generate emails for the Q2 campaign"
- "Create a GTM plan for new product"

**Claude's behavior:**
1. Parse intent
2. Load relevant context (via `context_orchestrator`)
3. Identify skills needed (via skill registry)
4. Assemble agent council if multi-step
5. Execute and stream progress
6. Evaluate output
7. Deliver or request approval

---

### [2] Modules (View/Create)
Modules are project containers for multi-step work.

**Sub-menu:**
```
[2] Modules
    [a] View Active Modules
        → Lists modules/ with status, last updated
        → Select to open in editor or chat about
    [b] Create New Module
        → Claude asks: "What's the goal?"
        → Creates module folder with MRD.md, .plan.md, README.md
    [c] Resume Module
        → Pick from active modules
        → Claude loads context and continues
```

**Module Structure:**
```
modules/{module-name}/
├── MRD.md           # Marketing Requirements Document
├── .plan.md         # Execution plan (skills, agents, steps)
├── README.md        # Versioning, goals, outputs, logs
├── outputs/         # Deliverables
└── artifacts/       # Intermediate data
```

---

### [3] Run Skills
Direct skill execution.

**Sub-menu:**
```
[3] Skills
    [a] Browse Skills
        → Categories: Intelligence, Content, Discovery, Strategy, etc.
        → Select category → see skills with descriptions
    [b] Search Skills
        → "Find skills for churn"
        → Claude matches and suggests
    [c] Run Skill
        → Select skill
        → Claude gathers required inputs
        → Executes with progress
        → Evaluates and delivers
    [d] Skill Info
        → Show full SKILL.md for any skill
```

**Skill Categories (66 skills):**
| Category | Count | Examples |
|----------|-------|----------|
| Customer Intelligence | 8 | account-360, churn-prediction, at-risk-detection |
| Content Creation | 7 | brand-voice, cold-email-personalization, ghostwrite-content |
| Data Discovery | 5 | crm-discovery, data-warehouse-discovery, identity-mapping |
| Campaign Operations | 6 | cohort-email-builder, lead-magnet, newsletter-builder |
| Marketing Strategy | 8 | positioning-angles, gtm-engineering, lifecycle-audit |
| Sales Performance | 4 | sales-rep-performance, qualify-leads, upsell-candidates |
| Data Quality | 4 | data-quality-audit, generate-context-summary |
| SEO & Keywords | 4 | keyword-research, seo-content, dataforseo |
| Research & Intel | 6 | research-company, research-competitors, social-listening |
| Social Media | 3 | twitter-keyword-search, reddit-keyword-search |
| System | 8 | skill-builder, marketing-orchestrator, artifact-manager |

---

### [4] Agents
Direct agent interaction.

**Sub-menu:**
```
[4] Agents
    [a] Meet the Team
        → Shows all agents with specializations
        → Organized: Orchestrators, Workers, Evaluators
    [b] Talk to Agent
        → Select an agent
        → Chat directly with that persona
        → They can run skills in their domain
    [c] Assemble Council
        → Claude recommends team for a task
        → User approves lineup
        → Council executes together
```

**Agent Roster:**
| Type | Agent | Specialization |
|------|-------|----------------|
| Orchestrator | Learning Meta-Agent | Knowledge pipeline |
| Worker | Lifecycle Auditor | CRM lifecycle analysis |
| Worker | Deep Research Agent | Company/market intel |
| Worker | LinkedIn Ghostwriter | Founder voice content |
| Worker | Competitive Intel Analyst | Social listening |
| Worker | Interview Agent | Primary research |
| Evaluator | Fact-Check Agent | Claim verification |
| Evaluator | QA Reviewer | Brand voice validation |

---

### [5] Query Data / Refresh
Data operations.

**Sub-menu:**
```
[5] Data
    [a] Query CRM
        → Natural language: "Find contacts with no activity in 30 days"
        → Claude translates to HubSpot/Salesforce query
    [b] Query Warehouse
        → Natural language: "What's our ARR by cohort?"
        → Claude generates SQL for Snowflake/BigQuery
    [c] Refresh Connections
        → Test and reconnect MCP servers
        → Shows status for each
    [d] Sync Firebase
        → Pull latest client data
        → Update local context
```

---

### [6] Client Details
Everything about the current client.

**Sub-menu:**
```
[6] Client
    [a] Profile Overview
        → Company, industry, platforms, goals
        → Voice contracts, personas
    [b] Firebase Data
        → Browse client's Firebase collections
        → Research reports, historical runs
    [c] Memory System
        → Episodic (past interactions)
        → Semantic (concepts/knowledge)
        → Procedural (learned patterns)
    [d] Configuration
        → Platform connections
        → Thresholds, preferences
    [e] Edit Client
        → Update any client details
        → Claude validates and saves
```

---

### [7] History
Past runs and logs.

**Sub-menu:**
```
[7] History
    [a] Recent Runs
        → Last 20 skill/workflow executions
        → Status, tokens, cost, duration
    [b] Search Runs
        → By skill, date, status
    [c] View Run Details
        → Full execution log
        → Inputs, outputs, evaluations
    [d] Cost Summary
        → By day, week, month
        → By skill type
```

---

### [s] Switch Client
Quick client switch.

```
[s] Switch Client
    → Shows list of configured clients
    → Select to switch
    → Context loads automatically
    → Or: "Create New Client" → triggers onboarding
```

---

### [h] Health Check
System health.

```
[h] Health
    → MCP connections status
    → Firebase connection
    → Budget usage
    → Recent errors
```

---

### [q] Quit
Exit CLI.

---

## User Journey Implementation

### Phase 1: Client Setup (New Client)

**Trigger:** User selects "Create New Client" or `/onboard {client_name}`

**Claude's actions:**
1. Ask for basic info (company name, website, industry)
2. Run `research-company` skill
3. Run `crm-discovery` skill (if CRM connected)
4. Run `data-warehouse-discovery` skill (if warehouse connected)
5. Generate client profile
6. Store in Firebase via tool
7. Create `clients/{client_id}/` folder structure
8. Run `extract-founder-voice` if founder info available
9. Build persona via `persona_builder`
10. Report findings, ask for corrections

**No scripts.** Claude orchestrates all of this by reading skills and calling tools.

---

### Phase 2: Session Start (Returning Client)

**Trigger:** CLI starts or user switches client

**Claude's actions:**
1. Load context from Firebase (via tool)
2. Load client config from `clients/{client_id}/`
3. Check for recent modules in progress
4. Summarize: "Welcome back. Working on Acme Corp. Last session: lifecycle audit module in progress."

---

### Phase 3: Task Request

**Trigger:** User types request or uploads file

**Option A: Natural language**
- User: "Run a lifecycle audit"
- Claude parses, confirms understanding
- User approves → proceed

**Option B: Upload MRD**
- User: "I have an MRD" → drops file
- Claude reads file (PDF/DOCX/MD)
- Validates completeness
- Supplements if needed
- Proceeds with execution

---

### Phase 4: Planning

**Claude's actions:**
1. Create module folder: `modules/{task-name}/`
2. Generate `MRD.md` (or save uploaded)
3. Review available skills (read SKILL.md files)
4. Review available agents (read agent definitions)
5. Assemble council (orchestrator + workers + evaluators)
6. Generate `.plan.md` with:
   - Skills to run in order
   - Agent assignments
   - Expected outputs
   - Evaluation criteria
7. Generate `README.md`
8. Ask user to review and approve

---

### Phase 5: Execution

**Trigger:** User approves plan

**Claude's actions:**
1. Execute skills in order per `.plan.md`
2. Stream progress to chat window
3. Run evaluators after each skill output
4. Handle failures gracefully (retry, skip, or ask user)
5. Save outputs to `modules/{task-name}/outputs/`
6. Store artifacts in Firebase
7. Log telemetry

---

### Phase 6: Delivery

**Claude's actions:**
1. Run final evaluation
2. Check release policy
3. If AUTO_DELIVER: present results
4. If HUMAN_REVIEW: ask for approval
5. If AUTO_REFINE: make fixes and re-evaluate
6. Save final deliverables
7. Update module README with completion status

---

## Implementation Plan

### File Structure

```
mh1-hq/
├── mh1                      # Main CLI entry point (~200 lines)
├── lib/
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── display.py       # Rich terminal display (chat, menus, sidebar)
│   │   ├── input.py         # User input handling
│   │   └── state.py         # Session state (current client, mode)
│   └── ... (existing lib modules)
├── commands/                 # Command docs (for help text)
└── ...
```

### Dependencies

```
rich              # Terminal UI (panels, tables, progress)
prompt_toolkit    # Advanced input handling
```

### Implementation Steps

**Step 1: Create CLI Shell** (mh1)
- Entry point with Rich display
- Chat window + menu bar layout
- Route to Claude for all actions

**Step 2: Create Display Module** (lib/cli/display.py)
- `ChatWindow` class - conversation display
- `MenuBar` class - menu rendering
- `ContextSidebar` class - client info
- `ProgressIndicator` class - skill execution progress

**Step 3: Create Input Module** (lib/cli/input.py)
- Menu navigation
- Natural language input
- File upload handling
- Confirmation prompts

**Step 4: Create State Module** (lib/cli/state.py)
- Current client tracking
- Session history
- Mode tracking (chat, menu, skill execution)

**Step 5: Define Tool Schemas**
Claude needs clear tool definitions for:
- `load_client_context` - Load from Firebase
- `run_skill` - Execute a skill
- `create_module` - Create module folder
- `read_skill` - Read SKILL.md
- `list_skills` - Get skill catalog
- `list_agents` - Get agent roster
- `query_crm` - Natural language CRM query
- `query_warehouse` - Natural language SQL
- `evaluate_output` - Run evaluator
- `save_to_firebase` - Store data

---

## Example Session

```
╭─────────────────────────────────────────────────────────────────╮
│                          MH1 v2.0                                │
╰─────────────────────────────────────────────────────────────────╯

╭─ Client ─────────────────────╮
│ Acme Corp                    │
│ SaaS B2B | HubSpot          │
│ Last: 2h ago                 │
╰──────────────────────────────╯

╭─ Chat ──────────────────────────────────────────────────────────╮
│ > Run a lifecycle audit                                          │
│                                                                  │
│ Claude: I understand you want to run a lifecycle audit for       │
│ Acme Corp. This will:                                           │
│                                                                  │
│ • Analyze customer lifecycle stages in HubSpot                  │
│ • Pull health scores from Snowflake                             │
│ • Identify churn risks and upsell opportunities                 │
│ • Generate recommendations                                       │
│                                                                  │
│ Expected output: Lifecycle Audit Report (MD + JSON)             │
│ Estimated time: 5-10 minutes                                    │
│ Estimated cost: ~$0.50                                          │
│                                                                  │
│ Proceed? [y/n]                                                  │
╰──────────────────────────────────────────────────────────────────╯

╭─ Menu ──────────────────────────────────────────────────────────╮
│ [1] Ask  [2] Modules  [3] Skills  [4] Agents  [5] Data          │
│ [6] Client  [7] History  [s] Switch  [h] Health  [q] Quit       │
╰──────────────────────────────────────────────────────────────────╯

> y

╭─ Chat ──────────────────────────────────────────────────────────╮
│ Claude: Starting lifecycle audit...                              │
│                                                                  │
│ ✓ Created module: modules/lifecycle-audit-2026-01-30/           │
│ ✓ Generated MRD.md                                              │
│ ⠋ Running crm-discovery... (querying HubSpot)                   │
│                                                                  │
╰──────────────────────────────────────────────────────────────────╯
```

---

## Key Design Decisions

1. **No subprocess execution** - Claude calls tools directly, no `subprocess.run()`
2. **No hardcoded skill routing** - Claude reads SKILL.md and decides
3. **No automated pipelines** - Every step is a Claude decision
4. **Tools are the API** - Everything Claude does is via tool calls
5. **State is minimal** - Just current client and session history
6. **Display is dumb** - Only renders what Claude returns

---

## What Claude Needs

For this to work, Claude needs these capabilities in the session:

1. **File system access** - Read/write skills, modules, client configs
2. **Firebase tools** - Get/set documents, query collections
3. **MCP tools** - HubSpot, Snowflake, Firecrawl
4. **Skill execution** - Ability to "run" a skill (which means following its SKILL.md)
5. **Evaluation** - Call evaluator on outputs

The CLI just provides the interface. **Claude is the brain.**
