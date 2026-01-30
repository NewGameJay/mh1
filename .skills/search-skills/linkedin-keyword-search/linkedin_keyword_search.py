"""
LinkedIn Keyword Search - GPai Signal Collection
Customized for Perspective AI keywords
"""

import os
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import requests
import json
import time
import argparse
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Any, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

# Crustdata API credentials - loaded from environment variables
CRUSTDATA_API_KEY = os.environ.get("CRUSTDATA_API_KEY")
CRUSTDATA_API_URL = "https://api.crustdata.com"

# Search Parameters - GPai Keywords
KEYWORD = '"customer research" OR "voice of customer" OR "customer discovery" OR "product research" OR "qualitative research" OR "customer feedback"'
DATE_POSTED = "past-week"  # 7 day lookback
LIMIT = 100
SORT_BY = "relevance"

EXACT_KEYWORD_MATCH = False
CONTENT_TYPES = []
FILTERS = []
FIELDS = ""

MAX_REACTORS = 5
MAX_COMMENTS = 5

PROJECT_NAME = "gpai_signals"
OUTPUT_DIR = "outputs/linkedin-searches"

# ============================================================================
# SCRIPT
# ============================================================================

API_ENDPOINT = f"{CRUSTDATA_API_URL}/screener/linkedin_posts/keyword_search/"

from pathlib import Path
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


def calculate_credit_cost(num_posts: int, exact_match: bool, fields: str) -> int:
    base_cost = 3 if exact_match else 1
    if "reactors" in fields and "comments" in fields:
        multiplier = 10
    elif "reactors" in fields or "comments" in fields:
        multiplier = 5
    else:
        multiplier = 1
    return num_posts * base_cost * multiplier


def build_request_payload() -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "keyword": KEYWORD,
        "limit": LIMIT,
        "date_posted": DATE_POSTED,
        "sort_by": SORT_BY,
    }
    if EXACT_KEYWORD_MATCH:
        payload["exact_keyword_match"] = True
    if CONTENT_TYPES:
        payload["content_type"] = CONTENT_TYPES
    if FILTERS:
        payload["filters"] = FILTERS
    if FIELDS:
        payload["fields"] = FIELDS
        if "reactors" in FIELDS:
            payload["max_reactors"] = MAX_REACTORS
        if "comments" in FIELDS:
            payload["max_comments"] = MAX_COMMENTS
    return payload


