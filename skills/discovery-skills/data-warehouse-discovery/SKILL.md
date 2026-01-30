---
name: data-warehouse-discovery
description: |
  Explore data warehouses for customer intelligence, health scores, ARR, lifecycle data, and analytics.
  Use when asked to 'query data warehouse', 'explore customer data', 'check health scores', 
  'find ARR data', 'discover warehouse tables', or 'analyze customer data'.
license: MIT
compatibility:
  - Snowflake MCP (user-snowflake)
  - BigQuery API
  - Redshift via PostgreSQL driver
  - Databricks SQL connector
  - PostgreSQL MCP
metadata:
  author: mh1-engineering
  version: "2.0.0"
  status: active
  estimated_runtime: "1-5min"
  max_cost: "$0.50"
  client_facing: false
  requires_human_review: false
  tags:
    - data-warehouse
    - data-discovery
    - customer-intelligence
    - snowflake
    - bigquery
    - redshift
    - databricks
    - postgresql
allowed-tools: Read Write CallMcpTool Shell
---

# Data Warehouse Discovery Skill

Explore and query data warehouses for customer intelligence, health scores, ARR analysis, and lifecycle data across multiple platforms.

## When to Use

Use this skill when you need to:
- Explore available tables and schemas in any data warehouse
- Query health status distribution
- Analyze ARR by account or tier
- Find at-risk or churned accounts
- Investigate customer lifecycle data
- Run ad-hoc analytics queries

## Supported Platforms

| Platform | MCP/Driver | Connection Method |
|----------|-----------|-------------------|
| **Snowflake** | `user-snowflake` MCP | Native MCP tools |
| **BigQuery** | BigQuery API | Service account JSON |
| **Redshift** | PostgreSQL driver | JDBC/psycopg2 |
| **Databricks** | SQL connector | Personal access token |
| **PostgreSQL** | PostgreSQL MCP | Native MCP tools |

## Configuration

Configure your warehouse connection in `clients/{clientId}/config/warehouse.yaml`:

```yaml
warehouse:
  type: "{warehouse_type}"  # snowflake | bigquery | redshift | databricks | postgresql
  
  # Connection settings (platform-specific)
  snowflake:
    account: "{SNOWFLAKE_ACCOUNT}"
    user: "{SNOWFLAKE_USER}"
    warehouse: "{SNOWFLAKE_WAREHOUSE}"
    database: "{SNOWFLAKE_DATABASE}"
    schema: "{SNOWFLAKE_SCHEMA}"
    
  bigquery:
    project_id: "{GCP_PROJECT_ID}"
    dataset: "{BQ_DATASET}"
    credentials_file: "{GCP_CREDENTIALS_PATH}"
    
  redshift:
    host: "{REDSHIFT_HOST}"
    port: 5439
    database: "{REDSHIFT_DATABASE}"
    user: "{REDSHIFT_USER}"
    
  databricks:
    host: "{DATABRICKS_HOST}"
    http_path: "{DATABRICKS_HTTP_PATH}"
    catalog: "{DATABRICKS_CATALOG}"
    schema: "{DATABRICKS_SCHEMA}"
    
  postgresql:
    host: "{PG_HOST}"
    port: 5432
    database: "{PG_DATABASE}"
    user: "{PG_USER}"

  # Schema mapping (customize per client)
  tables:
    customers: "{customer_table}"        # e.g., "customers", "accounts", "orgs"
    health_scores: "{health_scores_table}"
    events: "{events_table}"
    users: "{users_table}"
    transactions: "{transactions_table}"
```

## Generic Query Templates

### Health & Status Queries

| Query ID | Description | Parameters |
|----------|-------------|------------|
| `dw_health_status_distribution` | Distribution of accounts by health status with ARR | `{health_scores_table}` |
| `dw_at_risk_high_value` | Accounts with ARR >= threshold marked At-Risk | `arr_threshold` (default: 24000) |
| `dw_churned_accounts` | Churned accounts with reactivation potential | `min_arr`, `limit` |
| `dw_dormant_high_value` | Active subscriptions with no activity N+ days | `days_inactive`, `min_arr`, `limit` |

### ARR & Revenue Queries

| Query ID | Description | Parameters |
|----------|-------------|------------|
| `dw_top_accounts_arr` | Top accounts sorted by ARR | `limit` (default: 20) |
| `dw_arr_by_segment` | ARR breakdown by customer segment | `segment_field` |
| `dw_revenue_trends` | Monthly/quarterly revenue trends | `period`, `months` |

### Activity & Engagement Queries

| Query ID | Description | Parameters |
|----------|-------------|------------|
| `dw_recent_activity` | Event activity for account (last N days) | `account_id`, `days` |
| `dw_engagement_velocity` | This period vs last period comparison | `account_id`, `period` |
| `dw_conversion_funnel` | Event funnel analysis | `account_id`, `funnel_stages` |
| `dw_session_patterns` | Daily activity and duration | `account_id` |

### Sales & Performance Queries

| Query ID | Description | Parameters |
|----------|-------------|------------|
| `dw_sales_activity_by_rep` | Metrics by sales/CS owner | `owner_field`, `days` |
| `dw_deal_velocity` | Health trends and conversion rates | `pipeline_field` |
| `dw_customer_lifecycle_distribution` | Breakdown by lifecycle stage | `lifecycle_field` |

## Process

### Step 1: Identify Platform and Connect

**Snowflake (via MCP):**
```
Call: snowflake_show_context to verify connection
```

