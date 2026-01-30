# CLI Testing Issues & Required Fixes

**Date:** 2026-01-30
**Tester:** Manual CLI walkthrough
**Status:** IN PROGRESS

---

## Summary

The CLI has critical issues where the main "Ask" flow completely bypasses the module system, MRD generation, agent council, and SKILL.md consultation. It runs scripts directly instead of following the documented flow.

---

## Correct Flow (from TRUE_USER_FLOW.md)

### Phase 4: Understanding Confirmation (MISSING)
```
9.  AI parses and understands the request
10. AI repeats back how it's interpreting the ask (shortened format)
11. Marketer confirms (y/n):
    - No → Loop back, clarify, re-interpret
    - Yes → Begin planning process
```

### Phase 5: Planning Process (MISSING)
```
12. AI calls orchestrator agent to create new module under modules/
13. Orchestrator scans context: client reports, history, context engineering data
14. AI generates MRD (Marketing Requirements Document):
    - Guides overall setup
    - Defines process
    - Specifies expected outputs
15. AI reviews available agents:
    - AI agents with personas
    - Specialists in marketing verticals
    - Employs them as worker sub-agents of a council
16. AI Workers + Orchestrator review all Skills:
    - Read SKILL.md files
    - Understand use cases
    - Review historical outputs
17. AI Workers reach consensus and develop .plan.md:
    - All relevant skills to be called
    - Goals and KPIs related to MRD
    - Context reviews
    - Final output specifications
18. AI creates module files:
    - MRD.md - Requirements document
    - .plan.md - Execution plan
    - README.md - Versioning, goals, outputs, usage, logs
```

### Phase 6: Review & Approval (PARTIALLY WORKING)
```
19. AI asks marketer to review and approve the MRD, plan, etc.
20. Marketer can:
    - Make direct changes to files, OR
    - Chat with AI to make updates
21. When approved, execution begins
```

### Phase 7: Execution (BROKEN)
```
22. AI calls the orchestrator
23. Worker AIs execute per the plan
24. Skills/docs are processed according to SKILL.md workflows
25. Evaluator AI reviews throughout for quality
```

### Phase 8: Delivery (BROKEN)
```
26. AI delivers final outputs:
    - Stored in Firebase
    - Files saved under outputs/ folder in module
```

---

## Issues Found

### Initial Screen (No Client Selected)

| Option | Status | Notes |
|--------|--------|-------|
| [1] Continue (Select Client) | ✅ Works | Shows client list correctly |
| [2] Create New Client | ⚠️ Partial | Works but no AI - see below |
| [3] Browse Skills | 🔄 PENDING | |
| [4] Browse Agents | 🔄 PENDING | |
| [5] Chat Mode | 🔄 PENDING | |
| [c] Connections | 🔄 PENDING | |
| [h] Help | 🔄 PENDING | |

---

### Option [2] Create New Client - PARTIAL SUCCESS

**What Works:**
- Form collects: Company name, Website, Industry, Founder details (Name, Role, LinkedIn, Twitter)
- Creates client directory at `/clients/{client-id}/`
- Sets active client correctly after creation
- Shows updated menu

**What's Missing/Broken:**
| Issue | Type | Description |
|-------|------|-------------|
| No AI Research | ❌ Critical | Says "Running research-company" but no bright-crawler agent |
| No Founder Research | ❌ Critical | LinkedIn URL collected but not actually browsed |
| No Website Analysis | ❌ Critical | Website URL not analyzed for brand voice |
| Scripts Only | ❌ Critical | Just running Python scripts, not agents |
| Empty Client Profile | ⚠️ Warning | Client created but context is empty |

**Test Data Used:**
- Company: Lester Tester
- Website: lestertest.com
- Industry: cyber security research
- Founder: Josh Flores, CEO
- LinkedIn: https://www.linkedin.com/in/joshua-flores-063660174/

**What Should Happen:**
1. AI crawls website to extract brand voice
2. AI browses LinkedIn to research founders
3. AI generates client profile with insights
4. Client context populated for future queries
5. Onboarding recommendations provided

---

### Code Analysis: Create New Client Flow Failure

#### Root Cause: `run_auto_discovery()` in `mh1` (lines 623-688)

**What happens:**
```python
def run_auto_discovery(client_id: str, components: Dict):
    """Run auto-discovery for a client using the discovery onboarding skill."""
    discovery = DiscoveryOnboarding()
    plan = discovery.create_discovery_plan(client_id)

    for step in plan.steps:
        # Just shells out to claude CLI
        result = subprocess.run(
            ['claude', '-p', prompt, '--output-format', 'text'],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=WORKSPACE
        )
```

**Problems:**
- Uses `subprocess.run()` to call Claude CLI with just a text prompt
- Prompt is just `"Run skill: skills/{step.skill_name}/SKILL.md"` with inputs as JSON
- NO Firecrawl MCP invocation for website scraping
- NO browser automation for LinkedIn research
- NO agent involvement whatsoever
- Output is captured but NEVER saved to client context

---

#### Deviation 1: Hardcoded Discovery Steps

**File:** `lib/copilot_planner.py` - `DiscoveryOnboarding.create_discovery_plan()` (lines 1066-1153)

