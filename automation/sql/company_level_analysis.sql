-- =============================================================================
-- MH1 SQL Template: company_level_analysis
-- Purpose: Build company-level dataset for lifecycle analysis
--
-- Before using, replace these placeholders:
--   {DATABASE} -> Your database name
--   {SCHEMA} -> Your schema name
--   {EVENTS_TABLE} -> Your events/activity table name
--   {ORGS_TABLE} -> Your organizations/accounts dimension table
--   {HEALTH_TABLE} -> Your health scores/CRM metrics table
--   {ORG_ID_FIELD} -> Your organization identifier (e.g., org_id, account_id)
--   {ORG_NAME_FIELD} -> Your organization name field
--   {CRM_ID_FIELD} -> Your CRM identifier (e.g., hubspot_company_id)
--   {ACCOUNT_ID_FIELD} -> Your account identifier field
--   {ACCOUNT_NAME_FIELD} -> Your account name field
--   {HEALTH_SCORE_FIELD} -> Your health score field
--   {HEALTH_STATUS_FIELD} -> Your health status field
--   {MRR_FIELD} -> Your MRR field
--   {ARR_FIELD} -> Your ARR field
--   {REPORT_DATE_FIELD} -> Your report date field
--   {TIMESTAMP_FIELD} -> Your event timestamp field
--   {EVENT_TYPE_FIELD} -> Your event type/name field
--   {SESSION_ID_FIELD} -> Your session/cookie identifier field
--   {EMAIL_FIELD} -> Your email field name
--   {CS_OWNER_FIELD} -> Your CS owner/account manager field (optional)
--   {SEGMENT_FIELD} -> Your company segment/vertical field (optional)
--
-- Example for Snowflake: MY_DB.ANALYTICS.EVENTS
-- Example for BigQuery: `project.dataset.events`
--
-- Platform: Snowflake (default), adaptable to BigQuery/PostgreSQL
-- =============================================================================

-- Phase 0: Company-Level Lifecycle Intelligence
-- Purpose: Build company-level dataset for lifecycle analysis
--
-- CRITICAL SCHEMA INSIGHT:
--   Events table typically uses {ORG_ID_FIELD} (high coverage)
--   Join path: Events.{ORG_ID_FIELD} → {ORGS_TABLE}.{CRM_ID_FIELD} → Health Scores

-- ============================================================================
-- STEP 0: Data Quality Checks (for validation)
-- ============================================================================

-- 0.1 Org ID coverage in events (last 90 days)
SELECT
  COUNT(*) AS total_events,
  COUNT({ORG_ID_FIELD}) AS events_with_org_id,
  ROUND(COUNT({ORG_ID_FIELD}) * 100.0 / COUNT(*), 2) AS pct_events_with_org_id,
  COUNT(DISTINCT {ORG_ID_FIELD}) AS unique_org_ids
FROM {DATABASE}.{SCHEMA}.{EVENTS_TABLE}
WHERE {TIMESTAMP_FIELD} >= DATEADD('day', -90, CURRENT_DATE());

-- 0.2 Session/cookie-to-org stability (check for multi-org sessions)
WITH session_orgs AS (
  SELECT {SESSION_ID_FIELD}, COUNT(DISTINCT {ORG_ID_FIELD}) AS org_count
  FROM {DATABASE}.{SCHEMA}.{EVENTS_TABLE}
  WHERE {TIMESTAMP_FIELD} >= DATEADD('day', -90, CURRENT_DATE())
    AND {SESSION_ID_FIELD} IS NOT NULL
  GROUP BY 1
)
SELECT org_count, COUNT(*) AS session_count 
FROM session_orgs 
GROUP BY 1 
ORDER BY 1;

-- 0.3 Org ID to CRM match rate through orgs dimension
SELECT 
  COUNT(DISTINCT e.{ORG_ID_FIELD}) AS unique_orgs_in_events,
  COUNT(DISTINCT o.{CRM_ID_FIELD}) AS orgs_with_crm_id,
  COUNT(DISTINCT hs.{CRM_ID_FIELD}) AS orgs_matched_to_health,
  ROUND(COUNT(DISTINCT o.{CRM_ID_FIELD}) * 100.0 / NULLIF(COUNT(DISTINCT e.{ORG_ID_FIELD}), 0), 2) AS pct_with_crm,
  ROUND(COUNT(DISTINCT hs.{CRM_ID_FIELD}) * 100.0 / NULLIF(COUNT(DISTINCT e.{ORG_ID_FIELD}), 0), 2) AS pct_matched_health
