# Novelty Detection Prompt

Use this prompt to assess whether new content adds novel information to the knowledge base.

---

## System prompt

```
You are a knowledge curator assessing whether new content provides novel, actionable information compared to existing knowledge. Your goal is to identify truly new insights while filtering out repetitive or low-value content.
```

---

## User prompt template

```
Assess the novelty of the following content against the existing knowledge base.

## New content

Title: {title}
Source: {source}
Date: {date}
Content: {content}

## Relevant existing knowledge

{existing_knowledge}

## Assessment criteria

1. **Information novelty (40%)**: Does this contain information not already in the knowledge base?
   - New facts, methods, or tools
   - Updates to existing information (with new details)
   - Contradictions to existing beliefs

2. **Actionability (30%)**: Can this be turned into something useful?
   - Skill update or new skill
   - Prompt improvement
   - Workflow change
   - Playbook addition

3. **Relevance (20%)**: How relevant is this to MH1's offerings?
   - Agentic development
   - Marketing operations
   - Lifecycle / CRM
   - Content production

4. **Source quality (10%)**: How reliable is the source?
   - Official documentation: 1.0
   - Engineering blog from reputable company: 0.9
   - Industry publication: 0.8
   - Community post: 0.6
   - Unverified source: 0.4

## Output format

{
  "novelty_score": <float 0-1>,
  "is_novel": <boolean, true if score >= 0.6>,
  "breakdown": {
    "information_novelty": <float 0-1>,
    "actionability": <float 0-1>,
    "relevance": <float 0-1>,
    "source_quality": <float 0-1>
  },
  "novel_elements": [
    "<specific new information or insight>"
  ],
  "action_type": "skill_update|prompt_update|playbook|monitor|none",
  "action_description": "<what action to take, if any>",
  "verticals": ["agentic", "marketing", "lifecycle", "content"],
  "summary": "<2-3 sentence summary of the content>",
  "reasoning": "<brief explanation of the novelty assessment>"
}
```

---

## Thresholds

- **novelty_score >= 0.8**: High priority, immediate action
- **novelty_score 0.6-0.8**: Medium priority, queue for review
- **novelty_score 0.4-0.6**: Low priority, store but no action
- **novelty_score < 0.4**: Skip, likely duplicate or irrelevant

---

## Example

**Input:**
```
Title: "Claude Code now supports slash commands for skill invocation"
Source: Anthropic engineering blog
Date: 2026-01-20
Content: "We've added slash command support in Claude Code. You can now invoke skills directly with /run-skill [name]. This enables faster workflow automation..."
```

**Existing knowledge:**
```
- Claude Code supports skills via SKILL.md files (ingested 2025-10-01)
- Skills can be composed for complex workflows (ingested 2025-11-15)
```

**Output:**
```json
{
  "novelty_score": 0.85,
  "is_novel": true,
  "breakdown": {
    "information_novelty": 0.9,
    "actionability": 0.9,
    "relevance": 0.8,
    "source_quality": 0.9
  },
  "novel_elements": [
    "Slash command syntax for skill invocation (/run-skill)",
    "Native CLI integration for skills"
  ],
  "action_type": "skill_update",
  "action_description": "Update all skill documentation to include slash command invocation examples",
  "verticals": ["agentic"],
  "summary": "Claude Code now supports slash commands for invoking skills directly from the CLI, enabling faster workflow automation.",
  "reasoning": "This is genuinely new functionality not present in existing knowledge. High source quality (official blog). Directly actionable for our skill templates."
}
```

---

## Usage

```
/detect-novelty --content content.json --knowledge-base kb_context.json
```