**BigQuery (via API):**
```python
from google.cloud import bigquery
client = bigquery.Client(project="{GCP_PROJECT_ID}")
```

**Redshift (via psycopg2):**
```python
import psycopg2
conn = psycopg2.connect(
    host="{REDSHIFT_HOST}",
    port=5439,
    dbname="{REDSHIFT_DATABASE}",
    user="{REDSHIFT_USER}",
    password="{REDSHIFT_PASSWORD}"
)
```

**Databricks (via connector):**
```python
from databricks import sql
conn = sql.connect(
    server_hostname="{DATABRICKS_HOST}",
    http_path="{DATABRICKS_HTTP_PATH}",
    access_token="{DATABRICKS_TOKEN}"
)
```

### Step 2: Discover Available Data

**Snowflake:**
```sql
SHOW SCHEMAS IN DATABASE {database};
SHOW TABLES IN SCHEMA {database}.{schema};
DESCRIBE TABLE {database}.{schema}.{table};
```

**BigQuery:**
```sql
SELECT table_name FROM `{project}.{dataset}.INFORMATION_SCHEMA.TABLES`;
SELECT column_name, data_type FROM `{project}.{dataset}.INFORMATION_SCHEMA.COLUMNS` WHERE table_name = '{table}';
```

**Redshift:**
```sql
SELECT schemaname, tablename FROM pg_tables WHERE schemaname NOT IN ('pg_catalog', 'information_schema');
SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}';
```

**Databricks:**
```sql
SHOW SCHEMAS IN {catalog};
SHOW TABLES IN {catalog}.{schema};
DESCRIBE TABLE {catalog}.{schema}.{table};
```

**PostgreSQL:**
```sql
SELECT schemaname, tablename FROM pg_tables WHERE schemaname = 'public';
\d {table}
```

### Step 3: Execute Query

**Generic Health Status Distribution:**

```sql
-- Adjust table/column names based on client configuration
SELECT 
    {health_status_column} AS health_status,
    COUNT(DISTINCT {account_id_column}) AS account_count,
    SUM({arr_column}) AS total_arr,
    AVG({health_score_column}) AS avg_health_score
FROM {health_scores_table}
WHERE {snapshot_date_column} = CURRENT_DATE - INTERVAL '1 day'
GROUP BY {health_status_column}
ORDER BY total_arr DESC;
```

**Generic At-Risk High Value:**

```sql
SELECT 
    {account_id_column},
    {account_name_column},
    {arr_column},
    {health_status_column},
    {owner_column}
FROM {health_scores_table}
WHERE {health_status_column} = 'At-Risk'
  AND {arr_column} >= :arr_threshold
ORDER BY {arr_column} DESC
LIMIT :limit;
```

### Step 4: Format Results

Return results as:
- Summary statistics (totals, averages)
- Top N records for detailed queries
- Formatted markdown table

## Common Schema Patterns

### Customer/Account Table
```
{customer_table}:
  - account_id (PK)
  - account_name
  - domain
  - industry
  - segment
  - arr / mrr
  - created_at
  - owner_id
```

### Health Scores Table
```
{health_scores_table}:
  - account_id (FK)
  - snapshot_date
  - health_score (0-100)
  - health_status (Healthy, At-Risk, Churned)
  - arr
  - owner_id
```

### Events Table
```
{events_table}:
  - event_id (PK)
  - account_id (FK)
  - user_id (FK)
  - event_type
  - event_timestamp
  - properties (JSON)
```

### Users Table
```
{users_table}:
  - user_id (PK)
  - account_id (FK)
  - email
  - role
  - last_active_at
```

## Output Schema

```json
{
  "query_id": "string",
  "platform": "{warehouse_type}",
  "executed_at": "ISO timestamp",
  "row_count": "number",
  "execution_time_ms": "number",
  "results": [
    { "column1": "value1", "column2": "value2" }
  ],
  "summary": {
    "total_records": "number",
    "total_arr": "number (if applicable)",
    "key_insights": ["string"]
  }
}
```

## Quality Criteria

- [ ] Query executes without error
- [ ] Results match expected schema
- [ ] Execution time < 30 seconds
- [ ] Row count matches expected range
- [ ] No PII exposed in output

## Platform-Specific Notes

### Snowflake
- Use `CURRENT_DATE - 1` for date arithmetic
- Supports semi-structured data (VARIANT type)
- Case-sensitive identifiers when quoted

### BigQuery
- Use `DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)` for date arithmetic
- Supports nested/repeated fields (STRUCT, ARRAY)
- Table references use backticks: `` `project.dataset.table` ``

### Redshift
- PostgreSQL-compatible syntax
- Use `GETDATE() - INTERVAL '1 day'` for dates
- Requires `UNLOAD` for large exports

### Databricks
- Unity Catalog uses 3-level namespace: `catalog.schema.table`
- Supports Delta Lake time travel
- Use `CURRENT_DATE - INTERVAL 1 DAY` for dates

### PostgreSQL
- Standard SQL syntax
- Use `CURRENT_DATE - INTERVAL '1 day'` for dates
- `\d` commands for schema discovery (psql only)

## Known Limitations

1. **Event data location varies** - may be in separate system (check client config)
2. **Health score availability** - not all clients have health scoring
3. **Demo mode** may return cached data if credentials unavailable
4. **Cross-platform joins** require identity mapping skill

## Notes

- Always verify table/column names from client configuration
- Add `LIMIT` to heavy queries to control cost
- Log all queries to telemetry for cost tracking
- Use parameterized queries to prevent SQL injection
