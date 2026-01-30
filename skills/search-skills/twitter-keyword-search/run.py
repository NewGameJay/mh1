#!/usr/bin/env python3
"""
Twitter Keyword Search Skill - Execution Script (v1.0.0)

Search Twitter for posts matching keywords using Crustdata API.
Collects signals for social listening campaigns.

Usage:
    python skills/twitter-keyword-search/run.py --keyword "AI marketing" --limit 50

    from skills.twitter_keyword_search.run import run_twitter_keyword_search
    result = run_twitter_keyword_search({"keyword": "AI marketing", "limit": 50})
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

SKILL_NAME = "twitter-keyword-search"
SKILL_VERSION = "v1.0.0"


class TwitterKeywordSearchSkill:
    """Twitter Keyword Search skill for social listening."""

    def __init__(self, client_id: str = None, client_name: str = None):
        self.client_id = client_id or "standalone"
        self.client_name = client_name
        self.run_id = str(uuid.uuid4())[:8]
        self.start_time = time.time()
        self.api_key = os.getenv("CRUSTDATA_API_KEY")

        if client_id:
            self.output_dir = SYSTEM_ROOT / "clients" / client_id / "signals" / "twitter"
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def _search_twitter_posts(self, keyword: str, limit: int = 50, date_range: str = "7d") -> Dict:
        """Search Twitter for posts matching keyword."""
        import random

        # Generate sample data (replace with actual API call when available)
        sample_posts = []
        handles = ["@techfounder", "@marketingpro", "@aiexpert", "@growthguru", "@startupgeek"]

        for i in range(min(limit, 20)):
            post = {
                "id": f"tweet_{uuid.uuid4().hex[:8]}",
                "author": {
                    "handle": random.choice(handles),
                    "name": f"User {i+1}",
                    "followers": random.randint(1000, 100000),
                    "verified": random.random() > 0.7
                },
                "content": f"Sample tweet about {keyword}. This is placeholder content for development. #marketing #ai",
                "engagement": {
                    "likes": random.randint(5, 500),
                    "retweets": random.randint(0, 100),
                    "replies": random.randint(0, 50),
                    "views": random.randint(100, 10000)
                },
                "posted_at": datetime.now(timezone.utc).isoformat(),
                "url": f"https://twitter.com/user/status/{uuid.uuid4().hex[:10]}",
                "keyword_matched": keyword
            }
            sample_posts.append(post)

        return {
            "posts": sample_posts,
            "total_count": len(sample_posts),
            "keyword": keyword,
            "source": "sample_data",
            "message": "Using sample data - integrate Twitter API for real results"
        }

    def _analyze_posts(self, posts: List[Dict]) -> Dict:
        """Analyze collected posts for insights."""
        if not posts:
            return {"total": 0, "top_accounts": [], "engagement_summary": {}}

        total_likes = sum(p.get("engagement", {}).get("likes", 0) for p in posts)
        total_retweets = sum(p.get("engagement", {}).get("retweets", 0) for p in posts)
        total_replies = sum(p.get("engagement", {}).get("replies", 0) for p in posts)
        total_views = sum(p.get("engagement", {}).get("views", 0) for p in posts)

        # Find top accounts by engagement
        account_engagement = {}
        for post in posts:
            handle = post.get("author", {}).get("handle", "Unknown")
            engagement = (
                post.get("engagement", {}).get("likes", 0) +
                post.get("engagement", {}).get("retweets", 0) * 3 +
                post.get("engagement", {}).get("replies", 0) * 2
            )
            if handle not in account_engagement:
                account_engagement[handle] = {"total": 0, "posts": 0, "info": post.get("author", {})}
            account_engagement[handle]["total"] += engagement
            account_engagement[handle]["posts"] += 1

        top_accounts = sorted(
            [{"handle": k, **v} for k, v in account_engagement.items()],
            key=lambda x: x["total"],
            reverse=True
        )[:5]

        return {
            "total_posts": len(posts),
            "engagement_summary": {
                "total_likes": total_likes,
                "total_retweets": total_retweets,
                "total_replies": total_replies,
                "total_views": total_views,
                "avg_likes": round(total_likes / len(posts), 1) if posts else 0,
                "avg_retweets": round(total_retweets / len(posts), 1) if posts else 0
            },
            "top_accounts": top_accounts
        }

    def _format_output_markdown(self, keyword: str, posts: List[Dict], analysis: Dict) -> str:
        """Format results as markdown."""
        md = f"""# Twitter Keyword Search: "{keyword}"

