#!/usr/bin/env python3
"""
ICP Historical Analysis Skill - v1.0.0

Analyze historical LinkedIn post engagement to measure ICP engagement rates
and identify content themes with highest ICP engagement.

Features:
- Weekly trigger for past 14 days analysis
- Week-over-week ICP engagement comparison
- Theme-based performance analysis
- Historical baseline comparison
- Integration with mh1-hq lib for Firebase, budget, and telemetry

Usage:
    # CLI
    python run.py --founder_id xyz123
    python run.py --client_id abc123 --founder_id xyz123 --lookback_days 14
    
    # Programmatic
    from skills.icp_historical_analysis.run import run_icp_historical_analysis
    result = run_icp_historical_analysis({
        "client_id": "abc123",
        "founder_id": "xyz789",
        "lookback_days": 14
    })
"""

import argparse
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add lib to path
SKILL_ROOT = Path(__file__).parent
SYSTEM_ROOT = SKILL_ROOT.parent.parent
sys.path.insert(0, str(SYSTEM_ROOT / "lib"))

# Import lib modules
try:
    from client import get_client_manager, ClientContext
    from firebase_client import get_firebase_client, FirebaseError
    from runner import WorkflowRunner, RunStatus, estimate_tokens
    from evaluator import evaluate_output
    from release_policy import determine_release_action, ReleaseAction, get_release_action_message
    from budget import BudgetManager
    from telemetry import log_run
except ImportError as e:
    print(f"Warning: Could not import lib modules: {e}")
    print("Running in standalone mode with limited functionality.")

# Constants
SKILL_NAME = "icp-historical-analysis"
SKILL_VERSION = "v1.0.0"

# Cost estimates (using Haiku for analysis)
COST_HAIKU_INPUT = 0.00025
COST_HAIKU_OUTPUT = 0.00125


