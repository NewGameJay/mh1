---
name: playbook-executor
description: |
  Execute multi-step query sequences (playbooks) for common business intelligence workflows.
  Use when asked to 'run playbook', 'execute workflow', 'analyze segment', 
  'run analysis', or 'execute query sequence'.
license: Proprietary
compatibility:
  - Any data warehouse (Snowflake, BigQuery, Redshift, Databricks)
  - Any CRM (HubSpot, Salesforce, Marketo)
  - Custom data sources via API
metadata:
  author: mh1-engineering
  version: "2.0.0"
  status: active
  estimated_runtime: "2-5min"
  max_cost: "$1.00"
  client_facing: true
  requires_human_review: false
  tags:
    - orchestration
    - playbook
    - workflow
    - automation
    - analytics
allowed-tools: Read Write CallMcpTool
---

# Playbook Executor Skill

Execute pre-defined multi-step query sequences (playbooks) that combine multiple data sources for comprehensive business intelligence.

## Supported Platforms

### Data Warehouses

| Platform | Integration | Query Format |
|----------|------------|--------------|
| Snowflake | MCP (user-snowflake) | SQL |
| BigQuery | MCP or API | SQL |
| Redshift | API | SQL |
| Databricks | API | SQL/SparkSQL |
| PostgreSQL | Direct connection | SQL |

### CRM Platforms

| Platform | Integration | Query Format |
|----------|------------|--------------|
| HubSpot | MCP (user-hubspot) | Search API |
| Salesforce | MCP or API | SOQL |
| Marketo | API | REST filters |
| Klaviyo | API | Segments API |

### Other Data Sources

| Platform | Integration | Notes |
|----------|------------|-------|
| REST APIs | Configurable | Generic HTTP |
| GraphQL | Configurable | Query language |
| CSV/Parquet | File system | Static data |

---

## Configuration

Configuration is stored in `config/playbook-executor.yaml`:

```yaml
# config/playbook-executor.yaml
playbook_executor:
  # Default data sources
  defaults:
    data_warehouse: "snowflake"
    crm: "hubspot"
    
  # Connection settings (override per environment)
  connections:
    snowflake:
      mcp_server: "user-snowflake"
    bigquery:
      project: "${BIGQUERY_PROJECT}"
      dataset: "${BIGQUERY_DATASET}"
    hubspot:
      mcp_server: "user-hubspot"
    salesforce:
      instance_url: "${SALESFORCE_URL}"
      
  # Artifact storage
  artifacts:
    enabled: true
    directory: "artifacts"
    retention_days: 90
    
  # Execution settings
  execution:
    max_parallel_steps: 3
    timeout_seconds: 300
    retry_attempts: 2
```

Playbooks are defined in `config/playbooks/`:

```yaml
# config/playbooks/presales_analysis.yaml
playbook:
  id: "presales_analysis"
  name: "Presales Opportunity Analysis"
  description: "Analyze open opportunities with account health context"
  version: "1.0"
  
  # Required data sources
  data_sources:
    - type: "data_warehouse"
      required: true
    - type: "crm"
      required: true
      
  steps:
    - id: "open_deals"
      name: "Get Open Deals"
      source: "crm"
      type: "search"
      config:
        object: "deals"
        filters:
          - property: "dealstage"
            operator: "IN"
            values: ["qualifiedtobuy", "presentationscheduled", "decisionmakerboughtin"]
        properties:
          - "dealname"
          - "amount"
          - "closedate"
          - "dealstage"
          - "associated_company"
          
    - id: "account_health"
      name: "Get Account Health Context"
      source: "data_warehouse"
      type: "query"
      config:
        template: |
          SELECT 
            account_id,
            account_name,
            health_score,
            health_status,
            arr,
            owner_email
          FROM {{accounts_table}}
          WHERE account_id IN ({{account_ids}})
        parameters:
          accounts_table: "analytics.accounts"
          account_ids: "${steps.open_deals.company_ids}"
          
    - id: "combine_results"
      name: "Combine Deals with Health"
      source: "transform"
      type: "join"
      config:
        left: "${steps.open_deals}"
        right: "${steps.account_health}"
        on: "company_id = account_id"
        
  outputs:
    - name: "opportunities_with_health"
      source: "${steps.combine_results}"
    - name: "summary"
      type: "aggregate"
      metrics:
        - name: "total_pipeline"
          expression: "SUM(amount)"
        - name: "avg_health_score"
          expression: "AVG(health_score)"
        - name: "at_risk_deals"
          expression: "COUNT(*) WHERE health_status = 'At-Risk'"
```

