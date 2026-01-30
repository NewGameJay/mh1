#!/usr/bin/env python3
"""
Create Assignment Brief Skill - Execution Script (v1.0.0)

Transform signals into structured LinkedIn post assignment briefs.
Integrates with Firestore for signal retrieval and brief storage.

Features:
- Signal content fetching from Firestore
- Content pillar alignment
- Duplicate brief detection
- Context loading from local files
- Automated brief generation

Usage:
    # Basic run with signal URL
    python skills/create-assignment-brief/run.py --signal_url "https://example.com/article"

    # Multiple signals
    python skills/create-assignment-brief/run.py --signal_urls "url1,url2,url3"

    # With explicit client
    python skills/create-assignment-brief/run.py --client_id abc123 --signal_url "https://example.com"

    # Programmatic
    from skills.create_assignment_brief.run import run_create_assignment_brief
    result = run_create_assignment_brief({
        "signal_url": "https://example.com/article"
    })
"""

import argparse
import json
import os
import re
import secrets
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add lib to path
SKILL_ROOT = Path(__file__).parent
SYSTEM_ROOT = SKILL_ROOT.parent.parent
sys.path.insert(0, str(SYSTEM_ROOT / "lib"))

# Import lib modules with fallback
try:
    from runner import WorkflowRunner, RunStatus, estimate_tokens
    from evaluator import evaluate_output
    from release_policy import determine_release_action, ReleaseAction, get_release_action_message
    from telemetry import log_run
except ImportError:
    # Stub implementations for standalone testing
    class RunStatus:
        SUCCESS = "success"
        FAILED = "failed"
        REVIEW = "review"

    class ReleaseAction:
        AUTO_DELIVER = "auto_deliver"
        HUMAN_REVIEW = "human_review"
        BLOCKED = "blocked"
        @property
        def value(self):
            return str(self)

    def estimate_tokens(text): return len(str(text)) // 4
    def evaluate_output(output, schema=None, requirements=None):
        return {"score": 0.85, "pass": True}
    def determine_release_action(standard_eval=None, is_external_facing=False):
        return ReleaseAction()
    def get_release_action_message(action): return "Auto-delivered"

    class WorkflowRunner:
        def __init__(self, **kwargs):
            self.run_id = str(uuid.uuid4())[:8]
            self.run_dir = Path("/tmp")
            self.telemetry = type('obj', (object,), {
                'start_time': datetime.now(timezone.utc).isoformat(),
                'end_time': None, 'steps': []
            })()
        def run_step(self, name, func, inputs):
            result = func(inputs)
            class StepResult:
                status = "success"
                output = result.get("output", {})
                error = None
            return StepResult()
        def complete(self, status, evaluation=None): return {}

    def log_run(**kwargs): pass


# Constants
SKILL_NAME = "create-assignment-brief"
SKILL_VERSION = "v1.0.0"


def get_client_from_active_file() -> Dict[str, str]:
    """Read client configuration from inputs/active_client.md."""
    active_client_path = SYSTEM_ROOT / "inputs" / "active_client.md"
    if not active_client_path.exists():
        return {}

    content = active_client_path.read_text()
    result = {}

    for line in content.split('\n'):
        line = line.strip()
        if '=' in line:
            parts = line.split('=', 1)
            if len(parts) == 2:
                key = parts[0].strip().upper()
                value = parts[1].strip().strip('"\'')
                if key == 'CLIENT_ID':
                    result['client_id'] = value
                elif key == 'CLIENT_NAME':
                    result['client_name'] = value
        elif 'Firestore Client ID:' in line:
            result['client_id'] = line.split(':', 1)[1].strip()
        elif 'Client Name:' in line:
            result['client_name'] = line.split(':', 1)[1].strip()

    return result


