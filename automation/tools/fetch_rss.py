#!/usr/bin/env python3
"""
Fetch posts from RSS sources and store them in the signals folder.
Idempotent - only adds new posts, skips duplicates.

Usage:
    python fetch_rss.py [--limit 50]
"""

import argparse
import hashlib
import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import feedparser

SIGNALS_DIR = Path(__file__).parent
SOURCES_FILE = SIGNALS_DIR / "sources.json"
INDEX_FILE = SIGNALS_DIR / "index.json"
CONTENT_DIR = SIGNALS_DIR / "content"


def load_sources():
    with open(SOURCES_FILE) as f:
        return json.load(f)


def load_index():
    if INDEX_FILE.exists():
        with open(INDEX_FILE) as f:
            return json.load(f)
    return {"posts": {}, "last_updated": None}


def save_index(index):
    index["last_updated"] = datetime.now().isoformat()
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)


def slugify(text, max_length=50):
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    text = text.strip("-")
    return text[:max_length]


def get_short_hash(url):
    """Generate short hash from URL."""
    return hashlib.sha256(url.encode()).hexdigest()[:6]


def get_source_domain(feed_url):
    """Extract domain from feed URL."""
    parsed = urlparse(feed_url)
    domain = parsed.netloc
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def parse_date(entry):
    """Extract date from feed entry."""
    for attr in ["published_parsed", "updated_parsed", "created_parsed"]:
        if hasattr(entry, attr) and getattr(entry, attr):
            try:
                return datetime(*getattr(entry, attr)[:6]).strftime("%Y-%m-%d")
            except (TypeError, ValueError):
                continue
    return datetime.now().strftime("%Y-%m-%d")


def get_content(entry):
    """Extract content from feed entry."""
    if hasattr(entry, "content") and entry.content:
        return entry.content[0].value
    if hasattr(entry, "summary"):
        return entry.summary
    if hasattr(entry, "description"):
        return entry.description
    return ""


def create_content_file(post_data, content):
    """Create markdown file with frontmatter."""
    escaped_title = post_data["title"].replace('"', '\\"')
    frontmatter = f"""---
id: {post_data["id"]}
type: "{post_data["type"]}"
author: "{post_data["author"]}"
title: "{escaped_title}"
date-posted: "{post_data["date_posted"]}"
date-added: "{post_data["date_added"]}"
url: "{post_data["url"]}"
status: "{post_data["status"]}"
used_in_assignment_brief: "{post_data["used_in_assignment_brief"]}"
---

{content}
"""
    filepath = CONTENT_DIR / post_data["file"]
    with open(filepath, "w") as f:
        f.write(frontmatter)


def fetch_feed(feed_url, limit):
    """Fetch and parse RSS feed."""
    try:
        feed = feedparser.parse(feed_url)
        if feed.bozo and not feed.entries:
            print(f"  Error parsing feed: {feed.bozo_exception}")
            return []
        return feed.entries[:limit]
    except Exception as e:
        print(f"  Error fetching feed: {e}")
        return []


def process_entry(entry, feed_url, index):
    """Process a single feed entry."""
    url = entry.get("link", "")
    if not url:
        return None

    # Check for duplicate
    if url in index["posts"]:
        return None

    title = entry.get("title", "Untitled")
    date_posted = parse_date(entry)
    date_added = datetime.now().strftime("%Y-%m-%d")
    source = get_source_domain(feed_url)
    content = get_content(entry)

    # Generate UUID for this signal
    signal_id = str(uuid.uuid4())

    # Generate filename
    slug = slugify(title)
    short_hash = get_short_hash(url)
    filename = f"{date_posted}-{slug}-{short_hash}.md"

    post_data = {
        "id": signal_id,
        "type": "web-sources-rss",
        "author": source,
        "title": title,
        "date_posted": date_posted,
        "date_added": date_added,
        "url": url,
        "status": "unused",
        "used_in_assignment_brief": "",
        "file": filename,
    }

    return post_data, content


def main():
    parser = argparse.ArgumentParser(description="Fetch RSS posts")
    parser.add_argument(
        "--limit", type=int, default=50, help="Max posts per feed (default: 50)"
    )
    args = parser.parse_args()

    # Ensure content directory exists
    CONTENT_DIR.mkdir(exist_ok=True)

    sources = load_sources()
    index = load_index()
    rss_feeds = sources.get("web-sources-rss", [])

    total_added = 0
    total_skipped = 0

    for feed_url in rss_feeds:
        print(f"\nFetching: {feed_url}")
        entries = fetch_feed(feed_url, args.limit)
        added = 0
        skipped = 0

        for entry in entries:
            result = process_entry(entry, feed_url, index)
            if result is None:
                skipped += 1
                continue

            post_data, content = result

            # Add to index
            index["posts"][post_data["id"]] = post_data

            # Create content file
            create_content_file(post_data, content)
            added += 1

        print(f"  Added: {added}, Skipped (duplicates): {skipped}")
        total_added += added
        total_skipped += skipped

    save_index(index)
    print(f"\nTotal: {total_added} added, {total_skipped} skipped")


if __name__ == "__main__":
    main()
