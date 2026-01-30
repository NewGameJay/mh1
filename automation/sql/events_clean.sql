-- =============================================================================
-- MH1 SQL Template: events_clean
-- Purpose: Create minimal normalized events view with canonical event names
--
-- Before using, replace these placeholders:
--   {DATABASE} -> Your database name
--   {SCHEMA} -> Your schema name
--   {EVENTS_TABLE} -> Your events/activity table name
--   {USERS_TABLE} -> Your users table name (for join)
--   {PRIMARY_KEY} -> Your primary user identifier
--   {USER_ID_FIELD} -> Your user ID field in events table
--   {EMAIL_FIELD} -> Your email field name
--   {TIMESTAMP_FIELD} -> Your event timestamp field
--   {INGESTION_TIMESTAMP} -> Your ingestion timestamp field (optional)
--   {EVENT_ID_FIELD} -> Your event ID field
--   {EVENT_TYPE_FIELD} -> Your event type/name field
--   {ACCOUNT_ID_FIELD} -> Your account/org identifier field
--   {ACCOUNT_NAME_FIELD} -> Your account name field
--   {SESSION_ID_FIELD} -> Your session/cookie identifier field (optional)
--
-- Example for Snowflake: MY_DB.ANALYTICS.EVENTS
-- Example for BigQuery: `project.dataset.events`
--
-- Prerequisites: Run discovery queries to identify event table structure
-- Platform: Snowflake (default), adaptable to BigQuery/PostgreSQL
-- =============================================================================

-- Phase 0: Events Clean Normalization
-- Purpose: Create minimal normalized events view with canonical event names
-- Execution: Update table/column names and event mappings based on discoveries

-- CRITICAL: Update all placeholder values with your actual table/column names
-- Update event name mappings in the CASE statement based on your actual events

-- Step 1: Create event_dictionary mapping (customize for your events)
-- This will be reflected in semantic_layer/event_dictionary.yml

-- Step 2: Build events_clean view

-- NOTE: This view cannot be created with read-only access.
-- Use this as a SELECT query template instead, or request write access.

-- Events Clean Query (SELECT version - can be run with read-only access)
-- Maps raw events to canonical lifecycle steps and joins with user data

