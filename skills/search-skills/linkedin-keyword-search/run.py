#!/usr/bin/env python3
"""
LinkedIn Keyword Search Skill - Execution Script (v1.0.0)

Search LinkedIn for posts matching keywords using Crustdata API.
Collects signals for social listening campaigns.

Usage:
    python skills/linkedin-keyword-search/run.py --keyword "AI marketing" --limit 50

    from skills.linkedin_keyword_search.run import run_linkedin_keyword_search
    result = run_linkedin_keyword_search({"keyword": "AI marketing", "limit": 50})
"""

import argparse
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

SKILL_ROOT = Path(__file__).parent
SYSTEM_ROOT = SKILL_ROOT.parent.parent
sys.path.insert(0, str(SYSTEM_ROOT / "lib"))

try:
    from runner import WorkflowRunner, RunStatus
except ImportError:
    class RunStatus:
        SUCCESS = "success"
        FAILED = "failed"
    class WorkflowRunner:
        def __init__(self, **kwargs): self.run_id = str(uuid.uuid4())[:8]
        def complete(self, status, evaluation=None): return {}

SKILL_NAME = "linkedin-keyword-search"
SKILL_VERSION = "v1.0.0"

# Crustdata API configuration
CRUSTDATA_API_URL = "https://api.crustdata.com/screener/linkedin_posts/search"


