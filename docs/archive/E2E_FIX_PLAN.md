# E2E Flow Fix Plan (Revised)

**Created:** 2026-01-29
**Revised:** 2026-01-29
**Status:** Ready for Implementation

**Reference:** See `TRUE_USER_FLOW.md` for the complete marketer journey.

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

## Critical Architecture Principle

**SKILL.md is the primary interface, not run.py.**

Agents must:
1. Have full client context (from memory system + Firebase)
2. Have the MRD (module requirements document)
3. Read and follow SKILL.md for workflow, constraints, process
4. Execute according to SKILL.md instructions (which may reference run.py internally)

**Never bypass SKILL.md by calling run.py directly.**

---

## The Complete Flow (per Mermaid diagram)

```
CLI → SelectClient → TaskInput → ParseIntent → CreateModule → GenerateMRD →
                                    ↓
              [Context Engineering: Memory + Firebase + Client Context]
                                    ↓
AgentCouncil → ReviewSkills (reads SKILL.md) → CreatePlan → ReviewPlan →
                                    ↓
              [APPROVE] → SetRunning → Orchestrator → Workers →
                                    ↓
              [Workers read SKILL.md + have client context + MRD]
                                    ↓
              SkillRunner (executes per SKILL.md) → Evaluators →
                                    ↓
              SetCompleted → OutputFiles → UpdateMemory (consolidation)
```

---

## Gap Analysis (Revised)

| Gap | Current State | Required State |
|-----|---------------|----------------|
| **1. `run-module` command missing** | CLI tells user to run non-existent command | Add command that invokes execution flow |
| **2. Execution bypasses SKILL.md** | `skill_runner.py` fallback returns inputs | Route through agent that reads SKILL.md |
| **3. No context injection** | Execution doesn't load client context | Inject memory + MRD + client context |
| **4. Agent Council not invoked** | `start_execution()` creates state only | Actually invoke orchestrator with context |
| **5. Memory not consolidated** | `complete_execution()` is stub | Trigger consolidation on completion |

---

## Implementation Phases

### Phase A: Add `run-module` CLI Command

**File:** `mh1`

**Changes:** Add subcommand that:
1. Loads module
2. Validates status (must be APPROVED or use --approve)
3. Invokes the full execution flow via `lib/module_executor.py`

```bash
./mh1 run-module lifecycle-audit-XXXXX           # Execute approved module
./mh1 run-module lifecycle-audit-XXXXX --approve # Approve then execute
```

---

### Phase B: Create Context-Aware Module Executor

**New File:** `lib/module_executor.py`

**Key Principle:** Agents execute skills with full context, following SKILL.md.

