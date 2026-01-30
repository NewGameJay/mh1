---
name: extract-founder-voice
description: |
  Transform a founder's historical post analysis into structured voice contract JSON.
  Use when asked to 'extract founder voice', 'create voice contract', 'analyze founder writing style'.
license: Proprietary
compatibility: []
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  estimated_runtime: "2-5min"
  client_facing: false
  tags:
    - extraction
    - voice
    - founder
allowed-tools: Read Write Shell
---

# Extract Founder Voice Skill

## When to Use

Use this skill when you need to:
- Extract structured voice data from a founder's historical post analysis
- Create a `voice_contract` for ghostwriting workflows
- Generate `founder_analysis` JSON for content pipelines
- Prepare voice rules for AI-assisted content creation

**Purpose:** Transform a founder's historical post analysis markdown into structured `founder_analysis` and `voice_contract` JSON objects that can be passed inline to subsequent ghostwriting stages.

---

## Input

| Input | Source | Description |
|-------|--------|-------------|
| `founder_slug` | Argument | Founder identifier (e.g., "jane-doe", "john-smith") |
| Analysis file | File system | `context/writing-analysis/{founder_slug}-historical-post-analysis.md` |

---

## Output

Returns two structured objects:

### 1. founder_analysis

```json
{
  "profile": {
    "name": "Jane Doe",
    "title": "Chief Marketing Officer",
    "company": "Acme Corp",
    "linkedinUrl": "https://www.linkedin.com/in/janedoe",
    "analysisDate": "2026-01-17",
    "postsAnalyzed": 9
  },
  "executiveSummary": "Jane Doe is a CMO-level executive with a distinctive, warm...",
  "contentThemes": [
    {
      "theme": "CMO Community",
      "description": "Events, networking, peer connections",
      "postCount": 4,
      "voiceNotes": ["Warm, grateful tone", "Heavy tagging", "Event-driven content"]
    }
  ],
  "engagementAnalysis": {
    "byPostType": [
      { "type": "Personal/Vulnerability", "avgReactions": 165, "avgComments": 49 },
      { "type": "Event/Community", "avgReactions": 50, "avgComments": 10 }
    ],
    "keyInsight": "Highest engagement comes from personal vulnerability combined with professional context"
  },
  "speakingVoiceInsights": {
    "naturalPhrases": ["AI fluent", "backend automations", "speed to action"],
    "voiceQualities": ["Diplomatic but direct", "Collaborative framing", "Practical over theoretical"]
  }
}
```

### 2. voice_contract

