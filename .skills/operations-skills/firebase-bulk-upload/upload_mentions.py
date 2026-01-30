#!/usr/bin/env python3
"""
Upload social listening mentions to Firestore.

Transforms platform-specific JSON data to standardized mention schema
and uploads to clients/{client_id}/signals/.

Client ID can be provided as argument or read from inputs/active_client.md.

Usage:
    # With explicit client_id
    python upload_mentions.py <json_file> <client_id> --platform <platform> [options]
    
    # Read client_id from active_client.md
    python upload_mentions.py <json_file> --platform <platform> [options]

Arguments:
    json_file: JSON file from collection script (or "-" for stdin)
    client_id: Firestore client document ID (optional)
    --platform: Required. One of: reddit, linkedin, twitter
    --limit: Max posts to upload (default: reddit=200, linkedin=100, twitter=50)
    --report-id: Report identifier (default: "initial-onboarding")
"""

import json
import sys
import os
import argparse
from datetime import datetime, timezone
from collections import defaultdict
from pathlib import Path

# Force UTF-8 encoding on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    print("Installing firebase-admin...", file=sys.stderr)
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "firebase-admin", "-q"])
    import firebase_admin
    from firebase_admin import credentials, firestore


# Get project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent


def get_client_from_active_file():
    """Read client configuration from inputs/active_client.md."""
    active_client_path = PROJECT_ROOT / "inputs" / "active_client.md"
    
    if not active_client_path.exists():
        return None
    
    content = active_client_path.read_text()
    
    for line in content.split('\n'):
        line = line.strip()
        if '=' in line:
            parts = line.split('=', 1)
            if len(parts) == 2:
                key = parts[0].strip().upper()
                value = parts[1].strip().strip('"\'')
                if key == 'CLIENT_ID':
                    return value
    
    return None


# Default limits per platform
DEFAULT_LIMITS = {
    "reddit": 200,
    "linkedin": 100,
    "twitter": 50
}

# Default keyword classification rules (client-specific keywords loaded from context)
# These are generic fallbacks - actual keywords should come from client's keywords.md
BRAND_KEYWORDS = []  # Populated from client context
COMPETITOR_KEYWORDS = []  # Populated from client context
PRODUCT_KEYWORDS = []  # Generic product keywords
INDUSTRY_KEYWORDS = ["marketing", "b2b", "saas", "demand generation"]  # Generic industry keywords


def find_firebase_credentials():
    """Find Firebase credentials file in common locations."""
    search_paths = [
        PROJECT_ROOT,
        os.getcwd(),
        os.path.dirname(os.getcwd()),
        os.path.dirname(os.path.dirname(os.getcwd())),  # Parent of parent directory
    ]

    for path in search_paths:
        try:
            path = Path(path)
            for filename in path.iterdir():
                if filename.is_file() and 'firebase' in filename.name.lower() and filename.suffix == '.json':
                    if 'adminsdk' in filename.name.lower():
                        return str(filename)
        except (OSError, PermissionError):
            continue

    if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
        return os.environ['GOOGLE_APPLICATION_CREDENTIALS']

    return None


def classify_sentiment(text):
    """Basic sentiment classification based on keyword presence."""
    if not text:
        return "neutral"

    text_lower = text.lower()

    positive_signals = ["great", "excellent", "love", "best", "recommend", "amazing",
                       "perfect", "fantastic", "awesome", "helpful", "thank", "works well",
                       "inspiring", "empowering", "supportive", "incredible", "proud"]
    negative_signals = ["bad", "worst", "terrible", "awful", "disappointed", "frustrat",
                       "problem", "issue", "sucks", "hate", "avoid", "scam", "waste",
                       "struggle", "failed", "toxic", "discriminat"]

    positive_count = sum(1 for word in positive_signals if word in text_lower)
    negative_count = sum(1 for word in negative_signals if word in text_lower)

    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"


def classify_keyword_category(keyword):
    """Classify keyword into category and priority."""
    if not keyword:
        return "useCases", "low"

    keyword_lower = keyword.lower()

    if any(k in keyword_lower for k in BRAND_KEYWORDS):
        return "brand", "high"
    elif any(k in keyword_lower for k in COMPETITOR_KEYWORDS):
        return "competitors", "high"
    elif any(k in keyword_lower for k in PRODUCT_KEYWORDS):
        return "products", "medium"
    elif any(k in keyword_lower for k in INDUSTRY_KEYWORDS):
        return "industry", "medium"
    else:
        return "useCases", "low"


