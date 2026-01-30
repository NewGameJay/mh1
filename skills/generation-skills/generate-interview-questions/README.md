# Generate Interview Questions

> Creates targeted interview questions based on research gaps - validates assumptions and fills information gaps.

## Quick Start

```bash
# 1. Verify setup
python skills/generate-interview-questions/verify_setup.py

# 2. Run skill (after running research skills)
python skills/generate-interview-questions/run.py \
  --client_id "abc123"
```

## What It Does

Generates targeted interview questions for client onboarding calls by:
- Loading all prior research (company, competitors, founders)
- Identifying information gaps in the research
- Finding assumptions that need validation
- Generating categorized, open-ended questions
- Creating a structured interview guide document

Best used after running company, competitor, and founder research skills.

## Prerequisites

- Python 3.8+
- Prior research skills completed (optional but recommended)
- Required packages: `pip install -r requirements.txt`

## Usage

### Basic (after research)

```bash
python skills/generate-interview-questions/run.py \
  --client_id "client_abc"
```

### With Options

```bash
python skills/generate-interview-questions/run.py \
  --client_id "client_abc" \
  --question_count 30 \
  --focus_areas "voice,strategy,audience" \
  --include_voice_questions
```

### Programmatic

```python
from skills.generate_interview_questions.run import run_generate_interview_questions

result = run_generate_interview_questions({
    "client_id": "client_abc",
    "question_count": 25
})

if result["status"] == "success":
    print(f"Questions generated: {len(result['output']['questions'])}")
    print(f"Research gaps: {len(result['output']['research_gaps'])}")
```

## Input

```json
{
  "client_id": "abc123",
  "founder_names": ["John Smith", "Jane Doe"],
  "focus_areas": ["voice", "strategy", "competitive"],
  "question_count": 25,
  "include_voice_questions": true
}
```

## Output

```json
{
  "status": "success",
  "output": {
    "questions": [
      {
        "id": 1,
        "category": "strategy",
        "question": "What are your top 3 business priorities for the next 6 months?",
        "purpose": "Understand strategic focus for content alignment",
        "gap_addressed": "Business priorities not publicly available",
        "priority": "high"
      }
    ],
    "research_gaps": [
      {"area": "pricing", "description": "Pricing strategy not publicly documented"}
    ],
    "assumptions_to_validate": [
      {"assumption": "Primary audience is mid-market companies", "source": "company-research"}
    ],
    "interview_guide_path": "clients/abc123/research/interview-questions.md"
  },
  "_meta": {
    "questions_generated": 25,
    "research_docs_loaded": 4,
    "runtime_seconds": 18.5,
    "cost_usd": 0.25
  }
}
```

## Question Categories

Questions are organized into categories:

| Category | Description |
|----------|-------------|
| `strategy` | Business goals, priorities, direction |
| `audience` | Target customers, ICP, segments |
| `voice` | Tone, style, content preferences |
| `competitive` | Positioning, differentiation |
| `content` | Topics, formats, frequency |
| `founder` | Personal perspective, expertise |
| `metrics` | Success measures, KPIs |

## Output Files

The skill generates:
- `clients/{client_id}/research/interview-questions.md` - Interview guide document
- `clients/{client_id}/research/interview-questions.json` - Structured data

## Workflow Position

This skill is typically run after research and before the client interview:

```
research-company → research-competitors → research-founder
                           ↓
            generate-interview-questions
                           ↓
                   [Client Interview]
                           ↓
            incorporate-interview-results
```

## Related Documentation

- [SKILL.md](./SKILL.md) - Full specification
- [examples/](./examples/) - Usage examples

## Troubleshooting

**Warning: No research found**
- The skill can run without prior research but questions will be generic
- Run company, competitor, and founder research first for better results

**Error: Too few questions**
- Increase `question_count` parameter
- Ensure prior research has enough gaps to address

**Questions not relevant**
- Use `focus_areas` to guide question generation
- Ensure research docs are up to date

## Support

For issues, check:
1. `verify_setup.py` output
2. Telemetry logs in `telemetry/`
3. SKILL.md for expected behavior
