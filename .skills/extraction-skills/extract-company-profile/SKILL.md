---
name: extract-company-profile
description: |
  Parse company profile markdown into structured JSON with products, positioning, and market data.
  Use when asked to 'extract company profile', 'parse company data', 'convert company info to JSON'.
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
    - company-profile
    - market-position
allowed-tools: Read Write Shell
---

# Extract Company Profile to JSON

Parse the `context/company-profile.md` file into a structured JSON object for programmatic use.

## When to Use

Use this skill when you need to:
- Convert company profile documents to machine-readable JSON
- Extract product/service data for content workflows
- Parse market positioning and value proposition data
- Prepare company overview data for programmatic use

## Input

Read file: `context/company-profile.md`

## Output

Write file: `context/company-profile.json`

## Output Schema

```json
{
  "overview": {
    "company_name": "string",
    "tagline": "string",
    "founded": "string",
    "founders": "string",
    "headquarters": "string",
    "employees": "string",
    "funding": "string",
    "valuation": "string"
  },
  "mission": "string",
  "vision": "string",
  "value_proposition": {
    "summary": "string",
    "points": ["string", ...]
  },
  "products_services": [
    {
      "name": "string",
      "description": "string",
      "target_customer": "string",
      "key_features": ["string", ...],
      "pricing": "string"
    }
  ],
  "market_position": {
    "category": "string",
    "key_differentiators": ["string", ...],
    "notable_customers": "string"
  },
  "target_market": {
    "company_size": "string",
    "budget": "string",
    "industries": "string",
    "geography": "string"
  },
  "quick_facts": ["string", ...]
}
```

---

## Expected Markdown Structure

```markdown
# Company Profile: {Company Name}

## Overview

| Field | Value |
|-------|-------|
| **Company Name** | {value} |
| **Tagline** | {value} |
| **Founded** | {value} |
| **Founders** | {value} |
| **Headquarters** | {value} |
| **Employees** | {value} |
| **Funding** | {value} |
| **Valuation** | {value} |

## Mission

{mission statement paragraph}

## Vision

{vision statement paragraph}

## Value Proposition

{summary paragraph}
- **{benefit}** {description}
- **{benefit}** {description}
...

## Key Products & Services

### {Product Name}
- **Description**: {description}
- **Target Customer**: {target}
- **Key Features**:
  - {feature 1}
  - {feature 2}
  ...
- **Pricing**: {pricing}

## Market Position

- **Category**: {category}
- **Key Differentiators**:
  - {differentiator 1}
  - {differentiator 2}
  ...
- **Notable Customers**: {customers}

## Target Market

| Segment | Details |
|---------|---------|
| **Company Size** | {value} |
| **Budget** | {value} |
| **Industries** | {value} |
| **Geography** | {value} |

## Quick Facts

- {fact 1}
- {fact 2}
...
```

---

## Parsing Rules

### Table Parsing (Overview, Target Market)

Extract key-value pairs from markdown tables:

```markdown
| Field | Value |
|-------|-------|
| **Company Name** | Acme Corp |
```

- Field name: Strip `**` markers, convert to snake_case
- Value: Use as-is

### Bullet List with Bold Labels (Value Proposition)

```markdown
- **10x output** across marketing channels
```

- Extract full bullet text as array element

### Nested Bullet Lists (Key Features)

```markdown
- **Key Features**:
  - Complete AI marketing audit
  - Custom automation roadmap
```

- Parent bullet becomes the key
- Child bullets become array values

### Simple Bullet Lists (Quick Facts)

```markdown
- Positioned in the premium tier at $30k/mo
- Addresses the "adoption gap"
```

- Each bullet becomes an array element

---

## Process

### Step 1: Extract Overview Table

Parse the table under `## Overview` into `overview` object.

Field mapping:
- "Company Name" → `company_name`
- "Tagline" → `tagline`
- "Founded" → `founded`
- "Founders" → `founders`
- "Headquarters" → `headquarters`
- "Employees" → `employees`
- "Funding" → `funding`
- "Valuation" → `valuation`

### Step 2: Extract Mission & Vision

- `mission`: First paragraph under `## Mission`
- `vision`: First paragraph under `## Vision`

### Step 3: Extract Value Proposition

- `value_proposition.summary`: First paragraph under `## Value Proposition`
- `value_proposition.points`: All bullet points (full text including bold)

### Step 4: Extract Products & Services

For each H3 under `## Key Products & Services`:

- `name`: H3 header text
- `description`: Value after "**Description**:"
- `target_customer`: Value after "**Target Customer**:"
- `key_features`: Array of nested bullets under "**Key Features**:"
- `pricing`: Value after "**Pricing**:"

### Step 5: Extract Market Position

- `category`: Value after "**Category**:"
- `key_differentiators`: Array of bullets under "**Key Differentiators**:"
- `notable_customers`: Value after "**Notable Customers**:"

### Step 6: Extract Target Market Table

Parse the table under `## Target Market`:
- "Company Size" → `company_size`
- "Budget" → `budget`
- "Industries" → `industries`
- "Geography" → `geography`

### Step 7: Extract Quick Facts

- `quick_facts`: All bullet points under `## Quick Facts`

### Step 8: Write Output

Write JSON to `context/company-profile.json` with 2-space indent.

---

## Validation

After generating, verify:
- [ ] `overview.company_name` is populated
- [ ] `mission` and `vision` are non-empty strings
- [ ] `products_services` has at least one entry
- [ ] `target_market` has all four fields
- [ ] JSON is valid and properly formatted

---

## Error Handling

| Issue | Action |
|-------|--------|
| Section not found | Use empty string or array |
| Table malformed | Best-effort extraction |
| Missing field in table | Use empty string |
