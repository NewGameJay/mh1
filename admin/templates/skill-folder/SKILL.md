---
name: skill-name
version: 1.0.0
description: |
  Brief description of what this skill does.
  Include the primary use case and expected outcome.

category: research|content|analysis|automation|meta
author: MH1
created: 2024-01-01
updated: 2024-01-01

# Stage configuration
stages:
  - id: "00-setup"
    name: "Setup & Validation"
    description: "Validate inputs and prepare environment"
    required: true
  - id: "01-extract"
    name: "Data Extraction"
    description: "Extract raw data from sources"
    checkpoint: true
    model: claude-haiku
  - id: "02-transform"
    name: "Transform & Process"
    description: "Process and transform extracted data"
    checkpoint: true
    model: claude-sonnet-4
  - id: "03-output"
    name: "Generate Output"
    description: "Create final deliverable"
    model: claude-sonnet-4

# Input/output definitions
inputs:
  - name: client_id
    type: string
    required: true
    description: "Client identifier"
  - name: options
    type: object
    required: false
    schema: config/input-schema.json
    description: "Optional configuration"

outputs:
  - name: result
    type: object
    schema: templates/output-schema.json
    description: "Primary output"
  - name: report
    type: markdown
    template: templates/report-template.md
    description: "Human-readable report"

# Dependencies
requires_skills: []
requires_context:
  - voice-contract
  - company-research
requires_mcp:
  - firebase

# Execution settings
timeout_minutes: 30
max_retries: 2
cost_estimate: "~$0.05 per run"

# Quality gates
quality_gates:
  - name: schema_validation
    type: schema
    schema: templates/output-schema.json
  - name: completeness
    type: checklist
    items:
      - "All required fields present"
      - "No placeholder values"
  - name: factuality
    type: source_check
    required_sources: 1
---

# Skill Name

## Overview

[Detailed description of what this skill does, when to use it, and expected outcomes.]

## Prerequisites

- [List prerequisites]
- [Required context or data]
- [Required MCP connections]

## Usage

```bash
/run-skill skill-name --client {client_id}
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| client_id | string | Yes | - | Client identifier |
| options | object | No | {} | Additional options |

## Process

This skill executes in the following stages:

### Stage 0: Setup & Validation
[Description of setup stage - loaded from stages/00-setup.md]

### Stage 1: Data Extraction
[Description of extraction stage - loaded from stages/01-extract.md]

### Stage 2: Transform & Process
[Description of transform stage - loaded from stages/02-transform.md]

### Stage 3: Generate Output
[Description of output stage - loaded from stages/03-output.md]

## Output

### Schema
See `templates/output-schema.json` for full schema.

### Example
See `references/examples/output-example.json` for sample output.

## Quality Criteria

- [ ] All required fields populated
- [ ] Data validated against schema
- [ ] Sources cited for factual claims
- [ ] Follows brand voice guidelines

## Troubleshooting

### Common Issues

1. **Issue**: Missing context
   **Solution**: Run `mh1 sync` to pull latest client context

2. **Issue**: Timeout
   **Solution**: Check MCP connections with `mh1 connections`

## Related Skills

- [related-skill-1](../related-skill-1/SKILL.md)
- [related-skill-2](../related-skill-2/SKILL.md)
