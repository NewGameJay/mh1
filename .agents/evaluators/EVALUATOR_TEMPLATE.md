# Evaluator Agent: [AGENT_NAME]

Version: v1.0.0  
Type: evaluator  
Author: [name]  
Created: [YYYY-MM-DD]

---

## Purpose

This evaluator checks outputs against quality criteria before delivery. It acts as a quality gate between worker output and final delivery.

---

## Evaluation dimensions

| Dimension          | Weight | Description                                   |
|--------------------|--------|-----------------------------------------------|
| Schema validity    | 0.20   | Output matches expected JSON schema           |
| Factuality         | 0.25   | Claims are source-linked and verifiable       |
| Completeness       | 0.20   | All required sections/fields present          |
| Brand voice        | 0.15   | Tone and style match guidelines               |
| Risk flags         | 0.20   | No hallucinations, bias, or sensitive content |

---

## Inputs

| Name        | Type     | Required | Description                      |
|-------------|----------|----------|----------------------------------|
| `output`    | object   | yes      | The output to evaluate           |
| `schema`    | object   | yes      | Expected output schema           |
| `context`   | object   | no       | Original task context            |
| `guidelines`| object   | no       | Brand voice and style guidelines |

---

## Outputs

| Name        | Type     | Description                              |
|-------------|----------|------------------------------------------|
| `score`     | number   | 0-1 overall quality score                |
| `pass`      | boolean  | true if score >= threshold               |
| `breakdown` | object   | Per-dimension scores                     |
| `issues`    | array    | List of identified issues                |
| `suggestions`| array   | Recommended fixes                        |

---

## Threshold configuration

```yaml
pass_threshold: 0.8       # Overall score required to pass
min_per_dimension: 0.6    # Minimum score per dimension
auto_fail_triggers:
  - hallucination_detected
  - schema_invalid
  - missing_required_field
  - sensitive_content_flagged
```

---

## Evaluation process

1. **Schema validation**
   - Parse output against schema
   - Check required fields
   - Validate types

2. **Factuality check**
   - Extract all factual claims
   - Verify each claim has a source
   - Cross-check against known data

3. **Completeness check**
   - Compare output sections to template
   - Flag missing sections
   - Check for placeholder text

4. **Brand voice check**
   - Analyze tone (formal, casual, technical)
   - Check vocabulary against guidelines
   - Flag off-brand language

5. **Risk assessment**
   - Scan for hallucination patterns
   - Check for bias indicators
   - Flag sensitive topics

---

## Actions on evaluation result

| Scenario                     | Action                                    |
|------------------------------|-------------------------------------------|
| Score >= 0.8                 | Pass; proceed to delivery                 |
| Score 0.6-0.8                | Return with suggestions; rerun once       |
| Score < 0.6                  | Fail; route to human review               |
| Auto-fail trigger            | Immediate fail; require human approval    |

---

## Output example

```json
{
  "score": 0.85,
  "pass": true,
  "breakdown": {
    "schema_validity": 1.0,
    "factuality": 0.9,
    "completeness": 0.8,
    "brand_voice": 0.75,
    "risk_flags": 0.9
  },
  "issues": [
    {
      "dimension": "brand_voice",
      "severity": "low",
      "description": "Paragraph 3 uses overly casual tone",
      "location": "section.recommendations[2]"
    }
  ],
  "suggestions": [
    "Revise paragraph 3 to use more professional language"
  ]
}
```

---

## Integration

This evaluator should be called:
- After every worker agent output
- Before any client-facing delivery
- On batch outputs before export

```
/eval --output output.json --schema schema.json --guidelines brand.json
```

---

## Notes

- Never skip evaluation on client deliverables
- Log all evaluation results to telemetry
- Review auto-fail triggers monthly to reduce false positives

---

## Extended Evaluation Dimensions (P2 Addition)

> Sources: r7.pdf, r8.pdf, r9.pdf, r10.pdf research

### New Dimensions

#### Trend Accuracy (Weight: 5%)
*From r10.pdf/r11.pdf TATS research*

For forecasting outputs, evaluate directional accuracy:
- Does the prediction correctly identify trend direction?
- Standard metrics (MSE, MAE) can hide directional errors
- Threshold: TDA ≥ 55% for production

| Score | Criteria |
|-------|----------|
| 5 | Trend direction correct with high confidence |
| 3 | Trend direction correct but marginal |
| 1 | Trend direction incorrect |

#### AI Washing Score (Weight: 5%)
*From r9.pdf AI Washing research*

Check for capability overclaims:
- Marketing washing: Overclaims capabilities
- Technical washing: Methodology exaggeration
- Strategic washing: Roadmap inflation
- Governance washing: Compliance overstatement

| Score | Criteria |
|-------|----------|
| 5 | No washing detected, claims substantiated |
| 3 | Minor unsubstantiated claims |
| 1 | Significant overclaims, high risk |

#### Planning Efficiency (Weight: 5%)
*From r7.pdf Tool Reliability research*

Monitor computational efficiency:
- Step count vs baseline for model
- Smaller models take 2.4× more steps
- Flag excessive planning loops

| Score | Criteria |
|-------|----------|
| 5 | Steps ≤ baseline for model |
| 3 | Steps 1.5× baseline |
| 1 | Steps > 2× baseline (cyclical loops) |

### Updated Dimension Weights

| Dimension | Original | Updated | Source |
|-----------|----------|---------|--------|
| Schema validity | 20% | 15% | Existing |
| Factuality | 25% | 20% | Existing |
| Completeness | 20% | 15% | Existing |
| Brand voice | 15% | 10% | Existing |
| Risk flags | 20% | 15% | Existing |
| Context efficiency | - | 10% | Existing |
| Trend accuracy | - | 5% | r10.pdf |
| AI washing | - | 5% | r9.pdf |
| Planning efficiency | - | 5% | r7.pdf |

### Auto-Fail Triggers (Extended)

Add to existing triggers:
- AI washing score = 1 (high risk)
- Trend accuracy = 1 for forecasting outputs
- Planning efficiency = 1 (indicates broken workflow)