**What happens:**
```python
def create_discovery_plan(self, client_id: str) -> DiscoveryPlan:
    """Create a discovery plan for a new client."""
    steps = [
        DiscoveryStep(
            skill_name="research-company",
            inputs={"company_name": client_data.get("company_name"), ...},
            description="Research company background",
        ),
        # More hardcoded steps...
    ]
    return DiscoveryPlan(client_id=client_id, steps=steps)
```

**Problems:**
- Hardcoded skill sequence, not AI-selected
- No reading of SKILL.md files to understand requirements
- No agent council to decide what research is needed
- Returns simple list of steps without dependencies or conditions

---

#### Deviation 2: SKILL.md Requirements Ignored

**File:** `skills/research-company/SKILL.md`

**SKILL.md defines proper requirements:**
```yaml
inputs:
  company_name:
    type: string
    required: true
  company_url:
    type: url
    required: true

mcp_tools:
  firecrawl:
    - firecrawl_scrape
    - firecrawl_map
```

**But execution in `mh1` just does:**
```python
prompt = f"Run skill: skills/{step.skill_name}/SKILL.md\nInputs: {json.dumps(step.inputs)}"
result = subprocess.run(['claude', '-p', prompt, ...])
```

**Problems:**
- Claude CLI called without MCP tools configured
- No Firecrawl server connection passed
- No browser automation fallback
- Skill's 4-stage workflow (setup → extract → transform → output) ignored

---

#### Deviation 3: No Client Context Saved

**What should happen after research:**
1. Firecrawl scrapes website
2. Browser automation reads LinkedIn
3. AI extracts insights (brand voice, positioning, competitors)
4. Results saved to `clients/{client_id}/context/` files
5. Context available for future queries

**What actually happens:**
1. subprocess.run() executes
2. stdout captured but not parsed
3. Nothing written to client context
4. Client profile remains empty (0 tokens)

---

#### Code Location Summary: Create New Client

| File | Function/Class | Line | Issue |
|------|----------------|------|-------|
| `mh1` | `run_auto_discovery()` | 623-688 | subprocess.run() only, no MCP/agents |
| `lib/copilot_planner.py` | `DiscoveryOnboarding.create_discovery_plan()` | 1066-1153 | Hardcoded steps |
| `lib/copilot_planner.py` | `DiscoveryStep` class | 1020-1040 | No dependency/condition support |
| `skills/research-company/SKILL.md` | - | - | Requires Firecrawl, not invoked |

---

### WHY Scripts Actually Fail: MCP Tools Not Connected

**Root Cause:** `subprocess.run(['claude', '-p', ...])` spawns a fresh Claude CLI process **without MCP servers connected**.

**Available MCP Servers (from `.mcp.json` - 13 total):**
```
firecrawl    - Web scraping (PRIMARY)
brightdata   - Proxy scraping / Crustdata equivalent (FALLBACK 1)
perplexity   - Web research API (FALLBACK 2)
browser      - Puppeteer automation (FALLBACK 3)
firebase-mcp - Client data storage
hubspot      - CRM data
snowflake    - Data warehouse
+ 6 more (airtable, notion, n8n, filesystem, parallel-search, parallel-task)
```

**The skill says:**
```yaml
requires_mcp:
  - firecrawl
optional_mcp:
  - serpapi
```

**But execution does:**
```python
subprocess.run(['claude', '-p', prompt], ...)  # No MCP tools!
```

**Result:** Claude sees "scrape website using Firecrawl" but has no Firecrawl tool available → outputs blank/incomplete template.

---

### What Onboarding SHOULD Do (AI-Controlled Workflow)