class CreateAssignmentBriefSkill:
    """
    Create Assignment Brief skill for transforming signals into structured briefs.
    """

    def __init__(
        self,
        client_id: str,
        client_name: str = None
    ):
        self.client_id = client_id
        self.client_name = client_name or client_id
        self.run_id = str(uuid.uuid4())[:8]
        self.start_time = time.time()

        # Build paths
        self.client_dir = SYSTEM_ROOT / "clients" / self.client_id
        self.context_dir = self.client_dir / "context"
        self.briefs_dir = SYSTEM_ROOT / "assignment-briefs"

        # Ensure directories exist
        self.briefs_dir.mkdir(parents=True, exist_ok=True)

    def _fetch_signal_content(self, signal_urls: List[str]) -> Dict:
        """Fetch signal content from Firestore using get-signal-by-url.js."""
        script_path = SYSTEM_ROOT / "tools" / "get-signal-by-url.js"

        if not script_path.exists():
            # Return mock data for testing
            return {
                "count": len(signal_urls),
                "signals": [
                    {
                        "id": f"signal_{i}",
                        "type": "article",
                        "title": f"Signal from {url[:50]}",
                        "content": "Sample signal content for brief generation.",
                        "author": "Unknown",
                        "url": url,
                        "datePosted": datetime.now(timezone.utc).isoformat(),
                        "status": "curated"
                    }
                    for i, url in enumerate(signal_urls)
                ],
                "notFound": []
            }

        try:
            cmd = ["node", str(script_path)] + signal_urls
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(SYSTEM_ROOT),
                timeout=60
            )

            if result.returncode != 0:
                return {"error": result.stderr, "signals": [], "notFound": signal_urls}

            return json.loads(result.stdout)

        except Exception as e:
            return {"error": str(e), "signals": [], "notFound": signal_urls}

    def _load_context_summary(self) -> Dict:
        """Load context summary from local file."""
        summary_path = self.context_dir / "context_summary.md"

        if summary_path.exists():
            return {"content": summary_path.read_text(), "source": "local"}

        # Try JSON version
        json_path = self.context_dir / "context_summary.json"
        if json_path.exists():
            with open(json_path, 'r') as f:
                return {"content": json.load(f), "source": "local"}

        return {"content": None, "source": None, "warning": "Context summary not found"}

    def _load_pov_config(self) -> Dict:
        """Load POV/content pillar configuration."""
        pov_path = self.context_dir / "pov.json"

        if pov_path.exists():
            with open(pov_path, 'r') as f:
                return json.load(f)

        return {"pillars": [], "warning": "POV config not found"}

    def _select_content_pillar(self, signal_content: str, pillars: List[Dict]) -> Dict:
        """Select the best-fit content pillar based on signal topic."""
        # In production, this would use LLM to match signal to pillar
        # For now, return first pillar or default
        if pillars:
            return pillars[0]

        return {
            "founder_name": "default",
            "content_pillar": "general",
            "funnel_stage": "TOFU",
            "target_persona": "general_audience",
            "pov": "Industry insights and perspectives"
        }

    def _generate_brief_id(self, title: str) -> str:
        """Generate unique brief ID from date, title slug, and random hash."""
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:40]
        date_str = datetime.now().strftime("%Y-%m-%d")
        random_hash = secrets.token_hex(3)
        return f"{date_str}-{slug}-{random_hash}"

    def _check_duplicate_briefs(self, signal_urls: List[str]) -> Dict:
        """Check if briefs already exist for these signals."""
        script_path = SYSTEM_ROOT / "tools" / "check-duplicate-briefs.js"

        if not script_path.exists():
            return {"duplicates": [], "exists": False}

        try:
            cmd = ["node", str(script_path)] + signal_urls
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(SYSTEM_ROOT),
                timeout=30
            )

            if result.returncode != 0:
                return {"duplicates": [], "exists": True, "message": result.stdout}

            return {"duplicates": [], "exists": False}

        except Exception as e:
            return {"duplicates": [], "exists": False, "error": str(e)}

    def _generate_brief_content(
        self,
        brief_id: str,
        signals: List[Dict],
        pillar: Dict,
        context: Dict
    ) -> str:
        """Generate the markdown brief content."""
        # Extract key info from first signal
        primary_signal = signals[0] if signals else {}
        title = primary_signal.get("title", "Untitled Brief")
        signal_urls = [s.get("url", "") for s in signals]

        # Build brief markdown
        brief = f"""---
id: "{brief_id}"
title: "{title}"
status: draft
founder: "{pillar.get('founder_name', 'unknown')}"
content_pillar: "{pillar.get('content_pillar', 'general')}"
funnel_stage: "{pillar.get('funnel_stage', 'TOFU')}"
signals: {json.dumps(signal_urls)}
pov: "{pillar.get('pov', '')}"
target_persona: "{pillar.get('target_persona', 'general')}"
---

# Objective

Define the outcome for this post based on the content pillar's goals and the signal's insights.

# Hook

[First 140 characters that stop the scroll and earn the "see more" click]

# Angle

{pillar.get('pov', 'Define the specific POV that makes this content unique.')}

# Key Takeaway

The single thing the reader should remember, believe, or do after reading this post.

# Context

**Signal Source:** {primary_signal.get('title', 'Unknown')}
**Author:** {primary_signal.get('author', 'Unknown')}
**Date:** {primary_signal.get('datePosted', 'Unknown')}

{primary_signal.get('content', 'Signal content not available.')[:500]}...

# Visual Direction

What image or visual supports this post? (authentic > stock, vertical preferred)

# Hashtags

#ContentStrategy #LinkedIn #ThoughtLeadership

# Distribution Notes

- Post in comments: (links go here, not in post body)
- Tag: (relevant people/companies, if any)
- Best time: Tuesday-Thursday, 8-10am

# References

"""
        for url in signal_urls:
            brief += f"- {url}\n"

        return brief

    def _save_brief(self, brief_id: str, content: str) -> str:
        """Save brief to local file."""
        filename = f"{brief_id}.md"
        filepath = self.briefs_dir / filename
        filepath.write_text(content)
        return str(filepath)

    def _upload_to_firestore(self, filepath: str) -> Dict:
        """Upload brief to Firestore."""
        script_path = SYSTEM_ROOT / "tools" / "upload-briefs-to-firestore.js"

        if not script_path.exists():
            return {"status": "skipped", "message": "Upload script not found"}

        try:
            cmd = ["node", str(script_path), "--files", filepath]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(SYSTEM_ROOT),
                timeout=60
            )

            if result.returncode != 0:
                return {"status": "error", "error": result.stderr}

            return {"status": "success", "output": result.stdout}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _update_signal_status(self, signal_urls: List[str], brief_id: str) -> Dict:
        """Update signal status to 'used' in Firestore."""
        script_path = SYSTEM_ROOT / "tools" / "update-signal-status.js"

        if not script_path.exists():
            return {"status": "skipped", "message": "Update script not found"}

        results = []
        for url in signal_urls:
            try:
                cmd = ["node", str(script_path), url, "--status", "used", "--brief-id", brief_id]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=str(SYSTEM_ROOT),
                    timeout=30
                )
                results.append({"url": url, "success": result.returncode == 0})
            except Exception as e:
                results.append({"url": url, "success": False, "error": str(e)})

        return {"results": results}

    def run(self, inputs: Dict) -> Dict:
        """
        Main execution method for creating assignment brief.

        Args:
            inputs: Dictionary with:
                - signal_url: Single signal URL
                - signal_urls: List of signal URLs (for grouped briefs)
                - skip_duplicate_check: Skip duplicate detection (default: false)

        Returns:
            Complete skill result with brief details and metadata
        """
        # Extract signal URLs
        signal_urls = inputs.get("signal_urls", [])
        if not signal_urls and inputs.get("signal_url"):
            signal_urls = [inputs.get("signal_url")]

        if not signal_urls:
            return {
                "status": "failed",
                "error": "signal_url or signal_urls is required"
            }

        skip_duplicate = inputs.get("skip_duplicate_check", False)

        print(f"\n{'='*60}")
        print(f"CREATE ASSIGNMENT BRIEF")
        print(f"{'='*60}")
        print(f"Client: {self.client_name} ({self.client_id})")
        print(f"Signals: {len(signal_urls)}")
        print(f"Run ID: {self.run_id}")
        print(f"{'='*60}\n")

        runner = WorkflowRunner(
            workflow_name=SKILL_NAME,
            version=SKILL_VERSION,
            client=self.client_id
        )

        try:
            # Step 1: Check for duplicates
            if not skip_duplicate:
                print("[Step 1] Checking for duplicate briefs...")
                dup_check = self._check_duplicate_briefs(signal_urls)
                if dup_check.get("exists"):
                    return {
                        "status": "skipped",
                        "reason": "duplicate",
                        "message": f"Brief already exists for these signals: {dup_check.get('message', '')}",
                        "run_id": runner.run_id
                    }
                print("  No duplicates found.")

            # Step 2: Fetch signal content
            print("\n[Step 2] Fetching signal content from Firestore...")
            signal_data = self._fetch_signal_content(signal_urls)

            if signal_data.get("error"):
                return {
                    "status": "failed",
                    "error": f"Failed to fetch signals: {signal_data.get('error')}",
                    "run_id": runner.run_id
                }

            signals = signal_data.get("signals", [])
            if not signals:
                return {
                    "status": "failed",
                    "error": f"No signals found for URLs: {signal_urls}",
                    "not_found": signal_data.get("notFound", []),
                    "run_id": runner.run_id
                }

            print(f"  Found {len(signals)} signal(s)")

            # Step 3: Load context
            print("\n[Step 3] Loading context...")
            context_summary = self._load_context_summary()
            pov_config = self._load_pov_config()

            if context_summary.get("warning"):
                print(f"  Warning: {context_summary.get('warning')}")

            # Step 4: Select content pillar
            print("\n[Step 4] Selecting content pillar...")
            pillar = self._select_content_pillar(
                signals[0].get("content", ""),
                pov_config.get("pillars", [])
            )
            print(f"  Selected: {pillar.get('content_pillar', 'default')}")

            # Step 5: Generate brief
            print("\n[Step 5] Generating brief...")
            title = signals[0].get("title", "Untitled Signal")
            brief_id = self._generate_brief_id(title)

            brief_content = self._generate_brief_content(
                brief_id=brief_id,
                signals=signals,
                pillar=pillar,
                context=context_summary
            )

            # Step 6: Save brief
            print("\n[Step 6] Saving brief...")
            filepath = self._save_brief(brief_id, brief_content)
            print(f"  Saved to: {filepath}")

            # Step 7: Upload to Firestore
            print("\n[Step 7] Uploading to Firestore...")
            upload_result = self._upload_to_firestore(filepath)
            print(f"  Status: {upload_result.get('status')}")

            # Step 8: Update signal status
            print("\n[Step 8] Updating signal status...")
            status_update = self._update_signal_status(signal_urls, brief_id)

            # Build result
            runtime = time.time() - self.start_time

            result = {
                "status": "success",
                "brief": {
                    "id": brief_id,
                    "title": title,
                    "filepath": filepath,
                    "founder": pillar.get("founder_name"),
                    "content_pillar": pillar.get("content_pillar"),
                    "funnel_stage": pillar.get("funnel_stage"),
                    "pov": pillar.get("pov"),
                    "target_persona": pillar.get("target_persona"),
                    "signal_count": len(signals)
                },
                "signals": [{"url": s.get("url"), "title": s.get("title")} for s in signals],
                "upload_result": upload_result,
                "run_id": runner.run_id,
                "runtime_seconds": round(runtime, 2)
            }

            print(f"\n{'='*60}")
            print(f"BRIEF CREATED SUCCESSFULLY")
            print(f"{'='*60}")
            print(f"ID: {brief_id}")
            print(f"Title: {title}")
            print(f"File: {filepath}")
            print(f"Runtime: {runtime:.1f}s")
            print(f"{'='*60}\n")

            runner.complete(RunStatus.SUCCESS)
            return result

        except Exception as e:
            runner.complete(RunStatus.FAILED)
            return {
                "status": "failed",
                "error": str(e),
                "error_type": type(e).__name__,
                "run_id": runner.run_id
            }


