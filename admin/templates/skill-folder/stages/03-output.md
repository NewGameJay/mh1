# Stage 03: Generate Output

## Purpose
Create final deliverable(s) from transformed data.

## Model
`claude-sonnet-4` - High-quality output generation

## Inputs
- `transformed_data`: From Stage 02
- `client_context`: For brand voice, formatting
- `output_templates`: From templates/

## Process

1. **Select output format**
   - JSON for structured data
   - Markdown for reports
   - Both if applicable

2. **Generate structured output**
   ```python
   # Validate against schema
   output = generate_output(transformed_data)
   validate_schema(output, "templates/output-schema.json")
   ```

3. **Generate report (if applicable)**
   ```python
   # Use report template
   report = render_template(
       "templates/report-template.md",
       data=transformed_data,
       context=client_context
   )
   ```

4. **Quality gates**
   - Schema validation
   - Completeness check
   - Factuality verification
   - Brand voice check

5. **Save outputs**
   - Local: `clients/{client_id}/outputs/{skill_name}/`
   - Firebase: `clients/{client_id}/outputs/{skill_name}`

## Output
- `result`: Primary structured output (JSON)
- `report`: Human-readable report (Markdown)
- `metadata`: Execution summary

## Checkpoint
Final stage - no checkpoint (output is the checkpoint)

## Output Locations

```
clients/{client_id}/
├── outputs/
│   └── {skill_name}/
│       ├── result.json        # Structured output
│       ├── report.md          # Human-readable report
│       └── metadata.json      # Execution metadata
```

## Error Handling
- Quality gate failure: Return to Stage 02 with feedback
- Schema validation failure: Fix output, re-validate
- Save failure: Retry with backoff, alert on persistent failure
