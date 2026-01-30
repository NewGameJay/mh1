---
name: data-quality-audit
description: |
  Audit data coverage, null rates, and join accuracy between data warehouse and CRM systems.
  Use when asked to 'check data quality', 'audit coverage', 'validate joins', 
  'find null rates', or 'assess data health'.
license: Proprietary
compatibility:
  - Any data warehouse (Snowflake, BigQuery, Redshift, Databricks)
  - Any CRM (HubSpot, Salesforce, Marketo)
metadata:
  author: mh1-engineering
  version: "2.0.0"
  status: active
  created: "2026-01-27"
  updated: "2026-01-28"
  estimated_runtime: "3-8min"
  max_runtime: "20min"
  estimated_cost: "$0.50"
  max_cost: "$1.50"
  client_facing: false
  requires_human_review: false
  tags:
    - data-quality
    - audit
    - integration
    - analytics
allowed-tools: Read Write CallMcpTool
---

# Data Quality Audit Skill

Comprehensive audit of data coverage, null rates, and cross-system join accuracy for data warehouse and CRM data.

## Supported Platforms

### Data Warehouses

| Platform | Integration | Notes |
|----------|------------|-------|
| Snowflake | MCP (user-snowflake) | Primary support |
| BigQuery | MCP or API | Google Cloud |
| Redshift | API | AWS |
| Databricks | API | Unified analytics |
| PostgreSQL | Direct connection | On-premise option |

### CRM Platforms

| Platform | Integration | Notes |
|----------|------------|-------|
| HubSpot | MCP (user-hubspot) | Contact/Company model |
| Salesforce | MCP or API | Lead/Contact/Account model |
| Marketo | API | Lead model |
| Dynamics 365 | API | Microsoft CRM |

---

## Configuration

Configuration is stored in `config/data-quality-audit.yaml`:

```yaml
# config/data-quality-audit.yaml
data_quality_audit:
  # Data warehouse settings
  data_warehouse:
    platform: "snowflake"  # snowflake, bigquery, redshift, databricks, postgres
    
  # CRM settings
  crm:
    platform: "hubspot"  # hubspot, salesforce, marketo, dynamics
    
  # Schema mappings (customize per client)
  schema:
    # Primary accounts/customers table
    accounts:
      table: "analytics.accounts"
      primary_key: "account_id"
      fields:
        account_id: "account_id"
        account_name: "name"
        health_score: "health_score"
        health_status: "health_status"
        arr: "annual_revenue"
        owner: "owner_email"
        crm_id: "crm_company_id"
        created_at: "created_date"
        
    # Health scores table (if separate)
    health_scores:
      table: "analytics.health_scores_daily"
      date_field: "report_date"
      fields:
        account_id: "account_id"
        health_score: "health_score"
        health_status: "health_status"
        
    # Contacts table
    contacts:
      table: "analytics.contacts"
      fields:
        contact_id: "contact_id"
        email: "email"
        account_id: "account_id"
        crm_id: "crm_contact_id"
        
    # Events/activity table
    events:
      table: "analytics.events"
      fields:
        event_id: "event_id"
        account_id: "account_id"
        event_type: "event_type"
        event_date: "event_timestamp"
        
  # Identity mapping configuration
  identity_mapping:
    # Primary join strategy
    primary_join:
      left_table: "accounts"
      left_field: "crm_id"
      right_source: "crm"
      right_field: "company_id"
      
    # Fallback join strategies
    fallback_joins:
      - name: "billing_id_match"
        left_field: "billing_account_ids"
        match_type: "contains"  # exact, contains, fuzzy
      - name: "domain_match"
        left_field: "domain"
        right_field: "website_domain"
        match_type: "exact"
        
  # Quality thresholds
  thresholds:
    coverage:
      healthy: 0.85
      warning: 0.70
      critical: 0.50
    null_rate:
      healthy: 0.05
      warning: 0.20
      critical: 0.50
    join_accuracy:
      healthy: 0.95
      warning: 0.85
      critical: 0.70
      
  # Fields to audit
  audit_fields:
    critical:
      - "account_id"
      - "health_status"
      - "arr"
    important:
      - "health_score"
      - "owner"
      - "crm_id"
    optional:
      - "industry"
      - "employee_count"
      
  # Known issues (document expected problems)
  known_issues:
    - field: "churn_reason"
      expected_null_rate: 0.95
      note: "Field mostly unpopulated - use health_status transitions as proxy"
    - field: "secondary_contact"
      expected_null_rate: 0.80
      note: "Optional field, many accounts have single contact"
```

