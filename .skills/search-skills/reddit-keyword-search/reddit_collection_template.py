"""
Reddit Keyword Search Collection Template

This template collects Reddit posts based on keywords and subreddits.
Customize the configuration section for your specific use case.
Client ID is read from inputs/active_client.md at runtime.

Usage:
    python reddit_collection_template.py                    # Output CSV files (default)
    python reddit_collection_template.py --json             # Output JSON to stdout
    python reddit_collection_template.py --json --limit 200 # Output JSON, limit to top 200 by engagement
"""

import sys
import io
import json
import csv
import time
import argparse
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    import praw
except ImportError:
    print("Installing praw...", file=sys.stderr)
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "praw", "-q"])
    import praw

# ============================================================================
# CLIENT CONFIGURATION - Read from inputs/active_client.md
# ============================================================================

def get_client_config():
    """Read client configuration from inputs/active_client.md."""
    # Find project root (where inputs/ directory is)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent  # skills/reddit-keyword-search -> mh1-hq
    
    active_client_path = project_root / "inputs" / "active_client.md"
    
    if not active_client_path.exists():
        print(f"Warning: active_client.md not found at {active_client_path}", file=sys.stderr)
        return {"client_id": "", "client_name": "Unknown"}
    
    content = active_client_path.read_text()
    config = {}
    
    for line in content.split('\n'):
        line = line.strip()
        if '=' in line:
            parts = line.split('=', 1)
            if len(parts) == 2:
                key = parts[0].strip().upper()
                value = parts[1].strip().strip('"\'')
                if key == 'CLIENT_ID':
                    config['client_id'] = value
                elif key == 'CLIENT_NAME':
                    config['client_name'] = value
    
    return config

# Load client config
CLIENT_CONFIG = get_client_config()
CLIENT_ID = CLIENT_CONFIG.get('client_id', '')
CLIENT_NAME = CLIENT_CONFIG.get('client_name', 'Unknown')

# ============================================================================
# CONFIGURATION - Customize these values
# ============================================================================

# Reddit API Credentials (MH1 account)
REDDIT_CLIENT_ID = "3Fs5LuDQiRxkVutQCieMrg"
REDDIT_CLIENT_SECRET = "fZl2T7hJmhZan9PLhFvfP_TwJHS8ew"
REDDIT_USER_AGENT = "KeywordSearch/1.0 by retr0b0t"

# Search Parameters
KEYWORDS = [
    "female founder",
    "women entrepreneur",
    "woman founder",
    "women-owned business",
]

# Subreddits to search (without r/ prefix)
SUBREDDITS = [
    ("Entrepreneur", 0),
    ("startups", 0),
    ("smallbusiness", 0),
    ("womeninbusiness", 0),
    ("femalefounders", 0),
]

# Time Range (in months)
MONTHS_BACK = 12

# Exclusion Filters
EXCLUSION_PATTERNS = [
    "/jfe/form",  # Qualtrics surveys
    "typeform.com/to/",
    "surveymonkey.com/r/",
    "forms.gle/",
]

# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================

PROJECT_NAME = f"{CLIENT_NAME.lower().replace(' ', '_')}_reddit_search"

# Get project root for output
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
OUTPUT_DIR = str(PROJECT_ROOT / "clients" / CLIENT_ID / "social-listening" / "collection-data") if CLIENT_ID else "output"

# ============================================================================
# SCRIPT
# ============================================================================

Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# Initialize Reddit API
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
)


def scrape_subreddit_for_keywords(
    subreddit_name, keywords, months=12, time_filter="year", seen_post_ids=None
):
    """Scrape a specific subreddit for multiple keywords with filtering."""
    if seen_post_ids is None:
        seen_post_ids = set()

    cutoff_date = datetime.now() - timedelta(days=months * 30)
    results = []
    duplicate_count = 0
    filtered_count = 0

    print(f"   Searching r/{subreddit_name} for keywords: {', '.join(keywords)}", file=sys.stderr)

    try:
        subreddit = reddit.subreddit(subreddit_name)

        for keyword in keywords:
            keyword_results = 0

            for submission in subreddit.search(
                keyword, limit=None, time_filter=time_filter, sort="new"
            ):
                post_date = datetime.fromtimestamp(submission.created_utc)

                if post_date >= cutoff_date:
                    if submission.id in seen_post_ids:
                        duplicate_count += 1
                        continue

                    text_to_check = (
                        f"{submission.title} {submission.selftext} {submission.url}"
                    ).lower()
                    if any(pattern.lower() in text_to_check for pattern in EXCLUSION_PATTERNS):
                        filtered_count += 1
                        continue

                    seen_post_ids.add(submission.id)
                    keyword_results += 1

                    post_data = {
                        "post_id": submission.id,
                        "matched_keyword": keyword,
                        "title": submission.title,
                        "selftext": submission.selftext[:1000],
                        "url": submission.url,
                        "permalink": f"https://reddit.com{submission.permalink}",
                        "subreddit": str(submission.subreddit),
                        "author": str(submission.author) if submission.author else "[deleted]",
                        "score": submission.score,
                        "upvote_ratio": submission.upvote_ratio,
                        "num_comments": submission.num_comments,
                        "created_utc": submission.created_utc,
                        "created_date": post_date.strftime("%Y-%m-%d %H:%M:%S"),
                        "is_self": submission.is_self,
                        "link_flair_text": submission.link_flair_text if submission.link_flair_text else "",
                        "over_18": submission.over_18,
                    }

                    results.append(post_data)

            if keyword_results > 0:
                print(f"      Found {keyword_results} posts for '{keyword}'", file=sys.stderr)

            time.sleep(1)

        print(f"   Found {len(results)} total unique posts in r/{subreddit_name}", file=sys.stderr)
        if filtered_count > 0:
            print(f"      (Filtered {filtered_count} posts matching exclusion patterns)", file=sys.stderr)

    except Exception as e:
        print(f"   Error scraping r/{subreddit_name}: {str(e)}", file=sys.stderr)

    return results, seen_post_ids


