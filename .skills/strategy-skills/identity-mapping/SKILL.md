---
name: identity-mapping
description: |
  Map identities between data warehouse and CRM using flexible matching strategies.
  Use when asked to 'map accounts', 'join warehouse to CRM', 'resolve identities',
  'link customer records', or 'cross-reference data sources'.
license: MIT
compatibility:
  - Any data warehouse (Snowflake, BigQuery, Redshift, Databricks, PostgreSQL)
  - Any CRM (HubSpot, Salesforce, Pipedrive, Zoho, Dynamics)
metadata:
  author: mh1-engineering
  version: "2.0.0"
  status: active
  estimated_runtime: "1-3min"
  max_cost: "$0.50"
  client_facing: false
  requires_human_review: false
  tags:
    - data-quality
    - identity
    - integration
    - cross-platform
allowed-tools: Read Write CallMcpTool Shell
---

# Identity Mapping Skill

Resolve and map identities between data warehouses and CRM systems using configurable matching strategies.

## When to Use

Use this skill when you need to:
- Join warehouse account data to CRM contacts/companies
- Validate identity match rates
- Resolve customer records across systems
- Build cross-platform customer views
- Deduplicate records

## Supported Matching Strategies

| Strategy | Match Quality | Coverage | Use Case |
|----------|--------------|----------|----------|
| **External ID** | Exact | High (if available) | Systems share common ID |
| **Email** | Exact | Medium | Contact-level matching |
| **Domain** | Good | High | Company-level matching |
| **Fuzzy Name** | Variable | Fallback | When IDs unavailable |
| **Composite** | Best | Variable | Combine multiple strategies |

## Configuration

Configure identity mapping in `clients/{clientId}/config/identity.yaml`:

```yaml
identity_mapping:
  # Primary matching strategy
  primary_strategy: "external_id"  # external_id | email | domain | fuzzy_name | composite
  
  # Fallback strategies (in order)
  fallback_strategies:
    - "domain"
    - "email"
    - "fuzzy_name"
  
  # Source systems
  warehouse:
    type: "{warehouse_type}"  # snowflake | bigquery | redshift | databricks | postgresql
    tables:
      accounts: "{warehouse_account_table}"
      users: "{warehouse_user_table}"
      events: "{warehouse_event_table}"
    fields:
      account_id: "{account_id_field}"
      account_name: "{account_name_field}"
      domain: "{domain_field}"
      external_ids: "{external_id_field}"  # May be array/JSON
      email: "{email_field}"
  
  crm:
    type: "{crm_type}"  # hubspot | salesforce | pipedrive | zoho | dynamics
    entities:
      companies: "{crm_company_entity}"
      contacts: "{crm_contact_entity}"
    fields:
      company_id: "{crm_company_id_field}"
      company_name: "{crm_company_name_field}"
      domain: "{crm_domain_field}"
      external_id: "{crm_external_id_field}"
      contact_email: "{crm_email_field}"
  
  # Matching thresholds
  thresholds:
    fuzzy_name_min_score: 0.85  # 0-1, higher = stricter
    domain_exact_match: true     # Require exact domain match
    email_case_insensitive: true
  
  # External ID configuration (if applicable)
  external_id_config:
    type: "single"  # single | array | json | comma_separated
    warehouse_field: "{external_id_field}"
    crm_field: "{crm_external_id_field}"
```

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `source_system` | string | yes | "warehouse" or "crm" |
| `source_ids` | array | yes | List of IDs to map |
| `strategy` | string | no | Override matching strategy |
| `include_unmatched` | boolean | no | Include unmatched records in output |

## Matching Strategy Details

### 1. External ID Matching (Highest Confidence)

Best for systems that share a common identifier (e.g., billing ID, subscription ID).

**Single ID Pattern:**
```sql
SELECT 
    w.{account_id_field} AS warehouse_id,
    c.{crm_company_id_field} AS crm_id,
    'external_id' AS match_method,
    1.0 AS confidence
FROM {warehouse_account_table} w
JOIN {crm_company_entity} c 
    ON w.{external_id_field} = c.{crm_external_id_field}
```

**Array/JSON ID Pattern:**
```sql
-- Snowflake (VARIANT column)
SELECT w.*, c.*
FROM {warehouse_account_table} w
JOIN {crm_company_entity} c 
    ON ARRAY_CONTAINS(w.{external_id_field}::VARIANT, c.{crm_external_id_field}::VARIANT)

-- BigQuery (ARRAY column)
SELECT w.*, c.*
FROM {warehouse_account_table} w
JOIN {crm_company_entity} c 
    ON c.{crm_external_id_field} IN UNNEST(w.{external_id_field})

-- PostgreSQL (JSONB array)
SELECT w.*, c.*
FROM {warehouse_account_table} w
JOIN {crm_company_entity} c 
    ON w.{external_id_field} @> to_jsonb(c.{crm_external_id_field})
```