FROM {DATABASE}.{SCHEMA}.{EVENTS_TABLE} e
LEFT JOIN {DATABASE}.{SCHEMA}.{ORGS_TABLE} o ON e.{ORG_ID_FIELD} = o.{ORG_ID_FIELD}
LEFT JOIN (
  SELECT DISTINCT {CRM_ID_FIELD}
  FROM {DATABASE}.{SCHEMA}.{HEALTH_TABLE}
  WHERE {REPORT_DATE_FIELD} = (SELECT MAX({REPORT_DATE_FIELD}) FROM {DATABASE}.{SCHEMA}.{HEALTH_TABLE})
) hs ON CAST(o.{CRM_ID_FIELD} AS TEXT) = hs.{CRM_ID_FIELD}
WHERE e.{TIMESTAMP_FIELD} >= DATEADD('day', -90, CURRENT_DATE());

-- 0.4 Event type distribution (90 days)
SELECT 
  {EVENT_TYPE_FIELD}, 
  COUNT(*) AS event_count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS pct_of_total
FROM {DATABASE}.{SCHEMA}.{EVENTS_TABLE} 
WHERE {TIMESTAMP_FIELD} >= DATEADD('day', -90, CURRENT_DATE())
GROUP BY 1 
ORDER BY 2 DESC;

-- 0.5 Health status distribution (latest date)
SELECT 
  {HEALTH_STATUS_FIELD}, 
  COUNT(*) AS company_count
FROM {DATABASE}.{SCHEMA}.{HEALTH_TABLE} 
WHERE {REPORT_DATE_FIELD} = (SELECT MAX({REPORT_DATE_FIELD}) FROM {DATABASE}.{SCHEMA}.{HEALTH_TABLE})
GROUP BY 1 
ORDER BY 2 DESC;

-- ============================================================================
-- STEP 1: Company 360 Dataset (Main Query)
-- ============================================================================

-- This is the primary query to generate company_360 output
-- Aggregates events at org level and joins to health scores