```
┌────────────────────────────────────────────────────────────┐
│           ONBOARDING RESEARCH CHAIN (AI-Controlled)        │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1. WEBSITE RESEARCH                                       │
│     ├─ TRY: Firecrawl MCP (primary)                        │
│     ├─ FALLBACK 1: BrightData MCP (paid, ~99% success)     │
│     ├─ FALLBACK 2: Browser/Puppeteer MCP                   │
│     └─ FALLBACK 3: Perplexity MCP (general web research)   │
│                                                            │
│  2. LINKEDIN RESEARCH (Founder)                            │
│     ├─ TRY: BrightData/Crustdata (LinkedIn scraping)       │
│     ├─ FALLBACK 1: Browser automation with rate limiting   │
│     └─ FALLBACK 2: Perplexity (public info search)         │
│                                                            │
│  3. SYNTHESIS                                              │
│     ├─ Anthropic Claude (primary)                          │
│     └─ OpenAI GPT-4 (fallback)                             │
│                                                            │
│  4. STORAGE                                                │
│     ├─ Save to clients/{id}/context/                       │
│     └─ Save to Firebase                                    │
│                                                            │
│  RULE: NEVER output blank/incomplete templates!            │
│        Always use fallback chain until data acquired.      │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Implementation Requirements

1. **AI Controls Workflow** - Not hardcoded scripts
   - AI decides which tool to try based on context
   - AI handles failures and selects fallbacks
   - AI validates output before saving

2. **Fallback Chain** - Never fail silently
   ```python
   async def research_website(url):
       # Try Firecrawl
       result = await mcp.firecrawl.scrape(url)
       if result.success: return result

       # Fallback to BrightData
       result = await mcp.brightdata.scrape(url)
       if result.success: return result

       # Fallback to Perplexity
       result = await mcp.perplexity.search(f"company info {url}")
       if result.success: return result

       # Final fallback: general knowledge (NEVER blank)
       return await claude.ask(f"What do you know about {url}?")
   ```

3. **Output Validation** - Before saving
   - Check required fields populated
   - Never save empty templates
   - Flag low-confidence data

4. **MCP Tool Access** - Required for execution
   - Execute within Claude Code session (has MCP tools)
   - OR pass `--mcp-config .mcp.json` to subprocess
   - OR use Anthropic SDK with tool definitions

---

### Main Menu (Client Selected: Swimply)

#### Option [1] Ask (Natural Language) - CRITICAL FAILURE

| Issue | Type | Description |
|-------|------|-------------|
| No Module Creation | ❌ Critical | Bypasses entire module system |
| No MRD Generation | ❌ Critical | No requirements document created |
| No Agent Council | ❌ Critical | Agents don't actually review/plan |
| Fake Agent Names | ❌ Bug | `data-quality-auditor` doesn't exist in agents/ |
| No SKILL.md Consultation | ❌ Critical | Skills run without reading instructions |
| LoadedContext Error | ❌ Bug | `'LoadedContext' object has no attribute 'get'` |
| IntelligenceBridge Error | ❌ Bug | `'IntelligenceBridge' object has no attribute 'consolidate'` |
| Client Context Empty | ❌ Bug | Client profile: 0 tokens |
| Memory Not Loading | ❌ Bug | Historical patterns: 0 patterns |
| No Output Location | ❌ UX | User not told where results are saved |
| Instant "Planning" | ❌ Critical | No AI analysis, just default skill matching |
| Low Confidence | ⚠️ Warning | 30% confidence suggests guessing |

**What Actually Happens:**
1. User types request
2. System instantly generates a "plan" file (no AI)
3. Default skills pulled based on keywords
4. Fake agent names assigned
5. Scripts execute directly
6. Results go... somewhere unknown
7. Returns to menu with no summary

**What Should Happen (per TRUE_USER_FLOW.md):**

**Understanding Phase:**
1. User types request (e.g., "Run a lifecycle audit")
2. AI parses and understands the request
3. AI repeats back interpretation: "I understand you want to analyze customer lifecycle stages to identify churn risks and opportunities..."
4. User confirms (y/n) - if no, loop back and clarify

**Planning Phase:**
5. AI calls orchestrator to create module at `modules/{client}/{module-name}/`
6. Orchestrator scans: client context, history, Firebase data
7. AI generates MRD.md with goals, scope, expected outputs
8. AI reviews agents in `agents/` directory (real agents with personas)
9. AI Workers + Orchestrator read SKILL.md files for relevant skills
10. Workers reach consensus on .plan.md
11. Module files created: MRD.md, .plan.md, README.md

**Approval Phase:**
12. AI shows plan to marketer
13. Marketer can edit files OR chat to adjust
14. Marketer approves → execution begins

**Execution Phase:**
15. Orchestrator coordinates workers
16. Workers execute skills per SKILL.md workflows
17. Evaluator reviews quality throughout
18. Outputs saved to `modules/{id}/outputs/`

**Delivery Phase:**
19. Results stored in Firebase
20. Memory consolidation occurs
21. User shown clear output location and summary

#### Option [1] Ask - Additional Test: "find my brand voice"

| Issue | Type | Description |
|-------|------|-------------|
| Wrong Skill Match | ❌ Critical | "find my brand voice" matched revenue/pipeline skills |
| Skills Returned | ❌ Wrong | pipeline-analysis, deal-velocity, at-risk-detection, upsell-candidates |
| Should Have Found | ✅ Expected | `brand-voice`, `extract-founder-voice` (actual skills in skills/) |
| No AI Reasoning | ❌ Critical | Just keyword matching, no semantic understanding |

**Actual Skills Available (relevant to brand voice):**
- `brand-voice` - Direct match for the request
- `extract-founder-voice` - Related voice extraction

**Log Output:**
```
Parsed intent: task=research, domain=revenue, platform=None
Matched 4 skills: ['pipeline-analysis', 'deal-velocity', 'at-risk-detection', 'upsell-candidates']
```

This proves the planner is doing dumb keyword matching (or broken matching), not AI-powered intent analysis. It parsed "find my brand voice" as domain=revenue which is completely wrong.

---

#### Option [2] Plans (View/Create)

| Issue | Type | Description |
|-------|------|-------------|
| Shows Old Plans | ✅ Works | Lists existing plans |
| "unknown" Plan | ⚠️ Warning | Plan with no name showing |
| No Module Integration | ❌ Critical | Plans ≠ Modules (should be same) |

#### Option [3] Run Skills - PENDING

#### Option [4] Run Agents - PENDING

#### Option [5] Query Data / Refresh - PENDING

#### Option [6] Client Details - PENDING

#### Option [7] History - PENDING

---

## Code Analysis: Deviations from TRUE_USER_FLOW.md

### CRITICAL: The Root Problem

**The planner (`lib/planner.py`) is NOT using AI for planning.** It uses:
1. Keyword matching for intent detection
2. Hardcoded dictionaries for skill sequences
3. Hardcoded agent expertise mappings
4. No reading of SKILL.md files
5. No agent council involvement

**Meanwhile, `lib/agent_council.py` exists and is well-designed but IS NOT BEING CALLED by the planner!**

---

### Deviation 1: Intent Parsing (Phase 4 Missing)

**File:** `lib/planner.py` - `IntentParser` class (lines 519-714)

**What happens:**
```python
def _detect_task_type(self, request: str) -> Optional[str]:
    """Detect task type from keywords."""
    for task_type, keywords in self.TASK_TYPE_KEYWORDS.items():
        if any(kw in request for kw in keywords):
            return task_type
    return None
