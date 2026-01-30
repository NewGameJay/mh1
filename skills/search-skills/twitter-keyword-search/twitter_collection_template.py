"""
X (Twitter) Keyword Search Collection Template

This template collects tweets based on keywords, hashtags, and filters using X API v2.
Uses tweepy library with Bearer Token authentication for Basic tier access.
Client ID is read from inputs/active_client.md at runtime.

Customize the configuration section for your specific use case.

Usage:
    python twitter_collection_template.py                   # Output CSV files (default)
    python twitter_collection_template.py --json            # Output JSON to stdout
    python twitter_collection_template.py --json --limit 50 # Output JSON, limit to top 50 by engagement
"""

import sys
import io

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import csv
import json
import time
import argparse
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    import tweepy
except ImportError:
    print("Installing tweepy...", file=sys.stderr)
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tweepy", "-q"])
    import tweepy

# ============================================================================
# CLIENT CONFIGURATION - Read from inputs/active_client.md
# ============================================================================

def get_client_config():
    """Read client configuration from inputs/active_client.md."""
    # Find project root (where inputs/ directory is)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent  # skills/twitter-keyword-search -> mh1-hq
    
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

# X API Credentials (MH1 account)
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAABUA5gEAAAAA4SkiE7tcZurJ9GvGJ%2F5Q4Ssl3f4%3D9Wn2IQbZZQ86IXcLyNZiA9O7vEBmKxIwlMu81FhEpeTZW9NmEq"

# Alternative: OAuth 1.0a (for user-context operations)
API_KEY = "guSdPaNJiwjNULe9O1L3Uee38"
API_KEY_SECRET = "YviUl45GeXNq0HMvj64XqnC9SscmH9qU119R6bgDshh71STJoL"
ACCESS_TOKEN = "487105286-OOXog2zf4g19FcKO1imVtmVicJhHRh9lJpN7mAzG"
ACCESS_TOKEN_SECRET = "HRtzXTJlVJx0Y7hLF92eHIFEuemNi6bCudWoTPuvOoYiW"

# ============================================================================
# SEARCH PARAMETERS
# ============================================================================

# Search Query (supports Boolean operators, hashtags, user filters)
SEARCH_QUERY = "(female founder OR women entrepreneur) -spam lang:en"

# Time Range (1-7 days for Basic tier)
DAYS_BACK = 7

# Maximum Tweets to Collect
MAX_TWEETS = 100

# ============================================================================
# FILTERS
# ============================================================================

MIN_LIKES = 0
MIN_RETWEETS = 0
MIN_REPLIES = 0

EXCLUSION_PATTERNS = [
    "crypto giveaway",
    "free airdrop",
    "NFT mint",
    "click here",
    "limited time offer",
]

EXCLUDE_PURE_RETWEETS = False

# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================

PROJECT_NAME = f"{CLIENT_NAME.lower().replace(' ', '_')}_twitter_search"

# Get project root for output
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
OUTPUT_DIR = str(PROJECT_ROOT / "clients" / CLIENT_ID / "social-listening" / "collection-data") if CLIENT_ID else "output"

# ============================================================================
# TWEET FIELDS
# ============================================================================

TWEET_FIELDS = [
    'id', 'text', 'created_at', 'author_id',
    'conversation_id', 'in_reply_to_user_id',
    'public_metrics', 'entities', 'context_annotations',
    'lang', 'possibly_sensitive', 'reply_settings',
    'referenced_tweets', 'source',
]

USER_FIELDS = [
    'id', 'name', 'username', 'created_at',
    'description', 'location', 'verified',
    'public_metrics', 'profile_image_url', 'url'
]

MEDIA_FIELDS = ['type', 'url', 'preview_image_url', 'alt_text']

EXPANSIONS = [
    'author_id',
    'referenced_tweets.id',
    'referenced_tweets.id.author_id',
    'entities.mentions.username',
    'attachments.media_keys'
]

# ============================================================================
# RATE LIMITING
# ============================================================================

MONTHLY_QUOTA = 10000
MONTHLY_USAGE_FILE = f"{OUTPUT_DIR}/twitter_monthly_usage.json"

# ============================================================================
# SCRIPT
# ============================================================================

Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


def get_twitter_client() -> tweepy.Client:
    """Initialize Twitter API client."""
    return tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=API_KEY,
        consumer_secret=API_KEY_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True
    )


