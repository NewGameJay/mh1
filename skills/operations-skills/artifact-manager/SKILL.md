---
name: artifact-manager
description: |
  Store and retrieve query results with checksums using configurable storage backends.
  Use when asked to 'save query results', 'store artifact', 'load cached data',
  'get artifact by run_id', or 'list recent queries'.
license: Proprietary
compatibility:
  - Local filesystem
  - AWS S3
  - Google Cloud Storage
  - Azure Blob Storage
metadata:
  author: mh1-engineering
  version: "2.0.0"
  status: active
  created: "2026-01-27"
  updated: "2026-01-28"
  estimated_runtime: "0.5-2min"
  max_runtime: "5min"
  estimated_cost: "$0.05"
  max_cost: "$0.15"
  client_facing: false
  requires_human_review: false
  tags:
    - data
    - caching
    - artifacts
    - storage
allowed-tools: Read Write Shell
---

# Artifact Manager Skill

Manage query result storage and retrieval using configurable storage backends. Provides run_id generation, checksum validation, and indexed lookup.

## Supported Platforms

### Storage Backends

| Backend | Integration | Notes |
|---------|------------|-------|
| Local Filesystem | Native | Default, no additional config |
| AWS S3 | boto3 | Requires AWS credentials |
| Google Cloud Storage | google-cloud-storage | Requires GCP credentials |
| Azure Blob Storage | azure-storage-blob | Requires Azure credentials |
| MinIO | S3-compatible | Self-hosted S3 alternative |

### Index Storage

| Backend | Integration | Notes |
|---------|------------|-------|
| JSON file | Native | Default, local index |
| SQLite | sqlite3 | Better query performance |
| PostgreSQL | psycopg2 | Shared index across instances |
| DynamoDB | boto3 | Serverless option for AWS |

---

## Configuration

Configuration is stored in `config/artifact-manager.yaml`:

```yaml
# config/artifact-manager.yaml
artifact_manager:
  # Storage backend configuration
  storage:
    backend: "local"  # local, s3, gcs, azure, minio
    
    # Local filesystem settings
    local:
      base_path: "artifacts"
      
    # AWS S3 settings
    s3:
      bucket: "${AWS_ARTIFACT_BUCKET}"
      prefix: "artifacts/"
      region: "${AWS_REGION}"
      # Credentials from environment or IAM role
      
    # Google Cloud Storage settings
    gcs:
      bucket: "${GCS_ARTIFACT_BUCKET}"
      prefix: "artifacts/"
      project: "${GCP_PROJECT}"
      
    # Azure Blob Storage settings
    azure:
      container: "${AZURE_ARTIFACT_CONTAINER}"
      prefix: "artifacts/"
      connection_string: "${AZURE_STORAGE_CONNECTION_STRING}"
      
    # MinIO (S3-compatible) settings
    minio:
      endpoint: "${MINIO_ENDPOINT}"
      bucket: "${MINIO_BUCKET}"
      access_key: "${MINIO_ACCESS_KEY}"
      secret_key: "${MINIO_SECRET_KEY}"
      secure: true
      
  # Index configuration
  index:
    backend: "json"  # json, sqlite, postgres, dynamodb
    
    # JSON index settings
    json:
      path: "artifacts/index.json"
      
    # SQLite settings
    sqlite:
      path: "artifacts/index.db"
      
    # PostgreSQL settings
    postgres:
      connection_string: "${POSTGRES_URL}"
      table: "artifact_index"
      
    # DynamoDB settings
    dynamodb:
      table: "${DYNAMODB_ARTIFACT_TABLE}"
      region: "${AWS_REGION}"
      
  # Retention policy
  retention:
    enabled: true
    max_age_days: 90
    max_entries: 10000
    cleanup_on_startup: false
    
  # Checksum settings
  checksum:
    algorithm: "sha256"  # sha256, md5, blake2b
    verify_on_load: true
```

---

## When to Use

