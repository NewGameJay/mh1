#!/usr/bin/env python3
"""
MH1 CLI - AI-First Marketing Operations

A thin wrapper around Claude with branded UI.
"""

import sys
import os
import re
import subprocess
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
import anthropic
from dotenv import load_dotenv

# Load .env and ensure it's in the environment for subprocesses
load_dotenv(override=True)

# Get environment with .env values for subprocesses
ENV = os.environ.copy()

# Brand Colors
C = {
    "pink": "#EC4899",
    "rose": "#F472B6",
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

LOGO = f"""[bold #EC4899]███╗[/][bold #F472B6]   [/][bold #F97316]███╗[/][bold #FBBF24]██╗[/][bold #FDE047]  ██╗[/]  [bold #EC4899]██╗[/]
[bold #EC4899]████╗[/][bold #F472B6] [/][bold #F97316]████║[/][bold #FBBF24]██║[/][bold #FDE047]  ██║[/]  [bold #F472B6]███║[/]
[bold #EC4899]██╔████╔██║[/][bold #FBBF24]███████║[/]  [bold #F97316]╚██║[/]
[bold #F472B6]██║[/][bold #F97316]╚██╔╝██║[/][bold #FBBF24]██╔══██║[/]   [bold #FBBF24]██║[/]
[bold #F97316]██║[/][bold #FBBF24] ╚═╝ [/][bold #FDE047]██║██║[/]  [bold #FDE047]██║[/]   [bold #FDE047]██║[/]
[bold #FBBF24]╚═╝[/]     [bold #FDE047]╚═╝╚═╝[/]  [bold #FDE047]╚═╝[/]   [bold #FDE047]╚═╝[/]"""

QUICK_ACTIONS = f"[{C['dim']}][[/][{C['yellow']}]1[/][{C['dim']}]] Skills  [[/][{C['yellow']}]2[/][{C['dim']}]] Agents  [[/][{C['yellow']}]3[/][{C['dim']}]] Client  [[/][{C['yellow']}]?[/][{C['dim']}]] Help  [[/][{C['yellow']}]q[/][{C['dim']}]] Quit[/]"


class Session:
    """Minimal session state."""
    def __init__(self):
        self.client_id = None
        self.client_name = None
        self.messages = []
        self.last_results = []  # Store last query results for selection

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})


session = Session()
api_client = anthropic.Anthropic()


def load_system_prompt() -> str:
    """Load system prompt from file."""
    prompt_path = PROJECT_ROOT / "prompts" / "system" / "mh1-cmo-copilot.md"
    if prompt_path.exists():
        base_prompt = prompt_path.read_text()
    else:
        base_prompt = "You are MH1, a CMO co-pilot for marketing operations."

    # Add context
    context = f"""

## Current Session
- Client: {session.client_name or 'None selected'} ({session.client_id or 'no-client'})
- Project Root: {PROJECT_ROOT}

## YOUR TOOLS - YOU MUST USE THEM
You have 4 tools. When you need to read a file, CALL read_file. When you need to run a command, CALL run_command. DO NOT describe what you would do - ACTUALLY DO IT.

- **read_file**: Read files. CALL THIS to read SKILL.md, configs, client data.
- **list_directory**: List directories. CALL THIS to explore skills/, clients/.
- **run_command**: Run shell commands. CALL THIS for node scripts, npm, bash.
- **write_file**: Write files. CALL THIS to save configs, reports.

## HOW TO RUN SKILLS
Skills are in skills/[category]/[skill-name]/SKILL.md. Example: skills/operations-skills/client-onboarding/SKILL.md

To run a skill:
1. CALL read_file to read the SKILL.md
2. Follow its instructions - CALL your tools for each step
3. CALL run_command for scripts, CALL write_file to save outputs

## CRITICAL RULES
1. DO NOT say "Let me read..." - CALL read_file and actually read it.
2. DO NOT say "I'll check..." - CALL list_directory and actually check.
3. ACTUALLY USE YOUR TOOLS. Every action requires a tool call.
4. Be concise. No fluff.
"""
    return base_prompt + context


