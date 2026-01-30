---
name: ghostwrite-content
version: 1.1.0
description: |
  Generate authentic LinkedIn posts in the founder's voice using collected social listening data.
  Use when asked to 'ghostwrite posts', 'create content calendar', 'generate LinkedIn posts',
  'write founder content', or 'produce social content'.

category: content
author: mh1-engineering
created: 2024-01-01
updated: 2026-01-28
license: Proprietary
compatibility: [Firebase, Firestore]

# Stage configuration
stages:
  - id: "00-id-resolution"
    name: "ID Resolution"
    description: "Parse active_client.md or use params to resolve CLIENT_ID and FOUNDER_ID"
    required: true
    checkpoint: false

  - id: "01-context-loading"
    name: "Context Loading"
    description: "Load all context (local-first with Firestore fallback)"
    required: true
    checkpoint: true
    model: claude-haiku

  - id: "01.5-context-only"
    name: "Context-Only Mode"
    description: "Generate context snapshots (conditional on --context-only flag)"
    conditional: true
    exit_point: true

  - id: "01.75-topic-curation"
    name: "Topic Curation"
    description: "Invoke linkedin-topic-curator to analyze signals and select topics"
    required: true
    checkpoint: true
    model: claude-sonnet-4
    agent: linkedin-topic-curator

  - id: "02-template-selection"
    name: "Template Selection"
    description: "Match topics to LinkedIn templates (parallel batches)"
    required: true
    checkpoint: true
    model: claude-sonnet-4
    agent: linkedin-template-selector
    parallel_batches: 4

  - id: "03-ghostwriting"
    name: "Ghostwriting"
    description: "Generate posts in founder's voice (parallel batches)"
    required: true
    checkpoint: true
    model: claude-sonnet-4
    agent: linkedin-ghostwriter
    parallel_batches: 4
    incremental_save: true

  - id: "04-qa-review"
    name: "QA Review"
    description: "Validate posts for AI tells and quality issues"
    required: true
    checkpoint: true
    model: claude-haiku
    agent: linkedin-qa-reviewer

  - id: "05-calendar-compilation"
    name: "Calendar Compilation"
    description: "Create publishable content calendar deliverables"
    required: true
    checkpoint: true

  - id: "05.5-post-persistence"
    name: "Post Persistence"
    description: "Upload posts to Firestore"
    required: true
    checkpoint: true

  - id: "06-final-presentation"
    name: "Final Presentation"
    description: "Present completion summary with next steps"
    required: true

# Input/output definitions
inputs:
  - name: client_id
    type: string
    required: false
    description: "Firebase Client ID. If not provided, reads from inputs/active_client.md"

  - name: founder_id
    type: string
    required: true
    description: "Firebase founder document ID"

  - name: client_name
    type: string
    required: false
    description: "Client display name (optional, defaults to client_id)"

  - name: platform
    type: string
    required: false
    default: "linkedin"
    enum: ["linkedin", "twitter"]
    description: "Target social platform"

  - name: post_count
    type: integer
    required: false
    default: 20
    min: 1
    max: 50
    description: "Number of posts to generate"

  - name: min_relevance
    type: number
    required: false
    default: 5
    min: 1
    max: 10
    description: "Minimum relevance score for source posts"

  - name: max_source_posts
    type: integer
    required: false
    default: 25
    description: "Maximum source posts to include"

  - name: execution_mode
    type: string
    required: false
    default: "suggest"
    enum: ["suggest", "preview", "execute"]
    description: "Execution mode"

  - name: context_only
    type: boolean
    required: false
    default: false
    description: "Generate context snapshot files only (no posts generated)"

  - name: auto_topics
    type: boolean
    required: false
    default: false
    description: "Auto-select top-scoring topics without user interaction"

  - name: voice_contract
    type: object
    required: false
    schema: templates/voice-contracts/schema.json
    description: "Voice contract defining founder's writing style (optional, loaded from Firebase if not provided)"

