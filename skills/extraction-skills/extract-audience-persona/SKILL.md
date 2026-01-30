---
name: extract-audience-persona
description: |
  Parse audience persona markdown into structured JSON with ICP, buyer personas, and messaging.
  Use when asked to 'extract personas', 'parse audience data', 'convert ICP to JSON'.
license: Proprietary
compatibility: []
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  estimated_runtime: "2-4min"
  client_facing: false
  tags:
    - extraction
    - personas
    - audience
    - icp
allowed-tools: Read Write Shell
---

# Extract Audience Persona to JSON

Parse the `context/audience-persona.md` file into a structured JSON object for programmatic use.

## When to Use

Use this skill when you need to:
- Convert audience persona documents to machine-readable JSON
- Extract ICP and buyer persona data for targeting workflows
- Parse buying committee and objection data for sales enablement
- Prepare persona-specific messaging for content automation

## Input

Read file: `context/audience-persona.md`

## Output

Write file: `context/audience-persona.json`

## Output Schema

```json
{
  "icp": {
    "company_characteristics": [
      {
        "attribute": "string",
        "ideal_profile": "string"
      }
    ],
    "buying_characteristics": [
      {
        "attribute": "string",
        "profile": "string"
      }
    ],
    "problem_fit": {
      "primary_pain_points": [
        {
          "name": "string",
          "description": "string"
        }
      ],
      "current_solutions": ["string", ...],
      "switching_triggers": ["string", ...]
    },
    "anti_icp": ["string", ...]
  },
  "buyer_personas": [
    {
      "persona_id": "string",
      "title": "string",
      "tagline": "string",
      "demographics": [
        {
          "attribute": "string",
          "value": "string"
        }
      ],
      "day_in_the_life": "string",
      "pain_points": [
        {
          "name": "string",
          "what_it_looks_like": "string",
          "impact": "string"
        }
      ],
      "goals": ["string", ...],
      "success_metrics": ["string", ...],
      "objections": [
        {
          "objection": "string",
          "response_strategy": "string"
        }
      ],
      "buying_triggers": {
        "internal": ["string", ...],
        "external": ["string", ...]
      },
      "information_sources": {
        "where_they_learn": "string",
        "who_they_trust": "string",
        "how_they_research": "string"
      },
      "champion_traits": ["string", ...]
    }
  ],
  "buying_committee": [
    {
      "role": "string",
      "persona": "string",
      "involvement": "string",
      "key_concern": "string"
    }
  ],
  "messaging_by_persona": [
    {
      "persona": "string",
      "lead_with": "string",
      "emphasize": "string",
      "proof_points": "string"
    }
  ]
}
```

---

## Expected Markdown Structure

```markdown
# Audience & Personas: {Company Name}

## Ideal Customer Profile (ICP)

### Company Characteristics

| Attribute | Ideal Profile |
|-----------|---------------|
| **{attribute}** | {value} |
...

### Buying Characteristics

| Attribute | Profile |
|-----------|---------|
| **{attribute}** | {value} |
...

### Problem Fit

**Primary Pain Points Addressed:**
1. **{Pain Point Name}**: {description}
...

**Current Solutions They Use:**
- {solution 1}
...

**Switching Triggers:**
- {trigger 1}
...

### Anti-ICP (Who NOT to target)

- **{segment}**: {reason}
...

---

## Buyer Persona {N}: {Persona Title}

> "{tagline quote}"

### Demographics

| Attribute | Value |
|-----------|-------|
| **{attribute}** | {value} |
...

### Day in the Life

{paragraph describing typical day}

### Pain Points

1. **{Pain Point Name}**
   - What it looks like: {description}
   - Impact: {impact}
...

### Goals

1. **{Goal Name}**: {description}
...

### Success Metrics (KPIs They Care About)

- {metric 1}
...

### Objections & Concerns

| Objection | Response Strategy |
|-----------|-------------------|
| "{objection}" | {response} |
...

### Buying Triggers

**Internal Triggers:**
- {trigger 1}
...

**External Triggers:**
- {trigger 1}
...

### Information Sources

- Where they learn: {sources}
- Who they trust: {trusted sources}
- How they research: {research process}

### What Makes Them a Champion

- {trait 1}
...

---

## Buying Committee Map

| Role | Persona | Involvement | Key Concern |
|------|---------|-------------|-------------|
| **{role}** | {persona} | {involvement} | "{concern}" |
...

### Handling the {Role} Blocker

**Objection**: "{objection}"

**Response Strategy**:
1. **{Strategy Name}**: {description}
...

---

## Messaging by Persona

### For {Persona}:
- **Lead with**: "{message}"
- **Emphasize**: {points}
- **Proof points**: {proof}

---
*{generation note}*
```

