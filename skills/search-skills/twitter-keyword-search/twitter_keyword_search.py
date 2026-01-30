"""
X (Twitter) Keyword Search - GPai Signal Collection
Customized for Perspective AI keywords
"""

import os
import sys
import io

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import tweepy
import csv
import json
import time
import argparse
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import List, Dict, Any, Optional
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

# X API Credentials - loaded from environment variables
BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN")
API_KEY = os.environ.get("TWITTER_API_KEY")
API_KEY_SECRET = os.environ.get("TWITTER_API_KEY_SECRET")
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

# ============================================================================
# SEARCH PARAMETERS - GPai Keywords
# ============================================================================

# Keywords for customer research, AI interviews, voice of customer
SEARCH_QUERY = '("AI customer research" OR "customer interviews at scale" OR "survey fatigue" OR "voice of customer" OR "product-market fit" OR "UX research" OR "qualitative research" OR "customer feedback") -spam -crypto lang:en'

DAYS_BACK = 7
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

EXCLUDE_PURE_RETWEETS = True

# ============================================================================
# RATE LIMITING
# ============================================================================

REQUESTS_PER_WINDOW = 450
REQUEST_WINDOW_MINUTES = 15
SAFETY_BUFFER = 50

MONTHLY_QUOTA = 10000
MONTHLY_USAGE_FILE = "twitter_monthly_usage.json"

QUOTA_WARNING_AT = 0.80
QUOTA_ALERT_AT = 0.90

# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================

PROJECT_NAME = "gpai_signals"
OUTPUT_DIR = "outputs/twitter-searches"

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
# SCRIPT
# ============================================================================

Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

request_count = 0
window_start = datetime.now()


def get_twitter_client() -> tweepy.Client:
    client = tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=API_KEY,
        consumer_secret=API_KEY_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True
    )
    return client


def load_monthly_usage() -> Dict[str, Any]:
    if Path(MONTHLY_USAGE_FILE).exists():
        with open(MONTHLY_USAGE_FILE, 'r') as f:
            data = json.load(f)
            last_reset = datetime.fromisoformat(data.get('last_reset', '2000-01-01'))
            now = datetime.now()
            if last_reset.year == now.year and last_reset.month == now.month:
                return data
    return {
        'tweets_collected': 0,
        'last_reset': datetime.now().isoformat(),
        'monthly_quota': MONTHLY_QUOTA
    }


def save_monthly_usage(usage_data: Dict[str, Any]):
    with open(MONTHLY_USAGE_FILE, 'w') as f:
        json.dump(usage_data, f, indent=2)


def update_monthly_usage(tweets_collected: int):
    usage = load_monthly_usage()
    usage['tweets_collected'] += tweets_collected
    save_monthly_usage(usage)


def check_rate_limit(log=None):
    if log is None:
        log = sys.stderr

    global request_count, window_start

    request_count += 1
    elapsed = (datetime.now() - window_start).total_seconds() / 60

    if request_count % 10 == 0:
        print(f"   Rate limit: {request_count}/{REQUESTS_PER_WINDOW} requests used in {elapsed:.1f} min", file=log)

    if elapsed >= REQUEST_WINDOW_MINUTES:
        request_count = 0
        window_start = datetime.now()

    if request_count >= (REQUESTS_PER_WINDOW - SAFETY_BUFFER):
        sleep_time = (REQUEST_WINDOW_MINUTES * 60) - (elapsed * 60)
        if sleep_time > 0:
            print(f"⏳ Rate limit approaching, sleeping {sleep_time/60:.1f} minutes...", file=log)
            time.sleep(sleep_time)
            request_count = 0
            window_start = datetime.now()


def build_search_query() -> str:
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
    if log is None:
        log = sys.stderr

    print(f"\n🔍 Searching X for: {query[:100]}...", file=log)
    print(f"📅 Time range: {start_time.strftime('%Y-%m-%d')} to now", file=log)
    print(f"🎯 Max results: {max_results}", file=log)

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

            check_rate_limit(log=log)

            if hasattr(response, 'includes') and 'users' in response.includes:
                for user in response.includes['users']:
                    users_lookup[user.id] = user

            all_tweets.append(response)

            if len(all_tweets) % 50 == 0:
                print(f"   Collected {len(all_tweets)} tweets...", file=log)

        print(f"✅ Found {len(all_tweets)} tweets", file=log)

    except tweepy.TooManyRequests as e:
        print(f"⚠️  Rate limit reached: {e}", file=log)
        print(f"   Collected {len(all_tweets)} tweets before limit", file=log)
    except tweepy.Forbidden as e:
        print(f"❌ API access forbidden: {e}", file=log)
    except Exception as e:
        print(f"❌ Error during search: {e}", file=log)

    return all_tweets, users_lookup


def filter_tweets(tweets: List[Any], exclusion_patterns: List[str], log=None) -> List[Any]:
    if log is None:
        log = sys.stderr

    if not exclusion_patterns:
        return tweets

    filtered = []
    excluded_count = 0

    for tweet in tweets:
        text_to_check = tweet.text.lower()
        if any(pattern.lower() in text_to_check for pattern in exclusion_patterns):
            excluded_count += 1
            continue
        filtered.append(tweet)

    if excluded_count > 0:
        print(f"🔍 Filtered out {excluded_count} tweets matching exclusion patterns", file=log)

    return filtered