**Comma-Separated Pattern:**
```sql
SELECT w.*, c.*
FROM {warehouse_account_table} w
JOIN {crm_company_entity} c 
    ON w.{external_id_field} LIKE '%' || c.{crm_external_id_field} || '%'
```

### 2. Domain Matching (High Confidence)

Match companies by email domain.

```sql
SELECT 
    w.{account_id_field} AS warehouse_id,
    w.{account_name_field} AS warehouse_name,
    c.{crm_company_id_field} AS crm_id,
    c.{crm_company_name_field} AS crm_name,
    'domain' AS match_method,
    0.95 AS confidence
FROM {warehouse_account_table} w
JOIN {crm_company_entity} c 
    ON LOWER(w.{domain_field}) = LOWER(c.{crm_domain_field})
WHERE w.{domain_field} IS NOT NULL 
  AND c.{crm_domain_field} IS NOT NULL
```

**Domain Normalization (remove common prefixes):**
```sql
-- Normalize domain: remove www., mail., etc.
WITH normalized AS (
    SELECT *,
        REGEXP_REPLACE(LOWER({domain_field}), '^(www\.|mail\.)', '') AS norm_domain
    FROM {warehouse_account_table}
)
SELECT * FROM normalized w
JOIN {crm_company_entity} c
    ON w.norm_domain = REGEXP_REPLACE(LOWER(c.{crm_domain_field}), '^(www\.|mail\.)', '')
```

### 3. Email Matching (Medium Confidence)

Match contacts by email address.

```sql
SELECT 
    wu.{user_id_field} AS warehouse_user_id,
    wu.{account_id_field} AS warehouse_account_id,
    cc.{contact_id_field} AS crm_contact_id,
    cc.{company_id_field} AS crm_company_id,
    'email' AS match_method,
    0.90 AS confidence
FROM {warehouse_user_table} wu
JOIN {crm_contact_entity} cc 
    ON LOWER(wu.{email_field}) = LOWER(cc.{crm_email_field})
WHERE wu.{email_field} IS NOT NULL 
  AND cc.{crm_email_field} IS NOT NULL
```

### 4. Fuzzy Name Matching (Lower Confidence)

Use when IDs and domains unavailable. Requires string similarity functions.

**Snowflake (JAROWINKLER_SIMILARITY):**
```sql
SELECT 
    w.{account_id_field} AS warehouse_id,
    w.{account_name_field} AS warehouse_name,
    c.{crm_company_id_field} AS crm_id,
    c.{crm_company_name_field} AS crm_name,
    JAROWINKLER_SIMILARITY(
        UPPER(w.{account_name_field}), 
        UPPER(c.{crm_company_name_field})
    ) / 100.0 AS similarity_score,
    'fuzzy_name' AS match_method
FROM {warehouse_account_table} w
CROSS JOIN {crm_company_entity} c
WHERE JAROWINKLER_SIMILARITY(
    UPPER(w.{account_name_field}), 
    UPPER(c.{crm_company_name_field})
) >= {fuzzy_name_min_score} * 100
```

**BigQuery:**
```sql
SELECT *,
    ML.DISTANCE(
        LOWER(w.{account_name_field}),
        LOWER(c.{crm_company_name_field}),
        'LEVENSHTEIN'
    ) AS edit_distance
FROM {warehouse_account_table} w
CROSS JOIN {crm_company_entity} c
WHERE LENGTH(w.{account_name_field}) > 0
  AND ML.DISTANCE(...) <= 3  -- Max 3 character edits
```

**PostgreSQL (pg_trgm extension):**
```sql
SELECT *,
    similarity(
        LOWER(w.{account_name_field}),
        LOWER(c.{crm_company_name_field})
    ) AS similarity_score
FROM {warehouse_account_table} w
CROSS JOIN {crm_company_entity} c
WHERE similarity(
    LOWER(w.{account_name_field}),
    LOWER(c.{crm_company_name_field})
) >= {fuzzy_name_min_score}
```

### 5. Composite Matching (Best Coverage)

Combine multiple strategies with priority ordering.