---

## When to Use

Use this skill when you need to:
- Validate data completeness before campaigns
- Check identity mapping accuracy
- Find fields with high null rates
- Assess cross-system join quality
- Document data gaps for engineering

Do NOT use when:
- Running time-sensitive queries (audits are slow)
- Looking for specific records (use targeted queries)

---

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `audit_type` | string | no | "full" | "full", "coverage", "nulls", or "joins" |
| `tables` | array | no | all configured | Tables to audit |
| `threshold_warn` | number | no | config default | Coverage below this triggers warning |
| `threshold_fail` | number | no | config default | Coverage below this triggers failure |
| `data_warehouse` | string | no | config default | Override data warehouse platform |
| `crm` | string | no | config default | Override CRM platform |

---

## Outputs

| Name | Type | Description |
|------|------|-------------|
| `coverage_metrics` | object | Field coverage percentages |
| `null_rates` | object | Null rate analysis by field |
| `join_accuracy` | object | Cross-system join statistics |
| `recommendations` | array | Actions to improve data quality |
| `overall_health` | string | "healthy", "warning", "critical" |

---

## Dependencies

| Type | Name | Purpose |
|------|------|---------|
| MCP | Configured data warehouse | Run audit queries |
| MCP | Configured CRM | Validate CRM data |
| Config | `config/data-quality-audit.yaml` | Schema and thresholds |

---

## Process

### Step 1: Load Configuration

```python
import yaml

def load_audit_config() -> dict:
    """Load data quality audit configuration"""
    with open("config/data-quality-audit.yaml") as f:
        return yaml.safe_load(f)["data_quality_audit"]
```

### Step 2: Coverage Metrics

Query coverage for identity and critical fields:

```python
def build_coverage_query(config: dict) -> str:
    """Build coverage metrics query based on configuration"""
    schema = config["schema"]["accounts"]
    table = schema["table"]
    fields = schema["fields"]
    
    # Build SELECT for each field
    field_queries = []
    for field_name, column in fields.items():
        field_queries.append(f"""
        SELECT
            '{field_name}' as FIELD,
            COUNT(*) as TOTAL_RECORDS,
            COUNT({column}) as NON_NULL,
            ROUND(COUNT({column}) * 100.0 / COUNT(*), 2) as COVERAGE_PCT
        FROM {table}
        """)
    
    return " UNION ALL ".join(field_queries)
```

**Generic coverage query template:**

```sql
-- Coverage metrics for configured fields
SELECT
    '{field_name}' as FIELD,
    COUNT(*) as TOTAL_RECORDS,
    COUNT({column_name}) as NON_NULL,
    ROUND(COUNT({column_name}) * 100.0 / NULLIF(COUNT(*), 0), 2) as COVERAGE_PCT
FROM {table_name}
{where_clause}
```

**Platform-specific syntax:**

| Platform | NULL check | Percentage |
|----------|-----------|------------|
| Snowflake | `COUNT(column)` | `ROUND(x * 100.0 / y, 2)` |
| BigQuery | `COUNTIF(column IS NOT NULL)` | `ROUND(x * 100 / y, 2)` |
| Redshift | `COUNT(column)` | `ROUND(x::numeric * 100 / y, 2)` |
| PostgreSQL | `COUNT(column)` | `ROUND(x::numeric * 100 / y, 2)` |

### Step 3: Null Rate Checks

```python
def build_null_rate_query(config: dict, table_key: str) -> str:
    """Build null rate query for critical fields"""
    schema = config["schema"][table_key]
    table = schema["table"]
    fields = schema["fields"]
    date_field = schema.get("date_field")
    
    # Build WHERE clause for latest data if date field exists
    where_clause = ""
    if date_field:
        where_clause = f"""
        WHERE {date_field} = (SELECT MAX({date_field}) FROM {table})
        """
    
    field_queries = []
    for field_name in config["audit_fields"]["critical"]:
        if field_name in fields:
            column = fields[field_name]
            field_queries.append(f"""
            SELECT
                '{field_name}' as FIELD,
                SUM(CASE WHEN {column} IS NULL THEN 1 ELSE 0 END) as NULL_COUNT,
                COUNT(*) as TOTAL,
                ROUND(SUM(CASE WHEN {column} IS NULL THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as NULL_PCT
            FROM {table}
            {where_clause}
            """)
    
    return " UNION ALL ".join(field_queries)
```

