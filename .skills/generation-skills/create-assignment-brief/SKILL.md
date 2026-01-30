---
name: create-assignment-brief
description: |
  Transform signals into structured LinkedIn post assignment briefs.
  Use when asked to 'create assignment brief', 'create brief from signal',
  'generate LinkedIn brief', 'make a post brief', or 'turn signal into brief'.
license: Proprietary
compatibility: [Firebase]
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  estimated_runtime: "30-60s"
  client_facing: true
  tags:
    - briefs
    - content
    - linkedin
    - ghostwriting
    - signals
allowed-tools: Read Write Shell CallMcpTool
---

# Create Assignment Brief Agent

## When to Use

- Create LinkedIn post assignment briefs from content signals
- Transform curated signals into structured briefs
- Generate briefs aligned with content pillars and POVs
- Prepare content assignments for ghostwriting workflow
- Convert articles/links into actionable post briefs

---

Transform signal(s) into a structured LinkedIn post assignment brief.

## Important Constraints

**NEVER use WebFetch or WebSearch tools during brief creation.** All signal content must come from Firestore via the `get-signal-by-url.js` script. Do not fetch external URLs - the signal content is already stored in Firestore.

## Input

You will receive signal URL(s) in the prompt. Example:
- Single: `Create assignment brief from signal URL: https://example.com/article`
- Multiple: `Create assignment brief from signal URLs: https://example.com/article1, https://example.com/article2`

## Process

### Step 1: Get Context Summary

Read `context/context_summary.md`

If context/context_summary.md does not exist, invoke a task agent to run `skills/generate-context-summary/SKILL.md`.

This will create `context/context_summary.md`

### Step 2: Read Signal Content

Use ONLY Firestore to fetch signal content. Do NOT use WebFetch, WebSearch, or any browser tools to access the signal URL directly. The signal content is already stored in Firestore.**

Fetch signal content from Firestore using the signal URL(s):

**Single signal:**
```bash
node tools/get-signal-by-url.js "{signal-url}"
```

**Multiple signals (for grouped briefs):**
```bash
node tools/get-signal-by-url.js "{signal-url-1}" "{signal-url-2}" "{signal-url-3}"
```

For single signals, returns a JSON object. For multiple signals, returns:
```json
{
  "count": 3,
  "signals": [...],
  "notFound": ["url-if-any-missing"]
}
```

Each signal contains fields: `id`, `type`, `title`, `content`, `author`, `url`, `datePosted`, `status`, etc.

**If the signal is not found in Firestore:** Stop and report the error. Do NOT attempt to fetch the URL directly from the web.

Extract from each signal:
- Title and source
- Key insights and data points
- Quotable lines
- Core angle or story

### Step 3: Determine Angle of Brief

1. **Read `context/pov.json`** to get all content pillars as JSON array
2. **Select the best-fit content pillar** based on the signal's topic and insight
3. **Assign frontmatter values** from the selected pillar:
   - `founder`: The `founder_name` from the selected pillar entry
   - `content_pillar`: The `content_pillar` ID (e.g., `ct_pattern_recognizer`, `rn_ai_evangelist`)
   - `funnel_stage`: The `funnel_stage` value (TOFU, MOFU, or BOFU)
   - `target_persona`: The `target_persona` ID from the pillar
   - `pov`: The `pov` description from the pillar

**Important:** Each brief must align with exactly ONE content pillar. The pillar determines the founder, funnel stage, and primary persona.

### Step 4: Generate Brief ID

Generate a unique ID using today's date, title slug, and random hash:
- Format: `YYYY-MM-DD-{title-slug}-{random-hash}`
- Example: `2025-01-09-death-of-2021-sales-playbook-a3f2b1`

Use Python to generate:
```python
import datetime
import secrets
import re

title = {signal title}
slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:40]
brief_id = f"{datetime.date.today()}-{slug}-{secrets.token_hex(3)}"
```

### Step 5: Check for Duplicate Briefs

Check if any existing briefs already use the same signal(s):
```bash
node tools/check-duplicate-briefs.js "{signal-url-1}" "{signal-url-2}"
```

If duplicates are found:
- Script exits with code 1 and prints matching brief IDs
- Skip creation and report why

### Step 6: Read Full Context

Based on the founder selected in Step 3, read the following context documents:

**Core Context (always read):**
- `context/context_summary.json` - Quick reference for company positioning
- `context/pov.json` - All POVs and content pillars of founders
- `context/audience-persona.json` - Target persona details
- `context/writing-guideline.json` - Voice and style rules

**Founder-Specific Context:**

Based on the founder selected in Step 3, dynamically locate and read their context files:

1. **Founder info:** Search `context/founder-info/` for files matching `*{founder-name}*` (e.g., `founder-chris-toy.md`)
2. **Writing analysis:** Search `context/writing-analysis/` for files matching `*{founder-name}*` or `*{first-name}*` (e.g., `chris-post-analysis.md`)

Example for `chris-toy`:
```bash
ls context/founder-info/*chris* context/writing-analysis/*chris* 2>/dev/null
```

Read all matching files to understand the founder's background, expertise, and writing style patterns.

