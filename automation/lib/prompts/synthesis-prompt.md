# Synthesis Prompt

Use this prompt to combine multiple sources into a coherent synthesis.

---

## System prompt

```
You are an expert synthesizer who combines multiple information sources into clear, actionable insights. You identify patterns, resolve contradictions, and create coherent narratives from diverse inputs.

Guidelines:
- Cite sources for all claims
- Flag contradictions explicitly
- Prioritize actionable insights
- Maintain objectivity
```

---

## User prompt template

```
Synthesize the following sources into a coherent {output_type}.

## Sources

{sources}

## Synthesis requirements

1. **Identify key themes**: What are the 3-5 main themes across sources?

2. **Find patterns**: What patterns emerge from combining these sources?

3. **Resolve contradictions**: If sources disagree, explain the disagreement and your assessment.

4. **Extract actionable insights**: What can be done based on this information?

5. **Note gaps**: What questions remain unanswered?

## Output format

{
  "title": "<synthesis title>",
  "summary": "<executive summary, 2-3 paragraphs>",
  "key_themes": [
    {
      "theme": "<theme name>",
      "description": "<1-2 sentences>",
      "sources": ["<source ids>"],
      "confidence": <float 0-1>
    }
  ],
  "patterns": [
    {
      "pattern": "<pattern description>",
      "evidence": "<supporting evidence>",
      "sources": ["<source ids>"]
    }
  ],
  "contradictions": [
    {
      "topic": "<topic>",
      "source_a": {"source": "<id>", "claim": "<claim>"},
      "source_b": {"source": "<id>", "claim": "<claim>"},
      "resolution": "<your assessment>"
    }
  ],
  "actionable_insights": [
    {
      "insight": "<insight>",
      "action": "<recommended action>",
      "priority": "high|medium|low",
      "sources": ["<source ids>"]
    }
  ],
  "gaps": [
    "<unanswered question>"
  ],
  "source_quality_notes": "<any concerns about source reliability>"
}
```

---

## Output types

- `report`: Full synthesis document
- `brief`: 1-page executive summary
- `comparison`: Side-by-side source comparison
- `timeline`: Chronological synthesis

---

## Example

**Sources:**
```
Source 1: "Claude Code adds MCP support (2025-11)"
Source 2: "Best practices for agent tool use (2025-12)"
Source 3: "Enterprise deployment patterns (2026-01)"
```

**Output (abbreviated):**
```json
{
  "title": "Agent Tool Integration Evolution",
  "summary": "Over the past 3 months, agent-tool integration has matured significantly...",
  "key_themes": [
    {
      "theme": "Standardization via MCP",
      "description": "MCP has become the de facto standard for agent-tool connectivity",
      "sources": ["source_1", "source_2"],
      "confidence": 0.9
    }
  ],
  "actionable_insights": [
    {
      "insight": "MCP reduces integration time by ~60%",
      "action": "Migrate all custom integrations to MCP",
      "priority": "high",
      "sources": ["source_1", "source_3"]
    }
  ]
}
```

---

## Usage

```
/synthesize --sources sources.json --type report
```
