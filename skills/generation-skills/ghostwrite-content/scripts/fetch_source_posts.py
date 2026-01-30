#!/usr/bin/env python3
"""
Fetch signals for ghostwriting context.
Multi-client marketing platform - mh1-hq structure.

Queries Firebase for high-relevance signals with proper filtering, sorting,
and limiting to avoid token overflow issues.

Usage:
    python fetch_source_posts.py <client_id> [options]

Arguments:
    client_id: Firebase Client ID (or omit to read from active_client.md)
    --client-name: Client display name (default: "Client")
    --min-relevance: Minimum relevance score (default: 5)
    --limit: Maximum posts to return (default: 25)
    --output: Output file path (default: stdout)
    --format: Output format: json, markdown, or summary (default: json)
"""

import json
import sys
import os
import argparse
import math
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

SKILL_ROOT = Path(__file__).parent.parent
SYSTEM_ROOT = SKILL_ROOT.parent.parent
sys.path.insert(0, str(SYSTEM_ROOT / "lib"))

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "firebase-admin", "-q"])
    import firebase_admin
    from firebase_admin import credentials, firestore

try:
    from dateutil import parser as date_parser
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dateutil", "-q"])
    from dateutil import parser as date_parser


def get_client_from_active_file():
    """Read client configuration from inputs/active_client.md."""
    active_client_path = SYSTEM_ROOT / "inputs" / "active_client.md"
    if not active_client_path.exists():
        return None, None
    
    with open(active_client_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    client_id = None
    client_name = None
    
    for line in content.split('\n'):
        if 'Firestore Client ID:' in line:
            client_id = line.split(':', 1)[1].strip()
        elif 'Client Name:' in line:
            client_name = line.split(':', 1)[1].strip()
    
    return client_id, client_name


def find_firebase_credentials():
    """Find Firebase credentials file in common locations."""
    search_paths = [os.getcwd(), os.path.dirname(os.getcwd()), str(SYSTEM_ROOT)]

    for path in search_paths:
        try:
            for filename in os.listdir(path):
                if 'firebase' in filename.lower() and filename.endswith('.json'):
                    if 'adminsdk' in filename.lower():
                        return os.path.join(path, filename)
        except (OSError, PermissionError):
            continue

    if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
        return os.environ['GOOGLE_APPLICATION_CREDENTIALS']

    return None


def parse_date(date_value):
    """Parse various date formats into a datetime object."""
    if date_value is None:
        return None
    if isinstance(date_value, datetime):
        return date_value
    if hasattr(date_value, 'timestamp'):
        return datetime.fromtimestamp(date_value.timestamp(), tz=timezone.utc)
    if isinstance(date_value, str):
        try:
            return date_parser.parse(date_value)
        except (ValueError, TypeError):
            return None
    return None


def is_in_date_range(post, start_date, end_date, date_field):
    """Check if a post falls within the specified date range."""
    if start_date is None and end_date is None:
        return True

    post_date = parse_date(post.get(date_field))
    if post_date is None:
        alt_field = "postedAt" if date_field == "collectedAt" else "collectedAt"
        post_date = parse_date(post.get(alt_field))

    if post_date is None:
        return False

    if post_date.tzinfo is None:
        post_date = post_date.replace(tzinfo=timezone.utc)

    if start_date and post_date < start_date:
        return False
    if end_date and post_date > end_date:
        return False

    return True


def calculate_engagement_score(post):
    """Calculate engagement-weighted effective score."""
    relevance = post.get("relevanceScore", 0) or 0
    engagement = post.get("engagement", {})

    likes = engagement.get("likes", 0) or 0
    comments = engagement.get("comments", 0) or 0
    shares = engagement.get("shares", 0) or 0

    total_engagement = likes + (comments * 2) + (shares * 3)
    engagement_multiplier = 1 + (0.1 * math.log10(1 + total_engagement))
    effective_score = relevance * engagement_multiplier

    return round(effective_score, 2)


def calculate_stats(posts, min_relevance, include_engagement=False):
    """Calculate statistics for the posts."""
    stats = {
        "totalLoaded": len(posts),
        "minRelevanceFilter": min_relevance,
        "avgRelevance": 0,
        "byPlatform": defaultdict(lambda: {"count": 0, "sumRelevance": 0, "sumEngagement": 0}),
        "byRelevanceTier": {"high": 0, "medium": 0, "low": 0},
        "byIcpFit": defaultdict(int),
        "byContentPotential": defaultdict(int)
    }

    if include_engagement:
        stats["avgEffectiveScore"] = 0
        stats["avgEngagement"] = 0

    if not posts:
        return stats

    total_relevance = 0
    total_effective = 0
    total_engagement = 0

    for post in posts:
        score = post.get("relevanceScore", 0) or 0
        platform = post.get("platform", "unknown")
        icp_fit = post.get("icpFit", "Unknown")
        content_potential = post.get("contentPotential", "Unknown")

        total_relevance += score
        stats["byPlatform"][platform]["count"] += 1
        stats["byPlatform"][platform]["sumRelevance"] += score

        if include_engagement:
            engagement = post.get("engagement", {})
            likes = engagement.get("likes", 0) or 0
            comments = engagement.get("comments", 0) or 0
            shares = engagement.get("shares", 0) or 0
            post_engagement = likes + comments + shares
            total_engagement += post_engagement
            stats["byPlatform"][platform]["sumEngagement"] += post_engagement
            effective = post.get("effectiveScore", 0) or 0
            total_effective += effective

        if score >= 8:
            stats["byRelevanceTier"]["high"] += 1
        elif score >= 5:
            stats["byRelevanceTier"]["medium"] += 1
        else:
            stats["byRelevanceTier"]["low"] += 1

        if icp_fit:
            icp_category = icp_fit.split(" - ")[0] if " - " in icp_fit else icp_fit.split()[0]
            stats["byIcpFit"][icp_category] += 1

        if content_potential:
            potential_category = content_potential.split(" - ")[0] if " - " in content_potential else content_potential.split()[0]
            stats["byContentPotential"][potential_category] += 1

    stats["avgRelevance"] = round(total_relevance / len(posts), 2) if posts else 0

    if include_engagement and posts:
        stats["avgEffectiveScore"] = round(total_effective / len(posts), 2)
        stats["avgEngagement"] = round(total_engagement / len(posts), 2)

    for platform, data in stats["byPlatform"].items():
        if data["count"] > 0:
            data["avgRelevance"] = round(data["sumRelevance"] / data["count"], 2)
            if include_engagement:
                data["avgEngagement"] = round(data["sumEngagement"] / data["count"], 2)
        del data["sumRelevance"]
        del data["sumEngagement"]

    stats["byPlatform"] = dict(stats["byPlatform"])
    stats["byIcpFit"] = dict(stats["byIcpFit"])
    stats["byContentPotential"] = dict(stats["byContentPotential"])

    return stats


def format_post_for_output(post, include_engagement=False):
    """Clean and format a signal for output."""
    engagement = post.get("engagement", {})
    author = post.get("author", {})
    url = post.get("sourceUrl") or post.get("postUrl")

    result = {
        "id": post.get("id"),
        "legacyId": post.get("legacyId"),
        "signalType": post.get("signalType", "keyword-match"),
        "platform": post.get("platform"),
        "relevanceScore": post.get("relevanceScore"),
        "engagementScore": post.get("engagementScore"),
        "icpFit": post.get("icpFit"),
        "contentPotential": post.get("contentPotential"),
        "content": post.get("content"),
        "sourceUrl": url,
        "postedAt": post.get("postedAt"),
        "author": {
            "name": author.get("name", ""),
            "handle": author.get("handle", ""),
            "profileUrl": author.get("profileUrl", author.get("url", "")),
            "followerCount": author.get("followerCount")
        },
        "engagement": {
            "likes": engagement.get("likes", 0),
            "comments": engagement.get("comments", 0),
            "shares": engagement.get("shares", 0),
            "views": engagement.get("views")
        },
        "matchedKeywords": post.get("matchedKeywords", []),
        "source": post.get("source", ""),
        "collectedAt": post.get("collectedAt"),
        "status": post.get("status", "active"),
        "usageStatus": post.get("usageStatus", "unused")
    }

    if include_engagement:
        result["effectiveScore"] = post.get("effectiveScore")

    return result


def main():
    parser = argparse.ArgumentParser(description='Fetch signals for ghostwriting')
    parser.add_argument('client_id', nargs='?', help='Firebase Client ID')
    parser.add_argument('--client-name', default='Client', help='Client display name')
    parser.add_argument('--min-relevance', type=float, default=5.0, help='Minimum relevance score')
    parser.add_argument('--limit', type=int, default=25, help='Maximum posts to return')
    parser.add_argument('--output', '-o', default=None, help='Output file path')
    parser.add_argument('--format', choices=['json', 'markdown', 'summary'], default='json')
    parser.add_argument('--start-date', default=None, help='Filter posts from date (YYYY-MM-DD)')
    parser.add_argument('--end-date', default=None, help='Filter posts until date (YYYY-MM-DD)')
    parser.add_argument('--date-field', choices=['collectedAt', 'postedAt'], default='collectedAt')
    parser.add_argument('--include-engagement-score', action='store_true')

    args = parser.parse_args()

    # Read from active_client.md if not provided
    if not args.client_id:
        active_client_id, active_name = get_client_from_active_file()
        if active_client_id:
            args.client_id = active_client_id
            if active_name:
                args.client_name = active_name
        else:
            print("ERROR: No client_id provided and could not read from active_client.md", file=sys.stderr)
            sys.exit(1)

    CLIENT_ID = args.client_id
    CLIENT_NAME = args.client_name

    start_date = None
    end_date = None
    if args.start_date:
        try:
            start_date = date_parser.parse(args.start_date)
            if start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=timezone.utc)
        except ValueError:
            print(f"ERROR: Invalid start date format: {args.start_date}", file=sys.stderr)
            sys.exit(1)
    if args.end_date:
        try:
            end_date = date_parser.parse(args.end_date)
            if end_date.tzinfo is None:
                end_date = end_date.replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
        except ValueError:
            print(f"ERROR: Invalid end date format: {args.end_date}", file=sys.stderr)
            sys.exit(1)

    cred_path = find_firebase_credentials()
    if not cred_path:
        print("ERROR: Could not find Firebase credentials file.", file=sys.stderr)
        sys.exit(1)

    print(f"Using credentials: {cred_path}", file=sys.stderr)

    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

    db = firestore.client()

    collection_path = f"clients/{CLIENT_ID}/signals"
    print(f"Querying: {collection_path}", file=sys.stderr)

    try:
        collection_ref = db.collection("clients").document(CLIENT_ID).collection("signals")
        docs = collection_ref.stream()
        all_posts = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            all_posts.append(data)

        print(f"Total signals in collection: {len(all_posts)}", file=sys.stderr)

    except Exception as e:
        print(f"ERROR: Failed to query Firebase: {e}", file=sys.stderr)
        sys.exit(1)

    if start_date or end_date:
        date_filtered = [p for p in all_posts if is_in_date_range(p, start_date, end_date, args.date_field)]
    else:
        date_filtered = all_posts

    filtered_posts = [p for p in date_filtered if (p.get("relevanceScore") or 0) >= args.min_relevance]
    total_available = len(filtered_posts)

    if args.include_engagement_score:
        for post in filtered_posts:
            post["effectiveScore"] = calculate_engagement_score(post)
        filtered_posts.sort(key=lambda p: p.get("effectiveScore") or 0, reverse=True)
    else:
        filtered_posts.sort(key=lambda p: p.get("relevanceScore") or 0, reverse=True)

    limited_posts = filtered_posts[:args.limit]
    formatted_posts = [format_post_for_output(p, args.include_engagement_score) for p in limited_posts]
    stats = calculate_stats(limited_posts, args.min_relevance, args.include_engagement_score)

    query_info = {
        "minRelevance": args.min_relevance,
        "limit": args.limit,
        "includeEngagementScore": args.include_engagement_score
    }

    if args.format == 'summary':
        output = {
            "success": True,
            "clientId": CLIENT_ID,
            "clientName": CLIENT_NAME,
            "query": query_info,
            "results": {
                "totalInCollection": len(all_posts),
                "totalAvailable": total_available,
                "postsReturned": len(formatted_posts)
            },
            "statistics": stats
        }
    else:
        output = {
            "success": True,
            "clientId": CLIENT_ID,
            "clientName": CLIENT_NAME,
            "query": query_info,
            "results": {
                "totalInCollection": len(all_posts),
                "totalAvailable": total_available,
                "postsReturned": len(formatted_posts)
            },
            "statistics": stats,
            "posts": formatted_posts
        }

    output_str = json.dumps(output, indent=2, ensure_ascii=False, default=str)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_str)
        print(f"Output written to: {args.output}", file=sys.stderr)
    else:
        print(output_str)

    print(f"\nFetch complete! Returned: {len(formatted_posts)}", file=sys.stderr)


if __name__ == "__main__":
    main()
