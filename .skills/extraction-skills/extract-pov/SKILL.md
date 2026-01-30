---
name: extract-pov
description: |
  Parse POV markdown into structured JSON with content pillars and founder perspectives.
  Use when asked to 'extract POV', 'parse content pillars', 'convert POV to JSON'.
license: Proprietary
compatibility: []
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  estimated_runtime: "1-2min"
  client_facing: false
  tags:
    - extraction
    - pov
    - content-pillars
allowed-tools: Read Write Shell
---

# Extract POV to JSON

Parse the `context/pov.md` file into a structured JSON array for programmatic use.

## When to Use

Use this skill when you need to:
- Convert POV markdown documents to machine-readable JSON
- Extract content pillar mappings for content workflows
- Generate structured data linking founders, personas, and funnel stages
- Prepare POV data for programmatic content generation

## Purpose

Convert the markdown-formatted POV document into a JSON array where each entry represents a single content pillar with its associated founder, target persona, funnel stage, and POV statement.

## Input

Read file: `context/pov.md`

## Output

Write file: `context/pov.json`

## Output Schema

```json
[
  {
    "founder_name": "founder-slug",
    "content_pillar": "pillar_id",
    "target_persona": "persona_id",
    "funnel_stage": "TOFU | MOFU | BOFU",
    "pov": "The full POV statement text"
  }
]
```

**Important**: Each tuple must have exactly **one** target persona. If a content pillar lists multiple target personas, select only the **first** persona listed.

---

## Process

### Step 1: Read the POV Markdown

Read `context/pov.md` and parse its structure.

### Step 2: Identify Founders

Scan for H2 headers (`## Founder Name`) to identify each founder section.

Convert founder name to slug format:
- "Jane Doe" → "jane-doe"
- "John Smith" → "john-smith"
- General rule: lowercase, replace spaces with hyphens

### Step 3: Extract Content Pillars

For each founder section, find all H3 headers (`### Content Pillar N: Pillar Name`).

For each content pillar, extract:

**Content Pillar ID:**
- Look in the Quick Reference tables at the bottom of the file
- Find the row matching the pillar name to get the Pillar ID
- The ID is in backticks in the first column

**From each pillar section, extract:**
- `**Founder POV:**` → `pov` (the full paragraph after this label, until the next `**` field)
- `**Target Persona:**` → `target_persona` (extract the ID in backticks only)
- `**Funnel Stage:**` → `funnel_stage` (TOFU, MOFU, or BOFU)

### Step 4: Build JSON Array

Create an array of objects, one per content pillar:

```json
{
  "founder_name": "{slug from founder header}",
  "content_pillar": "{ID from quick reference table}",
  "target_persona": "{ID in backticks from Target Persona field}",
  "funnel_stage": "{value from Funnel Stage field}",
  "pov": "{full text from Founder POV field}"
}
```

### Step 5: Write Output

Write the JSON array to `context/pov.json` with proper formatting (2-space indent).

---

## Parsing Rules

### Founder Name Extraction
```
## Jane Doe - CEO & Co-Founder
     ^^^^^^^^ extract this part, before any dash or comma
```
Convert to slug: lowercase, spaces → hyphens

### Content Pillar ID Extraction
Find in Quick Reference table:
```markdown
| Pillar ID | Name | Target Persona | Funnel |
|-----------|------|----------------|--------|
| `ct_pattern_recognizer` | The Pattern Recognizer | ... | TOFU |
```
Extract the ID from the first column (in backticks).

### POV Text Extraction
```markdown
**Founder POV:** Marketing fundamentals haven't changed...
```
Extract everything after `**Founder POV:**` until the next `**` label or section break (`---`).

### Target Persona Extraction

The source file may use full persona names or IDs in backticks. Extract the persona identifier and convert to slug format if needed.

```markdown
**Target Personas:** Senior Marketing Director, VP of Growth
```

**Handling Multiple Personas:**
When multiple personas are listed (comma-separated), select only the **first persona** listed. Each content pillar should have exactly one target persona in the output.

**Persona Name to Slug Conversion:**
- Lowercase the entire string
- Replace spaces with hyphens
- Replace slashes with hyphens
- Example: "VP of Marketing" → `vp-of-marketing`

### Funnel Stage Extraction
```markdown
**Funnel Stage:** TOFU
                  ^^^^ extract this value
```

---

## Markdown Structure Expected

```markdown
# Document Title

---

## {Founder Name} - {Title}

### Content Pillar {N}: {Pillar Name}

**Expertise Area:** {description}

**Founder POV:** {POV paragraph}

**Target Persona:** `{persona_id}` ({persona name}) - {description}

**Funnel Stage:** {TOFU|MOFU|BOFU}

---

[More content pillars...]

---

## Quick Reference

### {Founder Name} Content Pillars

| Pillar ID | Name | Target Persona | Funnel |
|-----------|------|----------------|--------|
| `{pillar_id}` | {Pillar Name} | `{persona_id}` | {funnel} |
```

---

## Validation

After generating, verify:
- [ ] Each founder section produced entries
- [ ] All `content_pillar` values were resolved from the Quick Reference tables
- [ ] All `funnel_stage` values are TOFU, MOFU, or BOFU
- [ ] All `pov` values are non-empty strings
- [ ] All `target_persona` values are IDs (no parenthetical descriptions)
- [ ] JSON is valid and properly formatted

---

## Error Handling

| Issue | Action |
|-------|--------|
| Pillar not found in Quick Reference | Use slugified pillar name as fallback ID |
| Missing Founder POV field | Log warning, skip entry |
| Missing Target Persona ID | Use empty string, log warning |
| Missing Funnel Stage | Default to "TOFU", log warning |
