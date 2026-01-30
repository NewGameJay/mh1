-- =============================================================================
-- MH1 SQL Template: contact_360
-- Purpose: Create minimal normalized contact view combining CRM + product data
--
-- Before using, replace these placeholders:
--   {DATABASE} -> Your database name
--   {SCHEMA} -> Your schema name
--   {USERS_TABLE} -> Your users table name
--   {EVENTS_TABLE} -> Your events table name
--   {HEALTH_TABLE} -> Your health scores/CRM table (optional)
--   {PRIMARY_KEY} -> Your primary user identifier (e.g., user_id, id)
--   {EMAIL_FIELD} -> Your email field name
--   {TIMESTAMP_FIELD} -> Your event timestamp field
--   {USER_CREATED_FIELD} -> Your user creation timestamp field
--   {ACCOUNT_ID_FIELD} -> Your account/org identifier field
--   {ACCOUNT_NAME_FIELD} -> Your account name field
--   {CRM_ID_FIELD} -> Your CRM identifier field (e.g., hubspot_company_id)
--   {HEALTH_SCORE_FIELD} -> Your health score field
--   {HEALTH_STATUS_FIELD} -> Your health status field
--   {MRR_FIELD} -> Your MRR field (optional)
--   {ARR_FIELD} -> Your ARR field (optional)
--   {REPORT_DATE_FIELD} -> Your report date field for time-series data
--
-- Example for Snowflake: MY_DB.ANALYTICS.USERS
-- Example for BigQuery: `project.dataset.users`
--
-- Prerequisites: identity_mapping.sql should exist (run it first)
-- Platform: Snowflake (default), adaptable to BigQuery/PostgreSQL
-- =============================================================================

-- Phase 0: Contact 360 Normalization
-- Purpose: Create minimal normalized contact view combining CRM + product data
-- Prerequisites: identity_map should exist (run identity_mapping.sql first)
-- Execution: Update table/column names with your discovered schemas

-- NOTE: This view cannot be created with read-only access.
-- Use this as a SELECT query template instead, or request write access.

-- Contact 360 Query (SELECT version - can be run with read-only access)
-- Combines product user data with available CRM company data

SELECT 
    -- Core identifiers (normalized)
    u.{PRIMARY_KEY} as app_user_id,
    NULL as crm_contact_id,  -- Will be populated via CRM API if needed
    MD5(LOWER(TRIM(u.{EMAIL_FIELD}))) as email_hash,
    LOWER(TRIM(u.{EMAIL_FIELD})) as email_normalized,
    u.{EMAIL_FIELD} as email_raw,
    
    -- Domain extraction (for company matching)
    CASE 
        WHEN u.{EMAIL_FIELD} IS NOT NULL AND u.{EMAIL_FIELD} LIKE '%@%' 
        THEN LOWER(TRIM(SPLIT_PART(u.{EMAIL_FIELD}, '@', 2)))
        ELSE NULL
    END as domain_normalized,
    
    -- Product user data
    u.{USER_CREATED_FIELD} as user_created_at,
    -- Add additional user fields from your schema here
    -- u.first_name,
    -- u.last_name,
    -- u.plan_type,
    
    -- Account/Company identifiers (from events if available)
    e.{ACCOUNT_ID_FIELD} as account_id,
    e.{ACCOUNT_NAME_FIELD} as account_name,
    
    -- CRM company data (company-level, not contact-level)
    -- Uncomment and configure based on your CRM data availability
    -- hs.{CRM_ID_FIELD} as crm_company_id,
    -- hs.{ACCOUNT_NAME_FIELD} as company_name_from_crm,
    -- hs.{ACCOUNT_ID_FIELD} as account_id_from_crm,
    -- hs.{HEALTH_SCORE_FIELD} as health_score,
    -- hs.{HEALTH_STATUS_FIELD} as health_status,
    -- hs.{MRR_FIELD} as mrr,
    -- hs.{ARR_FIELD} as arr,
    
    -- Computed fields
    CASE 
        WHEN u.{PRIMARY_KEY} IS NOT NULL THEN 'product_user'
        ELSE 'unknown'
    END as user_type,
    
    -- Health category (uncomment if using health scores)
    -- CASE 
    --     WHEN hs.{HEALTH_STATUS_FIELD} = 'At Risk' THEN 'at_risk'
    --     WHEN hs.{HEALTH_STATUS_FIELD} = 'Watchlist' THEN 'watchlist'
    --     WHEN hs.{HEALTH_SCORE_FIELD} >= 70 THEN 'healthy'
    --     WHEN hs.{HEALTH_SCORE_FIELD} >= 50 THEN 'medium'
    --     ELSE 'low'
    -- END as health_category,
    
    -- Identity source tracking
    CASE 
        WHEN e.{ACCOUNT_ID_FIELD} IS NOT NULL THEN 'account_id_match'
        WHEN u.{EMAIL_FIELD} IS NOT NULL AND u.{EMAIL_FIELD} LIKE '%@%' THEN 'email_domain_available'
        ELSE 'email_only'
    END as identity_source,
    
    CURRENT_TIMESTAMP() as query_executed_at

