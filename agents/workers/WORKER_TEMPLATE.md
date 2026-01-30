# Worker Agent: [AGENT_NAME]

Version: v1.0.0  
Type: worker  
Author: [name]  
Created: [YYYY-MM-DD]

---

## Purpose

[Describe the specific task this worker performs.]

---

## Specialization

This worker specializes in:
- [Domain 1: e.g., "Email copy analysis"]
- [Domain 2: e.g., "HubSpot data extraction"]

---

## Skills used

| Skill name       | Purpose                        |
|------------------|--------------------------------|
| `skill_1`        | [what it does]                 |
| `skill_2`        | [what it does]                 |

---

## Inputs

| Name        | Type     | Required | Description                      |
|-------------|----------|----------|----------------------------------|
| `task`      | string   | yes      | Specific task to perform         |
| `data`      | object   | yes      | Input data to process            |
| `config`    | object   | no       | Override defaults                |

---

## Execution Modes

| Mode | Behavior | Write Operations |
|------|----------|------------------|
| `suggest` | Generate recommendations only | None |
| `preview` | Show what would change (dry-run) | None |
| `execute` | Apply changes | With approval if high-impact |

### Mode Selection Logic

```python
mode = inputs.get("execution_mode", "suggest")

if mode == "suggest":
    return generate_recommendations(data)
elif mode == "preview":
    return preview_changes(data)
elif mode == "execute":
    if requires_approval(changes):
        return request_approval(changes)
    return execute_changes(changes)
```

---

## Outputs

| Name        | Type     | Description                      |
|-------------|----------|----------------------------------|
| `result`    | object   | Processed output                 |
| `confidence`| number   | 0-1 confidence score             |
| `sources`   | array    | Source references                |

---

## Process

1. Receive task from orchestrator
2. Load relevant skill(s)
3. Execute skill with input data
4. Validate output against schema
5. Return result with confidence score

---

## Model configuration

```yaml
model: claude-haiku  # Default for extraction tasks
fallback_model: claude-sonnet-4  # If confidence < 0.6
temperature: 0.1  # Low for consistency
max_tokens: 4096
```

---

## Tools / MCPs

| Tool         | Purpose                        |
|--------------|--------------------------------|
| `hubspot`    | CRM data access                |
| `snowflake`  | Data warehouse queries         |
| `web_fetch`  | External URL retrieval         |

---

## Constraints

- Output must match schema in `schemas/`
- All factual claims must include source
- Max execution time: 60 seconds
- Max retries on failure: 2

---

## Example

**Input:**
```json
{
  "task": "Extract email performance metrics",
  "data": {
    "campaign_id": "12345",
    "date_range": "2026-01-01 to 2026-01-15"
  }
}
```

**Output:**
```json
{
  "result": {
    "open_rate": 0.42,
    "click_rate": 0.08,
    "unsubscribe_rate": 0.002
  },
  "confidence": 0.95,
  "sources": ["hubspot:campaign:12345"]
}
```

---

## Notes

[Any additional context or known limitations.]
