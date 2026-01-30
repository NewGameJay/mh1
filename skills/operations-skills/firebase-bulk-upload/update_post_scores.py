#!/usr/bin/env python3
"""
Update social listening posts in Firestore with scoring data.

Takes scored posts JSON and updates existing Firestore documents with
relevance scores, ICP fit, content potential, and other scoring metadata.
Supports upsert mode to create posts that don't exist.

Client ID can be provided as argument or read from inputs/active_client.md.

Usage:
    # With explicit client_id
    python update_post_scores.py <json_file> <client_id> [options]
    
    # Read client_id from active_client.md
    python update_post_scores.py <json_file> [options]

Arguments:
    json_file: JSON file containing scored posts (or "-" for stdin)
    client_id: Firestore client document ID (optional)
    --upsert: Create posts if they do not exist (default: update only)
    --min-score: Only process posts with relevanceScore >= this value (default: 0)
"""

import json
import sys
import os
import argparse
from datetime import datetime, timezone
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


def extract_scoring_fields(post):
    """Extract only the scoring-related fields from a post."""
    scoring_data = {
        "lastUpdatedAt": datetime.now(timezone.utc).isoformat()
    }

    # Core scoring fields
    if "relevanceScore" in post:
        scoring_data["relevanceScore"] = post["relevanceScore"]

    if "icpFit" in post:
        scoring_data["icpFit"] = post["icpFit"]

    if "contentPotential" in post:
        scoring_data["contentPotential"] = post["contentPotential"]

    if "competitorsMentioned" in post:
        scoring_data["competitorsMentioned"] = post["competitorsMentioned"]

    if "scoredAt" in post:
        scoring_data["scoredAt"] = post["scoredAt"]

    if "source" in post:
        scoring_data["scoredBy"] = post["source"]

    # Detailed scores breakdown
    if "scores" in post:
        scoring_data["scores"] = post["scores"]

    # Enhanced enrichment fields (v2)
    if "matchedKeywords" in post:
        scoring_data["matchedKeywords"] = post["matchedKeywords"]

    if "sentiment" in post:
        scoring_data["sentiment"] = post["sentiment"]

    if "sentimentContext" in post:
        scoring_data["sentimentContext"] = post["sentimentContext"]

    if "personaMatch" in post:
        scoring_data["personaMatch"] = post["personaMatch"]

    if "signalTags" in post:
        scoring_data["signalTags"] = post["signalTags"]

    if "threadContext" in post:
        scoring_data["threadContext"] = post["threadContext"]

    return scoring_data


def build_full_document(post):
    """Build a complete document for upsert mode when post doesn't exist."""
    doc = {
        "platform": post.get("platform", "unknown"),
        "postId": post.get("postId", ""),
        "postUrl": post.get("postUrl", ""),
        "content": post.get("content", "")[:2000] if post.get("content") else "",
        "author": post.get("author", {}),
        "postedAt": post.get("postedAt", ""),
        "collectedAt": post.get("collectedAt", datetime.now(timezone.utc).isoformat()),
        "lastUpdatedAt": datetime.now(timezone.utc).isoformat(),
        "engagement": post.get("engagement", {"likes": 0, "comments": 0, "shares": 0}),
        "source": post.get("source", "social-listening-collect"),

        # Keyword matching (v2 - structured array)
        "matchedKeywords": post.get("matchedKeywords", []),

        # Scoring fields
        "relevanceScore": post.get("relevanceScore"),
        "icpFit": post.get("icpFit", ""),
        "contentPotential": post.get("contentPotential", ""),
        "competitorsMentioned": post.get("competitorsMentioned", []),
        "scoredAt": post.get("scoredAt", datetime.now(timezone.utc).isoformat()),
        "scoredBy": post.get("source", "competitive-intelligence-analyst"),

        # Enhanced enrichment fields (v2)
        "sentiment": post.get("sentiment", ""),
        "sentimentContext": post.get("sentimentContext", ""),
        "personaMatch": post.get("personaMatch", []),
        "signalTags": post.get("signalTags", []),
    }

    # Add detailed scores if present
    if "scores" in post:
        doc["scores"] = post["scores"]

    # Add thread context if present (primarily for Reddit)
    if "threadContext" in post:
        doc["threadContext"] = post["threadContext"]

    # Add actor type if present
    if "actorType" in post:
        doc["actorType"] = post["actorType"]

    # Legacy: Keep keywords field for backwards compatibility if present
    if "keywords" in post:
        doc["keywords"] = post["keywords"]

    return doc


