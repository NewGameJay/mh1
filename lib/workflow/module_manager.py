"""
Module Manager for MH1

Handles module folder creation, state management, and persistence.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
import yaml
import json

PROJECT_ROOT = Path(__file__).parent.parent.parent


class ModuleManager:
    """Manages module lifecycle: creation, state, execution tracking."""

    def __init__(self, client_id: str):
        self.client_id = client_id
        self.modules_dir = PROJECT_ROOT / "modules"
        self.templates_dir = self.modules_dir / "templates" / "_template"
        self.client_dir = PROJECT_ROOT / "clients" / client_id
        self.current_module = None
        self.current_module_path = None

    def create_module(self, name: str, description: str = "") -> dict:
        """
        Create a new module folder with templates.

        Args:
            name: Module name (will be slugified)
            description: Brief description of the module

        Returns:
            Dict with module info
        """
        # Generate module ID
        date_str = datetime.now().strftime("%Y%m%d")
        slug = self._slugify(name)
        module_id = f"{slug}-{date_str}"

        # Create module directory
        module_path = self.modules_dir / module_id
        module_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (module_path / "outputs").mkdir(exist_ok=True)
        (module_path / "inputs").mkdir(exist_ok=True)
        (module_path / "logs").mkdir(exist_ok=True)

        # Create MRD from template
        mrd_content = self._create_mrd_template(module_id, name, description)
        (module_path / "MRD.md").write_text(mrd_content)

        # Create plan from template
        plan_content = self._create_plan_template(module_id, name)
        (module_path / ".plan.md").write_text(plan_content)

        # Create README
        readme_content = self._create_readme(module_id, name, description)
        (module_path / "README.md").write_text(readme_content)

        # Create state file
        state = {
            "module_id": module_id,
            "name": name,
            "description": description,
            "client_id": self.client_id,
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "skills_planned": [],
            "skills_completed": [],
            "current_skill": None,
            "checkpoints": [],
        }
        (module_path / "state.json").write_text(json.dumps(state, indent=2))

        self.current_module = state
        self.current_module_path = module_path

        return {
            "module_id": module_id,
            "path": str(module_path),
            "mrd_path": str(module_path / "MRD.md"),
            "plan_path": str(module_path / ".plan.md"),
            "status": "created"
        }

    def _slugify(self, text: str) -> str:
        """Convert text to slug."""
        return text.lower().replace(" ", "-").replace("_", "-")[:50]

    def _create_mrd_template(self, module_id: str, name: str, description: str) -> str:
        """Generate MRD content."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return f"""# MRD: {name}

## Metadata
| Field | Value |
|-------|-------|
| Module ID | {module_id} |
| Client | {self.client_id} |
| Status | Draft |
| Priority | Medium |
| Owner | MH1 |
| Created | {date_str} |
| Updated | {date_str} |

---

## Executive Summary

{description or "[To be filled by Claude based on user request]"}