SELECT 
    -- Core identifiers (normalized)
    u.{PRIMARY_KEY} as app_user_id,
    NULL as crm_contact_id,  -- Will be populated via CRM API if needed
    MD5(LOWER(TRIM(e.{EMAIL_FIELD}))) as email_hash,
    LOWER(TRIM(e.{EMAIL_FIELD})) as email_normalized,
    e.{EMAIL_FIELD} as email_raw,
    
    -- Domain extraction (for company matching)
    CASE 
        WHEN e.{EMAIL_FIELD} IS NOT NULL AND e.{EMAIL_FIELD} LIKE '%@%' 
        THEN LOWER(TRIM(SPLIT_PART(e.{EMAIL_FIELD}, '@', 2)))
        ELSE NULL
    END as domain_normalized,
    
    -- Account/Company identifiers
    e.{ACCOUNT_ID_FIELD} as account_id,
    e.{ACCOUNT_NAME_FIELD} as account_name,
    
    -- Event metadata
    e.{EVENT_ID_FIELD} as raw_event_id,
    e.{EVENT_TYPE_FIELD} as raw_event_type,
    
    -- =========================================================================
    -- CANONICAL EVENT NAME MAPPING
    -- CUSTOMIZE: Update this CASE statement based on your actual event types
    -- =========================================================================
    CASE 
        -- Common event mappings (customize for your event schema)
        WHEN e.{EVENT_TYPE_FIELD} = 'page_view' THEN 'page_viewed'
        WHEN e.{EVENT_TYPE_FIELD} = 'pageview' THEN 'page_viewed'
        WHEN e.{EVENT_TYPE_FIELD} = 'view' THEN 'page_viewed'
        WHEN e.{EVENT_TYPE_FIELD} = 'click' THEN 'link_clicked'
        WHEN e.{EVENT_TYPE_FIELD} = 'button_click' THEN 'button_clicked'
        WHEN e.{EVENT_TYPE_FIELD} = 'form_submit' THEN 'form_submitted'
        WHEN e.{EVENT_TYPE_FIELD} = 'form_submission' THEN 'form_submitted'
        WHEN e.{EVENT_TYPE_FIELD} = 'signup' THEN 'signup_completed'
        WHEN e.{EVENT_TYPE_FIELD} = 'sign_up' THEN 'signup_completed'
        WHEN e.{EVENT_TYPE_FIELD} = 'login' THEN 'login_completed'
        WHEN e.{EVENT_TYPE_FIELD} = 'sign_in' THEN 'login_completed'
        WHEN e.{EVENT_TYPE_FIELD} = 'purchase' THEN 'purchase_completed'
        WHEN e.{EVENT_TYPE_FIELD} = 'conversion' THEN 'conversion_completed'
        WHEN e.{EVENT_TYPE_FIELD} = 'trial_started' THEN 'trial_started'
        WHEN e.{EVENT_TYPE_FIELD} = 'trial_ended' THEN 'trial_ended'
        WHEN e.{EVENT_TYPE_FIELD} = 'subscription_started' THEN 'subscription_started'
        WHEN e.{EVENT_TYPE_FIELD} = 'subscription_cancelled' THEN 'subscription_cancelled'
        WHEN e.{EVENT_TYPE_FIELD} = 'feature_used' THEN 'feature_used'
        WHEN e.{EVENT_TYPE_FIELD} = 'export' THEN 'export_completed'
        WHEN e.{EVENT_TYPE_FIELD} = 'download' THEN 'download_completed'
        WHEN e.{EVENT_TYPE_FIELD} = 'share' THEN 'share_completed'
        WHEN e.{EVENT_TYPE_FIELD} = 'invite_sent' THEN 'invite_sent'
        WHEN e.{EVENT_TYPE_FIELD} = 'session_start' THEN 'session_started'
        WHEN e.{EVENT_TYPE_FIELD} = 'session_end' THEN 'session_ended'
        ELSE 'unknown_event'
    END as canonical_event_name,
    
    -- =========================================================================
    -- LIFECYCLE STEP MAPPING
    -- CUSTOMIZE: Update based on your customer journey stages
    -- =========================================================================
    CASE 
        WHEN e.{EVENT_TYPE_FIELD} IN ('signup', 'sign_up', 'registration') THEN 'acquisition'
        WHEN e.{EVENT_TYPE_FIELD} IN ('login', 'sign_in', 'session_start') THEN 'activation'
        WHEN e.{EVENT_TYPE_FIELD} IN ('feature_used', 'export', 'download') THEN 'engagement'
        WHEN e.{EVENT_TYPE_FIELD} IN ('purchase', 'conversion', 'subscription_started') THEN 'revenue'
        WHEN e.{EVENT_TYPE_FIELD} IN ('share', 'invite_sent', 'referral') THEN 'referral'
        ELSE 'engagement'
    END as lifecycle_step,
    
    -- Timestamps
    e.{TIMESTAMP_FIELD} as event_ts,
    -- e.{INGESTION_TIMESTAMP} as ingestion_ts,  -- Uncomment if available
    CURRENT_TIMESTAMP() as processed_at,
    
    -- Session/identity tracking (uncomment if available)
    -- e.{SESSION_ID_FIELD} as session_id,
    
    -- Quality flags
    CASE WHEN e.{TIMESTAMP_FIELD} > CURRENT_TIMESTAMP() THEN 1 ELSE 0 END as is_future_dated,
    CASE WHEN u.{PRIMARY_KEY} IS NULL THEN 1 ELSE 0 END as is_orphaned_event,
    CASE WHEN e.{EMAIL_FIELD} IS NULL THEN 1 ELSE 0 END as is_anonymous_event,
    
    -- Identity source tracking
    CASE 
        WHEN e.{EMAIL_FIELD} IS NOT NULL AND u.{PRIMARY_KEY} IS NOT NULL THEN 'email_user_match'
        WHEN e.{EMAIL_FIELD} IS NOT NULL THEN 'email_only'
        WHEN e.{ACCOUNT_ID_FIELD} IS NOT NULL THEN 'account_id_only'
        ELSE 'unidentified'
    END as identity_source

