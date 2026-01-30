#!/usr/bin/env python3
"""
Migration Script: Convert flat skills/agents to folder structure

Usage:
    python scripts/migrate_to_folders.py --skills     # Migrate all skills
    python scripts/migrate_to_folders.py --agents     # Migrate all agents
    python scripts/migrate_to_folders.py --skill research-company  # Single skill
    python scripts/migrate_to_folders.py --dry-run    # Preview changes
"""

import os
import sys
import re
import yaml
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def parse_frontmatter(content: str) -> Tuple[Dict, str]:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith('---'):
        return {}, content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content

    try:
        frontmatter = yaml.safe_load(parts[1])
        body = parts[2].strip()
        return frontmatter or {}, body
    except yaml.YAMLError:
        return {}, content


def update_frontmatter(frontmatter: Dict, stages: List[Dict]) -> Dict:
    """Add stage configuration to frontmatter."""
    frontmatter['stages'] = stages
    frontmatter['updated'] = datetime.now().strftime('%Y-%m-%d')

    # Ensure required fields
    if 'version' not in frontmatter:
        frontmatter['version'] = '1.0.0'
    if 'category' not in frontmatter:
        frontmatter['category'] = 'general'

    return frontmatter


def extract_stages_from_body(body: str) -> List[Dict]:
    """Extract stage-like sections from skill body."""
    stages = []

    # Look for numbered sections or ## headers that indicate stages
    # Common patterns: "## Step 1", "## Phase 1", "### 1. Setup", etc.
    section_pattern = r'^##\s+(?:Step|Phase|Stage)?\s*(\d+)[:\.]?\s*(.+)$'

    current_stage = None
    current_content = []

    for line in body.split('\n'):
        match = re.match(section_pattern, line, re.IGNORECASE)
        if match:
            # Save previous stage
            if current_stage:
                current_stage['content'] = '\n'.join(current_content).strip()
                stages.append(current_stage)

            # Start new stage
            stage_num = int(match.group(1))
            stage_name = match.group(2).strip()
            current_stage = {
                'id': f"{stage_num:02d}-{slugify(stage_name)}",
                'name': stage_name,
                'description': '',
                'checkpoint': stage_num > 0,  # Stage 0 doesn't checkpoint
                'content': ''
            }
            current_content = []
        elif current_stage:
            current_content.append(line)

    # Don't forget the last stage
    if current_stage:
        current_stage['content'] = '\n'.join(current_content).strip()
        stages.append(current_stage)

    # If no stages found, create default structure
    if not stages:
        stages = [
            {'id': '00-setup', 'name': 'Setup & Validation', 'checkpoint': False},
            {'id': '01-process', 'name': 'Process', 'checkpoint': True},
            {'id': '02-output', 'name': 'Generate Output', 'checkpoint': False}
        ]

    return stages


def slugify(text: str) -> str:
    """Convert text to slug format."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')


def create_skill_folder_structure(skill_dir: Path, dry_run: bool = False) -> None:
    """Create subdirectory structure for a skill folder."""
    subdirs = ['config', 'scripts', 'stages', 'templates', 'references', 'references/examples']

    for subdir in subdirs:
        path = skill_dir / subdir
        if not dry_run:
            path.mkdir(parents=True, exist_ok=True)
        print(f"  {'Would create' if dry_run else 'Created'}: {path}")


def migrate_skill(skill_path: Path, dry_run: bool = False) -> bool:
    """
    Migrate a single skill from flat SKILL.md to folder structure.

    Args:
        skill_path: Path to SKILL.md file
        dry_run: If True, only print what would be done

    Returns:
        True if migration successful
    """
    skill_dir = skill_path.parent
    skill_name = skill_dir.name

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Migrating skill: {skill_name}")

    # Read existing SKILL.md
    content = skill_path.read_text()
    frontmatter, body = parse_frontmatter(content)

    # Create folder structure
    create_skill_folder_structure(skill_dir, dry_run)

    # Extract stages from body
    stages = extract_stages_from_body(body)
    print(f"  Found {len(stages)} stages")

    # Write stage files
    for stage in stages:
        if 'content' in stage and stage['content']:
            stage_file = skill_dir / 'stages' / f"{stage['id']}.md"
            stage_content = f"# Stage: {stage['name']}\n\n{stage['content']}"

            if not dry_run:
                stage_file.write_text(stage_content)
            print(f"  {'Would write' if dry_run else 'Wrote'}: {stage_file.name}")

    # Update frontmatter with stages
    stage_refs = [{'id': s['id'], 'name': s['name'], 'checkpoint': s.get('checkpoint', True)}
                  for s in stages]
    updated_frontmatter = update_frontmatter(frontmatter, stage_refs)

    # Write updated SKILL.md (without stage content in body)
    new_content = f"---\n{yaml.dump(updated_frontmatter, default_flow_style=False)}---\n\n{body}"

    if not dry_run:
        skill_path.write_text(new_content)
    print(f"  {'Would update' if dry_run else 'Updated'}: SKILL.md")

    # Create default config files
    default_config = {
        'batch_size': 500,
        'max_retries': 2,
        'timeout_seconds': 1800,
        'min_confidence': 0.7
    }

    config_file = skill_dir / 'config' / 'defaults.yaml'
    if not dry_run:
        config_file.write_text(yaml.dump(default_config, default_flow_style=False))
    print(f"  {'Would create' if dry_run else 'Created'}: config/defaults.yaml")

    return True


def migrate_agent(agent_path: Path, dry_run: bool = False) -> bool:
    """
    Migrate a single agent from flat .md to folder structure.

    Args:
        agent_path: Path to agent .md file
        dry_run: If True, only print what would be done

    Returns:
        True if migration successful
    """
    agent_name = agent_path.stem
    agent_type_dir = agent_path.parent
    new_agent_dir = agent_type_dir / agent_name

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Migrating agent: {agent_name}")

    # Create folder structure
    subdirs = [
        'Training/approaches',
        'Training/references/platform-docs',
        'Training/examples/successful',
        'Training/examples/failures',
        'Evaluation/test-cases'
    ]

    for subdir in subdirs:
        path = new_agent_dir / subdir
        if not dry_run:
            path.mkdir(parents=True, exist_ok=True)
        print(f"  {'Would create' if dry_run else 'Created'}: {path}")

    # Move original .md to AGENT.md in new folder
    new_agent_file = new_agent_dir / 'AGENT.md'
    if not dry_run:
        shutil.copy(agent_path, new_agent_file)
        agent_path.unlink()  # Remove original
    print(f"  {'Would move' if dry_run else 'Moved'}: {agent_path.name} -> {agent_name}/AGENT.md")

    # Create default rubric
    rubric_content = """# Agent Evaluation Rubric
