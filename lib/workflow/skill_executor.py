"""
Skill Executor for MH1

Loads and executes skills, streams progress, handles outputs.
Includes pre-flight checking for requirements.
"""

import os
import sys
import json
import yaml
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable, Generator
from dataclasses import dataclass

import anthropic
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown

from lib.workflow.preflight import PreflightChecker, check_skill_requirements

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Brand colors
C = {
    "pink": "#EC4899",
    "orange": "#F97316",
    "amber": "#FBBF24",
    "yellow": "#FDE047",
    "white": "#FAFAFA",
    "gray": "#9CA3AF",
    "dim": "#4B5563",
    "green": "#22C55E",
    "red": "#EF4444",
    "cyan": "#06B6D4",
}

console = Console()


@dataclass
class SkillResult:
    """Result of a skill execution."""
    skill_name: str
    success: bool
    output: dict
    error: Optional[str] = None
    duration_seconds: float = 0
    tokens_used: int = 0


class SkillExecutor:
    """Executes MH1 skills."""

    def __init__(self, client_id: str = None):
        self.client_id = client_id
        self.client = anthropic.Anthropic()
        self.skills_cache = {}
        self._load_skills()

    def _load_skills(self):
        """Load all available skills."""
        for dirname in [".skills", "skills"]:
            skills_dir = PROJECT_ROOT / dirname
            if not skills_dir.exists():
                continue
            for category_dir in skills_dir.iterdir():
                if not category_dir.is_dir() or category_dir.name.startswith("_"):
                    continue
                for skill_dir in category_dir.iterdir():
                    if not skill_dir.is_dir() or "TEMPLATE" in skill_dir.name:
                        continue
                    skill_md = skill_dir / "SKILL.md"
                    if skill_md.exists():
                        self._parse_skill(skill_md)

    def _parse_skill(self, skill_path: Path):
        """Parse a skill definition."""
        try:
            content = skill_path.read_text()
            if not content.startswith("---"):
                return

            parts = content.split("---", 2)
            if len(parts) < 3:
                return

            frontmatter = yaml.safe_load(parts[1])
            body = parts[2].strip()

            name = frontmatter.get("name", skill_path.parent.name)
            self.skills_cache[name] = {
                "name": name,
                "path": skill_path,
                "frontmatter": frontmatter,
                "body": body,
                "description": frontmatter.get("description", ""),
                "inputs": frontmatter.get("inputs", []),
                "outputs": frontmatter.get("outputs", {}),
                "category": skill_path.parent.parent.name.replace("-skills", ""),
            }
        except Exception as e:
            pass  # Skip malformed skills

    def list_skills(self) -> list:
        """List available skills."""
        return list(self.skills_cache.keys())

    def get_skill(self, name: str) -> Optional[dict]:
        """Get skill definition."""
        return self.skills_cache.get(name)

    def get_required_inputs(self, skill_name: str) -> list:
        """Get list of required inputs for a skill."""
        skill = self.get_skill(skill_name)
        if not skill:
            return []

        required = []
        for inp in skill.get("inputs", []):
            if isinstance(inp, dict):
                if inp.get("required", False):
                    required.append(inp.get("name", inp.get("param", "unknown")))
            elif isinstance(inp, str):
                # Simple string format - assume required
                required.append(inp)

        return required

    def validate_inputs(self, skill_name: str, inputs: dict) -> tuple[bool, list]:
        """
        Validate that required inputs are provided.

        Returns:
            Tuple of (is_valid, missing_inputs)
        """
        skill = self.get_skill(skill_name)
        if not skill:
            return False, [f"Skill '{skill_name}' not found"]

        missing = []
        skill_inputs = skill.get("inputs", [])

        for inp in skill_inputs:
            if isinstance(inp, dict):
                name = inp.get("name", inp.get("param"))
                required = inp.get("required", False)
                if required and name and name not in inputs:
                    desc = inp.get("description", "")
                    missing.append(f"{name}: {desc}" if desc else name)
            elif isinstance(inp, str) and inp not in inputs:
                missing.append(inp)

        return len(missing) == 0, missing

    def execute(
        self,
        skill_name: str,
        inputs: dict = None,
        context: str = "",
        stream_callback: Callable = None,
        skip_validation: bool = False,
    ) -> SkillResult:
        """
        Execute a skill.

        Args:
            skill_name: Name of the skill to run
            inputs: Input parameters
            context: Additional context (client data, previous outputs)
            stream_callback: Callback for streaming output
            skip_validation: Skip input validation (use with caution)

        Returns:
            SkillResult with output or error
        """
        start_time = time.time()
        inputs = inputs or {}

        # Get skill definition
        skill = self.get_skill(skill_name)
        if not skill:
            return SkillResult(
                skill_name=skill_name,
                success=False,
                output={},
                error=f"Skill '{skill_name}' not found"
            )

        # Pre-flight check: verify platform connections and requirements
        if not skip_validation:
            preflight = check_skill_requirements(skill_name, self.client_id, inputs)
            if not preflight.can_execute:
                # Show what's missing with setup guides
                self._show_preflight_failure(preflight)
                return SkillResult(
                    skill_name=skill_name,
                    success=False,
                    output={
                        "preflight_failed": True,
                        "missing_requirements": [
                            {"name": r.name, "type": r.type, "description": r.description}
                            for r in preflight.missing_requirements
                        ],
                        "setup_guides": preflight.setup_guides,
                        "user_actions": preflight.user_actions_needed,
                    },
                    error=f"BLOCKED: Pre-flight check failed. {'; '.join(preflight.user_actions_needed)}"
                )

        # Input validation: check required inputs are provided
        if not skip_validation:
            is_valid, missing = self.validate_inputs(skill_name, inputs)
            if not is_valid:
                missing_str = "\n".join(f"  - {m}" for m in missing)
                console.print(f"\n[{C['red']}]Cannot execute {skill_name}: Missing required inputs[/]")
                console.print(f"[{C['amber']}]Required inputs not provided:[/]\n{missing_str}\n")
                console.print(f"[{C['cyan']}]ACTION REQUIRED:[/] Ask the user for these inputs before retrying.\n")
                return SkillResult(
                    skill_name=skill_name,
                    success=False,
                    output={"missing_inputs": missing, "action": "collect_inputs"},
                    error=f"BLOCKED: Missing required inputs. You must ask the user for: {', '.join(m.split(':')[0] for m in missing)}. Then retry with [[SKILL:{skill_name}]]."
                )

        # Build execution prompt
        prompt = self._build_execution_prompt(skill, inputs, context)

        # Show progress with inputs
        self._show_start(skill_name, skill.get("description", ""), inputs)

        try:
            # Execute via Claude
            full_response = ""
            tokens = 0

            with self.client.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=self._get_executor_system_prompt(skill),
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    if stream_callback:
                        stream_callback(text)
                    else:
                        console.print(text, end="", markup=False)

            console.print("\n")

            # Parse output
            output = self._parse_output(full_response, skill)

            duration = time.time() - start_time
            self._show_complete(skill_name, duration)

            return SkillResult(
                skill_name=skill_name,
                success=True,
                output=output,
                duration_seconds=duration,
                tokens_used=tokens
            )

        except Exception as e:
            duration = time.time() - start_time
            self._show_error(skill_name, str(e))

            return SkillResult(
                skill_name=skill_name,
                success=False,
                output={},
                error=str(e),
                duration_seconds=duration
            )

    def _build_execution_prompt(self, skill: dict, inputs: dict, context: str) -> str:
        """Build the execution prompt for a skill."""
        skill_body = skill.get("body", "")
        input_str = "\n".join(f"- {k}: {v}" for k, v in inputs.items())

        return f"""Execute this skill with the given inputs.

## Skill: {skill['name']}

{skill_body}

## Inputs Provided
{input_str if input_str else "No specific inputs provided."}

## Additional Context
{context if context else "No additional context."}

## Client
{self.client_id or "No client specified"}

## Instructions
1. Follow the skill process exactly
2. Use the inputs provided
3. Generate the expected outputs
4. Be thorough but concise
5. Return structured output where specified

Execute now:"""

    def _get_executor_system_prompt(self, skill: dict) -> str:
        """Get system prompt for skill execution."""
        return f"""You are executing an MH1 marketing skill.

Skill: {skill['name']}
Category: {skill.get('category', 'general')}
Description: {skill.get('description', '')}

Your job:
1. Execute the skill's process step by step
2. Generate the specified outputs
3. Be thorough, accurate, and actionable
4. Return structured data when the skill specifies JSON output
5. Include confidence scores and sources where applicable

Do not refuse or skip steps. Execute fully."""

    def _parse_output(self, response: str, skill: dict) -> dict:
        """Parse skill output from response."""
        output = {
            "raw": response,
            "skill": skill["name"],
            "timestamp": datetime.now().isoformat(),
        }

        # Try to extract JSON if present
        if "```json" in response:
            try:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                if json_end > json_start:
                    json_str = response[json_start:json_end].strip()
                    output["structured"] = json.loads(json_str)
            except:
                pass

        return output

    def _show_start(self, skill_name: str, description: str, inputs: dict = None):
        """Show skill start indicator with inputs."""
        console.print()
        console.print(Panel(
            f"[{C['white']}]{description}[/]",
            title=f"[bold {C['pink']}]Running: {skill_name}[/]",
            border_style=C['pink']
        ))
        # Show inputs being passed
        if inputs:
            console.print(f"[{C['dim']}]Inputs:[/]")
            for k, v in inputs.items():
                val_preview = str(v)[:50] + "..." if len(str(v)) > 50 else str(v)
                console.print(f"  [{C['cyan']}]{k}[/]: {val_preview}")
        else:
            console.print(f"[{C['amber']}]No inputs provided to skill[/]")
        console.print()

    def _show_preflight_failure(self, result):
        """Show pre-flight check failure with setup guides."""
        from lib.workflow.preflight import PreflightResult

        console.print()
        console.print(Panel(
            f"[{C['red']}]Pre-flight check failed - requirements not met[/]",
            title=f"[bold {C['red']}]Cannot Execute: {result.skill_name}[/]",
            border_style=C['red']
        ))

        # Show what's missing
        if result.user_actions_needed:
            console.print(f"\n[{C['amber']}]Actions needed before this skill can run:[/]")
            for action in result.user_actions_needed:
                console.print(f"  [{C['yellow']}]→[/] {action}")

        # Show setup guides for platform connections
        if result.setup_guides:
            console.print(f"\n[{C['cyan']}]Setup Guides:[/]")
            for platform, guide in result.setup_guides.items():
                console.print(f"\n  [{C['white']}]{platform}:[/]")
                for step in guide.get("steps", [])[:5]:  # Show first 5 steps
                    console.print(f"    [{C['dim']}]{step}[/]")
                if guide.get("docs"):
                    console.print(f"    [{C['cyan']}]Docs:[/] {guide['docs']}")

        console.print()
        console.print(f"[{C['green']}]Once configured, retry the skill.[/]")
        console.print()

    def _show_complete(self, skill_name: str, duration: float):
        """Show skill completion."""
        console.print(f"\n[{C['green']}]✓ {skill_name} completed[/] [{C['dim']}]({duration:.1f}s)[/]\n")

    def _show_error(self, skill_name: str, error: str):
        """Show skill error."""
        console.print(f"\n[{C['red']}]✗ {skill_name} failed: {error}[/]\n")