def execute_skill(skill_name: str, params: dict) -> str:
    """Execute a skill and return its output."""
    console.print(f"\n[{C['amber']}]⚡ Running {skill_name}...[/]")

    # Find the skill directory
    skill_dir = None
    for dirname in ["skills", ".skills"]:
        base = PROJECT_ROOT / dirname
        if not base.exists():
            continue
        for category in base.iterdir():
            if not category.is_dir():
                continue
            candidate = category / skill_name
            if candidate.exists():
                skill_dir = candidate
                break
        if skill_dir:
            break

    if not skill_dir:
        return f"Error: Skill '{skill_name}' not found"

    # For firestore-nav and other node-based skills, run the script
    script_path = skill_dir / f"{skill_name}.js"
    if script_path.exists():
        # Build command
        cmd = ["node", str(script_path)]
        if "path" in params:
            cmd.append(params["path"])
        for k, v in params.items():
            if k != "path":
                cmd.extend([f"--{k}", str(v)])

        try:
            with Live(Spinner("dots", text=f"[{C['dim']}]Querying...[/]"), console=console, refresh_per_second=10):
                result = subprocess.run(
                    cmd,
                    cwd=skill_dir,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    env=ENV  # Pass environment with .env values
                )

            # Always return stdout - errors are often returned as JSON there
            output = result.stdout.strip() if result.stdout else ""

            if result.returncode != 0:
                # Check if error is in stdout (as JSON) or stderr
                if output:
                    return output  # Let the caller parse the JSON error
                elif result.stderr:
                    return json.dumps({"error": "SCRIPT_ERROR", "message": result.stderr.strip()})
                else:
                    return json.dumps({"error": "UNKNOWN_ERROR", "message": f"Script exited with code {result.returncode}"})

            return output if output else json.dumps({"error": "EMPTY_RESPONSE", "message": "Script returned no output"})

        except subprocess.TimeoutExpired:
            return json.dumps({"error": "TIMEOUT", "message": "Skill timed out after 30 seconds"})
        except Exception as e:
            return json.dumps({"error": "EXCEPTION", "message": str(e)})

    return f"Error: No executable found for skill '{skill_name}'"


def process_markers(text: str) -> tuple[str, list]:
    """Extract and process markers from response. Returns (clean_text, results)."""
    results = []

    # Process SKILL markers
    skill_pattern = r'\[\[SKILL:([^\]|]+)(?:\|([^\]]+))?\]\]'
    for match in re.finditer(skill_pattern, text):
        skill_name = match.group(1).strip()
        params_str = match.group(2) or ""

        # Parse params
        params = {}
        for part in params_str.split("|"):
            if "=" in part:
                k, v = part.split("=", 1)
                params[k.strip()] = v.strip()

        # Execute skill
        result = execute_skill(skill_name, params)
        results.append(("skill", skill_name, result))

    # Process SET_CLIENT markers
    client_pattern = r'\[\[SET_CLIENT:([^\]|]+)\|?([^\]]*)\]\]'
    for match in re.finditer(client_pattern, text):
        client_id = match.group(1).strip()
        client_name = match.group(2).strip() if match.group(2) else client_id.replace("-", " ").title()
        session.client_id = client_id
        session.client_name = client_name
        client_dir = PROJECT_ROOT / "clients" / client_id
        client_dir.mkdir(parents=True, exist_ok=True)
        results.append(("client", client_id, client_name))

    # Remove all markers from text
    clean = re.sub(r'\[\[[^\]]+\]\]', '', text)
    return clean.strip(), results


TOOLS = [
    {
        "name": "read_file",
        "description": "Read a file from the filesystem. Use for reading SKILL.md files, configs, client data, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file (relative to project root or absolute)"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "list_directory",
        "description": "List contents of a directory",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to directory"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "run_command",
        "description": "Run a shell command. Use for executing node scripts, npm commands, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Command to run"},
                "cwd": {"type": "string", "description": "Working directory (optional)"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to file"},
                "content": {"type": "string", "description": "Content to write"}
            },
            "required": ["path", "content"]
        }
    }
]