### Interpreted Task
[Claude will fill this with interpretation of user's request]

---

## Problem Statement

### What Changed?
[Context on why this module is needed]

### Why This Matters
[Business impact and urgency]

---

## Objectives

### Primary Goal
[Main objective to achieve]

### Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

---

## Scope

### In Scope
- Item 1
- Item 2

### Out of Scope
- Excluded item 1

---

## Inputs Required
- Input 1
- Input 2

---

## Expected Outputs
- Output 1
- Output 2

---

## Approach & Methodology

### Skills to Execute
1. skill-1 - Purpose
2. skill-2 - Purpose
3. skill-3 - Purpose

### Phase 1: Setup
- Validate input data availability
- Configure platform connections
- Initialize module workspace

### Phase 2: Execution
- Execute skills in dependency order
- Checkpoint after each skill
- Validate intermediate outputs

### Phase 3: Validation
- Run quality gates on outputs
- Verify success criteria met
- Generate final deliverables

---

## Dependencies & Blockers

### Critical Dependencies
- Dependency 1

### Known Blockers
- None identified

---

## Risk Assessment
- Risk 1: [description] - Mitigation: [approach]

---

## Success Metrics

### Quantitative
- Metric 1

### Qualitative
- Metric 1

---

## Constraints
- Budget: $XX
- Timeline: X days
- Resources: [limitations]

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {date_str} | MH1 | Initial MRD |
"""

    def _create_plan_template(self, module_id: str, name: str) -> str:
        """Generate execution plan content."""
        return f"""# Execution Plan: {name}

## Module Info
- **Module ID**: {module_id}
- **Client**: {self.client_id}
- **Status**: Pending Approval

---

## Pre-flight Checks
- [ ] Input data available
- [ ] Dependencies resolved
- [ ] Budget approved

---

## Skills to Execute

```yaml
skills:
  # Skills will be added here after council consensus
  # Example:
  # - name: skill-name
  #   inputs:
  #     param1: value
  #   checkpoint: true
  #   depends_on: null
```

---

## Execution Checkpoints

| # | Skill | Status | Started | Completed | Output |
|---|-------|--------|---------|-----------|--------|
| 1 | pending | - | - | - | - |

---

## Execution Log

<!-- Execution events will be logged here -->

---

## Resume Instructions

If execution is interrupted:
1. Check the last successful checkpoint above
2. Review any error logs
3. Resume from the next pending skill

---

## Notes

<!-- Add execution notes here -->
"""

    def _create_readme(self, module_id: str, name: str, description: str) -> str:
        """Generate README content."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return f"""# {name}

**Module ID:** {module_id}
**Client:** {self.client_id}
**Created:** {date_str}
**Status:** Draft

## Overview

{description or "Module description pending."}

## Files

- `MRD.md` - Marketing Requirements Document
- `.plan.md` - Execution plan with skill sequence
- `state.json` - Module state and progress
- `outputs/` - Final deliverables
- `inputs/` - Input data and uploads
- `logs/` - Execution logs

## Usage

This module was created by MH1. To execute:
1. Review and approve the MRD
2. Review and approve the execution plan
3. Run the module

## History

| Date | Event |
|------|-------|
| {date_str} | Module created |
"""

    def load_module(self, module_id: str) -> Optional[dict]:
        """Load an existing module."""
        module_path = self.modules_dir / module_id
        state_file = module_path / "state.json"

        if not state_file.exists():
            return None

        with open(state_file) as f:
            state = json.load(f)

        self.current_module = state
        self.current_module_path = module_path
        return state

    def update_state(self, updates: dict) -> dict:
        """Update module state."""
        if not self.current_module:
            raise ValueError("No module loaded")

        self.current_module.update(updates)
        self.current_module["updated_at"] = datetime.now().isoformat()

        state_file = self.current_module_path / "state.json"
        with open(state_file, "w") as f:
            json.dump(self.current_module, f, indent=2)

        return self.current_module

    def update_mrd(self, content: str) -> None:
        """Update MRD content."""
        if not self.current_module_path:
            raise ValueError("No module loaded")
        (self.current_module_path / "MRD.md").write_text(content)

    def update_plan(self, content: str) -> None:
        """Update plan content."""
        if not self.current_module_path:
            raise ValueError("No module loaded")
        (self.current_module_path / ".plan.md").write_text(content)

    def set_skills(self, skills: list) -> None:
        """Set the skills to execute."""
        self.update_state({
            "skills_planned": skills,
            "status": "planned"
        })

    def start_skill(self, skill_name: str) -> None:
        """Mark a skill as started."""
        self.update_state({
            "current_skill": skill_name,
            "status": "executing"
        })

    def complete_skill(self, skill_name: str, output: dict) -> None:
        """Mark a skill as completed."""
        completed = self.current_module.get("skills_completed", [])
        completed.append({
            "skill": skill_name,
            "completed_at": datetime.now().isoformat(),
            "output_summary": str(output)[:500]
        })

        checkpoints = self.current_module.get("checkpoints", [])
        checkpoints.append({
            "skill": skill_name,
            "timestamp": datetime.now().isoformat()
        })

        self.update_state({
            "skills_completed": completed,
            "checkpoints": checkpoints,
            "current_skill": None
        })

    def save_output(self, filename: str, content: str) -> str:
        """Save an output file."""
        if not self.current_module_path:
            raise ValueError("No module loaded")

        output_path = self.current_module_path / "outputs" / filename
        output_path.write_text(content)
        return str(output_path)

    def log_event(self, event: str) -> None:
        """Log an execution event."""
        if not self.current_module_path:
            return

        log_file = self.current_module_path / "logs" / "execution.log"
        timestamp = datetime.now().isoformat()
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] {event}\n")

    def get_status(self) -> dict:
        """Get current module status."""
        if not self.current_module:
            return {"status": "no_module"}

        planned = len(self.current_module.get("skills_planned", []))
        completed = len(self.current_module.get("skills_completed", []))

        return {
            "module_id": self.current_module.get("module_id"),
            "status": self.current_module.get("status"),
            "skills_planned": planned,
            "skills_completed": completed,
            "current_skill": self.current_module.get("current_skill"),
            "progress_pct": int((completed / planned * 100) if planned > 0 else 0)
        }


def ensure_client_dir(client_id: str) -> Path:
    """Ensure client directory exists and return path."""
    client_dir = PROJECT_ROOT / "clients" / client_id
    client_dir.mkdir(parents=True, exist_ok=True)
    (client_dir / "data").mkdir(exist_ok=True)
    (client_dir / "reports").mkdir(exist_ok=True)
    (client_dir / "config").mkdir(exist_ok=True)
    return client_dir


def save_client_data(client_id: str, filename: str, data: any) -> str:
    """Save data to client directory."""
    client_dir = ensure_client_dir(client_id)
    data_path = client_dir / "data" / filename

    if isinstance(data, (dict, list)):
        with open(data_path, "w") as f:
            json.dump(data, f, indent=2)
    else:
        data_path.write_text(str(data))

    return str(data_path)


def save_client_report(client_id: str, filename: str, content: str) -> str:
    """Save report to client directory."""
    client_dir = ensure_client_dir(client_id)
    report_path = client_dir / "reports" / filename
    report_path.write_text(content)
    return str(report_path)
