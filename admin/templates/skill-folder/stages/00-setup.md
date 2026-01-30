# Stage 00: Setup & Validation

## Purpose
Validate inputs, check prerequisites, and prepare the execution environment.

## Inputs Required
- `client_id`: Client identifier (required)
- `options`: Configuration options (optional)

## Validation Steps

1. **Check client exists**
   ```python
   client = firebase.get_document(f"clients/{client_id}")
   if not client:
       raise ValidationError(f"Client {client_id} not found")
   ```

2. **Check required context**
   ```python
   required_context = ["voice-contract", "company-research"]
   for ctx in required_context:
       if not context_exists(client_id, ctx):
           raise ValidationError(f"Missing required context: {ctx}")
   ```

3. **Check MCP connections**
   ```python
   required_mcp = ["firebase"]
   for mcp in required_mcp:
       if not mcp_connected(mcp):
           raise ConnectionError(f"MCP not connected: {mcp}")
   ```

## Output
- `validated_inputs`: Cleaned and validated input parameters
- `client_context`: Loaded client context
- `execution_config`: Runtime configuration

## Checkpoint
This stage does not create a checkpoint (always re-runs).

## Error Handling
- Missing client: Exit with clear error message
- Missing context: Suggest running prerequisite skills
- MCP disconnected: Provide connection instructions