WITH org_events AS (
  SELECT
    e.{ORG_ID_FIELD},
    -- Time windows
    MIN(e.{TIMESTAMP_FIELD}) AS first_event_ts,
    MAX(e.{TIMESTAMP_FIELD}) AS last_event_ts,
    
    -- Activity metrics (90 days)
    COUNT(*) AS events_90d,
    COUNT(DISTINCT DATE_TRUNC('day', e.{TIMESTAMP_FIELD})) AS active_days_90d,
    COUNT(DISTINCT e.{SESSION_ID_FIELD}) AS distinct_sessions_90d,
    
    -- Activity metrics (30 days)
    COUNT(CASE WHEN e.{TIMESTAMP_FIELD} >= DATEADD('day', -30, CURRENT_DATE()) THEN 1 END) AS events_30d,
    COUNT(DISTINCT CASE WHEN e.{TIMESTAMP_FIELD} >= DATEADD('day', -30, CURRENT_DATE()) 
      THEN DATE_TRUNC('day', e.{TIMESTAMP_FIELD}) END) AS active_days_30d,
    
    -- =========================================================================
    -- EVENT TYPE COUNTS
    -- CUSTOMIZE: Update these based on your event types
    -- =========================================================================
    SUM(CASE WHEN e.{EVENT_TYPE_FIELD} = 'page_view' THEN 1 ELSE 0 END) AS page_view_events,
    SUM(CASE WHEN e.{EVENT_TYPE_FIELD} = 'click' THEN 1 ELSE 0 END) AS click_events,
    SUM(CASE WHEN e.{EVENT_TYPE_FIELD} = 'conversion' THEN 1 ELSE 0 END) AS conversion_events,
    SUM(CASE WHEN e.{EVENT_TYPE_FIELD} = 'feature_used' THEN 1 ELSE 0 END) AS feature_events,
    -- Add more event types as needed for your schema
    
    -- Engagement score (customize based on your key engagement events)
    SUM(CASE WHEN e.{EVENT_TYPE_FIELD} IN ('click', 'feature_used', 'export') THEN 1 ELSE 0 END) AS engagement_events,
    
    -- Email coverage (optional enrichment only)
    COUNT(e.{EMAIL_FIELD}) AS events_with_email,
    COUNT(DISTINCT e.{EMAIL_FIELD}) AS unique_emails
    
  FROM {DATABASE}.{SCHEMA}.{EVENTS_TABLE} e
  WHERE e.{TIMESTAMP_FIELD} >= DATEADD('day', -90, CURRENT_DATE())
    AND e.{TIMESTAMP_FIELD} < CURRENT_DATE()  -- Exclude future dates
  GROUP BY e.{ORG_ID_FIELD}
),
latest_health AS (
  SELECT 
    {CRM_ID_FIELD}, 
    {ACCOUNT_ID_FIELD}, 
    {ACCOUNT_NAME_FIELD}, 
    {HEALTH_SCORE_FIELD}, 
    {HEALTH_STATUS_FIELD}, 
    {MRR_FIELD}, 
    {ARR_FIELD}
    -- {CS_OWNER_FIELD},  -- Uncomment if available
    -- {SEGMENT_FIELD}    -- Uncomment if available
  FROM {DATABASE}.{SCHEMA}.{HEALTH_TABLE}
  WHERE {REPORT_DATE_FIELD} = (SELECT MAX({REPORT_DATE_FIELD}) FROM {DATABASE}.{SCHEMA}.{HEALTH_TABLE})
)
SELECT
  -- Identifiers
  oe.{ORG_ID_FIELD} AS org_id,
  o.{ORG_NAME_FIELD} AS org_name,
  CAST(o.{CRM_ID_FIELD} AS TEXT) AS crm_company_id,
  hs.{ACCOUNT_ID_FIELD} AS account_id,
  hs.{ACCOUNT_NAME_FIELD} AS account_name,
  
  -- Health metrics
  hs.{HEALTH_SCORE_FIELD} AS health_score,
  hs.{HEALTH_STATUS_FIELD} AS health_status,
  hs.{MRR_FIELD} AS mrr,
  hs.{ARR_FIELD} AS arr,
  -- hs.{CS_OWNER_FIELD} AS cs_owner,  -- Uncomment if available
  -- hs.{SEGMENT_FIELD} AS segment,    -- Uncomment if available
  
  -- Activity metrics
  oe.events_90d,
  oe.active_days_90d,
  oe.distinct_sessions_90d,
  oe.events_30d,
  oe.active_days_30d,
  oe.first_event_ts,
  oe.last_event_ts,
  
  -- Event type breakdown
  oe.page_view_events,
  oe.click_events,
  oe.conversion_events,
  oe.feature_events,
  oe.engagement_events,
  
  -- Email coverage (optional enrichment)
  oe.events_with_email,
  oe.unique_emails,
  ROUND(oe.events_with_email * 100.0 / NULLIF(oe.events_90d, 0), 2) AS pct_events_with_email,
  
  -- Derived metrics
  ROUND(oe.events_90d * 1.0 / NULLIF(oe.active_days_90d, 0), 2) AS events_per_active_day,
  
  -- Conversion rate: conversion / engagement
  ROUND(oe.conversion_events * 100.0 / NULLIF(oe.engagement_events, 0), 2) AS conversion_rate,
  
  -- Usage frequency classification (90 days)
  CASE
    WHEN oe.active_days_90d >= 45 THEN 'daily_active'
    WHEN oe.active_days_90d >= 12 THEN 'weekly_active'
    WHEN oe.active_days_90d >= 2 THEN 'monthly_active'
    ELSE 'inactive'
  END AS usage_frequency,
  
  -- Activity trend: compare 30d to prior 30d (simplified)
  CASE 
    WHEN oe.events_30d < oe.events_90d * 0.2 THEN 'declining'  -- <20% of 90d in last 30d
    WHEN oe.events_30d > oe.events_90d * 0.4 THEN 'growing'    -- >40% of 90d in last 30d
    ELSE 'stable'
  END AS activity_trend,
  
  -- Stall detection
  CASE 
    WHEN oe.active_days_90d <= 2 THEN TRUE
    WHEN DATEDIFF('day', oe.last_event_ts, CURRENT_DATE()) > 14 THEN TRUE
    ELSE FALSE
  END AS is_stalled,
  
  -- Days since last event
  DATEDIFF('day', oe.last_event_ts, CURRENT_DATE()) AS days_since_last_event