```python
#!/usr/bin/env python3
"""
Module Executor - Context-Aware Skill Execution

Ensures agents have:
1. Client context (from memory layers)
2. MRD (module requirements)
3. SKILL.md (full skill definition)

Never bypasses SKILL.md by calling run.py directly.
"""

from pathlib import Path
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

SYSTEM_ROOT = Path(__file__).parent.parent

def execute_module(module) -> Dict:
    """
    Execute all skills in a module with full context awareness.

    Flow:
    1. Load context (client + memory + MRD)
    2. Start execution (transition to RUNNING)
    3. Invoke Orchestrator Agent with context
    4. Orchestrator routes to Workers per skill_plan
    5. Each Worker reads SKILL.md and executes accordingly
    6. Evaluators validate outputs
    7. Complete execution, trigger memory consolidation
    """
    from lib.agent_council import AgentCouncil, create_council_for_module
    from lib.memory.working import WorkingMemory
    from lib.memory.semantic import SemanticMemory
    from lib.memory.episodic import EpisodicMemory

    # === 1. LOAD CONTEXT ===
    context = build_execution_context(module)
    logger.info(f"Built context for module {module.module_id}")

    # === 2. START EXECUTION ===
    execution = module.start_execution(module.skill_plan)
    logger.info(f"Started execution {execution.run_id}")

    # === 3. INVOKE ORCHESTRATOR ===
    council = create_council_for_module(module)

    orchestrator_prompt = f"""
You are executing module: {module.module_id}

## Client Context
{context['client_context']}

## MRD (Module Requirements)
{context['mrd']}

## Skills to Execute (in order)
{context['skill_plan']}

## Memory Context
{context['memory_context']}

For each skill:
1. Read the full SKILL.md at skills/{{skill_name}}/SKILL.md
2. Follow the workflow defined in SKILL.md
3. Respect constraints, SLAs, and quality criteria
4. Checkpoint after each skill completes
5. Route outputs through evaluators

Begin execution.
"""

    # === 4. ORCHESTRATOR ROUTES TO WORKERS ===
    result = council.execute(
        prompt=orchestrator_prompt,
        module=module,
        context=context
    )

    # === 5. COMPLETE EXECUTION ===
    success = result.get("status") == "success"
    module.complete_execution(
        success=success,
        error=result.get("error") if not success else None
    )

    # === 6. MEMORY CONSOLIDATION (triggered in complete_execution) ===

    return result


def build_execution_context(module) -> Dict[str, Any]:
    """
    Build full context for agent execution.

    Includes:
    - Client context (brand voice, personas, history)
    - MRD content
    - Skill plan with SKILL.md summaries
    - Relevant memory (episodic, semantic, procedural)
    """
    from lib.memory.working import WorkingMemory
    from lib.memory.semantic import SemanticMemory
    from lib.memory.episodic import EpisodicMemory

    # Load client context
    client_context = load_client_context(module.client_id)

    # Load MRD
    mrd_path = SYSTEM_ROOT / "modules" / module.module_id / "MRD.md"
    mrd_content = mrd_path.read_text() if mrd_path.exists() else "No MRD found"

    # Build skill plan with SKILL.md summaries
    skill_summaries = []
    for skill_name in module.skill_plan:
        skill_md_path = SYSTEM_ROOT / "skills" / skill_name / "SKILL.md"
        if skill_md_path.exists():
            # Extract key sections from SKILL.md
            content = skill_md_path.read_text()
            skill_summaries.append({
                "name": skill_name,
                "path": f"skills/{skill_name}/SKILL.md",
                "preview": extract_skill_summary(content)
            })
        else:
            skill_summaries.append({
                "name": skill_name,
                "error": "SKILL.md not found"
            })

    # Load relevant memory
    memory_context = load_memory_context(module.client_id, module.meta.get("task_description", ""))

    return {
        "client_context": client_context,
        "mrd": mrd_content,
        "skill_plan": skill_summaries,
        "memory_context": memory_context
    }


def load_client_context(client_id: str) -> str:
    """Load client context from Firebase + local files."""
    context_parts = []

    # Client config
    client_dir = SYSTEM_ROOT / "clients" / client_id
    if client_dir.exists():
        config_file = client_dir / "config" / "client.yaml"
        if config_file.exists():
            context_parts.append(f"## Client Config\n{config_file.read_text()}")

        # Brand voice
        voice_file = client_dir / "voice_contract.md"
        if voice_file.exists():
            context_parts.append(f"## Brand Voice\n{voice_file.read_text()}")

    return "\n\n".join(context_parts) if context_parts else "No client context available"


def load_memory_context(client_id: str, task_description: str) -> str:
    """Load relevant memory for this execution."""
    memory_parts = []

    try:
        # Episodic - recent executions for this client
        from lib.memory.episodic import EpisodicMemory
        episodic = EpisodicMemory()
        recent = episodic.get_recent_events(client_id, limit=5)
        if recent:
            memory_parts.append(f"## Recent Activity\n{recent}")
    except Exception as e:
        logger.warning(f"Could not load episodic memory: {e}")

    try:
        # Semantic - similar past tasks
        from lib.memory.semantic import SemanticMemory
        semantic = SemanticMemory()
        similar = semantic.find_similar(task_description, limit=3)
        if similar:
            memory_parts.append(f"## Similar Past Tasks\n{similar}")
    except Exception as e:
        logger.warning(f"Could not load semantic memory: {e}")

    try:
        # Procedural - successful patterns
        from lib.memory.procedural import ProceduralMemory
        procedural = ProceduralMemory()
        patterns = procedural.get_relevant_patterns(task_description)
        if patterns:
            memory_parts.append(f"## Successful Patterns\n{patterns}")
    except Exception as e:
        logger.warning(f"Could not load procedural memory: {e}")

    return "\n\n".join(memory_parts) if memory_parts else "No memory context available"


def extract_skill_summary(skill_md_content: str) -> str:
    """Extract key info from SKILL.md for context."""
    lines = skill_md_content.split('\n')
    summary_parts = []

    # Get description from frontmatter
    in_frontmatter = False
    for line in lines:
        if line.strip() == '---':
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter and line.startswith('description:'):
            summary_parts.append(line.replace('description:', '').strip())

    # Get "When to Use" section
    in_when_to_use = False
    for line in lines:
        if '## When to Use' in line:
            in_when_to_use = True
            continue
        if in_when_to_use:
            if line.startswith('##'):
                break
            if line.strip().startswith('-'):
                summary_parts.append(line.strip())

    return ' | '.join(summary_parts[:3]) if summary_parts else "See SKILL.md for details"
```