class LinkedInKeywordSearchSkill:
    """LinkedIn Keyword Search skill for social listening."""

    def __init__(self, client_id: str = None, client_name: str = None):
        self.client_id = client_id or "standalone"
        self.client_name = client_name
        self.run_id = str(uuid.uuid4())[:8]
        self.start_time = time.time()
        self.api_key = os.getenv("CRUSTDATA_API_KEY")

        if client_id:
            self.output_dir = SYSTEM_ROOT / "clients" / client_id / "signals" / "linkedin"
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def _search_linkedin_posts(self, keyword: str, limit: int = 50, date_posted: str = "PAST_WEEK") -> Dict:
        """Search LinkedIn for posts matching keyword via Crustdata API."""
        if not self.api_key:
            # Return sample data for development/testing
            return self._generate_sample_data(keyword, limit)

        import subprocess

        # Build API request
        payload = {
            "keyword": keyword,
            "date_posted": date_posted,
            "limit": limit,
            "sort_by": "relevance"
        }

        try:
            # Call Crustdata API
            result = subprocess.run(
                [
                    "curl", "-s", "-X", "POST",
                    CRUSTDATA_API_URL,
                    "-H", f"Authorization: Bearer {self.api_key}",
                    "-H", "Content-Type: application/json",
                    "-d", json.dumps(payload)
                ],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return self._generate_sample_data(keyword, limit)

        except Exception as e:
            print(f"API call failed: {e}")
            return self._generate_sample_data(keyword, limit)

    def _generate_sample_data(self, keyword: str, limit: int) -> Dict:
        """Generate sample LinkedIn post data for testing."""
        import random

        sample_posts = []
        companies = ["TechCorp", "AI Startup", "Marketing Inc", "Growth Co", "SaaS Leader"]
        titles = ["CEO", "VP Marketing", "Head of Growth", "CMO", "Founder"]

        for i in range(min(limit, 10)):
            post = {
                "id": f"linkedin_post_{uuid.uuid4().hex[:8]}",
                "author": {
                    "name": f"Sample Author {i+1}",
                    "title": random.choice(titles),
                    "company": random.choice(companies),
                    "followers": random.randint(500, 50000)
                },
                "content": f"Sample post about {keyword}. This is placeholder content for development testing. The actual API would return real LinkedIn posts matching the keyword.",
                "engagement": {
                    "likes": random.randint(10, 500),
                    "comments": random.randint(1, 50),
                    "shares": random.randint(0, 20)
                },
                "posted_at": datetime.now(timezone.utc).isoformat(),
                "url": f"https://linkedin.com/posts/sample-{i+1}",
                "keyword_matched": keyword
            }
            sample_posts.append(post)

        return {
            "posts": sample_posts,
            "total_count": len(sample_posts),
            "keyword": keyword,
            "source": "sample_data",
            "message": "Using sample data - set CRUSTDATA_API_KEY for real results"
        }

    def _analyze_posts(self, posts: List[Dict]) -> Dict:
        """Analyze collected posts for insights."""
        if not posts:
            return {"total": 0, "top_authors": [], "engagement_summary": {}}

        total_likes = sum(p.get("engagement", {}).get("likes", 0) for p in posts)
        total_comments = sum(p.get("engagement", {}).get("comments", 0) for p in posts)
        total_shares = sum(p.get("engagement", {}).get("shares", 0) for p in posts)

        # Find top authors by engagement
        author_engagement = {}
        for post in posts:
            author = post.get("author", {}).get("name", "Unknown")
            engagement = (
                post.get("engagement", {}).get("likes", 0) +
                post.get("engagement", {}).get("comments", 0) * 3 +
                post.get("engagement", {}).get("shares", 0) * 5
            )
            if author not in author_engagement:
                author_engagement[author] = {"total": 0, "posts": 0, "info": post.get("author", {})}
            author_engagement[author]["total"] += engagement
            author_engagement[author]["posts"] += 1

        top_authors = sorted(
            [{"name": k, **v} for k, v in author_engagement.items()],
            key=lambda x: x["total"],
            reverse=True
        )[:5]

        return {
            "total_posts": len(posts),
            "engagement_summary": {
                "total_likes": total_likes,
                "total_comments": total_comments,
                "total_shares": total_shares,
                "avg_likes": round(total_likes / len(posts), 1) if posts else 0,
                "avg_comments": round(total_comments / len(posts), 1) if posts else 0
            },
            "top_authors": top_authors
        }

    def _format_output_markdown(self, keyword: str, posts: List[Dict], analysis: Dict) -> str:
        """Format results as markdown."""
        md = f"""# LinkedIn Keyword Search: "{keyword}"

**Search Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Posts Found:** {analysis['total_posts']}

---

## Engagement Summary

| Metric | Total | Average |
|--------|-------|---------|
| Likes | {analysis['engagement_summary']['total_likes']} | {analysis['engagement_summary']['avg_likes']} |
| Comments | {analysis['engagement_summary']['total_comments']} | {analysis['engagement_summary']['avg_comments']} |
| Shares | {analysis['engagement_summary']['total_shares']} | - |

---

## Top Authors

"""
        for i, author in enumerate(analysis['top_authors'][:5], 1):
            info = author.get("info", {})
            md += f"{i}. **{author['name']}** - {info.get('title', 'N/A')} at {info.get('company', 'N/A')}\n"
            md += f"   - Posts: {author['posts']} | Engagement Score: {author['total']}\n"

        md += """
---

## Sample Posts

"""
        for post in posts[:5]:
            author = post.get("author", {})
            engagement = post.get("engagement", {})
            md += f"""### {author.get('name', 'Unknown')} ({author.get('title', 'N/A')})

{post.get('content', 'No content')[:200]}...

- Likes: {engagement.get('likes', 0)} | Comments: {engagement.get('comments', 0)} | Shares: {engagement.get('shares', 0)}
- [View Post]({post.get('url', '#')})

---

"""

        md += f"""
## Next Steps

1. **Engage** - Comment on high-engagement posts to build visibility
2. **Analyze** - Identify content themes that resonate
3. **Connect** - Reach out to top authors in your niche
4. **Create** - Use insights to inform your content strategy

---

*Generated by linkedin-keyword-search skill on {datetime.now().strftime('%Y-%m-%d')}*
"""
        return md

    def run(self, inputs: Dict) -> Dict:
        """Main execution method."""
        keyword = inputs.get("keyword")
        limit = inputs.get("limit", 50)
        date_posted = inputs.get("date_posted", "PAST_WEEK")

        if not keyword:
            return {"status": "failed", "error": "keyword is required"}

        print(f"\n{'='*60}")
        print(f"LINKEDIN KEYWORD SEARCH")
        print(f"{'='*60}")
        print(f"Keyword: {keyword}")
        print(f"Limit: {limit}")
        print(f"Date Range: {date_posted}")
        print(f"API Key: {'✓ Set' if self.api_key else '✗ Not set (using sample data)'}")
        print(f"{'='*60}\n")

        runner = WorkflowRunner(
            workflow_name=SKILL_NAME,
            version=SKILL_VERSION,
            client=self.client_id
        )

        try:
            # Search LinkedIn
            print("[Searching LinkedIn...]")
            search_results = self._search_linkedin_posts(keyword, limit, date_posted)
            posts = search_results.get("posts", [])
            print(f"  Found {len(posts)} posts")

            # Analyze results
            print("[Analyzing posts...]")
            analysis = self._analyze_posts(posts)

            # Format output
            markdown = self._format_output_markdown(keyword, posts, analysis)

            # Save results
            if hasattr(self, 'output_dir'):
                # Save markdown
                md_path = self.output_dir / f"search-{self.run_id}.md"
                md_path.write_text(markdown)

                # Save JSON
                json_path = self.output_dir / f"search-{self.run_id}.json"
                json_path.write_text(json.dumps({
                    "keyword": keyword,
                    "posts": posts,
                    "analysis": analysis
                }, indent=2, default=str))

                print(f"\n  Saved to: {self.output_dir}")

            runtime = time.time() - self.start_time

            result = {
                "status": "success",
                "keyword": keyword,
                "posts_found": len(posts),
                "posts": posts,
                "analysis": analysis,
                "markdown": markdown,
                "source": search_results.get("source", "api"),
                "run_id": runner.run_id,
                "runtime_seconds": round(runtime, 2)
            }

            print(f"\n{'='*60}")
            print(f"SEARCH COMPLETE - {len(posts)} posts collected")
            print(f"{'='*60}\n")

            runner.complete(RunStatus.SUCCESS)
            return result

        except Exception as e:
            runner.complete(RunStatus.FAILED)
            return {"status": "failed", "error": str(e), "run_id": runner.run_id}


def run_linkedin_keyword_search(inputs: Dict) -> Dict:
    """Main entry point for LinkedIn keyword search skill."""
    skill = LinkedInKeywordSearchSkill(
        client_id=inputs.get("client_id"),
        client_name=inputs.get("client_name")
    )
    return skill.run(inputs)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Search LinkedIn for keyword mentions")
    parser.add_argument("--keyword", type=str, required=True, help="Keyword to search for")
    parser.add_argument("--limit", type=int, default=50, help="Max posts to return")
    parser.add_argument("--date_posted", type=str, default="PAST_WEEK",
                       choices=["PAST_24H", "PAST_WEEK", "PAST_MONTH"], help="Date range filter")
    parser.add_argument("--client_id", type=str, help="Client identifier")
    parser.add_argument("--output", type=str, help="Output file path (JSON)")

    args = parser.parse_args()

    inputs = {
        "keyword": args.keyword,
        "limit": args.limit,
        "date_posted": args.date_posted
    }
    if args.client_id: inputs["client_id"] = args.client_id

    result = run_linkedin_keyword_search(inputs)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2, default=str)
    else:
        # Print summary, not full JSON
        print(f"\nKeyword: {result.get('keyword')}")
        print(f"Posts Found: {result.get('posts_found', 0)}")
        print(f"Status: {result.get('status')}")

    sys.exit(0 if result.get("status") == "success" else 1)


if __name__ == "__main__":
    main()
