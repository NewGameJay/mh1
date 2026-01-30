"""
LinkedIn Keyword Search Collection Template

This template collects LinkedIn posts based on keywords with advanced filtering.
Uses Crustdata API with credit-based pricing.

Customize the configuration section for your specific use case.
Client ID is read from inputs/active_client.md at runtime.

Usage:
    python linkedin_collection_template.py                    # Output CSV files (default)
    python linkedin_collection_template.py --json             # Output JSON to stdout
    python linkedin_collection_template.py --json --limit 100 # Output JSON, limit to top 100 by engagement
"""

import sys
import io
import os

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import requests
import json
import csv
import time
import argparse
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Any, Optional
from pathlib import Path

# ============================================================================
# CLIENT CONFIGURATION - Read from inputs/active_client.md
# ============================================================================

def get_client_config():
    """Read client configuration from inputs/active_client.md."""
    # Find project root (where inputs/ directory is)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent  # skills/linkedin-keyword-search -> mh1-hq
    
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

# Crustdata API Credentials (MH1 account)
CRUSTDATA_API_KEY = "5b1620e40837c463bd2ceaa412f63f81a18d4ce8"
CRUSTDATA_API_URL = "https://api.crustdata.com"

# Search Parameters
KEYWORD = "female founder"  # Supports Boolean: "female founder" OR "women entrepreneur"
DATE_POSTED = "past-month"  # Options: past-24h, past-week, past-month, past-quarter, past-year
LIMIT = 100  # Max posts to retrieve (max 500)
SORT_BY = "relevance"  # Options: relevance, date_posted

# Exact Keyword Match (Costs 3 credits per post instead of 1)
EXACT_KEYWORD_MATCH = False  # Set to True for exact phrase matching

# Content Type Filters (optional)
CONTENT_TYPES = []  # Options: photos, videos, documents, jobs, collaborativeArticles, liveVideos

# ============================================================================
# FILTERS - Configure filters (all use AND logic)
# ============================================================================

FILTERS = []

# Example filters (uncomment and customize as needed):

# Filter 1: MEMBER - Posts by specific people
# FILTERS.append({
#     "filter_type": "MEMBER",
#     "type": "in",
#     "value": [
#         "https://www.linkedin.com/in/raaja-nemani",
#     ]
# })

# ============================================================================
# ENGAGEMENT DATA (COSTS EXTRA CREDITS)
# ============================================================================

# Options: "", "reactors", "comments", "reactors,comments"
# Cost: reactors=5 credits/post, comments=5 credits/post, both=10 credits/post
FIELDS = ""  # Leave empty for no engagement data

MAX_REACTORS = 5   # If fetching reactors (range: 0-5000)
MAX_COMMENTS = 5   # If fetching comments (range: 0-5000)

# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================

PROJECT_NAME = f"{CLIENT_NAME.lower().replace(' ', '_')}_linkedin_search"

# Get project root for output
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
OUTPUT_DIR = str(PROJECT_ROOT / "clients" / CLIENT_ID / "social-listening" / "collection-data") if CLIENT_ID else "output"

# ============================================================================
# SCRIPT - Usually no need to modify below this line
# ============================================================================

API_ENDPOINT = f"{CRUSTDATA_API_URL}/screener/linkedin_posts/keyword_search/"

# Ensure output directory exists
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# Incompatible filter combinations (for validation)
INCOMPATIBLE_FILTERS = [
    ("AUTHOR_COMPANY", "COMPANY"),
    ("MEMBER", "COMPANY"),
    ("AUTHOR_INDUSTRY", "COMPANY"),
    ("AUTHOR_TITLE", "COMPANY"),
]


def validate_filters(filters: List[Dict[str, Any]], log=None) -> bool:
    """Validate that no incompatible filter combinations are present."""
    if log is None:
        log = sys.stderr

    filter_types = {f["filter_type"] for f in filters}

    for type1, type2 in INCOMPATIBLE_FILTERS:
        if type1 in filter_types and type2 in filter_types:
            print(f"\n FILTER ERROR: Cannot combine {type1} and {type2}", file=log)
            return False

    return True


def calculate_credit_cost(num_posts: int, exact_match: bool, fields: str) -> int:
    """Calculate estimated credit cost for the search."""
    base_cost = 3 if exact_match else 1

    if "reactors" in fields and "comments" in fields:
        multiplier = 10
    elif "reactors" in fields or "comments" in fields:
        multiplier = 5
    else:
        multiplier = 1

    return num_posts * base_cost * multiplier