Use this skill when you need to:
- Store query results for later use
- Retrieve cached cohort data
- Generate run IDs for workflow tracking
- Validate artifact integrity via checksums
- List recent queries by template

Do NOT use when:
- Running ad-hoc queries (just execute directly)
- Storing non-query data (use filesystem)
- Working with real-time data requirements

---

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `action` | string | yes | "store", "load", "list", or "validate" |
| `run_id` | string | conditional | Required for "load" and "validate" |
| `template_id` | string | conditional | Required for "store" and "list" |
| `data` | object | conditional | Required for "store" - the data to save |
| `limit` | number | no | For "list" - max entries to return (default: 50) |
| `storage_backend` | string | no | Override default storage backend |

---

## Outputs

| Name | Type | Description |
|------|------|-------------|
| `run_id` | string | Unique identifier for the stored artifact |
| `artifact_path` | string | Path/URI to the stored data |
| `checksum` | string | Hash for integrity verification |
| `entry` | object | Full artifact entry metadata |
| `entries` | array | List of entries (for "list" action) |

---

## Dependencies

| Type | Name | Purpose |
|------|------|---------|
| Library | `lib/artifacts.py` | ArtifactStore class |
| Config | `config/artifact-manager.yaml` | Storage configuration |

---

## Core Classes

### ArtifactEntry

```python
@dataclass
class ArtifactEntry:
    run_id: str              # Unique identifier
    template_id: str         # Query template
    template_name: str       # Human-readable name
    source: str              # Data source identifier
    timestamp: str           # ISO format timestamp
    parameters: Dict         # Query parameters used
    row_count: int           # Number of rows in result
    artifact_path: str       # Path/URI to data file
    checksum: str            # Hash of data file
    checksum_algorithm: str  # Algorithm used (sha256, md5, etc.)
    storage_backend: str     # Where data is stored
    resolved_query: str      # Optional: actual query executed
    metadata: Dict           # Optional: additional metadata
```

### ArtifactStore

```python
class ArtifactStore:
    def __init__(self, config: dict = None)
    def add_entry(self, entry: ArtifactEntry)      # Store new artifact
    def get_entry(self, run_id: str) -> ArtifactEntry
    def list_entries(self, template_id: str = None, limit: int = 50)
    def get_latest(self, template_id: str) -> ArtifactEntry
    def load_artifact(self, run_id: str) -> DataFrame | Dict
    def delete_artifact(self, run_id: str) -> bool
    def cleanup_old_artifacts(self, max_age_days: int) -> int
```

---

## Process

### Action: "store"

Store query results with automatic checksum generation.

**Step 1: Load Configuration**

```python
import yaml

def load_config() -> dict:
    """Load artifact manager configuration"""
    config_path = "config/artifact-manager.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)["artifact_manager"]
```

**Step 2: Generate run_id**

```python
import hashlib
from datetime import datetime

def generate_run_id(template_id: str, parameters: dict) -> str:
    """Generate unique run_id with timestamp and hash suffix"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create hash from parameters for uniqueness
    param_str = str(sorted(parameters.items()))
    hash_suffix = hashlib.md5(param_str.encode()).hexdigest()[:4]
    
    return f"{template_id}_{timestamp}_{hash_suffix}"

# Example: "at_risk_accounts_20260127_143022_a1b2"
```

**Step 3: Save data file**

