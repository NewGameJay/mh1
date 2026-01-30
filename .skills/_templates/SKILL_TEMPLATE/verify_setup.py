#!/usr/bin/env python3
"""
Verify environment setup for [SKILL_NAME] skill.

Run this script to check that all dependencies and credentials
are properly configured before using the skill.

Usage:
    python verify_setup.py
"""

import sys
import os
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
        # Add required packages here
        # ("package_name", "import_name"),
        ("requests", "requests"),
    ]
    
    all_ok = True
    for package, import_name in required:
        print(f"Checking {package}...", end=" ")
        try:
            __import__(import_name)
            print("OK")
        except ImportError:
            print(f"FAIL (install with: pip install {package})")
            all_ok = False
    
    return all_ok


def check_environment_variables():
    """Check required environment variables are set."""
    required_vars = [
        # Add required environment variables here
        # "VARIABLE_NAME",
    ]
    
    if not required_vars:
        print("No environment variables required")
        return True
    
    all_ok = True
    for var in required_vars:
        print(f"Checking ${var}...", end=" ")
        if os.environ.get(var):
            print("OK")
        else:
            print(f"FAIL (not set)")
            all_ok = False
    
    return all_ok


def check_files():
    """Check required files exist."""
    skill_dir = Path(__file__).parent
    required_files = [
        "SKILL.md",
        "schemas/input.json",
        "schemas/output.json",
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


def check_api_connectivity():
    """Check API endpoints are reachable."""
    # Customize this for your skill's APIs
    endpoints = [
        # ("API Name", "https://api.example.com/health"),
    ]
    
    if not endpoints:
        print("No API connectivity checks configured")
        return True
    
    import requests
    
    all_ok = True
    for name, url in endpoints:
        print(f"Checking {name} API...", end=" ")
        try:
            response = requests.get(url, timeout=10)
            if response.ok:
                print("OK")
            else:
                print(f"FAIL (status {response.status_code})")
                all_ok = False
        except Exception as e:
            print(f"FAIL ({e})")
            all_ok = False
    
    return all_ok


def main():
    print("=" * 50)
    print("Verifying [SKILL_NAME] Setup")
    print("=" * 50)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment Variables", check_environment_variables),
        ("Required Files", check_files),
        ("API Connectivity", check_api_connectivity),
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
        return 0
    else:
        print("Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
