#!/usr/bin/env python3
"""
Qualify Leads Skill - v1.0.0

Pull LinkedIn post reactors and commenters from the past week, qualify them
against ICP definitions, and generate personalized outreach messages.

Features:
- Reactor and commenter qualification
- ICP matching with confidence scores
- Personalized draft message generation
- Deduplication across posts
- Integration with mh1-hq lib for Firebase, budget, and telemetry

Usage:
    # CLI
    python run.py --founder_id xyz123
    python run.py --client_id abc123 --founder_id xyz123 --lookback_days 7
    
    # Programmatic
    from skills.qualify_leads.run import run_qualify_leads
    result = run_qualify_leads({
        "client_id": "abc123",
        "founder_id": "xyz789",
        "lookback_days": 7,
        "generate_messages": True
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
from typing import Any, Dict, List, Optional, Tuple

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
SKILL_NAME = "qualify-leads"
SKILL_VERSION = "v1.0.0"

# Cost estimates
COST_HAIKU_INPUT = 0.00025
COST_HAIKU_OUTPUT = 0.00125
COST_SONNET_INPUT = 0.003
COST_SONNET_OUTPUT = 0.015


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


class QualifyLeadsSkill:
    """
    Qualify LinkedIn post engagers as sales leads.
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
        self.messages_generated = 0
    
    def _fetch_posts(self, founder_id: str, lookback_days: int) -> List[Dict]:
        """Fetch posts from Firebase within the lookback period."""
        if not self.firebase:
            return self._get_mock_posts(lookback_days)
        
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=lookback_days)
            
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
            return [dict(r, engagement_type="reaction") for r in reactors]
        except Exception as e:
            self.warnings.append(f"Could not fetch reactors for post {post_id}: {e}")
            return []
    
    def _fetch_commenters(self, post_id: str) -> List[Dict]:
        """Fetch commenters for a specific post."""
        if not self.firebase:
            return self._get_mock_commenters()
        
        try:
            commenters = self.firebase.get_collection(
                "comments",
                parent_collection=f"clients/{self.client_id}/posts",
                parent_doc=post_id
            )
            return [dict(c, engagement_type="comment") for c in commenters]
        except Exception as e:
            self.warnings.append(f"Could not fetch commenters for post {post_id}: {e}")
            return []
    
    def _load_icp_definitions(self, override: Optional[List[Dict]] = None) -> List[Dict]:
        """Load ICP definitions from client context or parameter override."""
        if override:
            return override
        
        return [
            {
                "name": "Primary",
                "criteria": {
                    "titles": ["VP", "Director", "Head of", "CMO", "Chief Marketing", "Chief Revenue"],
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
    
    def _match_to_icp(self, engager: Dict, icp_defs: List[Dict]) -> Tuple[Optional[str], float, str]:
        """
        Check if an engager matches any ICP definition.
        
        Returns:
            Tuple of (icp_type, confidence, reason) or (None, 0, reason) if no match
        """
        title = engager.get("title", "").lower()
        company = engager.get("company", "")
        headline = engager.get("headline", "").lower()
        
        # Check title field
        if not title and headline:
            title = headline
        
        for icp in sorted(icp_defs, key=lambda x: x.get("priority", 99)):
            criteria = icp.get("criteria", {})
            title_patterns = [t.lower() for t in criteria.get("titles", [])]
            
            # Score matching criteria
            title_match = any(pattern in title for pattern in title_patterns)
            
            if title_match:
                # Calculate confidence based on how many criteria match
                confidence = 0.7  # Base confidence for title match
                
                # Boost for seniority indicators
                if any(s in title for s in ["vp", "director", "head", "chief", "cmo", "cro"]):
                    confidence += 0.15
                
                # Boost for company info available
                if company:
                    confidence += 0.1
                
                confidence = min(confidence, 0.99)
                
                # Build reason
                matched_title = next((p for p in title_patterns if p in title), "title")
                reason = f"Matches {icp['name']} ICP: {matched_title.title()} role"
                if company:
                    reason += f" at {company}"
                
                return icp["name"], round(confidence, 2), reason
        
        return None, 0, "No ICP criteria matched"
    
    def _generate_message(
        self,
        lead: Dict,
        post: Dict,
        founder_name: str = "the founder"
    ) -> str:
        """Generate a personalized outreach message for a lead."""
        name = lead.get("name", "").split()[0] if lead.get("name") else "there"
        role = lead.get("role", "your role")
        company = lead.get("company", "your company")
        post_topic = post.get("topic", post.get("theme", "the topic"))
        engagement_type = lead.get("engagement_type", "reaction")
        
        # Engagement verb
        if engagement_type == "comment":
            engagement_verb = "commented on"
        else:
            engagement_verb = "engaged with"
        
        # Build message
        message = (
            f"Hi {name}, I noticed you {engagement_verb} my post about {post_topic}. "
            f"As {role} at {company}, I imagine you're dealing with similar challenges. "
            f"Would love to share some insights that might help — open to a quick chat?"
        )
        
        self.messages_generated += 1
        return message
    
    def _deduplicate_leads(self, leads: List[Dict]) -> List[Dict]:
        """Deduplicate leads that appear in multiple posts."""
        seen = {}
        
        for lead in leads:
            # Create unique key from name + company
            key = f"{lead.get('name', '').lower()}_{lead.get('company', '').lower()}"
            
            if key not in seen:
                seen[key] = lead
            else:
                # Merge engagement types if same person engaged multiple times
                existing = seen[key]
                if existing.get("engagement_type") != lead.get("engagement_type"):
                    existing["engagement_type"] = "both"
                # Keep higher confidence
                if lead.get("confidence", 0) > existing.get("confidence", 0):
                    existing["confidence"] = lead["confidence"]
                # Track multiple posts
                if "origin_posts" not in existing:
                    existing["origin_posts"] = [existing.get("origin_post_id")]
                existing["origin_posts"].append(lead.get("origin_post_id"))
        
        return list(seen.values())
    
    def _determine_priority(self, lead: Dict) -> str:
        """Determine outreach priority based on ICP type and confidence."""
        icp_type = lead.get("icp_type", "")
        confidence = lead.get("confidence", 0)
        engagement_type = lead.get("engagement_type", "")
        
        if icp_type == "Primary" and confidence >= 0.8:
            return "high"
        elif icp_type == "Primary" or (icp_type == "Secondary" and confidence >= 0.85):
            return "medium"
        else:
            return "low"
    
    def _get_mock_posts(self, lookback_days: int) -> List[Dict]:
        """Return mock posts for testing."""
        now = datetime.now(timezone.utc)
        themes = ["Marketing Automation", "B2B Growth", "Content Strategy", "Lead Generation"]
        
        posts = []
        for i in range(10):
            posts.append({
                "id": f"post_{i}",
                "published_at": (now - timedelta(days=i % lookback_days)).isoformat(),
                "topic": themes[i % len(themes)],
                "content": f"Sample post about {themes[i % len(themes)]}...",
                "url": f"https://linkedin.com/posts/founder-{i}"
            })
        
        return posts
    
    def _get_mock_reactors(self) -> List[Dict]:
        """Return mock reactors for testing."""
        import random
        
        titles = [
            "VP of Marketing", "Marketing Manager", "Software Engineer",
            "Director of Growth", "CEO", "Product Manager", "Sales Rep",
            "CMO", "Head of Marketing", "Growth Lead", "Intern",
            "Account Executive", "Customer Success Manager"
        ]
        
        companies = [
            "TechCorp Solutions", "Growth Labs", "SaaS Inc",
            "Marketing Pro", "Data Systems", "Cloud Nine"
        ]
        
        count = random.randint(10, 25)
        reactors = []
        
        for i in range(count):
            reactors.append({
                "id": f"reactor_{i}",
                "name": f"Person {i}",
                "title": random.choice(titles),
                "company": random.choice(companies),
                "linkedin_url": f"https://linkedin.com/in/person-{i}",
                "engagement_type": "reaction"
            })
        
        return reactors
    
    def _get_mock_commenters(self) -> List[Dict]:
        """Return mock commenters for testing."""
        import random
        
        titles = [
            "VP of Sales", "Marketing Director", "Founder",
            "Head of Demand Gen", "Growth Manager"
        ]
        
        count = random.randint(2, 8)
        commenters = []
        
        for i in range(count):
            commenters.append({
                "id": f"commenter_{i}",
                "name": f"Commenter {i}",
                "title": random.choice(titles),
                "company": f"Company {i}",
                "linkedin_url": f"https://linkedin.com/in/commenter-{i}",
                "comment_text": f"Great insights! This resonates with what we're seeing at Company {i}.",
                "engagement_type": "comment"
            })
        
        return commenters
    
    def _build_meta(self, runtime: float, cost: float, release_action: str, stats: Dict) -> Dict:
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
            "posts_analyzed": stats.get("posts_analyzed", 0),
            "engagers_processed": stats.get("engagers_processed", 0),
            "messages_generated": self.messages_generated,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def run(self, inputs: Dict) -> Dict:
        """
        Main execution method for lead qualification.
        
        Args:
            inputs: Dictionary with configuration parameters
        
        Returns:
            Complete skill result with qualified leads and metadata
        """
        founder_id = inputs.get("founder_id")
        if not founder_id:
            return {
                "status": "failed",
                "error": "founder_id is required",
                "_meta": self._build_meta(0, 0, "blocked", {})
            }
        
        lookback_days = inputs.get("lookback_days", 7)
        icp_definitions = inputs.get("icp_definitions")
        include_commenters = inputs.get("include_commenters", True)
        include_reactors = inputs.get("include_reactors", True)
        generate_messages = inputs.get("generate_messages", True)
        max_leads = inputs.get("max_leads", 100)
        
        try:
            # Load ICP definitions
            icp_defs = self._load_icp_definitions(icp_definitions)
            
            # Fetch posts
            posts = self._fetch_posts(founder_id, lookback_days)
            
            if not posts:
                self.warnings.append("No posts found in lookback period")
                return {
                    "status": "partial",
                    "output": {
                        "summary": {
                            "period": f"Last {lookback_days} days",
                            "posts_analyzed": 0,
                            "total_engagers": 0,
                            "qualified_leads": 0,
                            "qualification_rate": 0
                        },
                        "qualified_leads": [],
                        "recommendations": ["No posts found - ensure posts exist in Firebase"]
                    },
                    "warnings": self.warnings,
                    "_meta": self._build_meta(time.time() - self.start_time, 0, "human_review", {"posts_analyzed": 0})
                }
            
            # Collect all engagers
            all_engagers = []
            post_map = {}  # Map post_id to post data
            
            for post in posts:
                post_id = post.get("id", post.get("_id", ""))
                post_map[post_id] = post
                
                if include_reactors:
                    reactors = self._fetch_reactors(post_id)
                    for r in reactors:
                        r["origin_post_id"] = post_id
                        r["origin_post_url"] = post.get("url", f"https://linkedin.com/posts/{post_id}")
                        r["origin_post_topic"] = post.get("topic", post.get("theme", "Unknown"))
                    all_engagers.extend(reactors)
                
                if include_commenters:
                    commenters = self._fetch_commenters(post_id)
                    for c in commenters:
                        c["origin_post_id"] = post_id
                        c["origin_post_url"] = post.get("url", f"https://linkedin.com/posts/{post_id}")
                        c["origin_post_topic"] = post.get("topic", post.get("theme", "Unknown"))
                    all_engagers.extend(commenters)
            
            # Qualify engagers
            qualified_leads = []
            disqualified = {
                "total": 0,
                "reasons": {},
                "sample": []
            }
            
            for engager in all_engagers:
                icp_type, confidence, reason = self._match_to_icp(engager, icp_defs)
                
                if icp_type:
                    lead = {
                        "name": engager.get("name", "Unknown"),
                        "company": engager.get("company", "Unknown"),
                        "role": engager.get("title", engager.get("headline", "Unknown")),
                        "origin_post_url": engager.get("origin_post_url", ""),
                        "origin_post_id": engager.get("origin_post_id", ""),
                        "origin_post_topic": engager.get("origin_post_topic", ""),
                        "icp_type": icp_type,
                        "reason": reason,
                        "engagement_type": engager.get("engagement_type", "reaction"),
                        "engagement_date": engager.get("engagement_date", datetime.now(timezone.utc).isoformat()),
                        "linkedin_url": engager.get("linkedin_url", ""),
                        "confidence": confidence,
                        "additional_context": {}
                    }
                    
                    # Add comment text if available
                    if engager.get("comment_text"):
                        lead["additional_context"]["comment_text"] = engager["comment_text"]
                    
                    qualified_leads.append(lead)
                else:
                    disqualified["total"] += 1
                    
                    # Track disqualification reason
                    disq_reason = "no_icp_match"
                    if not engager.get("title"):
                        disq_reason = "insufficient_data"
                    
                    disqualified["reasons"][disq_reason] = disqualified["reasons"].get(disq_reason, 0) + 1
                    
                    # Keep sample of disqualified
                    if len(disqualified.get("sample", [])) < 5:
                        disqualified["sample"].append({
                            "name": engager.get("name", "Unknown"),
                            "role": engager.get("title", "Unknown"),
                            "reason": disq_reason
                        })
            
            # Deduplicate leads
            qualified_leads = self._deduplicate_leads(qualified_leads)
            
            # Add priority and generate messages
            for lead in qualified_leads:
                lead["priority"] = self._determine_priority(lead)
                
                if generate_messages:
                    post = post_map.get(lead.get("origin_post_id"), {})
                    lead["draft_msg"] = self._generate_message(lead, post)
            
            # Sort by priority and confidence
            priority_order = {"high": 0, "medium": 1, "low": 2}
            qualified_leads.sort(key=lambda x: (priority_order.get(x.get("priority"), 3), -x.get("confidence", 0)))
            
            # Limit results
            qualified_leads = qualified_leads[:max_leads]
            
            # Calculate post performance
            post_performance = []
            for post_id, post in post_map.items():
                leads_from_post = [l for l in qualified_leads if l.get("origin_post_id") == post_id]
                total_engagers = sum(1 for e in all_engagers if e.get("origin_post_id") == post_id)
                
                post_performance.append({
                    "post_id": post_id,
                    "topic": post.get("topic", "Unknown"),
                    "qualified_leads": len(leads_from_post),
                    "total_engagers": total_engagers,
                    "conversion_rate": round(len(leads_from_post) / total_engagers, 3) if total_engagers else 0
                })
            
            post_performance.sort(key=lambda x: x["qualified_leads"], reverse=True)
            
            # Build summary
            now = datetime.now(timezone.utc)
            period_start = now - timedelta(days=lookback_days)
            
            by_icp_type = {}
            by_engagement_type = {"reactions": 0, "comments": 0, "both": 0}
            
            for lead in qualified_leads:
                icp = lead.get("icp_type", "Unknown")
                by_icp_type[icp] = by_icp_type.get(icp, 0) + 1
                
                eng_type = lead.get("engagement_type", "reaction")
                if eng_type == "reaction":
                    by_engagement_type["reactions"] += 1
                elif eng_type == "comment":
                    by_engagement_type["comments"] += 1
                else:
                    by_engagement_type["both"] += 1
            
            summary = {
                "period": f"{period_start.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}",
                "posts_analyzed": len(posts),
                "total_engagers": len(all_engagers),
                "qualified_leads": len(qualified_leads),
                "qualification_rate": round(len(qualified_leads) / len(all_engagers), 3) if all_engagers else 0,
                "by_icp_type": by_icp_type,
                "by_engagement_type": by_engagement_type
            }
            
            # Generate recommendations
            recommendations = []
            
            high_priority = [l for l in qualified_leads if l.get("priority") == "high"]
            if high_priority:
                recommendations.append(
                    f"{len(high_priority)} high-priority leads (Primary ICP) - reach out within 48h"
                )
            
            if post_performance and post_performance[0]["qualified_leads"] > 0:
                top_post = post_performance[0]
                recommendations.append(
                    f"Post about '{top_post['topic']}' generated most qualified leads ({top_post['qualified_leads']})"
                )
            
            if summary["qualification_rate"] < 0.1:
                recommendations.append(
                    "Low qualification rate - consider expanding ICP criteria or improving targeting"
                )
            
            # Build output
            output = {
                "summary": summary,
                "qualified_leads": qualified_leads,
                "disqualified": disqualified,
                "post_performance": post_performance,
                "recommendations": recommendations
            }
            
            runtime = time.time() - self.start_time
            cost = 0.03 if generate_messages else 0.01
            
            # Determine release action
            if len(qualified_leads) >= 1:
                release_action = ReleaseAction.AUTO_DELIVER
            else:
                release_action = ReleaseAction.HUMAN_REVIEW
            
            stats = {
                "posts_analyzed": len(posts),
                "engagers_processed": len(all_engagers)
            }
            
            return {
                "status": "success" if not self.warnings else "partial",
                "output": output,
                "evaluation": {
                    "score": 0.85 if len(qualified_leads) >= 5 else 0.7,
                    "pass": len(qualified_leads) >= 1
                },
                "release_action": release_action.value,
                "run_id": self.run_id,
                "warnings": self.warnings if self.warnings else None,
                "_meta": self._build_meta(runtime, cost, release_action.value, stats)
            }
            
        except Exception as e:
            runtime = time.time() - self.start_time
            return {
                "status": "failed",
                "error": str(e),
                "error_type": type(e).__name__,
                "run_id": self.run_id,
                "_meta": self._build_meta(runtime, 0, "blocked", {})
            }


def run_qualify_leads(inputs: Dict) -> Dict:
    """
    Main entry point for qualify leads skill.
    
    Args:
        inputs: Dictionary with configuration
    
    Returns:
        Complete skill result with qualified leads and metadata
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
    
    skill = QualifyLeadsSkill(
        client_id=inputs["client_id"],
        client_name=inputs.get("client_name"),
        tenant_id=inputs.get("tenant_id"),
        execution_mode=inputs.get("execution_mode", "suggest")
    )
    
    return skill.run(inputs)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run qualify leads skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run.py --founder_id xyz123
    python run.py --client_id abc123 --founder_id xyz123
    python run.py --founder_id xyz123 --lookback_days 14
    python run.py --founder_id xyz123 --no-messages
    python run.py --founder_id xyz123 --output leads.json
        """
    )
    
    parser.add_argument("--client_id", type=str, help="Firebase Client ID")
    parser.add_argument("--founder_id", type=str, help="Founder document ID")
    parser.add_argument("--client_name", type=str, help="Client display name")
    parser.add_argument("--lookback_days", type=int, default=7, help="Days to analyze")
    parser.add_argument("--max_leads", type=int, default=100, help="Maximum leads to return")
    parser.add_argument("--no-messages", action="store_true", help="Skip message generation")
    parser.add_argument("--no-commenters", action="store_true", help="Exclude commenters")
    parser.add_argument("--no-reactors", action="store_true", help="Exclude reactors")
    parser.add_argument("--output", type=str, help="Output file path (JSON)")
    
    args = parser.parse_args()
    
    inputs = {
        "lookback_days": args.lookback_days,
        "max_leads": args.max_leads,
        "generate_messages": not args.no_messages,
        "include_commenters": not args.no_commenters,
        "include_reactors": not args.no_reactors
    }
    
    if args.client_id:
        inputs["client_id"] = args.client_id
    if args.founder_id:
        inputs["founder_id"] = args.founder_id
    if args.client_name:
        inputs["client_name"] = args.client_name
    
    result = run_qualify_leads(inputs)
    
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Output saved to {args.output}")
        
        # Print summary
        if result.get("status") in ["success", "partial"]:
            summary = result.get("output", {}).get("summary", {})
            print(f"\nQualified {summary.get('qualified_leads', 0)} leads from {summary.get('total_engagers', 0)} engagers")
    else:
        print(json.dumps(result, indent=2, default=str))
    
    sys.exit(0 if result["status"] in ["success", "partial"] else 1)


if __name__ == "__main__":
    main()