```json
{
  "version": "1.0",
  "founderId": "{firestore_id or slug}",
  "founderName": "Jane Doe",
  "extractedAt": "2026-01-19T12:00:00Z",
  "voiceRules": {
    "sentenceStructure": {
      "averageLength": 12,
      "openingStyle": "Bold statement opener",
      "paragraphPattern": "Short paragraphs, punchy sentences"
    },
    "vocabulary": {
      "register": "professional-casual",
      "contractions": true,
      "avoidList": ["dive into", "unlock", "leverage", "synergy", "rockstar"],
      "signaturePhrases": ["badass", "hive", "game changing", "I'd love to compare notes"]
    },
    "rhetoric": {
      "rhetoricalQuestions": false,
      "hookPattern": "Bold statement opener",
      "ctaStyle": "Compare notes / invitation to dialogue"
    }
  },
  "lengthProfile": {
    "sweetSpot": {
      "min": 300,
      "max": 800
    },
    "averageCharCount": 550,
    "distribution": {
      "short": { "percentage": 22, "charRange": "under 300" },
      "medium": { "percentage": 44, "charRange": "300-800" },
      "long": { "percentage": 33, "charRange": "800+" }
    }
  },
  "canonicalExamples": [
    {
      "type": "hook",
      "text": "Transformative badassery. 💃🏻🚀🔥",
      "why": "Bold statement opener with signature emoji",
      "engagement": { "likes": 101, "comments": 19 }
    },
    {
      "type": "full-post",
      "text": "My Dad disarmed live bombs for work...",
      "why": "Highest engagement - personal vulnerability with professional pivot",
      "engagement": { "likes": 165, "comments": 49 }
    },
    {
      "type": "cta",
      "text": "If you can relate, pls share your wisdom, rants, and questions. I know one truism for sure: it takes a village. 💃 👩‍👧‍👦 ❤️",
      "why": "Community-oriented close with signature emoji",
      "engagement": { "likes": 165, "comments": 49 }
    }
  ],
  "openingPatterns": [
    {
      "style": "Bold Statement Opener",
      "pattern": "2-5 words. Period. Sometimes with emoji.",
      "examples": ["Transformative badassery. 💃🏻🚀🔥", "Positioning. It's hard, essential, and game changing."],
      "frequency": "40%"
    },
    {
      "style": "Personal Hook Opener",
      "pattern": "Storytelling lead. Personal before professional.",
      "examples": ["My Dad disarmed live bombs for work.", "I'm a different person today than last Monday."],
      "frequency": "30%"
    }
  ],
  "emojiUsage": {
    "signatureEmoji": "💃",
    "vocabulary": {
      "celebration": ["💃", "🚀", "🔥"],
      "gratitude": ["❤️"],
      "professional": ["💡", "✔", "→"]
    },
    "placementRules": [
      "Opening: Single emoji to set tone",
      "Closing: Heart emoji with mentions",
      "Lists: Bullet points with 💡, ✔, →",
      "Never: Mid-sentence emoji spam"
    ]
  },
  "structuralPatterns": [
    {
      "name": "Statement → Story → Community Shoutout",
      "structure": ["Bold opening statement", "1-2 sentences of context/story", "Community mentions + gratitude", "Closing emoji/hashtags"],
      "useCase": "Event/networking posts"
    },
    {
      "name": "Personal Story → Professional Insight → Call to Engage",
      "structure": ["Personal hook - family/life story", "Extended narrative with emotional detail", "Pivot to professional relevance", "Call for community input"],
      "useCase": "Vulnerability/authenticity posts"
    }
  ],
  "antiPatterns": {
    "neverUse": [
      "em dashes (—)",
      "dive into / deep dive",
      "unlock / unlocking",
      "leverage (as verb)",
      "synergy",
      "rockstar",
      "touch base",
      "circle back",
      "let's unpack",
      "at the end of the day"
    ],
    "formattingToAvoid": [
      "Em dashes (—) - use regular dashes or periods",
      "Excessive hashtags - max 6, only at end",
      "Over-formatted posts - minimal bold, no headers",
      "Rhetorical questions in openers - she states, doesn't ask"
    ],
    "toneToAvoid": [
      "Overly promotional self-talk",
      "Humble-bragging",
      "Passive voice",
      "Hedging language ('I think maybe...')",
      "Generic platitudes without personal touch"
    ]
  },
  "hashtagStyle": {
    "placement": "Always at the end, never inline",
    "maxCount": 6,
    "format": "CamelCase (e.g., #B2BMarketing not #b2bmarketing)",
    "commonTags": ["#B2BMarketing", "#CMO", "#AIinMarketing", "#ModernCMO", "#MarketingLeadership", "#GTM"]
  },
  "taggingStyle": {
    "frequency": "EXTREMELY generous with @mentions",
    "patterns": [
      "Full names (first + last)",
      "Sometimes with title: 'guru Bob Wright'",
      "Often with relationship: 'Thank you Karina for inviting me'",
      "Grouped by context: 'Kudos and thank you 6sense!'"
    ],
    "specialPhrases": [
      "Kudos, [Name]",
      "Thank you [Name] for [specific thing]",
      "Loved seeing you [Name]"
    ]
  },
  "metadata": {
    "postsAnalyzed": 9,
    "confidenceScore": 0.92,
    "extractionMethod": "markdown-parsing"
  }
}
```

---

## Process

### Step 1: Read the Analysis File

```
Read: context/writing-analysis/{founder_slug}-historical-post-analysis.md
```

If file not found, return error.

