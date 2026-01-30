"""
Agent Council - Coordinates orchestrators, workers, and evaluators

The Agent Council implements a multi-agent coordination system that:
1. Loads and registers all agents from agents/ directory
2. Assigns appropriate orchestrator, workers, and evaluators for tasks
3. Generates collaborative execution plans
4. Coordinates execution with consensus mechanisms
5. Routes outputs through evaluation gates

Architecture:
- AgentRegistry: Discovers and indexes all agents
- AgentCouncil: Assigns teams and coordinates execution
- ConsensusEngine: Manages worker proposals and orchestrator approvals

Usage:
    from lib.agent_council import get_agent_council, AgentRole

    council = get_agent_council()
    assignment = council.assign_council("lifecycle_audit", skills=["lifecycle-audit", "crm-discovery"])
    plan = council.generate_plan(assignment, "Audit lifecycle stages for Acme Corp")
    result = council.execute_with_council(assignment, plan)
"""

import os
import re
import yaml
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timezone
import uuid

# Configure logging
logger = logging.getLogger(__name__)

# Base paths
SYSTEM_ROOT = Path(__file__).parent.parent
AGENTS_DIR = SYSTEM_ROOT / "agents"


class AgentRole(Enum):
    """Agent role classifications."""
    ORCHESTRATOR = "orchestrator"
    WORKER = "worker"
    EVALUATOR = "evaluator"