### Step 4: Identity Mapping Accuracy

```python
def build_join_accuracy_query(config: dict) -> str:
    """Build query to measure identity mapping accuracy"""
    identity = config["identity_mapping"]
    accounts = config["schema"]["accounts"]
    
    primary_join = identity["primary_join"]
    
    # Primary join accuracy
    queries = [f"""
    WITH primary_join AS (
        SELECT COUNT(DISTINCT a.{accounts["fields"]["account_id"]}) as matched
        FROM {accounts["table"]} a
        WHERE a.{accounts["fields"][primary_join["left_field"]]} IS NOT NULL
    ),
    total AS (
        SELECT COUNT(DISTINCT {accounts["fields"]["account_id"]}) as total
        FROM {accounts["table"]}
    )
    SELECT 
        'PRIMARY_JOIN' as JOIN_METHOD,
        p.matched as MATCHED,
        t.total as TOTAL,
        ROUND(p.matched * 100.0 / NULLIF(t.total, 0), 2) as MATCH_RATE_PCT
    FROM primary_join p, total t
    """]
    
    # Add fallback join queries
    for fallback in identity.get("fallback_joins", []):
        queries.append(build_fallback_join_query(fallback, config))
    
    return " UNION ALL ".join(queries)
```

### Step 5: CRM Data Quality Check

Query CRM to validate data freshness and completeness:

**HubSpot:**
```python
def check_hubspot_quality(config: dict) -> dict:
    """Check HubSpot data quality"""
    # Search for customers
    search_params = {
        "filterGroups": [{
            "filters": [{
                "propertyName": "lifecyclestage",
                "operator": "EQ",
                "value": "customer"
            }]
        }],
        "properties": [
            "email", "company", "hubspot_owner_id", 
            "notes_last_updated", "hs_email_last_open_date"
        ],
        "limit": 100
    }
    
    results = hubspot_mcp.search_contacts(search_params)
    
    # Calculate quality metrics
    total = len(results)
    missing_owner = sum(1 for r in results if not r.get("hubspot_owner_id"))
    missing_company = sum(1 for r in results if not r.get("company"))
    
    return {
        "total_sampled": total,
        "missing_owner_pct": missing_owner / total if total > 0 else 0,
        "missing_company_pct": missing_company / total if total > 0 else 0
    }
```

**Salesforce:**
```python
def check_salesforce_quality(config: dict) -> dict:
    """Check Salesforce data quality"""
    query = """
        SELECT Id, Email, AccountId, OwnerId, LastActivityDate
        FROM Contact
        WHERE Account.Type = 'Customer'
        LIMIT 100
    """
    
    results = salesforce_api.query(query)
    
    # Calculate quality metrics
    total = len(results)
    missing_account = sum(1 for r in results if not r.get("AccountId"))
    missing_owner = sum(1 for r in results if not r.get("OwnerId"))
    
    return {
        "total_sampled": total,
        "missing_account_pct": missing_account / total if total > 0 else 0,
        "missing_owner_pct": missing_owner / total if total > 0 else 0
    }
```

### Step 6: Generate Health Assessment