def load_monthly_usage() -> Dict[str, Any]:
    """Load monthly quota usage from file."""
    try:
        usage_file = Path(MONTHLY_USAGE_FILE)
        if usage_file.exists():
            with open(usage_file, 'r') as f:
                data = json.load(f)
                last_reset = datetime.fromisoformat(data.get('last_reset', '2000-01-01'))
                now = datetime.now()
                if last_reset.year == now.year and last_reset.month == now.month:
                    return data
    except:
        pass

    return {
        'tweets_collected': 0,
        'last_reset': datetime.now().isoformat(),
        'monthly_quota': MONTHLY_QUOTA
    }


def save_monthly_usage(usage_data: Dict[str, Any]):
    """Save monthly quota usage to file."""
    with open(MONTHLY_USAGE_FILE, 'w') as f:
        json.dump(usage_data, f, indent=2)


def update_monthly_usage(tweets_collected: int):
    """Update monthly quota usage."""
    usage = load_monthly_usage()
    usage['tweets_collected'] += tweets_collected
    save_monthly_usage(usage)


def build_search_query() -> str:
    """Build search query with filters."""
    query = SEARCH_QUERY

    if MIN_LIKES > 0:
        query += f" min_faves:{MIN_LIKES}"
    if MIN_RETWEETS > 0:
        query += f" min_retweets:{MIN_RETWEETS}"
    if MIN_REPLIES > 0:
        query += f" min_replies:{MIN_REPLIES}"
    if EXCLUDE_PURE_RETWEETS:
        query += " -is:retweet"

    return query


def search_tweets(client: tweepy.Client, query: str, start_time: datetime, max_results: int = 100, log=None) -> List[Dict[str, Any]]:
    """Search for tweets using X API v2."""
    if log is None:
        log = sys.stderr

    print(f"\n Searching X for: {query}", file=log)
    print(f" Time range: {start_time.strftime('%Y-%m-%d')} to now", file=log)

    all_tweets = []
    users_lookup = {}

    try:
        for page, response in enumerate(tweepy.Paginator(
            client.search_recent_tweets,
            query=query,
            start_time=start_time,
            tweet_fields=TWEET_FIELDS,
            user_fields=USER_FIELDS,
            media_fields=MEDIA_FIELDS,
            expansions=EXPANSIONS,
            max_results=min(100, max_results)
        ).flatten(limit=max_results)):

            if hasattr(response, 'includes') and 'users' in response.includes:
                for user in response.includes['users']:
                    users_lookup[user.id] = user

            all_tweets.append(response)

            if len(all_tweets) % 50 == 0:
                print(f"   Collected {len(all_tweets)} tweets...", file=log)

        print(f" Found {len(all_tweets)} tweets", file=log)

    except tweepy.TooManyRequests as e:
        print(f" Rate limit reached: {e}", file=log)
    except Exception as e:
        print(f" Error during search: {e}", file=log)

    return all_tweets, users_lookup


def filter_tweets(tweets: List[Any], exclusion_patterns: List[str], log=None) -> List[Any]:
    """Apply post-collection filtering."""
    if log is None:
        log = sys.stderr

    if not exclusion_patterns:
        return tweets

    filtered = []
    for tweet in tweets:
        text_to_check = tweet.text.lower()
        if not any(pattern.lower() in text_to_check for pattern in exclusion_patterns):
            filtered.append(tweet)

    excluded_count = len(tweets) - len(filtered)
    if excluded_count > 0:
        print(f" Filtered out {excluded_count} tweets", file=log)

    return filtered