---

## When to Use

Use this skill when you need to:
- Run a complete analysis workflow (not just one query)
- Analyze a customer segment from multiple angles
- Generate a comprehensive report combining data sources
- Execute a standardized analysis playbook

---

## Built-in Playbook Templates

These templates can be customized per client:

| Playbook ID | Name | Steps | Data Sources |
|-------------|------|-------|--------------|
| `presales_analysis` | Presales Opportunities | 3 | DW + CRM |
| `at_risk_renewals` | At-Risk Renewals | 3 | DW + CRM |
| `expansion_candidates` | Expansion Candidates | 2 | DW |
| `churn_risk` | Churn Risk Detection | 2 | DW + CRM |
| `health_dashboard` | Health Score Dashboard | 4 | DW |
| `segment_analysis` | Segment Deep Dive | 3 | DW + CRM |

---

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `playbook_id` | string | yes | Playbook identifier |
| `parameters` | object | no | Override default parameters |
| `save_artifacts` | boolean | no | Save results to artifact store (default: true) |
| `data_warehouse` | string | no | Override default data warehouse |
| `crm` | string | no | Override default CRM |

---

## Playbook Definition Schema

```yaml
playbook:
  id: "string"           # Unique identifier
  name: "string"         # Human-readable name
  description: "string"  # What this playbook does
  version: "string"      # Semantic version
  
  data_sources:          # Required data sources
    - type: "data_warehouse | crm | api"
      required: true | false
      
  parameters:            # User-configurable parameters
    - name: "string"
      type: "string | number | boolean | array"
      default: "any"
      description: "string"
      
  steps:                 # Execution steps
    - id: "string"       # Step identifier
      name: "string"     # Human-readable name
      source: "data_warehouse | crm | transform | api"
      type: "query | search | join | aggregate | filter"
      depends_on: ["step_id"]  # Optional dependencies
      config:            # Step-specific configuration
        # ... varies by step type
        
  outputs:               # Final outputs
    - name: "string"
      source: "${steps.step_id}"
      type: "data | aggregate"
```

---

## Step Types

### Query Step (data_warehouse)

```yaml
- id: "account_data"
  source: "data_warehouse"
  type: "query"
  config:
    template: |
      SELECT account_id, name, health_score
      FROM {{table}}
      WHERE health_status = {{status}}
      LIMIT {{limit}}
    parameters:
      table: "analytics.accounts"
      status: "'At-Risk'"
      limit: 100
```

### Search Step (crm)

```yaml
- id: "recent_contacts"
  source: "crm"
  type: "search"
  config:
    object: "contacts"
    filters:
      - property: "lifecyclestage"
        operator: "EQ"
        value: "customer"
    properties:
      - "email"
      - "firstname"
      - "lastname"
    limit: 100
```

### Transform Step

```yaml
- id: "enriched_data"
  source: "transform"
  type: "join"
  config:
    left: "${steps.account_data}"
    right: "${steps.recent_contacts}"
    on: "account_id = associated_company"
    type: "left"  # left, right, inner, outer
```

### Aggregate Step

```yaml
- id: "summary_stats"
  source: "transform"
  type: "aggregate"
  config:
    input: "${steps.enriched_data}"
    group_by: ["health_status"]
    metrics:
      - name: "count"
        expression: "COUNT(*)"
      - name: "total_arr"
        expression: "SUM(arr)"
      - name: "avg_health"
        expression: "AVG(health_score)"
```

### Filter Step

```yaml
- id: "high_value_only"
  source: "transform"
  type: "filter"
  config:
    input: "${steps.account_data}"
    condition: "arr >= 50000 AND health_score < 50"
```

---

## Process

### Step 1: Load Playbook Definition

