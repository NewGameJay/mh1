# Create Post Stage 3: Write the Post

**Steps:** 5C (Write the Post)

---

## Priority Order

1. **Voice authenticity** (sounds like the founder) - HIGHEST
2. **Content relevance** (addresses the topic) - HIGH
3. **Signal integration** (references industry context) - MEDIUM

---

## Input

Stage 2 output (includes file paths to voice data, NOT inline content).

---

## Output

```json
{
  "success": true,
  "stage": 3,
  "brief_path": "[from stage 2]",
  "brief_data": "[from stage 2]",
  "context": "[from stage 2]",
  "signals": "[from stage 2]",
  "template": "[from stage 2]",
  "outline": "[from stage 2]",
  "post_text": "The full LinkedIn post...",
  "word_count": 178,
  "hook_length": 74,
  "voice_confidence": 8,
  "voice_elements_used": {
    "opening_style": "Bold Statement",
    "signature_phrases": ["phrase1", "phrase2"],
    "structural_pattern": "...",
    "length_category": "medium"
  },
  "constraints_verified": {
    "hook_under_210": true,
    "no_em_dash": true,
    "no_anti_patterns": true,
    "signature_phrases_used": true,
    "opening_pattern_matched": true
  },
  "distribution_notes": {
    "hashtags": "#Tag1 #Tag2",
    "post_in_comments": "https://...",
    "best_time": "Tuesday-Thursday, 8-10am"
  },
  "error": null
}
```

---

## Process

### Step 1: Read Voice Files (MANDATORY)

**You MUST use the Read tool on BOTH files before writing anything.**

```
Read: context/writing-analysis/{founder}-founder-analysis.json
Read: context/writing-analysis/{founder}-voice-contract.json
```

If either file is missing, STOP and return error.

---

### Step 2: Apply Voice Contract Rules

From `voice-contract.json`, extract and follow:

| Element | Rule |
|---------|------|
| `openingPatterns` | Opening MUST match one of these patterns |
| `signaturePhrases` | Include 2+ VERBATIM in your post |
| `antiPatterns.neverUse` | NEVER use any of these words/phrases |
| `emojiUsage` | Follow placement rules |
| `lengthProfile` | Match typical distribution |

---

### Step 3: Study Example Posts

From `founder-analysis.json`, study `canonicalExamples` for:
- First sentence mechanics
- Paragraph rhythm
- Transition patterns
- Closing patterns

---

### Step 4: Write the Post

**Writing Rules:**
- Opening: Match founder's `openingPatterns`
- Voice: Use 2+ signature phrases VERBATIM
- Length: Match their distribution (most posts are medium)
- Closing: Use their CTA style
- Hashtags: End only, respect `maxCount`

**Content Rules:**
- No fabrication (don't invent stories/quotes not in context)
- TOFU: Thought leadership focus
- MOFU: Tie insight to what company enables
- BOFU: Clear product/solution connection
- Hook under 210 characters
- No URLs in post body (links go in comments)

---

### Step 5: Verify Anti-Patterns

Before outputting, scan post for everything in `antiPatterns.neverUse`. **If any violations found, rewrite those sections.**

---

### Step 6: Build Distribution Notes

**Populate `distribution_notes` from brief_data:**

```json
{
  "distribution_notes": {
    "hashtags": "{brief_data.hashtags}",
    "best_time": "Tuesday-Thursday, 8-10am",
    "post_in_comments": ["{signals[0].url}", "{signals[1].url}"]
  }
}
```

**Sources:**
- `hashtags`: From `brief_data.hashtags` (e.g., "#GPUCloud #AIInfrastructure")
- `best_time`: Default or from `brief_data.distribution_notes`
- `post_in_comments`: Signal URLs from `signals[]` array

---

## Validation (Must Pass Before Stage 4)

| Check | Requirement |
|-------|-------------|
| Voice files read | USED Read tool on both JSON files |
| Post text exists | Non-empty string |
| Word count | Between 50-400 |
| Hook length | Under 210 characters |
| No em dashes | Post contains no `—` characters |
| No anti-patterns | None of `antiPatterns.neverUse` appear |
| Signature phrases | 2+ used VERBATIM |
| Opening pattern matched | Matches one from voice contract |
| Voice confidence | Score >= 7 |
| `distribution_notes.hashtags` | Non-empty string from `brief_data.hashtags` |

**Data Passthrough Check (CRITICAL for Stage 4):**

These fields MUST be preserved in output for Stage 4 to write correct frontmatter:

| Field | Source | Must Exist |
|-------|--------|------------|
| `brief_data.id` | Stage 1 | YES (becomes `source_brief`) |
| `brief_data.pov` | Stage 1 | YES |
| `brief_data.hashtags` | Stage 1 | YES |
| `template.id` | Stage 2 | YES |
| `template.name` | Stage 2 | YES |
| `signals[]` | Stage 1 | YES (can be empty array) |

**If any check fails, fix the issue before proceeding to Stage 4.**

---

## Error Handling

| Error | Action |
|-------|--------|
| Voice file not found | Return `{success: false, error: "Cannot read {file}"}` |
| Voice JSON invalid | Return `{success: false, error: "Invalid JSON"}` |
| Anti-pattern found | Rewrite section, re-verify |
| Voice confidence < 7 | Return anyway with explanation |