def extract_themes(text):
    """Extract themes from text based on keyword patterns."""
    if not text:
        return []

    text_lower = text.lower()
    themes = []

    theme_keywords = {
        "funding": ["funding", "investor", "raise", "capital", "vc", "venture", "seed"],
        "hiring": ["hire", "hiring", "recruit", "talent", "candidate", "team"],
        "community": ["community", "network", "connect", "support", "mentor", "together"],
        "growth": ["scale", "grow", "growth", "expand", "milestone", "revenue"],
        "challenges": ["challenge", "struggle", "difficult", "hard", "obstacle", "barrier"],
        "success": ["success", "won", "achieve", "milestone", "celebrate", "proud"]
    }

    for theme, keywords in theme_keywords.items():
        if any(kw in text_lower for kw in keywords):
            themes.append(theme)

    return themes


def get_engagement_score(post, platform):
    """Calculate engagement score based on platform-specific metrics."""
    if platform == "reddit":
        return int(post.get('score', 0) or 0) + int(post.get('num_comments', 0) or 0)
    elif platform == "linkedin":
        return (int(post.get('likes', 0) or post.get('total_reactions', 0) or 0) +
                int(post.get('comments', 0) or post.get('total_comments', 0) or 0) * 2 +
                int(post.get('shares', 0) or post.get('num_shares', 0) or 0) * 3)
    elif platform == "twitter":
        return (int(post.get('likes', 0) or 0) +
                int(post.get('retweets', 0) or 0) * 2 +
                int(post.get('replies', 0) or 0))
    return 0


def transform_reddit_post(post, report_id):
    """Transform Reddit post to Firestore signal schema."""
    import uuid
    post_id = post.get('post_id', post.get('id', ''))
    signal_id = str(uuid.uuid4())

    title = post.get('title', '')
    selftext = post.get('selftext', '')
    full_text = f"{title} {selftext}".strip()

    matched_keyword = post.get('matched_keyword', '')
    category, priority = classify_keyword_category(matched_keyword)

    # Calculate engagement score: likes + comments*2 + shares*3
    likes = int(post.get('score', 0) or 0)
    comments = int(post.get('num_comments', 0) or 0)
    shares = 0
    engagement_score = likes + (comments * 2) + (shares * 3)

    return signal_id, {
        # Identity
        "id": signal_id,
        "legacyId": f"reddit_{post_id}",
        "externalId": post_id,
        # Signal type
        "signalType": "keyword-match",
        # Content
        "platform": "reddit",
        "sourceUrl": post.get('permalink', post.get('url', '')),
        "content": full_text[:2000],
        "contentPreview": title[:200],
        # Author
        "author": {
            "name": post.get('author', '[deleted]'),
            "handle": f"u/{post.get('author', '[deleted]')}",
            "profileUrl": f"https://reddit.com/user/{post.get('author', '')}" if post.get('author') else "",
            "followerCount": 0
        },
        # Engagement
        "engagement": {
            "likes": likes,
            "comments": comments,
            "shares": shares
        },
        "engagementScore": engagement_score,
        # Discovery
        "matchedKeywords": [matched_keyword] if matched_keyword else [],
        "keywordCategory": category,
        "keywordPriority": priority,
        # Analysis
        "sentiment": classify_sentiment(full_text),
        "themes": extract_themes(full_text),
        # Workflow
        "status": "active",
        "usageStatus": "unused",
        # Platform-specific
        "platformContext": {
            "subreddit": post.get('subreddit', ''),
            "isThread": post.get('is_self', True)
        },
        # Timestamps
        "postedAt": post.get('created_date', post.get('created_utc', '')),
        "collectedAt": datetime.now(timezone.utc).isoformat(),
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        # Provenance
        "source": "social-listening-collect",
        "reportId": report_id
    }


def transform_linkedin_post(post, report_id):
    """Transform LinkedIn post to Firestore signal schema."""
    import uuid
    post_id = post.get('post_id', post.get('uid', ''))
    signal_id = str(uuid.uuid4())

    content = post.get('content', post.get('text', ''))
    content_preview = post.get('content_preview', content[:200] if content else '')

    matched_keyword = post.get('matched_keyword', post.get('query_name', ''))
    category, priority = classify_keyword_category(matched_keyword)

    # Calculate engagement score: likes + comments*2 + shares*3
    likes = int(post.get('likes', 0) or post.get('total_reactions', 0) or 0)
    comments = int(post.get('comments', 0) or post.get('total_comments', 0) or 0)
    shares = int(post.get('shares', 0) or post.get('num_shares', 0) or 0)
    engagement_score = likes + (comments * 2) + (shares * 3)

    return signal_id, {
        # Identity
        "id": signal_id,
        "legacyId": f"linkedin_{post_id[:20]}",
        "externalId": post_id,
        # Signal type
        "signalType": "keyword-match",
        # Content
        "platform": "linkedin",
        "sourceUrl": post.get('url', post.get('share_url', '')),
        "content": content[:2000] if content else '',
        "contentPreview": content_preview[:200] if content_preview else '',
        # Author
        "author": {
            "name": post.get('actor_name', ''),
            "handle": post.get('actor_name', ''),
            "profileUrl": "",
            "followerCount": int(post.get('actor_followers', 0) or post.get('actor_followers_count', 0) or 0)
        },
        # Engagement
        "engagement": {
            "likes": likes,
            "comments": comments,
            "shares": shares
        },
        "engagementScore": engagement_score,
        # Discovery
        "matchedKeywords": [matched_keyword] if matched_keyword else [],
        "keywordCategory": category,
        "keywordPriority": priority,
        # Analysis
        "sentiment": classify_sentiment(content),
        "themes": extract_themes(content),
        # Workflow
        "status": "active",
        "usageStatus": "unused",
        # Timestamps
        "postedAt": post.get('date_posted', ''),
        "collectedAt": datetime.now(timezone.utc).isoformat(),
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        # Provenance
        "source": "social-listening-collect",
        "reportId": report_id
    }


