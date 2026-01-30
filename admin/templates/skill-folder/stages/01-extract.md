# Stage 01: Data Extraction

## Purpose
Extract raw data from configured sources.

## Model
`claude-haiku` - Fast, efficient extraction

## Inputs
- `validated_inputs`: From Stage 00
- `client_context`: Loaded context
- `execution_config`: Runtime config

## Process

1. **Identify data sources**
   - Firebase collections
   - MCP-connected platforms
   - Local cache files

2. **Extract data**
   ```python
   # Example: Extract from Firebase
   raw_data = []
   for source in data_sources:
       docs = firebase.collection(source).get()
       raw_data.extend([doc.to_dict() for doc in docs])
   ```

3. **Initial filtering**
   - Remove duplicates
   - Filter by date range (if applicable)
   - Validate data structure

## Output
- `extracted_data`: Raw extracted data
- `extraction_metadata`: Source info, counts, timestamps

## Checkpoint
Creates checkpoint at `checkpoints/01-extract.json`

Can resume from this point if later stages fail.

## Context Management
- If data > 8000 tokens: Use chunked processing
- Process chunks with Haiku, aggregate results

## Error Handling
- Source unavailable: Log warning, continue with available sources
- Rate limited: Implement backoff, retry
- Partial extraction: Save checkpoint, allow resume