```python
def assess_data_health(coverage_metrics: dict, null_rates: dict, 
                       join_accuracy: dict, config: dict) -> dict:
    """Assess overall data health based on metrics and thresholds"""
    thresholds = config["thresholds"]
    known_issues = {i["field"]: i for i in config.get("known_issues", [])}
    issues = []
    
    # Coverage checks
    for field, metrics in coverage_metrics.items():
        coverage = metrics["coverage_pct"] / 100
        
        if coverage < thresholds["coverage"]["critical"]:
            issues.append({
                "severity": "critical",
                "field": field,
                "metric": "coverage",
                "value": coverage,
                "threshold": thresholds["coverage"]["critical"]
            })
        elif coverage < thresholds["coverage"]["warning"]:
            issues.append({
                "severity": "warning",
                "field": field,
                "metric": "coverage",
                "value": coverage,
                "threshold": thresholds["coverage"]["warning"]
            })
    
    # Null rate checks (skip known issues)
    for field, metrics in null_rates.items():
        null_rate = metrics["null_pct"] / 100
        
        # Check if this is a known issue
        if field in known_issues:
            expected = known_issues[field].get("expected_null_rate", 0)
            if null_rate <= expected * 1.1:  # Allow 10% tolerance
                continue  # Skip, this is expected
        
        if null_rate > thresholds["null_rate"]["critical"]:
            issues.append({
                "severity": "critical",
                "field": field,
                "metric": "null_rate",
                "value": null_rate,
                "threshold": thresholds["null_rate"]["critical"]
            })
        elif null_rate > thresholds["null_rate"]["warning"]:
            issues.append({
                "severity": "warning",
                "field": field,
                "metric": "null_rate",
                "value": null_rate,
                "threshold": thresholds["null_rate"]["warning"]
            })
    
    # Join accuracy checks
    for method, metrics in join_accuracy.items():
        accuracy = metrics["match_rate_pct"] / 100
        
        if accuracy < thresholds["join_accuracy"]["critical"]:
            issues.append({
                "severity": "critical",
                "metric": "join_accuracy",
                "method": method,
                "value": accuracy,
                "threshold": thresholds["join_accuracy"]["critical"]
            })
        elif accuracy < thresholds["join_accuracy"]["warning"]:
            issues.append({
                "severity": "warning",
                "metric": "join_accuracy",
                "method": method,
                "value": accuracy,
                "threshold": thresholds["join_accuracy"]["warning"]
            })
    
    # Determine overall health
    critical_count = sum(1 for i in issues if i["severity"] == "critical")
    warning_count = sum(1 for i in issues if i["severity"] == "warning")
    
    if critical_count > 0:
        overall_health = "critical"
    elif warning_count > 3:
        overall_health = "warning"
    else:
        overall_health = "healthy"
    
    return {
        "overall_health": overall_health,
        "issues": issues,
        "summary": {
            "critical_issues": critical_count,
            "warning_issues": warning_count
        }
    }
```

### Step 7: Generate Recommendations

```python
def generate_recommendations(health_assessment: dict, config: dict) -> list:
    """Generate actionable recommendations based on issues"""
    recommendations = []
    
    for issue in health_assessment["issues"]:
        if issue["metric"] == "coverage":
            recommendations.append(
                f"COVERAGE: Field '{issue['field']}' has {issue['value']*100:.1f}% coverage "
                f"(threshold: {issue['threshold']*100:.0f}%). "
                f"Consider implementing data enrichment or making field required."
            )
        elif issue["metric"] == "null_rate":
            recommendations.append(
                f"NULL RATE: Field '{issue['field']}' has {issue['value']*100:.1f}% null rate. "
                f"Review data pipeline for this field."
            )
        elif issue["metric"] == "join_accuracy":
            recommendations.append(
                f"JOIN ACCURACY: {issue['method']} has {issue['value']*100:.1f}% match rate. "
                f"Review identity resolution logic."
            )
    
    # Add general recommendations
    if health_assessment["overall_health"] != "healthy":
        recommendations.append(
            "Schedule weekly data quality audits to track trends."
        )
    
    return recommendations
```

---

## Output Schema

```json
{
  "audit_timestamp": "ISO datetime",
  "overall_health": "healthy | warning | critical",
  "platforms": {
    "data_warehouse": "string",
    "crm": "string"
  },
  "coverage_metrics": {
    "account_id": {
      "total_records": "number",
      "non_null": "number",
      "coverage_pct": "number"
    },
    "crm_id": {
      "total_records": "number",
      "non_null": "number",
      "coverage_pct": "number"
    }
  },
  "null_rates": {
    "health_status": {
      "null_count": "number",
      "total": "number",
      "null_pct": "number"
    },
    "known_issue_field": {
      "null_count": "number",
      "total": "number",
      "null_pct": "number",
      "note": "Known issue - field mostly unpopulated"
    }
  },
  "join_accuracy": {
    "primary_join": {
      "method": "description",
      "matched": "number",
      "total": "number",
      "match_rate_pct": "number"
    },
    "fallback_join": {
      "method": "description",
      "matched": "number",
      "total": "number",
      "match_rate_pct": "number"
    },
    "recommendation": "Use primary join for best accuracy"
  },
  "crm_quality": {
    "total_sampled": "number",
    "missing_owner_pct": "number",
    "missing_company_pct": "number"
  },
  "issues": [
    {
      "severity": "critical | warning | info",
      "field": "string",
      "metric": "coverage | null_rate | join_accuracy",
      "value": "number",
      "threshold": "number",
      "description": "string",
      "impact": "string",
      "remediation": "string"
    }
  ],
  "recommendations": ["string"]
}
```

---

## Quality Criteria

- [ ] All audit queries execute without error
- [ ] Coverage metrics calculated correctly
- [ ] Known issues documented and excluded from alerts
- [ ] Join accuracy comparison complete
- [ ] Recommendations are actionable