def scrape_all_subreddits(subreddit_config, keywords, months=12):
    """Scrape all subreddits for keywords."""
    print("\n" + "=" * 60, file=sys.stderr)
    print(" STARTING REDDIT KEYWORD SEARCH", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"Client: {CLIENT_NAME} ({CLIENT_ID})", file=sys.stderr)
    print(f"Keywords: {', '.join(keywords)}", file=sys.stderr)
    print(f"Time frame: Last {months} months", file=sys.stderr)
    print(f"Exclusion filters: {len(EXCLUSION_PATTERNS)} patterns active", file=sys.stderr)

    all_results = []
    seen_post_ids = set()
    subreddit_stats = {}

    for i, (subreddit_name, _) in enumerate(subreddit_config, 1):
        print(f"\n[{i}/{len(subreddit_config)}] Processing: r/{subreddit_name}", file=sys.stderr)

        results, seen_post_ids = scrape_subreddit_for_keywords(
            subreddit_name, keywords, months, seen_post_ids=seen_post_ids
        )
        all_results.extend(results)
        subreddit_stats[subreddit_name] = len(results)

        time.sleep(2)

    return all_results, subreddit_stats


def output_json(data, project_name="reddit_search"):
    """Output posts as JSON to stdout."""
    output = {
        "platform": "reddit",
        "project": project_name,
        "clientId": CLIENT_ID,
        "clientName": CLIENT_NAME,
        "collectedAt": datetime.now().isoformat(),
        "count": len(data),
        "posts": data
    }
    print(json.dumps(output, ensure_ascii=False, default=str))


def print_summary(data, subreddit_stats, keywords, file=None):
    """Print final summary."""
    out = file or sys.stdout
    print("\n" + "=" * 60, file=out)
    print(" COLLECTION COMPLETE!", file=out)
    print("=" * 60, file=out)
    print(f"\n Total Unique Posts: {len(data)}", file=out)

    print(f"\n Posts per Subreddit:", file=out)
    for subreddit, count in sorted(subreddit_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  r/{subreddit:<30} {count:>5} posts", file=out)

    if data:
        keyword_counts = defaultdict(int)
        for post in data:
            keyword_counts[post["matched_keyword"]] += 1

        print(f"\n Posts per Keyword:", file=out)
        for keyword, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {keyword:<20} {count:>5} posts", file=out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Reddit Keyword Search')
    parser.add_argument('--json', action='store_true', help='Output JSON to stdout')
    parser.add_argument('--limit', type=int, default=None, help='Max posts to output')
    args = parser.parse_args()

    log = sys.stderr if args.json else sys.stdout

    print(" REDDIT KEYWORD SEARCH", file=log)
    print(f"Client: {CLIENT_NAME} ({CLIENT_ID})", file=log)
    print(f"Project: {PROJECT_NAME}", file=log)
    print(f"Keywords: {', '.join(KEYWORDS)}", file=log)
    print(f"Subreddits: {len(SUBREDDITS)} total", file=log)
    if args.json:
        print(f"Output mode: JSON to stdout", file=log)
    if args.limit:
        print(f"Limit: {args.limit} posts", file=log)

    # Full scrape
    scraped_data, subreddit_stats = scrape_all_subreddits(
        SUBREDDITS, KEYWORDS, months=MONTHS_BACK
    )

    # Apply limit
    if args.limit and scraped_data and len(scraped_data) > args.limit:
        print(f"\n Limiting to top {args.limit} posts by engagement", file=log)
        scraped_data = sorted(
            scraped_data,
            key=lambda x: x.get('score', 0) + x.get('num_comments', 0),
            reverse=True
        )[:args.limit]

    # Output results
    if scraped_data:
        if args.json:
            output_json(scraped_data, PROJECT_NAME)
            print_summary(scraped_data, subreddit_stats, KEYWORDS, file=log)
            print(f"\n Output {len(scraped_data)} posts as JSON", file=log)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"{OUTPUT_DIR}/{PROJECT_NAME}_posts_{timestamp}.csv"
            with open(csv_filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(scraped_data[0].keys()))
                writer.writeheader()
                writer.writerows(scraped_data)
            print_summary(scraped_data, subreddit_stats, KEYWORDS)
            print(f"\n Posts saved to: {csv_filename}")
    else:
        print("\n No data was collected.", file=log)
