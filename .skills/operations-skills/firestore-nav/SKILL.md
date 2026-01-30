---
name: firestore-nav
description: |
  Navigate Firestore collections and documents with path-based queries, depth control, and multiple output formats.
  Use when asked to 'browse Firestore', 'navigate collections', 'view document',
  'list subcollections', or 'explore database'.
license: Proprietary
compatibility: [Firebase, Firestore]
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  estimated_runtime: "<5s"
  max_cost: "$0.00"
  client_facing: false
  tags:
    - firebase
    - firestore
    - navigation
    - utility
allowed-tools: Read Shell
argument-hint: "<path> [--format json|markdown|table] [--depth N] [--fields f1,f2] [--limit N]"
---

# Firestore Navigation Skill

Navigate Firestore's hierarchical data structure with flexible path-based queries, depth control, field selection, and multiple output formats.

## When to Use

Use this skill when you need to:
- Browse Firestore collections and documents
- Navigate into subcollections
- View document data in various formats
- List documents with field filtering
- Explore the database structure

## Prerequisites

Ensure the `GOOGLE_APPLICATION_CREDENTIALS` environment variable is set to the path of your Firebase service account credentials JSON file.

## Instructions

### Step 1: Parse Arguments

Extract the path and options from `$ARGUMENTS`. Arguments format:

```
<path> [--format json|markdown|table] [--depth N] [--fields f1,f2] [--exclude f1,f2] [--limit N] [--expand]
```

**Options:**
| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--format` | json, markdown, table | json | Output format |
| `--depth` | 1-5 | 2 | How deep to expand nested objects |
| `--fields` | field1,field2 | all | Specific fields to include |
| `--exclude` | field1,field2 | none | Fields to exclude |
| `--limit` | 1-100 | 20 | Max documents for collections |
| `--expand` | flag | false | Expand nested objects inline |

**Path Types:**
| Path Type | Example | Behavior |
|-----------|---------|----------|
| Root | (empty) | List all root collections |
| Document | `clients/abc123` | Fetch single document |
| Collection | `clients/abc123/founderContent` | List documents (respects --limit) |
| Nested Doc | `clients/abc/socialListening/mentions` | Fetch nested document |
| Deep Collection | `clients/abc/socialListening/mentions/items` | List subcollection items |

**Path segment rule:** Odd segment count = collection (list), Even = document (get)

If no arguments provided, show usage:
```
Usage: /firestore-nav <path> [options]

Examples:
  /firestore-nav clients/{CLIENT_ID}
  /firestore-nav clients/{CLIENT_ID}/founderContent --format table
  /firestore-nav clients/{CLIENT_ID} --fields name,status
```

### Step 2: Install Dependencies (First Run Only)

Before the first run, ensure dependencies are installed:

```bash
cd "skills/firestore-nav" && npm install
```

### Step 3: Execute Navigation Script

Use the Bash tool to execute the script:

```bash
cd "skills/firestore-nav" && node firestore-nav.js {path} {options}
```

**Example commands:**
```bash
# Fetch a document
cd "skills/firestore-nav" && node firestore-nav.js clients/{CLIENT_ID}

# List a collection with limit
cd "skills/firestore-nav" && node firestore-nav.js clients/{CLIENT_ID}/founderContent --limit 5

# Format as markdown
cd "skills/firestore-nav" && node firestore-nav.js clients/{CLIENT_ID} --format markdown

# Select specific fields
cd "skills/firestore-nav" && node firestore-nav.js clients/{CLIENT_ID} --fields name,status,website

# Deep collection with table format
cd "skills/firestore-nav" && node firestore-nav.js clients/{CLIENT_ID}/socialListening/mentions/items --format table --limit 10
```

### Step 4: Handle Output

**JSON Output (default):**
```json
{
  "_meta": {
    "path": "clients/abc123",
    "type": "document",
    "exists": true,
    "id": "abc123",
    "subCollections": ["founderContent", "socialListening"]
  },
  "data": {
    "name": "{CLIENT_NAME}",
    "status": "active",
    "createdAt": "2026-01-19T10:30:00.000Z"
  }
}
```

**Markdown Output:**
```markdown
## Document: clients/abc123

**ID**: `abc123`
**Subcollections**: `founderContent`, `socialListening`

| Field | Value |
|-------|-------|
| name | {CLIENT_NAME} |
| status | active |
| createdAt | 2026-01-19 |
```

**Table Output (for collections):**
```
| id | name | status | createdAt |
|----|------|--------|-----------|
| founder1 | Chris Toy | active | 2026-01-15 |
| founder2 | Raaja Nemani | active | 2026-01-16 |

*Showing 2 of 2 documents*
```

### Step 5: Error Handling

**NOT_FOUND Error:**
```json
{
  "_meta": { "path": "clients/invalid", "type": "document", "exists": false },
  "error": "NOT_FOUND",
  "message": "Document not found: clients/invalid",
  "suggestion": "Check if the path is correct. Try listing the parent collection."
}
```

Response: Inform user the path doesn't exist and suggest listing the parent collection.

**FIREBASE_ERROR:**
```json
{
  "error": "FIREBASE_ERROR",
  "message": "Error description",
  "path": "clients/abc123"
}
```

Response: Check that:
- `GOOGLE_APPLICATION_CREDENTIALS` environment variable is set correctly
- Service account credentials file exists at the specified path
- Dependencies installed (`npm install` in skill directory)
- Network connection available

### Step 6: Format Response for User

Based on the `--format` option, present the data appropriately:

- **JSON**: Show the raw output with code block formatting
- **Markdown**: Display directly as formatted markdown
- **Table**: Display as a markdown table

Include helpful context:
- For documents: mention available subcollections
- For collections: mention total count vs. shown count
- For truncated results: suggest using `--limit` to see more

## Common Paths Reference

| Path | Description |
|------|-------------|
| `clients` | List all clients |
| `clients/{CLIENT_ID}` | {CLIENT_NAME} client document |
| `clients/{CLIENT_ID}/founderContent` | Founder profiles |
| `clients/{CLIENT_ID}/thoughtLeaders` | Thought leader profiles |
| `clients/{CLIENT_ID}/socialListening/mentions/items` | Social listening posts |

## Example Usage Patterns

**Browse subcollections:**
```
/firestore-nav clients/{CLIENT_ID}
```
→ Shows document data + lists available subcollections

**View collection as table:**
```
/firestore-nav clients/{CLIENT_ID}/thoughtLeaders --format table --limit 10
```
→ Shows thought leaders in table format

**Get specific fields:**
```
/firestore-nav clients/{CLIENT_ID} --fields name,displayName,website
```
→ Shows only requested fields

**Drill into deep data:**
```
/firestore-nav clients/{CLIENT_ID}/socialListening/mentions/items --format markdown --limit 5
```
→ Shows social listening items as markdown
