# References

This folder contains reference materials for the research-company skill:

## Contents

- `examples/` - Example inputs and outputs
- `golden-outputs/` - Validated outputs for testing
- `external-docs/` - Links to external documentation

## Example Structure

```
references/
├── examples/
│   ├── input-basic.json       # Basic input example
│   ├── input-deep.json        # Deep research example
│   ├── output-success.json    # Successful output
│   └── output-partial.json    # Partial success with warnings
├── golden-outputs/
│   └── acme-corp.json         # Golden output for testing
└── external-docs/
    └── firecrawl-api.md       # Firecrawl API reference
```

## Adding New Examples

When adding examples:
1. Ensure inputs validate against `schemas/input.json`
2. Ensure outputs validate against `templates/output-schema.json`
3. Include realistic data that demonstrates skill behavior
4. Document any special cases or edge conditions

## Using for Testing

Golden outputs in `golden-outputs/` are used by the test suite:

```bash
python -m pytest skills/research-company/tests/ -v
```

Tests compare actual output structure and key fields against golden outputs.