outputs:
  - name: result
    type: object
    schema: templates/output-schema.json
    description: "Complete skill output with posts and metadata"

  - name: content_calendar
    type: object
    schema: templates/calendar-schema.json
    description: "Structured content calendar"

  - name: posts
    type: array
    schema: templates/post-schema.json
    description: "Generated posts array"

  - name: report
    type: markdown
    template: templates/completion-report.md
    description: "Human-readable completion report"

# Dependencies
requires_skills: []
requires_context:
  - voice-contract
  - brand
  - messaging
  - audience
  - strategy
requires_mcp:
  - firebase

requires_agents:
  - linkedin-topic-curator
  - linkedin-template-selector
  - linkedin-ghostwriter
  - linkedin-qa-reviewer

requires_resources:
  - inputs/_templates/linkedin-post-templates.csv

# Execution settings
timeout_minutes: 30
max_retries: 2
cost_estimate: "~$5.00 per 20 posts"

metadata:
  status: active
  estimated_runtime: "10-20min"
  max_cost: "$5.00"
  client_facing: true
  tags:
    - content
    - linkedin
    - ghostwriting
    - social-media

# Quality gates
quality_gates:
  - name: schema_validation
    type: schema
    schema: templates/output-schema.json

  - name: voice_authenticity
    type: threshold
    metric: voice_confidence_avg
    min_value: 7.0
    max_value: 10.0

  - name: qa_compliance
    type: checklist
    items:
      - "No em dashes in posts"
      - "No rhetorical questions (unless founder uses them)"
      - "No structures of 3"
      - "All citations verified"

  - name: completeness
    type: checklist
    items:
      - "All requested posts generated"
      - "Content calendar created"
      - "Posts persisted to Firestore"

allowed-tools: Read Write Shell CallMcpTool
---

# Ghostwrite Content Skill

Generate authentic LinkedIn posts in the founder's voice using collected social listening data.

## When to Use

Use this skill when you need to:
- Generate LinkedIn posts for a founder/executive
- Create a content calendar from social listening signals
- Ghostwrite authentic social media content
- Produce thought leadership content in a specific voice

## Overview

This skill transforms social listening data into publishable content calendars by:
1. Loading client context from Firebase (with local file fallback)
2. Fetching social signals, thought leaders, and industry events
3. Analyzing founder voice patterns from historical posts
4. Curating topics based on relevance and timing
5. Matching topics to proven templates
6. Generating posts in the founder's authentic voice
7. QA review for AI tells
8. Compiling into a publishable content calendar

## Prerequisites

- Client context documents (brand, messaging, audience, strategy) in local files or Firestore
- Founder posts collected in Firestore (minimum 10 posts for voice analysis)
- Social listening data collected (signals, thought leaders, events)
- Firebase MCP connection configured

## Voice Contract Integration

This skill uses voice contracts to ensure authentic content generation. The voice contract schema at `templates/voice-contracts/schema.json` defines:

- **Voice characteristics**: Tone, vocabulary level, sentence structure, formality
- **Signature phrases**: Expressions frequently used by the founder
- **Topics of expertise**: Subject areas they speak about authoritatively
- **Anti-patterns**: Things to NEVER do when writing in this voice
- **Example posts**: High-performing content to learn from

Voice contracts can be:
1. Passed as input parameter
2. Loaded from Firestore at `clients/{clientId}/founders/{founderId}`
3. Generated during context loading from founder posts

## Usage

### CLI

```bash
# Basic run (reads client from active_client.md)
python skills/ghostwrite-content/run.py --founder_id xyz123

# With explicit client
python skills/ghostwrite-content/run.py --client_id abc123 --founder_id xyz123 --post_count 30

# Context-only mode (debug)
python skills/ghostwrite-content/run.py --founder_id xyz123 --context_only

# Auto-select topics
python skills/ghostwrite-content/run.py --founder_id xyz123 --auto_topics
```

### Programmatic