```python
def save_artifact_data(data, run_id: str, config: dict) -> str:
    """Save data to configured storage backend"""
    backend = config["storage"]["backend"]
    
    if backend == "local":
        return save_to_local(data, run_id, config["storage"]["local"])
    elif backend == "s3":
        return save_to_s3(data, run_id, config["storage"]["s3"])
    elif backend == "gcs":
        return save_to_gcs(data, run_id, config["storage"]["gcs"])
    elif backend == "azure":
        return save_to_azure(data, run_id, config["storage"]["azure"])
    else:
        raise ValueError(f"Unknown storage backend: {backend}")

def save_to_local(data, run_id: str, config: dict) -> str:
    """Save to local filesystem"""
    import pandas as pd
    import json
    
    base_path = config["base_path"]
    
    if isinstance(data, pd.DataFrame):
        file_path = f"{base_path}/{run_id}.csv"
        data.to_csv(file_path, index=False)
    else:
        file_path = f"{base_path}/{run_id}.json"
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    return file_path

def save_to_s3(data, run_id: str, config: dict) -> str:
    """Save to AWS S3"""
    import boto3
    import pandas as pd
    import json
    from io import StringIO, BytesIO
    
    s3 = boto3.client('s3', region_name=config.get("region"))
    bucket = config["bucket"]
    prefix = config.get("prefix", "")
    
    if isinstance(data, pd.DataFrame):
        key = f"{prefix}{run_id}.csv"
        buffer = StringIO()
        data.to_csv(buffer, index=False)
        s3.put_object(Bucket=bucket, Key=key, Body=buffer.getvalue())
    else:
        key = f"{prefix}{run_id}.json"
        s3.put_object(
            Bucket=bucket, 
            Key=key, 
            Body=json.dumps(data, indent=2, default=str)
        )
    
    return f"s3://{bucket}/{key}"

def save_to_gcs(data, run_id: str, config: dict) -> str:
    """Save to Google Cloud Storage"""
    from google.cloud import storage
    import pandas as pd
    import json
    
    client = storage.Client(project=config.get("project"))
    bucket = client.bucket(config["bucket"])
    prefix = config.get("prefix", "")
    
    if isinstance(data, pd.DataFrame):
        blob_name = f"{prefix}{run_id}.csv"
        blob = bucket.blob(blob_name)
        blob.upload_from_string(data.to_csv(index=False), content_type='text/csv')
    else:
        blob_name = f"{prefix}{run_id}.json"
        blob = bucket.blob(blob_name)
        blob.upload_from_string(
            json.dumps(data, indent=2, default=str), 
            content_type='application/json'
        )
    
    return f"gs://{config['bucket']}/{blob_name}"

def save_to_azure(data, run_id: str, config: dict) -> str:
    """Save to Azure Blob Storage"""
    from azure.storage.blob import BlobServiceClient
    import pandas as pd
    import json
    
    blob_service = BlobServiceClient.from_connection_string(
        config["connection_string"]
    )
    container = blob_service.get_container_client(config["container"])
    prefix = config.get("prefix", "")
    
    if isinstance(data, pd.DataFrame):
        blob_name = f"{prefix}{run_id}.csv"
        container.upload_blob(blob_name, data.to_csv(index=False), overwrite=True)
    else:
        blob_name = f"{prefix}{run_id}.json"
        container.upload_blob(
            blob_name, 
            json.dumps(data, indent=2, default=str), 
            overwrite=True
        )
    
    return f"azure://{config['container']}/{blob_name}"
```

**Step 4: Calculate checksum**

```python
def calculate_checksum(data, algorithm: str = "sha256") -> str:
    """Calculate checksum of data"""
    import hashlib
    import pandas as pd
    import json
    
    if algorithm == "sha256":
        hasher = hashlib.sha256()
    elif algorithm == "md5":
        hasher = hashlib.md5()
    elif algorithm == "blake2b":
        hasher = hashlib.blake2b()
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    
    if isinstance(data, pd.DataFrame):
        content = data.to_csv(index=False).encode()
    else:
        content = json.dumps(data, sort_keys=True, default=str).encode()
    
    hasher.update(content)
    return hasher.hexdigest()
```

**Step 5: Create and store entry**

