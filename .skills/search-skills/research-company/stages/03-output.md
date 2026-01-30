# Stage 03: Generate Output

## Purpose

Generate final deliverables from transformed data: structured JSON output, human-readable research document, and save to client directory. Applies quality gates before release.

## Model

`claude-sonnet-4` - High-quality output generation and document synthesis

## Inputs

| Name | Source | Description |
|------|--------|-------------|
| `company_profile` | Stage 02 | Structured company information |
| `market_positioning` | Stage 02 | Target audience, ICP, value props |
| `products_services` | Stage 02 | Products and services catalog |
| `brand_voice` | Stage 02 | Voice attributes and examples |
| `key_messages` | Stage 02 | Core messaging themes |
| `industry` | Stage 02 | Industry classification |
| `quality_metrics` | Stage 02 | Confidence scores |
| `extraction_metadata` | Stage 01 | Scraping statistics |

## Process

### 1. Build Structured Output

```python
output = {
    "company_name": inputs["company_name"],
    "website_url": inputs["website_url"],
    "industry": industry,
    "company_profile": company_profile,
    "market_positioning": market_positioning,
    "products_services": products_services,
    "brand_voice": brand_voice,
    "key_messages": key_messages,
    "pages_scraped": extraction_metadata["pages_scraped"]
}
```

### 2. Generate Research Document

```python
research_doc_prompt = """
Generate a comprehensive Company Research document for {company_name}.

Use the following structure and include all extracted information:

# Company Research: {company_name}

## Executive Summary
[2-3 sentence overview of the company]

## Company Profile
- **Name**:
- **Website**:
- **Industry**:
- **Founded**:
- **Headquarters**:
- **Size**:
- **Description**:

### Mission & Vision
[Mission and vision statements]

## Market Positioning

### Target Audience
[Who they sell to]

### Ideal Customer Profile
[ICP characteristics]

### Value Proposition
[Core value proposition]

### Differentiators
[List of differentiators]

## Products & Services
[For each product/service, include name, description, features, pricing]

## Brand Voice

### Tone & Personality
[Voice characteristics]

### Key Terms
[Frequently used terms]

### Example Quotes
[Voice examples from the website]

## Key Messages
[Core messaging themes with examples]

## Research Metadata
- **Pages Analyzed**: {pages_count}
- **Research Date**: {date}
- **Confidence Score**: {confidence}

## Sources
[List all source URLs]

---

Data to include:
{structured_data}
"""

research_doc = llm_generate(
    prompt=research_doc_prompt,
    data={
        "company_name": output["company_name"],
        "structured_data": json.dumps(output, indent=2),
        "pages_count": extraction_metadata["pages_scraped"],
        "date": datetime.now().strftime("%Y-%m-%d"),
        "confidence": quality_metrics["overall"]
    },
    model="claude-sonnet-4"
)

# Enforce word limit
if word_count(research_doc) > 10000:
    research_doc = truncate_to_word_limit(research_doc, 10000)
```

### 3. Validate Against Schema

```python
# Validate structured output against schema
schema = load_schema("schemas/output.json")
validation_result = validate_json(output, schema)

if not validation_result.valid:
    log_error(f"Schema validation failed: {validation_result.errors}")
    # Attempt to fix common issues
    output = fix_schema_issues(output, validation_result.errors)
    validation_result = validate_json(output, schema)
```

### 4. Apply Quality Gates

```python
quality_gates = {
    "schema_validation": validate_schema(output, "schemas/output.json"),
    "company_name_present": bool(output["company_profile"].get("name")),
    "description_present": bool(output["company_profile"].get("description")),
    "product_identified": len(output["products_services"]) >= 1,
    "target_audience_present": bool(output["market_positioning"].get("target_audience")),
    "voice_detected": len(output["brand_voice"].get("tone", [])) >= 1,
    "sources_included": count_sources(research_doc) >= 3
}

quality_score = sum(quality_gates.values()) / len(quality_gates)
all_gates_passed = all(quality_gates.values())

# Determine release action
if quality_score >= 0.9 and all_gates_passed:
    release_action = "auto_deliver"
    release_message = "All quality gates passed"
elif quality_score >= 0.6:
    release_action = "human_review"
    release_message = f"Quality score {quality_score:.0%} - review recommended"
else:
    release_action = "blocked"
    release_message = f"Quality score {quality_score:.0%} - below threshold"
```