def extract_tweet_data(tweet: Any, users_lookup: Dict[int, Any]) -> Dict[str, Any]:
    author = users_lookup.get(tweet.author_id, {})
    metrics = tweet.public_metrics if hasattr(tweet, 'public_metrics') and tweet.public_metrics else {}
    entities = tweet.entities if hasattr(tweet, 'entities') and tweet.entities else {}
    hashtags = [tag['tag'] for tag in entities.get('hashtags', [])] if entities else []
    mentions = [mention['username'] for mention in entities.get('mentions', [])] if entities else []
    urls = [url['expanded_url'] for url in entities.get('urls', [])] if entities else []

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
        'conversation_id': tweet.conversation_id if hasattr(tweet, 'conversation_id') else '',
        'tweet_type': tweet_type,
        'lang': tweet.lang if hasattr(tweet, 'lang') else '',
        'likes': metrics.get('like_count', 0),
        'retweets': metrics.get('retweet_count', 0),
        'replies': metrics.get('reply_count', 0),
        'quotes': metrics.get('quote_count', 0),
        'impressions': metrics.get('impression_count', 0),
        'hashtags': ', '.join(hashtags[:5]),
        'mentions': ', '.join(mentions[:5]),
        'urls': urls[0] if urls else '',
        'tweet_url': f"https://twitter.com/{author.username if hasattr(author, 'username') else 'i'}/status/{tweet.id}"
    }


def output_json(tweets_data: List[Dict[str, Any]], project_name: str):
    output = {
        "platform": "twitter",
        "project": project_name,
        "collectedAt": datetime.now().isoformat(),
        "count": len(tweets_data),
        "posts": tweets_data
    }
    print(json.dumps(output, ensure_ascii=False, default=str))


def main(json_output: bool = False, output_limit: Optional[int] = None):
    log = sys.stderr if json_output else sys.stdout

    print("🔍 X (TWITTER) KEYWORD SEARCH - GPai Signals", file=log)
    print("=" * 80, file=log)
    print(f"Project: {PROJECT_NAME}", file=log)
    print(f"Days back: {DAYS_BACK}", file=log)
    print(f"Max tweets: {MAX_TWEETS}", file=log)
    if json_output:
        print(f"Output mode: JSON to stdout", file=log)
    print("=" * 80, file=log)

    # Check monthly quota
    usage = load_monthly_usage()
    current = usage['tweets_collected']
    new_total = current + MAX_TWEETS
    quota_percentage = new_total / MONTHLY_QUOTA
    print(f"\n📊 Monthly Quota: {current:,}/{MONTHLY_QUOTA:,} tweets used ({quota_percentage*100:.1f}%)", file=log)

    if quota_percentage >= 1.0:
        print(f"❌ MONTHLY QUOTA EXCEEDED!", file=log)
        return

    # Initialize client
    print("\n🔐 Authenticating with X API...", file=log)
    client = get_twitter_client()
    print("✅ Authentication successful", file=log)

    # Build query
    query = build_search_query()

    # Calculate start time
    start_time = datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)

    # Search tweets
    tweets, users_lookup = search_tweets(client, query, start_time, MAX_TWEETS, log=log)

    if not tweets:
        print("\n⚠️  No tweets were collected.", file=log)
        return

    # Apply filtering
    tweets = filter_tweets(tweets, EXCLUSION_PATTERNS, log=log)

    # Extract tweet data
    print("\n📝 Processing tweet data...", file=log)
    tweets_data = []
    for tweet in tweets:
        tweet_data = extract_tweet_data(tweet, users_lookup)
        tweets_data.append(tweet_data)

    # Apply limit if specified
    if output_limit and tweets_data and len(tweets_data) > output_limit:
        print(f"\n📉 Limiting to top {output_limit} tweets by engagement", file=log)
        tweets_data = sorted(
            tweets_data,
            key=lambda x: x.get('likes', 0) + x.get('retweets', 0) * 2,
            reverse=True
        )[:output_limit]

    # Update monthly usage
    update_monthly_usage(len(tweets_data))

    if tweets_data:
        if json_output:
            output_json(tweets_data, PROJECT_NAME)
            print(f"\n✅ Output {len(tweets_data)} tweets as JSON", file=log)
        else:
            print(f"\n✅ Collected {len(tweets_data)} tweets", file=log)
            for tweet in tweets_data[:5]:
                print(f"  - @{tweet['author_username']}: {tweet['text'][:80]}...", file=log)
    else:
        print("\n⚠️  No tweets were collected after filtering.", file=log)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='X (Twitter) Keyword Search - GPai Signals')
    parser.add_argument('--json', action='store_true', help='Output JSON to stdout')
    parser.add_argument('--limit', type=int, default=None, help='Max tweets to output')
    args = parser.parse_args()

    main(json_output=args.json, output_limit=args.limit)