```

**Problems:**
- Simple keyword matching against predefined lists
- `_detect_domain()` - Same keyword matching
- `_parse_with_claude()` - Only called as fallback when keyword matching fails
- Returns low confidence (0.7) when AI parsing fails

**TRUE FLOW REQUIRES (Steps 9-11):**
- AI parses and understands the request
- AI repeats back interpretation to user
- User confirms y/n - loop back if no

---

### Deviation 2: Skill Matching (No SKILL.md Reading)

**File:** `lib/planner.py` - `SkillMatcher` class (lines 721-939)

**What happens:**
```python
SKILL_SEQUENCES = {
    ("analysis", "lifecycle", "hubspot"): [
        "lifecycle-audit",
        "churn-prediction",
        "at-risk-detection",
    ],
    ...
}

def match(self, intent: ParsedIntent) -> List[SkillStep]:
    key = (intent.task_type, intent.domain, intent.platform)
    if key in self.SKILL_SEQUENCES:
        return self._create_steps(self.SKILL_SEQUENCES[key], intent)
```

**Problems:**
- Hardcoded skill sequences based on (task_type, domain, platform) tuples
- NO reading of SKILL.md files
- NO understanding of skill capabilities
- NO historical pattern review

**TRUE FLOW REQUIRES (Steps 16-17):**
- AI Workers + Orchestrator review all Skills
- Read SKILL.md files
- Understand use cases
- Review historical outputs
- Workers reach consensus on plan

---

### Deviation 3: Agent Assignment (Fake Agents)

**File:** `lib/planner.py` - `AgentMatcher` class (lines 946-1041)

**What happens:**
```python
AGENT_EXPERTISE = {
    "lifecycle-auditor": {
        "skills": ["lifecycle-audit", "churn-prediction", ...],
        ...
    },
    "data-quality-auditor": {
        "skills": ["data-quality-audit", ...],
        ...
    },
}
```

**Problems:**
- Hardcoded agent expertise mapping in code
- Creates agents that DON'T EXIST in agents/ directory
- Example: "data-quality-auditor" appears in output but doesn't exist
- NO loading of actual agent definitions from agents/

**TRUE FLOW REQUIRES (Step 15):**
- AI reviews available agents
- Load actual agents from agents/ directory
- Employ them as worker sub-agents of a council

**IRONY:** `lib/agent_council.py` exists with proper `AgentRegistry` that loads from agents/ but IT'S NOT BEING USED!

---

### Deviation 4: No Module Creation

**File:** `lib/planner.py` - `PlanGenerator.generate()` (lines 1481-1563)

**What happens:**
```python
plan_filename = f"{plan.name}_{plan.plan_id}_{timestamp}.plan.md"
plan_path = MODULES_DIR / client_id / plan_filename
self.plan_writer.write(plan, plan_path)
```

**Problems:**
- Only creates a single .plan.md file
- NO module directory structure created
- NO MRD.md generation
- NO README.md generation

**TRUE FLOW REQUIRES (Steps 12, 14, 18):**
- Create module under modules/ using template
- Generate MRD.md (Marketing Requirements Document)
- Create module files: MRD.md, .plan.md, README.md

---

### Deviation 5: No Understanding Confirmation

**File:** `mh1` - `handle_plan_request()` (lines 2178-2273)

**What happens:**
```python
def handle_plan_request(request: str, client, components: Dict):
    ...
    status.start("Parsing intent and matching skills...")
    plan_path = plan_generator.generate(request, client.client_id)
    status.stop(f"Plan created: {plan_path.name}")
