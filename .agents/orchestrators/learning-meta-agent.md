# Orchestrator Agent: Learning Meta-Agent

Version: v1.0.0  
Type: orchestrator  
Author: Josh / MH1  
Created: 2026-01-23

---

## Purpose

The Learning Meta-Agent orchestrates the knowledge acquisition pipeline. It schedules source ingestion, routes content to specialized agents, detects novelty, and maintains the knowledge base that powers all other agents.

---

## Capabilities

- Schedule and coordinate daily/weekly source ingestion
- Route content to vertical-specialized sub-agents
- Detect novelty vs existing knowledge
- Generate weekly innovation briefs
- Recommend skill and prompt updates

---

## Sub-agents (workers)

| Agent name           | Role                              | When invoked                |
|----------------------|-----------------------------------|-----------------------------|
| `source-fetcher`     | Fetch content from defined sources| On schedule or manual trigger|
| `classifier-agent`   | Tag content by vertical/topic     | After fetch                 |
| `summarizer-agent`   | Generate multi-level summaries    | After classification        |
| `novelty-detector`   | Compare to knowledge base         | After summarization         |
| `skill-curator`      | Convert insights to skill updates | When novelty score >= 0.7   |
| `brief-generator`    | Create weekly innovation brief    | Weekly (Fridays)            |

---

## Workflow pattern

```
┌─────────────────────────────────────────────────────────────┐
│  TRIGGER: Schedule (daily) or Manual                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Source fetching                                     │
│  Agent: source-fetcher                                       │
│  Action: Fetch new content from all configured sources       │
│  Output: Raw content items with metadata                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: Classification                                      │
│  Agent: classifier-agent                                     │
│  Action: Tag by vertical, topic, relevance                  │
│  Output: Classified content items                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3: Summarization                                       │
│  Agent: summarizer-agent                                     │
│  Action: Generate tl;dr, executive, and deep summaries      │
│  Output: Content with summaries                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 4: Novelty detection                                   │
│  Agent: novelty-detector                                     │
│  Action: Compare to vector store, score novelty             │
│  Output: Novelty scores + action recommendations            │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
    Novelty >= 0.7                   Novelty < 0.7
              │                               │
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│  Step 5a: Skill curation│     │  Step 5b: Store only    │
│  Agent: skill-curator   │     │  Action: Index in KB    │
│  Action: Generate skill │     │  No further action      │
│  update recommendations │     │                         │
└─────────────────────────┘     └─────────────────────────┘
              │                               │
              └───────────────┬───────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 6: Knowledge base update                               │
│  Action: Store all items in vector DB + metadata DB         │
│  Output: Updated knowledge base                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 7: Weekly synthesis (Fridays only)                     │
│  Agent: brief-generator                                      │
│  Action: Generate weekly innovation brief                   │
│  Output: Learning log in knowledge/learning-logs/           │
└─────────────────────────────────────────────────────────────┘
```

---

## Schedule

| Task                 | Frequency | Time        | Notes                    |
|----------------------|-----------|-------------|--------------------------|
| Full pipeline run    | Daily     | 6:00 AM UTC | All sources              |
| High-priority sources| 2x daily  | 6:00, 18:00 | Anthropic, Cursor only   |
| Weekly synthesis     | Weekly    | Fri 18:00   | Generate learning log    |

---

## Configuration

```yaml
orchestrator:
  model: claude-sonnet-4
  max_concurrent_workers: 5
  timeout_per_source: 60

workers:
  source-fetcher:
    model: claude-haiku
    timeout: 30
  classifier-agent:
    model: claude-haiku
    timeout: 15
  summarizer-agent:
    model: claude-sonnet-4
    timeout: 45
  novelty-detector:
    model: claude-sonnet-4
    timeout: 30
  skill-curator:
    model: claude-sonnet-4
    timeout: 60
  brief-generator:
    model: claude-sonnet-4
    timeout: 120

thresholds:
  novelty_high: 0.8
  novelty_medium: 0.6
  novelty_low: 0.4
  relevance_minimum: 0.3

storage:
  vector_db: pinecone
  metadata_db: postgresql
  document_store: s3
```

---

## Inputs

| Name            | Type     | Required | Description                      |
|-----------------|----------|----------|----------------------------------|
| `sources`       | array    | no       | Override source list             |
| `force_full`    | boolean  | no       | Force full fetch (ignore cache)  |
| `date_range`    | object   | no       | Override date filter             |
| `skip_synthesis`| boolean  | no       | Skip weekly synthesis            |

---

## Outputs

| Name            | Type     | Description                      |
|-----------------|----------|----------------------------------|
| `items_fetched` | integer  | Count of items fetched           |
| `items_novel`   | integer  | Count of novel items             |
| `skill_updates` | array    | Recommended skill updates        |
| `learning_log`  | string   | Path to learning log (if weekly) |
| `status`        | string   | success | partial | failed         |

---

## Telemetry

Log for each run:
- `run_id`: unique identifier
- `trigger`: schedule | manual
- `sources_checked`: count
- `items_fetched`: count
- `items_processed`: count
- `items_novel`: count
- `skill_updates_generated`: count
- `tokens_used`: total
- `duration_seconds`: total
- `errors`: list

---

## Manual invocation

```bash
# Run full pipeline
claude /learning-pipeline

# Run for specific sources only
claude /learning-pipeline --sources "anthropic,cursor"

# Force full fetch (ignore cache)
claude /learning-pipeline --force-full

# Generate synthesis only (no fetch)
claude /learning-synthesis
```

---

## Error handling

| Error type           | Action                                      |
|----------------------|---------------------------------------------|
| Source fetch failed  | Log error, continue with other sources      |
| Classification failed| Use default vertical, continue             |
| Novelty detection    | Default to 0.5 score, flag for review       |
| Vector DB write      | Retry 3x, then queue for later             |
| Weekly synthesis     | Retry once, alert if failed                 |

---

## Monitoring

Set up alerts for:
- Pipeline didn't run in 24h
- Fetch success rate < 80%
- No novel items detected in 7 days
- Vector DB write failures
- Token usage > 2x baseline

---

## Notes

- First run will take longer (full fetch + embedding generation)
- Subsequent runs use incremental fetch (since last run)
- Vector DB should be warmed up before heavy querying
- Weekly synthesis requires at least 3 days of data
