#!/usr/bin/env python3
"""
Comprehensive skill validation script for MH1.

Validates all SKILL.md files against the frontmatter schema and checks:
- YAML frontmatter required fields (name, description, version, status)
- Skill name matches folder name
- Referenced workflows, schemas, and scripts exist
- Body structure (recommended sections)
- Trigger phrases in description

Usage:
    python scripts/validate_skills.py
    python scripts/validate_skills.py --verbose
    python scripts/validate_skills.py --skill lifecycle-audit
    python scripts/validate_skills.py --output custom_report.json

Output:
    telemetry/skill_validation_report.json
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)

try:
    import jsonschema
    from jsonschema import Draft7Validator
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    print("Warning: jsonschema not installed. Schema validation will be limited.")
    print("Install with: pip install jsonschema")


# Project root (parent of scripts directory)
PROJECT_ROOT = Path(__file__).parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"
SCHEMAS_DIR = PROJECT_ROOT / "schemas"
WORKFLOWS_DIR = PROJECT_ROOT / "workflows"
AGENTS_DIR = PROJECT_ROOT / "agents"
TELEMETRY_DIR = PROJECT_ROOT / "telemetry"
DEFAULT_OUTPUT = TELEMETRY_DIR / "skill_validation_report.json"


@dataclass
class ValidationIssue:
    """Represents a single validation issue."""
    severity: str  # "error", "warning", "info"
    code: str
    message: str
    field: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class SkillValidationResult:
    """Validation result for a single skill."""
    name: str
    folder_name: str
    path: str
    valid: bool
    has_frontmatter: bool
    frontmatter: Optional[Dict[str, Any]] = None
    issues: List[ValidationIssue] = field(default_factory=list)

    # Extracted metadata for reporting
    version: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    # Reference validation
    referenced_schemas: List[str] = field(default_factory=list)
    referenced_workflows: List[str] = field(default_factory=list)
    referenced_scripts: List[str] = field(default_factory=list)
    referenced_agents: List[str] = field(default_factory=list)
    missing_references: List[str] = field(default_factory=list)

    def add_error(self, code: str, message: str, field: str = None, suggestion: str = None):
        self.issues.append(ValidationIssue("error", code, message, field, suggestion))
        self.valid = False

    def add_warning(self, code: str, message: str, field: str = None, suggestion: str = None):
        self.issues.append(ValidationIssue("warning", code, message, field, suggestion))

    def add_info(self, code: str, message: str, field: str = None):
        self.issues.append(ValidationIssue("info", code, message, field))

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")


@dataclass
class ValidationReport:
    """Complete validation report."""
    timestamp: str
    total_skills: int
    valid_skills: int
    invalid_skills: int
    total_errors: int
    total_warnings: int
    skills: List[Dict[str, Any]] = field(default_factory=list)
    summary_by_status: Dict[str, int] = field(default_factory=dict)
    summary_by_category: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "total_skills": self.total_skills,
            "valid_skills": self.valid_skills,
            "invalid_skills": self.invalid_skills,
            "total_errors": self.total_errors,
            "total_warnings": self.total_warnings,
            "pass_rate": round(self.valid_skills / self.total_skills * 100, 1) if self.total_skills > 0 else 0,
            "summary_by_status": self.summary_by_status,
            "summary_by_category": self.summary_by_category,
            "skills": self.skills
        }


class SkillValidator:
    """Validates SKILL.md files against schema and conventions."""

    REQUIRED_FIELDS = ["name", "description"]
    RECOMMENDED_FIELDS = ["version", "status"]

    REQUIRED_BODY_SECTIONS = [
        "## When to Use",
        "## Inputs",
        "## Outputs",
    ]

    RECOMMENDED_BODY_SECTIONS = [
        "## Process",
        "## Dependencies",
        "## Quality Criteria",
    ]

    VALID_STATUSES = ["active", "deprecated", "experimental"]
    VALID_LICENSES = ["MIT", "Apache-2.0", "Proprietary", "UNLICENSED"]

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.schema = self._load_schema()
        self.validator = None
        if HAS_JSONSCHEMA and self.schema:
            self.validator = Draft7Validator(self.schema)

    def _load_schema(self) -> Optional[Dict]:
        """Load the frontmatter JSON schema."""
        schema_path = SCHEMAS_DIR / "skill-frontmatter.json"
        if not schema_path.exists():
            print(f"Warning: Schema not found at {schema_path}")
            return None

        try:
            with open(schema_path) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON in schema: {e}")
            return None

    def extract_frontmatter(self, skill_path: Path) -> Tuple[Optional[Dict], str, List[str]]:
        """Extract YAML frontmatter from SKILL.md file."""
        skill_file = skill_path / "SKILL.md"
        if not skill_file.exists():
            return None, "", ["SKILL.md not found"]

        content = skill_file.read_text()
        errors = []

        # Check for YAML frontmatter (--- ... ---)
        yaml_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)

        if yaml_match:
            yaml_content = yaml_match.group(1)
            body = yaml_match.group(2)
            try:
                frontmatter = yaml.safe_load(yaml_content)
                if not isinstance(frontmatter, dict):
                    return None, body, ["Frontmatter is not a valid YAML object"]
                return frontmatter, body, []
            except yaml.YAMLError as e:
                return None, content, [f"Invalid YAML frontmatter: {e}"]

        return None, content, ["No YAML frontmatter found (missing --- delimiters)"]

    def validate_frontmatter_schema(self, frontmatter: Dict, result: SkillValidationResult):
        """Validate frontmatter against JSON schema."""
        if not self.validator:
            return

        errors = list(self.validator.iter_errors(frontmatter))
        for error in errors:
            field_path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else None
            result.add_error(
                "SCHEMA_VIOLATION",
                error.message,
                field=field_path
            )

    def validate_required_fields(self, frontmatter: Dict, result: SkillValidationResult):
        """Check for required fields."""
        # Check top-level required fields
        for field in self.REQUIRED_FIELDS:
            if field not in frontmatter:
                result.add_error(
                    "MISSING_REQUIRED_FIELD",
                    f"Missing required field: {field}",
                    field=field,
                    suggestion=f"Add '{field}' to frontmatter"
                )

        # Check for version (can be top-level or in metadata)
        version = frontmatter.get("version") or (frontmatter.get("metadata", {}).get("version"))
        if not version:
            result.add_warning(
                "MISSING_VERSION",
                "Version not specified",
                field="version",
                suggestion="Add 'version: \"1.0.0\"' or 'metadata.version: \"1.0.0\"'"
            )
        else:
            result.version = version
            # Validate semver format
            if not re.match(r'^\d+\.\d+\.\d+$', str(version)):
                result.add_error(
                    "INVALID_VERSION_FORMAT",
                    f"Version '{version}' is not valid semver (X.Y.Z)",
                    field="version",
                    suggestion="Use semantic versioning format: X.Y.Z"
                )

        # Check for status (can be top-level or in metadata)
        status = frontmatter.get("status") or (frontmatter.get("metadata", {}).get("status"))
        if not status:
            result.add_warning(
                "MISSING_STATUS",
                "Status not specified, defaulting to 'active'",
                field="status",
                suggestion="Add 'metadata.status: active'"
            )
            result.status = "active"
        else:
            result.status = status
            if status not in self.VALID_STATUSES:
                result.add_error(
                    "INVALID_STATUS",
                    f"Invalid status '{status}'. Must be one of: {self.VALID_STATUSES}",
                    field="status"
                )

    def validate_name_matches_folder(self, frontmatter: Dict, folder_name: str, result: SkillValidationResult):
        """Check that skill name matches folder name."""
        skill_name = frontmatter.get("name", "")
        if skill_name != folder_name:
            result.add_error(
                "NAME_FOLDER_MISMATCH",
                f"Skill name '{skill_name}' does not match folder name '{folder_name}'",
                field="name",
                suggestion=f"Change name to '{folder_name}' or rename folder to '{skill_name}'"
            )

        # Validate name format
        if skill_name and not re.match(r'^[a-z][a-z0-9-]*$', skill_name):
            result.add_error(
                "INVALID_NAME_FORMAT",
                f"Invalid name format: '{skill_name}'. Must be lowercase with hyphens only.",
                field="name",
                suggestion="Use lowercase letters, numbers, and hyphens only"
            )

    def validate_description(self, frontmatter: Dict, result: SkillValidationResult):
        """Validate description field."""
        description = frontmatter.get("description", "")
        if not description:
            return

        result.description = description[:200] + "..." if len(description) > 200 else description

        # Check minimum length
        if len(description) < 20:
            result.add_error(
                "DESCRIPTION_TOO_SHORT",
                f"Description is too short ({len(description)} chars, minimum 20)",
                field="description"
            )

        # Check for trigger phrases
        if "use when" not in description.lower():
            result.add_warning(
                "MISSING_TRIGGER_PHRASES",
                "Description should include 'Use when' trigger phrases",
                field="description",
                suggestion="Add: Use when asked to 'trigger 1', 'trigger 2', 'trigger 3'."
            )

        # Count quoted triggers
        triggers = re.findall(r"'([^']+)'", description)
        if len(triggers) < 2:
            result.add_info(
                "FEW_TRIGGER_PHRASES",
                f"Only {len(triggers)} trigger phrases found (recommend 3+)",
                field="description"
            )

    def validate_body_sections(self, body: str, result: SkillValidationResult):
        """Check that body has recommended sections."""
        body_lower = body.lower()

        for section in self.REQUIRED_BODY_SECTIONS:
            if section.lower() not in body_lower:
                result.add_warning(
                    "MISSING_BODY_SECTION",
                    f"Missing recommended section: {section}",
                    suggestion=f"Add '{section}' section to document body"
                )

        for section in self.RECOMMENDED_BODY_SECTIONS:
            if section.lower() not in body_lower:
                result.add_info(
                    "MISSING_OPTIONAL_SECTION",
                    f"Missing optional section: {section}"
                )

    def validate_references(self, frontmatter: Dict, body: str, skill_path: Path, result: SkillValidationResult):
        """Check that referenced files exist."""
        # Check schemas referenced in frontmatter
        self._check_schema_references(frontmatter, skill_path, result)

        # Check workflows referenced in body
        self._check_workflow_references(body, result)

        # Check scripts referenced
        self._check_script_references(frontmatter, skill_path, result)

        # Check agent references
        self._check_agent_references(frontmatter, result)

        # Check required resources
        self._check_resource_references(frontmatter, result)

    def _check_schema_references(self, frontmatter: Dict, skill_path: Path, result: SkillValidationResult):
        """Check schema file references."""
        schemas_to_check = []

        # Check inputs/outputs for schema references
        for input_def in frontmatter.get("inputs", []):
            if "schema" in input_def:
                schemas_to_check.append(input_def["schema"])

        for output_def in frontmatter.get("outputs", []):
            if "schema" in output_def:
                schemas_to_check.append(output_def["schema"])

        # Check quality_gates for schema references
        for gate in frontmatter.get("quality_gates", []):
            if "schema" in gate:
                schemas_to_check.append(gate["schema"])

        for schema_ref in schemas_to_check:
            result.referenced_schemas.append(schema_ref)

            # Schema could be relative to skill or absolute
            schema_path = skill_path / schema_ref
            if not schema_path.exists():
                schema_path = PROJECT_ROOT / schema_ref

            if not schema_path.exists():
                result.missing_references.append(f"schema:{schema_ref}")
                result.add_error(
                    "MISSING_SCHEMA",
                    f"Referenced schema not found: {schema_ref}",
                    suggestion=f"Create {schema_ref} or fix the path"
                )

    def _check_workflow_references(self, body: str, result: SkillValidationResult):
        """Check workflow references in body."""
        # Look for workflow references like "workflows/templates/something.md"
        workflow_refs = re.findall(r'workflows/[a-zA-Z0-9_/-]+\.(?:md|yaml)', body)

        for ref in workflow_refs:
            result.referenced_workflows.append(ref)
            if not (PROJECT_ROOT / ref).exists():
                result.missing_references.append(f"workflow:{ref}")
                result.add_warning(
                    "MISSING_WORKFLOW",
                    f"Referenced workflow not found: {ref}"
                )

    def _check_script_references(self, frontmatter: Dict, skill_path: Path, result: SkillValidationResult):
        """Check script references."""
        # Check requires_resources for script references
        for resource in frontmatter.get("requires_resources", []):
            if resource.endswith(".py") or resource.endswith(".sh"):
                result.referenced_scripts.append(resource)

                # Check relative to project root
                if not (PROJECT_ROOT / resource).exists():
                    result.missing_references.append(f"script:{resource}")
                    result.add_warning(
                        "MISSING_SCRIPT",
                        f"Referenced script not found: {resource}"
                    )

    def _check_agent_references(self, frontmatter: Dict, result: SkillValidationResult):
        """Check agent definition references."""
        for agent in frontmatter.get("requires_agents", []):
            result.referenced_agents.append(agent)

            # Look for agent definition in agents/ directory
            agent_paths = [
                AGENTS_DIR / "workers" / f"{agent}.md",
                AGENTS_DIR / "orchestrators" / f"{agent}.md",
                AGENTS_DIR / "evaluators" / f"{agent}.md",
            ]

            if not any(p.exists() for p in agent_paths):
                result.missing_references.append(f"agent:{agent}")
                result.add_warning(
                    "MISSING_AGENT",
                    f"Referenced agent not found: {agent}",
                    suggestion=f"Create agents/workers/{agent}.md"
                )

    def _check_resource_references(self, frontmatter: Dict, result: SkillValidationResult):
        """Check required resource references."""
        for resource in frontmatter.get("requires_resources", []):
            # Skip scripts (handled separately)
            if resource.endswith(".py") or resource.endswith(".sh"):
                continue

            if not (PROJECT_ROOT / resource).exists():
                result.missing_references.append(f"resource:{resource}")
                result.add_warning(
                    "MISSING_RESOURCE",
                    f"Referenced resource not found: {resource}"
                )

    def extract_tags(self, frontmatter: Dict) -> List[str]:
        """Extract tags from frontmatter."""
        tags = frontmatter.get("tags", [])
        if not tags:
            tags = frontmatter.get("metadata", {}).get("tags", [])
        return tags if isinstance(tags, list) else []

    def extract_category(self, frontmatter: Dict) -> Optional[str]:
        """Extract category from frontmatter."""
        return frontmatter.get("category")

    def validate_skill(self, skill_path: Path) -> SkillValidationResult:
        """Validate a single skill directory."""
        folder_name = skill_path.name
        result = SkillValidationResult(
            name=folder_name,
            folder_name=folder_name,
            path=str(skill_path),
            valid=True,
            has_frontmatter=False
        )

        # Extract frontmatter
        frontmatter, body, extract_errors = self.extract_frontmatter(skill_path)

        for error in extract_errors:
            result.add_error("FRONTMATTER_ERROR", error)

        if frontmatter is None:
            result.has_frontmatter = False
            return result

        result.has_frontmatter = True
        result.frontmatter = frontmatter
        result.name = frontmatter.get("name", folder_name)
        result.tags = self.extract_tags(frontmatter)

        # Run all validations
        self.validate_frontmatter_schema(frontmatter, result)
        self.validate_required_fields(frontmatter, result)
        self.validate_name_matches_folder(frontmatter, folder_name, result)
        self.validate_description(frontmatter, result)
        self.validate_body_sections(body, result)
        self.validate_references(frontmatter, body, skill_path, result)

        return result


def find_all_skills(exclude_templates: bool = True) -> List[Path]:
    """Find all skill directories."""
    skills = []

    if not SKILLS_DIR.exists():
        print(f"Error: Skills directory not found at {SKILLS_DIR}")
        return skills

    def scan_directory(directory: Path, is_template_dir: bool = False):
        """Recursively scan directory for skills."""
        for item in directory.iterdir():
            if item.is_dir():
                # Check if this is the _templates directory
                if item.name.startswith('_'):
                    if not exclude_templates:
                        # Scan inside _templates for actual skill folders
                        scan_directory(item, is_template_dir=True)
                    continue

                skill_file = item / "SKILL.md"
                if skill_file.exists():
                    skills.append(item)

    scan_directory(SKILLS_DIR)
    return sorted(skills, key=lambda p: p.name)


def generate_report(results: List[SkillValidationResult]) -> ValidationReport:
    """Generate a validation report from results."""
    report = ValidationReport(
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        total_skills=len(results),
        valid_skills=sum(1 for r in results if r.valid),
        invalid_skills=sum(1 for r in results if not r.valid),
        total_errors=sum(r.error_count for r in results),
        total_warnings=sum(r.warning_count for r in results),
    )

    # Build skills list
    for result in results:
        skill_data = {
            "name": result.name,
            "folder_name": result.folder_name,
            "path": result.path,
            "valid": result.valid,
            "has_frontmatter": result.has_frontmatter,
            "version": result.version,
            "status": result.status,
            "description": result.description,
            "tags": result.tags,
            "error_count": result.error_count,
            "warning_count": result.warning_count,
            "issues": [asdict(i) for i in result.issues],
            "referenced_schemas": result.referenced_schemas,
            "referenced_workflows": result.referenced_workflows,
            "referenced_scripts": result.referenced_scripts,
            "referenced_agents": result.referenced_agents,
            "missing_references": result.missing_references,
        }
        report.skills.append(skill_data)

        # Track by status
        status = result.status or "unknown"
        report.summary_by_status[status] = report.summary_by_status.get(status, 0) + 1

        # Track by category (from tags)
        if result.tags:
            category = result.tags[0] if result.tags else "uncategorized"
            report.summary_by_category[category] = report.summary_by_category.get(category, 0) + 1

    return report


def print_results(results: List[SkillValidationResult], verbose: bool = False):
    """Print validation results to console."""
    # ANSI colors
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

    print(f"\n{BOLD}Skill Validation Report{RESET}")
    print("=" * 60)

    for result in results:
        status_icon = f"{GREEN}PASS{RESET}" if result.valid else f"{RED}FAIL{RESET}"
        print(f"\n{status_icon} {BOLD}{result.name}{RESET}")

        if verbose or not result.valid:
            for issue in result.issues:
                if issue.severity == "error":
                    color = RED
                    prefix = "ERROR"
                elif issue.severity == "warning":
                    color = YELLOW
                    prefix = "WARN"
                else:
                    color = BLUE
                    prefix = "INFO"

                field_str = f" [{issue.field}]" if issue.field else ""
                print(f"  {color}{prefix}{RESET}{field_str}: {issue.message}")

                if verbose and issue.suggestion:
                    print(f"    {BLUE}Suggestion:{RESET} {issue.suggestion}")

    # Summary
    valid_count = sum(1 for r in results if r.valid)
    total_count = len(results)
    error_count = sum(r.error_count for r in results)
    warning_count = sum(r.warning_count for r in results)

    print("\n" + "=" * 60)
    print(f"{BOLD}Summary:{RESET}")
    print(f"  Total skills:  {total_count}")
    print(f"  {GREEN}Valid:{RESET}         {valid_count}")
    print(f"  {RED}Invalid:{RESET}       {total_count - valid_count}")
    print(f"  Total errors:  {error_count}")
    print(f"  Total warnings: {warning_count}")
    print(f"  Pass rate:     {valid_count/total_count*100:.1f}%" if total_count > 0 else "")

    if valid_count == total_count:
        print(f"\n{GREEN}{BOLD}All skills validated successfully!{RESET}")
    else:
        print(f"\n{YELLOW}Run with --verbose for detailed suggestions{RESET}")


def main():
    parser = argparse.ArgumentParser(
        description="Validate all SKILL.md files in the skills/ directory"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output including info messages and suggestions"
    )
    parser.add_argument(
        "--skill", "-s",
        type=str,
        help="Validate a specific skill by name"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=str(DEFAULT_OUTPUT),
        help=f"Output JSON report path (default: {DEFAULT_OUTPUT})"
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Only output JSON, no console output"
    )
    parser.add_argument(
        "--include-templates",
        action="store_true",
        help="Include _templates directory in validation"
    )

    args = parser.parse_args()

    # Initialize validator
    validator = SkillValidator(verbose=args.verbose)

    # Find skills to validate
    if args.skill:
        skill_path = SKILLS_DIR / args.skill
        if not skill_path.exists():
            print(f"Error: Skill '{args.skill}' not found at {skill_path}")
            sys.exit(1)
        skills = [skill_path]
    else:
        skills = find_all_skills(exclude_templates=not args.include_templates)

    if not skills:
        print("No skills found to validate")
        sys.exit(1)

    # Validate all skills
    results = []
    for skill_path in skills:
        result = validator.validate_skill(skill_path)
        results.append(result)

    # Generate report
    report = generate_report(results)

    # Ensure telemetry directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write JSON report
    with open(output_path, 'w') as f:
        json.dump(report.to_dict(), f, indent=2)

    # Print to console
    if not args.json_only:
        print_results(results, args.verbose)
        print(f"\nReport written to: {output_path}")
    else:
        print(json.dumps(report.to_dict(), indent=2))

    # Exit with error code if any skills are invalid
    sys.exit(0 if report.invalid_skills == 0 else 1)


if __name__ == "__main__":
    main()