```python
import yaml
from pathlib import Path

def load_playbook(playbook_id: str) -> dict:
    """Load playbook definition from config"""
    playbook_path = Path(f"config/playbooks/{playbook_id}.yaml")
    
    if not playbook_path.exists():
        # Check built-in templates
        playbook_path = Path(f"templates/playbooks/{playbook_id}.yaml")
    
    if not playbook_path.exists():
        raise ValueError(f"Playbook not found: {playbook_id}")
    
    with open(playbook_path) as f:
        return yaml.safe_load(f)["playbook"]
```

### Step 2: Validate Data Sources

```python
def validate_data_sources(playbook: dict, config: dict) -> dict:
    """Ensure required data sources are available"""
    connections = {}
    
    for source in playbook["data_sources"]:
        source_type = source["type"]
        
        if source_type == "data_warehouse":
            platform = config.get("data_warehouse", "snowflake")
            connections["data_warehouse"] = get_dw_connection(platform, config)
        elif source_type == "crm":
            platform = config.get("crm", "hubspot")
            connections["crm"] = get_crm_connection(platform, config)
        elif source_type == "api":
            connections["api"] = get_api_client(source.get("config", {}))
    
    return connections
```

### Step 3: Execute Steps

```python
def execute_playbook(playbook: dict, connections: dict, parameters: dict) -> dict:
    """Execute playbook steps in order, respecting dependencies"""
    results = {}
    
    # Build dependency graph
    steps = topological_sort(playbook["steps"])
    
    for step in steps:
        # Wait for dependencies
        if step.get("depends_on"):
            for dep_id in step["depends_on"]:
                if dep_id not in results:
                    raise RuntimeError(f"Dependency not satisfied: {dep_id}")
        
        # Resolve parameter references
        resolved_config = resolve_references(step["config"], results, parameters)
        
        # Execute step
        if step["source"] == "data_warehouse":
            result = execute_dw_query(connections["data_warehouse"], resolved_config)
        elif step["source"] == "crm":
            result = execute_crm_search(connections["crm"], resolved_config)
        elif step["source"] == "transform":
            result = execute_transform(step["type"], resolved_config, results)
        elif step["source"] == "api":
            result = execute_api_call(connections["api"], resolved_config)
        
        results[step["id"]] = {
            "step_id": step["id"],
            "name": step["name"],
            "source": step["source"],
            "status": "success",
            "row_count": len(result) if hasattr(result, '__len__') else 0,
            "data": result,
            "execution_time_ms": measure_time()
        }
    
    return results
```

### Step 4: Save Artifacts

```python
def save_artifacts(playbook_id: str, results: dict, config: dict) -> str:
    """Save results to artifact store"""
    from lib.artifacts import ArtifactStore
    
    store = ArtifactStore(config.get("artifacts_dir", "artifacts"))
    run_id = generate_run_id(playbook_id)
    
    store.save(
        run_id=run_id,
        playbook_id=playbook_id,
        results=results,
        timestamp=datetime.now().isoformat()
    )
    
    return run_id
```

### Step 5: Generate Insights

```python
def generate_insights(results: dict, playbook: dict) -> list:
    """Generate heuristic insights from results"""
    insights = []
    
    # Example insight generation
    for output in playbook.get("outputs", []):
        if output.get("type") == "aggregate":
            data = results[output["source"].replace("${steps.", "").replace("}", "")]
            
            # Generate summary insights
            if "total_arr" in data:
                insights.append(f"Total ARR in scope: ${data['total_arr']:,.0f}")
            if "count" in data:
                insights.append(f"Total accounts: {data['count']}")
    
    return insights
```

---

## Output Schema

```json
{
  "playbook_id": "string",
  "playbook_name": "string",
  "executed_at": "ISO timestamp",
  "run_id": "string",
  "steps": [
    {
      "step_id": "string",
      "name": "string",
      "source": "data_warehouse | crm | transform | api",
      "status": "success | error | skipped",
      "row_count": "number",
      "execution_time_ms": "number",
      "data": "array | object"
    }
  ],
  "summary": {
    "total_steps": "number",
    "successful_steps": "number",
    "total_execution_time_ms": "number"
  },
  "insights": ["string"],
  "artifact_path": "string (if saved)",
  "metadata": {
    "data_warehouse": "string",
    "crm": "string",
    "parameters_used": "object"
  }
}
```