def build_request_payload() -> Dict[str, Any]:
    """Build the API request payload from configuration."""
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
    """Fetch LinkedIn posts from Crustdata API with retry logic."""
    if log is None:
        log = sys.stderr

    headers = {
        "Authorization": f"Token {CRUSTDATA_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = build_request_payload()

    print("\n SENDING API REQUEST...", file=log)
    print(f"Endpoint: {API_ENDPOINT}", file=log)
    print(f"Payload: {json.dumps(payload, indent=2)}", file=log)

    max_retries = 3
    backoff_seconds = 2.0

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(API_ENDPOINT, headers=headers, json=payload, timeout=60)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                if attempt < max_retries:
                    print(f"\n 429 Too Many Requests - Retrying in {backoff_seconds}s...", file=log)
                    time.sleep(backoff_seconds)
                    backoff_seconds *= 2
                    continue
                else:
                    print(f"\n 429 Too Many Requests - Max retries exceeded", file=log)
                    return None
            else:
                print(f"\n HTTP {response.status_code}", file=log)
                print(f"Response: {response.text[:500]}", file=log)
                return None

        except requests.exceptions.Timeout:
            if attempt < max_retries:
                print(f"\n Request timeout - Retrying in {backoff_seconds}s...", file=log)
                time.sleep(backoff_seconds)
                backoff_seconds *= 2
                continue
            else:
                return None

        except Exception as e:
            print(f"\n Error: {str(e)}", file=log)
            return None

    return None


def extract_post_data(post: Dict[str, Any]) -> Dict[str, Any]:
    """Extract relevant fields from a post."""
    return {
        "post_id": post.get("uid") or post.get("backend_urn", ""),
        "share_url": post.get("share_url", ""),
        "actor_name": post.get("actor_name", ""),
        "actor_type": post.get("actor_type", ""),
        "text": (post.get("text") or "").replace("\n", " ")[:1000],
        "date_posted": post.get("date_posted", ""),
        "total_reactions": post.get("total_reactions", 0),
        "total_comments": post.get("total_comments", 0),
        "num_shares": post.get("num_shares", 0),
        "actor_followers_count": post.get("actor_followers_count", 0),
        "is_sponsored": post.get("is_sponsored", False),
        "person_title": post.get("person_details", {}).get("title", "") if post.get("actor_type") == "PERSON" else "",
        "person_company": post.get("person_details", {}).get("company_name", "") if post.get("actor_type") == "PERSON" else "",
        "person_location": post.get("person_details", {}).get("location", "") if post.get("actor_type") == "PERSON" else "",
        "company_name": post.get("company_details", {}).get("name", "") if post.get("actor_type") == "ORGANIZATION" else "",
        "company_industry": post.get("company_details", {}).get("industry", "") if post.get("actor_type") == "ORGANIZATION" else "",
        "company_size": post.get("company_details", {}).get("company_size", "") if post.get("actor_type") == "ORGANIZATION" else "",
        "num_reactors": len(post.get("reactors", [])),
        "num_comments_collected": len(post.get("comments", [])),
    }


def output_json(posts: List[Dict[str, Any]], project_name: str):
    """Output posts as JSON to stdout for piping to upload script."""
    output = {
        "platform": "linkedin",
        "project": project_name,
        "clientId": CLIENT_ID,
        "clientName": CLIENT_NAME,
        "collectedAt": datetime.now().isoformat(),
        "count": len(posts),
        "posts": posts
    }
    print(json.dumps(output, ensure_ascii=False, default=str))


def main(json_output: bool = False, output_limit: Optional[int] = None):
    """Main execution function."""
    log = sys.stderr if json_output else sys.stdout

    print(" LINKEDIN KEYWORD SEARCH", file=log)
    print(f"\n Client: {CLIENT_NAME} ({CLIENT_ID})", file=log)
    print(f" Configuration:", file=log)
    print(f"   Keyword: {KEYWORD}", file=log)
    print(f"   Date Range: {DATE_POSTED}", file=log)
    print(f"   Max Posts: {LIMIT}", file=log)
    if json_output:
        print(f"   Output mode: JSON to stdout", file=log)
    if output_limit:
        print(f"   Limit: {output_limit} posts (by engagement)", file=log)

    # Validate filters
    if FILTERS and not validate_filters(FILTERS, log=log):
        return

    # Fetch posts
    result = fetch_linkedin_posts(log=log)

    if not result:
        print("\n Failed to fetch posts", file=log)
        return

    # Extract posts
    posts_data = []
    if isinstance(result, dict):
        posts = result.get("posts", [])
        print(f"\n API returned {len(posts)} posts", file=log)
    elif isinstance(result, list):
        posts = result
        print(f"\n API returned {len(posts)} posts", file=log)
    else:
        posts = []

    # Process posts
    for post in posts:
        post_data = extract_post_data(post)
        posts_data.append(post_data)

    # Apply limit if specified (sort by engagement first)
    if output_limit and posts_data and len(posts_data) > output_limit:
        print(f"\n Limiting to top {output_limit} posts by engagement", file=log)
        posts_data = sorted(
            posts_data,
            key=lambda x: x.get('total_reactions', 0) + x.get('total_comments', 0) * 2,
            reverse=True
        )[:output_limit]

    # Output results
    if posts_data:
        if json_output:
            output_json(posts_data, PROJECT_NAME)
            print(f"\n Output {len(posts_data)} posts as JSON", file=log)
        else:
            # Save to CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"{OUTPUT_DIR}/{PROJECT_NAME}_posts_{timestamp}.csv"
            with open(csv_filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(posts_data[0].keys()))
                writer.writeheader()
                writer.writerows(posts_data)
            print(f"\n Posts saved to: {csv_filename}")
    else:
        print("\n No posts were collected.", file=log)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LinkedIn Keyword Search')
    parser.add_argument('--json', action='store_true', help='Output JSON to stdout')
    parser.add_argument('--limit', type=int, default=None, help='Max posts to output')
    args = parser.parse_args()

    main(json_output=args.json, output_limit=args.limit)
