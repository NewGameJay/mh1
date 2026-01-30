"""
Get LinkedIn Post Reactors - Crustdata API

Fetches reactors and commenters for LinkedIn posts using the Crustdata API.
Returns enriched profile information for each reactor.

Usage:
    python tools/get-post-reactors.py --urls "https://linkedin.com/posts/..." "https://linkedin.com/posts/..."
    python tools/get-post-reactors.py --urls-file /path/to/urls.txt
    python tools/get-post-reactors.py --json

Output (JSON):
    {
        "success": true,
        "posts": [
            {
                "post_url": "...",
                "reactors": [...],
                "commenters": [...]
            }
        ],
        "total_reactors": N,
        "total_commenters": N
    }
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
from typing import List, Dict, Any, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

# Crustdata API credentials - loaded from environment variables
CRUSTDATA_API_KEY = os.environ.get("CRUSTDATA_API_KEY")
CRUSTDATA_API_URL = "https://api.crustdata.com"

# Default limits
DEFAULT_MAX_REACTORS = 50
DEFAULT_MAX_COMMENTS = 25

# ============================================================================
# API FUNCTIONS
# ============================================================================


def get_post_engagement(
    post_url: str,
    max_reactors: int = DEFAULT_MAX_REACTORS,
    max_comments: int = DEFAULT_MAX_COMMENTS,
    log=None
) -> Optional[Dict[str, Any]]:
    """
    Fetch reactors and commenters for a LinkedIn post.
    
    Uses Crustdata's LinkedIn post engagement endpoint.
    """
    if log is None:
        log = sys.stderr
    
    if not CRUSTDATA_API_KEY:
        print("❌ CRUSTDATA_API_KEY not found in environment", file=log)
        return None
    
    headers = {
        "Authorization": f"Token {CRUSTDATA_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Use the post details endpoint with engagement data
    endpoint = f"{CRUSTDATA_API_URL}/screener/linkedin_posts/details/"
    
    payload = {
        "post_url": post_url,
        "fields": "reactors,comments",
        "max_reactors": max_reactors,
        "max_comments": max_comments
    }
    
    print(f"🔍 Fetching engagement for: {post_url[:60]}...", file=log)
    
    max_retries = 3
    backoff_seconds = 2.0
    
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
            
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
                print(f"❌ 404 Not Found - Post not found or private", file=log)
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


def extract_reactor_data(reactor: Dict[str, Any]) -> Dict[str, Any]:
    """Extract relevant fields from a reactor object."""
    return {
        "linkedin_url": reactor.get("linkedin_url") or reactor.get("profile_url", ""),
        "name": reactor.get("name") or reactor.get("full_name", ""),
        "headline": reactor.get("headline", ""),
        "title": reactor.get("title", ""),
        "company": reactor.get("company_name") or reactor.get("current_company", ""),
        "location": reactor.get("location", ""),
        "reaction_type": reactor.get("reaction_type", "LIKE"),
        "follower_count": reactor.get("follower_count", 0),
        "connection_degree": reactor.get("connection_degree", ""),
    }


def extract_commenter_data(comment: Dict[str, Any]) -> Dict[str, Any]:
    """Extract relevant fields from a comment object."""
    author = comment.get("author", {})
    return {
        "linkedin_url": author.get("linkedin_url") or author.get("profile_url", ""),
        "name": author.get("name") or author.get("full_name", ""),
        "headline": author.get("headline", ""),
        "title": author.get("title", ""),
        "company": author.get("company_name") or author.get("current_company", ""),
        "comment_text": comment.get("text", "")[:500],
        "comment_date": comment.get("posted_date", ""),
        "likes": comment.get("num_likes", 0),
    }


def process_post_engagement(result: Dict[str, Any], post_url: str) -> Dict[str, Any]:
    """Process API response and extract reactor/commenter data."""
    
    # Handle different response formats
    post_data = result.get("post") or result
    
    reactors_raw = post_data.get("reactors", []) or []
    comments_raw = post_data.get("comments", []) or []
    
    reactors = [extract_reactor_data(r) for r in reactors_raw]
    commenters = [extract_commenter_data(c) for c in comments_raw]
    
    return {
        "post_url": post_url,
        "post_id": post_data.get("uid") or post_data.get("backend_urn", ""),
        "total_reactions": post_data.get("total_reactions", len(reactors)),
        "total_comments": post_data.get("total_comments", len(commenters)),
        "reactors": reactors,
        "commenters": commenters,
        "fetched_at": datetime.now().isoformat()
    }


# ============================================================================
# MAIN
# ============================================================================


def load_urls_from_file(filepath: str) -> List[str]:
    """Load URLs from a text file (one per line)."""
    urls = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                urls.append(line)
    return urls


def main(
    urls: List[str],
    max_reactors: int = DEFAULT_MAX_REACTORS,
    max_comments: int = DEFAULT_MAX_COMMENTS,
    json_output: bool = False
):
    log = sys.stderr if json_output else sys.stdout
    
    print("🔍 GET POST REACTORS - Crustdata API", file=log)
    print("=" * 60, file=log)
    print(f"Posts to process: {len(urls)}", file=log)
    print(f"Max reactors per post: {max_reactors}", file=log)
    print(f"Max comments per post: {max_comments}", file=log)
    print("=" * 60, file=log)
    
    if not CRUSTDATA_API_KEY:
        error = {
            "success": False,
            "error": "CRUSTDATA_API_KEY not found in environment"
        }
        if json_output:
            print(json.dumps(error, ensure_ascii=False))
        else:
            print(f"\n❌ {error['error']}", file=log)
        return
    
    results = []
    total_reactors = 0
    total_commenters = 0
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing post...", file=log)
        
        result = get_post_engagement(
            post_url=url,
            max_reactors=max_reactors,
            max_comments=max_comments,
            log=log
        )
        
        if result:
            processed = process_post_engagement(result, url)
            results.append(processed)
            total_reactors += len(processed["reactors"])
            total_commenters += len(processed["commenters"])
            print(f"  ✅ Found {len(processed['reactors'])} reactors, {len(processed['commenters'])} commenters", file=log)
        else:
            results.append({
                "post_url": url,
                "error": "Failed to fetch engagement data",
                "reactors": [],
                "commenters": []
            })
            print(f"  ❌ Failed to fetch engagement", file=log)
        
        # Rate limiting delay between requests
        if i < len(urls):
            time.sleep(1)
    
    # Output results
    output = {
        "success": True,
        "posts": results,
        "total_posts": len(urls),
        "total_reactors": total_reactors,
        "total_commenters": total_commenters,
        "collected_at": datetime.now().isoformat()
    }
    
    if json_output:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print("\n" + "=" * 60, file=log)
        print("✨ COLLECTION COMPLETE!", file=log)
        print("=" * 60, file=log)
        print(f"\n📊 Summary:", file=log)
        print(f"  Posts processed: {len(urls)}", file=log)
        print(f"  Total reactors: {total_reactors}", file=log)
        print(f"  Total commenters: {total_commenters}", file=log)
        
        # Print top reactors by follower count
        all_reactors = []
        for r in results:
            for reactor in r.get("reactors", []):
                reactor["source_post"] = r.get("post_url", "")
                all_reactors.append(reactor)
        
        if all_reactors:
            all_reactors.sort(key=lambda x: x.get("follower_count", 0), reverse=True)
            print(f"\n📈 Top Reactors by Followers:", file=log)
            for reactor in all_reactors[:10]:
                print(f"  - {reactor['name']}: {reactor.get('follower_count', 0):,} followers ({reactor.get('title', 'N/A')})", file=log)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get LinkedIn Post Reactors - Crustdata API')
    parser.add_argument('--urls', nargs='+', help='LinkedIn post URLs to analyze')
    parser.add_argument('--urls-file', type=str, help='Path to file containing URLs (one per line)')
    parser.add_argument('--max-reactors', type=int, default=DEFAULT_MAX_REACTORS, help=f'Max reactors to fetch per post (default: {DEFAULT_MAX_REACTORS})')
    parser.add_argument('--max-comments', type=int, default=DEFAULT_MAX_COMMENTS, help=f'Max comments to fetch per post (default: {DEFAULT_MAX_COMMENTS})')
    parser.add_argument('--json', action='store_true', help='Output JSON to stdout')
    
    args = parser.parse_args()
    
    # Collect URLs
    urls = []
    if args.urls:
        urls.extend(args.urls)
    if args.urls_file:
        urls.extend(load_urls_from_file(args.urls_file))
    
    if not urls:
        print(json.dumps({
            "success": False,
            "error": "No URLs provided. Use --urls or --urls-file"
        }))
        sys.exit(1)
    
    main(
        urls=urls,
        max_reactors=args.max_reactors,
        max_comments=args.max_comments,
        json_output=args.json
    )
