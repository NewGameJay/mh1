#!/usr/bin/env python3
"""
Validate SKILL.md files against AgentSkills.io + MH1 schema.

Usage:
    python scripts/validate_skill.py skills/ghostwrite-content
    python scripts/validate_skill.py --all
    python scripts/validate_skill.py --all --fix-triggers
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def load_schema() -> Dict:
    """Load the frontmatter JSON schema."""
    schema_path = Path(__file__).parent.parent / "schemas" / "skill-frontmatter.json"
    if not schema_path.exists():
        print(f"{Colors.RED}Error: Schema not found at {schema_path}{Colors.RESET}")
        sys.exit(1)
    
    with open(schema_path) as f:
        return json.load(f)

def extract_frontmatter(skill_path: Path) -> Tuple[Optional[Dict], str, List[str]]:
    """
    Extract YAML frontmatter from SKILL.md file.
    
    Returns:
        Tuple of (frontmatter_dict, body_content, errors)
    """
    skill_file = skill_path / "SKILL.md"
    if not skill_file.exists():
        return None, "", [f"SKILL.md not found in {skill_path}"]
    
    content = skill_file.read_text()
    errors = []
    
    # Check for YAML frontmatter (--- ... ---)
    yaml_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    
    if yaml_match:
        yaml_content = yaml_match.group(1)
        body = yaml_match.group(2)
        try:
            frontmatter = yaml.safe_load(yaml_content)
            return frontmatter, body, []
        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML frontmatter: {e}")
            return None, content, errors
    
    # No YAML frontmatter - try to parse old format
    errors.append("No YAML frontmatter found (missing ---)")
    
    # Try to extract old-style metadata
    old_format = {}
    
    # Look for "# Skill: [name]" pattern
    name_match = re.search(r'^#\s*Skill:\s*(.+)$', content, re.MULTILINE)
    if name_match:
        old_format['name'] = name_match.group(1).strip().lower().replace(' ', '-')
    
    # Look for Version: pattern
    version_match = re.search(r'^Version:\s*v?(.+)$', content, re.MULTILINE)
    if version_match:
        if 'metadata' not in old_format:
            old_format['metadata'] = {}
        old_format['metadata']['version'] = version_match.group(1).strip()
    
    # Look for Status: pattern
    status_match = re.search(r'^Status:\s*(.+)$', content, re.MULTILINE)
    if status_match:
        if 'metadata' not in old_format:
            old_format['metadata'] = {}
        old_format['metadata']['status'] = status_match.group(1).strip().split('|')[0].strip()
    
    # Look for ## Purpose section for description
    purpose_match = re.search(r'^## Purpose\n+(.+?)(?=\n#|\n---|\Z)', content, re.MULTILINE | re.DOTALL)
    if purpose_match:
        purpose_text = purpose_match.group(1).strip()
        # Take first paragraph only
        old_format['description'] = purpose_text.split('\n\n')[0][:500]
    
    if old_format:
        errors.append("Found old-format metadata - migration needed")
        return old_format, content, errors
    
    return None, content, errors

def validate_frontmatter(frontmatter: Dict, schema: Dict) -> List[str]:
    """Validate frontmatter against schema."""
    errors = []
    
    # Check required fields
    for field in schema.get('required', []):
        if field not in frontmatter:
            errors.append(f"Missing required field: {field}")
    
    # Validate name format
    if 'name' in frontmatter:
        name_pattern = schema['properties']['name'].get('pattern', '')
        if name_pattern and not re.match(name_pattern, frontmatter['name']):
            errors.append(f"Invalid name format: '{frontmatter['name']}' (must be lowercase with hyphens)")
    
    # Validate description length
    if 'description' in frontmatter:
        desc = frontmatter['description']
        min_len = schema['properties']['description'].get('minLength', 0)
        max_len = schema['properties']['description'].get('maxLength', 1000)
        
        if len(desc) < min_len:
            errors.append(f"Description too short: {len(desc)} chars (min {min_len})")
        if len(desc) > max_len:
            errors.append(f"Description too long: {len(desc)} chars (max {max_len})")
    
    # Validate license
    if 'license' in frontmatter:
        valid_licenses = schema['properties']['license'].get('enum', [])
        if frontmatter['license'] not in valid_licenses:
            errors.append(f"Invalid license: '{frontmatter['license']}' (valid: {valid_licenses})")
    
    # Validate metadata.version format
    if 'metadata' in frontmatter and 'version' in frontmatter['metadata']:
        version_pattern = schema['properties']['metadata']['properties']['version'].get('pattern', '')
        if version_pattern and not re.match(version_pattern, frontmatter['metadata']['version']):
            errors.append(f"Invalid version format: '{frontmatter['metadata']['version']}' (must be X.Y.Z)")
    
    # Validate metadata.status
    if 'metadata' in frontmatter and 'status' in frontmatter['metadata']:
        valid_statuses = schema['properties']['metadata']['properties']['status'].get('enum', [])
        if frontmatter['metadata']['status'] not in valid_statuses:
            errors.append(f"Invalid status: '{frontmatter['metadata']['status']}' (valid: {valid_statuses})")
    
    # Validate compatibility is array (if present)
    if 'compatibility' in frontmatter:
        if not isinstance(frontmatter['compatibility'], list):
            errors.append(f"compatibility must be an array, got {type(frontmatter['compatibility']).__name__}")
    
    # Validate metadata.tags is array (if present)
    if 'metadata' in frontmatter and 'tags' in frontmatter['metadata']:
        if not isinstance(frontmatter['metadata']['tags'], list):
            errors.append(f"metadata.tags must be an array, got {type(frontmatter['metadata']['tags']).__name__}")
    
    return errors

def check_trigger_phrases(description: str) -> Tuple[bool, List[str]]:
    """Check if description contains trigger phrases."""
    warnings = []
    
    # Look for "Use when" pattern
    has_trigger = 'use when' in description.lower()
    
    if not has_trigger:
        warnings.append("Description missing 'Use when' trigger phrases")
    
    # Count quoted triggers
    triggers = re.findall(r"'([^']+)'", description)
    if len(triggers) < 2:
        warnings.append(f"Only {len(triggers)} trigger phrases found (recommend 3+)")
    
    return has_trigger, warnings

def check_body_structure(body: str) -> List[str]:
    """Check that body has recommended sections."""
    warnings = []
    
    recommended_sections = [
        "## When to Use",
        "## Inputs",
        "## Outputs",
        "## Process",
    ]
    
    optional_sections = [
        "## Dependencies",
        "## Quality criteria",
        "## Context handling",
        "## SLA",
    ]
    
    for section in recommended_sections:
        if section.lower() not in body.lower():
            warnings.append(f"Missing recommended section: {section}")
    
    return warnings

def validate_skill(skill_path: Path, schema: Dict, verbose: bool = False) -> Tuple[bool, List[str], List[str]]:
    """
    Validate a single skill.
    
    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    errors = []
    warnings = []
    
    # Extract frontmatter
    frontmatter, body, extract_errors = extract_frontmatter(skill_path)
    errors.extend(extract_errors)
    
    if frontmatter is None:
        return False, errors, warnings
    
    # Validate frontmatter
    fm_errors = validate_frontmatter(frontmatter, schema)
    errors.extend(fm_errors)
    
    # Check trigger phrases
    if 'description' in frontmatter:
        has_triggers, trigger_warnings = check_trigger_phrases(frontmatter['description'])
        warnings.extend(trigger_warnings)
    
    # Check body structure
    body_warnings = check_body_structure(body)
    warnings.extend(body_warnings)
    
    is_valid = len(errors) == 0
    return is_valid, errors, warnings

