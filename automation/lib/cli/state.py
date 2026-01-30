"""
MH1 CLI State Management

Minimal state tracking for the CLI session.
All logic lives in Claude - this just tracks presentation state.
"""

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class ClientContext:
    """Current client context (loaded from Firebase/files)."""
    client_id: str
    name: str
    industry: Optional[str] = None
    crm: Optional[str] = None
    warehouse: Optional[str] = None
    last_run: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClientContext":
        return cls(**data)


@dataclass
class ChatMessage:
    """A single chat message."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatMessage":
        return cls(**data)


@dataclass
class SessionState:
    """
    CLI session state.

    Tracks:
    - Current client (if any)
    - Chat history (last 50 messages)
    - Current mode (chat, menu, executing)
    - Active module (if working on one)
    """
    client: Optional[ClientContext] = None
    chat_history: List[ChatMessage] = field(default_factory=list)
    mode: str = "menu"  # menu | chat | executing | submenu
    active_module: Optional[str] = None
    submenu: Optional[str] = None  # Current submenu if in submenu mode

    # Limits
    MAX_CHAT_HISTORY = 50

    def add_message(self, role: str, content: str) -> None:
        """Add a chat message, maintaining history limit."""
        self.chat_history.append(ChatMessage(role=role, content=content))
        if len(self.chat_history) > self.MAX_CHAT_HISTORY:
            self.chat_history = self.chat_history[-self.MAX_CHAT_HISTORY:]

    def clear_chat(self) -> None:
        """Clear chat history."""
        self.chat_history = []

    def get_recent_chat(self, limit: int = 10) -> List[ChatMessage]:
        """Get recent chat messages."""
        return self.chat_history[-limit:]

    def set_client(self, client: ClientContext) -> None:
        """Set current client."""
        self.client = client

    def clear_client(self) -> None:
        """Clear current client."""
        self.client = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize state to dict."""
        return {
            "client": self.client.to_dict() if self.client else None,
            "chat_history": [m.to_dict() for m in self.chat_history],
            "mode": self.mode,
            "active_module": self.active_module,
            "submenu": self.submenu,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionState":
        """Deserialize state from dict."""
        state = cls()
        if data.get("client"):
            state.client = ClientContext.from_dict(data["client"])
        state.chat_history = [ChatMessage.from_dict(m) for m in data.get("chat_history", [])]
        state.mode = data.get("mode", "menu")
        state.active_module = data.get("active_module")
        state.submenu = data.get("submenu")
        return state


# Session file path
SESSION_FILE = Path.home() / ".mh1" / "session.json"


def load_session() -> SessionState:
    """Load session state from disk."""
    if SESSION_FILE.exists():
        try:
            data = json.loads(SESSION_FILE.read_text())
            return SessionState.from_dict(data)
        except (json.JSONDecodeError, KeyError, TypeError):
            # Corrupted file, start fresh
            return SessionState()
    return SessionState()


def save_session(state: SessionState) -> None:
    """Save session state to disk."""
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    SESSION_FILE.write_text(json.dumps(state.to_dict(), indent=2))
