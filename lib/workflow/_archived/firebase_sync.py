"""
Firebase Sync - Pull client data from Firestore to local files.

This module syncs client data from Firestore when a client is selected,
ensuring the local context includes all data shared in previous sessions.
"""

import json
import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Try to import firebase client
try:
    from automation.lib.firebase_client import get_firebase_client, FirebaseClient, FirebaseError
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    FirebaseError = Exception


def is_firebase_configured() -> bool:
    """Check if Firebase is configured and available."""
    if not FIREBASE_AVAILABLE:
        return False

    # Check for project ID
    project_id = os.environ.get("FIREBASE_PROJECT_ID") or os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        return False

    # Check for credentials
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if creds_path and os.path.exists(creds_path):
        return True

    # Check for config/firebase-credentials.json
    config_creds = Path(__file__).parent.parent.parent / "config" / "firebase-credentials.json"
    if config_creds.exists():
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(config_creds)
        return True

    return False


def sync_client_from_firestore(
    client_id: str,
    project_root: Path = None,
    console = None
) -> Dict[str, Any]:
    """
    Sync client data from Firestore to local files.

    Args:
        client_id: The client ID to sync
        project_root: Path to project root (defaults to parent of lib/)
        console: Rich console for output (optional)

    Returns:
        Dict with sync results:
        - success: bool
        - synced: list of synced collections
        - skipped: list of skipped collections
        - error: error message if failed
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent.parent

    result = {
        "success": False,
        "synced": [],
        "skipped": [],
        "error": None
    }

    # Check if Firebase is configured
    if not is_firebase_configured():
        result["skipped"].append("firebase_not_configured")
        result["success"] = True  # Not an error, just not configured
        return result

    try:
        # Get Firebase client
        client = get_firebase_client()

        # Define what to sync from Firestore
        collections_to_sync = [
            {
                "firestore_path": f"clients/{client_id}",
                "local_path": "config/profile.yaml",
                "type": "document",
                "description": "Client profile"
            },
            {
                "firestore_path": f"clients/{client_id}/config/datasources",
                "local_path": "config/datasources.yaml",
                "type": "document",
                "description": "Data source connections"
            },
            {
                "firestore_path": f"clients/{client_id}/config/platforms",
                "local_path": "config/platforms.yaml",
                "type": "document",
                "description": "Platform settings"
            },
            {
                "firestore_path": f"clients/{client_id}/campaigns",
                "local_path": "campaigns/index.json",
                "type": "collection",
                "description": "Campaign list"
            },
            {
                "firestore_path": f"clients/{client_id}/voice-profiles",
                "local_path": "voice-profiles/index.json",
                "type": "collection",
                "description": "Voice profiles"
            },
        ]

        client_dir = project_root / "clients" / client_id

        for sync_item in collections_to_sync:
            try:
                local_file = client_dir / sync_item["local_path"]
                local_file.parent.mkdir(parents=True, exist_ok=True)

                if sync_item["type"] == "document":
                    # Parse Firestore path
                    path_parts = sync_item["firestore_path"].split("/")
                    if len(path_parts) == 2:
                        # Top-level document
                        collection, doc_id = path_parts
                        data = client.get_document(collection, doc_id)
                    elif len(path_parts) == 4:
                        # Subcollection document
                        collection, doc_id, subcoll, subdoc_id = path_parts
                        data = client.get_document(collection, doc_id, subcoll, subdoc_id)
                    else:
                        result["skipped"].append(sync_item["description"])
                        continue

                    if data:
                        # Remove internal fields
                        data = {k: v for k, v in data.items() if not k.startswith("_")}

                        # Save as YAML or JSON based on extension
                        if local_file.suffix == ".yaml":
                            with open(local_file, "w") as f:
                                yaml.dump(data, f, default_flow_style=False)
                        else:
                            with open(local_file, "w") as f:
                                json.dump(data, f, indent=2)

                        result["synced"].append(sync_item["description"])
                    else:
                        result["skipped"].append(sync_item["description"])

                elif sync_item["type"] == "collection":
                    # Parse Firestore path for collection
                    path_parts = sync_item["firestore_path"].split("/")
                    if len(path_parts) == 3:
                        # Subcollection
                        parent_coll, parent_doc, coll = path_parts
                        docs = client.get_collection(
                            coll,
                            parent_doc=parent_doc,
                            parent_collection=parent_coll,
                            limit=100
                        )
                    else:
                        result["skipped"].append(sync_item["description"])
                        continue

                    if docs:
                        # Clean and save
                        clean_docs = [
                            {k: v for k, v in doc.items() if not k.startswith("_")}
                            for doc in docs
                        ]
                        with open(local_file, "w") as f:
                            json.dump(clean_docs, f, indent=2)
                        result["synced"].append(sync_item["description"])
                    else:
                        result["skipped"].append(sync_item["description"])

            except Exception as e:
                logger.debug(f"Skipping {sync_item['description']}: {e}")
                result["skipped"].append(sync_item["description"])

        # Write sync timestamp
        sync_meta = {
            "last_sync": datetime.now().isoformat(),
            "synced": result["synced"],
            "skipped": result["skipped"]
        }
        sync_file = client_dir / "config" / ".sync_meta.json"
        sync_file.parent.mkdir(parents=True, exist_ok=True)
        with open(sync_file, "w") as f:
            json.dump(sync_meta, f, indent=2)

        result["success"] = True

    except FirebaseError as e:
        result["error"] = f"Firebase error: {e}"
        logger.warning(f"Firebase sync failed for {client_id}: {e}")
    except Exception as e:
        result["error"] = f"Sync error: {e}"
        logger.warning(f"Sync failed for {client_id}: {e}")

    return result


def show_sync_status(result: Dict[str, Any], console) -> None:
    """Display sync status to console."""
    if not console:
        return

    C = {
        "green": "#22C55E",
        "yellow": "#FBBF24",
        "gray": "#9CA3AF",
        "dim": "#4B5563",
    }

    if result.get("error"):
        console.print(f"  [{C['yellow']}]⚠ Firebase sync: {result['error']}[/]")
    elif result["synced"]:
        console.print(f"  [{C['green']}]↓ Synced from cloud: {', '.join(result['synced'])}[/]")
    elif "firebase_not_configured" in result.get("skipped", []):
        # Silently skip if Firebase not configured
        pass
    else:
        console.print(f"  [{C['dim']}]↓ No cloud data to sync[/]")


def push_client_to_firestore(
    client_id: str,
    data: Dict[str, Any],
    collection: str = "profile",
    project_root: Path = None
) -> bool:
    """
    Push local client data to Firestore.

    Args:
        client_id: The client ID
        data: Data to push
        collection: Subcollection name (profile, config, etc.)
        project_root: Path to project root

    Returns:
        True if successful
    """
    if not is_firebase_configured():
        return False

    try:
        client = get_firebase_client()

        if collection == "profile":
            # Top-level client document
            client.set_document("clients", client_id, data, merge=True)
        else:
            # Subcollection document
            client.set_document("clients", client_id, data, merge=True,
                              subcollection="config", subdoc_id=collection)

        return True
    except Exception as e:
        logger.warning(f"Failed to push to Firestore: {e}")
        return False
