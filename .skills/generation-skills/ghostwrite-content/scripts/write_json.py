#!/usr/bin/env python3
"""
Write JSON data to file with proper encoding and error handling.
MH1 Platform - Utility script.

Usage:
    python write_json.py <filepath> [json_string]
    
    If json_string is omitted, reads JSON from stdin.

Examples:
    python write_json.py "posts/batch-1.json" '{"posts": [...]}'
    echo '{"posts": [...]}' | python write_json.py "posts/batch-1.json"
"""

import json
import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


def main():
    if len(sys.argv) < 2:
        print("Usage: python write_json.py <filepath> [json_string]", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]

    if len(sys.argv) >= 3:
        json_str = sys.argv[2]
    else:
        json_str = sys.stdin.read()

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    dir_path = os.path.dirname(filepath)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    written_size = os.path.getsize(filepath)
    print(f"Written: {filepath} ({written_size} bytes)")

    print(json.dumps({
        "success": True,
        "filepath": filepath,
        "bytes": written_size
    }))


if __name__ == "__main__":
    main()