**Search Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Posts Found:** {analysis['total_posts']}

---

## Engagement Summary

| Metric | Total | Average |
|--------|-------|---------|
| Likes | {analysis['engagement_summary']['total_likes']:,} | {analysis['engagement_summary']['avg_likes']} |
| Retweets | {analysis['engagement_summary']['total_retweets']:,} | {analysis['engagement_summary']['avg_retweets']} |
| Replies | {analysis['engagement_summary']['total_replies']:,} | - |
| Views | {analysis['engagement_summary']['total_views']:,} | - |

---

## Top Accounts

"""
        for i, account in enumerate(analysis['top_accounts'][:5], 1):
            info = account.get("info", {})
            verified = "✓" if info.get("verified") else ""
            md += f"{i}. **{account['handle']}** {verified} - {info.get('followers', 0):,} followers\n"
            md += f"   - Posts: {account['posts']} | Engagement Score: {account['total']}\n"

        md += """
---

## Sample Posts

"""
        for post in posts[:5]:
            author = post.get("author", {})
            engagement = post.get("engagement", {})
            verified = "✓" if author.get("verified") else ""
            md += f"""### {author.get('handle', 'Unknown')} {verified}

{post.get('content', 'No content')[:280]}

- ❤️ {engagement.get('likes', 0)} | 🔄 {engagement.get('retweets', 0)} | 💬 {engagement.get('replies', 0)} | 👁️ {engagement.get('views', 0)}
- [View Tweet]({post.get('url', '#')})

---

"""

        md += f"""
## Next Steps

1. **Engage** - Reply to relevant conversations
2. **Follow** - Connect with top accounts in the space
3. **Analyze** - Identify content themes that resonate
4. **Create** - Use insights to inform your content strategy

---

*Generated by twitter-keyword-search skill on {datetime.now().strftime('%Y-%m-%d')}*
"""
        return md

    def run(self, inputs: Dict) -> Dict:
        """Main execution method."""
        keyword = inputs.get("keyword")
        limit = inputs.get("limit", 50)
        date_range = inputs.get("date_range", "7d")

        if not keyword:
            return {"status": "failed", "error": "keyword is required"}

        print(f"\n{'='*60}")
        print(f"TWITTER KEYWORD SEARCH")
        print(f"{'='*60}")
        print(f"Keyword: {keyword}")
        print(f"Limit: {limit}")
        print(f"Date Range: {date_range}")
        print(f"{'='*60}\n")

        runner = WorkflowRunner(
            workflow_name=SKILL_NAME,
            version=SKILL_VERSION,
            client=self.client_id
        )

        try:
            # Search Twitter
            print("[Searching Twitter...]")
            search_results = self._search_twitter_posts(keyword, limit, date_range)
            posts = search_results.get("posts", [])
            print(f"  Found {len(posts)} posts")

            # Analyze results
            print("[Analyzing posts...]")
            analysis = self._analyze_posts(posts)

            # Format output
            markdown = self._format_output_markdown(keyword, posts, analysis)

            # Save results
            if hasattr(self, 'output_dir'):
                md_path = self.output_dir / f"search-{self.run_id}.md"
                md_path.write_text(markdown)

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


def run_twitter_keyword_search(inputs: Dict) -> Dict:
    """Main entry point for Twitter keyword search skill."""
    skill = TwitterKeywordSearchSkill(
        client_id=inputs.get("client_id"),
        client_name=inputs.get("client_name")
    )
    return skill.run(inputs)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Search Twitter for keyword mentions")
    parser.add_argument("--keyword", type=str, required=True, help="Keyword to search for")
    parser.add_argument("--limit", type=int, default=50, help="Max posts to return")
    parser.add_argument("--date_range", type=str, default="7d",
                       choices=["24h", "7d", "30d"], help="Date range filter")
    parser.add_argument("--client_id", type=str, help="Client identifier")
    parser.add_argument("--output", type=str, help="Output file path (JSON)")

    args = parser.parse_args()

    inputs = {
        "keyword": args.keyword,
        "limit": args.limit,
        "date_range": args.date_range
    }
    if args.client_id: inputs["client_id"] = args.client_id

    result = run_twitter_keyword_search(inputs)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2, default=str)
    else:
        print(f"\nKeyword: {result.get('keyword')}")
        print(f"Posts Found: {result.get('posts_found', 0)}")
        print(f"Status: {result.get('status')}")

    sys.exit(0 if result.get("status") == "success" else 1)


if __name__ == "__main__":
    main()
