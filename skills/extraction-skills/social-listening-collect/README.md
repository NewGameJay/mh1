# Social Listening Collection Skill

This skill collects social media posts matching client keywords from LinkedIn, Twitter, and Reddit, then scores them for relevance to the client's audience.

## Quick Start

```bash
# Run collection (reads client from inputs/active_client.md)
./mh1 run skill social-listening-collect

# Or with custom keyword file
./mh1 run skill social-listening-collect --keyword-file path/to/keywords.md

# Platform-specific collection
./mh1 run skill social-listening-collect --platforms linkedin,twitter

# Using Python directly
python skills/social-listening-collect/run.py
```

## What It Does

1. **Reads client config** from `inputs/active_client.md`
2. **Loads keywords** from `clients/{client_id}/social-listening/keywords.md`
3. **Scrapes platforms** in parallel (LinkedIn, Twitter, Reddit)
4. **Scores posts** using competitive-intelligence-analyst agent
5. **Uploads to Firestore** with deduplication (increments existing totals)
6. **Generates report** with collection summary

## Client Configuration

The skill reads client details from `inputs/active_client.md`:

```markdown
CLIENT_ID = your_firebase_client_id
CLIENT_NAME = Your Client Name
DEFAULT_FOUNDER = founder_name
```

## Output Files

After collection, find results at:
- `clients/{client_id}/social-listening/collection-data/scored_posts_{timestamp}.json`
- `clients/{client_id}/social-listening/collection-data/collection_report.md`

## Firestore Path

```
clients/{CLIENT_ID}/signals/{signalId}
```

## Programmatic Usage

```python
from skills.social_listening_collect.run import run_social_listening

result = run_social_listening({
    "platforms": ["linkedin", "twitter"],
    "date_range": "past-week"
})

print(f"Collected {result['stats']['total_posts']} posts")
```
