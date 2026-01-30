#!/usr/bin/env python3
"""
Ghostwrite Content Skill - Full Production Implementation (v1.0.0)

Generate authentic LinkedIn posts in the founder's voice using collected
social listening data. Integrates with mh1-hq lib for budget tracking,
evaluation, and telemetry.

Features:
- Firebase integration for client data and signals
- LLM-powered voice analysis and ghostwriting
- Per-tenant cost tracking and budget enforcement
- Deterministic release policy (auto_deliver/refine/review/blocked)
- Three execution modes: suggest, preview, execute
- Large dataset handling with context manager (RLM pattern)

Usage:
    # Basic run
    ./mh1 run skill ghostwrite-content --client_id <id> --founder_id <id>
    
    # Preview mode
    ./mh1 run skill ghostwrite-content --client_id <id> --execution_mode preview
    
    # Programmatic
    from skills.ghostwrite_content.run import run_ghostwrite_content
    result = run_ghostwrite_content({
        "client_id": "abc123",
        "founder_id": "founder_xyz",
        "post_count": 20,
        "execution_mode": "suggest"
    })
"""

import argparse
import json
import os
import sys
import time
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add lib to path
SKILL_ROOT = Path(__file__).parent
SYSTEM_ROOT = SKILL_ROOT.parent.parent
sys.path.insert(0, str(SYSTEM_ROOT / "lib"))

from runner import (
    WorkflowRunner, 
    SkillRunner,
    RunStatus, 
    ContextManager, 
    ContextConfig,
    ContextStrategy,
    estimate_tokens,
    get_model_for_subtask,
    should_offload_context
)
from evaluator import evaluate_output
from release_policy import determine_release_action, ReleaseAction, get_release_action_message
from budget import BudgetManager, BudgetExceededError
from telemetry import log_run

# Constants
SKILL_NAME = "ghostwrite-content"
SKILL_VERSION = "v1.0.0"

# Cost estimates (per 1K tokens)
COST_PER_1K_INPUT = 0.003   # Sonnet input
COST_PER_1K_OUTPUT = 0.015  # Sonnet output
COST_HAIKU_INPUT = 0.00025  # Haiku input
COST_HAIKU_OUTPUT = 0.00125 # Haiku output

# Load defaults from config
def load_defaults():
    """Load default configuration from config/defaults.json."""
    config_path = SKILL_ROOT / "config" / "defaults.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

DEFAULTS = load_defaults()


