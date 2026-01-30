"""
MH1 Client Selector
Manages client selection, session persistence, fuzzy matching, and deduplication.

Features:
- Query Firebase for available clients
- Fuzzy match clients by name or ID (normalized matching)
- Deduplication check on client creation
- Persist active client selection
- Session-aware client context
- Alias support for client name variations

Usage:
    from lib.client_selector import (
        ClientSelector,
        get_client_selector,
        normalize_name,
        check_duplicate_client,
        DuplicateClientError,
    )

    selector = get_client_selector()

    # List all clients
    clients = selector.list_clients()

    # Select by fuzzy match (only existing clients)
    client = selector.select_client("swimply inc")  # Finds "Swimply"

    # Create client with deduplication check
    try:
        new_client = selector.create_client("Swimply Inc")
    except DuplicateClientError as e:
        print(e)  # "Similar client exists: Swimply (swimply). Use --force-create to proceed."

    # Force create (bypass deduplication)
    new_client = selector.create_client("Swimply Inc", force_create=True)

    # Get active client
    active = selector.get_active_client()
"""

import os
import re
import uuid
import threading
from typing import Optional, List, Tuple, Dict, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
import logging
from difflib import SequenceMatcher

from .firebase_client import get_firebase_client, FirebaseError
from .workflow_state import (
    WorkflowPhase,
    get_client_workflow_state,
    WorkflowMetrics,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Name Normalization & Deduplication Functions
# =============================================================================

def normalize_name(name: str) -> str:
    """
    Normalize a client name for comparison.

    Transforms name to lowercase, removes spaces/punctuation, and strips whitespace.

    Args:
        name: The display name to normalize

    Returns:
        Normalized name suitable for comparison

    Examples:
        >>> normalize_name("Swimply Inc")
        'swimplyinc'
        >>> normalize_name("  Acme Corp.  ")
        'acmecorp'
        >>> normalize_name("My-Company LLC")
        'mycompanyllc'
    """
    if not name:
        return ""
    # Lowercase
    normalized = name.lower()
    # Remove common punctuation and special characters
    normalized = re.sub(r'[.\-_,\'"!@#$%^&*()+=\[\]{}|\\/:;<>?~`]', '', normalized)
    # Remove all whitespace
    normalized = re.sub(r'\s+', '', normalized)
    return normalized.strip()


def check_duplicate_client(
    display_name: str,
    existing_clients: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Check if a client name matches any existing clients.

    Checks for:
    1. Exact normalized name matches (e.g., "swimply" matches "swimply")
    2. One normalized name contains the other (e.g., "swimplyinc" contains "swimply")
    3. Alias matches (if client has aliases field)

    Args:
        display_name: The proposed new client name
        existing_clients: List of existing client dicts with at least:
            - display_name or displayName
            - client_id or id or _id
            - Optional: normalized_name, aliases

    Returns:
        List of matching client dicts (empty if no duplicates found)
    """
    if not display_name or not existing_clients:
        return []

    query_normalized = normalize_name(display_name)
    if not query_normalized:
        return []

    matches = []

    for client in existing_clients:
        # Get client display name
        client_display = client.get("displayName") or client.get("display_name") or ""
        client_id = client.get("_id") or client.get("id") or client.get("client_id") or ""

        # Check normalized name match
        # Use stored normalized_name if available, otherwise compute it
        client_normalized = client.get("normalized_name") or normalize_name(client_display)

        # Exact match (highest priority)
        if query_normalized == client_normalized:
            matches.append({
                "client_id": client_id,
                "display_name": client_display,
                "match_type": "normalized_name",
                "normalized_name": client_normalized,
            })
            continue

        # Check alias matches (second priority - more specific than containment)
        aliases = client.get("aliases", [])
        alias_matched = False
        if aliases:
            for alias in aliases:
                alias_normalized = normalize_name(alias)
                if query_normalized == alias_normalized:
                    matches.append({
                        "client_id": client_id,
                        "display_name": client_display,
                        "match_type": "alias",
                        "matched_alias": alias,
                    })
                    alias_matched = True
                    break

        if alias_matched:
            continue

        # Containment match: "swimplyinc" contains "swimply" OR "swimply" contains "swimplyinc"
        # This handles cases like "Swimply Inc" matching "Swimply"
        if (client_normalized and query_normalized and
            (client_normalized in query_normalized or query_normalized in client_normalized)):
            matches.append({
                "client_id": client_id,
                "display_name": client_display,
                "match_type": "normalized_contains",
                "normalized_name": client_normalized,
            })
            continue

    return matches


class DuplicateClientError(Exception):
    """Raised when attempting to create a client that already exists."""

    def __init__(self, display_name: str, duplicates: List[Dict[str, Any]]):
        self.display_name = display_name
        self.duplicates = duplicates

        # Build message
        dup_descriptions = []
        for dup in duplicates:
            dup_descriptions.append(f"{dup['display_name']} ({dup['client_id']})")

        message = (
            f"Similar client exists: {', '.join(dup_descriptions)}. "
            f"Use --force-create to proceed."
        )
        super().__init__(message)

# Base paths
SYSTEM_ROOT = Path(__file__).parent.parent
INPUTS_DIR = SYSTEM_ROOT / "inputs"
CLIENTS_DIR = SYSTEM_ROOT / "clients"


@dataclass
class ClientSummary:
    """Summary information for client list display."""
    client_id: str
    display_name: str
    current_phase: WorkflowPhase
    metrics: Optional[WorkflowMetrics] = None
    website: str = ""
    created_at: str = ""
    normalized_name: str = ""
    aliases: List[str] = field(default_factory=list)

    @property
    def phase_label(self) -> str:
        """Human-readable phase label."""
        labels = {
            WorkflowPhase.NOT_STARTED: "Not Started",
            WorkflowPhase.ONBOARDED: "Onboarded",
            WorkflowPhase.DISCOVERED: "Discovered",
            WorkflowPhase.CONFIGURED: "Configured",
            WorkflowPhase.SIGNALS_COLLECTED: "Signals Ready",
            WorkflowPhase.BRIEFS_CURATED: "Briefs Ready",
            WorkflowPhase.CONTENT_CREATED: "Content Ready",
            WorkflowPhase.DELIVERED: "Delivered",
        }
        return labels.get(self.current_phase, self.current_phase.value)

    @property
    def metrics_summary(self) -> str:
        """Short metrics summary for display."""
        if not self.metrics:
            return ""
        parts = []
        if self.metrics.unused_signals_count > 0:
            parts.append(f"{self.metrics.unused_signals_count} signals")
        if self.metrics.briefs_ready_count > 0:
            parts.append(f"{self.metrics.briefs_ready_count} briefs")
        if self.metrics.posts_approved_count > 0:
            parts.append(f"{self.metrics.posts_approved_count} posts")
        return ", ".join(parts) if parts else "no pending items"


@dataclass
class ActiveClient:
    """
    Active client with full session context.

    Persisted to inputs/active_client.md and Firebase sessions.
    """
    client_id: str
    display_name: str
    current_phase: WorkflowPhase
    persona: Optional[Any] = None  # AgentPersona, imported lazily to avoid circular
    selected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Additional context
    website: str = ""
    industry: str = ""
    metrics: Optional[WorkflowMetrics] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "client_id": self.client_id,
            "display_name": self.display_name,
            "current_phase": self.current_phase.value,
            "selected_at": self.selected_at,
            "session_id": self.session_id,
            "website": self.website,
            "industry": self.industry,
            "metrics": asdict(self.metrics) if self.metrics else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActiveClient":
        """Create from dictionary."""
        phase_str = data.get("current_phase", "not_started")
        try:
            phase = WorkflowPhase(phase_str)
        except ValueError:
            phase = WorkflowPhase.NOT_STARTED

        metrics_data = data.get("metrics")
        metrics = None
        if metrics_data:
            metrics = WorkflowMetrics(
                signals_count=metrics_data.get("signals_count", 0),
                unused_signals_count=metrics_data.get("unused_signals_count", 0),
                briefs_total_count=metrics_data.get("briefs_total_count", 0),
                briefs_ready_count=metrics_data.get("briefs_ready_count", 0),
                posts_draft_count=metrics_data.get("posts_draft_count", 0),
                posts_approved_count=metrics_data.get("posts_approved_count", 0),
                posts_synced_count=metrics_data.get("posts_synced_count", 0),
            )

        return cls(
            client_id=data.get("client_id", ""),
            display_name=data.get("display_name", data.get("client_id", "")),
            current_phase=phase,
            selected_at=data.get("selected_at", datetime.now(timezone.utc).isoformat()),
            session_id=data.get("session_id", str(uuid.uuid4())),
            website=data.get("website", ""),
            industry=data.get("industry", ""),
            metrics=metrics,
        )


class ClientSelector:
    """
    Manages client selection and session persistence.

    Provides:
    - List clients from Firebase
    - Fuzzy match for client selection
    - Active client persistence (local + Firebase)
    - Session management
    """

    def __init__(self, inputs_dir: Path = None):
        """
        Initialize client selector.

        Args:
            inputs_dir: Directory for active_client.md (default: inputs/)
        """
        self.inputs_dir = inputs_dir or INPUTS_DIR
        self.inputs_dir.mkdir(parents=True, exist_ok=True)
        self._active_client_path = self.inputs_dir / "active_client.md"
        self._lock = threading.RLock()
        self._cached_active: Optional[ActiveClient] = None

    def list_clients(self, limit: int = 50) -> List[ClientSummary]:
        """
        Query Firebase for all clients.

        Returns:
            List of ClientSummary objects sorted by most recently updated.
        """
        try:
            fb = get_firebase_client()
            # Try to get clients ordered by update time, fall back to unordered
            # (some clients may not have _updated_at field)
            clients_data = fb.get_collection(
                "clients",
                limit=limit,
                order_by="_updated_at",
                order_direction="DESCENDING"
            )

            # Fallback if no results (field may not exist on all docs)
            if not clients_data:
                clients_data = fb.get_collection("clients", limit=limit)

            summaries = []
            for client_data in clients_data:
                client_id = client_data.get("_id", client_data.get("id", ""))
                if not client_id:
                    continue

                # Get workflow state for this client
                try:
                    state = get_client_workflow_state(client_id)
                    phase = state.current_phase
                    metrics = state.metrics
                except Exception:
                    phase = WorkflowPhase.NOT_STARTED
                    metrics = None

                display_name = client_data.get("displayName", client_data.get("name", client_id))
                # Get or compute normalized name
                normalized = client_data.get("normalized_name") or normalize_name(display_name)
                aliases = client_data.get("aliases", [])

                summary = ClientSummary(
                    client_id=client_id,
                    display_name=display_name,
                    current_phase=phase,
                    metrics=metrics,
                    website=client_data.get("website", ""),
                    created_at=client_data.get("_created_at", ""),
                    normalized_name=normalized,
                    aliases=aliases if isinstance(aliases, list) else [],
                )
                summaries.append(summary)

            return summaries

        except FirebaseError as e:
            logger.error(f"Failed to list clients from Firebase: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing clients: {e}")
            return []

    def select_client(self, query: str) -> Optional[ActiveClient]:
        """
        Select an EXISTING client by fuzzy matching name or ID.

        This method ONLY selects existing clients - it never creates new ones.
        For client creation, use create_client() instead.

        Args:
            query: Search query (partial name, ID, or index number)

        Returns:
            ActiveClient if found, None otherwise
        """
        query = query.strip().lower()

        if not query:
            return None

        clients = self.list_clients()

        if not clients:
            logger.warning("No clients found in Firebase")
            return None

        # Try exact ID match first
        for client in clients:
            if client.client_id.lower() == query:
                return self._create_active_client(client)

        # Try numeric index
        if query.isdigit():
            idx = int(query) - 1  # 1-based index
            if 0 <= idx < len(clients):
                return self._create_active_client(clients[idx])

        # Check normalized name match (for queries like "swimply inc" -> "Swimply")
        query_normalized = normalize_name(query)
        for client in clients:
            if client.normalized_name == query_normalized:
                logger.info(f"Normalized match: '{query}' -> '{client.display_name}'")
                return self._create_active_client(client)

        # Check alias matches
        for client in clients:
            for alias in client.aliases:
                if normalize_name(alias) == query_normalized:
                    logger.info(f"Alias match: '{query}' -> '{client.display_name}' (via alias '{alias}')")
                    return self._create_active_client(client)

        # Fuzzy match on display name and ID
        best_match = None
        best_score = 0.0

        for client in clients:
            # Score against display name
            name_score = SequenceMatcher(
                None,
                query,
                client.display_name.lower()
            ).ratio()

            # Score against client ID
            id_score = SequenceMatcher(
                None,
                query,
                client.client_id.lower()
            ).ratio()

            # Score against normalized name
            normalized_score = SequenceMatcher(
                None,
                query_normalized,
                client.normalized_name
            ).ratio()

            # Also check if query is a substring
            if query in client.display_name.lower():
                name_score = max(name_score, 0.8)
            if query in client.client_id.lower():
                id_score = max(id_score, 0.8)
            if query_normalized in client.normalized_name:
                normalized_score = max(normalized_score, 0.85)

            score = max(name_score, id_score, normalized_score)

            if score > best_score:
                best_score = score
                best_match = client

        # Require minimum confidence
        if best_match and best_score >= 0.4:
            logger.info(f"Fuzzy matched '{query}' to '{best_match.display_name}' (score: {best_score:.2f})")
            return self._create_active_client(best_match)

        logger.warning(f"No existing client matched query '{query}'")
        return None

    def _create_active_client(self, summary: ClientSummary) -> ActiveClient:
        """Create ActiveClient from ClientSummary."""
        return ActiveClient(
            client_id=summary.client_id,
            display_name=summary.display_name,
            current_phase=summary.current_phase,
            metrics=summary.metrics,
            website=summary.website,
        )

    def create_client(
        self,
        display_name: str,
        force_create: bool = False,
        website: str = "",
        industry: str = "",
        aliases: Optional[List[str]] = None,
    ) -> ActiveClient:
        """
        Create a new client with deduplication check.

        Before creating, checks for duplicate clients by normalized name or alias.
        If duplicates are found and force_create is False, raises DuplicateClientError.

        Args:
            display_name: The display name for the new client
            force_create: If True, bypass duplicate check (--force-create flag)
            website: Optional website URL
            industry: Optional industry classification
            aliases: Optional list of alternative names for this client

        Returns:
            ActiveClient for the newly created client

        Raises:
            DuplicateClientError: If similar client exists and force_create is False
            ValueError: If display_name is empty
        """
        if not display_name or not display_name.strip():
            raise ValueError("Client display_name cannot be empty")

        display_name = display_name.strip()

        # Check for duplicates unless force_create is set
        if not force_create:
            clients = self.list_clients()

            # Convert ClientSummary list to dict format for check_duplicate_client
            existing_clients = [
                {
                    "_id": c.client_id,
                    "displayName": c.display_name,
                    "normalized_name": c.normalized_name,
                    "aliases": c.aliases,
                }
                for c in clients
            ]

            duplicates = check_duplicate_client(display_name, existing_clients)

            if duplicates:
                raise DuplicateClientError(display_name, duplicates)

        # Generate client ID (slug)
        client_id = self._generate_client_id(display_name)

        # Compute normalized name
        normalized = normalize_name(display_name)

        # Prepare client data
        now = datetime.now(timezone.utc).isoformat()
        client_data = {
            "displayName": display_name,
            "normalized_name": normalized,
            "aliases": aliases or [],
            "website": website,
            "industry": industry,
            "_created_at": now,
            "_updated_at": now,
        }

        # Save to Firebase
        try:
            fb = get_firebase_client()
            fb.set_document("clients", client_id, client_data)
            logger.info(f"Created new client: {display_name} ({client_id})")
        except FirebaseError as e:
            logger.error(f"Failed to create client in Firebase: {e}")
            raise

        # Create and return ActiveClient
        return ActiveClient(
            client_id=client_id,
            display_name=display_name,
            current_phase=WorkflowPhase.NOT_STARTED,
            website=website,
            industry=industry,
        )

    def _generate_client_id(self, display_name: str) -> str:
        """
        Generate a URL-safe client ID (slug) from display name.

        Args:
            display_name: The display name to convert

        Returns:
            A lowercase, hyphenated slug suitable for use as client_id
        """
        # Lowercase
        slug = display_name.lower()
        # Replace spaces and underscores with hyphens
        slug = re.sub(r'[\s_]+', '-', slug)
        # Remove non-alphanumeric characters (except hyphens)
        slug = re.sub(r'[^a-z0-9\-]', '', slug)
        # Remove consecutive hyphens
        slug = re.sub(r'-+', '-', slug)
        # Strip leading/trailing hyphens
        slug = slug.strip('-')

        return slug or "client"

    def add_alias(self, client_id: str, alias: str) -> bool:
        """
        Add an alias to an existing client.

        Args:
            client_id: The client ID to update
            alias: The alias to add

        Returns:
            True if successful, False otherwise
        """
        try:
            fb = get_firebase_client()
            client_data = fb.get_document("clients", client_id)

            if not client_data:
                logger.error(f"Client not found: {client_id}")
                return False

            aliases = client_data.get("aliases", [])
            if alias not in aliases:
                aliases.append(alias)

            fb.set_document(
                "clients",
                client_id,
                {
                    "aliases": aliases,
                    "_updated_at": datetime.now(timezone.utc).isoformat(),
                },
                merge=True
            )
            logger.info(f"Added alias '{alias}' to client {client_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to add alias: {e}")
            return False

    def get_active_client(self) -> Optional[ActiveClient]:
        """
        Get the currently active client.

        Reads from inputs/active_client.md file.

        Returns:
            ActiveClient if one is selected, None otherwise
        """
        with self._lock:
            if not self._active_client_path.exists():
                return None

            try:
                content = self._active_client_path.read_text()

                # Parse YAML-style content
                client_id = None
                display_name = None

                for line in content.split('\n'):
                    line_lower = line.lower().strip()

                    # Match client_id: "value" or client_id: value
                    if 'client_id' in line_lower:
                        match = re.search(r'["\']?([^"\':\s]+)["\']?\s*$', line.split(':')[-1])
                        if match:
                            client_id = match.group(1).strip('"\'')

                    # Match display_name or client_name
                    elif 'display_name' in line_lower or 'client_name' in line_lower:
                        match = re.search(r'["\']?([^"\']+)["\']?\s*$', line.split(':')[-1])
                        if match:
                            display_name = match.group(1).strip('"\'')

                if not client_id:
                    return None

                # Get current workflow state from Firebase
                try:
                    state = get_client_workflow_state(client_id)
                    phase = state.current_phase
                    metrics = state.metrics
                except Exception:
                    phase = WorkflowPhase.NOT_STARTED
                    metrics = None

                return ActiveClient(
                    client_id=client_id,
                    display_name=display_name or client_id,
                    current_phase=phase,
                    metrics=metrics,
                )

            except Exception as e:
                logger.error(f"Failed to read active client: {e}")
                return None

    def persist_selection(self, client: ActiveClient) -> bool:
        """
        Persist active client selection.

        Writes to:
        1. inputs/active_client.md (local file)
        2. Firebase system/sessions/{session_id}/active_client

        Args:
            client: ActiveClient to persist

        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            try:
                # Write to local file
                content = f"""# Active Client

```yaml
client_id: "{client.client_id}"
display_name: "{client.display_name}"
session_id: "{client.session_id}"
```

Selected at: {client.selected_at}
"""
                self._active_client_path.write_text(content)
                logger.info(f"Persisted active client to {self._active_client_path}")

                # Also write to Firebase for session tracking
                try:
                    fb = get_firebase_client()
                    fb.set_document(
                        "system",
                        "sessions",
                        client.to_dict(),
                        merge=True,
                        subcollection="active_clients",
                        subdoc_id=client.session_id
                    )
                    logger.info(f"Persisted session to Firebase: {client.session_id}")
                except Exception as e:
                    logger.warning(f"Could not persist to Firebase (non-fatal): {e}")

                self._cached_active = client
                return True

            except Exception as e:
                logger.error(f"Failed to persist active client: {e}")
                return False

    def clear_selection(self) -> bool:
        """
        Clear the active client selection.

        Returns:
            True if successful
        """
        with self._lock:
            try:
                if self._active_client_path.exists():
                    self._active_client_path.unlink()
                self._cached_active = None
                return True
            except Exception as e:
                logger.error(f"Failed to clear selection: {e}")
                return False

    def search_clients(self, query: str) -> List[Tuple[ClientSummary, float]]:
        """
        Search clients with relevance scores.

        Searches across display name, client ID, normalized name, and aliases.

        Args:
            query: Search query

        Returns:
            List of (ClientSummary, score) tuples, sorted by score descending
        """
        query = query.lower().strip()
        query_normalized = normalize_name(query)
        clients = self.list_clients()

        scored = []
        for client in clients:
            name_score = SequenceMatcher(None, query, client.display_name.lower()).ratio()
            id_score = SequenceMatcher(None, query, client.client_id.lower()).ratio()
            normalized_score = SequenceMatcher(None, query_normalized, client.normalized_name).ratio()

            # Check aliases
            alias_score = 0.0
            for alias in client.aliases:
                alias_normalized = normalize_name(alias)
                alias_match = SequenceMatcher(None, query_normalized, alias_normalized).ratio()
                alias_score = max(alias_score, alias_match)

            # Boost for substring matches
            if query in client.display_name.lower():
                name_score = max(name_score, 0.8)
            if query in client.client_id.lower():
                id_score = max(id_score, 0.8)
            if query_normalized in client.normalized_name:
                normalized_score = max(normalized_score, 0.85)

            # Exact normalized match gets highest score
            if query_normalized == client.normalized_name:
                normalized_score = 1.0

            score = max(name_score, id_score, normalized_score, alias_score)
            if score > 0.2:
                scored.append((client, score))

        return sorted(scored, key=lambda x: x[1], reverse=True)


# Singleton accessor
_selector_instance: Optional[ClientSelector] = None
_selector_lock = threading.Lock()


def get_client_selector() -> ClientSelector:
    """Get or create the global ClientSelector instance."""
    global _selector_instance

    with _selector_lock:
        if _selector_instance is None:
            _selector_instance = ClientSelector()
        return _selector_instance


def get_active_client_id() -> Optional[str]:
    """Convenience function to get just the active client ID."""
    selector = get_client_selector()
    active = selector.get_active_client()
    return active.client_id if active else None


if __name__ == "__main__":
    # Test basic functionality
    print("Client Selector Module")
    print("=" * 50)

    selector = ClientSelector()

    print("\nListing clients...")
    clients = selector.list_clients()

    if clients:
        print(f"\nFound {len(clients)} clients:")
        for i, client in enumerate(clients, 1):
            print(f"  [{i}] {client.display_name} ({client.phase_label})")
            if client.metrics_summary:
                print(f"      - {client.metrics_summary}")
    else:
        print("No clients found (Firebase may not be configured)")

    print("\nCurrent active client:")
    active = selector.get_active_client()
    if active:
        print(f"  {active.display_name} ({active.client_id})")
    else:
        print("  None selected")
