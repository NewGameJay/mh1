# MH1 True User Flow

**The Marketer's Journey**

This document describes what a non-technical marketer should experience when using MH1. This is the north star for implementation.

---

## Priority Order

| Priority | Focus | Notes |
|----------|-------|-------|
| **P1** | Working | Bug-free, functional, smooth |
| **P2** | Accuracy | Correct outputs, proper context |
| **P3** | Quality | Memory/learning system MUST work |
| **P4** | Speed | Fast execution |
| **P5** | Scale | Multi-client, team features |

---

## The Marketer's Workflow

### Phase 1: Client Setup

1. **Marketer creates a company/client** and triggers onboarding
2. **Marketer adds necessary info** about the client (industry, platforms, goals, etc.)
3. **System automatically runs deep discovery** for that brand:
   - Who they are
   - What they're doing/selling
   - Their positioning
   - Their goals
4. **Reports are stored locally** for context
5. **All data/details/findings stored in Firebase + memory system** organized by the intelligence/learning system

### Phase 2: Session Start (Returning)

6. **If client already exists**, context is pulled from Firebase
7. Context is **temporarily held and referenced** for the session

### Phase 3: Task Request

8. **Marketer asks for what they want to do OR uploads an MRD:**

   **Option A: Describe the task**
   - "Run a lifecycle audit"
   - "Generate emails for our Q2 campaign"
   - "Create a GTM plan for the new product"
   - "Map the lifecycle for this new offering"

   **Option B: Upload existing MRD**
   - Marketer uploads a pre-made MRD (PDF, HTML, DOCX)
   - System parses and validates the MRD
   - If MRD has sufficient detail, skips MRD generation (Step 14)
   - Orchestrator verifies MRD completeness before proceeding

### Phase 4: Understanding Confirmation

9. **AI parses and understands** the request
10. **AI repeats back** how it's interpreting the ask and expected results (shortened format)
11. **Marketer confirms (y/n):**
    - **No** → Loop back, clarify, re-interpret
    - **Yes** → Begin planning process

### Phase 5: Planning Process

12. **AI calls orchestrator agent** to create a new module under `modules/` using template

13. **Orchestrator scans context:**
    - Client/company reports
    - History
    - Context engineering data

14. **AI generates MRD** (Marketing Requirements Document) OR validates uploaded MRD:

    **If no MRD uploaded:**
    - AI generates MRD from task description
    - Guides overall setup
    - Defines process
    - Specifies expected outputs

    **If MRD uploaded:**
    - AI parses uploaded file (PDF/HTML/DOCX)
    - Validates completeness (goals, scope, outputs defined)
    - If incomplete, AI supplements with missing sections
    - Saves parsed MRD as `MRD.md` in module folder

15. **AI reviews available agents:**
    - AI agents with personas
    - Specialists in marketing verticals
    - Employs them as worker sub-agents of a council

16. **AI Workers + Orchestrator review all Skills:**
    - Read SKILL.md files
    - Understand use cases
    - Review historical outputs

17. **AI Workers reach consensus** and develop `.plan.md`:
    - All relevant skills to be called
    - Goals and KPIs related to MRD
    - Context reviews
    - Final output specifications

18. **AI creates module files:**
    - `MRD.md` - Requirements document
    - `.plan.md` - Execution plan
    - `README.md` - Versioning, goals, outputs, usage, logs

### Phase 6: Review & Approval

19. **AI asks marketer to review and approve** the MRD, plan, etc.
20. **Marketer can:**
    - Make direct changes to files, OR
    - Chat with AI to make updates
21. **When approved**, execution begins

### Phase 7: Execution

22. **AI calls the orchestrator**
23. **Worker AIs execute** per the plan
24. **Skills/docs are processed** according to SKILL.md workflows
25. **Evaluator AI reviews throughout** for quality

### Phase 8: Delivery

26. **AI delivers final outputs:**
    - Stored in Firebase
    - Files saved under `outputs/` folder in module

### Phase 9: Iteration

27. **Marketer repeats process** as needed
28. **Modules saved as templates** with improvements based on experience
29. **Templates productized for sale**

---

## Main Menu Options

What the marketer sees:

```
MH1 Marketing Copilot
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

● Client: {client_name} ({client_id})
  Phase: {phase} | {n} modules

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1] Ask (Natural Language)
    → Speak to Claude naturally about anything

[2] Modules (View/Create)
    → Review past modules, hyperlink to file destinations
    → Create new modules

[3] Run Skills
    → Run skills individually
    → AI team (orchestrator, workers, evaluators) assists

[4] Run Agents
    → Scan lineup of vertical experts
    → Ask them questions directly
    → Use them to run skills

[5] Query Data / Refresh
    → Refresh MCPs and connections
    → Refresh Firebase docs

[6] Client Details
    → Breakdown of everything tied to client
    → Firebase data, memory system data

[7] History
    → Past runs
    → Logs of actions

[s] Switch Client
[h] Health Check
[q] Quit

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Menu Details

### [1] Ask (Natural Language)

The marketer types naturally OR uploads an MRD:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
What would you like to do?

[Type] Describe your task in natural language
[u]    Upload an MRD (PDF, HTML, DOCX)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
>
```

**Natural language examples:**
- "I want to run a lifecycle audit"
- "Help me understand our churn risk"
- "What content should we create for Q2?"

**Upload flow:**
- Marketer presses `u` to upload
- Selects file (PDF, HTML, DOCX)
- AI parses and validates the MRD
- If valid, proceeds directly to planning with uploaded MRD

AI responds conversationally, clarifies, confirms understanding.

