-- =============================================================================
-- MH1 SQL Template: schema_inspection
-- Purpose: Inspect schemas of discovered candidate tables
--
-- Before using, replace these placeholders:
--   {DATABASE} -> Your database name
--   {SCHEMA} -> Your schema name
--   {USERS_TABLE} -> Your users/accounts table name (e.g., users, customers, accounts)
--   {EVENTS_TABLE} -> Your events/activity table name
--   {HEALTH_TABLE} -> Your health scores/CRM metrics table (if applicable)
--   {PRIMARY_KEY} -> Your primary user identifier field (e.g., user_id, id, customer_id)
--   {EMAIL_FIELD} -> Your email field name (e.g., email, user_email)
--   {TIMESTAMP_FIELD} -> Your event timestamp field (e.g., created_at, event_time)
--
-- Example for Snowflake: MY_DB.ANALYTICS.USERS
-- Example for BigQuery: `project.dataset.users`
--
-- Prerequisites: Run discovery_tables.sql first to identify candidates
-- Platform: Snowflake (default), adaptable to BigQuery/PostgreSQL
-- =============================================================================

-- Phase 0: Schema Inspection
-- Purpose: Inspect schemas of discovered candidate tables
-- Prerequisites: Run discovery_tables.sql first to identify candidates
-- Execution: Update table names below with your discovered tables

-- Step 1: Describe user/account tables
-- Replace with your actual table references
DESCRIBE TABLE {DATABASE}.{SCHEMA}.{USERS_TABLE};
-- Additional tables to inspect:
-- DESCRIBE TABLE {DATABASE}.{SCHEMA}.customers;
-- DESCRIBE TABLE {DATABASE}.{SCHEMA}.accounts;

-- Step 2: Describe event tables
DESCRIBE TABLE {DATABASE}.{SCHEMA}.{EVENTS_TABLE};
-- Additional tables to inspect:
-- DESCRIBE TABLE {DATABASE}.{SCHEMA}.activity;
-- DESCRIBE TABLE {DATABASE}.{SCHEMA}.tracking_events;

-- Step 3: Describe CRM/health score tables (if available)
-- DESCRIBE TABLE {DATABASE}.{SCHEMA}.{HEALTH_TABLE};
-- DESCRIBE TABLE {DATABASE}.{SCHEMA}.crm_contacts;
-- DESCRIBE TABLE {DATABASE}.{SCHEMA}.hubspot_companies;

-- Step 4: Sample rows from user table
-- Update field names based on your schema
SELECT 
    {PRIMARY_KEY},
    {EMAIL_FIELD},
    created_at
    -- Add other relevant fields from your schema
FROM {DATABASE}.{SCHEMA}.{USERS_TABLE} 
LIMIT 5;

-- Step 5: Sample rows from event table
-- Update field names based on your schema
SELECT 
    event_id,           -- or {EVENT_ID_FIELD}
    event_type,         -- or event_name, action
    {EMAIL_FIELD},
    user_id,            -- or {USER_ID_FIELD}
    {TIMESTAMP_FIELD}
FROM {DATABASE}.{SCHEMA}.{EVENTS_TABLE} 
ORDER BY {TIMESTAMP_FIELD} DESC
LIMIT 10;

-- Step 6: Sample rows from health/CRM table (if available)
-- Uncomment and update field names based on your schema
-- SELECT 
--     {CRM_ID_FIELD},
--     account_name,
--     {ACCOUNT_ID_FIELD},
--     health_score,
--     health_status,
--     report_date
-- FROM {DATABASE}.{SCHEMA}.{HEALTH_TABLE} 
-- ORDER BY report_date DESC
-- LIMIT 5;

-- Step 7: Check for identity mapping columns in user table
-- Look for: hubspot_contact_id, crm_id, external_id, email
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = '{SCHEMA}'
AND table_name = '{USERS_TABLE}'
AND (
    LOWER(column_name) LIKE '%hubspot%'
    OR LOWER(column_name) LIKE '%crm%'
    OR LOWER(column_name) LIKE '%contact%'
    OR LOWER(column_name) = 'email'
    OR LOWER(column_name) LIKE '%external%'
    OR LOWER(column_name) LIKE '%id%'
)
ORDER BY ordinal_position;

-- Step 8: Check for identity mapping columns in event table
-- Look for: user_id, contact_id, email, external_id
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = '{SCHEMA}'
AND table_name = '{EVENTS_TABLE}'
AND (
    LOWER(column_name) LIKE '%user%'
    OR LOWER(column_name) LIKE '%contact%'
    OR LOWER(column_name) LIKE '%email%'
    OR LOWER(column_name) LIKE '%external%'
    OR LOWER(column_name) LIKE '%id%'
    OR LOWER(column_name) LIKE '%account%'
)
ORDER BY ordinal_position;

-- Step 9: Inspect event properties structure (if JSON/VARIANT)
-- Replace with your actual event table and properties column
-- SELECT 
--     event_name,
--     properties,         -- JSON/VARIANT column
--     {TIMESTAMP_FIELD},
--     user_id
-- FROM {DATABASE}.{SCHEMA}.{EVENTS_TABLE}
-- WHERE properties IS NOT NULL
-- LIMIT 10;

-- Step 10: Check distinct event names (to build event dictionary)
SELECT 
    event_type as event_name,  -- or event_name, action
    COUNT(*) as event_count,
    MIN({TIMESTAMP_FIELD}) as first_seen,
    MAX({TIMESTAMP_FIELD}) as last_seen
FROM {DATABASE}.{SCHEMA}.{EVENTS_TABLE}
GROUP BY event_type
ORDER BY event_count DESC;

-- Step 11: Find timestamp columns across candidate tables
-- Helps identify time fields for joins and filtering
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = '{SCHEMA}'
AND (
    LOWER(column_name) LIKE '%time%'
    OR LOWER(column_name) LIKE '%date%'
    OR LOWER(column_name) LIKE '%ts%'
    OR LOWER(column_name) LIKE '%_at%'
    OR LOWER(column_name) LIKE '%created%'
    OR LOWER(column_name) LIKE '%updated%'
)
ORDER BY table_name, ordinal_position;

-- Step 12: Check for account/organization hierarchy
-- Look for parent-child relationships in account structure
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = '{SCHEMA}'
AND (
    LOWER(column_name) LIKE '%org%'
    OR LOWER(column_name) LIKE '%account%'
    OR LOWER(column_name) LIKE '%company%'
    OR LOWER(column_name) LIKE '%workspace%'
    OR LOWER(column_name) LIKE '%tenant%'
    OR LOWER(column_name) LIKE '%parent%'
)
ORDER BY table_name, ordinal_position;