def fetch_linkedin_posts(log=None) -> Optional[Dict[str, Any]]:
    if log is None:
        log = sys.stderr

    headers = {
        "Authorization": f"Token {CRUSTDATA_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = build_request_payload()

    print("\n🚀 SENDING API REQUEST...", file=log)
    print(f"Keyword: {KEYWORD[:80]}...", file=log)
    print(f"Date Range: {DATE_POSTED}", file=log)

    max_retries = 3
    backoff_seconds = 2.0

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(API_ENDPOINT, headers=headers, json=payload, timeout=60)

            rate_remaining = response.headers.get("X-RateLimit-Remaining")
            if rate_remaining:
                print(f"📊 Rate Limit Remaining: {rate_remaining}", file=log)

            if response.status_code == 200:
                return response.json()

            elif response.status_code == 429:
                if attempt < max_retries:
                    print(f"⚠️  429 Too Many Requests - Retrying in {backoff_seconds}s...", file=log)
                    time.sleep(backoff_seconds)
                    backoff_seconds *= 2
                    continue
                else:
                    print(f"❌ 429 Too Many Requests - Max retries exceeded", file=log)
                    return None

            elif response.status_code == 404:
                print(f"❌ 404 Not Found - No matching posts", file=log)
                return None

            elif response.status_code == 400:
                print(f"❌ 400 Bad Request", file=log)
                try:
                    print(f"Error: {response.json().get('error')}", file=log)
                except:
                    print(f"Response: {response.text[:500]}", file=log)
                return None

            else:
                print(f"❌ HTTP {response.status_code}", file=log)
                return None

        except requests.exceptions.Timeout:
            if attempt < max_retries:
                print(f"⚠️  Timeout - Retrying in {backoff_seconds}s...", file=log)
                time.sleep(backoff_seconds)
                backoff_seconds *= 2
                continue
            else:
                print(f"❌ Timeout - Max retries exceeded", file=log)
                return None

        except Exception as e:
            print(f"❌ Error: {str(e)}", file=log)
            return None

    return None


def extract_post_data(post: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "post_id": post.get("uid") or post.get("backend_urn", ""),
        "share_url": post.get("share_url", ""),
        "actor_name": post.get("actor_name", ""),
        "actor_type": post.get("actor_type", ""),
        "text": (post.get("text") or "").replace("\n", " ")[:2000],
        "date_posted": post.get("date_posted", ""),
        "total_reactions": post.get("total_reactions", 0),
        "total_comments": post.get("total_comments", 0),
        "num_shares": post.get("num_shares", 0),
        "actor_followers_count": post.get("actor_followers_count", 0),
        "person_title": post.get("person_details", {}).get("title", "") if post.get("actor_type") == "PERSON" else "",
        "person_company": post.get("person_details", {}).get("company_name", "") if post.get("actor_type") == "PERSON" else "",
    }


def output_json(posts: List[Dict[str, Any]], project_name: str):
    output = {
        "platform": "linkedin",
        "project": project_name,
        "collectedAt": datetime.now().isoformat(),
        "count": len(posts),
        "posts": posts
    }
    print(json.dumps(output, ensure_ascii=False, default=str))


def print_summary(posts: List[Dict[str, Any]], log=None):
    if log is None:
        log = sys.stderr

    print("\n" + "=" * 80, file=log)
    print("✨ COLLECTION COMPLETE!", file=log)
    print("=" * 80, file=log)
    print(f"\n📊 Total Posts Retrieved: {len(posts)}", file=log)

    if posts:
        actor_types = defaultdict(int)
        for post in posts:
            actor_types[post["actor_type"]] += 1

        print(f"\n📈 Posts by Actor Type:", file=log)
        for actor_type, count in sorted(actor_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {actor_type:<20} {count:>5} posts", file=log)


def main(json_output: bool = False, output_limit: Optional[int] = None):
    log = sys.stderr if json_output else sys.stdout

    print("🔍 LINKEDIN KEYWORD SEARCH - GPai Signals", file=log)
    print("=" * 80, file=log)
    print(f"Date Range: {DATE_POSTED}", file=log)
    print(f"Max Posts: {LIMIT}", file=log)
    if json_output:
        print(f"Output mode: JSON to stdout", file=log)
    print("=" * 80, file=log)

    result = fetch_linkedin_posts(log=log)

    if not result:
        print("\n❌ Failed to fetch posts", file=log)
        return

    posts_data = []
    if isinstance(result, dict):
        posts = result.get("posts", [])
        print(f"\n✅ API returned {len(posts)} posts", file=log)
    elif isinstance(result, list):
        posts = result
        print(f"\n✅ API returned {len(posts)} posts", file=log)
    else:
        posts = []

    for post in posts:
        post_data = extract_post_data(post)
        posts_data.append(post_data)

    if output_limit and posts_data and len(posts_data) > output_limit:
        print(f"\n📉 Limiting to top {output_limit} posts", file=log)
        posts_data = sorted(
            posts_data,
            key=lambda x: x.get('total_reactions', 0) + x.get('total_comments', 0) * 2,
            reverse=True
        )[:output_limit]

    if posts_data:
        if json_output:
            output_json(posts_data, PROJECT_NAME)
            print_summary(posts_data, log=log)
            print(f"\n✅ Output {len(posts_data)} posts as JSON", file=log)
        else:
            print_summary(posts_data, log=log)
    else:
        print("\n⚠️  No posts were collected.", file=log)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LinkedIn Keyword Search - GPai Signals')
    parser.add_argument('--json', action='store_true', help='Output JSON to stdout')
    parser.add_argument('--limit', type=int, default=None, help='Max posts to output')
    args = parser.parse_args()

    main(json_output=args.json, output_limit=args.limit)