---

## Parsing Rules

### ICP Tables

```markdown
| Attribute | Ideal Profile |
|-----------|---------------|
| **Industry** | B2B SaaS, Fintech, eCommerce/DTC... |
```

Extract:
- `attribute`: Strip `**` markers
- `ideal_profile` or `profile`: Cell value

### Numbered Pain Points

```markdown
1. **AI Adoption Gap**: Using AI tools (ChatGPT, Jasper) but not seeing EBIT impact...
```

Extract:
- `name`: Bold text before colon
- `description`: Text after colon

### Persona Pain Points (Nested)

```markdown
1. **The AI Expectation Gap**
   - What it looks like: CEO/Board asking "what's our AI strategy?"...
   - Impact: Political pressure without resources...
```

Extract:
- `name`: Bold text
- `what_it_looks_like`: Text after "What it looks like:"
- `impact`: Text after "Impact:"

### Objections Table

```markdown
| Objection | Response Strategy |
|-----------|-------------------|
| "$30K/mo is more than my current agency spend" | Focus on consolidation... |
```

Extract as array of objects.

### Buying Triggers (Grouped)

```markdown
**Internal Triggers:**
- Just lost a key team member and can't backfill
- Q1/Q2 planning reveals budget for "AI initiatives"

**External Triggers:**
- Competitor launched AI-powered campaign
```

Extract into `internal` and `external` arrays.

### Information Sources (Labeled Bullets)

```markdown
- Where they learn: LinkedIn, CMO Coffee Talk...
- Who they trust: Peer CMOs/VPs, former colleagues...
- How they research: LinkedIn posts first, then direct outreach...
```

Extract into object with three keys.

### Anti-ICP Bullets

```markdown
- **Early-stage startups (<$5M ARR)**: Can't afford $30K/mo...
```

Extract full text including bold and description.

---

## Process

### Step 1: Extract ICP

From `## Ideal Customer Profile (ICP)`:
- Parse `### Company Characteristics` table → `icp.company_characteristics`
- Parse `### Buying Characteristics` table → `icp.buying_characteristics`
- From `### Problem Fit`:
  - Parse numbered list under "**Primary Pain Points Addressed:**" → `icp.problem_fit.primary_pain_points`
  - Parse bullets under "**Current Solutions They Use:**" → `icp.problem_fit.current_solutions`
  - Parse bullets under "**Switching Triggers:**" → `icp.problem_fit.switching_triggers`
- Parse `### Anti-ICP` bullets → `icp.anti_icp`

### Step 2: Extract Buyer Personas

For each `## Buyer Persona {N}: {Title}`:

Generate `persona_id` from title:
- Remove "The " prefix
- Convert to snake_case
- Example: "The Growth-Stage VP of Marketing" → `growth_stage_vp_of_marketing`

Extract:
- `tagline`: Text in blockquote under H2
- `demographics`: Parse table under `### Demographics`
- `day_in_the_life`: Paragraph under `### Day in the Life`
- `pain_points`: Parse nested list under `### Pain Points`
- `goals`: Parse numbered list under `### Goals`
- `success_metrics`: Parse bullets under `### Success Metrics`
- `objections`: Parse table under `### Objections & Concerns`
- `buying_triggers`: Parse grouped bullets under `### Buying Triggers`
- `information_sources`: Parse labeled bullets under `### Information Sources`
- `champion_traits`: Parse bullets under `### What Makes Them a Champion`

### Step 3: Extract Buying Committee

From `## Buying Committee Map`:
- Parse the main table → `buying_committee`

### Step 4: Extract Messaging by Persona

From `## Messaging by Persona`:
- Parse each `### For {Persona}:` section
- Extract `lead_with`, `emphasize`, `proof_points` from labeled bullets

### Step 5: Write Output

Write JSON to `context/audience-persona.json` with 2-space indent.

---

## Validation

After generating, verify:
- [ ] `icp.company_characteristics` has entries
- [ ] `buyer_personas` has at least 2 entries
- [ ] Each persona has `demographics`, `pain_points`, `goals`
- [ ] `buying_committee` has entries
- [ ] JSON is valid and properly formatted

---

## Error Handling

| Issue | Action |
|-------|--------|
| Section not found | Use empty array/object |
| Table malformed | Best-effort extraction |
| Missing persona section | Skip, continue with rest |
| Tagline missing | Use empty string |
