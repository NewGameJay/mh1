"""
MH1 CLI Module

AI-first command line interface for MH1 marketing operations.
All logic lives in Claude - this is just the presentation layer.
"""

from .state import SessionState, load_session, save_session
from .display import (
    render_header,
    render_client_context,
    render_menu,
    render_submenu,
    render_chat,
    render_progress,
    render_skill_list,
    render_agent_list,
    render_help,
    clear_screen,
    COLORS,
    SUBMENUS,
)

__all__ = [
    # State
    "SessionState",
    "load_session",
    "save_session",
    # Display
    "render_header",
    "render_client_context",
    "render_menu",
    "render_submenu",
    "render_chat",
    "render_progress",
    "render_skill_list",
    "render_agent_list",
    "render_help",
    "clear_screen",
    "COLORS",
    "SUBMENUS",
]