name: {name}-evaluation
version: 1.0.0
min_passing_score: 0.8

weights:
  accuracy: 0.25
  completeness: 0.20
  relevance: 0.20
  voice_match: 0.15
  actionability: 0.10
  efficiency: 0.10
""".format(name=agent_name)

    rubric_file = new_agent_dir / 'Evaluation' / 'rubric.yaml'
    if not dry_run:
        rubric_file.write_text(rubric_content)
    print(f"  {'Would create' if dry_run else 'Created'}: Evaluation/rubric.yaml")

    return True


def find_skills(skills_dir: Path) -> List[Path]:
    """Find all SKILL.md files that need migration."""
    skills = []
    for skill_path in skills_dir.glob('*/SKILL.md'):
        # Check if already migrated (has stages/ folder)
        if not (skill_path.parent / 'stages').exists():
            skills.append(skill_path)
    return skills


def find_agents(agents_dir: Path) -> List[Path]:
    """Find all agent .md files that need migration."""
    agents = []
    for agent_type_dir in agents_dir.iterdir():
        if agent_type_dir.is_dir():
            for agent_path in agent_type_dir.glob('*.md'):
                # Skip if it's already in a folder structure (AGENT.md)
                if agent_path.name != 'AGENT.md':
                    agents.append(agent_path)
    return agents


def main():
    parser = argparse.ArgumentParser(description='Migrate skills/agents to folder structure')
    parser.add_argument('--skills', action='store_true', help='Migrate all skills')
    parser.add_argument('--agents', action='store_true', help='Migrate all agents')
    parser.add_argument('--skill', type=str, help='Migrate specific skill by name')
    parser.add_argument('--agent', type=str, help='Migrate specific agent by name')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without making them')

    args = parser.parse_args()

    skills_dir = PROJECT_ROOT / 'skills'
    agents_dir = PROJECT_ROOT / 'agents'

    if args.skill:
        skill_path = skills_dir / args.skill / 'SKILL.md'
        if skill_path.exists():
            migrate_skill(skill_path, args.dry_run)
        else:
            print(f"Skill not found: {args.skill}")
            sys.exit(1)

    elif args.agent:
        # Search for agent in all type directories
        found = False
        for agent_type_dir in agents_dir.iterdir():
            if agent_type_dir.is_dir():
                agent_path = agent_type_dir / f"{args.agent}.md"
                if agent_path.exists():
                    migrate_agent(agent_path, args.dry_run)
                    found = True
                    break
        if not found:
            print(f"Agent not found: {args.agent}")
            sys.exit(1)

    elif args.skills:
        skills = find_skills(skills_dir)
        print(f"Found {len(skills)} skills to migrate")
        for skill_path in skills:
            migrate_skill(skill_path, args.dry_run)

    elif args.agents:
        agents = find_agents(agents_dir)
        print(f"Found {len(agents)} agents to migrate")
        for agent_path in agents:
            migrate_agent(agent_path, args.dry_run)

    else:
        parser.print_help()
        print("\nExamples:")
        print("  python scripts/migrate_to_folders.py --skills --dry-run")
        print("  python scripts/migrate_to_folders.py --skill research-company")
        print("  python scripts/migrate_to_folders.py --agents")


if __name__ == '__main__':
    main()