```python
from lib.artifacts import ArtifactStore, ArtifactEntry

def store_artifact(data, template_id: str, template_name: str, 
                   source: str, parameters: dict, config: dict) -> dict:
    """Store artifact and return metadata"""
    
    run_id = generate_run_id(template_id, parameters)
    artifact_path = save_artifact_data(data, run_id, config)
    checksum_algo = config.get("checksum", {}).get("algorithm", "sha256")
    checksum = calculate_checksum(data, checksum_algo)
    
    entry = ArtifactEntry(
        run_id=run_id,
        template_id=template_id,
        template_name=template_name,
        source=source,
        timestamp=datetime.now().isoformat(),
        parameters=parameters,
        row_count=len(data) if hasattr(data, '__len__') else 0,
        artifact_path=artifact_path,
        checksum=checksum,
        checksum_algorithm=checksum_algo,
        storage_backend=config["storage"]["backend"],
        resolved_query=parameters.get("resolved_query"),
        metadata={}
    )
    
    store = ArtifactStore(config)
    store.add_entry(entry)
    
    return {
        "action": "store",
        "success": True,
        "run_id": run_id,
        "artifact_path": artifact_path,
        "checksum": checksum,
        "row_count": entry.row_count,
        "template_id": template_id,
        "timestamp": entry.timestamp,
        "storage_backend": config["storage"]["backend"]
    }
```

### Action: "load"

Retrieve artifact data by run_id.

```python
def load_artifact(run_id: str, config: dict) -> dict:
    """Load artifact by run_id"""
    store = ArtifactStore(config)
    
    # Get entry metadata
    entry = store.get_entry(run_id)
    if not entry:
        return {"action": "load", "success": False, "error": f"Artifact not found: {run_id}"}
    
    # Load data based on storage backend
    data = load_from_backend(entry.artifact_path, entry.storage_backend, config)
    
    # Verify checksum if configured
    verify = config.get("checksum", {}).get("verify_on_load", True)
    checksum_valid = True
    
    if verify:
        calculated = calculate_checksum(data, entry.checksum_algorithm)
        checksum_valid = (calculated == entry.checksum)
        
        if not checksum_valid:
            print(f"WARNING: Checksum mismatch for {run_id}")
    
    return {
        "action": "load",
        "success": True,
        "run_id": run_id,
        "entry": entry.__dict__,
        "data": data,
        "checksum_valid": checksum_valid
    }

def load_from_backend(artifact_path: str, backend: str, config: dict):
    """Load data from specified storage backend"""
    if backend == "local":
        return load_from_local(artifact_path)
    elif backend == "s3":
        return load_from_s3(artifact_path, config["storage"]["s3"])
    elif backend == "gcs":
        return load_from_gcs(artifact_path, config["storage"]["gcs"])
    elif backend == "azure":
        return load_from_azure(artifact_path, config["storage"]["azure"])
    else:
        raise ValueError(f"Unknown storage backend: {backend}")
```

### Action: "list"

List recent artifacts, optionally filtered by template.

```python
def list_artifacts(template_id: str = None, limit: int = 50, config: dict = None) -> dict:
    """List artifacts with optional filtering"""
    store = ArtifactStore(config)
    
    entries = store.list_entries(template_id=template_id, limit=limit)
    
    return {
        "action": "list",
        "success": True,
        "total_count": len(entries),
        "returned_count": min(len(entries), limit),
        "filter": {"template_id": template_id} if template_id else None,
        "entries": [
            {
                "run_id": e.run_id,
                "template_id": e.template_id,
                "template_name": e.template_name,
                "timestamp": e.timestamp,
                "row_count": e.row_count,
                "storage_backend": e.storage_backend
            }
            for e in entries[:limit]
        ]
    }
```

### Action: "validate"

Verify artifact integrity via checksum.

