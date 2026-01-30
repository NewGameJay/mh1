#!/usr/bin/env python3
"""
Fetch thought leader profiles and posts for ghostwriting context.
Multi-client marketing platform - mh1-hq structure.

Usage:
    python fetch_thought_leader_posts.py [client_id] [options]

Arguments:
    client_id: Firebase Client ID (or omit to read from active_client.md)
    --min-relevance: Minimum relevance score (default: 7.0)
    --limit-per-leader: Maximum posts per thought leader (default: 5)
    --limit-leaders: Maximum thought leaders (default: 10)
    --limit-total-posts: Maximum total posts (default: 50)
    --output: Output file path (default: stdout)
    --format: Output format: json, markdown, or summary (default: json)
"""

import json
import sys
import os
import argparse
from datetime import datetime, timezone
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
    """Find Firebase credentials file."""
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


def extract_relevance_score(leader_data):
    """Extract relevance score from thought leader data."""
    relevance = leader_data.get("relevance", {})
    if isinstance(relevance, dict):
        return relevance.get("score", 0) or 0
    return 0


def format_leader_for_output(leader_data, posts):
    """Format thought leader data for output."""
    relevance = leader_data.get("relevance", {})
    discovery = leader_data.get("discovery", {})

    tags = leader_data.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.strip("[]").split(",") if t.strip()]

    return {
        "id": leader_data.get("id"),
        "name": leader_data.get("name"),
        "title": leader_data.get("title"),
        "company": leader_data.get("company"),
        "bio": leader_data.get("bio"),
        "linkedinUrl": leader_data.get("linkedinUrl"),
        "twitterHandle": leader_data.get("twitterHandle"),
        "tags": tags,
        "relevance": {
            "score": relevance.get("score") if isinstance(relevance, dict) else 0,
            "reason": relevance.get("reason") if isinstance(relevance, dict) else "",
        },
        "discovery": {
            "source": discovery.get("source") if isinstance(discovery, dict) else "",
            "searchStrategy": discovery.get("searchStrategy") if isinstance(discovery, dict) else "",
        },
        "topThemes": leader_data.get("topThemes", []),
        "writingStyle": leader_data.get("writingStyle"),
        "totalPostsCollected": leader_data.get("totalPostsCollected", 0),
        "status": leader_data.get("status", "active"),
        "posts": posts
    }


def format_post_for_output(post_data):
    """Format a thought leader post for output."""
    author = post_data.get("author", {})

    return {
        "id": post_data.get("id"),
        "platform": post_data.get("platform"),
        "content": post_data.get("content"),
        "url": post_data.get("url"),
        "postedAt": post_data.get("postedAt"),
        "likes": post_data.get("likes", 0),
        "comments": post_data.get("comments", 0),
        "shares": post_data.get("shares", 0),
        "collectedAt": post_data.get("collectedAt"),
    }


def calculate_stats(leaders, all_posts):
    """Calculate statistics for the fetched data."""
    stats = {
        "totalLeaders": len(leaders),
        "totalPosts": len(all_posts),
        "avgRelevance": 0,
        "byTag": defaultdict(int),
        "byPlatform": defaultdict(int),
        "postsPerLeader": {}
    }

    if not leaders:
        return stats

    total_relevance = 0
    for leader in leaders:
        relevance = leader.get("relevance", {})
        score = relevance.get("score", 0) if isinstance(relevance, dict) else 0
        total_relevance += score

        tags = leader.get("tags", [])
        for tag in tags:
            stats["byTag"][tag] += 1

        stats["postsPerLeader"][leader.get("name", "Unknown")] = len(leader.get("posts", []))

    stats["avgRelevance"] = round(total_relevance / len(leaders), 2) if leaders else 0

    for post in all_posts:
        platform = post.get("platform", "unknown")
        stats["byPlatform"][platform] += 1

    stats["byTag"] = dict(stats["byTag"])
    stats["byPlatform"] = dict(stats["byPlatform"])

    return stats