---

### Phase C: Update Agent Council for Module Execution

**File:** `lib/agent_council.py`

**Ensure:** The council's `execute()` method:
1. Provides full context to Orchestrator
2. Orchestrator instructs Workers to read SKILL.md
3. Workers have access to memory layers
4. Evaluators run per SKILL.md quality criteria

---

### Phase D: Wire Memory Consolidation

**File:** `lib/module_manager.py` (`complete_execution` method)

**Changes:** Trigger consolidation that:
1. Writes to episodic memory (what happened)
2. Promotes patterns to semantic memory (if criteria met)
3. Updates procedural memory (successful workflows)

```python
def complete_execution(self, success: bool = True, error: str = None):
    """Complete execution and trigger memory consolidation."""
    if not self.execution:
        raise ValueError("Module not in execution state")

    now = datetime.now(timezone.utc).isoformat()
    self.execution.completed_at = now

    # Transition status
    if success:
        self.transition_to(ModuleStatus.COMPLETED)
    else:
        self.execution.error = error
        self.transition_to(ModuleStatus.FAILED)

    # === MEMORY CONSOLIDATION ===
    try:
        from lib.memory.consolidation import MemoryConsolidator
        consolidator = MemoryConsolidator()

        consolidator.consolidate_module_execution(
            client_id=self.client_id,
            module_id=self.module_id,
            execution=self.execution,
            skill_plan=self.skill_plan,
            success=success,
            outputs=self.get_outputs()
        )
        logger.info(f"Memory consolidation complete for {self.module_id}")
    except Exception as e:
        logger.warning(f"Memory consolidation failed (non-fatal): {e}")

    self.save()
```

---

### Phase E: Fix SkillRunner Fallback

**File:** `lib/skill_runner.py` (lines 451-457)

**Change:** When no `executor_func` is provided, route through agent-based execution that reads SKILL.md, not a direct bypass.

```python
# OLD (broken - bypasses SKILL.md):
if executor_func:
    raw_result = executor_func(inputs)
else:
    from lib.runner import SkillRunner
    runner = SkillRunner(skill_name, version=skill_meta.version, tenant_id=tenant_id)
    raw_result = runner.run(inputs, lambda i: {"output": i})

# NEW (correct - agent reads SKILL.md):
if executor_func:
    raw_result = executor_func(inputs)
else:
    # Execute via agent that reads and follows SKILL.md
    from lib.copilot_planner import CopilotPlanner
    planner = CopilotPlanner()
    raw_result = planner._execute_skill(
        skill_name=skill_name,
        client_id=inputs.get("client_id", "standalone"),
        inputs=inputs
    )
```

---

## Context Engineering Requirements

The execution flow must preserve access to:

| Layer | Source | Used For |
|-------|--------|----------|
| **Working Memory** | Current session | Task description, user clarifications |
| **Episodic Memory** | Firebase | Recent client activity, past runs |
| **Semantic Memory** | Embeddings | Similar tasks, relevant concepts |
| **Procedural Memory** | Success patterns | What worked before |
| **Client Context** | `clients/{id}/` | Brand voice, personas, config |
| **MRD** | `modules/{id}/MRD.md` | Task requirements, scope, outputs |
| **SKILL.md** | `skills/{name}/SKILL.md` | Workflow, constraints, process |

---

## Execution Flow Detail

