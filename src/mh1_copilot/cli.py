#!/usr/bin/env python3
"""
MH1 CLI Bootstrap

This is the pip-installable entry point. It:
1. Ensures the full MH1 system is installed at ~/.mh1
2. Runs the actual CLI from there

Usage:
    pip install mh1-copilot
    mh1
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

MH1_HOME = Path.home() / ".mh1"
MH1_REPO = "https://github.com/NewGameJay/mh1.git"
MH1_CLI = MH1_HOME / "mh1"
MH1_VENV = MH1_HOME / ".venv"

# Colors for terminal output
CYAN = "\033[0;36m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
NC = "\033[0m"  # No Color

LOGO = f"""{CYAN}
    ███╗   ███╗██╗  ██╗     ██╗
    ████╗ ████║██║  ██║    ███║
    ██╔████╔██║███████║    ╚██║
    ██║╚██╔╝██║██╔══██║     ██║
    ██║ ╚═╝ ██║██║  ██║     ██║
    ╚═╝     ╚═╝╚═╝  ╚═╝     ╚═╝
{NC}"""


def print_logo():
    print(LOGO)


def check_python_version():
    """Ensure Python 3.10+"""
    if sys.version_info < (3, 10):
        print(f"{RED}Error: MH1 requires Python 3.10 or newer{NC}")
        print(f"You have: Python {sys.version_info.major}.{sys.version_info.minor}")
        sys.exit(1)


def install_mh1():
    """Install the full MH1 system to ~/.mh1"""
    print_logo()
    print(f"{CYAN}Installing MH1...{NC}\n")

    # Check for git
    if not shutil.which("git"):
        print(f"{RED}Error: git is required for installation{NC}")
        print("Install git and try again.")
        sys.exit(1)

    # Clone the repository
    print(f"Cloning MH1 to {MH1_HOME}...")
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", MH1_REPO, str(MH1_HOME)],
            check=True,
            capture_output=True
        )
        print(f"{GREEN}✓ Repository cloned{NC}")
    except subprocess.CalledProcessError as e:
        print(f"{RED}Error cloning repository:{NC}")
        print(e.stderr.decode() if e.stderr else str(e))
        sys.exit(1)

    # Create virtual environment
    print("Creating Python environment...")
    try:
        subprocess.run(
            [sys.executable, "-m", "venv", str(MH1_VENV)],
            check=True,
            capture_output=True
        )
        print(f"{GREEN}✓ Virtual environment created{NC}")
    except subprocess.CalledProcessError as e:
        print(f"{RED}Error creating venv:{NC}")
        print(e.stderr.decode() if e.stderr else str(e))
        sys.exit(1)

    # Install dependencies
    print("Installing dependencies...")
    pip_path = MH1_VENV / "bin" / "pip"
    requirements = MH1_HOME / "requirements.txt"

    try:
        subprocess.run(
            [str(pip_path), "install", "-q", "--upgrade", "pip"],
            check=True,
            capture_output=True
        )
        subprocess.run(
            [str(pip_path), "install", "-q", "-r", str(requirements)],
            check=True,
            capture_output=True
        )
        print(f"{GREEN}✓ Dependencies installed{NC}")
    except subprocess.CalledProcessError as e:
        print(f"{RED}Error installing dependencies:{NC}")
        print(e.stderr.decode() if e.stderr else str(e))
        sys.exit(1)

    # Make CLI executable
    MH1_CLI.chmod(0o755)

    print(f"\n{GREEN}✓ MH1 installed successfully!{NC}\n")
    print(f"Location: {MH1_HOME}")
    print()


def update_mh1():
    """Update existing MH1 installation"""
    print(f"{CYAN}Updating MH1...{NC}")
    try:
        subprocess.run(
            ["git", "-C", str(MH1_HOME), "pull"],
            check=True
        )
        print(f"{GREEN}✓ Updated{NC}")
    except subprocess.CalledProcessError:
        print(f"{YELLOW}Warning: Could not update. Try reinstalling.{NC}")


def run_mh1(args):
    """Run the actual MH1 CLI"""
    python_path = MH1_VENV / "bin" / "python"

    # Run the CLI
    try:
        result = subprocess.run(
            [str(python_path), str(MH1_CLI)] + args,
            cwd=str(MH1_HOME)
        )
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"{RED}Error running MH1: {e}{NC}")
        sys.exit(1)


def main():
    """Main entry point"""
    check_python_version()

    # Handle special commands
    args = sys.argv[1:]

    if "--version" in args or "-v" in args:
        from mh1_copilot import __version__
        print(f"mh1-copilot {__version__}")
        return

    if "--help" in args and not MH1_HOME.exists():
        print_logo()
        print("MH1 - AI-Powered Marketing Operations CLI\n")
        print("Usage: mh1 [options] [command]\n")
        print("On first run, MH1 will install to ~/.mh1\n")
        print("Options:")
        print("  --version     Show version")
        print("  --update      Update MH1")
        print("  --reinstall   Reinstall MH1")
        print("  --where       Show installation path")
        return

    if "--where" in args:
        if MH1_HOME.exists():
            print(MH1_HOME)
        else:
            print("MH1 not installed. Run 'mh1' to install.")
        return

    if "--reinstall" in args:
        if MH1_HOME.exists():
            print(f"Removing {MH1_HOME}...")
            shutil.rmtree(MH1_HOME)
        install_mh1()
        return

    if "--update" in args:
        if MH1_HOME.exists():
            update_mh1()
        else:
            print("MH1 not installed. Run 'mh1' to install.")
        return

    # Install if needed
    if not MH1_HOME.exists():
        install_mh1()

    # Check if venv exists, reinstall if not
    if not MH1_VENV.exists():
        print(f"{YELLOW}Virtual environment missing. Reinstalling...{NC}")
        shutil.rmtree(MH1_HOME, ignore_errors=True)
        install_mh1()

    # Run the CLI
    run_mh1(args)


if __name__ == "__main__":
    main()