### Step 2: Extract Profile Information

Parse the header section for:
- **Name**: From "**Author**:" line
- **LinkedIn URL**: From "**LinkedIn**:" line
- **Analysis Date**: From "**Analysis Date**:" line
- **Posts Analyzed**: From "**Posts Analyzed**:" line

### Step 3: Extract Executive Summary

Find "## Executive Summary" section and capture the full paragraph.

### Step 4: Extract Length Distribution (Section 1)

Parse the table in "## 1. Post Length Distribution":
- Extract short/medium/long percentages
- Extract character ranges
- Calculate average character count

### Step 5: Extract Opening Patterns (Section 2)

Parse "## 2. Opening Sentence Patterns" for:
- Style names (Style A, Style B, etc.)
- Pattern descriptions
- Example opening sentences
- Frequency/usage notes

### Step 6: Extract Signature Phrases (Section 3)

Parse "## 3. Signature Phrases & Vocabulary":
- Words used frequently (from table)
- Phrases they love (from bullet list)
- Marketing/business jargon used

### Step 7: Extract Anti-Patterns (Section 4)

Parse "## 4. Words & Patterns to AVOID":
- Never use words/phrases
- Formatting to avoid
- Tone to avoid

### Step 8: Extract Emoji Usage (Section 5)

Parse "## 5. Emoji Usage":
- Emoji vocabulary table
- Placement rules
- Signature emoji identification

### Step 9: Extract Structural Patterns (Section 6)

Parse "## 6. Structural Patterns":
- Pattern names
- Structure templates
- Use cases

### Step 10: Extract Content Themes (Section 9)

Parse "## 9. Content Themes":
- Theme names and descriptions
- Post counts per theme
- Voice notes for each theme

### Step 11: Extract Canonical Examples (Section 11)

Parse "## 11. Example Posts for Voice Matching":
- High-performing posts with engagement numbers
- Hook examples
- CTA examples
- Full post examples

### Step 12: Extract Speaking Voice Insights (Section 13)

If present, parse "## 13. Speaking Voice Insights":
- Natural phrases from conversation
- Voice quality notes

### Step 13: Assemble Outputs

Combine extracted data into the two output structures:
- `founder_analysis`: Profile + themes + engagement + speaking insights
- `voice_contract`: Rules + patterns + examples + anti-patterns

---

## Extraction Rules

### For Tables
1. Identify table headers (| header1 | header2 |)
2. Parse each row into object with header keys
3. Handle "N/A" or empty cells as null

### For Bullet Lists
1. Identify lines starting with "- " or "* "
2. Extract text after bullet
3. Handle nested bullets (indentation)

### For Quoted Examples
1. Find lines starting with "> "
2. Preserve multi-line quotes (consecutive > lines)
3. Extract engagement data if present in parentheses

### For Code Blocks
1. Find ``` markers
2. Extract content between markers
3. Parse as structured pattern template

---

## Error Handling

| Error | Action |
|-------|--------|
| File not found | Return error with file path |
| Section not found | Use empty array/object, continue |
| Parse error in table | Log warning, skip row, continue |
| No examples found | Set canonicalExamples to empty array |

---

## Output Format

Return JSON object with both structures:

```json
{
  "success": true,
  "founder_slug": "{founder_slug}",
  "founder_analysis": { /* full founder_analysis object */ },
  "voice_contract": { /* full voice_contract object */ },
  "extraction_stats": {
    "sectionsFound": 11,
    "examplesExtracted": 3,
    "patternsExtracted": 4,
    "antiPatternsExtracted": 15
  }
}
```

---

## Usage

This skill is called by Phase 0 (Context Preload) for each founder:

```
For each founder in --founder-distribution:
  1. Call extract-context skill with founder_slug
  2. Store founder_analysis in CONTEXT_BUNDLE.founders[slug].founder_analysis
  3. Store voice_contract in CONTEXT_BUNDLE.founders[slug].voice_contract
```

The structured outputs are then passed inline to Stage 3 (Ghostwriter) without needing to re-read or re-parse the markdown file.