def find_all_skills(base_path: Path) -> List[Path]:
    """Find all skill directories."""
    skills_dir = base_path / "skills"
    skills = []
    
    for item in skills_dir.iterdir():
        if item.is_dir() and not item.name.startswith('_'):
            skill_file = item / "SKILL.md"
            if skill_file.exists():
                skills.append(item)
    
    return sorted(skills)

def print_result(skill_name: str, is_valid: bool, errors: List[str], warnings: List[str], verbose: bool):
    """Print validation result for a skill."""
    if is_valid:
        status = f"{Colors.GREEN}PASS{Colors.RESET}"
    else:
        status = f"{Colors.RED}FAIL{Colors.RESET}"
    
    print(f"  {status} {skill_name}")
    
    if verbose or not is_valid:
        for error in errors:
            print(f"       {Colors.RED}ERROR:{Colors.RESET} {error}")
    
    if verbose and warnings:
        for warning in warnings:
            print(f"       {Colors.YELLOW}WARN:{Colors.RESET} {warning}")

def generate_migration_suggestion(skill_path: Path) -> str:
    """Generate YAML frontmatter suggestion for old-format skill."""
    frontmatter, body, _ = extract_frontmatter(skill_path)
    
    if frontmatter is None:
        frontmatter = {}
    
    skill_name = skill_path.name
    
    # Build suggested frontmatter
    suggestion = {
        'name': frontmatter.get('name', skill_name),
        'description': frontmatter.get('description', f"[FILL IN] Description for {skill_name}. Use when asked to '[trigger 1]', '[trigger 2]', '[trigger 3]'."),
        'license': 'Proprietary',
        'metadata': {
            'author': 'mh1-engineering',
            'version': frontmatter.get('metadata', {}).get('version', '1.0.0'),
            'status': frontmatter.get('metadata', {}).get('status', 'active'),
        }
    }
    
    yaml_str = yaml.dump(suggestion, default_flow_style=False, sort_keys=False)
    return f"---\n{yaml_str}---\n"

