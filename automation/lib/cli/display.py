"""
MH1 CLI Display Module

Rich terminal rendering for the AI-first CLI.
This is pure presentation - no logic, no decisions.
"""

import os
from typing import List, Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich.spinner import Spinner
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich.box import ROUNDED, SIMPLE, MINIMAL

# Color scheme
COLORS = {
    "primary": "#7C3AED",      # Purple
    "secondary": "#10B981",    # Green
    "accent": "#F59E0B",       # Amber
    "muted": "#6B7280",        # Gray
    "error": "#EF4444",        # Red
    "success": "#10B981",      # Green
    "warning": "#F59E0B",      # Amber
    "info": "#3B82F6",         # Blue
}

# Menu structure
MAIN_MENU = [
    ("1", "Ask", "Natural language chat"),
    ("2", "Modules", "View/create project modules"),
    ("3", "Skills", "Browse and run skills"),
    ("4", "Agents", "Meet and use AI agents"),
    ("5", "Data", "Query CRM/warehouse, refresh connections"),
    ("6", "Client", "View client details"),
    ("7", "History", "Past runs and logs"),
    ("s", "Switch", "Switch client"),
    ("h", "Health", "System health check"),
    ("q", "Quit", "Exit MH1"),
]

SUBMENUS = {
    "modules": [
        ("a", "View Active", "List modules in progress"),
        ("b", "Create New", "Start a new module"),
        ("c", "Resume", "Continue a module"),
        ("←", "Back", "Return to main menu"),
    ],
    "skills": [
        ("a", "Browse", "Browse skills by category"),
        ("b", "Search", "Search for skills"),
        ("c", "Run", "Run a specific skill"),
        ("d", "Info", "View skill details"),
        ("←", "Back", "Return to main menu"),
    ],
    "agents": [
        ("a", "Meet Team", "View all agents"),
        ("b", "Talk", "Chat with an agent"),
        ("c", "Council", "Assemble agent council"),
        ("←", "Back", "Return to main menu"),
    ],
    "data": [
        ("a", "Query CRM", "Natural language CRM query"),
        ("b", "Query Warehouse", "Natural language SQL"),
        ("c", "Refresh", "Refresh MCP connections"),
        ("d", "Sync", "Sync Firebase data"),
        ("←", "Back", "Return to main menu"),
    ],
    "client": [
        ("a", "Profile", "Client overview"),
        ("b", "Firebase", "Browse Firebase data"),
        ("c", "Memory", "View memory system"),
        ("d", "Config", "Platform configuration"),
        ("e", "Edit", "Edit client details"),
        ("←", "Back", "Return to main menu"),
    ],
    "history": [
        ("a", "Recent", "Last 20 runs"),
        ("b", "Search", "Search runs"),
        ("c", "Details", "View run details"),
        ("d", "Costs", "Cost summary"),
        ("←", "Back", "Return to main menu"),
    ],
}

console = Console()


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def render_header() -> Panel:
    """Render the MH1 header."""
    header_text = Text()
    header_text.append("MH1", style=f"bold {COLORS['primary']}")
    header_text.append(" v2.0", style=COLORS['muted'])
    header_text.append("  |  ", style=COLORS['muted'])
    header_text.append("AI-First Marketing Operations", style=COLORS['secondary'])

    return Panel(
        header_text,
        box=ROUNDED,
        border_style=COLORS['primary'],
        padding=(0, 1),
    )


def render_client_context(client: Optional[Dict[str, Any]]) -> Panel:
    """Render the client context sidebar."""
    if not client:
        content = Text("No client selected\n", style=COLORS['muted'])
        content.append("Press ", style=COLORS['muted'])
        content.append("s", style=f"bold {COLORS['accent']}")
        content.append(" to switch client", style=COLORS['muted'])
    else:
        content = Text()
        content.append(f"{client.get('name', 'Unknown')}\n", style=f"bold {COLORS['primary']}")

        if client.get('industry'):
            content.append(f"{client['industry']}\n", style=COLORS['muted'])

        platforms = []
        if client.get('crm'):
            platforms.append(client['crm'])
        if client.get('warehouse'):
            platforms.append(client['warehouse'])
        if platforms:
            content.append(" | ".join(platforms) + "\n", style=COLORS['secondary'])

        if client.get('last_run'):
            content.append(f"Last: {client['last_run']}", style=COLORS['muted'])

    return Panel(
        content,
        title="[bold]Client[/bold]",
        title_align="left",
        box=ROUNDED,
        border_style=COLORS['muted'],
        width=30,
    )


def render_menu(highlight: Optional[str] = None) -> Panel:
    """Render the main menu bar."""
    menu_text = Text()

    for i, (key, label, _) in enumerate(MAIN_MENU):
        if i > 0:
            menu_text.append("  ")

        style = f"bold {COLORS['accent']}" if highlight == key else COLORS['muted']
        menu_text.append(f"[{key}]", style=style)
        menu_text.append(f" {label}", style=COLORS['primary'] if highlight == key else "white")

    return Panel(
        menu_text,
        box=SIMPLE,
        border_style=COLORS['muted'],
        padding=(0, 1),
    )


