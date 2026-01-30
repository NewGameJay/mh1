# [SKILL_NAME]

> [One-line description of what this skill does]

## Quick Start

```bash
# 1. Verify setup
python skills/[skill-name]/verify_setup.py

# 2. Run skill
python skills/[skill-name]/run.py --input data.json
```

## What It Does

[2-3 sentences explaining the skill's purpose and when to use it.]

## Prerequisites

- Python 3.8+
- Required packages: `pip install -r requirements.txt`
- API credentials (see `.env.template`)

## Usage

### Basic

```bash
python skills/[skill-name]/run.py --input input.json
```

### With Options

```bash
python skills/[skill-name]/run.py \
  --input input.json \
  --client-id abc123 \
  --mode preview
```

## Input

```json
{
  "field1": "required value",
  "field2": "optional value"
}
```

## Output

```json
{
  "result": "...",
  "_meta": {
    "skill": "[skill-name]",
    "version": "1.0.0"
  }
}
```

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `API_KEY` | Yes | Your API key |

## Related Documentation

- [SKILL.md](./SKILL.md) - Full specification
- [quick_reference.md](./quick_reference.md) - Parameter cheat sheet
- [examples/](./examples/) - Usage examples

## Troubleshooting

**Error: Missing credentials**
- Ensure `.env` file exists with required variables
- Run `verify_setup.py` to diagnose

**Error: Budget exceeded**
- Check quota in `config/quotas.yaml`
- Contact admin to increase limit

## Support

For issues, check:
1. `verify_setup.py` output
2. Telemetry logs in `telemetry/`
3. SKILL.md for expected behavior
