#!/usr/bin/env python3
"""
Verify environment setup for cohort-retention-analysis skill.

Run this script to check that all dependencies and credentials
are properly configured before using the skill.

Usage:
    python verify_setup.py
    python verify_setup.py --client_id FFC
"""

import sys
import os
import argparse
from pathlib import Path


def check_python_version():
    """Check Python version is 3.8+."""
    print("Checking Python version...", end=" ")
    if sys.version_info >= (3, 8):
        print(f"OK (Python {sys.version_info.major}.{sys.version_info.minor})")
        return True
    else:
        print(f"FAIL (Python {sys.version_info.major}.{sys.version_info.minor}, need 3.8+)")
        return False


def check_dependencies():
    """Check required packages are installed."""
    required = [
        ("scipy", "scipy"),  # For chi-square tests
        ("numpy", "numpy"),  # For numerical operations
        ("pyyaml", "yaml"),  # For reading lifecycle config
    ]

    all_ok = True
    for package, import_name in required:
        print(f"Checking {package}...", end=" ")
        try:
            __import__(import_name)
            print("OK")
        except ImportError:
            print(f"WARN (optional, install with: pip install {package})")
            # Don't fail - these are optional since we can use LLM for analysis

    return all_ok


def check_environment_variables():
    """Check required environment variables are set."""
    # No strict requirements - data sources are configured per-client
    optional_vars = [
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "BIGQUERY_PROJECT",
        "HUBSPOT_API_KEY",
    ]

    print("Checking data source environment variables...")
    found_any = False
    for var in optional_vars:
        if os.environ.get(var):
            print(f"  ${var}: SET")
            found_any = True
        else:
            print(f"  ${var}: not set")

    if not found_any:
        print("  Note: No data source credentials found in environment.")
        print("  Configure per-client in clients/{client_id}/config/datasources.yaml")

    return True  # Not strictly required


def check_files():
    """Check required files exist."""
    skill_dir = Path(__file__).parent
    required_files = [
        "SKILL.md",
        "schemas/input.json",
        "schemas/output.json",
        "quick_reference.md",
    ]

    all_ok = True
    for file in required_files:
        path = skill_dir / file
        print(f"Checking {file}...", end=" ")
        if path.exists():
            print("OK")
        else:
            print(f"FAIL (not found)")
            all_ok = False

    return all_ok


def check_lib_dependencies():
    """Check MH1 lib modules are available."""
    # Navigate to system root
    skill_dir = Path(__file__).parent
    system_root = skill_dir.parent.parent
    lib_dir = system_root / "lib"

    required_libs = [
        "freshness.py",
        "client.py",
        "mcp_client.py",
    ]

    all_ok = True
    for lib_file in required_libs:
        path = lib_dir / lib_file
        print(f"Checking lib/{lib_file}...", end=" ")
        if path.exists():
            print("OK")
        else:
            print(f"FAIL (not found)")
            all_ok = False

    return all_ok


def check_client_config(client_id: str = None):
    """Check client-specific configuration."""
    if not client_id:
        print("No client_id provided, skipping client config check")
        print("  Run with --client_id <id> to verify client setup")
        return True

    skill_dir = Path(__file__).parent
    system_root = skill_dir.parent.parent
    clients_dir = system_root / "clients"
    client_dir = clients_dir / client_id

    print(f"Checking client config for: {client_id}")

    all_ok = True

    # Check lifecycle config
    lifecycle_path = client_dir / "context" / "lifecycle.yaml"
    lifecycle_yml = client_dir / "context" / "lifecycle.yml"
    print(f"  Checking lifecycle config...", end=" ")
    if lifecycle_path.exists() or lifecycle_yml.exists():
        print("OK")
    else:
        print("MISSING")
        print("    Run client-onboarding Phase 2.5 to create lifecycle mapping")
        all_ok = False

    # Check datasources config
    datasources_path = client_dir / "config" / "datasources.yaml"
    print(f"  Checking datasources config...", end=" ")
    if datasources_path.exists():
        print("OK")
    else:
        print("MISSING")
        print("    Run client-onboarding to create data source configuration")
        all_ok = False

    return all_ok


def main():
    parser = argparse.ArgumentParser(description="Verify cohort-retention-analysis setup")
    parser.add_argument("--client_id", help="Client ID to check configuration for")
    args = parser.parse_args()

    print("=" * 50)
    print("Verifying Cohort Retention Analysis Setup")
    print("=" * 50)
    print()

    checks = [
        ("Python Version", lambda: check_python_version()),
        ("Dependencies", lambda: check_dependencies()),
        ("Environment Variables", lambda: check_environment_variables()),
        ("Required Files", lambda: check_files()),
        ("Lib Dependencies", lambda: check_lib_dependencies()),
        ("Client Config", lambda: check_client_config(args.client_id)),
    ]

    results = []
    for name, check_fn in checks:
        print(f"\n--- {name} ---")
        results.append((name, check_fn()))

    print("\n" + "=" * 50)
    print("Summary")
    print("=" * 50)

    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("All checks passed! Skill is ready to use.")
        if not args.client_id:
            print("\nTip: Run with --client_id <id> to verify client-specific setup")
        return 0
    else:
        print("Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