class PlanExecutor:
    """Executes a module plan with multiple skills."""

    def __init__(self, client_id: str, module_manager=None):
        self.client_id = client_id
        self.skill_executor = SkillExecutor(client_id)
        self.module_manager = module_manager
        self.results = []
        self.is_running = False
        self.current_skill_idx = 0

    def execute_plan(
        self,
        skills: list,
        on_progress: Callable = None,
        on_skill_complete: Callable = None,
    ) -> list[SkillResult]:
        """
        Execute a list of skills in sequence.

        Args:
            skills: List of skill configs [{"name": "skill-name", "inputs": {...}}]
            on_progress: Callback for progress updates
            on_skill_complete: Callback when each skill completes

        Returns:
            List of SkillResults
        """
        self.is_running = True
        self.results = []
        total = len(skills)

        console.print()
        console.print(Panel(
            f"[{C['white']}]Executing {total} skills in sequence[/]",
            title=f"[bold {C['amber']}]Plan Execution[/]",
            border_style=C['amber']
        ))

        # Show plan overview
        self._show_plan_overview(skills)

        for idx, skill_config in enumerate(skills):
            if not self.is_running:
                break

            self.current_skill_idx = idx
            skill_name = skill_config.get("name")
            inputs = skill_config.get("inputs", {})
            depends_on = skill_config.get("depends_on")

            # Get context from previous results if dependency exists
            context = ""
            if depends_on:
                for result in self.results:
                    if result.skill_name == depends_on and result.success:
                        context = f"Previous skill output ({depends_on}):\n{json.dumps(result.output, indent=2)[:2000]}"
                        break

            # Show progress
            self._show_skill_progress(idx, total, skill_name, "running")

            if on_progress:
                on_progress(idx, total, skill_name, "running")

            # Log start
            if self.module_manager:
                self.module_manager.start_skill(skill_name)
                self.module_manager.log_event(f"Started skill: {skill_name}")

            # Execute
            result = self.skill_executor.execute(
                skill_name=skill_name,
                inputs=inputs,
                context=context
            )
            self.results.append(result)

            # Update status
            status = "completed" if result.success else "failed"
            self._show_skill_progress(idx, total, skill_name, status)

            # Log completion
            if self.module_manager:
                if result.success:
                    self.module_manager.complete_skill(skill_name, result.output)
                self.module_manager.log_event(f"Skill {skill_name}: {status}")

            if on_skill_complete:
                on_skill_complete(idx, skill_name, result)

            # Checkpoint after each skill
            if skill_config.get("checkpoint", True):
                self._show_checkpoint(idx, total)

            # Stop on failure unless configured otherwise
            if not result.success and not skill_config.get("continue_on_failure", False):
                console.print(f"[{C['red']}]Plan execution stopped due to failure[/]")
                break

        self.is_running = False

        # Show summary
        self._show_execution_summary()

        return self.results

    def _show_plan_overview(self, skills: list):
        """Show plan overview table."""
        table = Table(show_header=True, header_style=f"bold {C['pink']}")
        table.add_column("#", style=C['dim'], width=3)
        table.add_column("Skill", style=C['white'])
        table.add_column("Status", style=C['gray'])

        for idx, skill in enumerate(skills, 1):
            table.add_row(str(idx), skill.get("name", "unknown"), "pending")

        console.print(table)
        console.print()

    def _show_skill_progress(self, idx: int, total: int, skill_name: str, status: str):
        """Show skill progress."""
        pct = int((idx + 1) / total * 100)
        status_icons = {
            "pending": f"[{C['dim']}]○[/]",
            "running": f"[{C['amber']}]●[/]",
            "completed": f"[{C['green']}]✓[/]",
            "failed": f"[{C['red']}]✗[/]",
        }
        icon = status_icons.get(status, "○")

        console.print(f"{icon} [{C['white']}][{idx+1}/{total}][/] {skill_name} [{C['dim']}]({pct}%)[/]")

    def _show_checkpoint(self, idx: int, total: int):
        """Show checkpoint indicator."""
        console.print(f"[{C['green']}]  ↳ Checkpoint saved ({idx+1}/{total})[/]")

    def _show_execution_summary(self):
        """Show execution summary."""
        succeeded = sum(1 for r in self.results if r.success)
        failed = sum(1 for r in self.results if not r.success)
        total_time = sum(r.duration_seconds for r in self.results)

        console.print()
        console.print(Panel(
            f"[{C['green']}]{succeeded} succeeded[/]  [{C['red']}]{failed} failed[/]  [{C['dim']}]{total_time:.1f}s total[/]",
            title=f"[bold {C['amber']}]Execution Complete[/]",
            border_style=C['green'] if failed == 0 else C['red']
        ))

    def stop(self):
        """Stop execution."""
        self.is_running = False