FROM {DATABASE}.{SCHEMA}.{USERS_TABLE} u

-- Join events to get account ID (if available for this user)
LEFT JOIN (
    SELECT DISTINCT
        LOWER(TRIM({EMAIL_FIELD})) as email_normalized,
        {ACCOUNT_ID_FIELD},
        {ACCOUNT_NAME_FIELD}
    FROM {DATABASE}.{SCHEMA}.{EVENTS_TABLE}
    WHERE {EMAIL_FIELD} IS NOT NULL
        AND {ACCOUNT_ID_FIELD} IS NOT NULL
) e
    ON LOWER(TRIM(u.{EMAIL_FIELD})) = e.email_normalized

-- Left join CRM data via account ID (uncomment if available)
-- LEFT JOIN {DATABASE}.{SCHEMA}.{HEALTH_TABLE} hs
--     ON e.{ACCOUNT_ID_FIELD} = hs.{ACCOUNT_ID_FIELD}
--     AND hs.{REPORT_DATE_FIELD} = (SELECT MAX({REPORT_DATE_FIELD}) FROM {DATABASE}.{SCHEMA}.{HEALTH_TABLE})

-- Filter: show users with email
WHERE u.{EMAIL_FIELD} IS NOT NULL

LIMIT 10000;  -- Sample query - remove limit for full dataset

-- ============================================================================
-- VALIDATION QUERIES
-- ============================================================================

-- Step 2: Validation queries

-- Check row count and completeness
-- (Run after creating view or as standalone with CTE)
-- SELECT 
--     COUNT(*) as total_contacts,
--     COUNT(crm_contact_id) as has_crm_id,
--     COUNT(app_user_id) as has_app_user_id,
--     ROUND(COUNT(app_user_id) * 100.0 / COUNT(*), 2) as product_user_coverage_pct
-- FROM contact_360;

-- Distribution by identity source
-- SELECT 
--     identity_source,
--     COUNT(*) as contact_count,
--     ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM contact_360), 2) as pct_of_total
-- FROM contact_360
-- GROUP BY identity_source
-- ORDER BY contact_count DESC;

-- Coverage by date (temporal coverage)
-- SELECT 
--     DATE_TRUNC('month', user_created_at) as cohort_month,
--     COUNT(*) as contacts_created,
--     COUNT(CASE WHEN app_user_id IS NOT NULL THEN 1 END) as with_product_user
-- FROM contact_360
-- WHERE user_created_at >= DATEADD('year', -2, CURRENT_DATE())
-- GROUP BY cohort_month
-- ORDER BY cohort_month DESC
-- LIMIT 24;
