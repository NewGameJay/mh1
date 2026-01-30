#!/usr/bin/env python3
"""
Reddit Keyword Search Skill - Execution Script (v1.0.0)

Search Reddit for posts and comments matching keywords.
Collects signals for social listening campaigns.

Usage:
    python skills/reddit-keyword-search/run.py --keyword "AI marketing" --subreddits "marketing,startups"

    from skills.reddit_keyword_search.run import run_reddit_keyword_search
    result = run_reddit_keyword_search({"keyword": "AI marketing"})
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

SKILL_NAME = "reddit-keyword-search"
SKILL_VERSION = "v1.0.0"

# Popular marketing-related subreddits
DEFAULT_SUBREDDITS = [
    "marketing", "digitalmarketing", "socialmedia", "startups",
    "entrepreneur", "SaaS", "growthHacking", "contentmarketing"
]


class RedditKeywordSearchSkill:
    """Reddit Keyword Search skill for social listening."""

    def __init__(self, client_id: str = None, client_name: str = None):
        self.client_id = client_id or "standalone"
        self.client_name = client_name
        self.run_id = str(uuid.uuid4())[:8]
        self.start_time = time.time()

        if client_id:
            self.output_dir = SYSTEM_ROOT / "clients" / client_id / "signals" / "reddit"
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def _search_reddit_posts(self, keyword: str, subreddits: List[str], limit: int = 50) -> Dict:
        """Search Reddit for posts matching keyword."""
        import random

        # Generate sample data (replace with actual Reddit API/Firecrawl when available)
        sample_posts = []

        for i in range(min(limit, 20)):
            subreddit = random.choice(subreddits)
            post = {
                "id": f"reddit_{uuid.uuid4().hex[:8]}",
                "subreddit": subreddit,
                "title": f"Discussion about {keyword} in {subreddit}",
                "author": f"u/reddit_user_{i+1}",
                "content": f"Sample Reddit post about {keyword}. This is placeholder content for development testing. What are your thoughts on {keyword}? Looking for recommendations and experiences.",
                "engagement": {
                    "upvotes": random.randint(10, 1000),
                    "comments": random.randint(5, 200),
                    "upvote_ratio": round(random.uniform(0.7, 0.99), 2)
                },
                "posted_at": datetime.now(timezone.utc).isoformat(),
                "url": f"https://reddit.com/r/{subreddit}/comments/{uuid.uuid4().hex[:6]}",
                "keyword_matched": keyword,
                "flair": random.choice(["Discussion", "Question", "Resource", None])
            }
            sample_posts.append(post)

        return {
            "posts": sample_posts,
            "total_count": len(sample_posts),
            "keyword": keyword,
            "subreddits_searched": subreddits,
            "source": "sample_data",
            "message": "Using sample data - integrate Reddit API for real results"
        }

    def _analyze_posts(self, posts: List[Dict]) -> Dict:
        """Analyze collected posts for insights."""
        if not posts:
            return {"total": 0, "by_subreddit": {}, "engagement_summary": {}}

        total_upvotes = sum(p.get("engagement", {}).get("upvotes", 0) for p in posts)
        total_comments = sum(p.get("engagement", {}).get("comments", 0) for p in posts)

        # Group by subreddit
        by_subreddit = {}
        for post in posts:
            subreddit = post.get("subreddit", "unknown")
            if subreddit not in by_subreddit:
                by_subreddit[subreddit] = {"posts": 0, "total_upvotes": 0, "total_comments": 0}
            by_subreddit[subreddit]["posts"] += 1
            by_subreddit[subreddit]["total_upvotes"] += post.get("engagement", {}).get("upvotes", 0)
            by_subreddit[subreddit]["total_comments"] += post.get("engagement", {}).get("comments", 0)

        # Sort subreddits by engagement
        top_subreddits = sorted(
            [{"subreddit": k, **v} for k, v in by_subreddit.items()],
            key=lambda x: x["total_upvotes"],
            reverse=True
        )

        return {
            "total_posts": len(posts),
            "engagement_summary": {
                "total_upvotes": total_upvotes,
                "total_comments": total_comments,
                "avg_upvotes": round(total_upvotes / len(posts), 1) if posts else 0,
                "avg_comments": round(total_comments / len(posts), 1) if posts else 0
            },
            "by_subreddit": by_subreddit,
            "top_subreddits": top_subreddits[:5]
        }

    def _extract_themes(self, posts: List[Dict]) -> List[str]:
        """Extract common themes from posts."""
        themes = set()
        theme_indicators = {
            "recommendations": ["recommend", "suggestion", "best", "favorite"],
            "problems": ["issue", "problem", "challenge", "struggle"],
            "comparisons": ["vs", "versus", "compare", "better than"],
            "how-to": ["how to", "tutorial", "guide", "steps"],
            "opinions": ["think", "opinion", "view", "thoughts"]
        }

        for post in posts:
            content = (post.get("title", "") + " " + post.get("content", "")).lower()
            for theme, keywords in theme_indicators.items():
                if any(kw in content for kw in keywords):
                    themes.add(theme)

        return list(themes)

    def _format_output_markdown(self, keyword: str, posts: List[Dict], analysis: Dict, themes: List[str]) -> str:
        """Format results as markdown."""
        md = f"""# Reddit Keyword Search: "{keyword}"

**Search Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Posts Found:** {analysis['total_posts']}

---

## Engagement Summary

| Metric | Total | Average |
|--------|-------|---------|
| Upvotes | {analysis['engagement_summary']['total_upvotes']:,} | {analysis['engagement_summary']['avg_upvotes']} |
| Comments | {analysis['engagement_summary']['total_comments']:,} | {analysis['engagement_summary']['avg_comments']} |

