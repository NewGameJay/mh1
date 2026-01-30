---
name: social-listening-collect
version: 1.1.0
description: |
  Collect social media posts from LinkedIn, Twitter, and Reddit that match client keywords,
  score for ICP relevance, and store to Firestore with intelligent deduplication.
  Use when asked to 'collect social signals', 'run social listening', 'gather social posts',
  'scrape social media', or 'build signal database'.

category: automation
author: mh1-engineering
created: 2026-01-27
updated: 2026-01-28
license: Proprietary

# Stage configuration
stages:
  - id: "00-id-resolution"
    name: "ID Resolution"
    description: "Load client configuration from inputs/active_client.md"
    required: true
    duration: "instant"
  - id: "01-keyword-processing"
    name: "Keyword Processing"
    description: "Parse keyword file and build KEYWORDS_DATA structure"
    required: true
    checkpoint: true
    model: claude-haiku
    duration: "1-2min"
  - id: "02-social-scraping"
    name: "Social Media Scraping"
    description: "Execute platform scraping skills in parallel (LinkedIn, Twitter, Reddit)"
    checkpoint: true
    model: null
    duration: "3-8min"
    parallel: true
  - id: "03-scoring-enrichment"
    name: "Scoring & Enrichment"
    description: "Score posts for relevance using competitive-intelligence-analyst agent"
    checkpoint: true
    model: claude-sonnet-4
    duration: "5-10min"
  - id: "04-stats-extraction"
    name: "Stats Extraction"
    description: "Parse upload results and extract statistics for report"
    model: null
    duration: "instant"
  - id: "05-collection-report"
    name: "Collection Report"
    description: "Generate human-readable collection summary report"
    model: claude-sonnet-4
    duration: "1min"

# Input/output definitions
inputs:
  - name: client_id
    type: string
    required: false
    description: "Client identifier (reads from inputs/active_client.md if not provided)"
  - name: keyword_file
    type: string
    required: false
    description: "Path to keyword file (default: clients/{client_id}/social-listening/keywords.md)"
  - name: platforms
    type: array
    required: false
    default: ["linkedin", "twitter", "reddit"]
    description: "Platforms to scrape"
  - name: date_range
    type: string
    required: false
    default: "past-week"
    enum: ["past-24h", "past-week", "past-month"]
    description: "Time window for collection"

outputs:
  - name: scored_posts
    type: array
    schema: templates/output-schema.json
    description: "Posts with relevance scores and enrichment"
  - name: collection_report
    type: markdown
    template: templates/collection-report.md
    description: "Human-readable summary report"
  - name: stats
    type: object
    description: "Collection statistics"

# Dependencies
requires_skills:
  - linkedin-keyword-search
  - twitter-keyword-search
  - reddit-keyword-search
  - firebase-bulk-upload
requires_context: []
requires_mcp:
  - firebase
requires_agents:
  - competitive-intelligence-analyst

# Execution settings
timeout_minutes: 25
max_retries: 3
cost_estimate: "~$3.00 per run"

# Quality gates
quality_gates:
  - name: platform_data
    type: checklist
    items:
      - "At least one platform returned data"
      - "At least 10 posts collected total"
  - name: scoring_complete
    type: checklist
    items:
      - "All posts have relevanceScore assigned"
      - "All posts have sentiment assigned"
  - name: report_generated
    type: checklist
    items:
      - "Collection report generated"
      - "Report saved to output directory"

# Metadata
metadata:
  status: active
  estimated_runtime: "10-22min"
  max_cost: "$3.00"
  client_facing: false
  tags:
    - social-listening
    - data-collection
    - linkedin
    - twitter
    - reddit
    - firestore
  compatibility:
    - Firebase
    - Crustdata API
    - Twitter API
    - Reddit API
allowed-tools: Read Write Shell CallMcpTool
---

# Skill: social-listening-collect

## Overview

Collect social media posts from LinkedIn, Twitter, and Reddit that match client keywords, score for ICP relevance, and store to Firestore with intelligent deduplication. Designed for scheduled/periodic execution to build a persistent social listening database.

**Client configuration** is read from `inputs/active_client.md` at runtime.

## Prerequisites

- Client configured in `inputs/active_client.md`
- Keyword file at `clients/{client_id}/social-listening/keywords.md`
- Firebase MCP connection active
- API credentials configured for:
  - Crustdata (LinkedIn)
  - Twitter API v2
  - Reddit API (PRAW)

## Usage