```python
from skills.ghostwrite_content.run import run_ghostwrite_content

result = run_ghostwrite_content({
    "client_id": "abc123",
    "founder_id": "xyz789",
    "post_count": 20,
    "platform": "linkedin",
    "execution_mode": "suggest"
})
```

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `client_id` | No* | from active_client.md | Firebase Client ID |
| `founder_id` | Yes | - | Founder document ID |
| `platform` | No | linkedin | Target platform |
| `post_count` | No | 20 | Posts to generate |
| `min_relevance` | No | 5 | Min relevance score |
| `max_source_posts` | No | 25 | Max source posts |
| `execution_mode` | No | suggest | suggest/preview/execute |
| `context_only` | No | false | Generate context snapshots only |
| `auto_topics` | No | false | Auto-select topics |

*Required if not in active_client.md

## Execution Modes

| Mode | Description |
|------|-------------|
| **suggest** | Generate recommendations without changes |
| **preview** | Show what would be created/updated |
| **execute** | Create posts and persist to Firebase |

## Process

This skill executes in the following stages:

### Stage 0: ID Resolution
Parse `active_client.md` or use parameters to resolve CLIENT_ID and FOUNDER_ID.
- See [stages/00-id-resolution.md](./stages/00-id-resolution.md)

### Stage 1: Context Loading
Load all context using LOCAL-FIRST pattern with Firestore fallback.
- See [stages/01-context-loading.md](./stages/01-context-loading.md)

### Stage 1.5: Context-Only Mode (Conditional)
Generate context snapshots if `--context-only` flag is set.
- See [stages/01.5-context-only.md](./stages/01.5-context-only.md)

### Stage 1.75: Topic Curation
Invoke linkedin-topic-curator agent to analyze signals and select topics.
- See [stages/01.75-topic-curation.md](./stages/01.75-topic-curation.md)

### Stage 2: Template Selection
Match topics to LinkedIn templates using parallel batches.
- See [stages/02-template-selection.md](./stages/02-template-selection.md)

### Stage 3: Ghostwriting
Generate posts in founder's voice using parallel batches with incremental saves.
- See [stages/03-ghostwriting.md](./stages/03-ghostwriting.md)

### Stage 4: QA Review
Validate posts for AI tells and quality issues.
- See [stages/04-qa-review.md](./stages/04-qa-review.md)

### Stage 5: Calendar Compilation
Create publishable content calendar deliverables.
- See [stages/05-calendar-compilation.md](./stages/05-calendar-compilation.md)

### Stage 5.5: Post Persistence
Upload posts to Firestore with bi-directional references.
- See [stages/05.5-post-persistence.md](./stages/05.5-post-persistence.md)

### Stage 6: Final Presentation
Present completion summary with next steps.
- See [stages/06-final-presentation.md](./stages/06-final-presentation.md)

## Output

### File Structure

```
clients/{clientId}/campaigns/ghostwrite-{platform}-{date}/
├── README.md
├── CONTENT_CALENDAR_FINAL.md
├── CONTENT_CALENDAR_FINAL.json
├── final-{platform}-posts-{date}.json
├── checkpoint.json
├── source-data/
│   ├── source_posts.json
│   ├── thought_leader_posts.json
│   ├── parallel_events.json
│   ├── template-selections.json
│   └── context-snapshot.json
└── posts/
    ├── batch-1-posts.json
    └── ...
```

### Schemas

- Output schema: [templates/output-schema.json](./templates/output-schema.json)
- Post schema: [templates/post-schema.json](./templates/post-schema.json)
- Calendar schema: [templates/calendar-schema.json](./templates/calendar-schema.json)

## Quality Gates

Each stage has a blocking quality gate:

| Gate | Criteria |
|------|----------|
| 0->1 | CLIENT_ID and FOUNDER_ID resolved |
| 1->1.75 | 5+ source posts, context docs present, 10+ founder posts |
| 1.75->2 | selectedTopics returned, total posts +/-2 of target |
| 2->3 | template-selections.json exists, all scores >=6.0 |
| 3->4 | All posts generated, avg voice confidence >=7/10 |
| 4->5 | Zero critical QA violations, citations verified |
| 5->5.5 | CONTENT_CALENDAR_FINAL.json exists |
| 5.5->6 | Firebase upload successful |

