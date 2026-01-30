# Scripts

This folder contains helper scripts for the skill.

## Naming convention

- `fetch_*.py` — Data fetching scripts
- `transform_*.py` — Data transformation scripts
- `validate_*.py` — Validation scripts
- `export_*.py` — Export/formatting scripts

## Usage

Scripts can be called by the skill during execution:

```python
# Example: fetch data from an API
python scripts/fetch_data.py --input input.json --output output.json
```

## Requirements

If scripts have Python dependencies, list them in `requirements.txt` in this folder.