```python
def validate_artifact(run_id: str, config: dict) -> dict:
    """Validate artifact integrity"""
    store = ArtifactStore(config)
    entry = store.get_entry(run_id)
    
    if not entry:
        return {"action": "validate", "valid": False, "error": "Artifact not found"}
    
    # Load and verify
    try:
        data = load_from_backend(entry.artifact_path, entry.storage_backend, config)
        calculated_checksum = calculate_checksum(data, entry.checksum_algorithm)
        is_valid = (calculated_checksum == entry.checksum)
        
        return {
            "action": "validate",
            "run_id": run_id,
            "valid": is_valid,
            "stored_checksum": entry.checksum,
            "calculated_checksum": calculated_checksum,
            "checksum_algorithm": entry.checksum_algorithm,
            "artifact_path": entry.artifact_path,
            "storage_backend": entry.storage_backend,
            "row_count": entry.row_count
        }
    except Exception as e:
        return {
            "action": "validate",
            "run_id": run_id,
            "valid": False,
            "error": str(e)
        }
```

---

## Output Schema

### Store Response

```json
{
  "action": "store",
  "success": true,
  "run_id": "at_risk_accounts_20260127_143022_a1b2",
  "artifact_path": "s3://my-bucket/artifacts/at_risk_accounts_20260127_143022_a1b2.csv",
  "checksum": "abc123...",
  "row_count": 47,
  "template_id": "at_risk_accounts",
  "timestamp": "2026-01-27T14:30:22Z",
  "storage_backend": "s3"
}
```

### Load Response

```json
{
  "action": "load",
  "success": true,
  "run_id": "at_risk_accounts_20260127_143022_a1b2",
  "entry": {
    "run_id": "at_risk_accounts_20260127_143022_a1b2",
    "template_id": "at_risk_accounts",
    "template_name": "At-Risk Accounts",
    "source": "snowflake",
    "timestamp": "2026-01-27T14:30:22Z",
    "parameters": {
      "min_arr": 10000,
      "limit": 50
    },
    "row_count": 47,
    "artifact_path": "s3://my-bucket/artifacts/at_risk_accounts_20260127_143022_a1b2.csv",
    "checksum": "abc123...",
    "checksum_algorithm": "sha256",
    "storage_backend": "s3"
  },
  "data": [
    {"account_id": "A-12345", "account_name": "Acme Corp"}
  ],
  "checksum_valid": true
}
```

### List Response

```json
{
  "action": "list",
  "success": true,
  "total_count": 127,
  "returned_count": 50,
  "filter": {
    "template_id": "at_risk_accounts"
  },
  "entries": [
    {
      "run_id": "at_risk_accounts_20260127_143022_a1b2",
      "template_id": "at_risk_accounts",
      "template_name": "At-Risk Accounts",
      "timestamp": "2026-01-27T14:30:22Z",
      "row_count": 47,
      "storage_backend": "s3"
    }
  ]
}
```

### Validate Response

```json
{
  "action": "validate",
  "run_id": "at_risk_accounts_20260127_143022_a1b2",
  "valid": true,
  "stored_checksum": "abc123...",
  "calculated_checksum": "abc123...",
  "checksum_algorithm": "sha256",
  "artifact_path": "s3://my-bucket/artifacts/at_risk_accounts_20260127_143022_a1b2.csv",
  "storage_backend": "s3",
  "row_count": 47
}
```

---

## Quality Criteria

- [ ] run_id is unique and descriptive
- [ ] Checksum matches stored data
- [ ] Index updated atomically
- [ ] Data file readable (CSV or JSON)
- [ ] Entry contains all required metadata
- [ ] Storage backend correctly configured

---

## Example Usage

**Store query results (local):**
```
Store this query result as artifact with template_id=at_risk_accounts
```

**Store to S3:**
```
Store query result to S3 with template_id=expansion_candidates
```

**Load cached data:**
```
Load artifact with run_id=at_risk_accounts_20260127_143022_a1b2
```

**List recent artifacts:**
```
List recent artifacts for template at_risk_accounts, limit 10
```

**Validate artifact:**
```
Validate integrity of artifact run_id=at_risk_accounts_20260127_143022_a1b2
```

---

## Index Structure

The artifact index (JSON format example):