## Context Loading Priority

Company context uses LOCAL-FIRST loading:

| Data Type | Priority | Path |
|-----------|----------|------|
| Brand | LOCAL -> Firebase | `clients/{clientId}/context/brand.md` |
| Messaging | LOCAL -> Firebase | `clients/{clientId}/context/messaging.md` |
| Audience | LOCAL -> Firebase | `clients/{clientId}/context/audience.md` |
| Strategy | LOCAL -> Firebase | `clients/{clientId}/context/strategy.md` |
| Competitive | LOCAL -> Firebase | `clients/{clientId}/context/competitive.md` |
| Founder posts | Firebase only | `founders/{founderId}/posts` |
| Signals | Firebase only | `signals` |
| Thought leaders | Firebase only | `thoughtLeaders/*/posts` |
| Parallel events | Firebase only | `parallelEvents/*` |

## Budget & Cost Tracking

- Estimated cost calculated based on post count before execution
- Budget check against tenant limits (daily/monthly)
- Actual cost tracked from token usage
- Uses Haiku for extraction tasks, Sonnet for synthesis

## Dependencies

### Agents (External)
- `linkedin-topic-curator` - agents/workers/linkedin-topic-curator.md
- `linkedin-template-selector` - agents/workers/linkedin-template-selector.md
- `linkedin-ghostwriter` - agents/workers/linkedin-ghostwriter.md
- `linkedin-qa-reviewer` - agents/workers/linkedin-qa-reviewer.md

### External Resources
- `inputs/_templates/linkedin-post-templates.csv` - 81 LinkedIn post templates

### Firebase Collections
- `clients/{clientId}/context/*` - Company context
- `clients/{clientId}/founders/{founderId}` - Founder profile
- `clients/{clientId}/founders/{founderId}/posts` - Founder posts
- `clients/{clientId}/signals` - Social listening signals
- `clients/{clientId}/thoughtLeaders/*` - Thought leader data
- `clients/{clientId}/parallelEvents/*` - Industry events
- `clients/{clientId}/posts/*` - Generated posts (output)

## Error Handling

| Error | Solution |
|-------|----------|
| Founder not found | Lists available founders, suggests founder-post-ingest |
| Insufficient posts (<5) | Suggests lower min_relevance or social-listening-collect |
| Insufficient founder posts (<10) | Suggests founder-post-ingest agent |
| Template selection failure | Uses fallback templates |
| QA failure after 2 attempts | Flags post for manual review |

## Release Policy

Output release is governed by evaluation score:
- **auto_deliver**: Score >=0.8, all dimensions >=0.6
- **auto_refine**: Score 0.6-0.8, no critical issues
- **human_review**: Score <0.6 or critical issues
- **blocked**: Score <0.4 or sensitive content detected

## Troubleshooting

### Common Issues

1. **Issue**: Missing voice contract
   **Solution**: Ensure founder posts are collected via founder-post-ingest, or provide voice_contract parameter

2. **Issue**: Low voice confidence scores
   **Solution**: Collect more founder posts (minimum 10, recommended 50+) for better pattern matching

3. **Issue**: QA failures for AI tells
   **Solution**: Review and update voice contract anti-patterns

4. **Issue**: Timeout during ghostwriting
   **Solution**: Reduce batch size or post count

## Related Skills

- [social-listening-collect](../social-listening-collect/SKILL.md) - Collect social listening data
- [founder-post-ingest](../founder-post-ingest/SKILL.md) - Collect founder posts for voice analysis
- [thought-leader-discover](../thought-leader-discover/SKILL.md) - Add thought leaders to track

## See Also

- [Stage files](./stages/) - Detailed stage instructions
- [Config files](./config/) - Customization options
- [Templates](./templates/) - Output format specifications
- [References](./references/) - Additional documentation
- [lib/evaluator.py](../../lib/evaluator.py) - Evaluation framework
- [lib/budget.py](../../lib/budget.py) - Budget management