FROM org_events oe
INNER JOIN {DATABASE}.{SCHEMA}.{ORGS_TABLE} o ON oe.{ORG_ID_FIELD} = o.{ORG_ID_FIELD}
LEFT JOIN latest_health hs ON CAST(o.{CRM_ID_FIELD} AS TEXT) = hs.{CRM_ID_FIELD}
WHERE o.{CRM_ID_FIELD} IS NOT NULL
  AND o.{CRM_ID_FIELD} NOT IN ('-1', '0', '')  -- Exclude invalid CRM IDs
ORDER BY oe.events_90d DESC;

-- ============================================================================
-- STEP 2: Cohort-Specific Queries
-- ============================================================================

-- 2.1 Health status vs usage frequency dispersion
-- Shows companies in same health status but different usage patterns
WITH company_360 AS (
  SELECT
    e.{ORG_ID_FIELD},
    o.{ORG_NAME_FIELD},
    CAST(o.{CRM_ID_FIELD} AS TEXT) AS crm_company_id,
    hs.{ACCOUNT_ID_FIELD},
    hs.{ACCOUNT_NAME_FIELD},
    hs.{HEALTH_STATUS_FIELD},
    hs.{HEALTH_SCORE_FIELD},
    hs.{ARR_FIELD},
    COUNT(*) AS events_90d,
    COUNT(DISTINCT DATE_TRUNC('day', e.{TIMESTAMP_FIELD})) AS active_days_90d,
    MAX(e.{TIMESTAMP_FIELD}) AS last_event_ts,
    SUM(CASE WHEN e.{EVENT_TYPE_FIELD} IN ('click', 'feature_used') THEN 1 ELSE 0 END) AS engagement_events,
    SUM(CASE WHEN e.{EVENT_TYPE_FIELD} = 'conversion' THEN 1 ELSE 0 END) AS conversion_events,
    CASE
      WHEN COUNT(DISTINCT DATE_TRUNC('day', e.{TIMESTAMP_FIELD})) >= 45 THEN 'daily_active'
      WHEN COUNT(DISTINCT DATE_TRUNC('day', e.{TIMESTAMP_FIELD})) >= 12 THEN 'weekly_active'
      WHEN COUNT(DISTINCT DATE_TRUNC('day', e.{TIMESTAMP_FIELD})) >= 2 THEN 'monthly_active'
      ELSE 'inactive'
    END AS usage_frequency
  FROM {DATABASE}.{SCHEMA}.{EVENTS_TABLE} e
  INNER JOIN {DATABASE}.{SCHEMA}.{ORGS_TABLE} o ON e.{ORG_ID_FIELD} = o.{ORG_ID_FIELD}
  LEFT JOIN (
    SELECT {CRM_ID_FIELD}, {ACCOUNT_ID_FIELD}, {ACCOUNT_NAME_FIELD}, {HEALTH_STATUS_FIELD}, {HEALTH_SCORE_FIELD}, {ARR_FIELD}
    FROM {DATABASE}.{SCHEMA}.{HEALTH_TABLE}
    WHERE {REPORT_DATE_FIELD} = (SELECT MAX({REPORT_DATE_FIELD}) FROM {DATABASE}.{SCHEMA}.{HEALTH_TABLE})
  ) hs ON CAST(o.{CRM_ID_FIELD} AS TEXT) = hs.{CRM_ID_FIELD}
  WHERE e.{TIMESTAMP_FIELD} >= DATEADD('day', -90, CURRENT_DATE())
    AND o.{CRM_ID_FIELD} IS NOT NULL
    AND o.{CRM_ID_FIELD} NOT IN ('-1', '0', '')
  GROUP BY e.{ORG_ID_FIELD}, o.{ORG_NAME_FIELD}, o.{CRM_ID_FIELD}, hs.{ACCOUNT_ID_FIELD}, hs.{ACCOUNT_NAME_FIELD}, hs.{HEALTH_STATUS_FIELD}, hs.{HEALTH_SCORE_FIELD}, hs.{ARR_FIELD}
)
SELECT
  {HEALTH_STATUS_FIELD} AS health_status,
  usage_frequency,
  COUNT(*) AS company_count,
  AVG(events_90d) AS avg_events,
  AVG(engagement_events) AS avg_engagement,
  AVG(conversion_events) AS avg_conversions,
  AVG(active_days_90d) AS avg_active_days
FROM company_360
WHERE {HEALTH_STATUS_FIELD} IS NOT NULL
GROUP BY {HEALTH_STATUS_FIELD}, usage_frequency
ORDER BY {HEALTH_STATUS_FIELD}, usage_frequency;