class ProgressStreamer:
    """Streams execution progress to the console."""

    def __init__(self):
        self.current_task = None
        self.tasks = []

    def start_task(self, name: str, total: int = 100):
        """Start a new progress task."""
        self.current_task = {
            "name": name,
            "total": total,
            "current": 0,
            "status": "running"
        }
        self.tasks.append(self.current_task)
        self._render()

    def update(self, current: int = None, status: str = None, message: str = None):
        """Update current task progress."""
        if not self.current_task:
            return

        if current is not None:
            self.current_task["current"] = current
        if status is not None:
            self.current_task["status"] = status
        if message is not None:
            self.current_task["message"] = message

        self._render()

    def complete(self, status: str = "completed"):
        """Complete current task."""
        if self.current_task:
            self.current_task["status"] = status
            self.current_task["current"] = self.current_task["total"]
        self._render()

    def _render(self):
        """Render progress to console."""
        if not self.current_task:
            return

        task = self.current_task
        pct = int(task["current"] / task["total"] * 100) if task["total"] > 0 else 0
        bar_width = 20
        filled = int(bar_width * pct / 100)
        bar = "█" * filled + "░" * (bar_width - filled)

        status_colors = {
            "running": C['amber'],
            "completed": C['green'],
            "failed": C['red'],
        }
        color = status_colors.get(task["status"], C['gray'])

        msg = task.get("message", "")
        console.print(f"[{color}]{task['name']}[/] [{C['dim']}]{bar}[/] {pct}% {msg}", end="\r")

        if task["status"] in ["completed", "failed"]:
            console.print()  # New line after completion
