-- =============================================================================
-- MH1 SQL Template: identity_mapping
-- Purpose: Build identity_map linking organizations to CRM companies
--
-- Before using, replace these placeholders:
--   {DATABASE} -> Your database name
--   {SCHEMA} -> Your schema name
--   {EVENTS_TABLE} -> Your events/activity table
--   {ORGS_TABLE} -> Your organizations/accounts dimension table
--   {HEALTH_TABLE} -> Your health scores/CRM metrics table
--   {ORG_ID_FIELD} -> Your organization identifier (e.g., org_id, account_id, company_id)
--   {CRM_ID_FIELD} -> Your CRM identifier (e.g., hubspot_company_id, salesforce_account_id)
--   {EMAIL_FIELD} -> Your email field name
--   {TIMESTAMP_FIELD} -> Your event timestamp field
--   {ACCOUNT_ID_FIELD} -> Your account identifier field
--   {ACCOUNT_NAME_FIELD} -> Your account name field
--   {HEALTH_SCORE_FIELD} -> Your health score field (e.g., health_score, nps_score)
--   {HEALTH_STATUS_FIELD} -> Your health status field (e.g., health_status, risk_level)
--   {ARR_FIELD} -> Your ARR/revenue field
--   {REPORT_DATE_FIELD} -> Your report date field for time-series data
--
-- Example for Snowflake: MY_DB.ANALYTICS.EVENTS
-- Example for BigQuery: `project.dataset.events`
--
-- Platform: Snowflake (default), adaptable to BigQuery/PostgreSQL
-- =============================================================================

-- Phase 0: Identity Mapping
-- Purpose: Build identity_map linking organizations to CRM companies
--
-- CRITICAL SCHEMA INSIGHT:
--   Events table typically uses {ORG_ID_FIELD} (high coverage), NOT email
--   Join path: Events.{ORG_ID_FIELD} → {ORGS_TABLE}.{CRM_ID_FIELD} → CRM
--   Email coverage: varies by client (optional enrichment only)

-- ============================================================================
-- STEP 1: Validate org/account ID coverage (primary identifier)
-- ============================================================================

SELECT 
    COUNT(*) as total_events,
    COUNT({ORG_ID_FIELD}) as events_with_org_id,
    ROUND(COUNT({ORG_ID_FIELD}) * 100.0 / COUNT(*), 2) as pct_with_org_id,
    COUNT(DISTINCT {ORG_ID_FIELD}) as unique_orgs,
    COUNT({EMAIL_FIELD}) as events_with_email,
    ROUND(COUNT({EMAIL_FIELD}) * 100.0 / COUNT(*), 2) as pct_with_email
FROM {DATABASE}.{SCHEMA}.{EVENTS_TABLE}
WHERE {TIMESTAMP_FIELD} >= DATEADD('day', -90, CURRENT_DATE());

-- ============================================================================
-- STEP 2: Org ID to CRM ID mapping (PRIMARY METHOD)
-- ============================================================================

-- Check org to CRM mapping via organizations dimension table
SELECT 
    COUNT(*) as total_orgs,
    COUNT({CRM_ID_FIELD}) as orgs_with_crm_id,
    ROUND(COUNT({CRM_ID_FIELD}) * 100.0 / COUNT(*), 2) as pct_with_crm
FROM {DATABASE}.{SCHEMA}.{ORGS_TABLE}
WHERE {CRM_ID_FIELD} IS NOT NULL
  AND {CRM_ID_FIELD} NOT IN ('-1', '0', '');

-- ============================================================================
-- STEP 3: Build company_identity_map (Org ID primary)
-- ============================================================================

CREATE OR REPLACE VIEW company_identity_map AS
-- Method 1: Org ID to CRM ID (PRIMARY - highest coverage)
SELECT DISTINCT
    o.{ORG_ID_FIELD} as org_id,
    o.org_name as org_name,
    CAST(o.{CRM_ID_FIELD} AS TEXT) as crm_company_id,
    hs.{ACCOUNT_ID_FIELD} as account_id,
    hs.{ACCOUNT_NAME_FIELD} as account_name,
    hs.{HEALTH_STATUS_FIELD} as health_status,
    hs.{HEALTH_SCORE_FIELD} as health_score,
    hs.{ARR_FIELD} as arr,
    'org_to_crm' as mapping_method,
    1 as priority  -- Highest priority
