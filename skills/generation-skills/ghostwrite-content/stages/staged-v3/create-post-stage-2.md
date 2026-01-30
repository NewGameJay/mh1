# Create Post Stage 2: Template Selection & Outline

**Steps:** 5A-5B (Select Template, Create Outline)

---

## Input

Stage 1 output plus `CONTEXT_BUNDLE.templates` (prompts only, examples loaded on-demand).

---

## Output

```json
{
  "success": true,
  "stage": 2,
  "brief_path": "[from stage 1]",
  "brief_data": "[from stage 1]",
  "context": "[from stage 1]",
  "signals": "[from stage 1]",
  "template": {
    "id": "6",
    "name": "6. Culture Building & Core Values",
    "funnel_location": "TOFU",
    "prompt": "How do you think about building culture...",
    "example_text": "Culture isn't something you build...",
    "example_url": "https://linkedin.com/...",
    "selection_rationale": "Matches TOFU funnel and aligns with transformation/culture POV"
  },
  "outline": {
    "opening": {
      "hook": "Culture isn't defined. It's inherited.",
      "hook_length": 38,
      "rehook": "80% of company culture comes directly from the founder."
    },
    "body": {
      "main_insight": "Your job as a change agent is articulation, not architecture.",
      "supporting_points": ["Point 1", "Point 2"],
      "themes": "Founder DNA, transformation, change management"
    },
    "close": {
      "cta_type": "reflection",
      "cta_text": "The change agents who win are the ones who align with what already exists."
    }
  },
  "error": null
}
```

---

## Process

### Step 5A: Select Template

1. **Filter by funnel stage:** Match `templates.prompts` where `Funnel_Location == brief_data.funnel_stage`

2. **Match POV to template:** Look up full POV from `context.pov_data` using `brief_data.founder` + `brief_data.content_pillar`

3. **Score templates:** Select template that best expresses the POV

4. **Get example:** Read example for selected template ID from CSV:
   ```bash
   # Use Grep to find row: pattern="^{selectedId}," file="artifacts/linkedin-post-templates-examples.csv"
   ```

---

### Step 5B: Create Outline

**Opening:**
- `hook`: Start from `brief_data.hook`, keep UNDER 210 characters
- `rehook`: Bridge sentence that expands on hook (1-2 sentences)

**Body:**
- `main_insight`: Core message from `brief_data.pov`
- `supporting_points`: 2-3 points from `brief_data.angle` and `key_takeaway`
- `themes`: From `brief_data.typical_themes`

**Close:**
- `cta_type`: One of `question`, `reflection`, `action`, `share`
- `cta_text`: Specific closing line

---

## Validation (Must Pass Before Stage 3)

| Check | Requirement |
|-------|-------------|
| `template.id` | Non-empty string (e.g., "6") - **CRITICAL for Firestore** |
| `template.name` | Non-empty string (e.g., "Culture Building") - **CRITICAL for Firestore** |
| Template matches funnel | `template.funnel_location == brief_data.funnel_stage` |
| Example loaded | `template.example_text` non-empty |
| Hook length | Under 210 characters |
| Outline complete | All fields present (hook, rehook, main_insight, supporting_points, cta_type, cta_text) |
| Context preserved | All Stage 1 fields passed through (including `brief_data.pov`, `brief_data.hashtags`) |

**If any check fails, return error and do not proceed to Stage 3.**

---

## Error Handling

| Error | Action |
|-------|--------|
| No templates match funnel | Return `{success: false, error: "No templates for {funnel}"}` |
| Example CSV read fails | Continue without example, log warning |
| POV not found | Use `brief_data.pov` directly, log warning |
| Outline incomplete | Return `{success: false, error: "Incomplete outline"}` |
