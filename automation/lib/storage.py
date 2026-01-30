"""
MH1 Storage & Artifact Management
Handles persistent state, file I/O, and artifact versioning.
The "Memory" of the system.
"""

import json
import shutil
from pathlib import Path
from typing import Any, Optional, Dict, List
from datetime import datetime

SYSTEM_ROOT = Path(__file__).parent.parent
OUTPUTS_DIR = SYSTEM_ROOT.parent / "outputs"  # Store outputs outside system folder usually, or configured
ARTIFACTS_DIR = OUTPUTS_DIR / "artifacts"
STATE_DIR = SYSTEM_ROOT / "state"

# Ensure directories exist
OUTPUTS_DIR.mkdir(exist_ok=True)
ARTIFACTS_DIR.mkdir(exist_ok=True)
STATE_DIR.mkdir(exist_ok=True)

class StorageManager:
    """
    Manages file artifacts and persistent state.
    """
    
    def __init__(self, project_id: str = "default"):
        self.project_id = project_id
        self.project_state_file = STATE_DIR / f"{project_id}_state.json"

    # --- State Management ---

    def load_state(self) -> Dict[str, Any]:
        """Load persistent project state."""
        if self.project_state_file.exists():
            with open(self.project_state_file, 'r') as f:
                return json.load(f)
        return {}

    def save_state(self, state: Dict[str, Any]):
        """Save persistent project state."""
        with open(self.project_state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def update_state(self, key: str, value: Any):
        """Update a specific key in state."""
        state = self.load_state()
        state[key] = value
        self.save_state(state)

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get a value from state."""
        state = self.load_state()
        return state.get(key, default)

    # --- Artifact Management ---

    def save_artifact(self, content: Any, name: str, type: str = "json", metadata: Dict = None) -> str:
        """
        Save a generated artifact with versioning.
        Returns the absolute path to the saved file.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.{type}"
        
        # Organize by type folders
        type_dir = ARTIFACTS_DIR / type
        type_dir.mkdir(exist_ok=True)
        
        file_path = type_dir / filename
        
        meta = metadata or {}
        meta.update({
            "created_at": timestamp,
            "project_id": self.project_id,
            "original_name": name
        })

        if type == "json":
            with open(file_path, 'w') as f:
                # If content is string but type is json, try to parse
                if isinstance(content, str):
                    try:
                        content = json.loads(content)
                    except:
                        pass
                json.dump(content, f, indent=2)
        elif type in ["md", "txt"]:
            with open(file_path, 'w') as f:
                f.write(str(content))
        else:
            # Binary or other
            with open(file_path, 'wb') as f:
                f.write(content)
        
        # Save sidecar metadata
        with open(file_path.with_suffix('.meta.json'), 'w') as f:
            json.dump(meta, f, indent=2)
            
        print(f"[Storage] Saved artifact: {file_path}")
        return str(file_path)

    def list_artifacts(self, type: str = None) -> List[str]:
        """List available artifacts, optionally filtered by type."""
        if type:
            search_dir = ARTIFACTS_DIR / type
            if not search_dir.exists():
                return []
            return [str(p) for p in search_dir.glob(f"*.{type}")]
        
        return [str(p) for p in ARTIFACTS_DIR.rglob("*") if p.is_file() and not p.name.endswith('.meta.json')]

    def get_latest_artifact(self, name_pattern: str) -> Optional[str]:
        """Get the most recent artifact matching a name pattern."""
        files = sorted(ARTIFACTS_DIR.rglob(f"*{name_pattern}*"), key=lambda p: p.stat().st_mtime, reverse=True)
        # Filter out meta files
        files = [f for f in files if not f.name.endswith('.meta.json')]
        return str(files[0]) if files else None

# Factory
def get_storage(project_id: str = "default") -> StorageManager:
    return StorageManager(project_id)