---

## Example Usage

**Run presales analysis:**
```
Execute playbook presales_analysis
```

**Run at-risk renewal analysis:**
```
Run the at_risk_renewals playbook, save artifacts
```

**Expansion candidates with custom limit:**
```
Execute expansion_candidates with limit=50
```

**Custom parameters:**
```
Run playbook segment_analysis with parameters:
  - segment: "enterprise"
  - min_arr: 100000
  - health_threshold: 60
```

---

## Sample Output

```json
{
  "playbook_id": "at_risk_renewals",
  "playbook_name": "At-Risk Renewals",
  "executed_at": "2026-01-28T14:30:00Z",
  "run_id": "run_20260128_143000_abc123",
  "steps": [
    {
      "step_id": "health_distribution",
      "name": "Health Status Distribution",
      "source": "data_warehouse",
      "status": "success",
      "row_count": 5,
      "execution_time_ms": 1200
    },
    {
      "step_id": "at_risk_accounts",
      "name": "At-Risk High-Value Accounts",
      "source": "data_warehouse",
      "status": "success",
      "row_count": 240,
      "execution_time_ms": 890
    },
    {
      "step_id": "renewal_pipeline",
      "name": "Renewal Pipeline Deals",
      "source": "crm",
      "status": "success",
      "row_count": 23,
      "execution_time_ms": 450
    }
  ],
  "summary": {
    "total_steps": 3,
    "successful_steps": 3,
    "total_execution_time_ms": 2540
  },
  "insights": [
    "240 accounts at-risk with combined ARR of $3.2M",
    "23 renewals in pipeline totaling $1.27M",
    "Top at-risk account: Acme Corp ($156K ARR)"
  ],
  "artifact_path": "artifacts/run_20260128_143000_abc123.json",
  "metadata": {
    "data_warehouse": "snowflake",
    "crm": "hubspot",
    "parameters_used": {
      "limit": 100,
      "min_arr": 10000
    }
  }
}
```

---

## Creating Custom Playbooks

### Step 1: Create Playbook File

```yaml
# config/playbooks/my_custom_playbook.yaml
playbook:
  id: "my_custom_playbook"
  name: "My Custom Analysis"
  description: "Custom analysis for specific use case"
  version: "1.0"
  
  data_sources:
    - type: "data_warehouse"
      required: true
      
  parameters:
    - name: "min_value"
      type: "number"
      default: 10000
      description: "Minimum value threshold"
      
  steps:
    - id: "main_query"
      source: "data_warehouse"
      type: "query"
      config:
        template: |
          SELECT * FROM analytics.accounts
          WHERE arr >= {{min_value}}
        parameters:
          min_value: "${parameters.min_value}"
          
  outputs:
    - name: "results"
      source: "${steps.main_query}"
```

### Step 2: Test Playbook

```
Execute playbook my_custom_playbook with min_value=50000
```

### Step 3: Iterate and Refine

Add additional steps, transforms, and outputs as needed.

---

## Quality Criteria

- [ ] All steps execute successfully
- [ ] Results saved to artifact store
- [ ] Insights generated from data
- [ ] Execution time reasonable (< 60s total)

---

## Error Handling

| Error | Action |
|-------|--------|
| Data warehouse connection failed | Return cached results if available |
| CRM rate limit | Retry with exponential backoff |
| Step timeout | Mark step as failed, continue if possible |
| Invalid playbook_id | Return error with valid options |
| Parameter validation failed | Return error with expected format |
| Dependency cycle detected | Return error, do not execute |

---

## Notes

- Playbooks are defined in `config/playbooks/` (YAML format)
- Built-in templates in `templates/playbooks/` can be customized
- Artifacts stored with checksums for auditability
- Run IDs enable reproducibility
- Add new playbooks by creating new YAML files

---

## Changelog

### v2.0.0 (2026-01-28)
- Converted to platform-agnostic framework
- Added support for multiple data warehouses
- Added support for multiple CRMs
- Implemented configurable playbook definitions
- Added step types: query, search, join, aggregate, filter
- Added dependency management between steps
- Removed hardcoded playbook references

### v1.0.0 (2026-01-27)
- Initial release
