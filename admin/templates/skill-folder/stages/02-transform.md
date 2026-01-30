# Stage 02: Transform & Process

## Purpose
Process and transform extracted data into structured output.

## Model
`claude-sonnet-4` - Complex reasoning and transformation

## Inputs
- `extracted_data`: From Stage 01
- `client_context`: Voice contract, brand guidelines
- `execution_config`: Processing parameters

## Process

1. **Data enrichment**
   - Add contextual information
   - Link to related entities
   - Calculate derived fields

2. **Apply business logic**
   ```python
   # Example: Score and categorize
   for item in extracted_data:
       item['relevance_score'] = calculate_relevance(item, client_context)
       item['category'] = categorize(item)
       item['priority'] = determine_priority(item)
   ```

3. **Quality filtering**
   - Apply quality thresholds
   - Remove low-confidence items
   - Flag items needing review

4. **Structure output**
   - Format according to output schema
   - Validate against schema
   - Prepare for final stage

## Output
- `transformed_data`: Processed and structured data
- `transform_metadata`: Processing stats, quality metrics

## Checkpoint
Creates checkpoint at `checkpoints/02-transform.json`

## Context Management
- Large datasets: Process in batches of 500-1000 items
- Use Haiku for simple transformations per item
- Use Sonnet for synthesis and complex reasoning

## Error Handling
- Transformation failure: Log item, continue with others
- Schema validation: Fix or flag items that don't conform
- Quality below threshold: Generate warning, include in report