### [2] Modules (View/Create)

```
Modules Menu
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Active Modules:
  [1] lifecycle-audit-20260129 (RUNNING)
      → modules/lifecycle-audit-20260129/

  [2] content-calendar-20260128 (COMPLETED)
      → modules/content-calendar-20260128/

Recent Completed:
  [3] gtm-plan-20260115 (COMPLETED)
  [4] email-sequences-20260110 (COMPLETED)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[n] Create New Module
[t] Browse Templates
[b] Back
```

### [3] Run Skills

```
Run Skills
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Available Skills (65 total):

Lifecycle & Analytics:
  [1] lifecycle-audit
  [2] cohort-retention-analysis
  [3] churn-prediction
  [4] at-risk-detection

Content Production:
  [5] email-copy-generator
  [6] ghostwrite-content
  [7] newsletter-builder

Research:
  [8] competitive-intel
  [9] social-listening-collect

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Select skill or describe what you need:
>

AI team will assist with execution.
```

### [4] Run Agents

```
Agent Council
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your Team of Experts:

Orchestrators:
  [O1] Chief Marketing Strategist
       Coordinates campaigns, plans modules

Workers:
  [W1] Lifecycle Specialist
       Customer journey, retention, churn

  [W2] Content Strategist
       Copy, messaging, brand voice

  [W3] Growth Engineer
       GTM, acquisition, conversion

  [W4] Analytics Expert
       Data analysis, reporting, insights

Evaluators:
  [E1] Quality Reviewer
       Checks accuracy, completeness

  [E2] Brand Guardian
       Ensures voice consistency

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[a] Ask an agent directly
[r] Run agents on a skill
[b] Back
```

### [5] Query Data / Refresh

```
Data & Connections
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MCP Connections:
  ✓ HubSpot - Connected (last sync: 5m ago)
  ✓ Firebase - Connected
  ✓ Snowflake - Connected
  ○ Notion - Not configured

Firebase Collections:
  clients/{client_id}/
  modules/{client_id}/
  memory/{client_id}/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[r] Refresh all connections
[f] Query Firebase
[m] Query memory system
[b] Back
```

### [6] Client Details

```
Client: Swimply
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ID: cli_B0bCCLkqvFhK7JCWKNR1
Created: 2026-01-15
Status: Active

Configuration:
  Industry: Marketplace / Consumer
  CRM: HubSpot
  Warehouse: Snowflake

Context:
  Brand Voice: ✓ Defined (voice_contract.md)
  Personas: 3 defined
  Competitors: 5 tracked

Memory:
  Episodic Events: 47
  Semantic Concepts: 23
  Procedural Patterns: 8

Modules:
  Total: 12
  Completed: 10
  Running: 1
  Failed: 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[e] Edit client config
[v] View voice contract
[m] View memory details
[b] Back
```

### [7] History

```
History
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Recent Activity:

2026-01-29 14:23
  Module: lifecycle-audit-20260129
  Status: COMPLETED
  Skills: 4/4 passed
  Duration: 2m 34s

2026-01-28 09:15
  Module: content-calendar-20260128
  Status: COMPLETED
  Skills: 3/3 passed
  Duration: 1m 12s

2026-01-27 16:45
  Skill: competitive-intel (standalone)
  Status: SUCCESS
  Duration: 45s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[f] Filter by date
[s] Filter by status
[l] View logs
[b] Back
```

---

## Key Principles

### For the Non-Technical Marketer

1. **No code required** - Everything through natural language or simple menus
2. **AI does the heavy lifting** - Planning, skill selection, execution
3. **Transparency** - Always shows what AI understands and plans to do
4. **Control** - Marketer approves before execution
5. **Iteration** - Easy to refine, re-run, improve

### For the System

1. **Context is everything** - Memory system, Firebase, client data all available
2. **SKILL.md is the interface** - Agents read and follow skill definitions
3. **Agent Council model** - Orchestrator, workers, evaluators collaborate
4. **Learn and improve** - Templates saved, patterns extracted, memory consolidated

---

## Critical Success Factors

| Factor | Requirement |
|--------|-------------|
| **Smooth** | No crashes, no confusing errors |
| **Bug-free** | Every path works as expected |
| **Valuable** | Outputs are genuinely useful |
| **Context-aware** | AI knows the client, history, goals |
| **Learning** | System gets better with use |

---

## Implementation Checklist

### P1: Working (Must Have)

- [ ] Client creation and onboarding works
- [ ] Deep discovery runs and stores results
- [ ] Context loads for returning sessions
- [ ] Natural language task input works
- [ ] MRD upload option works (PDF, HTML, DOCX)
- [ ] AI confirms understanding (y/n loop)
- [ ] Module creation works
- [ ] MRD generation OR validation of uploaded MRD works
- [ ] Plan generation works
- [ ] Approval flow works
- [ ] Execution runs all skills
- [ ] Outputs delivered to Firebase + files
- [ ] All 7 menu options functional

### P2: Accuracy

- [ ] AI correctly interprets tasks
- [ ] Skills selected match the need
- [ ] Outputs are factually correct
- [ ] Context used appropriately

### P3: Quality

- [ ] Memory system stores and retrieves correctly
- [ ] Learning improves over time
- [ ] Evaluators catch quality issues
- [ ] Templates capture successful patterns

### P4: Speed

- [ ] Execution completes in reasonable time
- [ ] No unnecessary delays
- [ ] Parallel where possible

### P5: Scale

- [ ] Multiple clients work
- [ ] Team features (future)
- [ ] Template marketplace (future)

---

*This document defines what the marketer should experience. All implementation should serve this vision.*