```json
[
  {
    "run_id": "at_risk_accounts_20260127_143022_a1b2",
    "template_id": "at_risk_accounts",
    "template_name": "At-Risk Accounts",
    "source": "snowflake",
    "timestamp": "2026-01-27T14:30:22Z",
    "parameters": {
      "min_arr": 10000,
      "limit": 50
    },
    "row_count": 47,
    "artifact_path": "s3://my-bucket/artifacts/at_risk_accounts_20260127_143022_a1b2.csv",
    "checksum": "abc123def456...",
    "checksum_algorithm": "sha256",
    "storage_backend": "s3",
    "resolved_query": "SELECT ... FROM ... WHERE ..."
  }
]
```

Entries are stored **newest first** for efficient latest lookup.

---

## File Formats

| Data Type | File Extension | Format |
|-----------|---------------|--------|
| DataFrame | .csv | Standard CSV with headers |
| Dict/List | .json | Pretty-printed JSON |
| Text | .txt | Plain text |
| Binary | .parquet | Apache Parquet (compressed) |

---

## Integration with Other Skills

### Using Artifacts in Cohort Email Builder

```python
from lib.artifacts import ArtifactStore

config = load_config()
store = ArtifactStore(config)
cohort_data = store.load_artifact("at_risk_accounts_20260127_120000_x1y2")

# Process cohort data
from lib.communication_strategy import assign_reason_codes
companies_with_codes = assign_reason_codes(cohort_data.to_dict('records'))
```

### Using Artifacts in Playbook Executor

```python
# Get latest at-risk data
store = ArtifactStore(config)
latest = store.get_latest("at_risk_accounts")

if latest and (datetime.now() - datetime.fromisoformat(latest.timestamp)).days < 1:
    # Use cached data if less than 24 hours old
    data = store.load_artifact(latest.run_id)
else:
    # Run fresh query
    data = run_query(...)
    # Store for future use
    store_artifact(data, ...)
```

---

## Run ID Patterns

| Pattern | Example | Use Case |
|---------|---------|----------|
| `{template}_{date}_{time}_{hash}` | `at_risk_20260127_143022_a1b2` | Standard query result |
| `{cohort}_{date}_{time}_{hash}` | `retention_cohort_20260127_090000_c3d4` | Named cohort |
| `view_{date}_{time}_{hash}` | `view_20260127_143022_e5f6` | Dashboard view export |
| `campaign_{name}_{date}` | `campaign_retention_q1_20260127` | Campaign data |

---

## Retention and Cleanup

```python
def cleanup_old_artifacts(config: dict) -> int:
    """Remove artifacts older than retention period"""
    retention = config.get("retention", {})
    
    if not retention.get("enabled", True):
        return 0
    
    max_age_days = retention.get("max_age_days", 90)
    cutoff = datetime.now() - timedelta(days=max_age_days)
    
    store = ArtifactStore(config)
    entries = store.list_entries(limit=None)
    
    deleted = 0
    for entry in entries:
        entry_time = datetime.fromisoformat(entry.timestamp)
        if entry_time < cutoff:
            store.delete_artifact(entry.run_id)
            deleted += 1
    
    return deleted
```

---

## Notes

- Artifacts are immutable once stored (edit creates new entry)
- Index is sorted newest-first for efficient latest lookup
- Checksum verification recommended for data integrity
- CSV preferred for tabular data (easier inspection)
- JSON for complex nested structures
- Parquet for large datasets (better compression)
- Configure retention policy to manage storage costs
- Use appropriate storage backend for your infrastructure

---

## Changelog

### v2.0.0 (2026-01-28)
- Added multi-backend storage support (S3, GCS, Azure, MinIO)
- Added configurable index backends (JSON, SQLite, PostgreSQL, DynamoDB)
- Added checksum algorithm configuration
- Added retention policy and cleanup
- Removed hardcoded paths
- Added storage backend metadata to entries

### v1.0.0 (2026-01-27)
- Initial release
