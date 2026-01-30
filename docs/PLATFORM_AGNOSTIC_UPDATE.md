# Platform-Agnostic Skills Update

**Date:** January 28, 2026  
**Version:** 2.0.0 (All Flowcode-derived skills)

---

## Summary

All skills derived from Flowcode have been updated to be **company-agnostic** and support **multiple platforms**. They can now be deployed for any client using any combination of CRM, data warehouse, and marketing tools.

---

## Supported Platforms

### Data Warehouses
- Snowflake
- BigQuery
- Redshift
- Databricks
- PostgreSQL

### CRM Platforms
- HubSpot
- Salesforce
- Pipedrive
- Zoho CRM
- Microsoft Dynamics 365

### Analytics Platforms (Event Sources)
- Segment
- Amplitude
- Mixpanel
- Google Analytics 4
- Rudderstack
- Snowplow

### Email/Marketing Platforms
- HubSpot Marketing
- Salesforce Marketing Cloud
- Marketo
- Klaviyo
- Custom SMTP

### Storage Backends (Artifacts)
- Local filesystem
- AWS S3
- Google Cloud Storage
- Azure Blob Storage
- MinIO

---

## Skills Updated (21 total)

### Discovery & Intelligence (4)

| Skill | Old Name | Platforms |
|-------|----------|-----------|
| `data-warehouse-discovery` | `snowflake-discovery` | Snowflake, BigQuery, Redshift, Databricks, PostgreSQL |
| `crm-discovery` | `hubspot-discovery` | HubSpot, Salesforce, Pipedrive, Zoho, Dynamics |
| `identity-mapping` | (same) | Any warehouse + CRM combination |
| `data-quality-audit` | (same) | Any warehouse + CRM combination |

### Customer Intelligence (7)

| Skill | Version | Changes |
|-------|---------|---------|
| `at-risk-detection` | 2.0.0 | Generic revenue thresholds, multi-platform queries |
| `upsell-candidates` | 2.0.0 | Removed F1/F2, configurable tier upgrades |
| `churn-prediction` | 2.0.0 | Generic churn signals, configurable lookback |
| `dormant-detection` | 2.0.0 | Multiple detection methods, configurable thresholds |
| `engagement-velocity` | 2.0.0 | Configurable comparison periods |
| `conversion-funnel` | 2.0.0 | Industry-specific funnel templates |
| `reactivation-detection` | 2.0.0 | Generic winback scoring |

### Sales Intelligence (6)

| Skill | Version | Changes |
|-------|---------|---------|
| `pipeline-analysis` | 2.0.0 | 5 CRM platforms, configurable pipelines |
| `sales-rep-performance` | 2.0.0 | Generic owner fields, warehouse + CRM support |
| `deal-velocity` | 2.0.0 | Configurable health values, benchmarks |
| `renewal-tracker` | 2.0.0 | Configurable urgency thresholds |
| `account-360` | 2.0.0 | Modular data sources, 5 CRM activity queries |
| `call-analytics` | 2.0.0 | Duration normalization, status mapping |

### Content & Automation (4)

| Skill | Version | Changes |
|-------|---------|---------|
| `email-copy-generator` | 2.0.0 | Semantic reason codes, 4 CRM writebacks |
| `cohort-email-builder` | 2.0.0 | Generic segmentation, any warehouse |
| `playbook-executor` | 2.0.0 | YAML-defined playbooks, any data source |
| `artifact-manager` | 2.0.0 | 5 storage backends, configurable retention |

---

## Key Changes Made

### 1. Removed Flowcode-Specific References

| Removed | Replaced With |
|---------|--------------|
| F1/F2 platform | Configurable `tier` field |
| DTX database | `{database}` placeholder |
| REPORTING_COMBINED schema | `{schema}` placeholder |
| RPT_* table names | `{customer_table}`, `{events_table}` |
| FC1_ZUORA_ACCOUNT_IDS | `{account_id_field}` |
| Hardcoded pipeline IDs | Configurable `pipelines.sales`, `pipelines.renewal` |
| CS_OWNER field | Configurable `owner_field` |
| $24K ARR threshold | `thresholds.high_value_min` |

### 2. Added Platform Configuration

Every skill now includes a configuration section:

```yaml
configuration:
  data_source: snowflake | bigquery | salesforce | hubspot
  customer_table: "{schema}.{table}"
  revenue_field: "arr" | "mrr" | "revenue"
  health_score_field: "health_score" | null
  thresholds:
    high_value_min: 10000  # configurable
    at_risk_score_max: 40  # configurable
```

