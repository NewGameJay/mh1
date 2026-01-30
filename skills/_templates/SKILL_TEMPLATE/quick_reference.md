# Quick Reference: [SKILL_NAME]

## Usage

```bash
# Basic usage
python skills/[skill-name]/run.py --input <input_file>

# With client context
python skills/[skill-name]/run.py --client-id <client_id> --input <input_file>

# Preview mode (no writes)
python skills/[skill-name]/run.py --mode preview --input <input_file>
```

---

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--input` | string | required | Input file path |
| `--client-id` | string | from active_client.md | Client identifier |
| `--mode` | string | execute | suggest / preview / execute |
| `--output` | string | auto | Output file path |

---

## Common Patterns

### Pattern 1: [Name]
```bash
# Description of when to use this pattern
python skills/[skill-name]/run.py [flags]
```

### Pattern 2: [Name]
```bash
# Description of when to use this pattern
python skills/[skill-name]/run.py [flags]
```

---

## Input Format

```json
{
  "field1": "value",
  "field2": ["item1", "item2"]
}
```

---

## Output Format

```json
{
  "result": "...",
  "_meta": {
    "skill": "[skill-name]",
    "version": "1.0.0",
    "execution_time_ms": 1234
  }
}
```

---

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `Error: Missing credentials` | API key not set | Set in .env file |
| `Error: Client not found` | Invalid client_id | Check inputs/active_client.md |
| `Error: Budget exceeded` | Over spending limit | Increase quota or wait |

---

## Related Skills

- `skill-a` - Does X before this skill
- `skill-b` - Uses output from this skill

---

## Tips

1. Always run `verify_setup.py` first
2. Use `--mode preview` for testing
3. Check telemetry for cost tracking