def find_existing_document(collection_ref, post_id):
    """Find document by legacyId or externalId for upsert."""
    # Try legacyId first
    query = collection_ref.where('legacyId', '==', post_id).limit(1)
    docs = list(query.stream())
    if docs:
        return docs[0].reference

    # Try externalId
    query = collection_ref.where('externalId', '==', post_id).limit(1)
    docs = list(query.stream())
    if docs:
        return docs[0].reference

    return None


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
        description='Update social listening posts with scoring data',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('json_file', help='JSON file with scored posts (or "-" for stdin)')
    parser.add_argument('client_id', nargs='?', default=None,
                       help='Firestore client document ID (optional, reads from active_client.md)')
    parser.add_argument('--upsert', action='store_true',
                       help='Create posts if they do not exist (default: update only)')
    parser.add_argument('--min-score', type=float, default=0,
                       help='Only process posts with relevanceScore >= this value (default: 0)')

    args = parser.parse_args()

    # Get client_id from args or active_client.md
    client_id = args.client_id
    if not client_id:
        client_id = get_client_from_active_file()
        if not client_id:
            print("ERROR: client_id not provided and not found in inputs/active_client.md", file=sys.stderr)
            sys.exit(1)
        print(f"Using client_id from active_client.md: {client_id}", file=sys.stderr)

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
    print(f"Loading scored posts...", file=sys.stderr)
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
            posts = [doc.get('data', doc) for doc in data['documents']]
        else:
            posts = [data]

    print(f"Found {len(posts)} posts in file", file=sys.stderr)

    # Filter by minimum score
    if args.min_score > 0:
        posts = [p for p in posts if p.get('relevanceScore', 0) >= args.min_score]
        print(f"Filtered to {len(posts)} posts with relevanceScore >= {args.min_score}", file=sys.stderr)

    # Collection path for signals (new data structure)
    collection_path = f"clients/{client_id}/signals"
    collection_ref = get_collection_ref(db, collection_path)

    # Stats tracking
    updated_count = 0
    created_count = 0
    skipped_count = 0
    errors = []

    # Score distribution tracking
    score_distribution = {
        "high": 0,      # >= 7
        "medium": 0,    # >= 5, < 7
        "low": 0        # < 5
    }

    # Enrichment stats tracking (v2)
    enrichment_stats = {
        "with_sentiment": 0,
        "with_competitors": 0,
        "with_signal_tags": 0,
        "with_persona_match": 0,
        "with_matched_keywords": 0,
        "sentiment_breakdown": {"positive": 0, "negative": 0, "neutral": 0, "mixed": 0},
        "signal_tag_counts": {},
        "competitor_mentions": {}
    }

    print(f"\nProcessing posts...", file=sys.stderr)

    for i, post in enumerate(posts):
        post_id = post.get('postId', '')

        if not post_id:
            print(f"  [{i+1}] Skipping post without postId", file=sys.stderr)
            skipped_count += 1
            continue

        # Track score distribution
        score = post.get('relevanceScore', 0)
        if score >= 7:
            score_distribution["high"] += 1
        elif score >= 5:
            score_distribution["medium"] += 1
        else:
            score_distribution["low"] += 1

        # Track enrichment stats (v2)
        if post.get('sentiment'):
            enrichment_stats["with_sentiment"] += 1
            sentiment = post.get('sentiment', '').lower()
            if sentiment in enrichment_stats["sentiment_breakdown"]:
                enrichment_stats["sentiment_breakdown"][sentiment] += 1

        if post.get('competitorsMentioned'):
            enrichment_stats["with_competitors"] += 1
            for comp in post.get('competitorsMentioned', []):
                comp_name = comp.get('name', 'Unknown') if isinstance(comp, dict) else str(comp)
                enrichment_stats["competitor_mentions"][comp_name] = \
                    enrichment_stats["competitor_mentions"].get(comp_name, 0) + 1

        if post.get('signalTags'):
            enrichment_stats["with_signal_tags"] += 1
            for tag in post.get('signalTags', []):
                enrichment_stats["signal_tag_counts"][tag] = \
                    enrichment_stats["signal_tag_counts"].get(tag, 0) + 1

        if post.get('personaMatch'):
            enrichment_stats["with_persona_match"] += 1

        if post.get('matchedKeywords'):
            enrichment_stats["with_matched_keywords"] += 1

        try:
            # Try to find existing document by legacyId or externalId
            existing_ref = find_existing_document(collection_ref, post_id)

            if existing_ref:
                # Update existing document with scoring fields only
                scoring_data = extract_scoring_fields(post)
                existing_ref.update(scoring_data)
                updated_count += 1

                if (i + 1) % 50 == 0:
                    print(f"  [{i+1}/{len(posts)}] Updated {updated_count} posts...", file=sys.stderr)

            elif args.upsert:
                # Create new document with auto-generated ID and legacyId for lookup
                full_doc = build_full_document(post)
                full_doc['legacyId'] = post_id  # Store original ID for future lookups
                full_doc['externalId'] = post_id  # Also set externalId
                new_doc_ref = collection_ref.document()  # Auto-generate UUID
                new_doc_ref.set(full_doc)
                created_count += 1

                if (i + 1) % 50 == 0:
                    print(f"  [{i+1}/{len(posts)}] Created {created_count} new posts...", file=sys.stderr)

            else:
                # Skip - document doesn't exist and upsert not enabled
                skipped_count += 1
                if skipped_count <= 5:
                    print(f"  [{i+1}] Skipping {post_id} - not found (use --upsert to create)", file=sys.stderr)

        except Exception as e:
            error_msg = f"Error with post {post_id}: {str(e)}"
            print(f"  ERROR: {error_msg}", file=sys.stderr)
            errors.append(error_msg)

    # Summary
    print("\n" + "="*60, file=sys.stderr)
    print(f"Score update complete!", file=sys.stderr)
    print(f"  Updated: {updated_count}", file=sys.stderr)
    print(f"  Created: {created_count}", file=sys.stderr)
    print(f"  Skipped: {skipped_count}", file=sys.stderr)
    print(f"  Errors: {len(errors)}", file=sys.stderr)
    print(f"\nScore distribution:", file=sys.stderr)
    print(f"  High (>=7): {score_distribution['high']}", file=sys.stderr)
    print(f"  Medium (5-7): {score_distribution['medium']}", file=sys.stderr)
    print(f"  Low (<5): {score_distribution['low']}", file=sys.stderr)

    # Enrichment stats summary (v2)
    total_processed = updated_count + created_count
    print(f"\nEnrichment coverage:", file=sys.stderr)
    print(f"  With sentiment: {enrichment_stats['with_sentiment']}/{total_processed}", file=sys.stderr)
    print(f"  With competitor mentions: {enrichment_stats['with_competitors']}/{total_processed}", file=sys.stderr)
    print(f"  With signal tags: {enrichment_stats['with_signal_tags']}/{total_processed}", file=sys.stderr)
    print(f"  With persona match: {enrichment_stats['with_persona_match']}/{total_processed}", file=sys.stderr)
    print(f"  With matched keywords: {enrichment_stats['with_matched_keywords']}/{total_processed}", file=sys.stderr)

    if enrichment_stats['sentiment_breakdown']:
        print(f"\nSentiment breakdown:", file=sys.stderr)
        for sent, count in enrichment_stats['sentiment_breakdown'].items():
            if count > 0:
                print(f"  {sent}: {count}", file=sys.stderr)

    if enrichment_stats['competitor_mentions']:
        print(f"\nTop competitor mentions:", file=sys.stderr)
        sorted_comps = sorted(enrichment_stats['competitor_mentions'].items(),
                             key=lambda x: x[1], reverse=True)[:5]
        for comp, count in sorted_comps:
            print(f"  {comp}: {count}", file=sys.stderr)

    if enrichment_stats['signal_tag_counts']:
        print(f"\nTop signal tags:", file=sys.stderr)
        sorted_tags = sorted(enrichment_stats['signal_tag_counts'].items(),
                            key=lambda x: x[1], reverse=True)[:5]
        for tag, count in sorted_tags:
            print(f"  {tag}: {count}", file=sys.stderr)

    if errors:
        print("\nErrors encountered:", file=sys.stderr)
        for e in errors[:5]:
            print(f"  - {e}", file=sys.stderr)
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more", file=sys.stderr)

    # Output JSON result to stdout
    result = {
        'success': len(errors) == 0,
        'updated': updated_count,
        'created': created_count,
        'skipped': skipped_count,
        'errors': len(errors),
        'errorMessages': errors[:10],
        'collectionPath': collection_path,
        'clientId': client_id,
        'scoreDistribution': score_distribution,
        'enrichmentStats': enrichment_stats,
        'minScoreFilter': args.min_score,
        'upsertEnabled': args.upsert
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