```

**Problems:**
- Jumps straight to plan generation
- NO "AI repeats back interpretation"
- NO y/n confirmation loop
- User sees plan AFTER it's already generated

**TRUE FLOW REQUIRES (Steps 10-11):**
- AI repeats back how it's interpreting the ask
- Marketer confirms (y/n)
- No → Loop back, clarify, re-interpret
- Yes → Begin planning process

---

### Deviation 6: Execution Bypasses Agents

**File:** `mh1` - `execute_plan()` (lines 2307-2449)

**What happens:**
```python
result = subprocess.run(
    ['claude', '-p', prompt, '--output-format', 'text'],
    capture_output=True,
    text=True,
    timeout=300,
    cwd=WORKSPACE
)
```

**Problems:**
- Just shells out to Claude CLI with skill path
- NO orchestrator coordination
- NO worker agent execution
- NO evaluator review
- Agents listed in plan are NEVER actually invoked

**TRUE FLOW REQUIRES (Steps 22-25):**
- AI calls the orchestrator
- Worker AIs execute per the plan
- Skills/docs processed according to SKILL.md workflows
- Evaluator AI reviews throughout for quality

---

### Bug: LoadedContext.get() Missing

**File:** `lib/context_orchestrator.py` - `LoadedContext` class (lines 98-157)

**Error:**
```
'LoadedContext' object has no attribute 'get'
```

**Cause:** `lib/planner.py` line 1500:
```python
client_context = context.get("client", {})
```

But `LoadedContext` is a dataclass, not a dict. Should be:
```python
client_context = context.client
```

---

### The Unused Solution: lib/agent_council.py

**This file has proper implementations but is NOT being called:**

- `AgentRegistry` - Loads agents from agents/ directory
- `AgentCouncil` - Coordinates orchestrators, workers, evaluators
- `CouncilAssignment` - Proper assignment structure
- `ConsensusEngine` - Worker proposals and orchestrator approvals
- `ExecutionPlan` - Phases with dependencies

**Integration point exists but is commented out or not called:**
```python
def create_council_for_module(module: "Module") -> CouncilAssignment:
    # This function exists but is never called from the planner!
```

---

## Code Locations Needing Fixes

| File | Issue | Fix Required |
|------|-------|--------------|
| `mh1:handle_plan_request()` | No understanding confirmation | Add y/n loop before planning |
| `lib/planner.py:IntentParser` | Keyword matching only | Use AI for intent parsing |
| `lib/planner.py:SkillMatcher` | Hardcoded sequences | Read SKILL.md files |
| `lib/planner.py:AgentMatcher` | Fake agent names | Use agent_council.py instead |
| `lib/planner.py:PlanGenerator` | No module creation | Create module directories with MRD |
| `lib/planner.py:line 1500` | LoadedContext.get() bug | Use `context.client` instead |
| `mh1:execute_plan()` | Subprocess only | Use agent council for execution |
| `lib/intelligence_bridge.py` | consolidate() missing | Add consolidate() method |

---

## Testing Progress

- [x] Initial screen navigation
- [x] Client selection
- [x] Option [1] Ask - FAILED
- [x] Option [2] Plans - Partial
- [ ] Option [2] Create New Client (from initial)
- [ ] Option [3] Browse Skills
- [ ] Option [4] Browse Agents
- [ ] Option [5] Chat Mode
- [ ] Option [3] Run Skills (from main)
- [ ] Option [4] Run Agents (from main)
- [ ] Option [5] Query Data
- [ ] Option [6] Client Details
- [ ] Option [7] History
- [ ] [c] Connections
- [ ] [h] Help

---

---

## Option [5] Chat Mode - CRITICAL FAILURE

### Current Implementation: `run_chat_mode()` in `mh1` (lines 939-973)

**What actually happens:**
```python
def run_chat_mode(client=None):
    context = ""
    if client:
        context = f"Current client: {client.display_name} ({client.client_id})\n"

    result = subprocess.run(
        ['claude', '-p', f"{context}User request: {user_input}", '--output-format', 'text'],
        ...
    )
```

**That's it.** Just the client name passed to Claude CLI.

### What's Missing

| Feature | Status | Impact |
|---------|--------|--------|
| Client context loading | ❌ Missing | AI knows nothing about client |
| System prompt/guardrails | ❌ Missing | AI has no instructions |
| Action keyword detection | ❌ Missing | Can't distinguish questions from actions |
| MCP tools | ❌ Missing | Can't query real data |
| Conversation memory | ❌ Missing | Each message is stateless |
| Skill/command awareness | ❌ Missing | Can't trigger workflows |
| Persona integration | ❌ Missing | PersonaBuilder exists but unused |

### The Unused Solution: `lib/persona_builder.py`

**`PersonaBuilder.to_system_prompt()` exists (lines 212-264)** but is NEVER called by chat mode:

```python
def to_system_prompt(self) -> str:
    """Generate system prompt for copilot interactions."""
    sections = []
    sections.append(f"You are the MH1 Copilot for {self.company_name}.")
    # Company context, target audience, POV, differentiators
    # Voice/communication style, domain vocabulary
    sections.append("\n## Behavior")
    sections.append("""
    - When creating a plan, show expected outcomes before execution
    - Ask for approval before running skills
    - Match the founder's voice in all content
    """)
```

### What Chat Mode SHOULD Do

**Simple Questions (Chat):**
1. Load client persona via `PersonaBuilder`
2. Generate system prompt with full context
3. AI answers using loaded context
4. Remember conversation for follow-ups

**Action Requests (Trigger):**
1. Detect action keywords: "run", "create", "analyze", "generate", "audit"
2. Identify target skill/workflow
3. Hand off to planning flow (with understanding confirmation)
4. Return to chat after completion

**Example Flow:**
```
User: "What's Swimply's brand voice?"
→ AI answers from loaded persona (simple chat)