```bash
# Run with defaults (reads client from active_client.md)
/run-skill social-listening-collect

# With custom keyword file
/run-skill social-listening-collect --keyword-file path/to/keywords.md

# Platform-specific
/run-skill social-listening-collect --platforms linkedin,twitter

# Custom date range
/run-skill social-listening-collect --date-range past-month

# Python programmatic
from skills.social_listening_collect.run import run_social_listening
result = run_social_listening({
    "platforms": ["linkedin", "twitter"],
    "date_range": "past-week"
})
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| client_id | string | No | from active_client.md | Client identifier |
| keyword_file | string | No | clients/{client_id}/social-listening/keywords.md | Path to keyword file |
| platforms | array | No | ["linkedin", "twitter", "reddit"] | Platforms to scrape |
| date_range | string | No | past-week | Time window (past-24h, past-week, past-month) |

## Process

This skill executes in the following stages:

### Stage 0: ID Resolution (instant)
Load client configuration from `inputs/active_client.md`. Extract CLIENT_ID and CLIENT_NAME.

**Details**: [stages/00-id-resolution.md](stages/00-id-resolution.md)

### Stage 1: Keyword Processing (1-2min)
Parse keyword file and build KEYWORDS_DATA structure with platform-specific queries.

**Details**: [stages/01-keyword-processing.md](stages/01-keyword-processing.md)

### Stage 2: Social Media Scraping (3-8min)
Execute platform scraping skills **in parallel** for LinkedIn, Twitter, and Reddit.

**Details**: [stages/02-social-scraping.md](stages/02-social-scraping.md)

### Stage 3: Scoring & Enrichment (5-10min)
Score posts for relevance using competitive-intelligence-analyst agent. Enrich with sentiment, ICP fit, and signal tags.

**Details**: [stages/03-scoring-enrichment.md](stages/03-scoring-enrichment.md)

### Stage 4: Stats Extraction (instant)
Parse upload results and extract statistics for the collection report.

**Details**: [stages/04-stats-extraction.md](stages/04-stats-extraction.md)

### Stage 5: Collection Report (1min)
Generate human-readable collection summary with aggregations and recommendations.

**Details**: [stages/05-collection-report.md](stages/05-collection-report.md)

## Configuration Reference

| File | Purpose |
|------|---------|
| `config/defaults.yaml` | Client-agnostic parameters, thresholds, paths |
| `config/defaults.json` | Legacy JSON config (deprecated, use YAML) |
| `config/firestore-schema.json` | Document structure, field definitions |
| `config/signal-tags.json` | Signal tag taxonomy for audience |

## Output

### Schema
See `templates/output-schema.json` for full schema.

### Output Directory Structure

```
clients/{client_id}/social-listening/
├── keywords.md                     # Input: Social listening keywords
└── collection-data/                # Output: Created during this skill
    ├── {platform}_posts.json       # Raw posts from each platform
    ├── all_posts_combined.json     # Combined posts before scoring
    ├── scored_posts_{timestamp}.json # Posts with relevance scores
    ├── firestore_upload.json       # Prepared upload payload
    ├── collection_report.md        # Human-readable summary
    └── {platform}_log.txt          # Collection logs
```

### Firestore Storage Path

Signals are stored with deduplication at:
```
clients/{CLIENT_ID}/signals/{signalId}
```

## Data Requirements

| Requirement | Minimum | Recommended | On Insufficient |
|-------------|---------|-------------|-----------------|
| Keywords | 3 | 10+ | warn_and_continue |
| Posts collected | 10 | 50+ | warn_and_continue |

## Context Handling

| Input size | Strategy | Model |
|------------|----------|-------|
| < 8K tokens | Inline (direct prompt) | claude-sonnet-4 |
| 8K-50K tokens | Chunked processing | Haiku for chunks, Sonnet for synthesis |
| > 50K tokens | Context offloading | Use ContextManager |

### Expected Input Size

- **Typical:** 50-200 posts, ~10K tokens
- **Maximum tested:** 500 posts, ~50K tokens
- **Strategy for large inputs:** chunked

## Quality Criteria

This skill's output passes if:
- [ ] At least one platform returned data
- [ ] At least 10 posts collected total
- [ ] All posts have relevanceScore assigned
- [ ] Collection report generated

## Troubleshooting

### Common Issues

1. **Issue**: Keyword file not found
   **Solution**: Create keyword file at `clients/{client_id}/social-listening/keywords.md` or provide custom path

2. **Issue**: No data collected
   **Solution**: Broaden keywords, extend date range, or check API credentials

3. **Issue**: Scoring agent timeout
   **Solution**: Reduce batch size in config/defaults.yaml or process in smaller chunks

4. **Issue**: Firebase upload fails
   **Solution**: Check Firebase MCP connection with `mh1 connections`

## Related Skills

- [linkedin-keyword-search](../linkedin-keyword-search/SKILL.md) - LinkedIn scraping
- [twitter-keyword-search](../twitter-keyword-search/SKILL.md) - Twitter/X scraping
- [reddit-keyword-search](../reddit-keyword-search/SKILL.md) - Reddit scraping
- [firebase-bulk-upload](../firebase-bulk-upload/SKILL.md) - Firestore batch upload

## Changelog

### v1.1.0 (2026-01-28)
- Migrated to new skill folder structure with YAML config
- Added stage configuration in frontmatter
- Created templates/output-schema.json for signal validation
- Added references/ folder for examples
- Updated documentation format

### v1.0.0 (2026-01-27)
- Ported from MH-1-Platform to mh1-hq
- Updated to use `inputs/active_client.md` for client configuration
- Added run.py with lib integration