```sql
WITH external_matches AS (
    SELECT w.{account_id_field}, c.{crm_company_id_field}, 
           'external_id' AS method, 1.0 AS confidence, 1 AS priority
    FROM {warehouse_account_table} w
    JOIN {crm_company_entity} c ON w.{external_id_field} = c.{crm_external_id_field}
),
domain_matches AS (
    SELECT w.{account_id_field}, c.{crm_company_id_field},
           'domain' AS method, 0.95 AS confidence, 2 AS priority
    FROM {warehouse_account_table} w
    JOIN {crm_company_entity} c ON LOWER(w.{domain_field}) = LOWER(c.{crm_domain_field})
    WHERE w.{account_id_field} NOT IN (SELECT {account_id_field} FROM external_matches)
),
email_matches AS (
    -- Contact-to-account rollup
    SELECT DISTINCT wu.{account_id_field}, cc.{company_id_field} AS {crm_company_id_field},
           'email' AS method, 0.90 AS confidence, 3 AS priority
    FROM {warehouse_user_table} wu
    JOIN {crm_contact_entity} cc ON LOWER(wu.{email_field}) = LOWER(cc.{crm_email_field})
    WHERE wu.{account_id_field} NOT IN (
        SELECT {account_id_field} FROM external_matches
        UNION SELECT {account_id_field} FROM domain_matches
    )
),
all_matches AS (
    SELECT * FROM external_matches
    UNION ALL SELECT * FROM domain_matches
    UNION ALL SELECT * FROM email_matches
)
SELECT DISTINCT ON ({account_id_field})
    {account_id_field} AS warehouse_id,
    {crm_company_id_field} AS crm_id,
    method AS match_method,
    confidence
FROM all_matches
ORDER BY {account_id_field}, priority
```

## Process

### Step 1: Load Client Configuration

```python
import yaml

with open(f"clients/{client_id}/config/identity.yaml") as f:
    config = yaml.safe_load(f)

warehouse_config = config['identity_mapping']['warehouse']
crm_config = config['identity_mapping']['crm']
```

### Step 2: Build Mapping Query

Select appropriate query based on `primary_strategy`:

```python
if config['primary_strategy'] == 'external_id':
    query = build_external_id_query(warehouse_config, crm_config)
elif config['primary_strategy'] == 'domain':
    query = build_domain_query(warehouse_config, crm_config)
elif config['primary_strategy'] == 'composite':
    query = build_composite_query(warehouse_config, crm_config, config['fallback_strategies'])
# ... etc
```

### Step 3: Execute and Calculate Match Rates

```python
results = execute_query(query)

total_source = count_source_records()
matched = len([r for r in results if r.get('crm_id')])
unmatched = total_source - matched

match_rate = matched / total_source * 100
```

### Step 4: Return Mapping Results

## Output Schema

```json
{
  "source_system": "warehouse | crm",
  "total_source_records": "number",
  "matched_records": "number",
  "unmatched_records": "number",
  "match_rate": "number (percentage)",
  "match_breakdown": {
    "external_id": "number",
    "domain": "number",
    "email": "number",
    "fuzzy_name": "number"
  },
  "mappings": [
    {
      "source_id": "string",
      "target_id": "string",
      "confidence": "high | medium | low",
      "match_method": "external_id | domain | email | fuzzy_name",
      "score": "number (0-1)"
    }
  ],
  "unmatched": [
    {
      "source_id": "string",
      "source_name": "string (optional)",
      "reason": "no_external_id | no_domain | no_email_match | below_threshold"
    }
  ]
}
```

## Expected Coverage Metrics

Typical match rates by strategy:

| Strategy | Expected Coverage | Notes |
|----------|------------------|-------|
| External ID | 90-100% | If both systems have the ID |
| Domain | 70-85% | Varies by data quality |
| Email | 50-70% | Depends on contact overlap |
| Fuzzy Name | 40-60% | High false positive risk |
| Composite | 85-95% | Best overall coverage |

## Quality Criteria

- [ ] Match rate >= 80% for composite strategy
- [ ] No duplicate mappings (1:1 or documented 1:many)
- [ ] Unmatched records have clear reasons
- [ ] Match method documented per record
- [ ] Confidence scores align with method quality

## Common Issues and Solutions

### Low External ID Coverage
- **Cause:** IDs not synced between systems
- **Solution:** Use domain matching as primary, implement ID sync

### Domain Matching Misses
- **Cause:** Different domain formats (www.example.com vs example.com)
- **Solution:** Normalize domains before matching

### High False Positives in Name Matching
- **Cause:** Common company names ("ABC Inc", "Tech Solutions")
- **Solution:** Lower threshold or require secondary match

### Duplicate Matches
- **Cause:** Multiple CRM records for same company
- **Solution:** Dedupe CRM first, or take highest-confidence match

## Notes

- Always start with highest-confidence strategy available
- Validate a sample of matches manually before bulk processing
- Log match statistics to track data quality trends
- Consider re-running after data quality improvements
- External ID matching is always preferred when available
