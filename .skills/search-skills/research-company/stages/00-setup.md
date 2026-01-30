# Stage 00: Setup & Validation

## Purpose

Validate inputs, check prerequisites, verify website accessibility, and prepare the execution environment for company research.

## Model

N/A - No LLM required for validation

## Inputs Required

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | string | Yes | Unique client identifier |
| `company_name` | string | Yes | Official company name |
| `website_url` | string | Yes | Primary company website URL |
| `additional_urls` | array | No | Additional URLs to analyze |
| `industry` | string | No | Industry vertical (auto-detected if not provided) |
| `depth` | string | No | Research depth: quick, standard, deep |
| `execution_mode` | string | No | suggest, preview, or execute |
| `tenant_id` | string | No | Tenant ID for cost tracking |

## Validation Steps

### 1. Validate Required Inputs

```python
# Validate client_id
if not inputs.get("client_id"):
    raise ValidationError("client_id is required")

# Validate company_name
if not inputs.get("company_name"):
    raise ValidationError("company_name is required")

# Validate website_url
website_url = inputs.get("website_url")
if not website_url:
    raise ValidationError("website_url is required")

# Validate URL format
if not is_valid_url(website_url):
    raise ValidationError(f"Invalid URL format: {website_url}")
```

### 2. Check Website Accessibility

```python
# Attempt to reach the website
try:
    response = check_url_accessible(website_url, timeout=10)
    if response.status_code >= 400:
        raise ValidationError(f"Website returned error: {response.status_code}")
except ConnectionError:
    raise ValidationError(f"Website unreachable: {website_url}")
```

### 3. Validate Additional URLs (if provided)

```python
additional_urls = inputs.get("additional_urls", [])
valid_additional_urls = []
for url in additional_urls:
    if is_valid_url(url) and check_url_accessible(url):
        valid_additional_urls.append(url)
    else:
        log_warning(f"Skipping inaccessible URL: {url}")
```

### 4. Check MCP Connections

```python
# Verify Firecrawl MCP is available
if not mcp_connected("firecrawl"):
    raise ConnectionError("Firecrawl MCP not connected - required for web scraping")

# Optionally check SerpAPI for additional search
if mcp_connected("serpapi"):
    enable_search_enrichment = True
```

### 5. Load Configuration

```python
# Load depth configuration
depth = inputs.get("depth", "standard")
depth_config = load_config("config/defaults.yaml")["depth"][depth]

# Set runtime parameters
max_pages = depth_config["max_pages"]
timeout = depth_config["timeout_seconds"]
```

### 6. Initialize Client Directory

```python
# Ensure client directory structure exists
client_dir = f"clients/{client_id}"
ensure_directory(f"{client_dir}/research")
ensure_directory(f"{client_dir}/context")
```

## Output

| Name | Type | Description |
|------|------|-------------|
| `validated_inputs` | object | Cleaned and validated input parameters |
| `website_accessible` | boolean | Website accessibility status |
| `additional_urls` | array | Validated additional URLs |
| `depth_config` | object | Loaded depth configuration |
| `execution_config` | object | Runtime configuration |
| `mcp_status` | object | Status of required MCP connections |

## Checkpoint

This stage does not create a checkpoint (always re-runs for fresh validation).

## Error Handling

| Error | Trigger | Action |
|-------|---------|--------|
| Missing required input | client_id, company_name, or website_url not provided | Exit with ValidationError |
| Invalid URL format | URL fails format validation | Exit with ValidationError |
| Website unreachable | Primary URL returns 4xx/5xx or times out | Exit with ConnectionError, suggest alternatives |
| Firecrawl not connected | MCP connection failed | Exit with ConnectionError, provide setup instructions |
| Additional URL failed | Secondary URL inaccessible | Log warning, continue with primary URL |

## Success Criteria

- [ ] All required inputs validated
- [ ] Primary website accessible
- [ ] Firecrawl MCP connected
- [ ] Client directory structure ready
- [ ] Depth configuration loaded
