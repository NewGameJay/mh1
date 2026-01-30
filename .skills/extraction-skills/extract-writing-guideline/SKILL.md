---
name: extract-writing-guideline
description: |
  Parse writing guidelines markdown into structured JSON for brand voice enforcement.
  Use when asked to 'extract writing guidelines', 'parse style guide', 'convert brand voice to JSON'.
license: Proprietary
compatibility: []
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  estimated_runtime: "1-3min"
  client_facing: false
  tags:
    - extraction
    - writing-guidelines
    - brand-voice
allowed-tools: Read Write Shell
---

# Extract Writing Guideline to JSON

Parse the `context/writing-guideline.md` file into a structured JSON object for programmatic use.

## When to Use

Use this skill when you need to:
- Convert writing guidelines to machine-readable JSON format
- Extract voice/tone rules for content validation
- Parse style guides for programmatic brand voice enforcement
- Prepare vocabulary and formatting rules for AI writing assistants

## Input

Read file: `context/writing-guideline.md`

## Output

Write file: `context/writing-guideline.json`

## Output Schema

```json
{
  "voice_tone": {
    "characteristics": [
      {
        "dimension": "string",
        "guideline": "string",
        "example": "string"
      }
    ],
    "description": "string",
    "by_context": [
      {
        "context": "string",
        "guidance": "string"
      }
    ]
  },
  "vocabulary": {
    "preferred_terms": [
      {
        "use_this": "string",
        "instead_of": "string",
        "reason": "string"
      }
    ],
    "signature_phrases": [
      {
        "phrase": "string",
        "usage": "string"
      }
    ],
    "industry_terminology": [
      {
        "term": "string",
        "usage_guideline": "string"
      }
    ],
    "jargon_policy": "string",
    "words_to_avoid": [
      {
        "avoid": "string",
        "reason": "string",
        "use_instead": "string"
      }
    ]
  },
  "formatting": {
    "sentence_structure": {
      "typical_length": "string",
      "complexity": "string",
      "voice": "string"
    },
    "paragraph_structure": {
      "length": "string",
      "flow": "string"
    },
    "lists": {
      "when_to_use": "string",
      "format": "string",
      "parallel_structure": "string"
    },
    "headers": {
      "style": "string",
      "hierarchy": "string",
      "formatting": "string"
    },
    "opening_patterns": [
      {
        "name": "string",
        "description": "string",
        "example": "string"
      }
    ],
    "closing_patterns": [
      {
        "name": "string",
        "description": "string",
        "example": "string"
      }
    ],
    "visual_elements": {
      "emoji_usage": "string",
      "bold_italic": "string",
      "line_breaks": "string"
    }
  },
  "dos_and_donts": {
    "do": [
      {
        "rule": "string",
        "description": "string",
        "example": "string"
      }
    ],
    "dont": [
      {
        "rule": "string",
        "description": "string",
        "alternative": "string"
      }
    ]
  },
  "content_pillars": [
    {
      "name": "string",
      "description": "string",
      "key_messages": ["string", ...],
      "example_topics": ["string", ...]
    }
  ],
  "example_content": [
    {
      "title": "string",
      "style": "string",
      "content": "string",
      "why_it_works": "string"
    }
  ],
  "platform_guidelines": [
    {
      "platform": "string",
      "guidelines": {
        "key": "value"
      }
    }
  ],
  "quick_reference": {
    "sound_like": "string",
    "key_characteristics": ["string", ...],
    "avoid_sounding": "string",
    "when_in_doubt": "string"
  },
  "source_analysis": [
    {
      "name": "string",
      "role": "string",
      "contribution": "string"
    }
  ]
}
```

---

## Expected Markdown Structure

```markdown
# Writing Guidelines: {Company Name}

> {attribution note}

---

## Voice & Tone

### Voice Characteristics

| Dimension | Guideline | Example |
|-----------|-----------|---------|
| **{dimension}** | {guideline} | "{example}" |
...

### Voice Description

{paragraph 1 - primary description}

{paragraph 2 - additional details}

{paragraph 3 - overall impression}

### Tone by Context

| Context | Tone Guidance |
|---------|---------------|
| **{context}** | {guidance} |
...

---

## Vocabulary

### Preferred Terms

| Use This | Instead Of | Reason |
|----------|------------|--------|
| {term} | {avoid} | {reason} |
...

### Signature Phrases

- **"{phrase}"** — {usage guidance}
...

### Industry Terminology

| Term | Usage Guideline |
|------|-----------------|
| {term} | {guideline} |
...

### Jargon Policy

{policy paragraph}

### Words to Avoid

| Avoid | Reason | Use Instead |
|-------|--------|-------------|
| {word} | {reason} | {alternative} |
...

---

## Formatting Conventions

### Sentence Structure

- **Typical Length**: {guideline}
- **Complexity**: {guideline}
- **Voice**: {guideline}

### Paragraph Structure

- **Length**: {guideline}
- **Flow**: {guideline}

### Lists

- **When to Use**: {guideline}
- **Format**: {guideline}
- **Parallel Structure**: {guideline}

### Headers

- **Style**: {guideline}
- **Hierarchy**: {guideline}
- **Formatting**: {guideline}

### Opening Patterns

1. **{Pattern Name}**: {description}
   - Example: "{example}"
...

### Closing Patterns

1. **{Pattern Name}**: {description}
   - Example: "{example}"
...

### Visual Elements

- **Emoji Usage**: {guideline}
- **Formatting (Bold/Italic)**: {guideline}
- **Line Breaks**: {guideline}

---

## Do's and Don'ts

### Do

1. **{Rule Title}**
   - {description}
   - Example: "{example}"
...

### Don't

1. **{Rule Title}**
   - {description}
   - Instead: {alternative}
...

---

## Content Pillars

### Pillar {N}: {Pillar Name}

**Description**: {description}

**Key Messages**:
- {message 1}
- {message 2}
...

**Example Topics**:
- {topic 1}
- {topic 2}
...

---

## Example Content

### Example {N}: {Title} ({Style} Style)

{description}

> "{quoted example content}"

**Why it works**: {explanation}

---

## Platform-Specific Guidelines

### {Platform Name}

- **{aspect}**: {guideline}
...

---

## Quick Reference Card

### In 30 Seconds

**Sound like**: {description}

**Key characteristics**:
- {characteristic 1}
- {characteristic 2}
...

**Avoid sounding**: {description}

**When in doubt**: {guidance}

---

## Source Analysis

| Founder | Role | Primary Voice Contribution |
|---------|------|---------------------------|
| {name} | {role} | {contribution} |
...

---
*{generation note}*
```

