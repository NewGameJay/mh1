# Evaluation Prompt

Use this prompt to evaluate outputs before delivery.

---

## System prompt

```
You are a quality assurance evaluator for marketing and analytics outputs. Your job is to assess outputs against defined criteria and return structured evaluation results.

Be rigorous but fair. Flag real issues, not stylistic preferences.
```

---

## User prompt template

```
Evaluate the following output against the criteria below.

## Output to evaluate

{output}

## Expected schema

{schema}

## Evaluation criteria

1. **Schema validity (18%)**: Does the output match the expected schema? Are all required fields present with correct types?

2. **Factuality (23%)**: Are all factual claims supported by data or sources? Flag any claims that appear unsupported or potentially hallucinated.

3. **Completeness (18%)**: Are all required sections present? Is any expected content missing or marked as placeholder?

4. **Brand voice (13%)**: Does the tone match professional marketing standards? Flag overly casual, robotic, or inconsistent language.

5. **Risk flags (18%)**: Are there any hallucinations, bias indicators, sensitive topics, or content that could cause issues if delivered to a client?

6. **Context efficiency (10%)**: Was large context handled efficiently? Check if chunked processing was used for large inputs (>8000 tokens) and if appropriate models were used for sub-tasks (Haiku for extraction, Sonnet for synthesis).

## Output format

Return a JSON object with this structure:

{
  "score": <float 0-1>,
  "pass": <boolean>,
  "breakdown": {
    "schema_validity": <float 0-1>,
    "factuality": <float 0-1>,
    "completeness": <float 0-1>,
    "brand_voice": <float 0-1>,
    "risk_flags": <float 0-1>,
    "context_efficiency": <float 0-1>
  },
  "issues": [
    {
      "dimension": "<dimension name>",
      "severity": "critical|high|medium|low",
      "description": "<specific issue>",
      "location": "<where in output>"
    }
  ],
  "suggestions": [
    "<specific suggestion for improvement>"
  ]
}

Pass threshold: score >= 0.8 AND all dimension scores >= 0.6 AND no critical issues

Note: Each dimension must score at least 0.6 (MIN_PER_DIMENSION) to pass, even if the overall weighted score meets the 0.8 threshold.
```

---

## Example evaluation

**Input (abbreviated):**
```json
{
  "summary": "Email performance improved 15% this quarter.",
  "recommendations": ["Increase send frequency", "Test subject lines"]
}
```

**Output:**
```json
{
  "score": 0.72,
  "pass": false,
  "breakdown": {
    "schema_validity": 1.0,
    "factuality": 0.5,
    "completeness": 0.8,
    "brand_voice": 0.9,
    "risk_flags": 0.7,
    "context_efficiency": 1.0
  },
  "issues": [
    {
      "dimension": "factuality",
      "severity": "high",
      "description": "Claim '15% improvement' has no source or data reference",
      "location": "summary"
    },
    {
      "dimension": "completeness",
      "severity": "medium",
      "description": "Missing 'methodology' section",
      "location": "root"
    }
  ],
  "suggestions": [
    "Add source reference for the 15% improvement claim",
    "Add methodology section explaining how metrics were calculated"
  ]
}
```

---

## Usage

```
/eval --output output.json --schema schema.json
```

Or in a workflow:
```python
eval_result = run_prompt(
    "evaluation-prompt",
    output=output_content,
    schema=schema_content
)
if not eval_result["pass"]:
    route_to_human_review(eval_result)
```
