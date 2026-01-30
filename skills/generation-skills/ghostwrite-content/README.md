# Ghostwrite Content - MH1-HQ

Generate authentic LinkedIn posts in the founder's voice from social listening data.

## Quick Start

```bash
# Basic usage (reads client from inputs/active_client.md)
python skills/ghostwrite-content/run.py --founder_id <founder_id>

# With explicit client
python skills/ghostwrite-content/run.py --client_id <client_id> --founder_id <founder_id> --post_count 30

# Context-only mode (debug)
python skills/ghostwrite-content/run.py --founder_id <founder_id> --context_only

# Auto-select topics (automated runs)
python skills/ghostwrite-content/run.py --founder_id <founder_id> --auto_topics
```

## Client Configuration

Client configuration is read from `inputs/active_client.md` at runtime, or passed explicitly:

```
client_id = <Firebase Client ID>
client_name = <Client Display Name>
founder_id = <Founder Document ID>
```

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--client_id` | No* | from active_client.md | Firebase Client ID |
| `--founder_id` | Yes | - | Founder document ID |
| `--platform` | No | linkedin | Target platform |
| `--post_count` | No | 20 | Posts to generate |
| `--min_relevance` | No | 5 | Min relevance score |
| `--max_source_posts` | No | 25 | Max source posts |
| `--execution_mode` | No | suggest | suggest/preview/execute |
| `--context_only` | No | false | Generate context snapshots only |
| `--auto_topics` | No | false | Auto-select topics |

*Required if not in active_client.md

## Prerequisites

1. Firebase credentials available (firebase-adminsdk*.json)
2. Founder has 10+ posts collected (run `founder-post-ingest` agent)
3. Social listening data collected (run `social-listening-collect`)
4. **Recommended**: Local context files at `clients/{clientId}/context/`

## Integration with mh1-hq lib

This skill integrates with:
- `lib/budget.py` - Per-tenant cost tracking and limits
- `lib/evaluator.py` - Quality gates and release policy
- `lib/telemetry.py` - Run logging and metrics
- `lib/runner.py` - Workflow execution with checkpointing

## Stage Pipeline

```
Stage 0: ID Resolution
Stage 1: Context Loading (LOCAL-FIRST)
    [Branch: --context_only?]
    ├── YES: Exit with context files
    └── NO: Continue
Stage 1.75: Topic Curation
Stage 2: Template Selection
Stage 3: Ghostwriting
Stage 4: QA Review
Stage 5: Calendar Compilation
Stage 5.5: Post Persistence
Stage 6: Final Presentation
```

## Output Structure

```
clients/{clientId}/campaigns/ghostwrite-{platform}-{date}/
├── README.md
├── CONTENT_CALENDAR_FINAL.md
├── CONTENT_CALENDAR_FINAL.json
├── final-{platform}-posts-{date}.json
├── source-data/
│   ├── source_posts.json
│   ├── thought_leader_posts.json
│   ├── parallel_events.json
│   └── template-selections.json
└── posts/
    └── batch-*.json
```

## Error Handling

| Error | Solution |
|-------|----------|
| Founder not found | Lists available founders, suggests founder-post-ingest |
| Insufficient posts (<5) | Suggests lower `--min_relevance` or social-listening-collect |
| Insufficient founder posts (<10) | Suggests founder-post-ingest agent |
| Template selection failure | Uses fallback templates |
| QA failure after 2 attempts | Flags post for manual review |

## See Also

- [SKILL.md](./SKILL.md) - Full skill documentation
- [Stage files](./stages/) - Detailed stage instructions
- [Config files](./config/) - Customization options
- [Templates](./templates/) - Output format specifications
