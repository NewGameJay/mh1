"""
MH1 Skill Registry
Introspection layer to discover, validate, and manage skills.
The "Brain" that knows what the system can do.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

SYSTEM_ROOT = Path(__file__).parent.parent
SKILLS_DIR = SYSTEM_ROOT / "skills"

@dataclass
class SkillMetadata:
    name: str
    path: str
    version: str
    description: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    dependencies: List[str]
    deprecated: bool = False

class SkillRegistry:
    """
    Manages the catalog of available skills.
    """
    
    def __init__(self):
        self.skills: Dict[str, SkillMetadata] = {}
        self.refresh()

    def refresh(self):
        """Scan the skills directory and rebuild registry."""
        self.skills = {}
        
        if not SKILLS_DIR.exists():
            return

        for skill_dir in SKILLS_DIR.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith('_'):
                self._load_skill(skill_dir)

    def _load_skill(self, skill_dir: Path):
        """Parse SKILL.md and schemas to load skill metadata."""
        skill_name = skill_dir.name
        skill_md = skill_dir / "SKILL.md"
        
        if not skill_md.exists():
            return

        # Basic parsing of SKILL.md (in a real implementation, use a proper Markdown parser)
        content = skill_md.read_text()
        
        # Extract version
        version = "unknown"
        for line in content.split('\n'):
            if line.strip().startswith("Version:"):
                version = line.split(":", 1)[1].strip()
                break
        
        # Extract description (naive)
        description = "No description provided."
        
        # Load inputs schema
        input_schema = {}
        input_file = skill_dir / "schemas" / "input.json"
        if input_file.exists():
            try:
                input_schema = json.loads(input_file.read_text())
            except:
                pass

        # Load outputs schema
        output_schema = {}
        output_file = skill_dir / "schemas" / "output.json"
        if output_file.exists():
            try:
                output_schema = json.loads(output_file.read_text())
            except:
                pass

        self.skills[skill_name] = SkillMetadata(
            name=skill_name,
            path=str(skill_dir),
            version=version,
            description=description,
            inputs=input_schema,
            outputs=output_schema,
            dependencies=[], # TODO: Parse dependencies
            deprecated="deprecated" in content.lower() and "status: deprecated" in content.lower()
        )

    def list_skills(self) -> List[SkillMetadata]:
        """Return list of all skills."""
        return list(self.skills.values())

    def get_skill(self, name: str) -> Optional[SkillMetadata]:
        """Get metadata for a specific skill."""
        return self.skills.get(name)

    def find_skills_for_task(self, task_description: str) -> List[SkillMetadata]:
        """
        Semantic search for skills relevant to a task.
        (Placeholder for embedding-based search)
        """
        # Simple keyword matching for now
        matches = []
        task_words = set(task_description.lower().split())
        
        for skill in self.skills.values():
            skill_words = set(skill.name.replace('-', ' ').split())
            if task_words & skill_words:
                matches.append(skill)
        
        return matches

# Factory
def get_registry() -> SkillRegistry:
    return SkillRegistry()
