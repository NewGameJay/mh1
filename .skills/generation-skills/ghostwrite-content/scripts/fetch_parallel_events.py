#!/usr/bin/env python3
"""
Fetch parallel monitor events (news, industry insights) for ghostwriting context.
Multi-client marketing platform - mh1-hq structure.

Usage:
    python fetch_parallel_events.py [client_id] [options]

Arguments:
    client_id: Firebase Client ID (or omit to read from active_client.md)
    --days: Maximum age of events in days (default: 14)
    --limit: Maximum events to return (default: 20)
    --output: Output file path (default: stdout)
    --format: Output format: json, markdown, or summary (default: json)
"""

import json
import sys
import os
import argparse
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


def parse_event_date(event_data):
    """Parse event date from various formats."""
    event_date = event_data.get("eventDate")

    if event_date is None:
        return None

    if hasattr(event_date, 'isoformat'):
        return event_date

    if isinstance(event_date, str):
        try:
            return datetime.fromisoformat(event_date.replace('Z', '+00:00'))
        except ValueError:
            try:
                return datetime.strptime(event_date, "%Y-%m-%d")
            except ValueError:
                return None

    return None


def format_event_for_output(event_data):
    """Format a parallel event for output."""
    source_urls = event_data.get("sourceUrls", [])
    if isinstance(source_urls, str):
        source_urls = [u.strip() for u in source_urls.strip("[]").split(",") if u.strip()]

    event_date = event_data.get("eventDate")
    if hasattr(event_date, 'isoformat'):
        event_date_str = event_date.isoformat()
    elif isinstance(event_date, str):
        event_date_str = event_date
    else:
        event_date_str = None

    created_at = event_data.get("createdAt")
    if hasattr(created_at, 'isoformat'):
        created_at_str = created_at.isoformat()
    elif isinstance(created_at, str):
        created_at_str = created_at
    else:
        created_at_str = None

    return {
        "id": event_data.get("id"),
        "output": event_data.get("output"),
        "eventDate": event_date_str,
        "sourceUrls": source_urls,
        "source": event_data.get("source"),
        "monitorId": event_data.get("monitorId"),
        "parallelEventGroupId": event_data.get("parallelEventGroupId"),
        "createdAt": created_at_str,
        "reviewed": event_data.get("reviewed", False),
        "notes": event_data.get("notes")
    }


def calculate_stats(events, days_filter):
    """Calculate statistics for the fetched events."""
    stats = {
        "totalEvents": len(events),
        "daysFilter": days_filter,
        "bySource": defaultdict(int),
        "byMonitor": defaultdict(int),
        "topTopics": {},
        "dateRange": {"earliest": None, "latest": None}
    }

    if not events:
        return stats

    event_dates = []

    for event in events:
        source = event.get("source", "unknown")
        monitor_id = event.get("monitorId", "unknown")

        stats["bySource"][source] += 1
        stats["byMonitor"][monitor_id] += 1

        event_date = event.get("eventDate")
        if event_date:
            event_dates.append(event_date)

    if event_dates:
        stats["dateRange"]["earliest"] = min(event_dates)
        stats["dateRange"]["latest"] = max(event_dates)

    stats["bySource"] = dict(stats["bySource"])
    stats["byMonitor"] = dict(stats["byMonitor"])

    return stats


def main():
    parser = argparse.ArgumentParser(description='Fetch parallel monitor events')
    parser.add_argument('client_id', nargs='?', help='Firebase Client ID')
    parser.add_argument('--client-name', default='Client')
    parser.add_argument('--days', type=int, default=14)
    parser.add_argument('--limit', type=int, default=20)
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

    cutoff_date = datetime.now(timezone.utc) - timedelta(days=args.days)
    print(f"Querying: clients/{CLIENT_ID}/parallelEvents", file=sys.stderr)
    print(f"Cutoff date: {cutoff_date.isoformat()}", file=sys.stderr)

    try:
        events_ref = db.collection("clients").document(CLIENT_ID).collection("parallelEvents")
        docs = events_ref.stream()

        all_events = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            all_events.append(data)

    except Exception as e:
        print(f"ERROR: Failed to query Firebase: {e}", file=sys.stderr)
        sys.exit(1)

    filtered_events = []
    for event in all_events:
        event_date = parse_event_date(event)
        if event_date is None:
            filtered_events.append(event)
        elif event_date >= cutoff_date:
            filtered_events.append(event)

    def get_sort_date(e):
        event_date = parse_event_date(e)
        if event_date:
            return event_date
        return datetime.min.replace(tzinfo=timezone.utc)

    filtered_events.sort(key=get_sort_date, reverse=True)
    limited_events = filtered_events[:args.limit]

    formatted_events = [format_event_for_output(e) for e in limited_events]
    stats = calculate_stats(formatted_events, args.days)

    output = {
        "success": True,
        "clientId": CLIENT_ID,
        "clientName": CLIENT_NAME,
        "query": {
            "days": args.days,
            "limit": args.limit,
            "cutoffDate": cutoff_date.isoformat()
        },
        "results": {
            "totalEventsInCollection": len(all_events),
            "eventsInDateRange": len(filtered_events),
            "eventsReturned": len(formatted_events)
        },
        "statistics": stats,
        "events": formatted_events
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