User: "Run a lifecycle audit"
→ AI detects action keyword "run" + "lifecycle audit"
→ Hands off to Ask flow with understanding confirmation
→ Returns results to chat
```

### Code Location Summary: Chat Mode

| File | Function | Line | Issue |
|------|----------|------|-------|
| `mh1` | `run_chat_mode()` | 939-973 | No context, no system prompt, no action detection |
| `lib/persona_builder.py` | `PersonaBuilder.to_system_prompt()` | 212-264 | Exists but never called |
| - | Action keyword detection | - | Doesn't exist |
| - | MCP tool integration | - | Not passed to Claude CLI |

---

## Priority Fixes

### P0 - CRITICAL (System Non-Functional)

1. **Fix subprocess execution to use MCP tools**
   - Current: `subprocess.run(['claude', '-p', ...])` has no tools
   - Fix: Execute in session OR pass `--mcp-config`
   - Affects: ALL skill execution (Ask, Create Client, Run Skills)

2. **Implement AI-controlled workflow with fallback chain**
   - Current: Hardcoded skill sequences, no fallbacks
   - Fix: AI decides tools, handles failures, validates output
   - Rule: NEVER output blank/incomplete templates

3. **Fix Option [1] Ask to use module system**
   - Current: Bypasses modules, MRD, agent council
   - Fix: Integrate `lib/agent_council.py` (already exists)

4. **Fix agent assignment to use real agents**
   - Current: Hardcoded fake agent names in `AGENT_EXPERTISE`
   - Fix: Load from `agents/` directory via `AgentRegistry`

5. **Fix Chat Mode to load context and detect actions**
   - Current: Just client name, no system prompt
   - Fix: Use `PersonaBuilder.to_system_prompt()` + action detection

### P1 - HIGH (Bugs Blocking Features)

6. **Fix LoadedContext.get() error**
   - File: `lib/planner.py:1500`
   - Fix: `context.client` instead of `context.get("client")`

7. **Fix IntelligenceBridge.consolidate() error**
   - File: `lib/intelligence_bridge.py`
   - Fix: Add missing `consolidate()` method

### P2 - MEDIUM (UX Issues)

8. **Show output location to user**
9. **Load client context properly (0 tokens currently)**
10. **Add understanding confirmation loop (y/n)**

### P3 - LOW (Cleanup)

11. **Clean up "unknown" plans**
12. **Remove hardcoded SKILL_SEQUENCES dict**
13. **Remove hardcoded AGENT_EXPERTISE dict**

---

## Complete `mh1` Function Audit

**File:** `/Users/jflo7006/Downloads/Marketerhire/mh1-hq/mh1`
**Total Lines:** 3,533
**Total Functions:** ~50

### Legend

| Status | Meaning |
|--------|---------|
| ✅ OK | Works correctly |
| ⚠️ PARTIAL | Partially works but has issues |
| ❌ BROKEN | Critical failure, doesn't follow TRUE_USER_FLOW |
| 🔧 DISPLAY | Display-only function, no execution |

---

### Utility Functions (Lines 1-200)

| Function | Lines | Status | Notes |
|----------|-------|--------|-------|
| `is_interactive()` | 76-81 | ✅ OK | Checks terminal mode |
| `safe_input()` | 84-91 | ✅ OK | Safe input handling |
| `StatusDisplay` class | 94-136 | ✅ OK | Spinner/status display |
| `clear_screen()` | 139-140 | ✅ OK | Clear terminal |
| `get_copilot_components()` | 143-198 | ⚠️ PARTIAL | Loads correct modules but they aren't used properly downstream |

---

### Platform Setup Functions (Lines 201-621)

| Function | Lines | Status | Notes |
|----------|-------|--------|-------|
| `check_platform_connection()` | 201-230 | ✅ OK | Checks MCP config |
| `guide_platform_setup()` | 233-383 | ✅ OK | Shows setup guides |
| `guide_hubspot_setup()` | 386-410 | ✅ OK | HubSpot setup menu |
| `guide_hubspot_oauth_setup()` | 413-487 | ✅ OK | OAuth setup guide |
| `guide_hubspot_private_app_setup()` | 490-561 | ✅ OK | Private app setup |
| `collect_platform_credentials()` | 564-620 | ✅ OK | Credential collection |

---

### Discovery & Onboarding Functions (Lines 623-757) - CRITICAL FAILURES

| Function | Lines | Status | Issue |
|----------|-------|--------|-------|
| `run_auto_discovery()` | 623-688 | ❌ BROKEN | **Uses `subprocess.run(['claude', '-p', ...])` - No MCP tools, no context, no output saved** |
| `prompt_discovery_inputs()` | 691-757 | ✅ OK | Just collects inputs |

**`run_auto_discovery()` Details:**
```python
# Line 663-668 - THE PROBLEM
result = subprocess.run(
    ['claude', '-p', prompt, '--output-format', 'text'],
    capture_output=True,
    text=True,
    timeout=120,
    cwd=WORKSPACE
)
```
- No `--mcp-config` passed
- No Firecrawl for website scraping
- No BrightData for LinkedIn
- No Perplexity for research
- Output captured but never parsed or saved

---

### Skills & Agents Browser Functions (Lines 764-973) - MIXED

| Function | Lines | Status | Issue |
|----------|-------|--------|-------|
| `get_skill_description()` | 764-782 | ✅ OK | Reads SKILL.md frontmatter |
| `show_skills_browser()` | 785-838 | 🔧 DISPLAY | Display only |
| `show_agents_browser()` | 841-908 | 🔧 DISPLAY | Display only |
| `run_agent_chat()` | 911-936 | ❌ BROKEN | **subprocess.run() - No agent persona loaded, no MCP** |
| `run_chat_mode()` | 939-973 | ❌ BROKEN | **subprocess.run() - No PersonaBuilder, no context, no action detection** |

**`run_agent_chat()` Details (Line 927-932):**
```python
# Just passes a generic prompt, doesn't load actual agent definition
agent_prompt = f"You are the {agent_name} agent. Respond as this specialized agent would."
result = subprocess.run(
    ['claude', '-p', f"{agent_prompt}\n\nUser: {user_input}", '--output-format', 'text'],
    ...
)
```
- Agent files in `agents/` directory are NEVER read
- No persona, no expertise, no tools

**`run_chat_mode()` Details (Line 962-968):**
```python
context = f"Current client: {client.display_name} ({client.client_id})\n"
result = subprocess.run(
    ['claude', '-p', f"{context}User request: {user_input}", '--output-format', 'text'],
    ...
)
```
- No `PersonaBuilder.to_system_prompt()` called
- No client context loaded (brand voice, history, etc.)
- No action keyword detection
- No conversation memory

---

### Client Management Functions (Lines 976-1277)

| Function | Lines | Status | Notes |
|----------|-------|--------|-------|
| `find_similar_clients()` | 976-1025 | ✅ OK | Fuzzy name matching |
| `create_client_directories()` | 1028-1042 | ✅ OK | Creates directory structure |
| `create_client_wizard()` | 1045-1277 | ⚠️ PARTIAL | Saves to Firebase but doesn't run research |

**`create_client_wizard()` Issue:**
- Collects all client info correctly
- Saves to Firebase correctly
- Creates local directories correctly
- BUT: Doesn't trigger auto-discovery research
- Client profile remains empty (no brand voice, no research)

---

### Menu Display Functions (Lines 1280-1509)

| Function | Lines | Status | Notes |
|----------|-------|--------|-------|
| `show_welcome_menu()` | 1280-1293 | 🔧 DISPLAY | Welcome screen |
| `show_client_menu()` | 1296-1389 | 🔧 DISPLAY | Client menu |
| `show_client_details()` | 1392-1424 | 🔧 DISPLAY | Client info |
| `show_copilot_menu()` | 1431-1509 | 🔧 DISPLAY | Legacy menu |

---

### Plan Processing Functions (Lines 1512-1857) - CRITICAL FAILURES

| Function | Lines | Status | Issue |
|----------|-------|--------|-------|
| `process_with_plan()` | 1512-1647 | ❌ BROKEN | **subprocess.run() - No MCP, no agents, no module** |
| `show_status_screen()` | 1650-1700 | 🔧 DISPLAY | Display only |
| `show_help_screen()` | 1703-1758 | 🔧 DISPLAY | Help text |
| `select_or_onboard()` | 1761-1805 | ✅ OK | Selection logic |
| `onboard_new_client()` | 1808-1857 | ❌ BROKEN | **Calls broken `run_auto_discovery()`** |

**`process_with_plan()` Details (Line 1596-1601):**
```python
result = subprocess.run(
    ['claude', '-p', prompt, '--output-format', 'text'],
    capture_output=True,
    text=True,
    timeout=300,
    cwd=WORKSPACE
)
```
- Same subprocess.run() pattern
- No MCP tools
- No agent council
- No module creation
- No MRD generation

---

### Sync Functions (Lines 1860-2045) - OK

| Function | Lines | Status | Notes |
|----------|-------|--------|-------|
| `handle_sync_command()` | 1860-1999 | ✅ OK | Uses proper sync modules |

---

### Module Shortcut Functions (Lines 2052-2167) - PARTIAL

| Function | Lines | Status | Notes |
|----------|-------|--------|-------|
| `handle_module_shortcut_command()` | 2052-2167 | ⚠️ PARTIAL | Creates module structure correctly, but execution still broken |

---

### Plan Generation & Execution (Lines 2178-2449) - CRITICAL FAILURES

| Function | Lines | Status | Issue |
|----------|-------|--------|-------|
| `handle_plan_request()` | 2178-2273 | ❌ BROKEN | **No understanding confirmation, calls broken `execute_plan()`** |
| `show_full_plan()` | 2276-2304 | 🔧 DISPLAY | Display only |
| `execute_plan()` | 2307-2449 | ❌ BROKEN | **subprocess.run() - No MCP, no agents, calls missing `consolidate()`** |

**`handle_plan_request()` Issues:**
1. No "AI repeats back interpretation" step
2. No y/n confirmation loop
3. Uses `plan_generator.generate()` which does keyword matching, not AI
4. Calls `execute_plan()` which is broken

**`execute_plan()` Details (Line 2370-2376):**
```python
result = subprocess.run(
    ['claude', '-p', prompt, '--output-format', 'text'],
    capture_output=True,
    text=True,
    timeout=300,
    cwd=WORKSPACE
)
```
Also calls `intelligence_bridge.consolidate()` at line 2431 which doesn't exist.

---

### Module Management Functions (Lines 2452-2561)

| Function | Lines | Status | Notes |
|----------|-------|--------|-------|
| `show_modules_menu()` | 2452-2459 | ✅ OK | Delegates to cli_menus |
| `_show_modules_menu_legacy()` | 2462-2536 | 🔧 DISPLAY | Legacy display |
| `manage_single_plan()` | 2539-2561 | ⚠️ PARTIAL | Calls broken `execute_plan()` |

---

### Health & History Functions (Lines 2564-2791) - OK

| Function | Lines | Status | Notes |
|----------|-------|--------|-------|
| `show_health_panel()` | 2564-2577 | ✅ OK | Uses health_panel module |
| `handle_history_command()` | 2580-2649 | ✅ OK | Uses history_view module |
| `handle_history_command_parsed()` | 2652-2706 | ✅ OK | Parsed args handler |
| `handle_sync_command_parsed()` | 2709-2727 | ✅ OK | Parsed args handler |
| `handle_logs_command_parsed()` | 2730-2746 | ✅ OK | Parsed args handler |
| `handle_logs_command()` | 2749-2791 | ✅ OK | Uses history_view module |

---

### Run Module Functions (Lines 2794-2904) - PARTIAL

| Function | Lines | Status | Notes |
|----------|-------|--------|-------|
| `handle_run_module_command()` | 2794-2904 | ⚠️ PARTIAL | Uses module_executor, better but may still lack MCP |

---

### Connections & File Handling (Lines 2907-3079) - OK

| Function | Lines | Status | Notes |
|----------|-------|--------|-------|
| `check_connections()` | 2907-2935 | ✅ OK | Shows connection status |
| `handle_file_attachments()` | 2938-3011 | ✅ OK | File validation/attachment |
| `prompt_file_attachment()` | 3014-3060 | ✅ OK | Interactive attachment |
| `show_attached_files()` | 3063-3079 | 🔧 DISPLAY | Display only |

---

### Main Entry Point (Lines 3082-3532)

| Function | Lines | Status | Notes |
|----------|-------|--------|-------|
| `parse_arguments()` | 3082-3228 | ✅ OK | Argparse setup |
| `main()` | 3231-3532 | ⚠️ PARTIAL | Routes to broken functions |

**`main()` Routing Issues:**
- Line 3354: Routes to `process_with_plan()` - BROKEN
- Line 3391: Routes to `select_or_onboard()` → `onboard_new_client()` → `run_auto_discovery()` - BROKEN
- Line 3411: Routes to `run_chat_mode()` - BROKEN
- Line 3479: Routes to `handle_plan_request()` - BROKEN
- Line 3498: Routes to `process_with_plan()` for skills - BROKEN
- Line 3524: Routes to `process_with_plan()` for natural language - BROKEN

---

## Summary: Functions Using Broken `subprocess.run()` Pattern

| Function | Line | Impact |
|----------|------|--------|
| `run_auto_discovery()` | 663 | Client onboarding fails |
| `run_agent_chat()` | 927 | Agent chat has no persona |
| `run_chat_mode()` | 962 | Chat has no context |
| `process_with_plan()` | 1596 | Legacy planning fails |
| `execute_plan()` | 2370 | Plan execution fails |

**All 5 functions do the same thing:**
```python
subprocess.run(
    ['claude', '-p', prompt, '--output-format', 'text'],
    capture_output=True,
    text=True,
    timeout=XXX,
    cwd=WORKSPACE
)
```

**All 5 are missing:**
- `--mcp-config .mcp.json`
- System prompt / PersonaBuilder
- Client context loading
- Agent council coordination
- Output parsing and storage

---

## The Fix: Replace subprocess.run() with Proper Execution

**Option A: Pass MCP config to subprocess**
```python
subprocess.run([
    'claude',
    '--mcp-config', '.mcp.json',  # ADD THIS
    '-p', prompt,
    '--output-format', 'text'
], ...)
```

**Option B: Use Anthropic SDK with tools**
```python
from anthropic import Anthropic
client = Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    system=persona_builder.to_system_prompt(),
    messages=[{"role": "user", "content": prompt}],
    tools=[firecrawl_tools, brightdata_tools, ...]
)
```

**Option C: Execute in-session (recommended)**
- Don't spawn subprocess at all
- Use the current Claude Code session which already has MCP tools
- Call skills via the SDK with tool definitions

---

## Existing Solutions That Are NOT Being Used

| Module | Location | Purpose | Used? |
|--------|----------|---------|-------|
| `AgentCouncil` | `lib/agent_council.py` | Orchestrator/worker coordination | ❌ NO |
| `AgentRegistry` | `lib/agent_council.py` | Load agents from agents/ | ❌ NO |
| `PersonaBuilder` | `lib/persona_builder.py` | System prompts with context | ❌ NO |
| `ContextOrchestrator` | `lib/context_orchestrator.py` | 3-level context loading | ⚠️ PARTIAL |
| MCP Servers (13) | `.mcp.json` | Firecrawl, BrightData, Perplexity... | ❌ NO |

**The irony:** All the right modules exist. They're imported in `get_copilot_components()`. But they're never actually used for execution.