def main():
    parser = argparse.ArgumentParser(description='Validate SKILL.md files')
    parser.add_argument('path', nargs='?', help='Path to skill directory')
    parser.add_argument('--all', action='store_true', help='Validate all skills')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show warnings')
    parser.add_argument('--suggest', action='store_true', help='Generate migration suggestions')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # Load schema
    schema = load_schema()
    
    # Determine which skills to validate
    base_path = Path(__file__).parent.parent
    
    if args.all:
        skills = find_all_skills(base_path)
    elif args.path:
        skill_path = Path(args.path)
        if not skill_path.is_absolute():
            skill_path = base_path / args.path
        skills = [skill_path]
    else:
        parser.print_help()
        sys.exit(1)
    
    # Validate skills
    results = []
    total = len(skills)
    passed = 0
    
    print(f"\n{Colors.BOLD}Validating {total} skill(s)...{Colors.RESET}\n")
    
    for skill_path in skills:
        is_valid, errors, warnings = validate_skill(skill_path, schema, args.verbose)
        
        if is_valid:
            passed += 1
        
        results.append({
            'name': skill_path.name,
            'path': str(skill_path),
            'valid': is_valid,
            'errors': errors,
            'warnings': warnings,
        })
        
        if not args.json:
            print_result(skill_path.name, is_valid, errors, warnings, args.verbose)
            
            if args.suggest and not is_valid:
                print(f"\n       {Colors.BLUE}Suggested frontmatter:{Colors.RESET}")
                suggestion = generate_migration_suggestion(skill_path)
                for line in suggestion.split('\n'):
                    print(f"       {line}")
                print()
    
    # Output results
    if args.json:
        print(json.dumps({
            'total': total,
            'passed': passed,
            'failed': total - passed,
            'results': results
        }, indent=2))
    else:
        print(f"\n{Colors.BOLD}Summary:{Colors.RESET}")
        print(f"  {Colors.GREEN}Passed:{Colors.RESET} {passed}/{total}")
        print(f"  {Colors.RED}Failed:{Colors.RESET} {total - passed}/{total}")
        
        if passed == total:
            print(f"\n{Colors.GREEN}{Colors.BOLD}All skills validated successfully!{Colors.RESET}")
        else:
            print(f"\n{Colors.YELLOW}Run with --suggest to see migration suggestions{Colors.RESET}")
    
    sys.exit(0 if passed == total else 1)

if __name__ == '__main__':
    main()