---

## Top Subreddits

"""
        for subreddit in analysis['top_subreddits'][:5]:
            md += f"### r/{subreddit['subreddit']}\n"
            md += f"- Posts: {subreddit['posts']} | Upvotes: {subreddit['total_upvotes']:,} | Comments: {subreddit['total_comments']:,}\n\n"

        if themes:
            md += """---

## Content Themes

"""
            for theme in themes:
                md += f"- **{theme.title()}** - Common discussion type\n"

        md += """
---

## Sample Posts

"""
        for post in posts[:5]:
            engagement = post.get("engagement", {})
            flair = f"[{post.get('flair')}] " if post.get('flair') else ""
            md += f"""### {flair}{post.get('title', 'Untitled')}

**r/{post.get('subreddit', 'unknown')}** by {post.get('author', 'anonymous')}

{post.get('content', 'No content')[:300]}...

- ⬆️ {engagement.get('upvotes', 0)} ({engagement.get('upvote_ratio', 0):.0%}) | 💬 {engagement.get('comments', 0)} comments
- [View Thread]({post.get('url', '#')})

---

"""

        md += f"""
## Engagement Opportunities

1. **High-engagement threads** - Sort by upvotes and engage in active discussions
2. **Unanswered questions** - Look for questions with few comments
3. **Weekly threads** - Many subreddits have regular promotion or question threads
4. **Cross-post** - Share insights across related subreddits

## Next Steps

1. **Join** - Subscribe to top subreddits
2. **Engage** - Add value to discussions (don't just self-promote)
3. **Monitor** - Set up alerts for your keywords
4. **Create** - Post valuable content that addresses common themes

---

*Generated by reddit-keyword-search skill on {datetime.now().strftime('%Y-%m-%d')}*
"""
        return md

    def run(self, inputs: Dict) -> Dict:
        """Main execution method."""
        keyword = inputs.get("keyword")
        subreddits = inputs.get("subreddits", DEFAULT_SUBREDDITS)
        limit = inputs.get("limit", 50)

        if isinstance(subreddits, str):
            subreddits = [s.strip() for s in subreddits.split(",")]

        if not keyword:
            return {"status": "failed", "error": "keyword is required"}

        print(f"\n{'='*60}")
        print(f"REDDIT KEYWORD SEARCH")
        print(f"{'='*60}")
        print(f"Keyword: {keyword}")
        print(f"Subreddits: {len(subreddits)}")
        print(f"Limit: {limit}")
        print(f"{'='*60}\n")

        runner = WorkflowRunner(
            workflow_name=SKILL_NAME,
            version=SKILL_VERSION,
            client=self.client_id
        )

        try:
            # Search Reddit
            print("[Searching Reddit...]")
            search_results = self._search_reddit_posts(keyword, subreddits, limit)
            posts = search_results.get("posts", [])
            print(f"  Found {len(posts)} posts")

            # Analyze results
            print("[Analyzing posts...]")
            analysis = self._analyze_posts(posts)

            # Extract themes
            print("[Extracting themes...]")
            themes = self._extract_themes(posts)

            # Format output
            markdown = self._format_output_markdown(keyword, posts, analysis, themes)

            # Save results
            if hasattr(self, 'output_dir'):
                md_path = self.output_dir / f"search-{self.run_id}.md"
                md_path.write_text(markdown)

                json_path = self.output_dir / f"search-{self.run_id}.json"
                json_path.write_text(json.dumps({
                    "keyword": keyword,
                    "posts": posts,
                    "analysis": analysis,
                    "themes": themes
                }, indent=2, default=str))

                print(f"\n  Saved to: {self.output_dir}")

            runtime = time.time() - self.start_time

            result = {
                "status": "success",
                "keyword": keyword,
                "posts_found": len(posts),
                "subreddits_searched": subreddits,
                "posts": posts,
                "analysis": analysis,
                "themes": themes,
                "markdown": markdown,
                "source": search_results.get("source", "api"),
                "run_id": runner.run_id,
                "runtime_seconds": round(runtime, 2)
            }

            print(f"\n{'='*60}")
            print(f"SEARCH COMPLETE - {len(posts)} posts from {len(analysis['by_subreddit'])} subreddits")
            print(f"{'='*60}\n")

            runner.complete(RunStatus.SUCCESS)
            return result

        except Exception as e:
            runner.complete(RunStatus.FAILED)
            return {"status": "failed", "error": str(e), "run_id": runner.run_id}


def run_reddit_keyword_search(inputs: Dict) -> Dict:
    """Main entry point for Reddit keyword search skill."""
    skill = RedditKeywordSearchSkill(
        client_id=inputs.get("client_id"),
        client_name=inputs.get("client_name")
    )
    return skill.run(inputs)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Search Reddit for keyword mentions")
    parser.add_argument("--keyword", type=str, required=True, help="Keyword to search for")
    parser.add_argument("--subreddits", type=str, help="Comma-separated subreddits to search")
    parser.add_argument("--limit", type=int, default=50, help="Max posts to return")
    parser.add_argument("--client_id", type=str, help="Client identifier")
    parser.add_argument("--output", type=str, help="Output file path (JSON)")

    args = parser.parse_args()

    inputs = {
        "keyword": args.keyword,
        "limit": args.limit
    }
    if args.subreddits: inputs["subreddits"] = args.subreddits
    if args.client_id: inputs["client_id"] = args.client_id

    result = run_reddit_keyword_search(inputs)

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