def handle_tool_call(tool_name: str, tool_input: dict) -> str:
    """Execute a tool and return result."""
    try:
        if tool_name == "read_file":
            path = tool_input["path"]
            if not path.startswith("/"):
                path = PROJECT_ROOT / path
            else:
                path = Path(path)
            if path.exists():
                content = path.read_text()
                # Truncate large files
                if len(content) > 10000:
                    return content[:10000] + f"\n... (truncated, {len(content)} chars total)"
                return content
            return f"Error: File not found: {path}"

        elif tool_name == "list_directory":
            path = tool_input["path"]
            if not path.startswith("/"):
                path = PROJECT_ROOT / path
            else:
                path = Path(path)
            if path.exists() and path.is_dir():
                items = sorted(path.iterdir())
                return "\n".join(f"{'[dir] ' if i.is_dir() else ''}{i.name}" for i in items[:50])
            return f"Error: Directory not found: {path}"

        elif tool_name == "run_command":
            cmd = tool_input["command"]
            cwd = tool_input.get("cwd", str(PROJECT_ROOT))
            if not cwd.startswith("/"):
                cwd = str(PROJECT_ROOT / cwd)
            result = subprocess.run(
                cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=60, env=ENV
            )
            output = result.stdout + result.stderr
            if len(output) > 5000:
                output = output[:5000] + "\n... (truncated)"
            return output or "(no output)"

        elif tool_name == "write_file":
            path = tool_input["path"]
            if not path.startswith("/"):
                path = PROJECT_ROOT / path
            else:
                path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(tool_input["content"])
            return f"Written to {path}"

        return f"Unknown tool: {tool_name}"
    except Exception as e:
        return f"Error: {e}"


def call_claude(user_message: str):
    """Send message to Claude with tool access."""
    session.add_message("user", user_message)
    system_prompt = load_system_prompt()

    console.print(f"\n[{C['amber']}]MH1:[/] ", end="")

    try:
        # Call with tools - loop until no more tool calls
        messages = session.messages.copy()
        max_iterations = 10

        for _ in range(max_iterations):
            response = api_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=system_prompt,
                messages=messages,
                tools=TOOLS,
            )

            # Check if Claude wants to use tools
            tool_calls = [block for block in response.content if block.type == "tool_use"]
            text_blocks = [block for block in response.content if block.type == "text"]

            # Print any text
            for block in text_blocks:
                console.print(block.text, markup=False)

            # If no tool calls, we're done
            if not tool_calls or response.stop_reason == "end_turn":
                final_text = "".join(b.text for b in text_blocks)
                session.add_message("assistant", final_text)
                break

            # Handle tool calls - serialize content blocks properly
            assistant_content = []
            for block in response.content:
                if block.type == "text":
                    assistant_content.append({"type": "text", "text": block.text})
                elif block.type == "tool_use":
                    assistant_content.append({
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input
                    })
            messages.append({"role": "assistant", "content": assistant_content})

            tool_results = []
            for tool_call in tool_calls:
                console.print(f"[{C['dim']}]→ {tool_call.name}: {list(tool_call.input.keys()) if tool_call.input else ''}[/]")
                result = handle_tool_call(tool_call.name, tool_call.input)
                # Show brief result
                result_preview = result[:100] + "..." if len(result) > 100 else result
                console.print(f"[{C['dim']}]  ← {result_preview.split(chr(10))[0]}[/]")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": result
                })

            messages.append({"role": "user", "content": tool_results})

        console.print()

    except Exception as e:
        console.print(f"\n[{C['red']}]Error: {e}[/]")
        import traceback
        traceback.print_exc()


def show_welcome():
    """Show welcome screen."""
    console.clear()
    console.print()
    console.print(LOGO)
    console.print()
    console.print(f"[{C['white']}]AI-powered marketing operations[/]")
    console.print(QUICK_ACTIONS)
    console.print()


def show_help():
    """Show help."""
    console.print(f"""
[{C['amber']}]MH1 Commands[/]

[{C['yellow']}]1[/] - List available skills
[{C['yellow']}]2[/] - List available agents
[{C['yellow']}]3[/] - Select/create client
[{C['yellow']}]?[/] - Show this help
[{C['yellow']}]q[/] - Quit

[{C['white']}]Or just type what you need:[/]
  "Run a lifecycle audit"
  "Create email sequences for onboarding"
  "Analyze our competitor landscape"
""")