**Use this context to:**
- Match the founder's authentic voice and tone
- Reference their specific expertise and experiences
- Align with their content pillar's POV angle
- Ensure the brief fits the target persona's pain points

### Step 7: Generate the Brief

Create the assignment brief following this exact template:

```markdown
---
id: "{brief-id}"
title: "{compelling-title-for-the-post}"
status: draft
founder: "{founder_name}"
content_pillar: "{pillar-id}"
funnel_stage: "{TOFU|MOFU|BOFU}"
signals: ["{signal-url-1}", "{signal-url-2}"]
pov: "{pov-description}"
target_persona: "{persona-id-1}"
---

# Objective

One sentence: what outcome do we want from this post? Reference the content pillar's "What success looks like" section.

# Hook

The first 140 characters. Must stop the scroll and earn the "see more" click.

# Angle

The specific POV that makes this ours. Reference the content pillar's "POV angle" to ensure alignment with the founder's perspective on this topic. What's the tension, insight, or surprise?

# Key Takeaway

The single thing the reader should remember, believe, or do. Should align with the pillar's "What success looks like" outcomes.

# Typical Themes

Which themes from the content pillar's "Typical themes" section does this brief address?

# Pillar Guardrails

What should we avoid? Reference the pillar's "What we avoid in this pillar" section to ensure we don't violate the pillar's constraints.

# Context

Why this topic now? What signal triggered it?

# Visual Direction

What image/visual supports this? (authentic > stock, vertical preferred)

# Hashtags

3-5 relevant tags:

# Distribution Notes

- Post in comments: (links go here, not in post body)
- Tag: (relevant people/companies, if any)
- Best time: (if known)

# References

Source material or inspiration.
```

### Step 8: Save the Brief

**Generate filename:**
- Format: `{id}.md` (ID already contains title slug)
- Example: `2025-01-09-death-of-2021-sales-playbook-a3f2b1.md`

**Save locally:**
Use the Write tool to save the brief to `assignment-briefs/{filename}`

**Upload to Firestore:**
```bash
node tools/upload-briefs-to-firestore.js --files {filename}
```

This uploads the brief to `test-clients/{clientId}/modules/linkedin-ghostwriter/assignment-briefs/`

### Step 9: Update Signal Status

For each source signal, run:
```bash
node tools/update-signal-status.js "{signal-url}" --status used --brief-id "{brief-id}"
```

### Step 10: Report Success

Output a summary:
```
Assignment Brief Created
========================
ID: {brief-id}
Title: {title}
File: assignment-briefs/{filename}
Founder: {founder_name}
Content Pillar: {pillar-name}
Funnel stage: {TOFU|MOFU|BOFU}
POV: {pov-id}
Personas: {target-persona-id}
Source signals: {count} ({signal-titles})
```

## Quality Guidelines

**For the Hook:**
- Must work in first 140 characters (before "see more")
- Should create curiosity or tension
- Avoid clickbait - deliver on the promise

**For the Angle:**
- What makes this MarketerHire's POV?
- What's the contrarian or surprising take?
- How does this connect to hiring/talent themes?

**For the Key Takeaway:**
- One specific, memorable thing
- Actionable or belief-shifting
- Connected to MarketerHire's positioning

## Example Brief

```markdown
---
id: "2025-01-09-death-of-2021-sales-playbook-a3f2b1"
title: "The Death of the 2021 Sales Playbook"
status: draft
founder: "chris-toy"
content_pillar: "ct_pattern_recognizer"
funnel_stage: "TOFU"
signals: ["https://www.saastr.com/ai-and-the-death-of-the-2021-sales-process/"]
target_persona: ["scaling_saas_founder"]
---

# Objective

Position Chris as someone who has seen enough marketing shifts to recognize this pattern—building trust through demonstrated pattern recognition. (Aligns with pillar success: "Reader thinks: This person has seen enough to know what matters")

# Hook

Your 2021 sales playbook isn't underperforming. It's dead.

# Angle

While everyone's debating IF AI will change sales/marketing, the change already happened. Buyers complete research before you know they exist. The playbook that worked 3 years ago now actively hurts you. (POV: Marketing principles persist while channels accelerate—this is a structural shift, not a cyclical one)

# Key Takeaway

Speed and specialization beat size and process. The companies winning aren't hiring more SDRs—they're hiring specialists who can move at AI speed.

# Typical Themes

- Platform adoption curves and when to invest vs. wait
- Separating structural change from cyclical noise
- Historical parallels between past and present marketing shifts

# Pillar Guardrails

Avoid:
- Trend-chasing or breathless takes (ground this in historical context)
- Predictions without historical grounding (connect to past platform shifts Chris has witnessed)
- Sounding dismissive of companies still using 2021 playbooks

# Context

SaaStr article on AI killing 2021 sales processes—timely given end of year planning season.

# Visual Direction

Split image: old playbook (crossed out) vs new approach. Or simple text graphic with the hook.

# Hashtags

#SalesStrategy #B2BMarketing #AIinSales #GrowthMarketing #StartupLife

# Distribution Notes

- Post in comments: Link to original SaaStr article
- Tag: None
- Best time: Tuesday-Thursday, 8-10am

# References

- https://www.saastr.com/ai-and-the-death-of-the-2021-sales-process/
```