### 5. Save Outputs

```python
client_id = inputs["client_id"]
output_dir = f"clients/{client_id}/research"

# Save research document
research_doc_path = f"{output_dir}/company-research.md"
save_file(research_doc_path, research_doc)

# Save structured JSON
json_path = f"{output_dir}/company-research.json"
save_json(json_path, output)

# Update output with paths
output["research_doc"] = research_doc
output["research_doc_path"] = research_doc_path
```

### 6. Build Final Response

```python
final_response = {
    "status": "success" if release_action != "blocked" else "review",
    "output": output,
    "evaluation": {
        "score": quality_score,
        "pass": all_gates_passed,
        "breakdown": quality_gates
    },
    "release_action": release_action,
    "release_message": release_message,
    "run_id": generate_run_id(),
    "_meta": {
        "client_id": client_id,
        "tenant_id": inputs.get("tenant_id", client_id),
        "run_id": run_id,
        "execution_mode": inputs.get("execution_mode", "suggest"),
        "runtime_seconds": calculate_runtime(),
        "cost_usd": calculate_cost(),
        "skill_version": "1.1.0",
        "pages_scraped": extraction_metadata["pages_scraped"],
        "tokens": token_usage,
        "timestamp": datetime.now().isoformat()
    }
}
```

## Output

| Name | Type | Description |
|------|------|-------------|
| `status` | string | success, review, failed, or budget_exceeded |
| `output` | object | All extracted company data |
| `evaluation` | object | Quality gate results |
| `release_action` | string | auto_deliver, human_review, or blocked |
| `release_message` | string | Explanation of release decision |
| `_meta` | object | Execution metadata |

## Output Locations

```
clients/{client_id}/
├── research/
│   ├── company-research.md     # Human-readable research document
│   └── company-research.json   # Structured data for other skills
```

## Checkpoint

Final stage - no checkpoint (outputs are the deliverable).

## Quality Gates

| Gate | Criterion | Required |
|------|-----------|----------|
| Schema validation | Output matches schemas/output.json | Yes |
| Company name | company_profile.name present | Yes |
| Description | company_profile.description present | Yes |
| Product identified | At least 1 product/service | Yes |
| Target audience | market_positioning.target_audience present | Yes |
| Voice detected | At least 1 tone attribute | Yes |
| Sources included | At least 3 source URLs in document | Yes |

## Release Policy

| Quality Score | Gates Passed | Action |
|--------------|--------------|--------|
| >= 0.9 | All | auto_deliver |
| >= 0.7 | Most | human_review |
| >= 0.6 | Some | human_review with priority |
| < 0.6 | Few | blocked |

## Human Review Triggers

| Trigger | Review SLA | Notes |
|---------|------------|-------|
| First run for client | 24h | Always review first research |
| Quality score < 0.7 | 8h | Expedited review |
| Industry auto-detected | - | Flag for verification only |
| Scraping was limited | 8h | May need manual enrichment |

## Error Handling

| Error | Trigger | Action |
|-------|---------|--------|
| Schema validation failure | Output doesn't match schema | Attempt fix, re-validate |
| Quality gates failed | Score below threshold | Return with UNVALIDATED flag |
| Save failure | File system error | Retry with backoff |
| Document too long | > 10,000 words | Truncate with summary |

## Success Criteria

- [ ] Structured output validates against schema
- [ ] Research document generated and saved
- [ ] All required quality gates pass
- [ ] Output saved to client directory
- [ ] Metadata complete
- [ ] Release action determined
