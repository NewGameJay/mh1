# Lifecycle Audit Skill Examples

This directory contains golden test inputs and outputs for the lifecycle-audit skill.

## Files

- `golden_test_input.json` - Standard input for testing the skill
- `golden_test_output.json` - Expected output structure (with variable fields normalized)

## Usage

### Running the golden test manually

```bash
cd /path/to/mh1-hq
python skills/lifecycle-audit/run.py --tenant_id acme_corp --limit 100 --output test_output.json
```

### Comparing with golden output

The golden output has certain fields normalized with placeholders:
- `<RUN_ID>` - Run identifier (changes each run)
- `<RUNTIME>` - Runtime in seconds (varies)
- `<TIMESTAMP>` - ISO timestamp (changes each run)
- `<TOKEN_COUNT>` - Token counts (may vary based on data)

When comparing your output to the golden output, ignore these fields and focus on:
- `status` should be `success` or `review`
- `output.summary` structure should match
- `output.recommendations` should be an array of recommendation objects
- `output.bottlenecks` should be an array (may be empty)
- `output.at_risk` should be an array of at-risk account objects
- `output.upsell_candidates` should be an array of upsell candidate objects

## Expected Output Structure

```json
{
  "status": "success",
  "output": {
    "summary": {
      "total_accounts": 100,
      "by_stage": { ... },
      "health_score": 0.0-1.0
    },
    "bottlenecks": [...],
    "at_risk": [...],
    "upsell_candidates": [...],
    "recommendations": [...],
    "conversions": [...],
    "_meta": {
      "tenant_id": "...",
      "run_id": "...",
      "execution_mode": "suggest",
      ...
    }
  },
  "evaluation": { ... },
  "release_action": "auto_deliver",
  "release_message": "..."
}
```