def render_submenu(submenu_name: str, highlight: Optional[str] = None) -> Panel:
    """Render a submenu."""
    items = SUBMENUS.get(submenu_name, [])

    table = Table(box=None, show_header=False, padding=(0, 2))
    table.add_column("Key", style=COLORS['accent'])
    table.add_column("Action", style="white")
    table.add_column("Description", style=COLORS['muted'])

    for key, label, desc in items:
        key_style = f"bold {COLORS['secondary']}" if highlight == key else COLORS['accent']
        table.add_row(f"[{key}]", label, desc, style=None if highlight != key else "bold")

    return Panel(
        table,
        title=f"[bold]{submenu_name.title()}[/bold]",
        title_align="left",
        box=ROUNDED,
        border_style=COLORS['secondary'],
    )


def render_chat(messages: List[Dict[str, str]], max_display: int = 10) -> Panel:
    """Render the chat window."""
    content = Text()

    recent = messages[-max_display:] if len(messages) > max_display else messages

    for msg in recent:
        role = msg.get("role", "user")
        text = msg.get("content", "")

        if role == "user":
            content.append("> ", style=f"bold {COLORS['accent']}")
            content.append(f"{text}\n\n", style="white")
        else:
            content.append("Claude: ", style=f"bold {COLORS['primary']}")
            content.append(f"{text}\n\n", style="white")

    if not messages:
        content.append("Type a message or select a menu option...", style=COLORS['muted'])

    return Panel(
        content,
        title="[bold]Chat[/bold]",
        title_align="left",
        box=ROUNDED,
        border_style=COLORS['primary'],
        height=20,
    )


def render_progress(task_name: str, status: str = "running", detail: str = "") -> Panel:
    """Render a progress indicator for skill execution."""
    content = Text()

    if status == "running":
        content.append("⠋ ", style=f"bold {COLORS['accent']}")
        content.append(f"{task_name}...", style="white")
    elif status == "success":
        content.append("✓ ", style=f"bold {COLORS['success']}")
        content.append(f"{task_name}", style="white")
    elif status == "error":
        content.append("✗ ", style=f"bold {COLORS['error']}")
        content.append(f"{task_name}", style="white")

    if detail:
        content.append(f"\n  {detail}", style=COLORS['muted'])

    return Panel(
        content,
        box=MINIMAL,
        border_style=COLORS['muted'],
        padding=(0, 1),
    )


def render_skill_list(skills: List[Dict[str, Any]], category: Optional[str] = None) -> Panel:
    """Render a list of skills."""
    table = Table(box=SIMPLE, show_header=True, header_style=f"bold {COLORS['primary']}")
    table.add_column("#", style=COLORS['accent'], width=4)
    table.add_column("Skill", style="white")
    table.add_column("Description", style=COLORS['muted'])

    for i, skill in enumerate(skills, 1):
        table.add_row(
            str(i),
            skill.get("name", ""),
            skill.get("description", "")[:60] + "..." if len(skill.get("description", "")) > 60 else skill.get("description", ""),
        )

    title = f"Skills: {category}" if category else "All Skills"

    return Panel(
        table,
        title=f"[bold]{title}[/bold]",
        title_align="left",
        box=ROUNDED,
        border_style=COLORS['secondary'],
    )


def render_agent_list(agents: List[Dict[str, Any]], agent_type: Optional[str] = None) -> Panel:
    """Render a list of agents."""
    table = Table(box=SIMPLE, show_header=True, header_style=f"bold {COLORS['primary']}")
    table.add_column("#", style=COLORS['accent'], width=4)
    table.add_column("Agent", style="white")
    table.add_column("Type", style=COLORS['secondary'])
    table.add_column("Specialization", style=COLORS['muted'])

    for i, agent in enumerate(agents, 1):
        table.add_row(
            str(i),
            agent.get("name", ""),
            agent.get("type", ""),
            agent.get("specialization", "")[:40] + "..." if len(agent.get("specialization", "")) > 40 else agent.get("specialization", ""),
        )

    title = f"Agents: {agent_type}" if agent_type else "All Agents"

    return Panel(
        table,
        title=f"[bold]{title}[/bold]",
        title_align="left",
        box=ROUNDED,
        border_style=COLORS['secondary'],
    )


def render_help() -> Panel:
    """Render help text."""
    help_text = """
**Navigation**
- Type a number/letter to select menu options
- Type naturally to chat with Claude
- Press Enter to send messages
- Press Ctrl+C to cancel operations

**Quick Commands**
- `/help` - Show this help
- `/clear` - Clear chat history
- `/client {name}` - Switch to client
- `/skill {name}` - Run a skill directly

**Tips**
- Claude understands natural language
- Just describe what you want to do
- Claude will figure out which skills/agents to use
    """

    return Panel(
        Markdown(help_text),
        title="[bold]Help[/bold]",
        title_align="left",
        box=ROUNDED,
        border_style=COLORS['info'],
    )


def render_full_screen(
    client: Optional[Dict[str, Any]] = None,
    messages: Optional[List[Dict[str, str]]] = None,
    mode: str = "menu",
    submenu: Optional[str] = None,
) -> None:
    """Render the full CLI screen."""
    clear_screen()

    # Header
    console.print(render_header())
    console.print()

    # Two-column layout: chat on left, context on right
    layout = Layout()
    layout.split_row(
        Layout(name="main", ratio=3),
        Layout(name="sidebar", ratio=1),
    )

    # Chat window
    chat_panel = render_chat(messages or [])

    # Client context
    context_panel = render_client_context(client)

    console.print(chat_panel)
    console.print()

    # Menu or submenu
    if mode == "submenu" and submenu:
        console.print(render_submenu(submenu))
    else:
        console.print(render_menu())

    console.print()
    console.print(render_client_context(client))