FROM {DATABASE}.{SCHEMA}.{EVENTS_TABLE} e

-- Join users via normalized email (adjust join logic for your schema)
LEFT JOIN {DATABASE}.{SCHEMA}.{USERS_TABLE} u
    ON LOWER(TRIM(e.{EMAIL_FIELD})) = LOWER(TRIM(u.{EMAIL_FIELD}))

-- Filter recent events (last 2 years)
WHERE e.{TIMESTAMP_FIELD} >= DATEADD('year', -2, CURRENT_DATE())
    AND e.{TIMESTAMP_FIELD} < DATEADD('day', 1, CURRENT_DATE())  -- Exclude future dates

LIMIT 100000;  -- Sample query - remove limit for full dataset

-- ============================================================================
-- VALIDATION QUERIES
-- ============================================================================

-- Step 3: Validation queries

-- Check row count and coverage
-- SELECT 
--     COUNT(*) as total_events,
--     COUNT(DISTINCT app_user_id) as unique_users,
--     COUNT(CASE WHEN canonical_event_name != 'unknown_event' THEN 1 END) as mapped_events,
--     ROUND(COUNT(CASE WHEN canonical_event_name != 'unknown_event' THEN 1 END) * 100.0 / COUNT(*), 2) as mapping_coverage_pct,
--     COUNT(CASE WHEN is_orphaned_event = 1 THEN 1 END) as orphaned_events,
--     COUNT(CASE WHEN is_future_dated = 1 THEN 1 END) as future_dated_events
-- FROM events_clean;

-- Distribution by canonical event
-- SELECT 
--     canonical_event_name,
--     COUNT(*) as event_count,
--     COUNT(DISTINCT app_user_id) as unique_users,
--     MIN(event_ts) as first_seen,
--     MAX(event_ts) as last_seen,
--     ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM events_clean), 2) as pct_of_total
-- FROM events_clean
-- GROUP BY canonical_event_name
-- ORDER BY event_count DESC;

-- Unknown events (need mapping in event_dictionary)
-- SELECT 
--     raw_event_type as raw_event_name,
--     COUNT(*) as event_count,
--     COUNT(DISTINCT app_user_id) as unique_users,
--     MIN(event_ts) as first_seen,
--     MAX(event_ts) as last_seen
-- FROM events_clean
-- WHERE canonical_event_name = 'unknown_event'
-- GROUP BY raw_event_type
-- ORDER BY event_count DESC
-- LIMIT 50;

-- Temporal coverage
-- SELECT 
--     DATE_TRUNC('day', event_ts) as event_date,
--     COUNT(*) as daily_event_count,
--     COUNT(DISTINCT app_user_id) as daily_active_users,
--     COUNT(DISTINCT canonical_event_name) as unique_event_types
-- FROM events_clean
-- WHERE event_ts >= DATEADD('month', -3, CURRENT_DATE())
-- GROUP BY event_date
-- ORDER BY event_date DESC
-- LIMIT 90;

-- Event-to-user mapping quality
-- SELECT 
--     identity_source,
--     COUNT(*) as event_count,
--     COUNT(DISTINCT app_user_id) as unique_users,
--     ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM events_clean), 2) as pct_of_total
-- FROM events_clean
-- GROUP BY identity_source
-- ORDER BY event_count DESC;