def main():
    """Main loop."""
    show_welcome()

    while True:
        try:
            # Build prompt with client display
            if session.client_name:
                client_display = f"[{C['cyan']}]{session.client_name}[/]"
            else:
                client_display = f"[{C['dim']}]no client[/]"

            prompt = f"{client_display} [{C['pink']}]>[/] "
            user_input = console.input(prompt).strip()

            if not user_input:
                continue

            # Check for client selection FIRST (if we have results)
            if user_input.isdigit() and session.last_results:
                idx = int(user_input) - 1
                if 0 <= idx < len(session.last_results):
                    doc = session.last_results[idx]
                    doc_data = doc.get("data", {})
                    client_id = doc.get("id", "unknown")
                    client_name = doc_data.get("displayName") or doc_data.get("name") or client_id

                    session.client_id = client_id
                    session.client_name = client_name
                    client_dir = PROJECT_ROOT / "clients" / client_id
                    client_dir.mkdir(parents=True, exist_ok=True)
                    session.last_results = []  # Clear results

                    console.print(f"\n[{C['green']}]✓ Switched to {client_name}[/]\n")
                else:
                    console.print(f"[{C['red']}]Invalid selection. Choose 1-{len(session.last_results)}[/]")
                continue

            # Quick actions
            if user_input.lower() == "q":
                console.print(f"\n[{C['dim']}]Goodbye![/]\n")
                break
            elif user_input == "?":
                show_help()
            elif user_input == "1":
                call_claude("List the available skills. Use list_directory to explore skills/ directory. Show them grouped by category.")
            elif user_input == "2":
                call_claude("List the available agents. Use list_directory to explore agents/ directory. Show them grouped by type.")
            elif user_input == "3":
                # Run skill directly - no need for Claude roundtrip
                console.print()
                output = execute_skill("firestore-nav", {"path": "clients", "limit": "50", "fields": "name,displayName,status"})
                try:
                    data = json.loads(output.strip())
                    if "documents" in data:
                        docs = data["documents"]
                        session.last_results = docs
                        console.print(f"\n[{C['white']}]Your clients ({len(docs)}):[/]\n")
                        for i, doc in enumerate(docs, 1):
                            doc_data = doc.get("data", {})
                            name = doc_data.get("displayName") or doc_data.get("name") or doc.get("id", "?")
                            status = doc_data.get("status", "")
                            line = f"  [{C['yellow']}]{i:2}[/]. {name}"
                            if status:
                                line += f" [{C['dim']}]({status})[/]"
                            console.print(line)
                        console.print(f"\n[{C['gray']}]Enter number to select client[/]")
                    elif "error" in data:
                        console.print(f"\n[{C['red']}]Error: {data.get('message', 'Unknown error')}[/]")
                except json.JSONDecodeError as e:
                    console.print(f"\n[{C['red']}]Failed to parse response: {e}[/]")
            else:
                # Check if it's a number (selection from last results)
                if user_input.isdigit() and session.last_results:
                    idx = int(user_input) - 1
                    if 0 <= idx < len(session.last_results):
                        doc = session.last_results[idx]
                        doc_data = doc.get("data", doc)
                        client_id = doc.get("id", "unknown")
                        client_name = doc_data.get("displayName", doc_data.get("name", client_id))

                        # Set the client directly
                        session.client_id = client_id
                        session.client_name = client_name
                        client_dir = PROJECT_ROOT / "clients" / client_id
                        client_dir.mkdir(parents=True, exist_ok=True)
                        session.last_results = []  # Clear results

                        console.print(f"\n[{C['green']}]✓ Switched to {client_name}[/]")
                    else:
                        console.print(f"[{C['red']}]Invalid selection. Choose 1-{len(session.last_results)}[/]")
                else:
                    call_claude(user_input)

        except KeyboardInterrupt:
            console.print(f"\n[{C['dim']}]Use 'q' to quit[/]")
        except Exception as e:
            console.print(f"\n[{C['red']}]Error: {e}[/]")


if __name__ == "__main__":
    main()
