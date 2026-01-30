-- =============================================================================
-- MH1 SQL Template: discovery_tables
-- Purpose: Find candidate tables for users, accounts, events, and CRM data
--
-- Before using, replace these placeholders:
--   {DATABASE} -> Your database name
--   {SCHEMA} -> Your schema name (optional, for USE SCHEMA command)
--
-- Example for Snowflake: MY_DB.ANALYTICS
-- Example for BigQuery: `project.dataset`
-- Example for PostgreSQL: public
--
-- Platform: Snowflake (default), adaptable to BigQuery/PostgreSQL
-- =============================================================================

-- Phase 0: Table Discovery
-- Purpose: Find candidate tables for users, accounts, events, and CRM data
-- Execution: Run this after database connection is established

-- Step 1: List all databases you have access to (Snowflake-specific)
SHOW DATABASES;

-- Step 2: Show current context (Snowflake-specific)
SELECT 
    CURRENT_WAREHOUSE() as warehouse,
    CURRENT_ROLE() as role,
    CURRENT_DATABASE() as database,
    CURRENT_SCHEMA() as schema;

-- Step 3: Set database/schema context
-- Replace {DATABASE} and {SCHEMA} with your actual values
USE DATABASE {DATABASE};
USE SCHEMA {SCHEMA};

-- Step 4: Search for user/account related tables
SELECT 
    table_catalog as database,
    table_schema as schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE (
    LOWER(table_name) LIKE '%user%'
    OR LOWER(table_name) LIKE '%account%'
    OR LOWER(table_name) LIKE '%customer%'
    OR LOWER(table_name) LIKE '%member%'
    OR LOWER(table_name) LIKE '%contact%'
    OR LOWER(table_name) LIKE '%profile%'
)
AND table_type = 'BASE TABLE'
ORDER BY table_catalog, table_schema, table_name;

-- Step 5: Search for event/activity related tables
SELECT 
    table_catalog as database,
    table_schema as schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE (
    LOWER(table_name) LIKE '%event%'
    OR LOWER(table_name) LIKE '%activity%'
    OR LOWER(table_name) LIKE '%heap%'
    OR LOWER(table_name) LIKE '%segment%'
    OR LOWER(table_name) LIKE '%rudder%'
    OR LOWER(table_name) LIKE '%pageview%'
    OR LOWER(table_name) LIKE '%session%'
    OR LOWER(table_name) LIKE '%track%'
    OR LOWER(table_name) LIKE '%analytics%'
)
AND table_type = 'BASE TABLE'
ORDER BY table_catalog, table_schema, table_name;

-- Step 6: Search for CRM/HubSpot related tables
SELECT 
    table_catalog as database,
    table_schema as schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE (
    LOWER(table_name) LIKE '%hubspot%'
    OR LOWER(table_name) LIKE '%salesforce%'
    OR LOWER(table_name) LIKE '%crm%'
    OR LOWER(table_name) LIKE '%contact%'
    OR LOWER(table_name) LIKE '%lead%'
    OR LOWER(table_name) LIKE '%company%'
    OR LOWER(table_name) LIKE '%deal%'
    OR LOWER(table_name) LIKE '%opportunity%'
)
AND table_type = 'BASE TABLE'
ORDER BY table_catalog, table_schema, table_name;

-- Step 7: Search for business process tables (trial, subscription, billing)
SELECT 
    table_catalog as database,
    table_schema as schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE (
    LOWER(table_name) LIKE '%trial%'
    OR LOWER(table_name) LIKE '%subscription%'
    OR LOWER(table_name) LIKE '%billing%'
    OR LOWER(table_name) LIKE '%payment%'
    OR LOWER(table_name) LIKE '%checkout%'
    OR LOWER(table_name) LIKE '%purchase%'
    OR LOWER(table_name) LIKE '%order%'
    OR LOWER(table_name) LIKE '%invoice%'
    OR LOWER(table_name) LIKE '%plan%'
)
AND table_type = 'BASE TABLE'
ORDER BY table_catalog, table_schema, table_name;

-- Step 8: Search for email/marketing tables
SELECT 
    table_catalog as database,
    table_schema as schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE (
    LOWER(table_name) LIKE '%email%'
    OR LOWER(table_name) LIKE '%campaign%'
    OR LOWER(table_name) LIKE '%marketing%'
    OR LOWER(table_name) LIKE '%mailing%'
    OR LOWER(table_name) LIKE '%newsletter%'
    OR LOWER(table_name) LIKE '%send%'
)
AND table_type = 'BASE TABLE'
ORDER BY table_catalog, table_schema, table_name;

-- Step 9: Get approximate row counts for candidate tables (Snowflake-specific)
-- Note: This may require specific warehouse context
SELECT 
    table_catalog as database,
    table_schema as schema,
    table_name,
    row_count,
    bytes
FROM information_schema.table_storage_metrics
WHERE (
    LOWER(table_name) LIKE '%user%'
    OR LOWER(table_name) LIKE '%event%'
    OR LOWER(table_name) LIKE '%hubspot%'
    OR LOWER(table_name) LIKE '%contact%'
    OR LOWER(table_name) LIKE '%customer%'
    OR LOWER(table_name) LIKE '%account%'
)
ORDER BY bytes DESC NULLS LAST
LIMIT 50;

-- Step 10: Summary query - Count tables by category
SELECT 
    CASE
        WHEN LOWER(table_name) LIKE '%user%' OR LOWER(table_name) LIKE '%account%' OR LOWER(table_name) LIKE '%customer%' THEN 'Users/Accounts'
        WHEN LOWER(table_name) LIKE '%event%' OR LOWER(table_name) LIKE '%activity%' OR LOWER(table_name) LIKE '%track%' THEN 'Events'
        WHEN LOWER(table_name) LIKE '%hubspot%' OR LOWER(table_name) LIKE '%crm%' OR LOWER(table_name) LIKE '%contact%' THEN 'CRM'
        WHEN LOWER(table_name) LIKE '%email%' OR LOWER(table_name) LIKE '%campaign%' THEN 'Marketing'
        WHEN LOWER(table_name) LIKE '%subscription%' OR LOWER(table_name) LIKE '%billing%' OR LOWER(table_name) LIKE '%payment%' THEN 'Billing'
        ELSE 'Other'
    END as category,
    COUNT(*) as table_count
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
GROUP BY category
ORDER BY table_count DESC;
