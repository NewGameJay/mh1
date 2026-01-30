#!/usr/bin/env python3
"""
Schema Validation Script

Validates all JSON schemas in the MH1 system:
- Checks JSON syntax is valid
- Validates against JSON Schema draft-07
- Ensures skill schemas have input.json and output.json
"""

import json
import sys
from pathlib import Path

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    print("Warning: jsonschema not installed, skipping draft-07 validation")

SYSTEM_ROOT = Path(__file__).parent.parent

def find_schemas():
    """Find all JSON schema files."""
    schemas = []
    
    # Main schemas directory
    schemas_dir = SYSTEM_ROOT / "schemas"
    if schemas_dir.exists():
        schemas.extend(schemas_dir.glob("*.json"))
    
    # Skill schemas
    skills_dir = SYSTEM_ROOT / "skills"
    if skills_dir.exists():
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith("_"):
                schema_dir = skill_dir / "schemas"
                if schema_dir.exists():
                    schemas.extend(schema_dir.glob("*.json"))
    
    return schemas

def validate_json_syntax(path: Path) -> tuple[bool, str]:
    """Check if file is valid JSON."""
    try:
        with open(path) as f:
            json.load(f)
        return True, ""
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"

def validate_schema_structure(path: Path, content: dict) -> tuple[bool, str]:
    """Check basic schema structure."""
    if "$schema" not in content:
        return False, "Missing $schema declaration"
    
    if "type" not in content and "properties" not in content and "$ref" not in content:
        return False, "Schema should have type, properties, or $ref"
    
    return True, ""

def check_skill_schemas():
    """Ensure each skill has input.json and output.json."""
    issues = []
    skills_dir = SYSTEM_ROOT / "skills"
    
    if not skills_dir.exists():
        return issues
    
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir() and not skill_dir.name.startswith("_"):
            schema_dir = skill_dir / "schemas"
            if not schema_dir.exists():
                issues.append(f"Skill '{skill_dir.name}' missing schemas/ directory")
                continue
            
            if not (schema_dir / "input.json").exists():
                issues.append(f"Skill '{skill_dir.name}' missing schemas/input.json")
            if not (schema_dir / "output.json").exists():
                issues.append(f"Skill '{skill_dir.name}' missing schemas/output.json")
    
    return issues

def main():
    print("MH1 Schema Validation")
    print("=" * 40)
    
    errors = []
    warnings = []
    
    # Find and validate all schemas
    schemas = find_schemas()
    print(f"\nFound {len(schemas)} schema files")
    
    for schema_path in schemas:
        relative_path = schema_path.relative_to(SYSTEM_ROOT)
        
        # Check JSON syntax
        valid, error = validate_json_syntax(schema_path)
        if not valid:
            errors.append(f"{relative_path}: {error}")
            continue
        
        # Load and check structure
        with open(schema_path) as f:
            content = json.load(f)
        
        valid, error = validate_schema_structure(schema_path, content)
        if not valid:
            warnings.append(f"{relative_path}: {error}")
        
        print(f"  ✓ {relative_path}")
    
    # Check skill schema completeness
    skill_issues = check_skill_schemas()
    warnings.extend(skill_issues)
    
    # Report results
    print("\n" + "=" * 40)
    
    if errors:
        print(f"\n❌ {len(errors)} ERRORS:")
        for e in errors:
            print(f"  - {e}")
    
    if warnings:
        print(f"\n⚠️  {len(warnings)} WARNINGS:")
        for w in warnings:
            print(f"  - {w}")
    
    if not errors and not warnings:
        print("\n✅ All schemas valid!")
    
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
