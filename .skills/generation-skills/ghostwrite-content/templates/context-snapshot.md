# Context Snapshot Template

This template defines the format for context window files generated in `--context-only` mode.

## Client Info (from active_client.md)

```
CLIENT_ID = {parsed from inputs/active_client.md}
CLIENT_NAME = {parsed from inputs/active_client.md}
FOLDER_NAME = {parsed from inputs/active_client.md}
FOUNDER = {resolved from founders subcollection}
```

## File Naming

| Agent | File Name |
|-------|-----------|
| Orchestrator | `00-ORCHESTRATOR_CONTEXT_{TIMESTAMP}.md` |
| Topic Curator | `01-TOPIC_CURATOR_CONTEXT_{TIMESTAMP}.md` |
| Template Selector | `02-TEMPLATE_SELECTOR_CONTEXT_{TIMESTAMP}.md` |
| Ghostwriter | `03-GHOSTWRITER_CONTEXT_{TIMESTAMP}.md` |

## Variables

| Variable | Description |
|----------|-------------|
| `{TIMESTAMP}` | File timestamp (YYYYMMDD_HHMMSS) |
| `{ISO_TIMESTAMP}` | Full ISO timestamp |
| `{FOUNDER_ID}` | Firestore founder document ID |
| `{FOUNDER_NAME}` | Human-readable founder name (default: Raaja Nemani) |
| `{PLATFORM}` | Target platform |
| `{POST_COUNT}` | Requested post count |
| `{MIN_RELEVANCE}` | Minimum relevance filter |
| `{MAX_SOURCE_POSTS}` | Maximum source posts |

## Orchestrator Context Template

```markdown
# Orchestrator Context Window

**Generated**: {ISO_TIMESTAMP}
**Client ID**: {CLIENT_ID}
**Client Name**: MH-1
**Founder ID**: {FOUNDER_ID}
**Founder Name**: {FOUNDER_NAME}
**Platform**: {PLATFORM}
**Post Count Requested**: {POST_COUNT}
**Min Relevance Filter**: {MIN_RELEVANCE}
**Max Source Posts**: {MAX_SOURCE_POSTS}
**Context-Only Mode**: true

---

## 1. Social Listening Posts

**Source**: `fetch_source_posts.py`
**Posts Loaded**: {SOURCE_POSTS_COUNT}
**Relevance Range**: {MIN_RELEVANCE_ACTUAL} to {MAX_RELEVANCE_ACTUAL}

### Statistics
| Platform | Count |
|----------|-------|
| LinkedIn | {LINKEDIN_COUNT} |
| Twitter | {TWITTER_COUNT} |
| Reddit | {REDDIT_COUNT} |

### Raw Data (source_posts.json)
```json
{SOURCE_POSTS_JSON}
```

---

## 2. Thought Leader Posts

**Source**: `fetch_thought_leader_posts.py`
**Leaders Loaded**: {THOUGHT_LEADERS_COUNT}
**Total Posts**: {TL_POSTS_COUNT}

### Statistics
| Tag | Count |
|-----|-------|
{TAG_TABLE}

### Raw Data (thought_leader_posts.json)
```json
{THOUGHT_LEADER_JSON}
```

---

## 3. Parallel Events

**Source**: `fetch_parallel_events.py`
**Events Loaded**: {EVENTS_COUNT}
**Date Range**: Last {EVENTS_DAYS} days

### Top Topics
{TOP_TOPICS_LIST}

### Raw Data (parallel_events.json)
```json
{PARALLEL_EVENTS_JSON}
```

---

## 4. Client Context (Local + Firestore)

### 4.1 Brand Context
**Source**: `clients/{clientId}/context/brand.md` (local) or `clients/{CLIENT_ID}/context/brand` (Firestore)
```json
{BRAND_JSON}
```

### 4.2 Messaging Context
**Source**: `clients/{clientId}/context/messaging.md` (local) or `clients/{CLIENT_ID}/context/messaging` (Firestore)
```json
{MESSAGING_JSON}
```

### 4.3 Audience Context
**Source**: `clients/{clientId}/context/audience.md` (local) or `clients/{CLIENT_ID}/context/audience` (Firestore)
```json
{AUDIENCE_JSON}
```

### 4.4 Strategy Context
**Source**: `clients/{clientId}/context/strategy.md` (local) or `clients/{CLIENT_ID}/context/strategy` (Firestore)
```json
{STRATEGY_JSON}
```

### 4.5 Competitive Context
**Source**: `clients/{clientId}/context/competitive.md` (local) or `clients/{CLIENT_ID}/context/competitive` (Firestore)
```json
{COMPETITIVE_JSON}
```

---

## 5. Founder Voice Data

### 5.1 Founder Profile
**Source**: `clients/{CLIENT_ID}/founderContent/{FOUNDER_ID}`
```json
{FOUNDER_PROFILE_JSON}
```

### 5.2 Founder Posts (Voice Examples)
**Source**: `clients/{CLIENT_ID}/founderContent/{FOUNDER_ID}/posts`
**Posts Loaded**: {FOUNDER_POSTS_COUNT}
```json
{FOUNDER_POSTS_JSON}
```

---

## 6. Case Studies

**Source**: `clients/{clientId}/case-studies/`

{IF CASE_STUDIES_EXIST}
### Available Case Studies
| File | Size |
|------|------|
{CASE_STUDIES_TABLE}

### Case Study Content
{CASE_STUDIES_CONTENT}
{ELSE}
**Status**: No case studies available
{END IF}

---

## 7. Data Distribution Summary

### Orchestrator Data Flow

| Data Type | Count | Passed To |
|-----------|-------|-----------|
| Social Listening Posts | {SOURCE_POSTS_COUNT} | Topic Curator |
| Thought Leader Posts | {TL_POSTS_COUNT} | Topic Curator |
| Parallel Events | {EVENTS_COUNT} | Topic Curator |
| Client Context (docs) | 5 | Topic Curator (moderate), Template Selector (full), Ghostwriter (full) |
| Founder Profile | 1 | Topic Curator (topThemes only), Ghostwriter (full) |
| Founder Posts | {FOUNDER_POSTS_COUNT} | Ghostwriter only |
| Case Studies | {CASE_STUDIES_COUNT} | Ghostwriter only |

### Context Isolation Preview

| Agent | Estimated Tokens | What It Receives |
|-------|------------------|------------------|
| Topic Curator | ~25K | TL posts, events, social posts, moderate context, founder topThemes |
| Template Selector | ~8K | Selected topics, templates CSV, full context |
| Ghostwriter | ~15K | Template selections, selected topics (summary only), founder voice, full context |
```

## Usage

Stage 1.5 (Context-Only Mode) uses this template to generate the orchestrator context file. Each agent generates its own context file using a similar structure.