-- 2.2 Reason Code Assignment Query
-- Assigns reason codes based on behavior patterns
-- CUSTOMIZE: Update reason codes and thresholds for your business
WITH company_360 AS (
  SELECT
    e.{ORG_ID_FIELD},
    o.{ORG_NAME_FIELD},
    CAST(o.{CRM_ID_FIELD} AS TEXT) AS crm_company_id,
    hs.{ACCOUNT_ID_FIELD},
    hs.{ACCOUNT_NAME_FIELD},
    hs.{HEALTH_STATUS_FIELD},
    hs.{HEALTH_SCORE_FIELD},
    COUNT(*) AS events_90d,
    COUNT(DISTINCT DATE_TRUNC('day', e.{TIMESTAMP_FIELD})) AS active_days_90d,
    MAX(e.{TIMESTAMP_FIELD}) AS last_event_ts,
    SUM(CASE WHEN e.{EVENT_TYPE_FIELD} IN ('click', 'feature_used') THEN 1 ELSE 0 END) AS engagement_events,
    SUM(CASE WHEN e.{EVENT_TYPE_FIELD} = 'conversion' THEN 1 ELSE 0 END) AS conversion_events,
    -- Compare 30d to prior 60d
    SUM(CASE WHEN e.{TIMESTAMP_FIELD} >= DATEADD('day', -30, CURRENT_DATE()) THEN 1 ELSE 0 END) AS events_last_30d,
    SUM(CASE WHEN e.{TIMESTAMP_FIELD} < DATEADD('day', -30, CURRENT_DATE()) THEN 1 ELSE 0 END) AS events_prior_60d
  FROM {DATABASE}.{SCHEMA}.{EVENTS_TABLE} e
  INNER JOIN {DATABASE}.{SCHEMA}.{ORGS_TABLE} o ON e.{ORG_ID_FIELD} = o.{ORG_ID_FIELD}
  LEFT JOIN (
    SELECT {CRM_ID_FIELD}, {ACCOUNT_ID_FIELD}, {ACCOUNT_NAME_FIELD}, {HEALTH_STATUS_FIELD}, {HEALTH_SCORE_FIELD}
    FROM {DATABASE}.{SCHEMA}.{HEALTH_TABLE}
    WHERE {REPORT_DATE_FIELD} = (SELECT MAX({REPORT_DATE_FIELD}) FROM {DATABASE}.{SCHEMA}.{HEALTH_TABLE})
  ) hs ON CAST(o.{CRM_ID_FIELD} AS TEXT) = hs.{CRM_ID_FIELD}
  WHERE e.{TIMESTAMP_FIELD} >= DATEADD('day', -90, CURRENT_DATE())
    AND o.{CRM_ID_FIELD} IS NOT NULL
    AND o.{CRM_ID_FIELD} NOT IN ('-1', '0', '')
  GROUP BY e.{ORG_ID_FIELD}, o.{ORG_NAME_FIELD}, o.{CRM_ID_FIELD}, hs.{ACCOUNT_ID_FIELD}, hs.{ACCOUNT_NAME_FIELD}, hs.{HEALTH_STATUS_FIELD}, hs.{HEALTH_SCORE_FIELD}
)
SELECT
  {ORG_ID_FIELD} AS org_id,
  {ORG_NAME_FIELD} AS org_name,
  crm_company_id,
  {ACCOUNT_ID_FIELD} AS account_id,
  {ACCOUNT_NAME_FIELD} AS account_name,
  {HEALTH_STATUS_FIELD} AS health_status,
  events_90d,
  engagement_events,
  conversion_events,
  events_last_30d,
  events_prior_60d,
  -- Reason code assignment (CUSTOMIZE thresholds for your business)
  CASE
    -- RC1: Usage decay - significant drop in last 30d vs prior period
    WHEN events_prior_60d > 0 AND events_last_30d < events_prior_60d * 0.25 THEN 'RC1'
    -- RC2: High engagement but no conversions
    WHEN engagement_events > 100 AND conversion_events = 0 THEN 'RC2'
    -- RC3: Low overall activity
    WHEN events_90d < 10 THEN 'RC3'
    ELSE 'RC_OTHER'
  END AS reason_code,
  CASE
    WHEN events_prior_60d > 0 AND events_last_30d < events_prior_60d * 0.25 THEN 'usage_decay'
    WHEN engagement_events > 100 AND conversion_events = 0 THEN 'high_engagement_no_convert'
    WHEN events_90d < 10 THEN 'low_activity'
    ELSE 'other'
  END AS reason_label