FROM {DATABASE}.{SCHEMA}.{ORGS_TABLE} o
LEFT JOIN (
    SELECT 
        {CRM_ID_FIELD}, 
        {ACCOUNT_ID_FIELD}, 
        {ACCOUNT_NAME_FIELD}, 
        {HEALTH_STATUS_FIELD}, 
        {HEALTH_SCORE_FIELD}, 
        {ARR_FIELD}
    FROM {DATABASE}.{SCHEMA}.{HEALTH_TABLE}
    WHERE {REPORT_DATE_FIELD} = (SELECT MAX({REPORT_DATE_FIELD}) FROM {DATABASE}.{SCHEMA}.{HEALTH_TABLE})
) hs ON CAST(o.{CRM_ID_FIELD} AS TEXT) = hs.{CRM_ID_FIELD}
WHERE o.{CRM_ID_FIELD} IS NOT NULL
  AND o.{CRM_ID_FIELD} NOT IN ('-1', '0', '');

-- ============================================================================
-- STEP 4: Email-based enrichment (OPTIONAL - typically lower coverage)
-- ============================================================================

-- NOTE: Email should NOT be used as primary join key
-- Only use for enrichment when org ID path is unavailable

CREATE OR REPLACE VIEW email_contact_enrichment AS
SELECT DISTINCT
    e.{ORG_ID_FIELD} as org_id,
    e.{EMAIL_FIELD} as email,
    MD5(LOWER(TRIM(e.{EMAIL_FIELD}))) as email_hash,
    SPLIT_PART(e.{EMAIL_FIELD}, '@', 2) as domain,
    MIN(e.{TIMESTAMP_FIELD}) as first_seen_ts,
    MAX(e.{TIMESTAMP_FIELD}) as last_seen_ts,
    COUNT(*) as event_count
FROM {DATABASE}.{SCHEMA}.{EVENTS_TABLE} e
WHERE e.{EMAIL_FIELD} IS NOT NULL
  AND e.{ORG_ID_FIELD} IS NOT NULL
  AND e.{TIMESTAMP_FIELD} >= DATEADD('day', -90, CURRENT_DATE())
GROUP BY e.{ORG_ID_FIELD}, e.{EMAIL_FIELD}, email_hash, domain;

-- ============================================================================
-- STEP 5: Validate mapping coverage
-- ============================================================================

-- Company mapping coverage check
SELECT 
    'Total ORGs with events (90d)' as metric,
    COUNT(DISTINCT e.{ORG_ID_FIELD}) as value
FROM {DATABASE}.{SCHEMA}.{EVENTS_TABLE} e
WHERE e.{TIMESTAMP_FIELD} >= DATEADD('day', -90, CURRENT_DATE())

UNION ALL

SELECT 
    'ORGs with CRM mapping' as metric,
    COUNT(DISTINCT e.{ORG_ID_FIELD}) as value
FROM {DATABASE}.{SCHEMA}.{EVENTS_TABLE} e
INNER JOIN {DATABASE}.{SCHEMA}.{ORGS_TABLE} o ON e.{ORG_ID_FIELD} = o.{ORG_ID_FIELD}
WHERE e.{TIMESTAMP_FIELD} >= DATEADD('day', -90, CURRENT_DATE())
  AND o.{CRM_ID_FIELD} IS NOT NULL
  AND o.{CRM_ID_FIELD} NOT IN ('-1', '0', '')

UNION ALL

SELECT 
    'ORGs matched to health scores' as metric,
    COUNT(DISTINCT e.{ORG_ID_FIELD}) as value
FROM {DATABASE}.{SCHEMA}.{EVENTS_TABLE} e
INNER JOIN {DATABASE}.{SCHEMA}.{ORGS_TABLE} o ON e.{ORG_ID_FIELD} = o.{ORG_ID_FIELD}
INNER JOIN {DATABASE}.{SCHEMA}.{HEALTH_TABLE} hs 
    ON CAST(o.{CRM_ID_FIELD} AS TEXT) = hs.{CRM_ID_FIELD}
WHERE e.{TIMESTAMP_FIELD} >= DATEADD('day', -90, CURRENT_DATE())
  AND hs.{REPORT_DATE_FIELD} = (SELECT MAX({REPORT_DATE_FIELD}) FROM {DATABASE}.{SCHEMA}.{HEALTH_TABLE})

UNION ALL

SELECT 
    'Events with email (optional enrichment)' as metric,
    COUNT(DISTINCT e.{EMAIL_FIELD}) as value
FROM {DATABASE}.{SCHEMA}.{EVENTS_TABLE} e
WHERE e.{TIMESTAMP_FIELD} >= DATEADD('day', -90, CURRENT_DATE())
  AND e.{EMAIL_FIELD} IS NOT NULL;
