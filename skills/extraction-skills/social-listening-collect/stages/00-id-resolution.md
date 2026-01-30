# Stage 00: ID Resolution

## Purpose
Load client configuration from `inputs/active_client.md` and resolve all required identifiers.

## Model
None (file read only)

## Duration
Instant

## Status
BLOCKING CHECKPOINT - must complete before proceeding

---

## Inputs Required
- `inputs/active_client.md`: Client configuration file

## Process

### 0.1 Load Client Configuration

Read `inputs/active_client.md` and extract:

```python
from lib.client import get_active_client_id, get_active_client_name

CLIENT_ID = get_active_client_id()
CLIENT_NAME = get_active_client_name()
```

**Alternative (fallback):**
```python
def _read_client_from_file():
    active_client_path = Path("inputs/active_client.md")
    content = active_client_path.read_text()
    result = {}

    for line in content.split('\n'):
        if '=' in line:
            parts = line.split('=', 1)
            key = parts[0].strip().upper()
            value = parts[1].strip().strip('"\'')
            if key == 'CLIENT_ID':
                result['client_id'] = value
            elif key == 'CLIENT_NAME':
                result['client_name'] = value
    return result
```

### 0.2 Validate Client Exists

```python
client_dir = Path(f"clients/{CLIENT_ID}")
if not client_dir.exists():
    # Create directory structure
    client_dir.mkdir(parents=True, exist_ok=True)
    (client_dir / "social-listening").mkdir(exist_ok=True)
    (client_dir / "social-listening" / "collection-data").mkdir(exist_ok=True)
```

### 0.3 Display Resolution Results

Display to user:

```
Client: {CLIENT_NAME}
Client ID: {CLIENT_ID}
Output path: clients/{CLIENT_ID}/social-listening/

Proceeding to Stage 1: Keyword Processing...
```

---

## Output
- `CLIENT_ID`: Validated client identifier
- `CLIENT_NAME`: Client display name
- `client_dir`: Path to client directory

## Checkpoint
This stage does not create a checkpoint (always re-runs).

## Quality Gate

- [ ] CLIENT_ID loaded from `inputs/active_client.md`
- [ ] CLIENT_NAME set
- [ ] Client directory exists or was created

## Error Handling

### Missing active_client.md

```
Error: Client configuration not found.

Expected path: inputs/active_client.md

Solutions:
1. Create the file with CLIENT_ID and CLIENT_NAME
2. Pass --client-id argument directly
```

### Invalid CLIENT_ID Format

```
Error: Invalid CLIENT_ID format.

CLIENT_ID must be alphanumeric with hyphens only.
Received: {invalid_value}
```

---

**Next Stage**: [Stage 01: Keyword Processing](./01-keyword-processing.md)