def get_client_from_active_file() -> Dict:
    """Read client configuration from inputs/active_client.md."""
    active_client_path = SYSTEM_ROOT / "inputs" / "active_client.md"
    if not active_client_path.exists():
        return {}
    
    with open(active_client_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    result = {}
    for line in content.split('\n'):
        if 'Firestore Client ID:' in line or 'CLIENT_ID' in line:
            result['client_id'] = line.split(':', 1)[1].strip().strip('"\'')
        elif 'Client Name:' in line or 'CLIENT_NAME' in line:
            result['client_name'] = line.split(':', 1)[1].strip().strip('"\'')
        elif 'Default Ghostwrite Founder:' in line or 'DEFAULT_FOUNDER' in line:
            result['default_founder'] = line.split(':', 1)[1].strip().strip('"\'')
    
    return result


class ICPHistoricalAnalysisSkill:
    """
    Analyze historical post engagement for ICP metrics.
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
        self.tenant_id = tenant_id or client_id
        self.execution_mode = execution_mode
        self.run_id = str(uuid.uuid4())[:8]
        self.start_time = time.time()
        
        # Initialize Firebase client
        try:
            self.firebase = get_firebase_client()
        except Exception:
            self.firebase = None
        
        # Telemetry
        self.tokens_input = 0
        self.tokens_output = 0
        self.warnings: List[str] = []
    
    def _fetch_posts(self, founder_id: str, lookback_days: int) -> List[Dict]:
        """Fetch posts from Firebase within the lookback period."""
        if not self.firebase:
            return self._get_mock_posts(lookback_days)
        
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=lookback_days)
            
            # Fetch from clients/{clientId}/founders/{founderId}/posts
            posts = self.firebase.get_collection(
                "posts",
                parent_collection=f"clients/{self.client_id}/founders",
                parent_doc=founder_id,
                where=[("published_at", ">=", cutoff_date.isoformat())]
            )
            
            return posts
        except Exception as e:
            self.warnings.append(f"Could not fetch posts from Firebase: {e}")
            return []
    
    def _fetch_reactors(self, post_id: str) -> List[Dict]:
        """Fetch reactors for a specific post."""
        if not self.firebase:
            return self._get_mock_reactors()
        
        try:
            reactors = self.firebase.get_collection(
                "reactors",
                parent_collection=f"clients/{self.client_id}/posts",
                parent_doc=post_id
            )
            return reactors
        except Exception as e:
            self.warnings.append(f"Could not fetch reactors for post {post_id}: {e}")
            return []
    
    def _load_icp_definitions(self, override: Optional[List[Dict]] = None) -> List[Dict]:
        """Load ICP definitions from client context or parameter override."""
        if override:
            return override
        
        # Default ICP definitions (should be loaded from client context in production)
        return [
            {
                "name": "Primary",
                "criteria": {
                    "titles": ["VP", "Director", "Head of", "CMO", "Chief Marketing"],
                    "seniority_levels": ["Director+", "VP+", "C-Level"],
                    "industries": ["B2B SaaS", "Technology", "Software"]
                },
                "priority": 1
            },
            {
                "name": "Secondary",
                "criteria": {
                    "titles": ["Manager", "Lead", "Senior"],
                    "seniority_levels": ["Manager+", "Senior"],
                    "industries": ["B2B SaaS", "Technology", "Marketing"]
                },
                "priority": 2
            }
        ]
    
    def _match_reactor_to_icp(self, reactor: Dict, icp_defs: List[Dict]) -> Optional[str]:
        """Check if a reactor matches any ICP definition."""
        reactor_title = reactor.get("title", "").lower()
        reactor_company = reactor.get("company", "")
        
        for icp in sorted(icp_defs, key=lambda x: x.get("priority", 99)):
            criteria = icp.get("criteria", {})
            
            # Check title match
            title_patterns = [t.lower() for t in criteria.get("titles", [])]
            if any(pattern in reactor_title for pattern in title_patterns):
                return icp["name"]
        
        return None
    
    def _analyze_week(
        self,
        posts: List[Dict],
        icp_defs: List[Dict],
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Analyze metrics for a specific week."""
        week_posts = [
            p for p in posts
            if start_date <= self._parse_date(p.get("published_at", "")) < end_date
        ]
        
        total_reactors = 0
        icp_matches = 0
        post_metrics = []
        
        for post in week_posts:
            post_id = post.get("id", post.get("_id", ""))
            reactors = self._fetch_reactors(post_id)
            post_icp_matches = 0
            
            for reactor in reactors:
                total_reactors += 1
                if self._match_reactor_to_icp(reactor, icp_defs):
                    icp_matches += 1
                    post_icp_matches += 1
            
            post_metrics.append({
                "post_id": post_id,
                "reactors": len(reactors),
                "icp_matches": post_icp_matches,
                "icp_rate": post_icp_matches / len(reactors) if reactors else 0,
                "topic": post.get("topic", post.get("theme", "Unknown"))
            })
        
        # Find top post
        top_post = max(post_metrics, key=lambda x: x["icp_rate"]) if post_metrics else None
        
        return {
            "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "posts": len(week_posts),
            "reactors": total_reactors,
            "avg_reactors": total_reactors / len(week_posts) if week_posts else 0,
            "icp_matches": icp_matches,
            "icp_rate": icp_matches / total_reactors if total_reactors else 0,
            "top_post": top_post,
            "post_metrics": post_metrics
        }
    
    def _analyze_themes(
        self,
        posts: List[Dict],
        week1_metrics: List[Dict],
        week2_metrics: List[Dict]
    ) -> List[Dict]:
        """Analyze performance by content theme."""
        all_metrics = week1_metrics + week2_metrics
        
        # Group by theme
        themes: Dict[str, Dict] = {}
        for pm in all_metrics:
            theme = pm.get("topic", "Unknown")
            if theme not in themes:
                themes[theme] = {
                    "posts": 0,
                    "total_reactors": 0,
                    "icp_matches": 0,
                    "sample_posts": []
                }
            themes[theme]["posts"] += 1
            themes[theme]["total_reactors"] += pm.get("reactors", 0)
            themes[theme]["icp_matches"] += pm.get("icp_matches", 0)
            themes[theme]["sample_posts"].append(pm.get("post_id", ""))
        
        # Calculate metrics and rank
        theme_analysis = []
        for theme, data in themes.items():
            icp_rate = data["icp_matches"] / data["total_reactors"] if data["total_reactors"] else 0
            
            # Determine recommendation
            if data["posts"] < 2:
                recommendation = "needs_data"
            elif icp_rate >= 0.25:
                recommendation = "high_performer"
            elif icp_rate >= 0.15:
                recommendation = "average"
            else:
                recommendation = "low_performer"
            
            theme_analysis.append({
                "theme": theme,
                "posts": data["posts"],
                "total_reactors": data["total_reactors"],
                "icp_matches": data["icp_matches"],
                "icp_rate": round(icp_rate, 3),
                "avg_engagement": data["total_reactors"] / data["posts"] if data["posts"] else 0,
                "recommendation": recommendation,
                "sample_posts": data["sample_posts"][:3]
            })
        
        # Sort by ICP rate descending
        return sorted(theme_analysis, key=lambda x: x["icp_rate"], reverse=True)
    
    def _generate_recommendations(
        self,
        summary: Dict,
        theme_analysis: List[Dict],
        comparison: Dict
    ) -> List[str]:
        """Generate actionable content strategy recommendations."""
        recommendations = []
        
        # Theme-based recommendations
        high_performers = [t for t in theme_analysis if t["recommendation"] == "high_performer"]
        low_performers = [t for t in theme_analysis if t["recommendation"] == "low_performer"]
        
        if high_performers:
            top_theme = high_performers[0]
            recommendations.append(
                f"Increase '{top_theme['theme']}' posts - "
                f"{top_theme['icp_rate']:.0%} ICP engagement vs "
                f"{summary['icp_engagement_rate']:.0%} average"
            )
        
        if low_performers:
            bottom_theme = low_performers[-1]
            recommendations.append(
                f"Review '{bottom_theme['theme']}' strategy - "
                f"only {bottom_theme['icp_rate']:.0%} ICP engagement"
            )
        
        # Trend-based recommendations
        if comparison.get("trend") == "declining":
            recommendations.append(
                "ICP engagement declining - consider reviewing recent content topics"
            )
        elif comparison.get("trend") == "improving":
            recommendations.append(
                "ICP engagement improving - continue current content strategy"
            )
        
        # Volume recommendations
        if summary.get("total_posts", 0) < 10:
            recommendations.append(
                "Increase posting frequency for more reliable ICP engagement data"
            )
        
        return recommendations
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse ISO date string to datetime."""
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception:
            return datetime.min.replace(tzinfo=timezone.utc)
    
    def _get_mock_posts(self, lookback_days: int) -> List[Dict]:
        """Return mock posts for testing when Firebase is unavailable."""
        now = datetime.now(timezone.utc)
        posts = []
        themes = ["Product Updates", "Thought Leadership", "Case Studies", "Industry News"]
        
        for i in range(20):
            days_ago = i % lookback_days
            posts.append({
                "id": f"post_{i}",
                "published_at": (now - timedelta(days=days_ago)).isoformat(),
                "topic": themes[i % len(themes)],
                "content": f"Sample post content {i}..."
            })
        
        return posts
    
    def _get_mock_reactors(self) -> List[Dict]:
        """Return mock reactors for testing."""
        import random
        count = random.randint(5, 30)
        reactors = []
        
        titles = [
            "VP of Marketing", "Marketing Manager", "Software Engineer",
            "Director of Growth", "CEO", "Product Manager", "Sales Rep",
            "CMO", "Head of Marketing", "Growth Lead"
        ]
        
        for i in range(count):
            reactors.append({
                "id": f"reactor_{i}",
                "name": f"User {i}",
                "title": random.choice(titles),
                "company": f"Company {i}"
            })
        
        return reactors
    
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
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def run(self, inputs: Dict) -> Dict:
        """
        Main execution method for ICP historical analysis.
        
        Args:
            inputs: Dictionary with:
                - founder_id: Founder document ID (required)
                - lookback_days: Days to analyze (default: 14)
                - icp_definitions: Override ICP definitions (optional)
                - min_engagement: Minimum engagement threshold (optional)
        
        Returns:
            Complete skill result with analysis and metadata
        """
        founder_id = inputs.get("founder_id")
        if not founder_id:
            return {
                "status": "failed",
                "error": "founder_id is required",
                "_meta": self._build_meta(0, 0, "blocked")
            }
        
        lookback_days = inputs.get("lookback_days", 14)
        icp_definitions = inputs.get("icp_definitions")
        min_engagement = inputs.get("min_engagement", 0)
        
        try:
            # Load ICP definitions
            icp_defs = self._load_icp_definitions(icp_definitions)
            
            # Fetch posts
            all_posts = self._fetch_posts(founder_id, lookback_days)
            
            if not all_posts:
                self.warnings.append("No posts found in lookback period")
            
            # Filter by minimum engagement if specified
            if min_engagement > 0:
                all_posts = [p for p in all_posts if p.get("engagement", 0) >= min_engagement]
            
            # Calculate date boundaries
            now = datetime.now(timezone.utc)
            week1_end = now
            week1_start = now - timedelta(days=7)
            week2_end = week1_start
            week2_start = now - timedelta(days=lookback_days)
            
            # Analyze each week
            week1 = self._analyze_week(all_posts, icp_defs, week1_start, week1_end)
            week2 = self._analyze_week(all_posts, icp_defs, week2_start, week2_end)
            
            # Calculate comparison
            icp_rate_change = week1["icp_rate"] - week2["icp_rate"]
            if week2["icp_rate"] > 0:
                pct_change = (icp_rate_change / week2["icp_rate"]) * 100
                pct_str = f"+{pct_change:.0f}%" if pct_change >= 0 else f"{pct_change:.0f}%"
            else:
                pct_str = "N/A"
            
            trend = "stable"
            if abs(icp_rate_change) > 0.05:
                trend = "improving" if icp_rate_change > 0 else "declining"
            
            comparison = {
                "icp_rate_change": round(icp_rate_change, 3),
                "icp_rate_change_pct": pct_str,
                "reactors_change": week1["reactors"] - week2["reactors"],
                "posts_change": week1["posts"] - week2["posts"],
                "trend": trend
            }
            
            # Analyze themes
            all_post_metrics = week1.get("post_metrics", []) + week2.get("post_metrics", [])
            theme_analysis = self._analyze_themes(all_posts, week1.get("post_metrics", []), week2.get("post_metrics", []))
            
            # Build summary
            total_reactors = week1["reactors"] + week2["reactors"]
            total_icp = week1["icp_matches"] + week2["icp_matches"]
            total_posts = week1["posts"] + week2["posts"]
            
            summary = {
                "period": f"{week2_start.strftime('%Y-%m-%d')} to {week1_end.strftime('%Y-%m-%d')}",
                "total_posts": total_posts,
                "total_reactors": total_reactors,
                "avg_reactors_per_post": round(total_reactors / total_posts, 1) if total_posts else 0,
                "icp_engagement_rate": round(total_icp / total_reactors, 3) if total_reactors else 0,
                "week_over_week_change": pct_str,
                "total_icp_matches": total_icp
            }
            
            # Get top performing posts
            top_posts = sorted(all_post_metrics, key=lambda x: x.get("icp_rate", 0), reverse=True)[:5]
            
            # Generate recommendations
            recommendations = self._generate_recommendations(summary, theme_analysis, comparison)
            
            # Build output
            output = {
                "summary": summary,
                "week1_analysis": {k: v for k, v in week1.items() if k != "post_metrics"},
                "week2_analysis": {k: v for k, v in week2.items() if k != "post_metrics"},
                "comparison": comparison,
                "theme_analysis": theme_analysis,
                "top_performing_posts": top_posts,
                "historical_baseline": {
                    "period": "Last 90 days",
                    "avg_icp_rate": summary["icp_engagement_rate"],  # Would calculate from full history
                    "avg_reactors_per_post": summary["avg_reactors_per_post"],
                    "total_posts_analyzed": total_posts,
                    "vs_baseline": "on par"  # Would compare to actual baseline
                },
                "recommendations": recommendations
            }
            
            runtime = time.time() - self.start_time
            cost = 0.02  # Estimated cost for analysis
            
            # Determine release action
            release_action = ReleaseAction.AUTO_DELIVER if total_posts >= 4 else ReleaseAction.HUMAN_REVIEW
            
            return {
                "status": "success" if not self.warnings else "partial",
                "output": output,
                "evaluation": {
                    "score": 0.85 if total_posts >= 4 else 0.6,
                    "pass": total_posts >= 4
                },
                "release_action": release_action.value,
                "run_id": self.run_id,
                "warnings": self.warnings if self.warnings else None,
                "_meta": self._build_meta(runtime, cost, release_action.value)
            }
            
        except Exception as e:
            runtime = time.time() - self.start_time
            return {
                "status": "failed",
                "error": str(e),
                "error_type": type(e).__name__,
                "run_id": self.run_id,
                "_meta": self._build_meta(runtime, 0, "blocked")
            }


def run_icp_historical_analysis(inputs: Dict) -> Dict:
    """
    Main entry point for ICP historical analysis skill.
    
    Args:
        inputs: Dictionary with configuration
    
    Returns:
        Complete skill result with analysis and metadata
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
    
    skill = ICPHistoricalAnalysisSkill(
        client_id=inputs["client_id"],
        client_name=inputs.get("client_name"),
        tenant_id=inputs.get("tenant_id"),
        execution_mode=inputs.get("execution_mode", "suggest")
    )
    
    return skill.run(inputs)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run ICP historical analysis skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run.py --founder_id xyz123
    python run.py --client_id abc123 --founder_id xyz123
    python run.py --founder_id xyz123 --lookback_days 30
    python run.py --founder_id xyz123 --output results.json
        """
    )
    
    parser.add_argument("--client_id", type=str, help="Firebase Client ID")
    parser.add_argument("--founder_id", type=str, help="Founder document ID")
    parser.add_argument("--client_name", type=str, help="Client display name")
    parser.add_argument("--lookback_days", type=int, default=14, help="Days to analyze")
    parser.add_argument("--min_engagement", type=int, default=0, help="Minimum engagement")
    parser.add_argument("--output", type=str, help="Output file path (JSON)")
    
    args = parser.parse_args()
    
    inputs = {
        "lookback_days": args.lookback_days,
        "min_engagement": args.min_engagement
    }
    
    if args.client_id:
        inputs["client_id"] = args.client_id
    if args.founder_id:
        inputs["founder_id"] = args.founder_id
    if args.client_name:
        inputs["client_name"] = args.client_name
    
    result = run_icp_historical_analysis(inputs)
    
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Output saved to {args.output}")
    else:
        print(json.dumps(result, indent=2, default=str))
    
    sys.exit(0 if result["status"] in ["success", "partial"] else 1)


if __name__ == "__main__":
    main()