### 3. Multi-Platform Query Templates

Each skill includes query templates for:
- **Snowflake SQL** - with `{field}` placeholders
- **BigQuery SQL** - using BigQuery syntax
- **Salesforce SOQL** - with custom field notation
- **HubSpot API** - JSON filter format
- **Pipedrive API** - REST endpoints
- **Zoho CRM** - COQL queries
- **Dynamics 365** - OData queries

### 4. Semantic Reason Codes

| Old Code | New Code | Purpose |
|----------|----------|---------|
| RC1 | REENGAGEMENT | Re-activate dormant users |
| RC2 | CONVERSION | Turn engagement into sales |
| RC3 | RETENTION | Reduce churn risk |
| RC4 | UPSELL | Upgrade to higher tier |
| RC5 | ADVOCACY | Activate power users |
| RC6 | WIN_BACK | Recover churned accounts |
| RC7 | ONBOARDING | Welcome new customers |
| RC8 | DISCOVERY | Gather information |

---

## Supporting Files Updated

### Semantic Layer (`config/semantic_layer/`)

| File | Changes |
|------|---------|
| `lifecycle_steps.yml` | Industry templates (SaaS, E-commerce, B2B, Marketplace) |
| `event_dictionary.yml` | Platform mappings (Segment, Amplitude, Mixpanel, GA4) |
| `company_event_semantics.yml` | Configurable join strategies and thresholds |

### SQL Templates (`sql/`)

| File | Changes |
|------|---------|
| `discovery_tables.sql` | `{DATABASE}`, `{SCHEMA}` placeholders |
| `schema_inspection.sql` | Generic table/field references |
| `identity_mapping.sql` | Configurable ID fields |
| `contact_360.sql` | Optional CRM joins |
| `events_clean.sql` | Generic event type mapping |
| `company_level_analysis.sql` | Configurable thresholds |

### Query Templates (`config/query_templates.json`)

- Renamed all `sf_*` and `hs_*` prefixes to generic names
- Added `platform` field to each query
- Made all field references configurable

### Prompts (`prompts/`)

| File | Changes |
|------|---------|
| `email_copy_generation.md` | Industry examples, CRM mapping table |
| `email_analysis_rubric.md` | Generic scoring dimensions |
| `reason_code_templates.md` | Semantic codes, multi-CRM writeback |

---

## Client Setup Guide

### 1. Create Client Configuration

```bash
mkdir -p clients/{client_id}/config
```

### 2. Configure Data Sources

Create `clients/{client_id}/config/datasources.yaml`:

```yaml
warehouse:
  type: snowflake  # or bigquery, redshift, databricks, postgresql
  database: "{your_database}"
  schema: "{your_schema}"
  customer_table: "customers"
  events_table: "events"
  health_table: "customer_health"

crm:
  type: hubspot  # or salesforce, pipedrive, zoho, dynamics
  pipelines:
    sales: "{your_sales_pipeline_id}"
    renewal: "{your_renewal_pipeline_id}"
  
field_mapping:
  account_id: "account_id"
  customer_name: "company_name"
  revenue: "arr"  # or mrr, revenue
  health_score: "health_score"
  owner: "owner_id"

thresholds:
  high_value_min: 10000
  at_risk_score_max: 40
  dormant_days: 30
  churn_lookback_days: 90
```

### 3. Copy Semantic Layer

```bash
cp -r config/semantic_layer/ clients/{client_id}/config/semantic_layer/
# Then customize for client-specific events and lifecycle stages
```

### 4. Run Skills

Skills automatically read from `clients/{client_id}/config/` when client context is active.

---

## Migration Notes

### For Existing Flowcode Clients

If you have existing Flowcode configurations:

1. Create `clients/flowcode/config/datasources.yaml` with Flowcode-specific values
2. Map F1/F2 to tier values
3. Configure pipeline IDs
4. Skills will work without code changes

### For New Clients

1. Follow the Client Setup Guide above
2. Customize semantic layer for industry
3. Configure thresholds based on business model
4. Test with `data-warehouse-discovery` and `crm-discovery` skills

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-27 | Initial Flowcode-specific skills |
| 2.0.0 | 2026-01-28 | Platform-agnostic update |

---

*All skills are now ready for multi-client, multi-platform deployment.*
