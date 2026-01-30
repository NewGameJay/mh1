#!/usr/bin/env python3
"""
Checkpoint manager for ghostwrite workflow state.
Multi-client marketing platform - mh1-hq structure.

Tracks stage progress so workflow can resume cleanly after context exhaustion.

Usage:
    python checkpoint.py <campaign_dir> load
    python checkpoint.py <campaign_dir> save <stage> [batches_json]
    python checkpoint.py <campaign_dir> complete <stage>
    python checkpoint.py <campaign_dir> init <client_id> <founder_id>

Commands:
    load     - Load existing checkpoint (returns JSON)
    save     - Save current stage progress
    complete - Mark a stage as fully completed
    init     - Initialize new checkpoint
"""

import json
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

CHECKPOINT_FILE = "checkpoint.json"


def load_checkpoint(campaign_dir):
    """Load existing checkpoint or return None."""
    path = os.path.join(campaign_dir, CHECKPOINT_FILE)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def save_checkpoint(campaign_dir, state):
    """Save checkpoint state to disk."""
    os.makedirs(campaign_dir, exist_ok=True)
    path = os.path.join(campaign_dir, CHECKPOINT_FILE)
    state["lastUpdated"] = datetime.now(timezone.utc).isoformat()

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    print(f"Checkpoint saved: stage {state.get('currentStage')}", file=sys.stderr)
    return path


def init_checkpoint(campaign_dir, client_id, founder_id):
    """Initialize a new checkpoint for a fresh run."""
    run_id = os.path.basename(campaign_dir)
    state = {
        "runId": run_id,
        "clientId": client_id,
        "founderId": founder_id,
        "currentStage": "0",
        "completedStages": [],
        "batchesCompleted": {},
        "files": {},
        "createdAt": datetime.now(timezone.utc).isoformat()
    }
    save_checkpoint(campaign_dir, state)
    return state


def update_stage(campaign_dir, stage, batches=None, client_id=None, client_name=None):
    """Update checkpoint with current stage and optional batch progress."""
    state = load_checkpoint(campaign_dir) or {
        "runId": os.path.basename(campaign_dir),
        "clientId": client_id,
        "clientName": client_name,
        "completedStages": [],
        "batchesCompleted": {},
        "files": {}
    }

    state["currentStage"] = stage

    if batches:
        state["batchesCompleted"][stage] = batches

    save_checkpoint(campaign_dir, state)
    return state


def complete_stage(campaign_dir, stage):
    """Mark a stage as fully completed."""
    state = load_checkpoint(campaign_dir) or {
        "runId": os.path.basename(campaign_dir),
        "completedStages": [],
        "batchesCompleted": {},
        "files": {}
    }

    if stage not in state["completedStages"]:
        state["completedStages"].append(stage)

    state["currentStage"] = None
    save_checkpoint(campaign_dir, state)
    return state


def main():
    """CLI interface for checkpoint operations."""
    if len(sys.argv) < 3:
        print("Usage:", file=sys.stderr)
        print("  checkpoint.py <campaign_dir> load", file=sys.stderr)
        print("  checkpoint.py <campaign_dir> save <stage> [batches_json]", file=sys.stderr)
        print("  checkpoint.py <campaign_dir> complete <stage>", file=sys.stderr)
        print("  checkpoint.py <campaign_dir> init <client_id> <founder_id>", file=sys.stderr)
        sys.exit(1)

    campaign_dir = sys.argv[1]
    action = sys.argv[2]

    if action == "load":
        state = load_checkpoint(campaign_dir)
        if state:
            state["exists"] = True
            print(json.dumps(state))
        else:
            print(json.dumps({"exists": False}))

    elif action == "init":
        if len(sys.argv) < 5:
            print("ERROR: init requires client_id and founder_id", file=sys.stderr)
            sys.exit(1)
        client_id = sys.argv[3]
        founder_id = sys.argv[4]
        state = init_checkpoint(campaign_dir, client_id, founder_id)
        print(json.dumps({
            "initialized": True,
            "runId": state["runId"],
            "clientId": client_id
        }))

    elif action == "save":
        if len(sys.argv) < 4:
            print("ERROR: save requires stage argument", file=sys.stderr)
            sys.exit(1)
        stage = sys.argv[3]
        batches = json.loads(sys.argv[4]) if len(sys.argv) > 4 else None
        state = update_stage(campaign_dir, stage, batches)
        print(json.dumps({
            "saved": True,
            "stage": stage,
            "batchesCompleted": state.get("batchesCompleted", {}).get(stage, [])
        }))

    elif action == "complete":
        if len(sys.argv) < 4:
            print("ERROR: complete requires stage argument", file=sys.stderr)
            sys.exit(1)
        stage = sys.argv[3]
        state = complete_stage(campaign_dir, stage)
        print(json.dumps({
            "completed": True,
            "stage": stage,
            "completedStages": state["completedStages"]
        }))

    else:
        print(f"ERROR: Unknown action '{action}'", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