FROM company_360
WHERE {HEALTH_STATUS_FIELD} IN ('At-Risk', 'Watchlist')  -- CUSTOMIZE status values
ORDER BY events_90d DESC;

-- ============================================================================
-- STEP 3: Export Query for company_360 output
-- ============================================================================
-- Run this query and export results to outputs/company_360.csv

WITH org_events AS (
  SELECT
    e.{ORG_ID_FIELD},
    MIN(e.{TIMESTAMP_FIELD}) AS first_event_ts,
    MAX(e.{TIMESTAMP_FIELD}) AS last_event_ts,
    COUNT(*) AS events_90d,
    COUNT(DISTINCT DATE_TRUNC('day', e.{TIMESTAMP_FIELD})) AS active_days_90d,
    COUNT(DISTINCT e.{SESSION_ID_FIELD}) AS distinct_sessions_90d,
    SUM(CASE WHEN e.{EVENT_TYPE_FIELD} = 'page_view' THEN 1 ELSE 0 END) AS page_view_events,
    SUM(CASE WHEN e.{EVENT_TYPE_FIELD} = 'click' THEN 1 ELSE 0 END) AS click_events,
    SUM(CASE WHEN e.{EVENT_TYPE_FIELD} = 'conversion' THEN 1 ELSE 0 END) AS conversion_events,
    SUM(CASE WHEN e.{EVENT_TYPE_FIELD} = 'feature_used' THEN 1 ELSE 0 END) AS feature_events
  FROM {DATABASE}.{SCHEMA}.{EVENTS_TABLE} e
  WHERE e.{TIMESTAMP_FIELD} >= DATEADD('day', -90, CURRENT_DATE())
    AND e.{TIMESTAMP_FIELD} < CURRENT_DATE()
  GROUP BY e.{ORG_ID_FIELD}
),
latest_health AS (
  SELECT {CRM_ID_FIELD}, {ACCOUNT_ID_FIELD}, {ACCOUNT_NAME_FIELD}, {HEALTH_SCORE_FIELD}, {HEALTH_STATUS_FIELD}, {MRR_FIELD}, {ARR_FIELD}
  FROM {DATABASE}.{SCHEMA}.{HEALTH_TABLE}
  WHERE {REPORT_DATE_FIELD} = (SELECT MAX({REPORT_DATE_FIELD}) FROM {DATABASE}.{SCHEMA}.{HEALTH_TABLE})
)
SELECT
  oe.{ORG_ID_FIELD} AS org_id,
  o.{ORG_NAME_FIELD} AS org_name,
  CAST(o.{CRM_ID_FIELD} AS TEXT) AS crm_company_id,
  hs.{ACCOUNT_ID_FIELD} AS account_id,
  hs.{ACCOUNT_NAME_FIELD} AS account_name,
  hs.{HEALTH_SCORE_FIELD} AS health_score,
  hs.{HEALTH_STATUS_FIELD} AS health_status,
  hs.{MRR_FIELD} AS mrr,
  hs.{ARR_FIELD} AS arr,
  oe.events_90d,
  oe.active_days_90d,
  oe.distinct_sessions_90d,
  oe.first_event_ts,
  oe.last_event_ts,
  oe.page_view_events,
  oe.click_events,
  oe.conversion_events,
  oe.feature_events,
  CASE
    WHEN oe.active_days_90d >= 45 THEN 'daily_active'
    WHEN oe.active_days_90d >= 12 THEN 'weekly_active'
    WHEN oe.active_days_90d >= 2 THEN 'monthly_active'
    ELSE 'inactive'
  END AS usage_frequency
FROM org_events oe
INNER JOIN {DATABASE}.{SCHEMA}.{ORGS_TABLE} o ON oe.{ORG_ID_FIELD} = o.{ORG_ID_FIELD}
LEFT JOIN latest_health hs ON CAST(o.{CRM_ID_FIELD} AS TEXT) = hs.{CRM_ID_FIELD}
WHERE o.{CRM_ID_FIELD} IS NOT NULL
  AND o.{CRM_ID_FIELD} NOT IN ('-1', '0', '')
ORDER BY oe.events_90d DESC;