---

## Example Usage

**Full data quality audit:**
```
Run data quality audit with full checks
```

**Coverage-only audit:**
```
Check data coverage for identity fields
```

**Pre-campaign validation:**
```
Audit data quality before retention campaign launch
```

**Specific tables:**
```
Audit data quality for tables: accounts, health_scores
```

---

## Sample Output

```json
{
  "audit_timestamp": "2026-01-28T14:30:00Z",
  "overall_health": "warning",
  "platforms": {
    "data_warehouse": "snowflake",
    "crm": "hubspot"
  },
  "coverage_metrics": {
    "account_id": {
      "total_records": 125000,
      "non_null": 125000,
      "coverage_pct": 100.0
    },
    "crm_id": {
      "total_records": 125000,
      "non_null": 104250,
      "coverage_pct": 83.4
    },
    "billing_account_ids": {
      "total_records": 125000,
      "non_null": 75000,
      "coverage_pct": 60.0
    }
  },
  "null_rates": {
    "health_status": {
      "null_count": 2500,
      "total": 50000,
      "null_pct": 5.0
    },
    "health_score": {
      "null_count": 1200,
      "total": 50000,
      "null_pct": 2.4
    },
    "churn_reason": {
      "null_count": 47500,
      "total": 50000,
      "null_pct": 95.0,
      "note": "Known issue - field mostly unpopulated"
    },
    "owner": {
      "null_count": 10000,
      "total": 50000,
      "null_pct": 20.0
    }
  },
  "join_accuracy": {
    "primary_join": {
      "method": "CRM ID direct match",
      "matched": 42500,
      "total": 50000,
      "match_rate_pct": 85.0
    },
    "billing_id_match": {
      "method": "Billing account ID contains match",
      "matched": 48000,
      "total": 50000,
      "match_rate_pct": 96.0
    },
    "recommendation": "Use billing_id_match for 11% better match rate"
  },
  "crm_quality": {
    "total_sampled": 100,
    "missing_owner_pct": 0.15,
    "missing_company_pct": 0.05
  },
  "issues": [
    {
      "severity": "warning",
      "field": "owner",
      "metric": "null_rate",
      "value": 0.20,
      "threshold": 0.20,
      "description": "20% of accounts unassigned",
      "impact": "Cannot route to correct owner",
      "remediation": "Implement owner assignment workflow"
    }
  ],
  "recommendations": [
    "Use billing_id_match join (96%) over primary CRM ID join (85%) for identity mapping",
    "20% of accounts lack owner assignment - implement assignment automation",
    "Schedule weekly audit to track data quality trends"
  ]
}
```

---

## Benchmark Reference

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Primary key coverage | 100% | <100% | <95% |
| CRM ID coverage | >85% | 70-85% | <70% |
| Identity join accuracy | >95% | 85-95% | <85% |
| Critical field null rate | <5% | 5-20% | >20% |
| Owner assignment | >90% | 70-90% | <70% |

---

## Configuring for New Clients

### Step 1: Document Schema

```yaml
# Identify your data model
schema:
  accounts:
    table: "your_schema.your_accounts_table"
    primary_key: "your_account_id_field"
    fields:
      account_id: "your_account_id_field"
      # ... map all fields
```

### Step 2: Define Identity Mapping

```yaml
identity_mapping:
  primary_join:
    left_table: "accounts"
    left_field: "crm_id"  # Your CRM ID field
    right_source: "crm"
    right_field: "company_id"
```

### Step 3: Document Known Issues

```yaml
known_issues:
  - field: "your_problematic_field"
    expected_null_rate: 0.80
    note: "Reason this field is often null"
```

### Step 4: Set Thresholds

```yaml
thresholds:
  coverage:
    healthy: 0.90  # Adjust based on your standards
    warning: 0.75
    critical: 0.50
```

---

## Notes

- Run monthly for trending analysis
- Export to engineering dashboard
- Use to validate before major campaigns
- Document known data gaps in configuration
- Adjust thresholds based on business requirements
- Schema mappings must be configured per client data model

---

## Changelog

### v2.0.0 (2026-01-28)
- Converted to platform-agnostic framework
- Added support for multiple data warehouses
- Added support for multiple CRMs
- Implemented configurable schema mappings
- Added configurable thresholds
- Added known issues documentation
- Removed hardcoded table references

### v1.0.0 (2026-01-27)
- Initial release