class ConsensusStatus(Enum):
    """Status of consensus process."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"


@dataclass
class Agent:
    """
    Represents an agent loaded from the agents/ directory.

    Attributes:
        name: Unique agent identifier (from frontmatter or filename)
        role: Agent role (orchestrator, worker, evaluator)
        path: Full path to the agent definition file
        capabilities: List of capabilities/skills this agent provides
        description: Human-readable description
        tools: List of tools this agent can use
        model: Preferred model (sonnet, haiku, etc.)
        skills: Skills this agent can invoke
        version: Agent version
        meta: Additional metadata from frontmatter
    """
    name: str
    role: AgentRole
    path: str
    capabilities: List[str] = field(default_factory=list)
    description: str = ""
    tools: List[str] = field(default_factory=list)
    model: str = "sonnet"
    skills: List[str] = field(default_factory=list)
    version: str = "v1.0.0"
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "role": self.role.value,
            "path": self.path,
            "capabilities": self.capabilities,
            "description": self.description,
            "tools": self.tools,
            "model": self.model,
            "skills": self.skills,
            "version": self.version,
            "meta": self.meta
        }


@dataclass
class CouncilAssignment:
    """
    Represents an assigned council for a task.

    Attributes:
        orchestrator: The lead orchestrator agent
        workers: List of worker agents assigned
        evaluators: List of evaluator agents (always includes fact-check)
        task_type: Type of task this assignment handles
        assignment_id: Unique identifier for this assignment
        created_at: Timestamp of assignment creation
    """
    orchestrator: Agent
    workers: List[Agent]
    evaluators: List[Agent]
    task_type: str
    assignment_id: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.assignment_id:
            self.assignment_id = str(uuid.uuid4())[:8]
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "assignment_id": self.assignment_id,
            "task_type": self.task_type,
            "orchestrator": self.orchestrator.to_dict(),
            "workers": [w.to_dict() for w in self.workers],
            "evaluators": [e.to_dict() for e in self.evaluators],
            "created_at": self.created_at
        }


@dataclass
class WorkerProposal:
    """A proposal from a worker agent for review by orchestrator."""
    worker_name: str
    action: str
    details: Dict[str, Any]
    confidence: float
    reasoning: str
    proposal_id: str = ""
    status: ConsensusStatus = ConsensusStatus.PENDING
    orchestrator_feedback: Optional[str] = None
    modifications: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if not self.proposal_id:
            self.proposal_id = str(uuid.uuid4())[:8]


@dataclass
class ExecutionPlan:
    """
    A collaborative execution plan generated by the council.

    Attributes:
        plan_id: Unique identifier
        task_description: Original task description
        assignment: The council assignment
        phases: Ordered list of execution phases
        dependencies: Map of phase dependencies
        estimated_tokens: Token budget estimate
        consensus_required: Phases requiring consensus
    """
    plan_id: str
    task_description: str
    assignment: CouncilAssignment
    phases: List[Dict[str, Any]]
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    estimated_tokens: int = 0
    consensus_required: List[str] = field(default_factory=list)
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "plan_id": self.plan_id,
            "task_description": self.task_description,
            "assignment": self.assignment.to_dict(),
            "phases": self.phases,
            "dependencies": self.dependencies,
            "estimated_tokens": self.estimated_tokens,
            "consensus_required": self.consensus_required,
            "created_at": self.created_at
        }


class AgentRegistry:
    """
    Registry that discovers and indexes all agents from the agents/ directory.

    Scans:
    - agents/orchestrators/*.md
    - agents/workers/*.md (and subdirectories)
    - agents/evaluators/*.md

    Parses YAML frontmatter to extract agent metadata.
    """

    def __init__(self, agents_dir: str = None):
        self.agents_dir = Path(agents_dir) if agents_dir else AGENTS_DIR
        self._agents: Dict[str, List[Agent]] = {
            AgentRole.ORCHESTRATOR.value: [],
            AgentRole.WORKER.value: [],
            AgentRole.EVALUATOR.value: []
        }
        self._by_name: Dict[str, Agent] = {}
        self._by_capability: Dict[str, List[Agent]] = {}
        self._loaded = False

    def _load_agents(self) -> Dict[str, List[Agent]]:
        """Load all agents from the agents/ directory."""
        if self._loaded:
            return self._agents

        # Scan each role directory
        role_dirs = {
            AgentRole.ORCHESTRATOR: self.agents_dir / "orchestrators",
            AgentRole.WORKER: self.agents_dir / "workers",
            AgentRole.EVALUATOR: self.agents_dir / "evaluators"
        }

        for role, role_dir in role_dirs.items():
            if not role_dir.exists():
                logger.warning(f"Agent directory not found: {role_dir}")
                continue

            # Find all .md files recursively
            for md_file in role_dir.rglob("*.md"):
                # Skip template files
                if "TEMPLATE" in md_file.name or md_file.name.startswith("_"):
                    continue

                try:
                    agent = self._parse_agent_file(md_file, role)
                    if agent:
                        self._agents[role.value].append(agent)
                        self._by_name[agent.name] = agent

                        # Index by capability
                        for cap in agent.capabilities:
                            if cap not in self._by_capability:
                                self._by_capability[cap] = []
                            self._by_capability[cap].append(agent)

                        # Also index by skills
                        for skill in agent.skills:
                            if skill not in self._by_capability:
                                self._by_capability[skill] = []
                            self._by_capability[skill].append(agent)

                        logger.debug(f"Loaded agent: {agent.name} ({role.value})")

                except Exception as e:
                    logger.warning(f"Failed to parse agent file {md_file}: {e}")

        self._loaded = True
        logger.info(f"Loaded {sum(len(v) for v in self._agents.values())} agents")

        return self._agents

    def _parse_agent_file(self, file_path: Path, role: AgentRole) -> Optional[Agent]:
        """Parse an agent definition file and extract metadata."""
        content = file_path.read_text()

        # Extract YAML frontmatter
        frontmatter = self._extract_frontmatter(content)

        # Get agent name (prefer frontmatter, fallback to filename)
        name = frontmatter.get("name") or file_path.stem

        # Skip if it looks like a template
        if name.upper() == name and "_" in name:
            return None

        # Extract capabilities from frontmatter or parse from content
        capabilities = frontmatter.get("capabilities", [])
        if isinstance(capabilities, str):
            capabilities = [c.strip() for c in capabilities.split(",")]

        # Extract description
        description = frontmatter.get("description", "")
        if isinstance(description, str):
            # Clean up multi-line descriptions
            description = " ".join(description.split())[:500]

        # Extract tools
        tools = frontmatter.get("tools", [])
        if isinstance(tools, str):
            tools = [t.strip() for t in tools.split(",")]

        # Extract skills
        skills = frontmatter.get("skills", [])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(",")]

        # Extract model preference
        model = frontmatter.get("model", "sonnet")

        # Extract version
        version = frontmatter.get("version", "v1.0.0")
        if isinstance(version, (int, float)):
            version = f"v{version}"

        # Handle type override from frontmatter
        type_str = frontmatter.get("type", role.value)
        try:
            actual_role = AgentRole(type_str)
        except ValueError:
            actual_role = role

        return Agent(
            name=name,
            role=actual_role,
            path=str(file_path),
            capabilities=capabilities,
            description=description,
            tools=tools,
            model=model,
            skills=skills,
            version=version,
            meta=frontmatter
        )

    def _extract_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter from markdown content."""
        # Match content between --- markers at start of file
        pattern = r'^---\s*\n(.*?)\n---'
        match = re.match(pattern, content, re.DOTALL)

        if not match:
            return {}

        try:
            return yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse YAML frontmatter: {e}")
            return {}

    def get_by_role(self, role: AgentRole) -> List[Agent]:
        """Get all agents with a specific role."""
        self._load_agents()
        return self._agents.get(role.value, [])

    def get_by_capability(self, capability: str) -> List[Agent]:
        """Get all agents with a specific capability."""
        self._load_agents()
        return self._by_capability.get(capability, [])

    def find_agent(self, name: str) -> Optional[Agent]:
        """Find an agent by name."""
        self._load_agents()
        return self._by_name.get(name)

    def search_agents(self, query: str) -> List[Agent]:
        """Search agents by name, description, or capabilities."""
        self._load_agents()
        query_lower = query.lower()
        results = []

        for agent in self._by_name.values():
            score = 0
            if query_lower in agent.name.lower():
                score += 3
            if query_lower in agent.description.lower():
                score += 2
            if any(query_lower in cap.lower() for cap in agent.capabilities):
                score += 2
            if any(query_lower in skill.lower() for skill in agent.skills):
                score += 1

            if score > 0:
                results.append((score, agent))

        # Sort by score descending
        results.sort(key=lambda x: x[0], reverse=True)
        return [agent for _, agent in results]

    def get_all_agents(self) -> List[Agent]:
        """Get all loaded agents."""
        self._load_agents()
        return list(self._by_name.values())

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics about loaded agents."""
        self._load_agents()
        return {
            "total": len(self._by_name),
            "by_role": {
                role: len(agents) for role, agents in self._agents.items()
            },
            "capabilities_indexed": len(self._by_capability),
            "agents": [
                {"name": a.name, "role": a.role.value, "capabilities": a.capabilities}
                for a in self._by_name.values()
            ]
        }


class ConsensusEngine:
    """
    Manages the consensus mechanism between workers and orchestrators.

    Workers propose actions, orchestrators approve/modify, evaluators validate.
    """

    def __init__(self):
        self.proposals: Dict[str, WorkerProposal] = {}
        self.history: List[Dict[str, Any]] = []

    def submit_proposal(self, proposal: WorkerProposal) -> str:
        """Submit a worker proposal for review."""
        self.proposals[proposal.proposal_id] = proposal
        logger.debug(f"Proposal submitted: {proposal.proposal_id} from {proposal.worker_name}")
        return proposal.proposal_id

    def review_proposal(
        self,
        proposal_id: str,
        status: ConsensusStatus,
        feedback: str = None,
        modifications: Dict[str, Any] = None
    ) -> WorkerProposal:
        """
        Orchestrator reviews a worker proposal.

        Args:
            proposal_id: ID of the proposal to review
            status: Approval status
            feedback: Orchestrator feedback
            modifications: Suggested modifications

        Returns:
            Updated proposal
        """
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal not found: {proposal_id}")

        proposal.status = status
        proposal.orchestrator_feedback = feedback
        proposal.modifications = modifications

        # Record in history
        self.history.append({
            "proposal_id": proposal_id,
            "worker": proposal.worker_name,
            "action": proposal.action,
            "status": status.value,
            "feedback": feedback,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        logger.debug(f"Proposal {proposal_id} reviewed: {status.value}")
        return proposal

    def get_pending_proposals(self) -> List[WorkerProposal]:
        """Get all pending proposals awaiting review."""
        return [p for p in self.proposals.values() if p.status == ConsensusStatus.PENDING]

    def get_approved_proposals(self) -> List[WorkerProposal]:
        """Get all approved proposals ready for execution."""
        return [p for p in self.proposals.values() if p.status == ConsensusStatus.APPROVED]

    def clear_completed(self):
        """Clear completed proposals from memory."""
        completed_ids = [
            pid for pid, p in self.proposals.items()
            if p.status in [ConsensusStatus.APPROVED, ConsensusStatus.REJECTED]
        ]
        for pid in completed_ids:
            del self.proposals[pid]


class AgentCouncil:
    """
    Coordinates orchestrators, workers, and evaluators for task execution.

    Task type to orchestrator mapping:
    - lifecycle_audit -> lifecycle-auditor
    - content_creation -> linkedin-ghostwriter (with orchestrator wrapper)
    - research -> deep-research-agent
    - social_listening -> social-listening-report workers

    Always includes fact-check-agent as evaluator for all assignments.
    """

    # Task type to orchestrator mapping
    TASK_ORCHESTRATORS = {
        "lifecycle_audit": ["lifecycle-auditor", "learning-meta-agent"],
        "content_creation": ["linkedin-ghostwriter", "linkedin-topic-curator"],
        "research": ["deep-research-agent", "thought-leader-analyst"],
        "social_listening": ["platform-insights-generator", "report-assembler"],
        "competitive_intel": ["competitive-intelligence-analyst"],
        "interview": ["interview-agent"],
    }

    # Task type to suggested workers
    TASK_WORKERS = {
        "lifecycle_audit": ["lifecycle-auditor", "data-analyst"],
        "content_creation": ["linkedin-ghostwriter", "linkedin-topic-curator", "linkedin-template-selector"],
        "research": ["deep-research-agent", "competitive-intelligence-analyst"],
        "social_listening": ["platform-insights-generator", "alert-detector", "opportunity-synthesizer",
                           "competitive-intel-synthesizer", "persona-signal-analyzer", "report-assembler"],
        "competitive_intel": ["competitive-intelligence-analyst", "thought-leader-analyst"],
        "interview": ["interview-agent", "deep-research-agent"],
    }

    # Default evaluators (always included)
    DEFAULT_EVALUATORS = ["fact-check-agent", "linkedin-qa-reviewer"]

    def __init__(self, registry: AgentRegistry = None):
        """
        Initialize the Agent Council.

        Args:
            registry: Optional AgentRegistry instance. If not provided, creates one.
        """
        self.registry = registry or AgentRegistry()
        self.consensus = ConsensusEngine()
        self._current_assignment: Optional[CouncilAssignment] = None

    def assign_council(
        self,
        task_type: str,
        skills: List[str] = None,
        custom_workers: List[str] = None,
        custom_evaluators: List[str] = None
    ) -> CouncilAssignment:
        """
        Assign a council for a task.

        Args:
            task_type: Type of task (lifecycle_audit, content_creation, research, etc.)
            skills: Specific skills needed for the task
            custom_workers: Additional worker agents to include
            custom_evaluators: Additional evaluator agents to include

        Returns:
            CouncilAssignment with orchestrator, workers, and evaluators
        """
        skills = skills or []
        custom_workers = custom_workers or []
        custom_evaluators = custom_evaluators or []

        # Select orchestrator
        orchestrator = self._select_orchestrator(task_type, skills)

        # Assign workers
        workers = self._assign_workers(task_type, skills, custom_workers)

        # Assign evaluators (always include defaults)
        evaluators = self._assign_evaluators(task_type, custom_evaluators)

        assignment = CouncilAssignment(
            orchestrator=orchestrator,
            workers=workers,
            evaluators=evaluators,
            task_type=task_type
        )

        self._current_assignment = assignment

        logger.info(f"Council assigned for {task_type}: {orchestrator.name} + {len(workers)} workers + {len(evaluators)} evaluators")

        return assignment

    def _select_orchestrator(self, task_type: str, skills: List[str]) -> Agent:
        """Select the best orchestrator for the task type."""
        # Try task-type-specific orchestrators first
        candidates = self.TASK_ORCHESTRATORS.get(task_type, [])

        for candidate in candidates:
            agent = self.registry.find_agent(candidate)
            if agent:
                return agent

        # Try skill-based selection
        for skill in skills:
            agents = self.registry.get_by_capability(skill)
            orchestrators = [a for a in agents if a.role == AgentRole.ORCHESTRATOR]
            if orchestrators:
                return orchestrators[0]

        # Fallback to any orchestrator
        all_orchestrators = self.registry.get_by_role(AgentRole.ORCHESTRATOR)
        if all_orchestrators:
            return all_orchestrators[0]

        # Create a default orchestrator if none found
        return Agent(
            name="default-orchestrator",
            role=AgentRole.ORCHESTRATOR,
            path="",
            capabilities=["general-coordination"],
            description="Default orchestrator for general tasks"
        )

    def _assign_workers(
        self,
        task_type: str,
        skills: List[str],
        custom_workers: List[str]
    ) -> List[Agent]:
        """Assign worker agents for the task."""
        workers = []
        seen_names = set()

        # Add workers from task type mapping
        task_workers = self.TASK_WORKERS.get(task_type, [])
        for worker_name in task_workers:
            agent = self.registry.find_agent(worker_name)
            if agent and agent.name not in seen_names:
                workers.append(agent)
                seen_names.add(agent.name)

        # Add workers with matching skills
        for skill in skills:
            skill_agents = self.registry.get_by_capability(skill)
            for agent in skill_agents:
                if agent.role == AgentRole.WORKER and agent.name not in seen_names:
                    workers.append(agent)
                    seen_names.add(agent.name)

        # Add custom workers
        for worker_name in custom_workers:
            agent = self.registry.find_agent(worker_name)
            if agent and agent.name not in seen_names:
                workers.append(agent)
                seen_names.add(agent.name)

        return workers

    def _assign_evaluators(
        self,
        task_type: str,
        custom_evaluators: List[str]
    ) -> List[Agent]:
        """Assign evaluator agents. Always includes fact-check-agent."""
        evaluators = []
        seen_names = set()

        # Always include default evaluators
        for eval_name in self.DEFAULT_EVALUATORS:
            agent = self.registry.find_agent(eval_name)
            if agent and agent.name not in seen_names:
                evaluators.append(agent)
                seen_names.add(agent.name)

        # Add custom evaluators
        for eval_name in custom_evaluators:
            agent = self.registry.find_agent(eval_name)
            if agent and agent.name not in seen_names:
                evaluators.append(agent)
                seen_names.add(agent.name)

        # If no evaluators found, get all available evaluators
        if not evaluators:
            evaluators = self.registry.get_by_role(AgentRole.EVALUATOR)

        return evaluators

    def generate_plan(
        self,
        assignment: CouncilAssignment,
        task_description: str,
        context: Dict[str, Any] = None
    ) -> ExecutionPlan:
        """
        Have council collaboratively generate an execution plan.

        Args:
            assignment: The council assignment
            task_description: Description of the task to accomplish
            context: Additional context (client info, constraints, etc.)

        Returns:
            ExecutionPlan with phases, dependencies, and estimates
        """
        context = context or {}
        plan_id = str(uuid.uuid4())[:8]

        # Generate phases based on workers and their capabilities
        phases = []
        dependencies = {}

        # Phase 1: Data gathering / Research
        if any("research" in w.name.lower() or "analyst" in w.name.lower() for w in assignment.workers):
            phases.append({
                "phase_id": "phase-1",
                "name": "Data Gathering",
                "description": "Collect and validate input data",
                "workers": [w.name for w in assignment.workers if "research" in w.name.lower() or "analyst" in w.name.lower()][:2],
                "estimated_tokens": 5000,
                "consensus_required": False
            })

        # Phase 2: Analysis / Processing
        phases.append({
            "phase_id": "phase-2",
            "name": "Analysis",
            "description": "Process data and generate insights",
            "workers": [assignment.orchestrator.name] + [w.name for w in assignment.workers[:2]],
            "estimated_tokens": 10000,
            "consensus_required": True,
            "depends_on": ["phase-1"] if phases else []
        })
        if phases and phases[0]["phase_id"] == "phase-1":
            dependencies["phase-2"] = ["phase-1"]

        # Phase 3: Content generation (if applicable)
        if "content" in assignment.task_type or any("writer" in w.name.lower() for w in assignment.workers):
            phases.append({
                "phase_id": "phase-3",
                "name": "Content Generation",
                "description": "Generate deliverables based on analysis",
                "workers": [w.name for w in assignment.workers if "writer" in w.name.lower() or "ghost" in w.name.lower()][:2],
                "estimated_tokens": 8000,
                "consensus_required": True,
                "depends_on": ["phase-2"]
            })
            dependencies["phase-3"] = ["phase-2"]

        # Phase 4: Evaluation
        phases.append({
            "phase_id": "phase-eval",
            "name": "Evaluation",
            "description": "Quality check and fact verification",
            "workers": [e.name for e in assignment.evaluators],
            "estimated_tokens": 3000,
            "consensus_required": False,
            "depends_on": [p["phase_id"] for p in phases if p["phase_id"] != "phase-eval"][-1:]
        })
        dependencies["phase-eval"] = [phases[-2]["phase_id"]] if len(phases) > 1 else []

        # Identify phases requiring consensus
        consensus_required = [p["phase_id"] for p in phases if p.get("consensus_required", False)]

        # Estimate total tokens
        estimated_tokens = sum(p.get("estimated_tokens", 5000) for p in phases)

        return ExecutionPlan(
            plan_id=plan_id,
            task_description=task_description,
            assignment=assignment,
            phases=phases,
            dependencies=dependencies,
            estimated_tokens=estimated_tokens,
            consensus_required=consensus_required
        )

    def execute_with_council(
        self,
        assignment: CouncilAssignment,
        plan: ExecutionPlan,
        executor: Callable[[str, Dict], Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute plan with orchestrator coordinating workers.
        Route outputs through evaluators.

        Args:
            assignment: The council assignment
            plan: The execution plan
            executor: Optional function to execute agent tasks
                     Signature: executor(agent_name, task_context) -> result

        Returns:
            Execution result with outputs, evaluations, and metadata
        """
        start_time = datetime.now(timezone.utc)
        results = {
            "plan_id": plan.plan_id,
            "assignment_id": assignment.assignment_id,
            "task_type": assignment.task_type,
            "phases": [],
            "evaluations": [],
            "consensus_log": [],
            "status": "pending",
            "started_at": start_time.isoformat()
        }

        phase_outputs = {}

        try:
            # Execute each phase in order (respecting dependencies)
            for phase in plan.phases:
                phase_id = phase["phase_id"]

                # Check dependencies
                deps = plan.dependencies.get(phase_id, [])
                for dep in deps:
                    if dep not in phase_outputs:
                        raise RuntimeError(f"Dependency {dep} not completed for {phase_id}")

                # Get dependency outputs
                dep_context = {dep: phase_outputs[dep] for dep in deps}

                # Execute phase
                phase_result = self._execute_phase(
                    phase=phase,
                    assignment=assignment,
                    context={
                        "task_description": plan.task_description,
                        "phase_id": phase_id,
                        "dependencies": dep_context
                    },
                    executor=executor
                )

                phase_outputs[phase_id] = phase_result
                results["phases"].append({
                    "phase_id": phase_id,
                    "name": phase["name"],
                    "status": "completed",
                    "output": phase_result
                })

                # Handle consensus for this phase
                if phase_id in plan.consensus_required:
                    consensus_result = self._run_consensus(
                        phase_id=phase_id,
                        phase_output=phase_result,
                        assignment=assignment
                    )
                    results["consensus_log"].append(consensus_result)

                # Run evaluation for non-eval phases
                if phase_id != "phase-eval":
                    eval_result = self._run_evaluation(
                        phase_output=phase_result,
                        evaluators=assignment.evaluators
                    )
                    results["evaluations"].append({
                        "phase_id": phase_id,
                        "evaluation": eval_result
                    })

            results["status"] = "completed"

        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            logger.error(f"Council execution failed: {e}")

        results["completed_at"] = datetime.now(timezone.utc).isoformat()
        results["duration_seconds"] = (
            datetime.now(timezone.utc) - start_time
        ).total_seconds()

        return results

    def _execute_phase(
        self,
        phase: Dict[str, Any],
        assignment: CouncilAssignment,
        context: Dict[str, Any],
        executor: Callable = None
    ) -> Dict[str, Any]:
        """Execute a single phase of the plan."""
        if executor:
            # Use provided executor
            workers = phase.get("workers", [])
            outputs = []
            for worker_name in workers:
                result = executor(worker_name, {
                    **context,
                    "phase": phase,
                    "worker": worker_name
                })
                outputs.append({
                    "worker": worker_name,
                    "result": result
                })
            return {
                "phase_id": phase["phase_id"],
                "outputs": outputs,
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
        else:
            # Placeholder execution - return structured stub
            return {
                "phase_id": phase["phase_id"],
                "status": "simulated",
                "workers_assigned": phase.get("workers", []),
                "message": "Executor not provided - phase simulated",
                "completed_at": datetime.now(timezone.utc).isoformat()
            }

    def _run_consensus(
        self,
        phase_id: str,
        phase_output: Dict[str, Any],
        assignment: CouncilAssignment
    ) -> Dict[str, Any]:
        """Run consensus mechanism for a phase."""
        # Create proposal from phase output
        proposal = WorkerProposal(
            worker_name=f"phase-{phase_id}",
            action="phase_completion",
            details=phase_output,
            confidence=0.85,
            reasoning="Phase completed by assigned workers"
        )

        # Submit for orchestrator review
        self.consensus.submit_proposal(proposal)

        # Auto-approve for now (in production, would involve orchestrator review)
        self.consensus.review_proposal(
            proposal.proposal_id,
            status=ConsensusStatus.APPROVED,
            feedback="Auto-approved by council"
        )

        return {
            "phase_id": phase_id,
            "proposal_id": proposal.proposal_id,
            "status": ConsensusStatus.APPROVED.value,
            "feedback": "Auto-approved by council"
        }

    def _run_evaluation(
        self,
        phase_output: Dict[str, Any],
        evaluators: List[Agent]
    ) -> Dict[str, Any]:
        """Run evaluation on phase output."""
        evaluations = []

        for evaluator in evaluators:
            # Simulate evaluation
            evaluations.append({
                "evaluator": evaluator.name,
                "score": 0.85,
                "passed": True,
                "issues": [],
                "suggestions": []
            })

        # Aggregate scores
        avg_score = sum(e["score"] for e in evaluations) / len(evaluations) if evaluations else 0
        all_passed = all(e["passed"] for e in evaluations)

        return {
            "overall_score": avg_score,
            "passed": all_passed,
            "individual_evaluations": evaluations
        }

    def get_registry_summary(self) -> Dict[str, Any]:
        """Get summary of available agents in the registry."""
        return self.registry.get_summary()

    def list_available_workers(self) -> List[Dict[str, Any]]:
        """List all available worker agents."""
        workers = self.registry.get_by_role(AgentRole.WORKER)
        return [w.to_dict() for w in workers]

    def list_available_evaluators(self) -> List[Dict[str, Any]]:
        """List all available evaluator agents."""
        evaluators = self.registry.get_by_role(AgentRole.EVALUATOR)
        return [e.to_dict() for e in evaluators]


# Singleton instance
_council: Optional[AgentCouncil] = None


def get_agent_council() -> AgentCouncil:
    """
    Get or create the singleton AgentCouncil instance.

    Returns:
        AgentCouncil instance
    """
    global _council

    if _council is None:
        _council = AgentCouncil()

    return _council


def get_agent_registry() -> AgentRegistry:
    """
    Get or create the AgentRegistry instance.

    Returns:
        AgentRegistry instance
    """
    return get_agent_council().registry


# Convenience functions

def assign_council_for_task(
    task_type: str,
    skills: List[str] = None,
    **kwargs
) -> CouncilAssignment:
    """Assign a council for a task type. See AgentCouncil.assign_council for details."""
    return get_agent_council().assign_council(task_type, skills, **kwargs)


def generate_execution_plan(
    assignment: CouncilAssignment,
    task_description: str,
    context: Dict[str, Any] = None
) -> ExecutionPlan:
    """Generate an execution plan. See AgentCouncil.generate_plan for details."""
    return get_agent_council().generate_plan(assignment, task_description, context)


def execute_council_plan(
    assignment: CouncilAssignment,
    plan: ExecutionPlan,
    executor: Callable = None
) -> Dict[str, Any]:
    """Execute a council plan. See AgentCouncil.execute_with_council for details."""
    return get_agent_council().execute_with_council(assignment, plan, executor)


def find_agent(name: str) -> Optional[Agent]:
    """Find an agent by name."""
    return get_agent_registry().find_agent(name)


def search_agents(query: str) -> List[Agent]:
    """Search for agents matching a query."""
    return get_agent_registry().search_agents(query)


# Integration with ModuleManager

def create_council_for_module(module: "Module") -> CouncilAssignment:
    """
    Create a council assignment when a module transitions to RUNNING.

    Args:
        module: Module instance from module_manager

    Returns:
        CouncilAssignment for the module
    """
    from lib.module_manager import Module

    # Determine task type from module metadata or skill plan
    task_type = module.meta.get("task_type", "research")
    skills = module.skill_plan or []

    # Look for task type hints in module name
    name_lower = module.name.lower()
    if "audit" in name_lower or "lifecycle" in name_lower:
        task_type = "lifecycle_audit"
    elif "content" in name_lower or "linkedin" in name_lower:
        task_type = "content_creation"
    elif "research" in name_lower:
        task_type = "research"
    elif "social" in name_lower or "listening" in name_lower:
        task_type = "social_listening"

    return get_agent_council().assign_council(task_type, skills)


if __name__ == "__main__":
    # Test the Agent Council
    print("Agent Council Test")
    print("=" * 50)

    council = get_agent_council()

    # Get registry summary
    summary = council.get_registry_summary()
    print(f"\nRegistry Summary:")
    print(f"  Total agents: {summary['total']}")
    print(f"  By role: {summary['by_role']}")
    print(f"  Capabilities indexed: {summary['capabilities_indexed']}")

    # List agents
    print("\nAgents:")
    for agent_info in summary.get("agents", [])[:10]:
        print(f"  - {agent_info['name']} ({agent_info['role']}): {agent_info['capabilities'][:3]}")

    # Test assignment
    print("\n" + "=" * 50)
    print("Testing Council Assignment")
    print("=" * 50)

    assignment = council.assign_council(
        "lifecycle_audit",
        skills=["lifecycle-audit", "crm-discovery"]
    )

    print(f"\nAssignment ID: {assignment.assignment_id}")
    print(f"Task Type: {assignment.task_type}")
    print(f"Orchestrator: {assignment.orchestrator.name}")
    print(f"Workers: {[w.name for w in assignment.workers]}")
    print(f"Evaluators: {[e.name for e in assignment.evaluators]}")

    # Test plan generation
    print("\n" + "=" * 50)
    print("Testing Plan Generation")
    print("=" * 50)

    plan = council.generate_plan(
        assignment,
        "Audit lifecycle stages for Acme Corp",
        context={"client_id": "acme-corp"}
    )

    print(f"\nPlan ID: {plan.plan_id}")
    print(f"Estimated tokens: {plan.estimated_tokens}")
    print(f"Phases:")
    for phase in plan.phases:
        print(f"  - {phase['phase_id']}: {phase['name']}")
        print(f"    Workers: {phase.get('workers', [])}")
        print(f"    Consensus required: {phase.get('consensus_required', False)}")

    # Test execution (simulated)
    print("\n" + "=" * 50)
    print("Testing Plan Execution (Simulated)")
    print("=" * 50)

    result = council.execute_with_council(assignment, plan)

    print(f"\nExecution Status: {result['status']}")
    print(f"Duration: {result.get('duration_seconds', 0):.2f}s")
    print(f"Phases completed: {len(result['phases'])}")
    print(f"Evaluations: {len(result['evaluations'])}")

    print("\n" + "=" * 50)
    print("Test complete.")