---

## Parsing Rules

### Voice Characteristics Table

```markdown
| Dimension | Guideline | Example |
|-----------|-----------|---------|
| **Formality** | Professional-Conversational | "Marketing leaders are..." |
```

Extract into array of objects with `dimension`, `guideline`, `example`.

### Signature Phrases

```markdown
- **"Move the bar"** — Use when discussing how tools/AI elevate standards
```

Extract:
- `phrase`: Text in quotes after bold
- `usage`: Text after the em-dash

### Opening/Closing Patterns

```markdown
1. **The Tension Hook**: Start with a conflict, myth, or misconception
   - Example: "Marketers aren't worried about AI..."
```

Extract:
- `name`: Bold text (e.g., "The Tension Hook")
- `description`: Text after colon
- `example`: Text from nested bullet

### Content Pillars

```markdown
### Pillar 1: AI + Human Marketing Operations

**Description**: The intersection of AI technology...

**Key Messages**:
- AI raises the bar—it doesn't replace marketers
...

**Example Topics**:
- How {product} automates personalized landing pages
...
```

Extract:
- `name`: Text after "Pillar N: "
- `description`: Text after "**Description**:"
- `key_messages`: Array of bullets under "**Key Messages**:"
- `example_topics`: Array of bullets under "**Example Topics**:"

### Do's and Don'ts

```markdown
1. **Anchor in Tension**
   - Start with a common myth or fear and dismantle it with context
   - Example: "AI won't replace marketers..."
```

Extract:
- `rule`: Bold text
- `description`: First nested bullet
- `example` (for Do) or `alternative` (for Don't): Second nested bullet

---

## Process

### Step 1: Extract Voice & Tone

From `## Voice & Tone`:
- Parse `### Voice Characteristics` table → `voice_tone.characteristics`
- Combine `### Voice Description` paragraphs → `voice_tone.description`
- Parse `### Tone by Context` table → `voice_tone.by_context`

### Step 2: Extract Vocabulary

From `## Vocabulary`:
- Parse `### Preferred Terms` table → `vocabulary.preferred_terms`
- Parse `### Signature Phrases` bullets → `vocabulary.signature_phrases`
- Parse `### Industry Terminology` table → `vocabulary.industry_terminology`
- Extract `### Jargon Policy` paragraph → `vocabulary.jargon_policy`
- Parse `### Words to Avoid` table → `vocabulary.words_to_avoid`

### Step 3: Extract Formatting

From `## Formatting Conventions`:
- Parse each subsection's bullet list into corresponding object

### Step 4: Extract Do's and Don'ts

From `## Do's and Don'ts`:
- Parse numbered lists under `### Do` and `### Don't`

### Step 5: Extract Content Pillars

From `## Content Pillars`:
- Parse each `### Pillar N:` section

### Step 6: Extract Example Content

From `## Example Content`:
- Parse each `### Example N:` section

### Step 7: Extract Platform Guidelines

From `## Platform-Specific Guidelines`:
- Parse each platform's H3 section

### Step 8: Extract Quick Reference

From `## Quick Reference Card`:
- Parse the structured content

### Step 9: Extract Source Analysis

From `## Source Analysis`:
- Parse the table

### Step 10: Write Output

Write JSON to `context/writing-guideline.json` with 2-space indent.

---

## Validation

After generating, verify:
- [ ] `voice_tone.characteristics` has entries
- [ ] `vocabulary.words_to_avoid` has entries
- [ ] `content_pillars` has at least 3 pillars
- [ ] `dos_and_donts.do` and `dos_and_donts.dont` both have entries
- [ ] JSON is valid and properly formatted

---

## Error Handling

| Issue | Action |
|-------|--------|
| Section not found | Use empty array/object |
| Table malformed | Best-effort extraction |
| Missing subsection | Skip, continue with rest |