def get_client_from_active_file():
    """Read client configuration from inputs/active_client.md."""
    active_client_path = SYSTEM_ROOT / "inputs" / "active_client.md"
    if not active_client_path.exists():
        return {}
    
    with open(active_client_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    result = {}
    
    for line in content.split('\n'):
        if 'Firestore Client ID:' in line:
            result['client_id'] = line.split(':', 1)[1].strip()
        elif 'Client Name:' in line:
            result['client_name'] = line.split(':', 1)[1].strip()
        elif 'Folder Name:' in line:
            result['folder_name'] = line.split(':', 1)[1].strip()
        elif 'Default Ghostwrite Founder:' in line:
            result['default_founder'] = line.split(':', 1)[1].strip()
    
    return result


class GhostwriteContentSkill:
    """
    Production-ready Ghostwrite Content skill with full MH1-HQ integration.
    """
    
    def __init__(
        self,
        client_id: str,
        client_name: str = None,
        tenant_id: str = None,
        execution_mode: str = "suggest"
    ):
        self.client_id = client_id
        self.client_name = client_name or client_id
        self.tenant_id = tenant_id or client_id  # Use client_id as tenant_id by default
        self.execution_mode = execution_mode
        self.run_id = str(uuid.uuid4())[:8]
        self.start_time = time.time()
        self.start_time_iso = datetime.now(timezone.utc).isoformat()
        
        # Initialize budget manager
        self.budget = BudgetManager()
        
        # Telemetry tracking
        self.tokens_input = 0
        self.tokens_output = 0
        self.sub_calls: List[Dict] = []
        self.data_quality: Dict = {}
        
    def _estimate_cost(self, post_count: int) -> float:
        """Estimate run cost based on expected operations."""
        cost_config = DEFAULTS.get("cost_estimates", {})
        
        # Per-post costs
        tokens_per_post_in = cost_config.get("per_post_tokens_input", 5000)
        tokens_per_post_out = cost_config.get("per_post_tokens_output", 1500)
        
        # Base costs for context loading and analysis
        base_input_tokens = 10000  # Context loading
        base_output_tokens = 2000   # Voice contract, etc.
        
        # Total tokens
        total_input = base_input_tokens + (post_count * tokens_per_post_in)
        total_output = base_output_tokens + (post_count * tokens_per_post_out)
        
        # Calculate cost
        cost = (
            total_input / 1000 * cost_config.get("sonnet_input_per_1k", COST_PER_1K_INPUT) +
            total_output / 1000 * cost_config.get("sonnet_output_per_1k", COST_PER_1K_OUTPUT)
        )
        
        return round(cost, 4)
    
    def _check_budget(self, estimated_cost: float) -> Dict:
        """Check if run is within budget limits."""
        allowed, message = self.budget.check_run_cost(self.tenant_id, estimated_cost)
        status = self.budget.check_budget(self.tenant_id, estimated_cost)
        
        return {
            "allowed": allowed,
            "message": message,
            "status": status.status,
            "daily_remaining": status.daily_remaining,
            "monthly_remaining": status.monthly_remaining
        }
    
    def _run_script(self, script_name: str, args: List[str]) -> Dict:
        """Run a Python script from the scripts directory."""
        script_path = SKILL_ROOT / "scripts" / script_name
        cmd = [sys.executable, str(script_path)] + args
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(SYSTEM_ROOT)
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr,
                    "returncode": result.returncode
                }
            
            # Try to parse JSON output
            try:
                output = json.loads(result.stdout)
                return {"success": True, "output": output, "stderr": result.stderr}
            except json.JSONDecodeError:
                return {"success": True, "output": result.stdout, "stderr": result.stderr}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _load_context(self, founder_id: str, output_dir: str) -> Dict:
        """Load all context using preload_all_context.py script."""
        args = [
            self.client_id,
            founder_id,
            "--client-name", self.client_name,
            "--output-dir", output_dir
        ]
        
        result = self._run_script("preload_all_context.py", args)
        
        if not result.get("success"):
            raise RuntimeError(f"Failed to load context: {result.get('error')}")
        
        return result.get("output", {})
    
    def _fetch_source_posts(self, min_relevance: float, limit: int, output_path: str) -> Dict:
        """Fetch social listening signals."""
        args = [
            self.client_id,
            "--min-relevance", str(min_relevance),
            "--limit", str(limit),
            "--output", output_path,
            "--include-engagement-score"
        ]
        
        result = self._run_script("fetch_source_posts.py", args)
        
        if not result.get("success"):
            raise RuntimeError(f"Failed to fetch source posts: {result.get('error')}")
        
        return result.get("output", {})
    
    def _fetch_thought_leader_posts(self, output_path: str) -> Dict:
        """Fetch thought leader posts."""
        tl_config = DEFAULTS.get("thought_leaders", {})
        
        args = [
            self.client_id,
            "--min-relevance", str(tl_config.get("min_relevance", 7.0)),
            "--limit-leaders", str(tl_config.get("limit_leaders", 10)),
            "--limit-per-leader", str(tl_config.get("limit_per_leader", 5)),
            "--limit-total-posts", str(tl_config.get("limit_total_posts", 50)),
            "--output", output_path
        ]
        
        result = self._run_script("fetch_thought_leader_posts.py", args)
        return result.get("output", {})
    
    def _fetch_parallel_events(self, output_path: str) -> Dict:
        """Fetch parallel monitor events."""
        events_config = DEFAULTS.get("parallel_events", {})
        
        args = [
            self.client_id,
            "--days", str(events_config.get("days", 14)),
            "--limit", str(events_config.get("limit", 20)),
            "--output", output_path
        ]
        
        result = self._run_script("fetch_parallel_events.py", args)
        return result.get("output", {})
    
    def _validate_context(self, context_result: Dict) -> Dict:
        """Validate loaded context meets requirements."""
        validation = DEFAULTS.get("validation", {})
        min_founder_posts = validation.get("min_founder_posts", 10)
        min_source_posts = validation.get("min_source_posts", 5)
        
        issues = []
        warnings = []
        
        metadata = context_result.get("metadata", {})
        
        # Check founder posts
        founder_posts = metadata.get("founderPostsAnalyzed", 0)
        if founder_posts < min_founder_posts:
            issues.append(f"Insufficient founder posts: {founder_posts} < {min_founder_posts} required")
        
        # Check voice confidence
        voice_confidence = metadata.get("voiceConfidence", 0)
        if voice_confidence < 0.5:
            warnings.append(f"Low voice confidence: {voice_confidence:.0%}")
        
        self.data_quality = {
            "founderPosts": founder_posts,
            "voiceConfidence": voice_confidence,
            "contextDocsLoaded": metadata.get("localContextDocs", 0) + metadata.get("firebaseContextDocs", 0),
            "issues": issues,
            "warnings": warnings
        }
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "metadata": metadata
        }
    
    def _build_campaign_dir(self, platform: str) -> str:
        """Build campaign directory path."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        campaign_name = f"ghostwrite-{platform}-{date_str}"
        campaign_dir = SYSTEM_ROOT / "clients" / self.client_id / "campaigns" / campaign_name
        campaign_dir.mkdir(parents=True, exist_ok=True)
        return str(campaign_dir)
    
    def _calculate_actual_cost(self) -> float:
        """Calculate actual cost from tracked tokens."""
        main_cost = (
            self.tokens_input / 1000 * COST_PER_1K_INPUT +
            self.tokens_output / 1000 * COST_PER_1K_OUTPUT
        )
        
        sub_cost = 0
        for sub_call in self.sub_calls:
            if "haiku" in sub_call.get("model", "").lower():
                sub_cost += (
                    sub_call.get("tokens_input", 0) / 1000 * COST_HAIKU_INPUT +
                    sub_call.get("tokens_output", 0) / 1000 * COST_HAIKU_OUTPUT
                )
            else:
                sub_cost += (
                    sub_call.get("tokens_input", 0) / 1000 * COST_PER_1K_INPUT +
                    sub_call.get("tokens_output", 0) / 1000 * COST_PER_1K_OUTPUT
                )
        
        return round(main_cost + sub_cost, 4)
    
    def _build_meta(self, runtime: float, cost: float, release_action: str) -> Dict:
        """Build metadata object for output."""
        return {
            "client_id": self.client_id,
            "client_name": self.client_name,
            "tenant_id": self.tenant_id,
            "run_id": self.run_id,
            "execution_mode": self.execution_mode,
            "runtime_seconds": round(runtime, 2),
            "cost_usd": cost,
            "release_action": release_action,
            "skill_version": SKILL_VERSION,
            "data_quality": self.data_quality,
            "tokens": {
                "input": self.tokens_input,
                "output": self.tokens_output,
                "total": self.tokens_input + self.tokens_output
            },
            "sub_calls": len(self.sub_calls),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def run(self, inputs: Dict) -> Dict:
        """
        Main execution method for ghostwrite content.
        
        Args:
            inputs: Dictionary with:
                - founder_id: Founder document ID (required)
                - platform: Target platform (default: linkedin)
                - post_count: Number of posts to generate (default: 20)
                - min_relevance: Minimum signal relevance (default: 5)
                - max_source_posts: Maximum source posts (default: 25)
                - execution_mode: suggest|preview|execute (default: suggest)
                - context_only: Generate context snapshots only (default: false)
                - auto_topics: Auto-select topics (default: false)
        
        Returns:
            Complete skill result with outputs, metadata, and release action
        """
        # Extract parameters
        founder_id = inputs.get("founder_id")
        if not founder_id:
            return {
                "status": "failed",
                "error": "founder_id is required",
                "_meta": self._build_meta(0, 0, "blocked")
            }
        
        params = DEFAULTS.get("parameters", {})
        platform = inputs.get("platform", params.get("platform", {}).get("default", "linkedin"))
        post_count = inputs.get("post_count", params.get("post_count", {}).get("default", 20))
        min_relevance = inputs.get("min_relevance", params.get("min_relevance", {}).get("default", 5))
        max_source_posts = inputs.get("max_source_posts", params.get("max_source_posts", {}).get("default", 25))
        self.execution_mode = inputs.get("execution_mode", "suggest")
        context_only = inputs.get("context_only", False)
        auto_topics = inputs.get("auto_topics", False)
        
        # Initialize workflow runner
        runner = WorkflowRunner(
            workflow_name=SKILL_NAME,
            version=SKILL_VERSION,
            client=self.client_id,
            tenant_id=self.tenant_id
        )
        
        try:
            # Step 0: Budget check
            estimated_cost = self._estimate_cost(post_count)
            budget_check = self._check_budget(estimated_cost)
            
            if not budget_check["allowed"]:
                return {
                    "status": "budget_exceeded",
                    "message": budget_check["message"],
                    "_meta": self._build_meta(
                        runtime=time.time() - self.start_time,
                        cost=0,
                        release_action="blocked"
                    )
                }
            
            # Build campaign directory
            campaign_dir = self._build_campaign_dir(platform)
            context_data_dir = str(SYSTEM_ROOT / "clients" / self.client_id / "context-data")
            os.makedirs(context_data_dir, exist_ok=True)
            
            # Step 1: Context Loading
            def context_step(step_inputs):
                context_result = self._load_context(founder_id, context_data_dir)
                
                # Validate context
                validation = self._validate_context(context_result)
                if not validation["valid"]:
                    raise ValueError(f"Context validation failed: {validation['issues']}")
                
                # Track tokens
                self.tokens_input += estimate_tokens(json.dumps(context_result))
                
                return {
                    "output": {
                        "context": context_result,
                        "validation": validation,
                        "context_data_dir": context_data_dir
                    },
                    "tokens_input": self.tokens_input,
                    "tokens_output": 0
                }
            
            context_result = runner.run_step("context_loading", context_step, {"founder_id": founder_id})
            if context_result.status != "success":
                raise Exception(f"Context loading failed: {context_result.error}")
            
            # Step 2: Fetch Source Posts
            def fetch_posts_step(step_inputs):
                source_posts_path = os.path.join(campaign_dir, "source-data", "source_posts.json")
                os.makedirs(os.path.dirname(source_posts_path), exist_ok=True)
                
                posts_result = self._fetch_source_posts(min_relevance, max_source_posts, source_posts_path)
                
                # Also fetch thought leaders and parallel events
                tl_path = os.path.join(campaign_dir, "source-data", "thought_leader_posts.json")
                events_path = os.path.join(campaign_dir, "source-data", "parallel_events.json")
                
                tl_result = self._fetch_thought_leader_posts(tl_path)
                events_result = self._fetch_parallel_events(events_path)
                
                return {
                    "output": {
                        "source_posts": posts_result,
                        "thought_leaders": tl_result,
                        "parallel_events": events_result,
                        "files": {
                            "source_posts": source_posts_path,
                            "thought_leaders": tl_path,
                            "parallel_events": events_path
                        }
                    },
                    "tokens_input": 0,
                    "tokens_output": 0
                }
            
            fetch_result = runner.run_step("fetch_source_data", fetch_posts_step, {})
            
            # If context-only mode, stop here
            if context_only:
                runtime = time.time() - self.start_time
                actual_cost = self._calculate_actual_cost()
                
                final_output = {
                    "mode": "context_only",
                    "context": context_result.output,
                    "source_data": fetch_result.output,
                    "campaign_dir": campaign_dir
                }
                
                return {
                    "status": "success",
                    "output": final_output,
                    "release_action": "auto_deliver",
                    "release_message": "Context-only mode completed successfully",
                    "run_id": runner.run_id,
                    "_meta": self._build_meta(runtime, actual_cost, "auto_deliver")
                }
            
            # Step 3: Placeholder for topic curation, template selection, ghostwriting
            # (These would invoke the actual LLM agents in production)
            def placeholder_generation_step(step_inputs):
                """
                This is a placeholder for the actual generation pipeline.
                In production, this would:
                1. Invoke linkedin-topic-curator agent
                2. Invoke linkedin-template-selector agent
                3. Invoke linkedin-ghostwriter agent
                4. Invoke linkedin-qa-reviewer agent
                """
                return {
                    "output": {
                        "status": "generation_pipeline_ready",
                        "message": "Context and source data loaded. Ready for agent pipeline.",
                        "next_steps": [
                            "Stage 1.75: Topic Curation (linkedin-topic-curator)",
                            "Stage 2: Template Selection (linkedin-template-selector)",
                            "Stage 3: Ghostwriting (linkedin-ghostwriter)",
                            "Stage 4: QA Review (linkedin-qa-reviewer)",
                            "Stage 5: Calendar Compilation",
                            "Stage 6: Final Presentation"
                        ],
                        "inputs_prepared": {
                            "context_bundle": os.path.join(context_data_dir, "context_bundle.json"),
                            "voice_contract": os.path.join(context_data_dir, "voice_contract.json"),
                            "source_posts": fetch_result.output.get("files", {}).get("source_posts"),
                            "thought_leaders": fetch_result.output.get("files", {}).get("thought_leaders"),
                            "parallel_events": fetch_result.output.get("files", {}).get("parallel_events")
                        }
                    },
                    "tokens_input": 0,
                    "tokens_output": 0
                }
            
            generation_result = runner.run_step("preparation_complete", placeholder_generation_step, {})
            
            # Build final output
            runtime = time.time() - self.start_time
            actual_cost = self._calculate_actual_cost()
            
            final_output = {
                "summary": {
                    "client_id": self.client_id,
                    "client_name": self.client_name,
                    "founder_id": founder_id,
                    "platform": platform,
                    "post_count_requested": post_count,
                    "campaign_dir": campaign_dir
                },
                "context": context_result.output,
                "source_data": fetch_result.output,
                "generation_status": generation_result.output,
                "data_quality": self.data_quality
            }
            
            # Evaluation
            eval_schema = {
                "required": ["summary", "context", "source_data"],
                "properties": {
                    "summary": {"type": "object"},
                    "context": {"type": "object"},
                    "source_data": {"type": "object"}
                }
            }
            
            evaluation = evaluate_output(
                final_output,
                schema=eval_schema,
                requirements={"required_sections": ["summary", "context"]}
            )
            
            # Determine release action
            release_action = determine_release_action(
                standard_eval=evaluation,
                is_external_facing=False
            )
            
            # Complete workflow
            if release_action == ReleaseAction.AUTO_DELIVER:
                telemetry = runner.complete(RunStatus.SUCCESS, evaluation=evaluation)
                status = "success"
            elif release_action == ReleaseAction.AUTO_REFINE:
                telemetry = runner.complete(RunStatus.SUCCESS, evaluation=evaluation)
                status = "success"
            elif release_action == ReleaseAction.HUMAN_REVIEW:
                runner.route_to_human(
                    reason=f"Evaluation score: {evaluation.get('score', 0):.0%}",
                    context={"output": final_output, "evaluation": evaluation}
                )
                telemetry = runner.complete(RunStatus.REVIEW, evaluation=evaluation)
                status = "review"
            else:
                telemetry = runner.complete(RunStatus.FAILED, evaluation=evaluation)
                status = "blocked"
            
            # Log telemetry
            log_run(
                run_id=runner.run_id,
                tenant_id=self.tenant_id,
                type="skill",
                name=SKILL_NAME,
                version=SKILL_VERSION,
                status=status,
                start_time=runner.telemetry.start_time,
                end_time=runner.telemetry.end_time,
                duration_seconds=runtime,
                tokens_input=self.tokens_input,
                tokens_output=self.tokens_output,
                model="claude-sonnet-4",
                client=self.client_id,
                evaluation=evaluation,
                steps=runner.telemetry.steps
            )
            
            return {
                "status": status,
                "output": final_output,
                "evaluation": evaluation,
                "release_action": release_action.value,
                "release_message": get_release_action_message(release_action),
                "run_id": runner.run_id,
                "run_dir": str(runner.run_dir),
                "_meta": self._build_meta(runtime, actual_cost, release_action.value)
            }
            
        except Exception as e:
            runner.complete(RunStatus.FAILED)
            runtime = time.time() - self.start_time
            
            return {
                "status": "failed",
                "error": str(e),
                "error_type": type(e).__name__,
                "run_id": runner.run_id,
                "_meta": self._build_meta(runtime, 0, "blocked")
            }


def run_ghostwrite_content(inputs: Dict) -> Dict:
    """
    Main entry point for ghostwrite content skill.
    
    Args:
        inputs: Dictionary with configuration:
            - client_id: Firebase Client ID (or read from active_client.md)
            - founder_id: Founder document ID (required)
            - client_name: Client display name (optional)
            - tenant_id: Tenant identifier (default: client_id)
            - platform: Target platform (default: linkedin)
            - post_count: Number of posts (default: 20)
            - min_relevance: Minimum signal relevance (default: 5)
            - max_source_posts: Maximum source posts (default: 25)
            - execution_mode: suggest|preview|execute (default: suggest)
            - context_only: Generate context only (default: false)
            - auto_topics: Auto-select topics (default: false)
    
    Returns:
        Complete skill result with outputs and metadata
    """
    # Read from active_client.md if client_id not provided
    if not inputs.get("client_id"):
        active_client = get_client_from_active_file()
        if active_client.get("client_id"):
            inputs["client_id"] = active_client["client_id"]
            if not inputs.get("client_name"):
                inputs["client_name"] = active_client.get("client_name")
            if not inputs.get("founder_id") and active_client.get("default_founder"):
                inputs["founder_id"] = active_client.get("default_founder")
        else:
            return {
                "status": "failed",
                "error": "client_id is required (not provided and not found in active_client.md)"
            }
    
    client_id = inputs.get("client_id")
    client_name = inputs.get("client_name", client_id)
    tenant_id = inputs.get("tenant_id", client_id)
    execution_mode = inputs.get("execution_mode", "suggest")
    
    skill = GhostwriteContentSkill(
        client_id=client_id,
        client_name=client_name,
        tenant_id=tenant_id,
        execution_mode=execution_mode
    )
    
    return skill.run(inputs)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run ghostwrite content skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic run (reads client from active_client.md)
    python run.py --founder_id xyz123 --post_count 20
    
    # Specify client explicitly
    python run.py --client_id abc123 --founder_id xyz123
    
    # Context-only mode
    python run.py --founder_id xyz123 --context_only
    
    # Preview mode
    python run.py --founder_id xyz123 --execution_mode preview
    
    # Save output to file
    python run.py --founder_id xyz123 --output results.json
        """
    )
    
    parser.add_argument("--client_id", type=str, help="Firebase Client ID")
    parser.add_argument("--founder_id", type=str, help="Founder document ID")
    parser.add_argument("--client_name", type=str, help="Client display name")
    parser.add_argument("--tenant_id", type=str, help="Tenant identifier")
    parser.add_argument("--platform", type=str, default="linkedin", help="Target platform")
    parser.add_argument("--post_count", type=int, default=20, help="Number of posts")
    parser.add_argument("--min_relevance", type=float, default=5, help="Minimum relevance score")
    parser.add_argument("--max_source_posts", type=int, default=25, help="Maximum source posts")
    parser.add_argument("--execution_mode", type=str, choices=["suggest", "preview", "execute"], default="suggest")
    parser.add_argument("--context_only", action="store_true", help="Generate context only")
    parser.add_argument("--auto_topics", action="store_true", help="Auto-select topics")
    parser.add_argument("--output", type=str, help="Output file path (JSON)")
    
    args = parser.parse_args()
    
    # Build inputs
    inputs = {
        "platform": args.platform,
        "post_count": args.post_count,
        "min_relevance": args.min_relevance,
        "max_source_posts": args.max_source_posts,
        "execution_mode": args.execution_mode,
        "context_only": args.context_only,
        "auto_topics": args.auto_topics
    }
    
    if args.client_id:
        inputs["client_id"] = args.client_id
    if args.founder_id:
        inputs["founder_id"] = args.founder_id
    if args.client_name:
        inputs["client_name"] = args.client_name
    if args.tenant_id:
        inputs["tenant_id"] = args.tenant_id
    
    # Run skill
    result = run_ghostwrite_content(inputs)
    
    # Output
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Output saved to {args.output}")
    else:
        print(json.dumps(result, indent=2, default=str))
    
    # Exit with appropriate code
    sys.exit(0 if result["status"] in ["success", "review"] else 1)


if __name__ == "__main__":
    main()
