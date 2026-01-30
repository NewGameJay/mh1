# Module Template

This is the standard structure for MH1 modules.

## Directory Structure

```
{module_id}/
├── README.md              # Module documentation
├── inputs/                # Input files and attachments
│   └── manifest.json      # File manifest with metadata
├── outputs/               # Generated outputs
└── logs/                  # Execution logs
```

## Inputs Directory

The `inputs/` directory stores files attached to this module.

### Manifest Format

The `manifest.json` file tracks all attached files:

```json
{
  "files": [
    {
      "file_id": "abc12345",
      "original_name": "data.csv",
      "stored_path": "/path/to/modules/{module_id}/inputs/abc12345_data.csv",
      "hash_sha256": "sha256_hash_of_file_contents",
      "size_bytes": 12345,
      "mime_type": "text/csv",
      "uploaded_at": "2024-01-29T12:00:00Z"
    }
  ],
  "created_at": "2024-01-29T12:00:00Z",
  "updated_at": "2024-01-29T12:00:00Z"
}
```

### Allowed File Types

- Data: `.csv`, `.json`, `.txt`, `.tsv`, `.parquet`
- Documents: `.md`, `.pdf`, `.xlsx`, `.xls`
- Config: `.yaml`, `.yml`
- Web: `.html`, `.xml`
- Images: `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`

### Size Limit

Maximum file size: 50MB per file.

## Usage

### Attaching Files via CLI

```bash
# Single file
./mh1 "audit lifecycle" --attach data.csv

# Multiple files
./mh1 "audit lifecycle" --attach contacts.csv --attach events.json

# With specific module ID
./mh1 "audit" --attach data.csv --module my-audit-module
```

### Attaching Files Interactively

When prompted "Attach files? [y/N]", enter "y" to add files.

### Programmatic Access

```python
from lib.file_handler import get_file_handler

handler = get_file_handler()

# Attach a file
file_info = handler.attach_file("my-module", "/path/to/file.csv")

# List all inputs
files = handler.list_inputs("my-module")

# Get manifest
manifest = handler.get_manifest("my-module")
```