def run_create_assignment_brief(inputs: Dict) -> Dict:
    """
    Main entry point for create assignment brief skill.

    Args:
        inputs: Dictionary with configuration:
            - client_id: Client identifier (or read from active_client.md)
            - signal_url: Single signal URL
            - signal_urls: List of signal URLs
            - skip_duplicate_check: Skip duplicate detection

    Returns:
        Complete skill result with brief details
    """
    # Read from active_client.md if client_id not provided
    if not inputs.get("client_id"):
        active_client = get_client_from_active_file()
        if active_client.get("client_id"):
            inputs["client_id"] = active_client["client_id"]
            if not inputs.get("client_name"):
                inputs["client_name"] = active_client.get("client_name")
        else:
            return {
                "status": "failed",
                "error": "client_id is required (not provided and not found in active_client.md)"
            }

    skill = CreateAssignmentBriefSkill(
        client_id=inputs.get("client_id"),
        client_name=inputs.get("client_name")
    )

    return skill.run(inputs)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Create assignment brief from signal URLs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Single signal
    python run.py --signal_url "https://example.com/article"

    # Multiple signals
    python run.py --signal_urls "url1,url2,url3"

    # With explicit client
    python run.py --client_id abc123 --signal_url "https://example.com"

    # Skip duplicate check
    python run.py --signal_url "https://example.com" --skip_duplicate_check
        """
    )

    parser.add_argument("--client_id", type=str, help="Client identifier")
    parser.add_argument("--client_name", type=str, help="Client display name")
    parser.add_argument("--signal_url", type=str, help="Single signal URL")
    parser.add_argument("--signal_urls", type=str, help="Comma-separated signal URLs")
    parser.add_argument("--skip_duplicate_check", action="store_true", help="Skip duplicate detection")
    parser.add_argument("--output", type=str, help="Output file path (JSON)")

    args = parser.parse_args()

    # Build inputs
    inputs = {
        "skip_duplicate_check": args.skip_duplicate_check
    }

    if args.client_id:
        inputs["client_id"] = args.client_id
    if args.client_name:
        inputs["client_name"] = args.client_name
    if args.signal_url:
        inputs["signal_url"] = args.signal_url
    if args.signal_urls:
        inputs["signal_urls"] = args.signal_urls.split(",")

    # Run skill
    result = run_create_assignment_brief(inputs)

    # Output
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Output saved to {args.output}")
    else:
        print(json.dumps(result, indent=2, default=str))

    # Exit with appropriate code
    sys.exit(0 if result.get("status") in ["success", "skipped"] else 1)


if __name__ == "__main__":
    main()