def transform_twitter_post(post, report_id):
    """Transform Twitter post to Firestore signal schema."""
    import uuid
    tweet_id = post.get('tweet_id', post.get('id', ''))
    signal_id = str(uuid.uuid4())

    text = post.get('text', '')
    matched_keyword = post.get('matched_query', post.get('query_name', ''))
    category, priority = classify_keyword_category(matched_keyword)

    # Calculate engagement score: likes + comments*2 + shares*3
    likes = int(post.get('likes', 0) or 0)
    comments = int(post.get('replies', 0) or 0)
    shares = int(post.get('retweets', 0) or 0)
    engagement_score = likes + (comments * 2) + (shares * 3)

    return signal_id, {
        # Identity
        "id": signal_id,
        "legacyId": f"twitter_{tweet_id}",
        "externalId": tweet_id,
        # Signal type
        "signalType": "keyword-match",
        # Content
        "platform": "twitter",
        "sourceUrl": post.get('url', post.get('tweet_url', '')),
        "content": text[:2000] if text else '',
        "contentPreview": text[:200] if text else '',
        # Author
        "author": {
            "name": post.get('author_name', ''),
            "handle": f"@{post.get('author_username', '')}",
            "profileUrl": f"https://twitter.com/{post.get('author_username', '')}" if post.get('author_username') else "",
            "followerCount": int(post.get('author_followers', 0) or 0)
        },
        # Engagement
        "engagement": {
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "retweets": shares
        },
        "engagementScore": engagement_score,
        # Discovery
        "matchedKeywords": [matched_keyword] if matched_keyword else [],
        "keywordCategory": category,
        "keywordPriority": priority,
        # Analysis
        "sentiment": classify_sentiment(text),
        "themes": extract_themes(text),
        # Workflow
        "status": "active",
        "usageStatus": "unused",
        # Timestamps
        "postedAt": post.get('created_at', ''),
        "collectedAt": datetime.now(timezone.utc).isoformat(),
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        # Provenance
        "source": "social-listening-collect",
        "reportId": report_id
    }


def parse_collection_path(path):
    """Parse a collection path into segments."""
    path = path.strip('/')
    return path.split('/')


def get_collection_ref(db, path):
    """Get a Firestore collection reference from a path string."""
    segments = parse_collection_path(path)

    if len(segments) == 1:
        return db.collection(segments[0])

    ref = db
    for i, segment in enumerate(segments):
        if i % 2 == 0:
            ref = ref.collection(segment)
        else:
            ref = ref.document(segment)

    return ref