def extract_tweet_data(tweet: Any, users_lookup: Dict[int, Any]) -> Dict[str, Any]:
    """Extract relevant fields from a tweet object."""
    author = users_lookup.get(tweet.author_id, {})
    metrics = tweet.public_metrics if hasattr(tweet, 'public_metrics') else {}

    tweet_type = 'original'
    if hasattr(tweet, 'referenced_tweets') and tweet.referenced_tweets:
        ref_types = [ref.type for ref in tweet.referenced_tweets]
        if 'replied_to' in ref_types:
            tweet_type = 'reply'
        elif 'quoted' in ref_types:
            tweet_type = 'quote'
        elif 'retweeted' in ref_types:
            tweet_type = 'retweet'

    return {
        'tweet_id': tweet.id,
        'created_at': tweet.created_at.isoformat() if hasattr(tweet, 'created_at') else '',
        'text': tweet.text,
        'author_id': tweet.author_id if hasattr(tweet, 'author_id') else '',
        'author_username': author.username if hasattr(author, 'username') else '',
        'author_name': author.name if hasattr(author, 'name') else '',
        'author_verified': author.verified if hasattr(author, 'verified') else False,
        'author_followers': author.public_metrics.get('followers_count', 0) if hasattr(author, 'public_metrics') else 0,
        'tweet_type': tweet_type,
        'lang': tweet.lang if hasattr(tweet, 'lang') else '',
        'likes': metrics.get('like_count', 0),
        'retweets': metrics.get('retweet_count', 0),
        'replies': metrics.get('reply_count', 0),
        'quotes': metrics.get('quote_count', 0),
        'tweet_url': f"https://twitter.com/{author.username if hasattr(author, 'username') else 'i'}/status/{tweet.id}"
    }


def output_json(tweets_data: List[Dict[str, Any]], project_name: str):
    """Output tweets as JSON to stdout."""
    output = {
        "platform": "twitter",
        "project": project_name,
        "clientId": CLIENT_ID,
        "clientName": CLIENT_NAME,
        "collectedAt": datetime.now().isoformat(),
        "count": len(tweets_data),
        "posts": tweets_data
    }
    print(json.dumps(output, ensure_ascii=False, default=str))


def main(json_output: bool = False, output_limit: Optional[int] = None):
    """Main execution function."""
    log = sys.stderr if json_output else sys.stdout

    print(" X (TWITTER) KEYWORD SEARCH", file=log)
    print(f"Client: {CLIENT_NAME} ({CLIENT_ID})", file=log)
    print(f"Project: {PROJECT_NAME}", file=log)
    print(f"Query: {SEARCH_QUERY}", file=log)
    print(f"Days back: {DAYS_BACK}", file=log)
    if json_output:
        print(f"Output mode: JSON to stdout", file=log)
    if output_limit:
        print(f"Limit: {output_limit} tweets", file=log)

    # Check monthly quota
    usage = load_monthly_usage()
    current = usage['tweets_collected']
    print(f"\n Monthly Quota: {current:,}/{MONTHLY_QUOTA:,} tweets used", file=log)

    if current >= MONTHLY_QUOTA:
        print(f" MONTHLY QUOTA EXCEEDED!", file=log)
        return

    # Initialize client
    print("\n Authenticating with X API...", file=log)
    client = get_twitter_client()
    print(" Authentication successful", file=log)

    # Build query and search
    query = build_search_query()
    start_time = datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)

    tweets, users_lookup = search_tweets(client, query, start_time, MAX_TWEETS, log=log)

    if not tweets:
        print("\n No tweets were collected.", file=log)
        return

    # Filter and extract data
    tweets = filter_tweets(tweets, EXCLUSION_PATTERNS, log=log)

    print("\n Processing tweet data...", file=log)
    tweets_data = [extract_tweet_data(tweet, users_lookup) for tweet in tweets]

    # Apply limit
    if output_limit and tweets_data and len(tweets_data) > output_limit:
        print(f"\n Limiting to top {output_limit} tweets by engagement", file=log)
        tweets_data = sorted(
            tweets_data,
            key=lambda x: x.get('likes', 0) + x.get('retweets', 0) * 2,
            reverse=True
        )[:output_limit]

    # Update monthly usage
    update_monthly_usage(len(tweets_data))

    # Output results
    if tweets_data:
        if json_output:
            output_json(tweets_data, PROJECT_NAME)
            print(f"\n Output {len(tweets_data)} tweets as JSON", file=log)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"{OUTPUT_DIR}/{PROJECT_NAME}_tweets_{timestamp}.csv"
            with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=list(tweets_data[0].keys()))
                writer.writeheader()
                writer.writerows(tweets_data)
            print(f"\n Tweets saved to: {csv_filename}")
    else:
        print("\n No tweets were collected.", file=log)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='X (Twitter) Keyword Search')
    parser.add_argument('--json', action='store_true', help='Output JSON to stdout')
    parser.add_argument('--limit', type=int, default=None, help='Max tweets to output')
    args = parser.parse_args()

    main(json_output=args.json, output_limit=args.limit)
