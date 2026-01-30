"""
Reddit Keyword Search - GPai Signal Collection
Customized for Perspective AI keywords
"""

import os
import praw
from datetime import datetime, timedelta
from collections import defaultdict
import time
import csv
import sys
import io
import json
import argparse

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ============================================================================
# CONFIGURATION
# ============================================================================

# Reddit API Credentials - loaded from environment variables
REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = "KeywordSearch/1.0 by retr0b0t"

# Search Parameters - GPai Keywords
KEYWORDS = [
    "customer research automation",
    "AI user interviews",
    "qualitative research",
    "product discovery research",
    "customer feedback tools",
    "survey alternative",
    "voice of customer",
    "user research software",
]

# Subreddits to search
SUBREDDITS = [
    ("SaaS", 0),
    ("startups", 0),
    ("ProductManagement", 0),
    ("UXResearch", 0),
    ("CustomerSuccess", 0),
    ("Entrepreneur", 0),
    ("userexperience", 0),
]

# Time Range - 1 week (for 7d lookback)
MONTHS_BACK = 1  # Will use time_filter="week" instead

# Exclusion Filters
EXCLUSION_PATTERNS = [
    "/jfe/form",
    "typeform.com/to/",
    "surveymonkey.com/r/",
    "forms.gle/",
    "getfeedback.com",
    "crypto",
    "nft",
    "airdrop",
]

PROJECT_NAME = "gpai_signals"

# ============================================================================
# SCRIPT
# ============================================================================

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
)


def scrape_subreddit_for_keywords(
    subreddit_name, keywords, time_filter="week", seen_post_ids=None, log=None
):
    if log is None:
        log = sys.stderr
    if seen_post_ids is None:
        seen_post_ids = set()

    results = []
    duplicate_count = 0
    filtered_count = 0

    print(f"  🔄 Searching r/{subreddit_name}...", file=log)

    try:
        subreddit = reddit.subreddit(subreddit_name)

        for keyword in keywords:
            keyword_results = 0

            for submission in subreddit.search(
                keyword, limit=50, time_filter=time_filter, sort="new"
            ):
                # Check for duplicates
                if submission.id in seen_post_ids:
                    duplicate_count += 1
                    continue

                # Apply exclusion filters
                text_to_check = (
                    f"{submission.title} {submission.selftext} {submission.url}"
                ).lower()
                if any(pattern.lower() in text_to_check for pattern in EXCLUSION_PATTERNS):
                    filtered_count += 1
                    continue

                # Mark as seen
                seen_post_ids.add(submission.id)
                keyword_results += 1

                post_date = datetime.fromtimestamp(submission.created_utc)

                post_data = {
                    "post_id": submission.id,
                    "matched_keyword": keyword,
                    "title": submission.title,
                    "selftext": submission.selftext[:2000],
                    "url": submission.url,
                    "permalink": f"https://reddit.com{submission.permalink}",
                    "subreddit": str(submission.subreddit),
                    "author": str(submission.author) if submission.author else "[deleted]",
                    "score": submission.score,
                    "upvote_ratio": submission.upvote_ratio,
                    "num_comments": submission.num_comments,
                    "created_utc": submission.created_utc,
                    "created_date": post_date.strftime("%Y-%m-%d %H:%M:%S"),
                }

                results.append(post_data)

            if keyword_results > 0:
                print(f"     • Found {keyword_results} posts for '{keyword}'", file=log)

            time.sleep(0.5)

        print(f"  ✅ Found {len(results)} unique posts in r/{subreddit_name}", file=log)
        if filtered_count > 0:
            print(f"     (Filtered {filtered_count} posts)", file=log)

    except Exception as e:
        print(f"  ❌ Error scraping r/{subreddit_name}: {str(e)}", file=log)

    return results, seen_post_ids


def scrape_all_subreddits(subreddit_config, keywords, time_filter="week", log=None):
    if log is None:
        log = sys.stderr

    print("\n" + "=" * 80, file=log)
    print("🚀 REDDIT KEYWORD SEARCH - GPai Signals", file=log)
    print("=" * 80, file=log)

    all_results = []
    seen_post_ids = set()
    subreddit_stats = {}

    for i, (subreddit_name, _) in enumerate(subreddit_config, 1):
        print(f"\n[{i}/{len(subreddit_config)}] Processing: r/{subreddit_name}", file=log)

        results, seen_post_ids = scrape_subreddit_for_keywords(
            subreddit_name, keywords, time_filter, seen_post_ids=seen_post_ids, log=log
        )
        all_results.extend(results)
        subreddit_stats[subreddit_name] = len(results)

        time.sleep(1)

    return all_results, subreddit_stats


def output_json(data, project_name="reddit_search"):
    output = {
        "platform": "reddit",
        "project": project_name,
        "collectedAt": datetime.now().isoformat(),
        "count": len(data),
        "posts": data
    }
    print(json.dumps(output, ensure_ascii=False, default=str))


def print_summary(data, subreddit_stats, log=None):
    if log is None:
        log = sys.stderr

    print("\n" + "=" * 80, file=log)
    print("✨ COLLECTION COMPLETE!", file=log)
    print("=" * 80, file=log)
    print(f"\n📊 Total Posts: {len(data)}", file=log)

    if data:
        keyword_counts = defaultdict(int)
        for post in data:
            keyword_counts[post["matched_keyword"]] += 1

        print(f"\n🎯 Posts per Keyword:", file=log)
        for keyword, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {keyword:<30} {count:>3} posts", file=log)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Reddit Keyword Search - GPai Signals')
    parser.add_argument('--json', action='store_true', help='Output JSON to stdout')
    parser.add_argument('--limit', type=int, default=None, help='Max posts to output')
    args = parser.parse_args()

    log = sys.stderr if args.json else sys.stdout

    print("🎯 REDDIT KEYWORD SEARCH - GPai Signals", file=log)
    print("=" * 80, file=log)
    print(f"Keywords: {len(KEYWORDS)} configured", file=log)
    print(f"Subreddits: {len(SUBREDDITS)} configured", file=log)
    if args.json:
        print(f"Output mode: JSON to stdout", file=log)
    print("=" * 80, file=log)

    scraped_data, subreddit_stats = scrape_all_subreddits(
        SUBREDDITS, KEYWORDS, time_filter="week", log=log
    )

    if args.limit and scraped_data and len(scraped_data) > args.limit:
        print(f"\n📉 Limiting to top {args.limit} posts", file=log)
        scraped_data = sorted(
            scraped_data,
            key=lambda x: x.get('score', 0) + x.get('num_comments', 0),
            reverse=True
        )[:args.limit]

    if scraped_data:
        if args.json:
            output_json(scraped_data, PROJECT_NAME)
            print_summary(scraped_data, subreddit_stats, log=log)
            print(f"\n✅ Output {len(scraped_data)} posts as JSON", file=log)
        else:
            print_summary(scraped_data, subreddit_stats, log=log)
    else:
        print("\n⚠️ No data was collected.", file=log)