def main():
    parser = argparse.ArgumentParser(
        description='Upload social listening mentions to Firestore',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('json_file', help='JSON file from collection script (or "-" for stdin)')
    parser.add_argument('client_id', nargs='?', default=None,
                       help='Firestore client document ID (optional, reads from active_client.md)')
    parser.add_argument('--platform', required=True, choices=['reddit', 'linkedin', 'twitter'],
                       help='Source platform')
    parser.add_argument('--limit', type=int, default=None,
                       help='Max posts to upload (default: platform-specific)')
    parser.add_argument('--report-id', default='initial-onboarding',
                       help='Report identifier (default: initial-onboarding)')

    args = parser.parse_args()

    # Get client_id from args or active_client.md
    client_id = args.client_id
    if not client_id:
        client_id = get_client_from_active_file()
        if not client_id:
            print("ERROR: client_id not provided and not found in inputs/active_client.md", file=sys.stderr)
            sys.exit(1)
        print(f"Using client_id from active_client.md: {client_id}", file=sys.stderr)

    # Set limit with platform-specific default
    limit = args.limit if args.limit is not None else DEFAULT_LIMITS.get(args.platform, 100)

    # Find credentials
    cred_path = find_firebase_credentials()
    if not cred_path:
        print("ERROR: Could not find Firebase credentials file.", file=sys.stderr)
        print("Please ensure a *firebase-adminsdk*.json file exists in the project.", file=sys.stderr)
        sys.exit(1)

    print(f"Using credentials: {cred_path}", file=sys.stderr)

    # Initialize Firebase
    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

    db = firestore.client()

    # Load JSON data
    print(f"Loading {args.platform} data...", file=sys.stderr)
    if args.json_file == '-':
        data = json.load(sys.stdin)
    else:
        with open(args.json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

    # Extract posts from various JSON structures
    posts = []
    if isinstance(data, list):
        posts = data
    elif isinstance(data, dict):
        if 'posts' in data:
            posts = data['posts']
        elif 'documents' in data:
            # Handle firestore_upload.json format
            posts = [doc.get('data', doc) for doc in data['documents']]
        else:
            posts = [data]

    print(f"Found {len(posts)} posts", file=sys.stderr)

    # Select transformer based on platform
    transformers = {
        'reddit': transform_reddit_post,
        'linkedin': transform_linkedin_post,
        'twitter': transform_twitter_post
    }
    transform = transformers[args.platform]

    # Sort by engagement and apply limit
    posts_with_score = [(post, get_engagement_score(post, args.platform)) for post in posts]
    posts_with_score.sort(key=lambda x: x[1], reverse=True)

    if len(posts_with_score) > limit:
        print(f"Limiting to top {limit} posts by engagement (from {len(posts_with_score)})", file=sys.stderr)
        posts_with_score = posts_with_score[:limit]

    # Transform posts
    mentions = []
    seen_ids = set()

    for post, _ in posts_with_score:
        mention_id, mention_data = transform(post, args.report_id)

        # Deduplicate by mention_id
        if mention_id not in seen_ids:
            seen_ids.add(mention_id)
            mentions.append((mention_id, mention_data))

    print(f"Transformed {len(mentions)} unique mentions", file=sys.stderr)

    # Upload to Firestore
    # Path structure: clients/{id}/signals/{signalId}
    collection_path = f"clients/{client_id}/signals"
    collection_ref = get_collection_ref(db, collection_path)

    upload_count = 0
    errors = []

    # Stats tracking
    stats = {
        "byPlatform": defaultdict(int),
        "bySentiment": defaultdict(int),
        "byCategory": defaultdict(int)
    }

    # Use batch writes (max 500 per batch)
    batch_size = 500
    batch = db.batch()
    batch_count = 0

    for mention_id, mention_data in mentions:
        try:
            doc_ref = collection_ref.document(mention_id)
            batch.set(doc_ref, mention_data)

            # Track stats
            stats["byPlatform"][mention_data["platform"]] += 1
            stats["bySentiment"][mention_data["sentiment"]] += 1
            stats["byCategory"][mention_data["keywordCategory"]] += 1

            batch_count += 1

            if batch_count >= batch_size:
                batch.commit()
                upload_count += batch_count
                print(f"[{upload_count}/{len(mentions)}] Committed batch", file=sys.stderr)
                batch = db.batch()
                batch_count = 0

        except Exception as e:
            error_msg = f"Error with mention {mention_id}: {str(e)}"
            print(f"  ERROR: {error_msg}", file=sys.stderr)
            errors.append(error_msg)

    # Commit remaining
    if batch_count > 0:
        batch.commit()
        upload_count += batch_count
        print(f"[{upload_count}/{len(mentions)}] Committed final batch", file=sys.stderr)

    # Summary
    print("\n" + "="*60, file=sys.stderr)
    print(f"Upload complete!", file=sys.stderr)
    print(f"  Uploaded: {upload_count}", file=sys.stderr)
    print(f"  Duplicates skipped: {len(posts_with_score) - len(mentions)}", file=sys.stderr)
    print(f"  Errors: {len(errors)}", file=sys.stderr)

    if errors:
        print("\nErrors encountered:", file=sys.stderr)
        for e in errors[:5]:
            print(f"  - {e}", file=sys.stderr)
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more", file=sys.stderr)

    # Output JSON result to stdout
    result = {
        'success': len(errors) == 0,
        'uploaded': upload_count,
        'duplicatesSkipped': len(posts_with_score) - len(mentions),
        'limitApplied': limit,
        'errors': len(errors),
        'errorMessages': errors[:10],
        'collectionPath': collection_path,
        'clientId': client_id,
        'statistics': {
            'byPlatform': dict(stats["byPlatform"]),
            'bySentiment': dict(stats["bySentiment"]),
            'byCategory': dict(stats["byCategory"])
        }
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
