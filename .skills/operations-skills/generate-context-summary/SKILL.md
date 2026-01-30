---
name: generate-context-summary
description: |
  Consolidate all onboarding documents into a single token-efficient context summary.
  Use when asked to 'generate context summary', 'consolidate onboarding docs', 'create context file'.
license: Proprietary
compatibility: []
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  estimated_runtime: "1-3min"
  client_facing: false
  tags:
    - generation
    - context
    - onboarding
allowed-tools: Read Write Shell
---

# Generate Context Summary Agent

Read all onboarding context files and generate a `context_summary.md` file for use as general context in content creation workflows.

## When to Use

Use this skill when you need to:
- Consolidate all onboarding research into a single reference file
- Create a token-efficient context document for content workflows
- Refresh the context summary after updating source documents
- Prepare a quick-reference document for content creators

## Purpose

This agent consolidates all onboarding documents into a single, token-efficient context file that can be referenced by other agents and workflows without needing to read multiple large files.

## Input

No input required. The agent reads from standard file locations.

## Process

### Step 1: Read All Context Files

Read the following files in order. Skip any files that don't exist (they may not be created for all clients).

**Unstructured Research Files:**
- `context/company-research.md` - Raw company research
- `context/competitor-research.md` - Competitor research and analysis
- `context/founder-info/*.md` - Founder background files
- `context/writing-analysis/*.md` - Founder writing analysis
- `context/tam-analysis.md` - Total addressable market analysis
- `context/testimonials.md` - Customer testimonials

**Structured Artifact Files:**
- `context/company-profile.md` - Structured company profile
- `context/audience-personas.md` - Target audience personas
- `context/team.md` - Team structure
- `context/pov.md` - Founder POVs, Content Pillars, Funnel Type, and Target Persona

### Step 2: Extract Key Information

From each file, extract the most important information:

**From Company Research:**
- Company name and tagline
- Key value propositions
- Target market
- Competitive differentiators

**From Company Profile:**
- Mission/vision
- Product/service offerings
- Pricing tiers (if available)
- How it works (process)

**From Audience Personas:**
- Each persona's ID, name, and title
- Core pain points
- Key metrics they care about
- Trust builders

**From Competitor Analysis:**
- Main competitors
- Competitive positioning
- Differentiation points

**From TAM Analysis:**
- Market size
- Target segments
- Growth opportunities

**From Testimonials:**
- Key themes from customer feedback
- Common pain points solved
- Success metrics mentioned

**From Founder Info:**
- Each founder's name and role
- Background highlights
- Areas of expertise
- Voice/style characteristics

**From POV:**
- Content Pillars ID's and names
- Core message
- Typical themes
- Guardrails

### Step 3: Generate Context Summary

Create a well-structured markdown file with the following sections:

```markdown
# Context Summary

**Generated:** {YYYY-MM-DD}
**Client:** {company-name}

---

## Company Overview

### Identity
- **Name:**
- **Tagline:**
- **Mission:**

### Value Proposition
{Key differentiators and why customers choose this company}

### Target Market
{Who they serve and why}

### How It Works
{Process overview}

### Pricing (if available)
{Tier summary}

---

## Audience Personas

### {Persona 1 Name} ({persona_id})
- **Title:**
- **Company Stage:**
- **Core Pain:**
- **Key Metric:**
- **Trust Builders:**

{Repeat for each persona}

---

## Brand Voice

### Voice Attributes
{Key voice characteristics}

### Tone Guidelines
{How we sound}

### Key Phrases
- **Use:**
- **Avoid:**

---

## Founders

### {Founder Name}
- **Role:**
- **Background:**
- **Expertise Areas:**
- **Voice Style:**

{Repeat for each founder}

---

## Content Pillars

### {Founder Name} Pillars

#### {Pillar Name} ({pillar_id})
- **Core Message:**
- **Themes:**
- **Guardrails:**

{Repeat for each pillar}

---

## Competitive Landscape

### Main Competitors
{List with brief descriptions}

### Our Differentiation
{What makes us different}

---

## Customer Insights

### What Customers Want
{Key desires from testimonials/reviews}

### Common Pain Points
{Problems we solve}

### Success Metrics
{How customers measure success with us}

### Key Quotes
{2-3 powerful customer quotes}

---

## Sales Insights

### Common Objections & Responses
{Key objection patterns}

### Winning Talking Points
{What resonates in sales conversations}

---

## Quick Reference

### Personas (IDs)
- {persona_id_1}: {one-line description}
- {persona_id_2}: {one-line description}

### Content Pillars (IDs)
- {pillar_id_1}: {founder} - {pillar name}
- {pillar_id_2}: {founder} - {pillar name}
```

### Step 4: Save the File

If `context/context_summary.md` already exists, replace it entirely with the newly generated content. This ensures the summary always reflects the current state of all source files.

Replace/write the generated summary to:
```
context/context_summary.md
```

### Step 5: Report Completion

Output a summary:
```
Context Summary Generated
=========================
File: context/context_summary.md
Generated: {date}

Files Read:
- {list of files successfully read}

Files Not Found (skipped):
- {list of files that didn't exist}

Sections Included:
- Company Overview
- Audience Personas ({count})
- Brand Voice
- Founders ({count})
- Content Pillars ({count})
- Competitive Landscape
- Customer Insights
- Sales Insights
- Quick Reference
```

## Quality Guidelines
**Make it scannable:**
- Use clear headers and bullet points
- Include IDs for easy reference
- Group related information

**Prioritize actionable info:**
- Focus on information needed for content creation
- Capture voice/tone essentials

**Handle missing files gracefully:**
- Skip sections for files that don't exist
- Note which files were missing in the report
- Don't fail the entire process for one missing file
