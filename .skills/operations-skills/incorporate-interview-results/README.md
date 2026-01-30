# Incorporate Interview Results

> Post-interview processing - updates research docs with validated information from client calls.

## Quick Start

```bash
# 1. Verify setup
python skills/incorporate-interview-results/verify_setup.py

# 2. Run skill with transcript
python skills/incorporate-interview-results/run.py \
  --client_id "abc123" \
  --interview_file "transcript.txt"
```

## What It Does

Processes interview transcripts and notes to update research documents by:
- Extracting key insights from interview content
- Validating or correcting research assumptions
- Filling identified research gaps
- Enriching founder voice data with real speech patterns
- Flagging conflicts between interview and research
- Generating an update summary document

This is the final step in the onboarding research workflow, producing validated research ready for content production.

## Prerequisites

- Python 3.8+
- Prior research skills completed (company, founder research)
- Interview transcript or notes
- Required packages: `pip install -r requirements.txt`

## Usage

### With Transcript File

```bash
python skills/incorporate-interview-results/run.py \
  --client_id "client_abc" \
  --interview_file "/path/to/transcript.txt" \
  --interviewee_name "John Smith"
```

### With Inline Transcript

```bash
python skills/incorporate-interview-results/run.py \
  --client_id "client_abc" \
  --interview_transcript "Full transcript text here..."
```

### Preview Mode (Validate Only)

```bash
python skills/incorporate-interview-results/run.py \
  --client_id "client_abc" \
  --interview_file "transcript.txt" \
  --validate_only
```

### Programmatic

```python
from skills.incorporate_interview_results.run import run_incorporate_interview_results

result = run_incorporate_interview_results({
    "client_id": "client_abc",
    "interview_transcript": "Full transcript...",
    "interviewee_name": "John Smith"
})

if result["status"] == "success":
    print(f"Insights extracted: {len(result['output']['extracted_insights'])}")
    print(f"Docs updated: {len(result['output']['docs_updated'])}")
    print(f"Conflicts: {len(result['output'].get('conflicts', []))}")
```

## Input

```json
{
  "client_id": "abc123",
  "interview_transcript": "Full transcript text...",
  "interviewee_name": "John Smith",
  "validate_only": false
}
```

Or with file:

```json
{
  "client_id": "abc123",
  "interview_file": "/path/to/transcript.txt",
  "interviewee_name": "John Smith"
}
```

## Output

```json
{
  "status": "success",
  "output": {
    "extracted_insights": [
      {
        "insight": "Primary audience is mid-market companies with 50-500 employees",
        "category": "audience",
        "confidence": "high",
        "source_quote": "We really focus on the mid-market..."
      }
    ],
    "assumptions_validated": [
      {
        "assumption": "Primary competitors are X and Y",
        "status": "confirmed",
        "notes": "Mentioned both as main competitors"
      }
    ],
    "gaps_filled": [
      {
        "gap": "Pricing strategy not documented",
        "resolution": "Value-based pricing with three tiers",
        "source_quote": "We use value-based pricing..."
      }
    ],
    "docs_updated": [
      "company-research.md",
      "founder-john-smith.md"
    ],
    "voice_updates": {
      "new_phrases": ["at the end of the day", "the reality is"],
      "confirmed_tone": ["conversational", "direct"],
      "words_analyzed": 8500
    },
    "conflicts": [],
    "update_summary_path": "clients/abc123/research/interview-results.md"
  },
  "_meta": {
    "insights_extracted": 12,
    "docs_updated": 2,
    "runtime_seconds": 35.2,
    "cost_usd": 0.55
  }
}
```

## Workflow Position

This skill is the final step in the onboarding research workflow:

```
research-company → research-competitors → research-founder
                           ↓
            generate-interview-questions
                           ↓
                   [Client Interview]
                           ↓
            incorporate-interview-results  ← You are here
                           ↓
               [Content Production Ready]
```

## Transcript Formats

The skill accepts various transcript formats:

**Plain text:**
```
John: Our main focus is the mid-market segment.
Interviewer: What does that mean specifically?
John: Companies with 50 to 500 employees...
```

**Notes format:**
```
## Audience
- Focus on mid-market (50-500 employees)
- Decision makers are VP-level

## Voice
- Prefers conversational tone
- Uses metaphors frequently
```

## Conflict Handling

When interview content contradicts research:

1. Conflict is flagged in output
2. Documents are NOT auto-updated
3. Requires human review
4. Both versions preserved for comparison

Example conflict:
```json
{
  "conflicts": [
    {
      "area": "target_audience",
      "research_value": "Enterprise companies",
      "interview_value": "Mid-market companies",
      "resolution_required": true
    }
  ]
}
```

## Output Files

The skill generates/updates:
- Updates existing research docs in `clients/{client_id}/research/`
- `clients/{client_id}/research/interview-results.md` - Summary of updates
- `clients/{client_id}/research/interview-results.json` - Structured data

## Related Documentation

- [SKILL.md](./SKILL.md) - Full specification
- [examples/](./examples/) - Usage examples

## Troubleshooting

**Error: No research documents found**
- Run research skills first (company, founder)
- Verify client_id is correct

**Warning: Insufficient interview content**
- Need at least 500 words of content
- Consider using full transcript instead of notes

**Error: Conflicts detected**
- Review conflicts in output
- Manually resolve before rerunning with `execute` mode

**Low voice confidence**
- Need more founder speech in transcript
- Ensure transcript captures founder's own words, not just interviewer

## Support

For issues, check:
1. `verify_setup.py` output
2. Telemetry logs in `telemetry/`
3. SKILL.md for expected behavior