```
┌─────────────────────────────────────────────────────────────────┐
│                    Module Execution Flow                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. CLI: ./mh1 run-module {module_id} --approve                 │
│     │                                                            │
│     ▼                                                            │
│  2. Load Module (meta.json, MRD.md, skill_plan)                 │
│     │                                                            │
│     ▼                                                            │
│  3. Build Context                                                │
│     ├── Client context (clients/{id}/)                          │
│     ├── Memory context (episodic, semantic, procedural)         │
│     ├── MRD content                                              │
│     └── SKILL.md summaries for each skill                       │
│     │                                                            │
│     ▼                                                            │
│  4. Transition to RUNNING                                        │
│     │                                                            │
│     ▼                                                            │
│  5. Invoke Agent Council                                         │
│     ├── Orchestrator receives full context                      │
│     ├── Routes to Workers per skill_plan                        │
│     └── Each Worker:                                             │
│         ├── Reads SKILL.md                                       │
│         ├── Follows workflow/process                             │
│         ├── Respects constraints/SLA                             │
│         ├── Checkpoints on completion                            │
│         └── Routes output to Evaluators                          │
│     │                                                            │
│     ▼                                                            │
│  6. Evaluators                                                   │
│     ├── Schema validation                                        │
│     ├── Quality criteria (from SKILL.md)                        │
│     ├── Factuality check                                         │
│     └── Pass/Fail/Retry decision                                │
│     │                                                            │
│     ▼                                                            │
│  7. Complete Execution                                           │
│     ├── Transition to COMPLETED/FAILED                          │
│     ├── Store outputs                                            │
│     └── Trigger memory consolidation                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Files Changed

| File | Action | Purpose |
|------|--------|---------|
| `mh1` | MODIFY | Add `run-module` command |
| `lib/module_executor.py` | CREATE | Context-aware execution orchestration |
| `lib/module_manager.py` | MODIFY | Wire memory consolidation |
| `lib/skill_runner.py` | MODIFY | Fix fallback to use SKILL.md-aware path |
| `lib/agent_council.py` | VERIFY | Ensure context passed to agents |
| `lib/cli_menus.py` | MODIFY | Update menu to match TRUE_USER_FLOW.md |

---

## CLI Menu Updates (per TRUE_USER_FLOW.md)

The main menu should offer:

```
[1] Ask (Natural Language)     → Speak to Claude naturally
[2] Modules (View/Create)      → NOT "Plans" - renamed
[3] Run Skills                 → Run skills with AI team assistance
[4] Run Agents                 → Team of vertical experts
[5] Query Data / Refresh       → MCPs, Firebase, connections
[6] Client Details             → Everything tied to client
[7] History                    → Past runs, logs

[s] Switch Client
[h] Health Check
[q] Quit
```

Each menu option should work smoothly for non-technical marketers.

---

## Success Criteria

| Criteria | Validation |
|----------|------------|
| Agents receive full client context | Log context in orchestrator |
| Agents read SKILL.md before execution | Log skill path access |
| Workers follow SKILL.md workflow | Check checkpoints match SKILL.md process |
| Evaluators use SKILL.md quality criteria | Compare eval dimensions to SKILL.md |
| Memory consolidation triggers | Check memory stores after completion |
| Full E2E works | `./mh1 run-module {id} --approve` completes |

---

## Test Scenario

```bash
# 1. Create module with full context
./mh1 -c swimply /audit

# 2. Verify MRD generated
cat modules/lifecycle-audit-XXXXX/MRD.md

# 3. Execute with context awareness
./mh1 run-module lifecycle-audit-XXXXX --approve

# 4. Verify agents read SKILL.md
grep "SKILL.md" logs/$(date +%Y-%m-%d)/swimply/*.json

# 5. Verify outputs match SKILL.md quality criteria
cat modules/lifecycle-audit-XXXXX/outputs/evaluation.json

# 6. Verify memory consolidation
./mh1 memory --client swimply --recent
```

---

---

## Phase F: MRD Upload Support (Future Enhancement)

**Per TRUE_USER_FLOW.md update:** Marketers should be able to upload an existing MRD (PDF, HTML, DOCX) instead of describing the task. This skips MRD generation if the uploaded MRD has sufficient detail.

**Implementation:**
1. Add `[u] Upload MRD` option to Ask menu
2. Parse uploaded files (use `pypdf`, `python-docx`, `beautifulsoup4`)
3. Validate MRD completeness (goals, scope, inputs, outputs defined)
4. If incomplete, AI supplements missing sections
5. Save parsed MRD as `MRD.md` in module folder
6. Proceed directly to planning phase

**Files to modify:**
- `mh1` - Add upload option to task input
- `lib/mrd_generator.py` - Add `parse_uploaded_mrd()` function
- `lib/cli_menus.py` - Add upload flow to Ask menu

---

*Plan revised to ensure SKILL.md is the primary interface and agents have full context awareness.*