def main():
    parser = argparse.ArgumentParser(description='Fetch thought leader posts')
    parser.add_argument('client_id', nargs='?', help='Firebase Client ID')
    parser.add_argument('--client-name', default='Client')
    parser.add_argument('--min-relevance', type=float, default=7.0)
    parser.add_argument('--limit-per-leader', type=int, default=5)
    parser.add_argument('--limit-leaders', type=int, default=10)
    parser.add_argument('--limit-total-posts', type=int, default=50)
    parser.add_argument('--output', '-o', default=None)
    parser.add_argument('--format', choices=['json', 'markdown', 'summary'], default='json')

    args = parser.parse_args()

    if not args.client_id:
        active_client_id, active_name = get_client_from_active_file()
        if active_client_id:
            args.client_id = active_client_id
            if active_name:
                args.client_name = active_name
        else:
            print("ERROR: No client_id provided", file=sys.stderr)
            sys.exit(1)

    CLIENT_ID = args.client_id
    CLIENT_NAME = args.client_name

    cred_path = find_firebase_credentials()
    if not cred_path:
        print("ERROR: Could not find Firebase credentials file.", file=sys.stderr)
        sys.exit(1)

    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

    db = firestore.client()

    print(f"Querying: clients/{CLIENT_ID}/thoughtLeaders", file=sys.stderr)

    try:
        leaders_ref = db.collection("clients").document(CLIENT_ID).collection("thoughtLeaders")
        docs = leaders_ref.stream()

        all_leaders = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            all_leaders.append(data)

    except Exception as e:
        print(f"ERROR: Failed to query Firebase: {e}", file=sys.stderr)
        sys.exit(1)

    filtered_leaders = []
    for leader in all_leaders:
        score = extract_relevance_score(leader)
        status = leader.get("status", "active")
        if score >= args.min_relevance and status == "active":
            filtered_leaders.append(leader)

    filtered_leaders.sort(key=lambda l: extract_relevance_score(l), reverse=True)
    limited_leaders = filtered_leaders[:args.limit_leaders]

    formatted_leaders = []
    all_posts = []
    total_posts_fetched = 0

    for leader in limited_leaders:
        leader_id = leader.get("id")
        leader_name = leader.get("name", "Unknown")

        remaining_posts = args.limit_total_posts - total_posts_fetched
        posts_to_fetch = min(args.limit_per_leader, remaining_posts)

        if posts_to_fetch <= 0:
            formatted_leader = format_leader_for_output(leader, [])
            formatted_leaders.append(formatted_leader)
            continue

        try:
            posts_ref = db.collection("clients").document(CLIENT_ID) \
                .collection("thoughtLeaders").document(leader_id).collection("posts")
            posts_docs = posts_ref.stream()

            leader_posts = []
            for doc in posts_docs:
                post_data = doc.to_dict()
                post_data["id"] = doc.id
                leader_posts.append(post_data)

            leader_posts.sort(key=lambda p: p.get("postedAt", ""), reverse=True)
            leader_posts = leader_posts[:posts_to_fetch]

            formatted_posts = [format_post_for_output(p) for p in leader_posts]
            all_posts.extend(formatted_posts)
            total_posts_fetched += len(formatted_posts)

        except Exception as e:
            print(f"  WARNING: Failed to fetch posts for {leader_name}: {e}", file=sys.stderr)
            formatted_posts = []

        formatted_leader = format_leader_for_output(leader, formatted_posts)
        formatted_leaders.append(formatted_leader)

    stats = calculate_stats(formatted_leaders, all_posts)

    output = {
        "success": True,
        "clientId": CLIENT_ID,
        "clientName": CLIENT_NAME,
        "query": {
            "minRelevance": args.min_relevance,
            "limitLeaders": args.limit_leaders,
            "limitPerLeader": args.limit_per_leader,
            "limitTotalPosts": args.limit_total_posts
        },
        "results": {
            "totalLeadersInCollection": len(all_leaders),
            "leadersReturned": len(formatted_leaders),
            "totalPostsFetched": total_posts_fetched
        },
        "statistics": stats,
        "thoughtLeaders": formatted_leaders
    }

    output_str = json.dumps(output, indent=2, ensure_ascii=False, default=str)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_str)
        print(f"Output written to: {args.output}", file=sys.stderr)
    else:
        print(output_str)


if __name__ == "__main__":
    main()
