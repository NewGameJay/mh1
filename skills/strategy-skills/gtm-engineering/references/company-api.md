# Crustdata Company Discovery API v2

<overview>
The Company Discovery API v2 (`POST /screener/companydb/search`) enables searching for companies matching specific criteria.

**Key Feature for TAM Mapping:** The response includes `total_count` which returns the total number of matching companies even when using `limit: 1`. This enables TAM sizing with minimal credit consumption.
</overview>

<endpoint>
## Endpoint

**URL:** `https://api.crustdata.com/screener/companydb/search`
**Method:** POST
**Authentication:** Bearer token in Authorization header
</endpoint>

<request_schema>
## Request Schema

```json
{
  "filters": {
    "op": "and",
    "conditions": [
      {
        "filter_type": "<filter_name>",
        "type": "<operator>",
        "value": "<value>"
      }
    ]
  },
  "offset": 0,
  "limit": 1,
  "sorts": [
    {
      "filter_type": "<field>",
      "type": "asc|desc"
    }
  ]
}
```

**Key Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `filters` | object | Filter conditions with `op` (and/or) and `conditions` array |
| `limit` | integer | Number of results to return. **Use `1` for TAM counts** |
| `offset` | integer | Pagination offset |
| `sorts` | array | Sort criteria |
</request_schema>

<response_schema>
## Response Schema

```json
{
  "companies": [
    {
      "company_id": "string",
      "company_name": "string",
      "linkedin_url": "string",
      "website": "string",
      "industry": "string",
      "employee_count": 150,
      "hq_country": "string",
      "hq_city": "string",
      "founded_year": 2020,
      "funding_total_usd": 15000000,
      "last_funding_round_type": "series_a",
      "description": "string"
    }
  ],
  "next_cursor": "string",
  "total_count": 1234
}
```

**Key Fields:**
| Field | Description |
|-------|-------------|
| `total_count` | **Total matching companies** - use for TAM sizing |
| `companies` | Array of company records (limited by `limit` param) |
| `next_cursor` | Pagination cursor for next page |
</response_schema>

<filters>
## Available Filters

### Industry & Vertical

| Filter Type | Operator | Value Example | Description |
|-------------|----------|---------------|-------------|
| `linkedin_industries` | `(.)` (contains) | `["Technology", "Software"]` | LinkedIn industry categories |
| `industry` | `=` | `"software"` | General industry |

### Company Size

| Filter Type | Operator | Value Example | Description |
|-------------|----------|---------------|-------------|
| `employee_metrics.latest_count` | `>=`, `<=`, `><` | `50` or `{"min": 50, "max": 500}` | Current headcount |
| `employee_count_range` | `in` | `["51-200", "201-500"]` | Headcount buckets |

### Funding & Stage

| Filter Type | Operator | Value Example | Description |
|-------------|----------|---------------|-------------|
| `last_funding_round_type` | `in` | `["seed", "series_a", "series_b"]` | Latest round type |
| `crunchbase_total_investment_usd` | `>=` | `1000000` | Total raised ($) |
| `funding_date` | `>=` | `"2024-01-01"` | Funding recency |

### Growth Metrics

| Filter Type | Operator | Value Example | Description |
|-------------|----------|---------------|-------------|
| `employee_metrics.growth_12m_percent` | `>=` | `30` | YoY headcount growth % |
| `employee_metrics.growth_6m_percent` | `>=` | `15` | 6-month growth % |

### Geography

| Filter Type | Operator | Value Example | Description |
|-------------|----------|---------------|-------------|
| `hq_country` | `=` | `"United States"` | HQ country |
| `hq_location` | `(.)` | `"San Francisco"` | HQ city/region |

### Company Age

| Filter Type | Operator | Value Example | Description |
|-------------|----------|---------------|-------------|
| `year_founded` | `>=`, `<=` | `2018` | Founded year |
</filters>

<operators>
## Filter Operators

| Operator | Meaning | Use Case |
|----------|---------|----------|
| `=` | Equals | Exact match |
| `in` | In list | Multiple values |
| `>=` | Greater than or equal | Minimum threshold |
| `<=` | Less than or equal | Maximum threshold |
| `><` | Between (range) | Range with min/max |
| `(.)` | Contains | Partial match / array contains |
</operators>

<icp_filter_mappings>
## ICP to Filter Mapping Guide

Use this to translate ICP characteristics into API filters:

### By Company Stage

| ICP Stage | Recommended Filters |
|-----------|---------------------|
| Early-stage startups | `last_funding_round_type: ["seed", "series_a"]`, `employee_metrics.latest_count: {"max": 50}` |
| Growth-stage | `last_funding_round_type: ["series_a", "series_b"]`, `employee_metrics.latest_count: {"min": 50, "max": 500}` |
| Scale-ups | `last_funding_round_type: ["series_b", "series_c"]`, `employee_metrics.latest_count: {"min": 200}` |
| Enterprise | `employee_metrics.latest_count: {"min": 1000}` |

### By Buying Signal

| Signal | Recommended Filters |
|--------|---------------------|
| Recently funded | `funding_date: {"min": "2024-01-01"}`, `crunchbase_total_investment_usd: {"min": 5000000}` |
| Fast-growing | `employee_metrics.growth_12m_percent: {"min": 30}` |
| Tech-focused | `linkedin_industries: ["Technology", "Software", "Internet"]` |
| US-based | `hq_country: "United States"` |
</icp_filter_mappings>

<example_queries>
## Example Queries for Common ICPs

### SaaS Startups (Seed-Series B, 20-200 employees)

```json
{
  "filters": {
    "op": "and",
    "conditions": [
      {"filter_type": "linkedin_industries", "type": "(.)", "value": ["Software", "Technology"]},
      {"filter_type": "last_funding_round_type", "type": "in", "value": ["seed", "series_a", "series_b"]},
      {"filter_type": "employee_metrics.latest_count", "type": ">=", "value": 20},
      {"filter_type": "employee_metrics.latest_count", "type": "<=", "value": 200},
      {"filter_type": "hq_country", "type": "=", "value": "United States"}
    ]
  },
  "limit": 1
}
```

### Fast-Growing Tech Companies

```json
{
  "filters": {
    "op": "and",
    "conditions": [
      {"filter_type": "linkedin_industries", "type": "(.)", "value": ["Technology"]},
      {"filter_type": "employee_metrics.growth_12m_percent", "type": ">=", "value": 30},
      {"filter_type": "employee_metrics.latest_count", "type": ">=", "value": 50}
    ]
  },
  "limit": 1
}
```

### Recently Funded AI/ML Companies

```json
{
  "filters": {
    "op": "and",
    "conditions": [
      {"filter_type": "linkedin_industries", "type": "(.)", "value": ["Artificial Intelligence", "Machine Learning"]},
      {"filter_type": "crunchbase_total_investment_usd", "type": ">=", "value": 5000000},
      {"filter_type": "last_funding_round_type", "type": "in", "value": ["seed", "series_a", "series_b"]}
    ]
  },
  "limit": 1
}
```
</example_queries>

<tam_preview_strategy>
## TAM Preview Strategy (Minimal Credits)

To get a TAM count for proposals without burning significant credits:

1. Build filters matching the prospect's ICP
2. Set `limit: 1` in the request
3. Extract `total_count` from response for TAM size
4. Use the single returned company as a sample/proof point

**Example Response with limit:1:**
```json
{
  "companies": [
    {
      "company_name": "Acme Corp",
      "employee_count": 150,
      "industry": "Software",
      "last_funding_round_type": "series_a"
    }
  ],
  "total_count": 2847
}
```

This tells you: "2,847 companies match this ICP" while only retrieving 1 record.
</tam_preview_strategy>

FULL API DOCUMENTATION

# Company API - Complete Documentation
This document contains the complete documentation for all endpoints in the Company API section.
Generated by combining 9 individual endpoint documentation files.

---

<!-- Error loading /docs/discover/company-apis/company-data-fields -->

# Comprehensive API Documentation: company-discovery-api

## 📋 Documentation Metadata

- **API Path:** `POST /screener/screen/`
- **Category:** Company API
- **Operation:** api
- **Documentation File:** company-discovery-api.md
- **Data Dictionary:** company-discovery.md
- **Generated:** 2025-11-27T14:03:48.587Z

---

## 📊 Data Dictionary

# Company Discovery Dictionary

## Firmographics

| **Column** | **Description** | **Data type** | **Possible values** | **Example value** |
| -------------------------------- | ----------------------------------------------------------------------------------- | --------------------- | --------------------- | --------------------- |
| company_name | Name of the company | string | - | `"Acme Corporation"` |
| last_updated_date | The timestamp when this information was last updated | datetime | - | `"2023-05-15T10:30:45Z"` |
| company_id | ID of the company (from older dictionary) | integer | - | `12345` |
| hq_country | The country where the company's headquarters is located | string | [See HQ Country values](/docs/discover/company-apis/filter-value-enumeration#hq-country) | `"US"` |
| hq_street_address | Street address of company headquarters | string | - | `"123 Main St, San Francisco, CA 94105"` |
| linkedin_logo_url | URL of company's logo image on LinkedIn | string | - | `"https://media.linkedin.com/company/logo.png"` |
| all_office_addresses | List of all office locations/addresses for the company | array[string] | - | `["123 Main St, San Francisco, CA", "456 Park Ave, New York, NY"]` |
| employee_count_range | Range indicating approximate number of employees (e.g. "201-500") | string | [See Employee Count Range values](/docs/discover/company-apis/filter-value-enumeration#employee-count-range) | `"201-500"` |
| company_type | Type of company (e.g. "Privately Held") | string | [See Company Type values](/docs/discover/company-apis/filter-value-enumeration#company-type) | `"Privately Held"` |
| fiscal_year_end | End of company's fiscal year | string | - | `"December"` |
| largest_headcount_country | The country with the most employees of the company | string | [See Largest Headcount Country values](/docs/discover/company-apis/filter-value-enumeration#largest-headcount-country) | `"IN"` |
| last_funding_round_type | The type of the company's last funding round | string | [See Last Funding Round Type values](/docs/discover/company-apis/filter-value-enumeration#last-funding-round-type) | `"Series B"` |
| company_website | The company's official website URL | string | - | `"https://www.acme.com"` |
| company_website_domain | The domain of the company's website | string | - | `"acme.com"` |
| linkedin_categories | The categories of the company on LinkedIn | string | - | `"Color Cosmetics,Skin Care,and Hair Care"` |
| linkedin_industries | The industries in which the company operates, according to LinkedIn | string | [See LinkedIn Industries values](/docs/discover/company-apis/filter-value-enumeration#linkedin-industries) | `"Wholesale,Personal Care Product Manufacturing"` |
| crunchbase_categories | The categories of the company on Crunchbase | string | [See Crunchbase Categories values](/docs/discover/company-apis/filter-value-enumeration#crunchbase-categories) | `"Consumer Goods,Beauty,Fashion"` |
| crunchbase_investors | The investors in the company, according to Crunchbase | string | - | `"Tikehau Capital,Andera Partners"` |
| crunchbase_total_investment_usd | The total amount of investment the company has received, according to Crunchbase | integer | - | `75000000` |
| markets | The markets in which the company operates (e.g., Private / NSE / NASDAQ) | string | - | `"Private"` |
| days_since_last_fundraise | The number of days since the company's last fundraising round | integer | - | `120` |
| linkedin_profile_url | The URL of the company's LinkedIn profile | string | - | `"https://www.linkedin.com/company/acme/"` |
| profile_url | The company's general profile URL (from older dictionary; not necessarily LinkedIn) | string | - | `"https://profile.example.com/acme"` |
| acquisition_status | "acquired" if the company is acquired; empty otherwise | string | [See Acquisition Status values](/docs/discover/company-apis/filter-value-enumeration#acquisition-status) | `"acquired"` |
| year_founded | The year the company was founded | date | - | `"2015-01-01"` |
| technology_domains | The technology domains in which the company operates | array[string] | - | `["Machine Learning", "Big Data", "Cloud Computing"]` |
| twitter_handle | Twitter handle of the company | string | - | `"acme"` |
| linkedin_id | LinkedIn ID of the company | string | - | `"12345678"` |
| linkedin_company_description | Description about the company as put in the "About" section of their LinkedIn page | string | - | `"Acme provides enterprise software solutions..."` |
| company_description | More general company description (from older dictionary) | string | - | `"Global technology provider specializing in..."` |
| stock_symbols | The ticker symbols for publicly traded companies | string | - | `"ACME"` |
| headquarters | HQ location of the company | string | - | `"San Francisco, California, United States"` |
| competitors | List of website domains of competing companies | string | - | `"competitor1.com,competitor2.com"` |
| estimated_revenue_lower_bound_usd | Estimated revenue in USD lower limit | integer | - | `10000000` |
| estimated_revenue_higher_bound_usd | Estimated revenue in USD higher limit | integer | - | `50000000` |

---

## Founder background

| **Column** | **Description** | **Source** | **Example value** |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- | ------------------- |
| founder_names_and_profile_urls | Names and LinkedIn profile URLs of the company's founders and decision makers (CxO and VP/Head of Sales/Marketing/Engineering/Product) | LinkedIn | `"Robert Jaegly ; https://www.linkedin.com/in/..., Miguel Merino ; https://www.linkedin.com/in/..."` |
| founders_location | Geographical location(s) of the company's founders and decision makers (CxO and VP/Head of Sales/Marketing/Engineering/Product) | LinkedIn | `"New York, New York, United States; Kecamatan Medan Area, North Sumatra, Indonesia"` |
| founders_education_institute | Educational institutions attended by the company's founders and decision makers (CxO and VP/Head of Sales/Marketing/Engineering/Product) | LinkedIn | `"The University of Toledo; Owens Community College"` |
| founders_degree_name | Degree(s) held by the company's founders and decision makers (CxO and VP/Head of Sales/Marketing/Engineering/Product) | LinkedIn | `"BS; AD"` |
| founders_previous_company | Previous company(ies) where the company's founders and decision makers (CxO and VP/Head of Sales/Marketing/Engineering/Product) have worked before | LinkedIn | `"Wisdom Delivers; KIK Custom Products; Lanxess; RB; Mana Products; Marianna Industries"` |
| founders_previous_title | Previous job title(s) held by the company's founders and decision makers (CxO and VP/Head of Sales/Marketing/Engineering/Product) | LinkedIn | `"Executive Assistant to CEO; VP of Purchasing Americas"` |
| ceo_location | Location of the company's CEO | LinkedIn | `"San Francisco, CA"` |
| decision_makers_hired_last_three_months | Decision maker titles hired in the last three months | LinkedIn | `"VP Sales, CTO"` |
| decision_makers_hired_last_six_months | Decision maker titles hired in the last six months | LinkedIn | `"VP Sales, CMO"` |
| decision_makers_hired_last_one_year | Decision maker titles hired in the last year | LinkedIn | `"VP Sales, CMO, CFO"` |

---

## Revenue

| **Column** | **Description** | **Source** | **Example value** |
| ---------------------------------- | ------------------------------------- | ---------- | ------------- |
| estimated_revenue_lower_bound_usd | Estimated revenue in USD lower limit | LinkedIn | `10000000` |
| estimated_revenue_higher_bound_usd | Estimated revenue in USD higher limit | LinkedIn | `50000000` |

---

## Employee Headcount

| **Column** | **Description** | **Source** | **Time Series Available** | **Example value** |
| ------------------------------------------------- | ------------------------------------------------------------------------------------ | ---------- | ------------------------- | ------------ |
| linkedin_headcount | The total number of employees at the company | LinkedIn | Yes | `375` |
| linkedin_followers | The total number of followers of the company's LinkedIn profile | LinkedIn | Yes | `12500` |
| linkedin_headcount_engineering | The total number of engineering employees at the company | LinkedIn | Yes | `150` |
| linkedin_headcount_sales | The total number of sales employees at the company | LinkedIn | Yes | `75` |
| linkedin_headcount_operations | The total number of operations employees at the company | LinkedIn | Yes | `50` |
| linkedin_headcount_human_resource | The total number of human resources employees at the company | LinkedIn | Yes | `25` |
| linkedin_headcount_india | The total number of employees based in India at the company | LinkedIn | Yes | `100` |
| linkedin_headcount_usa | The total number of employees based in USA at the company | LinkedIn | Yes | `200` |
| linkedin_headcount_engineering_percent | The percentage of employees that are in engineering roles | LinkedIn | Yes | `40.0` |
| linkedin_headcount_sales_percent | The percentage of employees that are in sales roles | LinkedIn | Yes | `20.0` |
| linkedin_headcount_operations_percent | The percentage of employees that are in operations roles | LinkedIn | Yes | `13.3` |
| linkedin_headcount_human_resource_percent | The percentage of employees that are in human resources roles | LinkedIn | Yes | `6.7` |
| linkedin_headcount_india_percent | The percentage of employees that are based in India | LinkedIn | | `26.7` |
| linkedin_headcount_usa_percent | The percentage of employees that are based in USA | LinkedIn | | `53.3` |
| linkedin_headcount_mom_percent | The month-over-month percentage change in headcount | LinkedIn | | `5.0` |
| linkedin_headcount_qoq_percent | The quarter-over-quarter percentage change in headcount | LinkedIn | | `15.0` |
| linkedin_headcount_yoy_percent | The year-over-year percentage change in headcount | LinkedIn | | `50.0` |
| linkedin_headcount_mom_absolute | The month-over-month absolute change in headcount | LinkedIn | | `18` |
| linkedin_headcount_qoq_absolute | The quarter-over-quarter absolute change in headcount | LinkedIn | | `49` |
| linkedin_headcount_yoy_absolute | The year-over-year absolute change in headcount | LinkedIn | | `125` |
| linkedin_headcount_two_years_growth_percent | The two-year percentage growth in headcount | LinkedIn | | `100.0` |
| linkedin_headcount_two_years_growth_absolute | The two-year absolute growth in headcount | LinkedIn | | `187` |
| linkedin_followers_mom_percent | The month-over-month percentage change in the number of followers | LinkedIn | | `3.0` |
| linkedin_followers_qoq_percent | The quarter-over-quarter percentage change in the number of followers | LinkedIn | | `10.0` |
| linkedin_followers_yoy_percent | The year-over-year percentage change in the number of followers | LinkedIn | | `30.0` |
| linkedin_followers_six_months_growth_percent | The six-month percentage growth in followers | LinkedIn | | `20.0` |
| linkedin_headcount_six_months_growth_percent | The six-month percentage growth in headcount | LinkedIn | | `25.0` |
| linkedin_headcount_six_months_growth_absolute | The six-month absolute growth in headcount | LinkedIn | | `75` |
| linkedin_headcount_sales_six_months_growth_percent | The six months growth percentage in Sales headcount | LinkedIn | | `20.0` |
| linkedin_headcount_sales_yoy_percent | The one year growth percentage in Sales headcount | LinkedIn | | `50.0` |
| linkedin_headcount_operations_six_months_growth_percent | The six months growth percentage in Operations headcount | LinkedIn | | `25.0` |
| linkedin_headcount_operations_yoy_percent | The one year growth percentage in Operations headcount | LinkedIn | | `66.7` |
| linkedin_headcount_quality_assurance_six_months_growth_percent | The six months growth percentage in Quality Assurance headcount | LinkedIn | | `33.3` |
| linkedin_headcount_quality_assurance_yoy_percent | The one year growth percentage in Quality Assurance headcount | LinkedIn | | `100.0` |
| linkedin_headcount_usa_six_months_growth_percent | The six months growth percentage in US headcount | LinkedIn | | `17.6` |
| linkedin_headcount_usa_yoy_percent | The one year growth percentage in US headcount | LinkedIn | | `42.9` |
| linkedin_headcount_india_six_months_growth_percent | The six months growth percentage in India headcount | LinkedIn | | `33.3` |
| linkedin_headcount_india_yoy_percent | The one year growth percentage in India headcount | LinkedIn | | `100.0` |
| linkedin_headcount_mexico_six_months_growth_percent | The six months growth percentage in Mexico headcount | LinkedIn | | `50.0` |
| linkedin_headcount_mexico_yoy_percent | The one year growth percentage in Mexico headcount | LinkedIn | | `100.0` |

---

## Employee Skills

| **Column** | **Description** | **Source** | **Time Series Available** | **Example value** |
| ----------------------------- | ---------------------------------------------------------- | -------- | --------------------- | ----------- |
| linkedin_all_employee_skill_names | All skill names of employees at the company | LinkedIn | | `"Customer Service, Sales, Marketing, Microsoft Office..."` |
| linkedin_all_employee_skill_count | Count of each skill among employees at the company | LinkedIn | Yes | `"92, 84, 83, 79, ..."` |
| linkedin_employee_skills_0_to_10_pct | Percentage of employees with 0-10% proficiency in skills | LinkedIn | | `"Beauty, Communication, Cosmetics"` |
| linkedin_employee_skills_11_to_30_pct | Percentage of employees with 11-30% proficiency in skills | LinkedIn | | `"Beauty, Communication, Customer Service, Fashion"` |
| linkedin_employee_skills_31_to_50_pct | Percentage of employees with 31-50% proficiency in skills | LinkedIn | | `"Customer Service"` |
| linkedin_employee_skills_51_to_70_pct | Percentage of employees with 51-70% proficiency in skills | LinkedIn | | `"Microsoft Office"` |
| linkedin_employee_skills_71_to_100_pct | Percentage of employees with 71-100% proficiency in skills | LinkedIn | | `"Java"` |

---

## Employee Review and Rating

| **Column** | **Description** | **Source** | **Time Series Available** | **Example value** |
| -------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | ---------- | ------------------------- | ----------- |
| glassdoor_overall_rating | The company's overall rating on Glassdoor | Glassdoor | Yes | `4.2` |
| glassdoor_culture_rating | The company's culture rating on Glassdoor | Glassdoor | Yes | `4.0` |
| glassdoor_diversity_rating | The company's diversity rating on Glassdoor | Glassdoor | Yes | `3.8` |
| glassdoor_work_life_balance_rating | The company's work-life balance rating on Glassdoor | Glassdoor | Yes | `4.5` |
| glassdoor_senior_management_rating | The company's senior management rating on Glassdoor | Glassdoor | Yes | `3.9` |
| glassdoor_compensation_rating | The company's compensation rating on Glassdoor | Glassdoor | Yes | `4.1` |
| glassdoor_career_opportunities_rating | The company's career opportunities rating on Glassdoor | Glassdoor | Yes | `4.0` |
| glassdoor_recommend_to_friend_pct | The percentage of Glassdoor reviewers who would recommend the company to a friend | Glassdoor | Yes | `85` |
| glassdoor_ceo_approval_pct | The percentage of Glassdoor reviewers who approve of the CEO | Glassdoor | Yes | `90` |
| glassdoor_business_outlook_pct | The percentage of Glassdoor reviewers with a positive business outlook | Glassdoor | Yes | `80` |
| glassdoor_review_count | The number of reviews of the company on Glassdoor | Glassdoor | Yes | `250` |
| glassdoor_ceo_approval_mom_pct | The month-over-month percentage change in CEO approval rating on Glassdoor | Glassdoor | | `5.0` |
| glassdoor_ceo_approval_qoq_pct | The quarter-over-quarter percentage change in CEO approval rating on Glassdoor | Glassdoor | | `10.0` |
| glassdoor_ceo_approval_yoy_pct | The year-over-year percentage change in CEO approval rating on Glassdoor | Glassdoor | | `15.0` |
| glassdoor_review_count_mom_pct | The month-over-month percentage change in the number of reviews on Glassdoor | Glassdoor | | `7.0` |
| glassdoor_review_count_qoq_pct | The quarter-over-quarter percentage change in the number of reviews on Glassdoor | Glassdoor | | `20.0` |
| glassdoor_review_count_yoy_pct | The year-over-year percentage change in the number of reviews on Glassdoor | Glassdoor | | `50.0` |

---

## Product Reviews

| **Column** | **Description** | **Source** | **Time Series Available** | **Example value** |
| ----------------------------------------------------- | ---------------------------------------------------------------- | ---------- | ------------------------- | ----------- |
| g2_review_count | The number of reviews of the company on G2 | G2 | Yes | `175` |
| g2_average_rating | The company's average rating on G2 | G2 | Yes | `4.3` |
| g2_review_count_mom_pct | The month-over-month % change in the number of reviews on G2 | G2 | | `5.0` |
| g2_review_count_qoq_pct | The quarter-over-quarter % change in the number of reviews on G2 | G2 | | `15.0` |
| g2_review_count_yoy_pct | The year-over-year % change in the number of reviews on G2 | G2 | | `40.0` |

---

## Web Traffic

| **Column** | **Description** | **Source** | **Time Series Available** | **Example value** |
| -------------------------------- | ------------------------------------------------------------------------------ | ---------- | ------------------------- | ----------- |
| monthly_visitors | The number of monthly visitors to the company's site as recorded by Similarweb | Similarweb | Yes | `500000` |
| monthly_visitor_mom_pct | The month-over-month % change in the number of monthly visitors (Similarweb) | Similarweb | | `8.0` |
| traffic_source_social_pct | The % of site traffic from social media (Similarweb) | Similarweb | | `15.0` |
| traffic_source_search_pct | The % of site traffic from search engines (Similarweb) | Similarweb | | `45.0` |
| traffic_source_direct_pct | The % of site traffic from direct (Similarweb) | Similarweb | | `20.0` |
| traffic_source_paid_referral_pct | The % of site traffic from paid referrals (Similarweb) | Similarweb | | `10.0` |
| traffic_source_referral_pct | The % of site traffic from non-paid referrals (Similarweb) | Similarweb | | `10.0` |

---

## Job Listing Growth By Function

| **Column** | **Description** | **Source** | **Example value** |
| ---------------------------------------------------------- | ------------------------------------------------------------- | ---------- | ----------- |
| job_openings_accounting_qoq_pct | Quarterly growth % of job openings in accounting | LinkedIn | `10.0` |
| job_openings_accounting_six_months_growth_pct | Six-month growth % of job openings in accounting | LinkedIn | `25.0` |
| job_openings_art_and_design_qoq_pct | Quarterly growth % of job openings in art and design | LinkedIn | `5.0` |
| job_openings_art_and_design_six_months_growth_pct | Six-month growth % of job openings in art and design | LinkedIn | `15.0` |
| job_openings_business_development_qoq_pct | Quarterly growth % of job openings in business development | LinkedIn | `20.0` |
| job_openings_business_development_six_months_growth_pct | Six-month growth % of job openings in business development | LinkedIn | `40.0` |
| job_openings_engineering_qoq_pct | Quarterly growth % of job openings in engineering | LinkedIn | `25.0` |
| job_openings_engineering_six_months_growth_pct | Six-month growth % of job openings in engineering | LinkedIn | `50.0` |
| job_openings_finance_qoq_pct | Quarterly growth % of job openings in finance | LinkedIn | `10.0` |
| job_openings_finance_six_months_growth_pct | Six-month growth % of job openings in finance | LinkedIn | `20.0` |
| job_openings_human_resource_qoq_pct | Quarterly growth % of job openings in human resources | LinkedIn | `15.0` |
| job_openings_human_resource_six_months_growth_pct | Six-month growth % of job openings in human resources | LinkedIn | `30.0` |
| job_openings_information_technology_qoq_pct | Quarterly growth % of job openings in information technology | LinkedIn | `20.0` |
| job_openings_information_technology_six_months_growth_pct | Six-month growth % of job openings in information technology | LinkedIn | `40.0` |
| job_openings_marketing_qoq_pct | Quarterly growth % of job openings in marketing | LinkedIn | `15.0` |
| job_openings_marketing_six_months_growth_pct | Six-month growth % of job openings in marketing | LinkedIn | `30.0` |
| job_openings_media_and_communication_qoq_pct | Quarterly growth % of job openings in media and communication | LinkedIn | `8.0` |
| job_openings_media_and_communication_six_months_growth_pct | Six-month growth % of job openings in media and communication | LinkedIn | `18.0` |
| job_openings_operations_qoq_pct | Quarterly growth % of job openings in operations | LinkedIn | `12.0` |
| job_openings_operations_six_months_growth_pct | Six-month growth % of job openings in operations | LinkedIn | `25.0` |
| job_openings_research_qoq_pct | Quarterly growth % of job openings in research | LinkedIn | `10.0` |
| job_openings_research_six_months_growth_pct | Six-month growth % of job openings in research | LinkedIn | `22.0` |
| job_openings_sales_qoq_pct | Quarterly growth % of job openings in sales | LinkedIn | `18.0` |
| job_openings_sales_six_months_growth_pct | Six-month growth % of job openings in sales | LinkedIn | `35.0` |
| job_openings_product_management_qoq_pct | Quarterly growth % of job openings in product management | LinkedIn | `15.0` |
| job_openings_product_management_six_months_growth_pct | Six-month growth % of job openings in product management | LinkedIn | `30.0` |
| job_openings_overall_qoq_pct | Quarterly growth % of overall job openings | LinkedIn | `15.0` |
| job_openings_overall_six_months_growth_pct | Six-month growth % of overall job openings | LinkedIn | `30.0` |

---

## Total Job Listings

| **Column** | **Description** | **Source** | **Example value** |
| -------------------------- | -------------------------------------------------------------------------- | ---------- | ----------- |
| recent_job_openings_title | Current job opening titles at the company | LinkedIn | `["Software Engineer", "Product Manager", "Sales Manager"]` |
| job_openings_count | The total count of current job openings at the company | LinkedIn | `45` |
| job_openings_count_mom_pct | The % change in the number of job openings on a month-over-month basis | LinkedIn | `8.0` |
| job_openings_count_qoq_pct | The % change in the number of job openings on a quarter-over-quarter basis | LinkedIn | `20.0` |
| job_openings_count_yoy_pct | The % change in the number of job openings on a year-over-year basis | LinkedIn | `50.0` |

---

## Ads

| **Column** | **Description** | **Source** | **Example value** |
| --------------- | -------------------------------------------- | ---------- | ----------- |
| meta_total_ads | Total ads during the lifetime of the company | Meta | `250` |
| meta_active_ads | Currently active ads by the company | LinkedIn | `75` |
| meta_ad_url | URL of company's page on Meta Ads Library | LinkedIn | `"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=US&view_all_page_id=12345"` |
| meta_ad_platforms | Platforms where the company runs Meta ads | Meta | `["Facebook", "Instagram"]` |
| meta_ad_id | ID of company's Meta ads | Meta | `"123456789"` |

---

## SEO and Google Search Ranking

| **Column** | **Description** | **Source** | **Example value** |
| ------------------------- | -------------------------------------------------------------------------------------------------- | ---------- | ----------- |
| average_organic_rank | Average rank of company domain on keywords for which it ranks in top 100 results | Spyfu | `15` |
| monthly_paid_clicks | Estimated number of clicks on website from Google Ads | Spyfu | `50000` |
| monthly_organic_clicks | Estimated number of clicks on website from organic search results | Spyfu | `250000` |
| average_ad_rank | Average position of all the company domain's ads | Spyfu | `3` |
| total_organic_results | Number of keywords for which the company domain appears in organic search results | Spyfu | `1500` |
| monthly_google_ads_budget | Monthly budget in USD of Google Ads campaigns | Spyfu | `25000` |
| monthly_organic_value | The collective value (in USD) of the company's organic keywords, based on clicks | Spyfu | `75000` |
| total_ads_purchased | Total number of keywords on which the company's domain has advertised | Spyfu | `200` |
| lost_ranks | Number of keywords on which the domain dropped rank this month (still top 100) | Spyfu | `45` |
| gained_ranks | Number of keywords on which the domain improved rank this month (still top 100) | Spyfu | `75` |
| newly_ranked | Number of keywords on which at least one domain page started ranking in top 100 for the first time | Spyfu | `30` |
| paid_seo_competitors_website_domains | List of website domains of companies competing for paid keywords | Spyfu | `"dluxurybrands.com, luxbp.com"` |
| organic_seo_competitors_website_domains | List of website domains of companies competing for organic keywords | Spyfu | `"dluxurybrands.com, luxbp.com"` |

---

## Google Search Impression

| **Column** | **Description** | **Source** | **Time Series Available** | **Example value** |
| ----------------------------- | --------------------------------------------------------------------- | ------ | --------------------- | ----------- |
| impressions | Number of times company is searched on Google | Google | Yes | `100000` |
| google_search_console_analytics_impressions_mom_pct | Monthly growth of the number of times company is searched on Google | Google | | `8.0` |
| google_search_console_analytics_impressions_qoq_pct | Quarterly growth of the number of times company is searched on Google | Google | | `25.0` |
| google_search_console_analytics_impressions_mom_pct | Yearly growth of the number of times company is searched on Google | Google | | `60.0` |

---

## 🔧 OpenAPI Specification

# Discovery API (in-db)

**Category:** Company API
**Base URL:** https://api.crustdata.com
**Official Docs:** /docs/discover/company-apis/company-discovery-api-in-db

**Endpoint:** `POST /screener/screen/`

**Description:** Retrieve a list of companies based on specified metrics and filters
> [Show Docs](/docs/discover/company-apis/company-discovery-api-in-db)

## Authentication
This endpoint requires a Bearer token in the `Authorization` header:

```
Authorization: Token <YOUR_TOKEN>
```
## Request Body Schema

| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `filters` | string | Yes | You can create two types of filters. A Basic Filter or an advanced filter. |  |  |
| `offset` | integer | No | The starting point of the result set. Default value is 0. |  |  |
| `count` | integer | No | The number of results to return in a single request. Maximum value is 100. Default value is 100. |  |  |
| `sorts` | array | No | An array of sorting criteria. Each sort object must contain "column" and "order" fields. |  |  |

## Example Request

```bash
curl -X POST "https://api.crustdata.com/screener/screen/" \
  -H "Authorization: Token &lt;YOUR_TOKEN&gt;" \
  -H "Content-Type: application/json" \
  -d '
    {
      "filters": {
        "op": "and",
        "conditions": [
          {
            "type": "in",
            "value": [
              "2-10",
              "11-50",
              "51-200"
            ],
            "column": "employee_count_range",
            "allow_null": true
          },
          {
            "column": "crunchbase_categories",
            "type": "in",
            "value": [
              "E-Commerce Platforms",
              "B2C",
              "Health Care"
            ]
          }
        ]
      },
      "offset": 0,
      "count": 100,
      "sorts": [
        {
          "column": "monthly_visitor_mom_pct",
          "order": "desc"
        }
      ]
    }
  '
```

## Rate Limiting
All Crustdata API requests count toward your per-minute quota. Inspect the response headers `X-RateLimit-Limit` and `X-RateLimit-Remaining` to monitor usage. Implement exponential back-off or retries when you receive a **429 Too Many Requests** response.

## Responses
### Status 200
**Description:** Successful response
**Response Schema:**
| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `fields` | array | No | An array of objects representing the columns in the dataset. |  |  |
| `rows` | array | No | An array of arrays, each representing a row of data. |  |  |

### Status 400
**Description:** Bad request, please check your request body to fix this error.
**Response Schema:**
| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `error` | string | No |  |  |  |

## 📋 OpenAPI Components

## Response Schema Components

```yaml
schemas:
  CompanyScreeningResponse:
    type: object
    description: "The response is JSON object that consists of two main components - fields and rows. The values in each of the rows elements are ordered in the same sequence as the fields in the fields array. For example, the ith value in a row corresponds to the ith field in the fields array."
    properties:
      fields:
        type: array
        description: "An array of objects representing the columns in the dataset."
      rows:
        type: array
        description: "An array of arrays, each representing a row of data."

  ScreeningRequest:
    type: object
    properties:
      filters:
        type: string
        description: "You can create two types of filters. A Basic Filter or an advanced filter."
      offset:
        type: integer
        description: "The starting point of the result set. Default value is 0."
      count:
        type: integer
        description: "The number of results to return in a single request. Maximum value is 100. Default value is 100."
      sorts:
        type: array
        description: "An array of sorting criteria. Each sort object must contain \"column\" and \"order\" fields."

  FilterGroup:
    type: object
    description: "This is a complex filter object which can contain a complex filter logic."
    properties:
      op:
        type: string
      conditions:
        type: array
        description: "An array of complex filter objects or basic filter objects."

  Condition:
    type: object
    description: "This is a basic filter object which contains a column, a type and a value."
    properties:
      column:
        type: string
        description: "Specify the column to filter data based on your screening criteria."
      type:
        type: string
        description: "Greater than or equal; Lesser than or equal; Equal; Lesser than, Greater than, Not equals, Exactly matches atleast one of the elements of list; Contains, case insensitive; Contains, case sensitive"
      value:
        type: string
        description: "Specify the value for the filter being applied."
      allow_null:
        type: boolean

  ConditionGroup:
    type: object
    description: "This is a complex filter object which can contain a complex filter logic."
    properties:
      op:
        type: string
      conditions:
        type: array
        description: "An array of complex filter objects or basic filter objects."

```

---

# Comprehensive API Documentation: company-discovery-api-in-db-v2

## 📋 Documentation Metadata

- **API Path:** `POST /screener/companydb/search`
- **Category:** Company API
- **Operation:** v2
- **Documentation File:** company-discovery-api-in-db-v2.md
- **Main Documentation:** discover/company-apis/company-discovery-api-in-db-v2.md
- **Generated:** 2025-11-27T14:03:48.598Z

---

## 📖 Original Documentation

# In-DB: Company Search API

### [ 🚀 Try Now ](/api#tag/company-api/post/screener/companydb/search)

Search and filter companies based on various business criteria including size, growth, funding, and industry.

## Endpoint

```
POST /screener/companydb/search
```

## Data Dictionary

[Explore the complete data dictionary for this endpoint here](/docs/dictionary/companydb-search)

## Request Parameters

| **Payload Keys** | **Description**                                                                                      | **Required** |
| ------------- | ---------------------------------------------------------------------------------------------------- | ------------ |
| `filters`     | An object containing the filter conditions. See the Building Complex Filters section below for details.                                                          | Yes         |
| `cursor`      | Pagination cursor from previous response. Used for fetching the next page of results.                 | No          |
| `limit`       | The number of results to return in a single request. Default value is `20`. Maximum is `1,000`.      | No          |
| `sorts`       | An array of sorting criteria. Each sort object should have `column` and `order` (asc/desc) fields.   | No          |

## Credit Usage

- **Company Discovery**: 1 credits per 100 results returned
- **No Results, No Charges**: You are never charged credits when our APIs return no results. Credits are only deducted when data is successfully returned from your API requests.

## Finding Valid Filter Values with Autocomplete

Use the **[CompanyDB Autocomplete API](/docs/discover/auxiliary-apis/companydb-autocomplete)** to find exact field values for your search filters. This dedicated autocomplete endpoint helps you discover what values exist in our database.

### 🔍 When to Use CompanyDB Autocomplete API

**Use Case 1: Discover Valid Field Values**
- Get possible values for any field returned by the CompanyDB search endpoint
- Convert partial or fuzzy text into matching value stored in our data for a field

**Use Case 2: Build Dynamic Search Interfaces**  
- Power autocomplete dropdowns and search suggestions in your UI
- Create responsive search experiences with accurate field matching

### Quick Example: Finding Industry Values

#### Step 1: Get industry suggestions
```bash
curl -X POST 'https://api.crustdata.com/screener/companydb/autocomplete' \
--header 'Authorization: Token $authToken' \
--header 'Content-Type: application/json' \
--data '{
    "field": "linkedin_industries",
    "query": "software",
    "limit": 5
}'
```

#### Step 2: Use exact value in your search
```bash
curl -X POST 'https://api.crustdata.com/screener/companydb/search' \
--header 'Authorization: Token $authToken' \
--header 'Content-Type: application/json' \
--data '{
    "filters": {
        "filter_type": "linkedin_industries",
        "type": "=",
        "value": "Software Development"
    }
}'
```

**💡 Tip**: The autocomplete API works with **any field** from the [data dictionary](/docs/dictionary/companydb-search)

## Filter Operators

### Matching Operators
| **Operator** | **Description** | **Example** | **Field Types** |
| ------------ | --------------- | ----------- | --------------- |
| `=` | Exact match | `{"type": "=", "value": "Private"}` | All |
| `!=` | Not equal to | `{"type": "!=", "value": "Acquired"}` | All |
| `in` | Matches any value in list | `{"type": "in", "value": ["series_a", "series_b", "series_c"]}` | All |
| `not_in` | Doesn't match any value in list | `{"type": "not_in", "value": ["Government", "Non-Profit"]}` | All |

:::note Case Sensitivity
The `=` operator performs **case-insensitive** matching for text fields (e.g., searching for "private" will match "Private", "PRIVATE", or "private"). 

The `in` operator performs **exact, case-sensitive** matching. When using `in`, ensure your values match the exact casing in the data. 
:::

:::tip Getting Exact Values for Filters
For best results with `=` and `in` operators, use the [CompanyDB Autocomplete API](/docs/discover/auxiliary-apis/companydb-autocomplete) to get exact field values
:::

### Comparison Operators
| **Operator** | **Description** | **Example** | **Field Types** |
| ------------ | --------------- | ----------- | --------------- |
| `>` | Greater than | `{"type": ">", "value": 100}` | Number, Date |
| `<` | Less than | `{"type": "<", "value": 10000}` | Number, Date |
| `=>` | Greater than or equal | `{"type": "=>", "value": 50}` | Number, Date |
| `=<` | Less than or equal | `{"type": "=<", "value": 500}` | Number, Date |

### Text Search Operators
| **Operator** | **Description** | **Example** | **Field Types** |
| ------------ | --------------- | ----------- | --------------- |
| `(.)` | Text search with fuzzy matching (allows typos) | `{"type": "(.)", "value": "technology"}` | Text |
| `[.]` | Exact token matching (no typos allowed) | `{"type": "[.]", "value": "Software Development"}` | Text |

:::tip Text Search Operators Best Practices
**Understanding the difference between `(.)` and `[.]`:**

- **`(.)` Fuzzy matching**: 
  - Allows typos and word edits (fuzzy matching)
  - Doesn't strictly respect word order
  - Multi-word searches: Each word is searched independently (all must be present but in any order)
  - Example: "Cloud Computing" may match "Computing Cloud" or "Cloud-based Computing Services"
  
- **`[.]` Exact token matching**: 
  - No typos allowed, requires exact tokens

**When to use which:**
- Use `(.)` for flexible searching when you want to find variations and don't mind typos
- Use `[.]` when you need exact matches without any variations (useful for specific company names or technical terms)
- Prefer `(.)` over `in` or `=` unless you have exact values from the [CompanyDB Autocomplete API](/docs/discover/auxiliary-apis/companydb-autocomplete)
:::

:::info Usage Notes
- **Text fields**: Prefer the fuzzy operator `(.)` for partial matches with automatic typo handling. Use exact match (`=`) or `in` only when you have exact values from the [CompanyDB Autocomplete API](/docs/discover/auxiliary-apis/companydb-autocomplete)
- **Numeric fields**: All operators work with numeric values like `employee_metrics.latest_count`, `crunchbase_total_investment_usd`
- **Date fields**: Comparison operators work with ISO date strings like `"2024-01-01"`. Note that date fields will only appear in the response if they exist in the data
- **Boolean fields**: Use `=` with `true` or `false` values
:::

## Location Filtering

### How It Works

When you filter by the `hq_location` field, the API automatically searches across both:
1. **Main location field** - The complete location string (e.g., "San Francisco, California, United States")
2. **Address components field** - Individual location hierarchy components (city, state, country)

This ensures flexible location matching regardless of data formatting.

### Example

When searching for companies in California:
```json
{
  "filter_type": "hq_location",
  "type": "(.)",
  "value": "California"
}
```

This automatically expands to search both:
- Companies with "California" in their full HQ location string
- Companies with "California" as one of their address components

**Note:** This automatic expansion works with all filter operators (=, !=, in, not_in, (.), [.]), providing consistent behavior across different search methods. You don't need to explicitly use the address_components field - it's handled automatically.

## Building Complex Filters

### Basic Filter Structure

Each filter condition requires three components:
- `filter_type`: The field to filter on (e.g., "company_name")
- `type`: The operator to use (e.g., "=", "in", "(.)")
- `value`: The value(s) to match

```json
{
    "filter_type": "company_type",
    "type": "=",
    "value": "Private"
}
```

### Combining Multiple Conditions

Use `op` with "and" or "or" to combine multiple filter conditions:

```json
{
    "op": "and",
    "conditions": [
        {
            "filter_type": "hq_country",
            "type": "=",
            "value": "United States"
        },
        {
            "filter_type": "employee_metrics.latest_count",
            "type": ">",
            "value": 100
        }
    ]
}
```

### Nested Conditions

You can nest AND/OR conditions for complex logic:

```json
{
    "op": "and",
    "conditions": [
        {
            "filter_type": "linkedin_industries",
            "type": "in",
            "value": ["Software Development", "Information Technology"]
        },
        {
            "op": "or",
            "conditions": [
            {
                "filter_type": "last_funding_round_type",
                "type": "in",
                "value": ["series_a", "series_b"]
            },
                {
                    "filter_type": "employee_metrics.growth_6m_percent",
                    "type": ">",
                    "value": 20
                }
            ]
        }
    ]
}
```

:::warning Important: Array Field Matching
When using filters with array fields (like linkedin_industries, crunchbase_categories, markets), the filter matches if ANY element in the array satisfies the condition.

**Example:** 
- `linkedin_industries in ["Software Development", "Cloud Computing"]` 
  - ✅ Matches if a company has EITHER "Software Development" OR "Cloud Computing" in its industries
  - The company doesn't need to have both - just one is sufficient
:::

## Example Requests

<details>
<summary>1. Basic company search examples</summary>

### 1. Basic company search examples

Find private companies:

```bash
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "filter_type": "company_type",
        "type": "=",
        "value": "Private"
    },
    "limit": 100
}' \
--compressed
```

Find companies whose name contains "tech" (text search with fuzzy matching):

```bash
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "filter_type": "company_name",
        "type": "(.)",
        "value": "tech"
    },
    "limit": 100
}' \
--compressed
```

Find companies founded after 2020:

```bash
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "filter_type": "year_founded",
        "type": ">",
        "value": 2020
    },
    "limit": 100
}' \
--compressed
```
</details>

<details>
<summary>2. Filter by company size and growth</summary>

### 2. Filter by company size and growth

Find high-growth companies (>50% employee growth in 6 months):

```bash
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "op": "and",
        "conditions": [
            {
                "filter_type": "employee_metrics.growth_6m_percent",
                "type": ">",
                "value": 50
            },
            {
                "filter_type": "employee_metrics.latest_count",
                "type": ">",
                "value": 50
            }
        ]
    },
    "limit": 50
}' \
--compressed
```

Find mid-size companies (201-1000 employees) with positive growth:

```bash
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "op": "and",
        "conditions": [
            {
                "filter_type": "employee_count_range",
                "type": "in",
                "value": ["201-500", "501-1000"]
            },
            {
                "filter_type": "employee_metrics.growth_12m",
                "type": ">",
                "value": 0
            }
        ]
    },
    "limit": 100
}' \
--compressed
```
</details>

<details>
<summary>3. Filter by funding and financial metrics</summary>

### 3. Filter by funding and financial metrics

Find recently funded companies (Series A/B/C in last year):

```bash
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "op": "and",
        "conditions": [
            {
                "filter_type": "last_funding_round_type",
                "type": "in",
                "value": ["series_a", "series_b", "series_c"]
            },
            {
                "filter_type": "last_funding_date",
                "type": "=>",
                "value": "2023-01-01"
            }
        ]
    },
    "limit": 100
}' \
--compressed
```

Find companies with significant funding (>$10M total):

```bash
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "op": "and",
        "conditions": [
            {
                "filter_type": "crunchbase_total_investment_usd",
                "type": ">",
                "value": 10000000
            },
            {
                "filter_type": "company_type",
                "type": "=",
                "value": "Private"
            }
        ]
    },
    "limit": 100
}' \
--compressed
```

Find companies by revenue range:

```bash
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "op": "and",
        "conditions": [
            {
                "filter_type": "estimated_revenue_lower_bound_usd",
                "type": "=>",
                "value": 1000000
            },
            {
                "filter_type": "estimated_revenue_higher_bound_usd",
                "type": "=<",
                "value": 50000000
            }
        ]
    },
    "limit": 100
}' \
--compressed
```
</details>

<details>
<summary>4. Filter by location</summary>

### 4. Filter by location

Find companies headquartered in specific countries:

```bash
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "op": "and",
        "conditions": [
            {
                "filter_type": "hq_country",
                "type": "in",
                "value": ["USA", "CAN", "GBR"]
            },
            {
                "filter_type": "employee_metrics.latest_count",
                "type": ">",
                "value": 100
            }
        ]
    },
    "limit": 100
}' \
--compressed
```

Find companies with largest workforce in specific country:

```bash
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "op": "and",
        "conditions": [
            {
                "filter_type": "largest_headcount_country",
                "type": "=",
                "value": "India"
            },
            {
                "filter_type": "hq_country",
                "type": "!=",
                "value": "India"
            }
        ]
    },
    "limit": 50
}' \
--compressed
```
</details>

<details>
<summary>5. Filter by industry and categories</summary>

### 5. Filter by industry and categories

Find SaaS companies in specific industries:

```bash
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "op": "and",
        "conditions": [
            {
                "filter_type": "crunchbase_categories",
                "type": "in",
                "value": ["SaaS", "Software as a Service"]
            },
            {
                "filter_type": "linkedin_industries",
                "type": "in",
                "value": ["Software Development", "Information Technology"]
            }
        ]
    },
    "limit": 100
}' \
--compressed
```

Find B2B enterprise companies:

```bash
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "op": "and",
        "conditions": [
            {
                "filter_type": "markets",
                "type": "in",
                "value": ["B2B", "Enterprise"]
            },
            {
                "filter_type": "employee_metrics.latest_count",
                "type": ">",
                "value": 50
            }
        ]
    },
    "limit": 100
}' \
--compressed
```
</details>

<details>
<summary>6. Complex nested filter example</summary>

### 6. Complex nested filter example

Find high-growth tech startups with recent funding:

```bash
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "op": "and",
        "conditions": [
            {
                "op": "or",
                "conditions": [
                    {
                        "filter_type": "last_funding_round_type",
                        "type": "in",
                        "value": ["series_a", "series_b", "series_c"]
                    },
                    {
                        "filter_type": "crunchbase_total_investment_usd",
                        "type": ">",
                        "value": 5000000
                    }
                ]
            },
            {
                "filter_type": "employee_metrics.growth_12m_percent",
                "type": "=>",
                "value": 30
            },
            {
                "filter_type": "linkedin_industries",
                "type": "(.)",
                "value": "technology"
            },
            {
                "filter_type": "year_founded",
                "type": ">",
                "value": 2015
            }
        ]
    },
    "limit": 50
}' \
--compressed
```
</details>

<details>
<summary>7. Filter by social media metrics</summary>

### 7. Filter by social media metrics

Find companies with strong LinkedIn presence and growth:

```bash
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "op": "and",
        "conditions": [
            {
                "filter_type": "follower_metrics.latest_count",
                "type": ">",
                "value": 10000
            },
            {
                "filter_type": "follower_metrics.growth_6m_percent",
                "type": ">",
                "value": 25
            }
        ]
    },
    "limit": 50
}' \
--compressed
```
</details>

<details>
<summary>8. Filter by corporate status</summary>

### 8. Filter by corporate status

Find public companies that went IPO recently:

```bash
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "op": "and",
        "conditions": [
            {
                "filter_type": "company_type",
                "type": "=",
                "value": "Public"
            },
            {
                "filter_type": "ipo_date",
                "type": "=>",
                "value": "2020-01-01"
            }
        ]
    },
    "limit": 50
}' \
--compressed
```

Find companies that were acquired:

```bash
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "filter_type": "acquisition_status",
        "type": "=",
        "value": "Acquired"
    },
    "limit": 100
}' \
--compressed
```
</details>

<details>
<summary>9. Find companies by LinkedIn URL or ID</summary>

### 9. Find companies by LinkedIn URL or ID

Find a company using its LinkedIn profile URL:

```bash
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "filter_type": "linkedin_profile_url",
        "type": "=",
        "value": "https://www.linkedin.com/company/microsoft"
    },
    "limit": 10
}' \
--compressed
```

Find a company using its LinkedIn ID:

```bash
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "filter_type": "linkedin_id",
        "type": "=",
        "value": "1035"
    },
    "limit": 10
}' \
--compressed
```

Find multiple companies by LinkedIn IDs:

```bash
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "filter_type": "linkedin_id",
        "type": "in",
        "value": ["1035", "1441", "2494"]
    },
    "limit": 10
}' \
--compressed
```

Note: The LinkedIn ID is the numeric identifier from the company's LinkedIn URL. For example, if the LinkedIn URL is `https://www.linkedin.com/company/1035/`, the LinkedIn ID is `1035`.

**How to get the LinkedIn ID or URL:** You can use the free [Company Identification API](/docs/discover/company-apis/company-identification-api) to get a company's `linkedin_id` and `linkedin_url` by providing its website domain:
- Example input: `query_company_website`: `"microsoft.com"` or `query_company_linkedin_url`: `"https://www.linkedin.com/company/microsoft"`
- Example output: `linkedin_id`: `"1035"` (Microsoft's LinkedIn ID), `linkedin_url`: `"https://www.linkedin.com/company/microsoft"`
</details>

<details>
<summary>10. Find companies by domain</summary>

### 10. Find companies by domain

Find a company by its website domain:

```bash
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "filter_type": "company_website_domain",
        "type": "=",
        "value": "tesla.com"
    },
    "limit": 10
}' \
--compressed
```

Find multiple companies by their domains:

```bash
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "filter_type": "company_website_domain",
        "type": "in",
        "value": ["apple.com", "google.com", "microsoft.com", "amazon.com"]
    },
    "limit": 20
}' \
--compressed
```

Find companies with specific domain patterns:

```bash
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "op": "and",
        "conditions": [
            {
                "filter_type": "company_website_domain",
                "type": "(.)",
                "value": ".ai"
            },
            {
                "filter_type": "crunchbase_categories",
                "type": "in",
                "value": ["Artificial Intelligence", "Machine Learning"]
            }
        ]
    },
    "limit": 100
}' \
--compressed
```
</details>

<details>
<summary>11. Find competitors of specific companies</summary>

### 11. Find competitors of specific companies

Find competitors by competitor IDs:

```bash
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "filter_type": "competitor_ids",
        "type": "in",
        "value": ["12345", "67890"]
    },
    "limit": 50
}' \
--compressed
```

Find competitors by competitor websites:

```bash
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "filter_type": "competitor_websites",
        "type": "in",
        "value": ["competitor1.com", "competitor2.com"]
    },
    "limit": 50
}' \
--compressed
```
</details>

<details>
<summary>12. Find companies with specific investors</summary>

### 12. Find companies with specific investors

Find companies backed by specific VCs:

```bash
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "op": "or",
        "conditions": [
            {
                "filter_type": "crunchbase_investors",
                "type": "in",
                "value": ["Sequoia Capital", "Andreessen Horowitz", "Accel"]
            },
            {
                "filter_type": "tracxn_investors",
                "type": "in",
                "value": ["Y Combinator", "500 Startups"]
            }
        ]
    },
    "limit": 100
}' \
--compressed
```
</details>

## Example Response

[Sample Response](/examples/company-search/companydb-response.json)

## Pagination

This API uses cursor-based pagination for efficient data retrieval:
- `cursor`: Pagination cursor from previous response (optional)
- `limit`: Results per page (default: 20, max: 1,000)

The response includes:
- `next_cursor`: Cursor for fetching the next page
- `total_count`: Total number of results matching your filters

### How Cursor Pagination Works

1. **First Request**: Don't include a cursor
2. **Subsequent Requests**: Use the `next_cursor` from the previous response
3. **End of Results**: When no more results exist, the next request returns an empty `companies` array

:::info Important
- The cursor is tied to your specific query (filters + sorts). Using a cursor with different query parameters will return an error.
- Cursors should be treated as opaque strings and not modified.
:::

<details>
<summary>Paginating through results</summary>

```bash
# First page (companies 1-100)
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
--data-raw '{
    "filters": { ... },
    "limit": 100
}'
# Response: { "companies": [...], "next_cursor": "eJx1jjEOwjAMRe...", "total_count": 250 }

# Second page (companies 101-200)
curl 'https://api.crustdata.com/screener/companydb/search/' \
-H "Authorization: Token $auth_token" \
--data-raw '{
    "filters": { ... },
    "limit": 100,
    "cursor": "eJx1jjEOwjAMRe..."
}'
# Response: { "companies": [...], "next_cursor": "eJx2kLEOwjAMRe...", "total_count": 250 }

# Eventually, when no more results:
# Response: { "companies": [], "total_count": 250 }
```
</details>

**Best Practices:**
- Use consistent filters across all pagination requests
- Check if `companies` array is empty to determine end of results
- Store the cursor if you need to resume pagination later

## Sorting

You can sort results by any numeric or date field. The sorts parameter accepts an array of sort objects:

```json
{
    "sorts": [
        {
            "column": "employee_metrics.latest_count",
            "order": "desc"
        },
        {
            "column": "year_founded",
            "order": "asc"
        }
    ]
}
```

Common sort fields:
- `employee_metrics.latest_count` - Sort by company size
- `employee_metrics.growth_12m_percent` - Sort by growth rate
- `crunchbase_total_investment_usd` - Sort by total funding
- `last_funding_date` - Sort by recent funding activity
- `follower_metrics.latest_count` - Sort by social media presence
- `year_founded` - Sort by company age

## Best Practices

1. **Use specific filters** to reduce result set size and improve performance
2. **Combine multiple criteria** for more targeted searches
3. **Use pagination** for large result sets
4. **Cache results** when appropriate to reduce API calls
5. **Use the autocomplete API** to get exact values for filters

## Common Use Cases

1. **Market Research**: Filter by industry, size, and location to understand market landscape
2. **Investment Scouting**: Find high-growth companies with recent funding rounds
3. **Competitive Analysis**: Identify competitors by industry and company characteristics
4. **Sales Prospecting**: Target companies by size, growth, and technology stack
5. **Partnership Discovery**: Find companies with complementary markets or technologies
6. **M&A Research**: Identify acquisition targets by financial metrics and growth

## Rate Limits and Performance

- Rate limit: 60 requests per minute (RPM)
- Maximum 1,000 companies per request
- Consider using specific filters to improve response time
- Use sorting and pagination efficiently for large datasets

---

## 🔧 OpenAPI Specification

# Company Discovery API v2 (In-DB)

**Category:** Company API
**Base URL:** https://api.crustdata.com
**Official Docs:** /docs/discover/company-apis/company-discovery-api-in-db-v2

**Endpoint:** `POST /screener/companydb/search`

**Description:** In-database search API for company data, enabling you to search across millions of 
companies with advanced filtering capabilities and improved performance.

**Note:** This API is currently in beta and available by invitation only.
> [Show Docs](/docs/discover/company-apis/company-discovery-api-in-db-v2)

## Authentication
This endpoint requires a Bearer token in the `Authorization` header:

```
Authorization: Token <YOUR_TOKEN>
```
## Request Body Schema

| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `filters` | string | Yes | Filter conditions for searching companies. Can be a simple condition or complex nested conditions with AND/OR logic. |  |  |
| `cursor` | string | No | Pagination cursor from previous response. Used for fetching the next page of results. |  |  |
| `limit` | integer | No | The number of results to return in a single request. Default value is 20. Maximum is 1,000. |  |  |
| `sorts` | array | No | Array of sort criteria |  |  |

## Example Request

```bash
curl -X POST "https://api.crustdata.com/screener/companydb/search" \
  -H "Authorization: Token &lt;YOUR_TOKEN&gt;" \
  -H "Content-Type: application/json" \
  -d '
    {
      "filters": {
        "op": "and",
        "conditions": [
          {
            "op": "or",
            "conditions": [
              {
                "filter_type": "last_funding_round_type",
                "type": "in",
                "value": [
                  "series_a",
                  "series_b",
                  "series_c"
                ]
              },
              {
                "filter_type": "crunchbase_total_investment_usd",
                "type": ">",
                "value": 5000000
              }
            ]
          },
          {
            "filter_type": "employee_metrics.growth_12m_percent",
            "type": "=>",
            "value": 30
          },
          {
            "filter_type": "linkedin_industries",
            "type": "(.)",
            "value": "technology"
          },
          {
            "filter_type": "year_founded",
            "type": ">",
            "value": 2015
          }
        ]
      },
      "limit": 50,
      "sorts": [
        {
          "column": "employee_metrics.growth_12m_percent",
          "order": "desc"
        }
      ]
    }
  '
```

## Rate Limiting
All Crustdata API requests count toward your per-minute quota. Inspect the response headers `X-RateLimit-Limit` and `X-RateLimit-Remaining` to monitor usage. Implement exponential back-off or retries when you receive a **429 Too Many Requests** response.

## Responses
### Status 200
**Description:** A JSON response containing a list of companies with pagination support.
**Response Schema:**
| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `companies` | array | Yes | Array of companies matching the search criteria |  |  |
| `next_cursor` | string | No | Cursor for fetching the next page of results |  |  |
| `total_count` | integer | No | Total number of companies matching the search criteria |  |  |

### Status 400
**Description:** Bad request, please check your request body to fix this error.
**Response Schema:**
| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `error` | string | No |  |  |  |

## 📋 OpenAPI Components

## Response Schema Components

```yaml
schemas:
  CompanyDBSearchResponse:
    type: object
    properties:
      companies:
        type: array
        description: "Array of companies matching the search criteria"
      next_cursor:
        type: string
        description: "Cursor for fetching the next page of results"
      total_count:
        type: integer
        description: "Total number of companies matching the search criteria"

  CompanyDBSearchRequest:
    type: object
    properties:
      filters:
        type: string
        description: "Filter conditions for searching companies. Can be a simple condition or complex nested conditions with AND/OR logic."
      cursor:
        type: string
        description: "Pagination cursor from previous response. Used for fetching the next page of results."
      limit:
        type: integer
        description: "The number of results to return in a single request. Default value is 20. Maximum is 1,000."
      sorts:
        type: array
        description: "Array of sort criteria"

  CompanyDBCondition:
    type: object
    description: "Basic filter condition for CompanyDB search"
    properties:
      filter_type:
        type: string
        description: "The field to filter on (e.g., \"company_name\", \"hq_country\", \"employee_metrics.latest_count\")"
      type:
        type: string
        description: "The operator to use for comparison. Use (.) for fuzzy text matching, [.] for exact token matching."
      value:
        type: string
        description: "The value(s) to match against"

  CompanyDBConditionGroup:
    type: object
    description: "Complex filter group for CompanyDB search with AND/OR logic"
    properties:
      op:
        type: string
        description: "Logical operator to combine conditions"
      conditions:
        type: array
        description: "Array of conditions to combine"

  CompanyDBProfile:
    type: object
    description: "Comprehensive company profile from CompanyDB"
    properties:
      company_id:
        type: string
        description: "Unique identifier for the company"
      company_name:
        type: string
        description: "Name of the company"
      year_founded:
        type: integer
        description: "Year the company was founded"
      company_type:
        type: string
        description: "Type of company (e.g., Private, Public, Non-Profit)"
      acquisition_status:
        type: string
        description: "Acquisition status of the company"
      # ... (41 more properties)

```

---

# Comprehensive API Documentation: company-enrichment-api

## 📋 Documentation Metadata

- **API Path:** `GET /screener/company`
- **Category:** Company API
- **Operation:** api
- **Documentation File:** company-enrichment-api.md
- **Data Dictionary:** company-enrichment.md
- **Main Documentation:** discover/company-apis/company-enrichment-api.md
- **Generated:** 2025-11-27T14:03:48.580Z

---

## 📖 Original Documentation

# Company Enrichment API

### [ 🚀 Try Now ](/api#tag/company-api/get/screener/company)

This endpoint enriches company data by retrieving detailed information about one or multiple companies using either their domain, name, or ID.

## Endpoint

```
GET /screener/company
```
## Data Dictionary 

[Explore the data dictionary for this endpoint here](/docs/dictionary/company-enrichment)

## Request Parameters

| Field                  | Type    | Example                                                     | Description                                                                                                                                                    |
| ---------------------- | ------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `company_domain`       | string  | `company_domain=crustdata.com,google.com`                     | The domain(s) of the company(ies) you want to retrieve data for. Accepts comma-separated list of up to 25 domains.                                             |
| `company_name`         | string  | `company_name="Acme, Inc.","Widget Co"`                     | The name(s) of the company(ies) you want to retrieve data for. Accepts comma-separated list of up to 25 names. Use double quotes if names contain commas.      |
| `company_linkedin_url` | string  | `company_linkedin_url=` `https://linkedin.com/company/hubspot` | The LinkedIn URL(s) of the company(ies). Accepts comma-separated list of up to 25 URLs.                                                                        |
| `company_id`           | integer | `company_id=12345,67890`                                    | The unique ID(s) of the company(ies) you want to retrieve data for. Accepts comma-separated list of up to 25 IDs.                                              |
| `fields`               | string  | `fields=headcount,funding_and_investment`         | Specifies which fields to include in the response. If not provided, returns basic company info and firmographics only. [See all fields](/docs/dictionary/company-enrichment) |
| `enrich_realtime`      | boolean | `enrich_realtime=true`                                      | When True and the requested company is not present in Crustdata's database, the company is enriched within 10 minutes of the request. Default: False           |
| `exact_match`          | boolean | `exact_match=true`                                          | Determines whether the company identifier should be matched exactly (true) or by the best match logic (false). Default: False                                  |

:::tip
The `fields` parameter allows you to customize the response by specifying exactly which fields you want to retrieve. This can help reduce payload size and improve performance.

-   **Default behavior**: Without the `fields` parameter, only basic company information and select firmographics are returned
-   **With fields parameter**: Returns only the explicitly requested fields
-   **Nested Fields:** You can specify nested fields up to the levels defined in the response structure (see [available fields here](/docs/dictionary/company-enrichment)). Fields nested beyond the allowed levels or within lists (arrays) cannot be individually accessed.
-   **User Permissions:** Access to certain fields may be restricted based on your user permissions. If you request fields you do not have access to, the API will return an error indicating unauthorized access.

:::

### Important: Fields Parameter Usage {#important-fields-parameter-usage}

#### Default Response Behavior

Without the `fields` parameter, the API returns only:
- Basic company information (company_id, company_name, domains, LinkedIn info, etc.)
- Select firmographics fields (headquarters, year_founded, revenue estimates, etc.)
- **NO nested objects** (headcount, web_traffic, funding, glassdoor, etc.)

#### Getting Additional Data

To retrieve nested data objects like headcount, web_traffic, or funding information, you MUST explicitly include them in the `fields` parameter:
- Example: `fields=headcount,web_traffic,funding_and_investment`
- This returns ONLY the specified fields

### Replicating Previous Default Behavior

To get the same fields that were returned by default before this update, use this request:

```bash
curl 'https://api.crustdata.com/screener/company?company_domain=example.com&fields=headcount,competitors,funding_and_investment,g2,gartner,glassdoor,job_openings,linkedin_followers,news_articles,producthunt,seo,taxonomy,web_traffic,founders.founders_locations,founders.founders_education_institute,founders.founders_degree_name,founders.founders_previous_companies,founders.founders_previous_titles' \
--header 'Authorization: Token $authToken'
```

**Additional fields available:** The above excludes `decision_makers`, `founders.profiles` (detailed profiles), and `cxos` which were not in the previous default. To include these as well:

```bash
curl 'https://api.crustdata.com/screener/company?company_domain=example.com&fields=headcount,competitors,funding_and_investment,g2,gartner,glassdoor,job_openings,linkedin_followers,news_articles,producthunt,seo,taxonomy,web_traffic,decision_makers,founders,cxos' \
--header 'Authorization: Token $authToken'
```

## Credit Usage

- **Database Enrichment**: 1 credit per company
- **Real-Time Enrichment** (`enrich_realtime=True`): 5 credits per company (4+1)
- **No Results, No Charges**: You are never charged credits when our APIs return no results. Credits are only deducted when data is successfully returned from your API requests.

## Example Requests

<details id="1-enrich-by-linkedin-profile-url">
<summary>1. Enrich by LinkedIn profile URL</summary>

### 1. Enrich by LinkedIn profile URL
```curl 
curl 'https://api.crustdata.com/screener/company?company_linkedin_url=https://www.linkedin.com/company/mintlify' \
--header 'Authorization: Token $authToken'
```
</details>

<details id="2-enrich-by-domain-with-fields-and-exact-match">
<summary>2. Enrich by Domain w/ Fields & Exact Match</summary>

### 2. Enrich by Domain w/ Fields & Exact Match
```curl
curl 'https://api.crustdata.com/screener/company?fields=headcount,founders.profiles,funding_and_investment&exact_match=true&company_domain=retool.com,mintlify.com' \
--header 'Authorization: Token $authToken'
```

Key features:
- `fields=headcount,founders.profiles,funding_and_investment` - Returns only specified fields
- `exact_match=true` - Matches domains exactly, not as substrings
</details>

<details id="3-enrich-by-domain-with-real-time-enrichment">
<summary>3. Enrich by Domain w/ Real-Time Enrichment</summary>

### 3. Enrich by Domain w/ Real-Time Enrichment
- Setting `enrich_realtime=true` retrieves data within 10 minutes for companies not in our database.

```curl
curl 'https://api.crustdata.com/screener/company?company_domain=browser-use.com&fields=headcount,founders.profiles,funding_and_investment&enrich_realtime=true' \
--header 'Authorization: Token $authToken'
```
</details>

<details id="4-enrich-with-gartner-data">
<summary>4. Enrich with Gartner Data</summary>

### 4. Enrich with Gartner Data
- Get Gartner data for a company by including `fields=gartner` in your request
- You can also request specific Gartner fields like `gartner.slug` or `gartner.products`

```curl
curl 'https://api.crustdata.com/screener/company?exact_match=true&company_domain=builder.io&fields=gartner' \
--header 'Authorization: Token $authToken'
```

Key features:
- `fields=gartner` - Returns all Gartner data
- `fields=gartner.slug,gartner.products` - Returns only specific Gartner fields
- Available fields: `gartner.slug`, `gartner.company_name`, `gartner.company_website_url`, `gartner.description`, `gartner.year_founded`, `gartner.head_office_city`, `gartner.head_office_country`, `gartner.num_employees_min`, `gartner.num_employees_max`, `gartner.products`, `gartner.reviews`

Response sample: [View example response](/examples/company-enrichment/company-enrichment-gartner-response.json)
</details>

<details id="5-enrich-with-producthunt-data">
<summary>5. Enrich with ProductHunt Data</summary>

### 5. Enrich with ProductHunt Data
- Get ProductHunt data for a company by including `fields=producthunt` in your request
- Includes company profile, ratings, reviews, launch history, and maker information

```curl
curl 'https://api.crustdata.com/screener/company?exact_match=true&company_domain=builder.io&fields=producthunt' \
--header 'Authorization: Token $authToken'
```

Key features:
- `fields=producthunt` - Returns all ProductHunt data
- Includes: company profile, product ratings, reviews, launch history, maker information, social media links, and categories

Response sample: [View example response](/examples/company-enrichment/company-enrichment-producthunt-response.json)
</details>

<details id="6-enrich-with-full-profile-data">
<summary>6. Enrich with Full Profile Data (All Fields)</summary>

### 6. Enrich with Full Profile Data (All Fields)
- Get complete company data including all available fields like founders profiles, CXOs, decision makers, and more
- This request returns all available data fields for comprehensive company intelligence

```curl
curl 'https://api.crustdata.com/screener/company?company_domain=ziphq.com&fields=headcount,founders.profiles,cxos,decision_makers,funding_and_investment,web_traffic,glassdoor,g2,linkedin_followers,job_openings,seo,news_articles,producthunt,gartner,competitors,taxonomy' \
--header 'Authorization: Token $authToken'
```

Key features:
- Returns all major data categories including people profiles
- `founders.profiles` - Detailed founder information with full LinkedIn profiles
- `cxos` - C-level executive profiles with complete background
- `decision_makers` - Key personnel with employment and education history
- Includes growth metrics, social data, and competitive intelligence

<details>
<summary>View example response with all fields</summary>

Response sample: [View full example response](/examples/company-enrichment/response_ziphq.json)

</details>
</details>

## Example Responses

<details id="1-response-and-enrichment-status">
<summary>Response</summary>

### Response

The response provides a comprehensive profile of the company, including firmographic details, social media links, headcount data, and growth metrics.

- Response sample with default fields : [View example response](/examples/company-enrichment/company-enrichment-response.json)
- Response sample with all the fields : [View example response](/examples/company-enrichment/response_ziphq.json)

### Response with Enrichment Status

When requesting data for a company not in our database, the enrichment process begins:

- Standard enrichment: Up to 24 hours
- Real time enrichment (`enrich_realtime=True`): Up to 10 minutes

The API response includes a status field with the following possible values:

- `enriching`: Company is being processed, poll later for full company info
  When a company is still being enriched, you might see a **202 Accepted** status code along with a response like this:

```json
[
  {
    "status": "enriching",
    "message": "The following companies will be enriched in the next 24 hours",
    "companies": [
      {
        "identifier": "https://www.linkedin.com/company/123456",
        "type": "linkedin_url"
      }
    ]
  }
]
```
- `not_found`: Enrichment failed (e.g., no website or employees found)

When a company cannot be found (e.g., it has no valid data or website), you may see a response like this:

```json
[
  {
    "status": "not_found",
    "message": "The requested company was not found and no data is available",
    "companies": [
      {
        "identifier": "https://www.linkedin.com/company/123456",
        "type": "linkedin_url"
      }
    ]
  }
]
```
</details>

---

## 📊 Data Dictionary

# Company Enrichment API Dictionary

This dictionary describes the data returned by the Company Enrichment API (`/screener/company` endpoint). It provides detailed information about companies across various categories including firmographics, headcount, traffic metrics, and more.

## Response Structure

The API returns an array of company objects, each containing comprehensive data organized in the following sections.

**⚠️ Note:** Fields marked with an asterisk (*) have upcoming data type changes.

## Basic Company Information

| Field                         | Type    | Description                                                        |
|-------------------------------|---------|-------------------------------------------------------------------|
| company_id                    | integer | Unique identifier for the company                                  |
| company_name                  | string  | Name of the company                                                |
| linkedin_profile_name          | string  | Name of the company on it's LinkedIn profile                              |
| linkedin_profile_url          | string  | URL to the company's LinkedIn profile                              |
| crunchbase_profile_url        | string  | URL to the company's Crunchbase profile                            |
| crunchbase_profile_uuid       | string  | Unique UUID from Crunchbase                                        |
| linkedin_id                   | string  | Unique LinkedIn identifier for the company                         |
| linkedin_logo_url             | string  | URL of the company's logo from LinkedIn                            |
| linkedin_logo_permalink       | string  | S3 link of company's logo with no expiry date
| company_twitter_url           | string  | URL to the company's Twitter profile                               |
| company_website_domain        | string  | Domain of the company's website                                    |
| company_website               | string  | Full URL of the company's website                                  |
| domains                       | array   | All known domains associated with the company                      |
| is_full_domain_match          | boolean | Boolean indicating if the domain perfectly matches the request     |

## Firmographics

| Field                             | Type     | Description                                                      |
|-----------------------------------|----------|------------------------------------------------------------------|
| hq_country                        | string   | Country where the company's headquarters is located              |
| headquarters                      | string   | Full address of the company headquarters                         |
| largest_headcount_country         | string   | Country with the highest employee count                          |
| hq_street_address                 | string   | Street address of company headquarters                           |
| year_founded                      | string   | Year the company was founded                                     |
| fiscal_year_end                   | string   | End of the company's fiscal year                                 |
| estimated_revenue_lower_bound_usd | integer  | Lower estimate of company's annual revenue in USD                |
| estimated_revenue_higher_bound_usd| integer  | Higher estimate of company's annual revenue in USD               |
| estimated_revenue_timeseries      | array    | Historic estimate revenue data over time                         |
| employee_count_range              | string   | Range indicating approximate number of employees (e.g. "201-500")|
| company_type                      | string   | Type of company (e.g. "Privately Held")                          |
| linkedin_company_description      | string   | Description from company's LinkedIn profile                      |
| acquisition_status                | string   | Status if the company has been acquired                          |
| ipo_date                          | string   | Date on which company went public                                |
| markets                           | array    | Markets in which the company operates (e.g., PRIVATE, NASDAQ)    |
| stock_symbols                     | array    | Stock ticker symbols for publicly traded companies               |
| ceo_location                      | string   | Location of the company's CEO                                    |
| all_office_addresses              | array    | List of all office locations/addresses for the company           |

## Taxonomy and Categories

| Field                               | Type   | Description                                                        |
|-------------------------------------|--------|-------------------------------------------------------------------|
| taxonomy.linkedin_specialities      | array  | List of specialties listed on LinkedIn                             |
| taxonomy.linkedin_industries        | array  | Industries in which the company operates according to LinkedIn     |
| taxonomy.crunchbase_categories      | array  | Categories assigned to the company on Crunchbase                   |
| taxonomy.primary_naics_detail       | object | Detailed information about the company's primary NAICS classification |
| taxonomy.primary_naics_detail.naics_code | string |  NAICS (North American Industry Classification System) code |
| taxonomy.primary_naics_detail.sector | string |  Broad sector classification under NAICS |
| taxonomy.primary_naics_detail.sub_sector | string |  Sub-sector classification under NAICS |
| taxonomy.primary_naics_detail.industry_group | string |  Industry group classification under NAICS |
| taxonomy.primary_naics_detail.industry | string |  Specific industry classification under NAICS |
| taxonomy.primary_naics_detail.year  | number |  Year of the NAICS classification |
| taxonomy.sic_detail_list            | array  | List of SIC (Standard Industrial Classification) codes and details |
| taxonomy.sic_detail_list[].sic_code | string | SIC code |
| taxonomy.sic_detail_list[].industry | string | Industry classification according to SIC |
| taxonomy.sic_detail_list[].year     | number | Year of the SIC classification |

## Competitors

| Field                                        | Type   | Description                                              |
|----------------------------------------------|--------|----------------------------------------------------------|
| competitors.competitor_website_domains       | array  | List of website domains of competing companies           |
| competitors.paid_seo_competitors_website_domains | array  | Domains competing for the same paid keywords         |
| competitors.organic_seo_competitors_website_domains | array  | Domains competing for the same organic keywords   |

## Headcount

| Field                                      | Type    | Description                                                |
|--------------------------------------------|---------|----------------------------------------------------------|
| headcount.linkedin_headcount               | integer | Total number of employees from LinkedIn                    |
| headcount.linkedin_headcount_total_growth_percent | object  | Growth percentages (mom, qoq, six_months, yoy)      |
| headcount.linkedin_headcount_total_growth_absolute | object  | Absolute growth figures (mom, qoq, six_months, yoy)|
| headcount.linkedin_headcount_by_role_absolute | object  | Employee counts broken down by role                     |
| headcount.linkedin_headcount_by_role_percent | object  | Percentage breakdown of employees by role                |
| headcount.linkedin_role_metrics            | object  | Categorization of roles by percentage ranges               |
| headcount.linkedin_headcount_by_role_six_months_growth_percent | object  | Six-month growth by role               |
| headcount.linkedin_headcount_by_role_yoy_growth_percent | object  | Year-over-year growth by role                 |
| headcount.linkedin_headcount_by_region_absolute | object  | Employee counts broken down by region                 |
| headcount.linkedin_headcount_by_region_percent | object  | Percentage breakdown of employees by region            |
| headcount.linkedin_region_metrics          | object  | Categorization of regions by percentage ranges             |
| headcount.linkedin_headcount_by_skill_absolute | object  | Employee counts broken down by skill                   |
| headcount.linkedin_headcount_by_skill_percent | object  | Percentage breakdown of employees by skill              |
| headcount.linkedin_skill_metrics           | object  | Categorization of skills by percentage ranges              |
| headcount.linkedin_headcount_timeseries    | array   | Historical headcount data over time                        |
| headcount.linkedin_headcount_by_function_timeseries | object  | Historical headcount by function over time        |

## Web Traffic

| Field                                        | Type     | Description                                                 |
|----------------------------------------------|----------|-------------------------------------------------------------|
| web_traffic.monthly_visitors*                 | ~~number~~ → integer  | Monthly visitors to the company website                     |
| web_traffic.monthly_visitor_mom_pct          | number   | Month-over-month percentage change in visitors              |
| web_traffic.monthly_visitor_qoq_pct          | number   | Quarter-over-quarter percentage change in visitors          |
| web_traffic.traffic_source_social_pct        | number   | Percentage of traffic from social media                     |
| web_traffic.traffic_source_search_pct        | number   | Percentage of traffic from search engines                   |
| web_traffic.traffic_source_direct_pct        | number   | Percentage of traffic from direct visits                    |
| web_traffic.traffic_source_paid_referral_pct | number   | Percentage of traffic from paid referrals                   |
| web_traffic.traffic_source_referral_pct      | number   | Percentage of traffic from organic referrals                |
| web_traffic.monthly_visitors_timeseries*      | array    | Historical data of monthly visitors (monthly_visitors field: ~~number~~ → integer)                         |

## Glassdoor

| Field                                      | Type     | Description                                               |
|--------------------------------------------|----------|-----------------------------------------------------------|
| glassdoor.glassdoor_overall_rating         | number   | Overall company rating on Glassdoor                       |
| glassdoor.glassdoor_ceo_approval_pct*       | ~~integer~~ → number   | Percentage of employees who approve of the CEO            |
| glassdoor.glassdoor_business_outlook_pct*   | ~~integer~~ → number   | Percentage with positive business outlook                 |
| glassdoor.glassdoor_review_count           | integer  | Number of reviews on Glassdoor                            |
| glassdoor.glassdoor_senior_management_rating | number   | Rating for senior management                            |
| glassdoor.glassdoor_compensation_rating    | number   | Rating for compensation and benefits                      |
| glassdoor.glassdoor_career_opportunities_rating | number   | Rating for career opportunities                      |
| glassdoor.glassdoor_culture_rating         | number   | Rating for company culture                                |
| glassdoor.glassdoor_diversity_rating       | number   | Rating for diversity                                      |
| glassdoor.glassdoor_work_life_balance_rating | number   | Rating for work-life balance                            |
| glassdoor.glassdoor_recommend_to_friend_pct* | ~~integer~~ → number   | Percentage who would recommend to a friend               |
| glassdoor.glassdoor_ceo_approval_growth_percent | object   | Growth percentages for CEO approval                  |
| glassdoor.glassdoor_review_count_growth_percent | object   | Growth percentages for review count                  |

## G2

| Field                      | Type     | Description                                               |
|----------------------------|----------|-----------------------------------------------------------|
| g2.g2_review_count         | integer  | Number of reviews on G2                                   |
| g2.g2_average_rating       | number   | Average rating on G2                                      |
| g2.g2_review_count_mom_pct | number   | Month-over-month percentage change in G2 reviews          |
| g2.g2_review_count_qoq_pct | number   | Quarter-over-quarter percentage change in G2 reviews      |
| g2.g2_review_count_yoy_pct | number   | Year-over-year percentage change in G2 reviews            |

## LinkedIn Followers

| Field                                                     | Type     | Description                                    |
|-----------------------------------------------------------|----------|------------------------------------------------|
| linkedin_followers.linkedin_followers                     | integer  | Total number of LinkedIn followers              |
| linkedin_followers.linkedin_follower_count_timeseries     | array    | Historical follower count data                  |
| linkedin_followers.linkedin_followers_mom_percent         | number   | Month-over-month percentage change in followers |
| linkedin_followers.linkedin_followers_qoq_percent         | number   | Quarter-over-quarter percentage change          |
| linkedin_followers.linkedin_followers_six_months_growth_percent | number   | Six-month growth percentage               |
| linkedin_followers.linkedin_followers_yoy_percent         | number   | Year-over-year percentage change in followers   |

## Funding and Investment

| Field                               | Type                     | Description                              | Schema                           |
| ----------------------------------- | ------------------------ | ---------------------------------------- | ------------------------------------- |
| funding_and_investment.crunchbase_total_investment_usd   | integer                  | Total investment amount in USD           | –                                     |
| funding_and_investment.days_since_last_fundraise         | integer                  | Days elapsed since latest round          | –                                     |
| funding_and_investment.last_funding_round_type           | string                   | Most recent funding-round type           | –                                     |
| funding_and_investment.crunchbase_investors_info_list    | array\<InvestorInfo>     | Detailed investors info                  | [InvestorInfo](#investorinfo)         |
| funding_and_investment.crunchbase_investors              | array                    | Flat list of investor names              | –                                     |
| funding_and_investment.last_funding_round_investment_usd | integer                  | Amount raised in latest round (USD)      | –                                     |
| funding_and_investment.funding_milestones_timeseries     | array\<FundingMilestone> | Historical funding milestones            | [FundingMilestone](#fundingmilestone) |
| funding_and_investment.acquisitions                      | array\<Acquisition>      | Companies **this** company acquired      | [Acquisition](#acquisition)           |
| funding_and_investment.acquired_by                       | array\<Acquisition>      | Companies that **acquired** this company | [Acquisition](#acquisition)           |

### Acquisition
| Field                     | Type           | Description                           |
| ------------------------- | -------------- | ------------------------------------- |
| acquirer_company_id     | integer        | Crustdata ID of the acquiring company |
| acquirer_company_name   | string         | Name of the acquirer                  |
| acquirer_crunchbase_url | string         | Acquirer’s Crunchbase URL             |
| acquiree_company_id     | integer        | Crustdata ID of the acquired company  |
| acquiree_company_name   | string         | Name of the acquiree                  |
| acquiree_crunchbase_url | string         | Acquiree’s Crunchbase URL             |
| announced_on_date       | string         | Announcement date                     |
| price_usd               | number         | Deal price (USD)                      |
| transaction_text        | string         | Free-text description                 |

### InvestorInfo
| Field        | Type   | Description                        |
| ------------ | ------ | ---------------------------------- |
| name       | string | Investor name                      |
| uuid       | string | Crunchbase UUID                    |
| type       | string | Investor type (eg: organization/person) |
| categories* | ~~string~~ → array | Array of investor categories (eg: accventure_capital,investment_bank,etc.)         |

### FundingMilestone

| Field                          | Type    | Description                              |
| ------------------------------ | ------- | ---------------------------------------- |
| funding_date                 | string  | Date of the funding round      |
| funding_milestone_amount_usd | integer | Amount raised (USD)                      |
| funding_round                | string  | Round type/name                          |
| funding_milestone_investors  | string  | Investor names in this round             |
| date                         | string  | Same date in alternate format  |

## Job Openings

| Field                                                        | Type     | Description                                        |
|--------------------------------------------------------------|----------|---------------------------------------------------|
| job_openings.recent_job_openings_title                       | string   | Title of recent job opening                        |
| job_openings.job_openings_count                              | integer  | Total count of current job openings                |
| job_openings.job_openings_count_growth_percent               | object   | Growth percentages for job openings                |
| job_openings.job_openings_by_function_qoq_pct                | object   | Quarter-over-quarter growth by function            |
| job_openings.job_openings_by_function_six_months_growth_pct  | object   | Six-month growth by function                       |
| job_openings.open_jobs_timeseries                            | array    | Historical job openings data                       |
| job_openings.recent_job_openings                             | array    | List of recent job openings with details           |

## SEO Metrics

| Field                                 | Type      | Description                                                   |
|---------------------------------------|-----------|---------------------------------------------------------------|
| seo.average_seo_organic_rank*          | ~~integer~~ → number    | Average rank in organic search results                        |
| seo.monthly_paid_clicks               | integer   | Monthly clicks from paid search                               |
| seo.monthly_organic_clicks            | integer   | Monthly clicks from organic search                            |
| seo.average_ad_rank*                   | ~~integer~~ → number    | Average position of ads                                       |
| seo.total_organic_results*             | ~~number~~ → integer    | Total number of keywords appearing in organic results         |
| seo.monthly_google_ads_budget         | number    | Estimated monthly Google Ads budget in USD                    |
| seo.monthly_organic_value*             | ~~integer~~ → number   | Estimated value of organic traffic in USD                     |
| seo.total_ads_purchased               | integer   | Total number of keywords advertised on                        |
| seo.lost_ranked_seo_keywords          | integer   | Number of keywords where ranking decreased                    |
| seo.gained_ranked_seo_keywords        | integer   | Number of keywords where ranking improved                     |
| seo.newly_ranked_seo_keywords         | integer   | Number of newly ranked keywords                               |

## Founders Information

| Field                                 | Type     | Description                                               |
|---------------------------------------|----------|-----------------------------------------------------------|
| founders.founders_locations           | array    | Locations of company founders                             |
| founders.founders_education_institute | string   | Educational institutions attended by founders             |
| founders.founders_degree_name         | string   | Degrees held by founders                                  |
| founders.founders_previous_companies  | array    | Previous companies where founders worked                  |
| founders.founders_previous_titles     | array    | Previous job titles held by founders                      |
| founders.profiles                     | array    | Detailed profiles of company founders                     |

### Founder Profile Details

Each object in `founders.profiles` contains:

| Field                                              | Type     | Description                                      |
|----------------------------------------------------|----------|--------------------------------------------------|
| founders.profiles[].linkedin_profile_url           | string   | LinkedIn profile URL (system format)             |
| founders.profiles[].linkedin_flagship_url          | string   | LinkedIn profile URL (human-readable format)     |
| founders.profiles[].name                           | string   | Full name of the founder                         |
| founders.profiles[].location                       | string   | Geographic location of the founder               |
| founders.profiles[].title                          | string   | Current job title                                |
| founders.profiles[].last_updated                   | string   | When the founder's data was last updated         |
| founders.profiles[].headline                       | string   | LinkedIn headline                                |
| founders.profiles[].summary                        | string   | Professional summary or bio                      |
| founders.profiles[].num_of_connections             | integer  | Number of LinkedIn connections                   |
| founders.profiles[].skills                         | array    | List of professional skills                      |
| founders.profiles[].profile_picture_url            | string   | URL to profile picture                           |
| founders.profiles[].twitter_handle                 | string   | Twitter username                                 |
| founders.profiles[].languages                      | array    | Languages spoken                                 |
| founders.profiles[].linkedin_open_to_cards         | object   | LinkedIn "open to" status information            |
| founders.profiles[].all_employers                  | array    | List of all companies the person has worked for |
| founders.profiles[].past_employers                 | array    | List of previous employers                       |
| founders.profiles[].all_employers_company_id       | array    | Company IDs corresponding to all employers       |
| founders.profiles[].all_titles                     | array    | List of all job titles held                      |
| founders.profiles[].all_schools                    | array    | List of educational institutions attended        |
| founders.profiles[].all_degrees                    | array    | List of degrees earned                           |
| founders.profiles[].current_employers              | array    | List of current employment details               |
| founders.profiles[].education_background           | array    | List of education entries                        |
| founders.profiles[].certifications                 | array    | Professional certifications                      |
| founders.profiles[].honors                         | array    | Awards and honors received                       |

## CXOs (C-Level Executives)

Information about C-level executives and senior leadership of the company.

| Field                               | Type     | Description                                                |
|-------------------------------------|----------|-----------------------------------------------------------|
| cxos                                | array    | Array of CXO-level executives at the company              |
| cxos[].linkedin_profile_url         | string   | LinkedIn profile URL (system format)                       |
| cxos[].linkedin_flagship_url        | string   | LinkedIn profile URL (human-readable format)               |
| cxos[].name                         | string   | Full name of the executive                                 |
| cxos[].location                     | string   | Geographic location of the executive                       |
| cxos[].title                        | string   | Current job title (e.g., CEO, CTO, CFO, etc.)            |
| cxos[].last_updated                 | string   | When the executive's data was last updated                 |
| cxos[].headline                     | string   | LinkedIn headline                                          |
| cxos[].summary                      | string   | Professional summary or bio                                |
| cxos[].num_of_connections           | integer  | Number of LinkedIn connections                             |
| cxos[].skills                       | array    | List of professional skills                                |
| cxos[].profile_picture_url          | string   | URL to profile picture                                     |
| cxos[].twitter_handle               | string   | Twitter username                                           |
| cxos[].languages                    | array    | Languages spoken                                           |
| cxos[].linkedin_open_to_cards       | object   | LinkedIn "open to" status information                      |
| cxos[].all_employers                | array    | List of all companies the person has worked for           |
| cxos[].past_employers               | array    | List of previous employers                                 |
| cxos[].all_employers_company_id     | array    | Company IDs corresponding to all employers                 |
| cxos[].all_titles                   | array    | List of all job titles held                                |
| cxos[].all_schools                  | array    | List of educational institutions attended                  |
| cxos[].all_degrees                  | array    | List of degrees earned                                     |
| cxos[].current_employers            | array    | List of current employment details                         |
| cxos[].education_background         | array    | List of education entries                                  |
| cxos[].certifications               | array    | Professional certifications                                |
| cxos[].honors                       | array    | Awards and honors received                                 |

## News Articles

| Field                        | Type     | Description                                         |
|------------------------------|----------|-----------------------------------------------------|
| news_articles                | array    | Array of recent news articles about the company     |
| news_articles[].article_url    | string   | URL of the news article                             |
| news_articles[].article_publisher_name | string   | Name of the publishing source                |
| news_articles[].article_title  | string   | Title of the news article                           |
| news_articles[].article_publish_date | string   | Publication date of the article               |

## Product Hunt

| Field                                | Type     | Description                                            |
|--------------------------------------|----------|--------------------------------------------------------|
| producthunt.slug                     | string   | Product Hunt slug/identifier                           |
| producthunt.company_name             | string   | Company name as listed on Product Hunt                 |
| producthunt.company_website_url      | string   | URL to the company's website                           |
| producthunt.angel_list_url           | string   | URL to the company's AngelList profile                 |
| producthunt.facebook_url             | string   | URL to the company's Facebook page                     |
| producthunt.instagram_url            | string   | URL to the company's Instagram profile                 |
| producthunt.github_url               | string   | URL to the company's GitHub profile                    |
| producthunt.twitter_url              | string   | URL to the company's Twitter profile                   |
| producthunt.threads_url              | string   | URL to the company's Threads profile                   |
| producthunt.linkedin_url             | string   | URL to the company's LinkedIn profile                  |
| producthunt.producthunt_url          | string   | URL to the company's Product Hunt page                 |
| producthunt.description              | string   | Description of the product                             |
| producthunt.rating                   | number   | Average rating on Product Hunt                         |
| producthunt.num_upvotes              | integer  | Total number of upvotes received                       |
| producthunt.num_reviews              | integer  | Total number of reviews received                       |
| producthunt.num_followers            | integer  | Total number of followers on Product Hunt              |
| producthunt.last_updated             | string   | Date and time when the data was last updated           |
| producthunt.categories               | array    | List of categories the product belongs to              |

### Product Hunt Makers

| Field                                | Type     | Description                                            |
|--------------------------------------|----------|--------------------------------------------------------|
| producthunt.makers                   | array    | Array of makers/creators of the product                |
| producthunt.makers[].username        | string   | Username of the maker on Product Hunt                  |
| producthunt.makers[].name            | string   | Full name of the maker                                 |
| producthunt.makers[].headline        | string   | Headline/short bio of the maker                        |
| producthunt.makers[].about           | string   | Detailed information about the maker                   |
| producthunt.makers[].num_badges      | integer  | Number of badges earned by the maker                   |
| producthunt.makers[].num_votes       | integer  | Number of votes received by the maker                  |
| producthunt.makers[].website_urls    | array    | List of website URLs associated with the maker         |
| producthunt.makers[].last_updated    | string   | When the maker's information was last updated          |

### Product Hunt Launches

| Field                                     | Type      | Description                                         |
|-------------------------------------------|-----------|-----------------------------------------------------|
| producthunt.launches                      | array     | Array of product launches on Product Hunt           |
| producthunt.launches[].launch_id          | string    | Unique identifier for the launch                    |
| producthunt.launches[].slug               | string    | URL-friendly name of the launch                     |
| producthunt.launches[].name               | string    | Name of the product launched                        |
| producthunt.launches[].tagline            | string    | Short description/tagline of the launch             |
| producthunt.launches[].description        | string    | Detailed description of the launch                  |
| producthunt.launches[].launched_at        | string    | Date and time when the product was launched         |
| producthunt.launches[].num_upvotes        | integer   | Number of upvotes received for the launch           |
| producthunt.launches[].num_comments       | integer   | Number of comments on the launch                    |
| producthunt.launches[].day_rank           | integer   | Ranking of the launch for the day                   |
| producthunt.launches[].week_rank          | integer   | Ranking of the launch for the week                  |
| producthunt.launches[].month_rank         | integer   | Ranking of the launch for the month                 |
| producthunt.launches[].year_rank          | integer   | Ranking of the launch for the year                  |
| producthunt.launches[].golden_kitty_award | boolean   | Whether the launch received a Golden Kitty Award    |
| producthunt.launches[].last_updated       | string    | When the launch information was last updated        |

## Decision Makers

Information about key decision makers and leadership team members of the company.

| Field                                | Type     | Description                                            |
|--------------------------------------|----------|--------------------------------------------------------|
| decision_makers                      | array    | Array of key decision makers at the company            |
| decision_makers[].linkedin_profile_url | string   | LinkedIn profile URL (system format)                |
| decision_makers[].linkedin_flagship_url | string   | LinkedIn profile URL (human-readable format)       |
| decision_makers[].name               | string   | Full name of the decision maker                        |
| decision_makers[].location           | string   | Geographic location of the decision maker              |
| decision_makers[].title              | string   | Current job title                                      |
| decision_makers[].last_updated       | string   | When the decision maker's data was last updated        |
| decision_makers[].headline           | string   | LinkedIn headline                                      |
| decision_makers[].summary            | string   | Professional summary or bio                            |
| decision_makers[].num_of_connections | integer  | Number of LinkedIn connections                         |
| decision_makers[].skills             | array    | List of professional skills                            |
| decision_makers[].profile_picture_url | string   | URL to profile picture                                |
| decision_makers[].twitter_handle     | string   | Twitter username                                       |
| decision_makers[].languages          | array    | Languages spoken                                       |
| decision_makers[].linkedin_open_to_cards | object   | LinkedIn "open to" status information              |
| decision_makers[].all_employers      | array    | List of all companies the person has worked for        |
| decision_makers[].past_employers     | array    | List of previous employers                             |
| decision_makers[].all_employers_company_id | array    | Company IDs corresponding to all employers       |
| decision_makers[].all_titles         | array    | List of all job titles held                            |
| decision_makers[].all_schools        | array    | List of educational institutions attended              |
| decision_makers[].all_degrees        | array    | List of degrees earned                                 |

### Current Employment Details

| Field                                                    | Type     | Description                                        |
|----------------------------------------------------------|----------|----------------------------------------------------|
| decision_makers[].current_employers                      | array    | List of current employers                          |
| decision_makers[].current_employers[].employer_name      | string   | Name of the employer                               |
| decision_makers[].current_employers[].employer_linkedin_id | string   | LinkedIn ID of the employer                      |
| decision_makers[].current_employers[].employer_logo_url  | string   | URL to employer's logo                             |
| decision_makers[].current_employers[].employer_linkedin_description | string   | Employer's LinkedIn description         |
| decision_makers[].current_employers[].employer_company_id | array    | Company IDs associated with the employer          |
| decision_makers[].current_employers[].employer_company_website_domain | array    | Website domains of the employer        |
| decision_makers[].current_employers[].employee_position_id | integer  | Unique ID for the position                       |
| decision_makers[].current_employers[].employee_title     | string   | Job title at the employer                          |
| decision_makers[].current_employers[].employee_description | string   | Job description                                  |
| decision_makers[].current_employers[].employee_location  | string   | Job location                                       |
| decision_makers[].current_employers[].start_date         | string   | Start date of employment                           |
| decision_makers[].current_employers[].end_date           | string   | End date of employment (null if current)           |

### Education Background

| Field                                                          | Type     | Description                                      |
|----------------------------------------------------------------|----------|--------------------------------------------------|
| decision_makers[].education_background                         | array    | List of education entries                         |
| decision_makers[].education_background[].degree_name           | string   | Name of degree earned                             |
| decision_makers[].education_background[].institute_name        | string   | Name of educational institution                   |
| decision_makers[].education_background[].institute_linkedin_id | string   | LinkedIn ID of the institution                    |
| decision_makers[].education_background[].institute_linkedin_url | string   | LinkedIn URL of the institution                   |
| decision_makers[].education_background[].institute_logo_url    | string   | URL to institution's logo                         |
| decision_makers[].education_background[].field_of_study        | string   | Major or specialization                           |
| decision_makers[].education_background[].activities_and_societies | string   | Extracurricular activities                     |
| decision_makers[].education_background[].start_date            | string   | Start date of education                           |
| decision_makers[].education_background[].end_date              | string   | End date of education                             |
| decision_makers[].certifications                               | array    | Professional certifications                       |
| decision_makers[].honors                                       | array    | Awards and honors received                        |

## Gartner

Information about the company from Gartner, including company details and product reviews.

| Field                      | Type     | Description                                               |
|----------------------------|----------|-----------------------------------------------------------|
| gartner.slug               | string   | Gartner identifier for the company                        |
| gartner.company_name       | string   | Company name as listed in Gartner                         |
| gartner.company_website_url| string   | Company website URL registered with Gartner               |
| gartner.description        | string   | Company description from Gartner                          |
| gartner.year_founded       | string   | Year the company was founded according to Gartner         |
| gartner.head_office_city   | string   | City where company headquarters is located                |
| gartner.head_office_country| string   | Country where company headquarters is located             |
| gartner.num_employees_min  | integer  | Minimum number of employees according to Gartner          |
| gartner.num_employees_max  | integer  | Maximum number of employees according to Gartner          |
| gartner.products           | array    | List of company products tracked by Gartner               |
| gartner.reviews            | array    | List of product reviews from Gartner                      |

---

## 🔧 OpenAPI Specification

# Company Enrichment API (realtime / in-db)

**Category:** Company API
**Base URL:** https://api.crustdata.com

**Endpoint:** `GET /screener/company`

**Description:** Retrieve detailed company data using one or more identifiers. **At least one** of `company_domain`, `company_name`, `company_linkedin_url`, or `company_id` must be supplied.

## Authentication
This endpoint requires a Bearer token in the `Authorization` header:

```
Authorization: Token <YOUR_TOKEN>
```
## Query Parameters
| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|

## Example Request

```bash
curl -X GET "https://api.crustdata.com/screener/company?company_domain=hubspot.com%2Cgithub.com&company_name=retool%2Cmintlify&company_linkedin_url=https%3A%2F%2Fwww.linkedin.com%2Fcompany%2Ftryretool%2Chttps%3A%2F%2Fwww.linkedin.com%2Fcompany%2Fmintlify" \
  -H "Authorization: Token &lt;YOUR_TOKEN&gt;"
```

## Rate Limiting
All Crustdata API requests count toward your per-minute quota. Inspect the response headers `X-RateLimit-Limit` and `X-RateLimit-Remaining` to monitor usage. Implement exponential back-off or retries when you receive a **429 Too Many Requests** response.

## Responses
### Status 200
**Description:** The response provides a comprehensive profile of the company, including firmographic details, social media links, headcount data, and growth metrics.
**Response Schema:**

### Status 400
**Description:** Bad request, please check your request body to fix this error.
**Response Schema:**
| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `error` | string | No |  |  |  |

## 📋 OpenAPI Components

## Query Parameters Components

```yaml
parameters:
  CompanyDomain:
    name: company_domain
    in: query
    description: "Comma-separated list (max 25) of company domains."
    required: false
    schema:
      type: string
      example: "hubspot.com,github.com"

  CompanyName:
    name: company_name
    in: query
    description: "Comma-separated list (max 25) of company names. If a name itself contains a comma, wrap it in double quotes.\n"
    required: false
    schema:
      type: string
      example: "retool,mintlify"

  CompanyLinkedInURL:
    name: company_linkedin_url
    in: query
    description: "Comma-separated list (max 25) of LinkedIn company profile URLs."
    required: false
    schema:
      type: string
      example: "https://www.linkedin.com/company/tryretool,https://www.linkedin.com/company/mintlify"

  CompanyID:
    name: company_id
    in: query
    description: "Comma-separated list (max 25) of Crustdata company IDs."
    required: false
    schema:
      type: string
      example: "12345,67890"

  Fields:
    name: fields
    in: query
    description: "Comma-separated list of fields to include in the response (supports dot-notation for nested fields).\n"
    required: false
    schema:
      type: string
      example: "company_name,company_domain,glassdoor.glassdoor_review_count"

  EnrichRealtime:
    name: enrich_realtime
    in: query
    description: "When **true** and a company isn’t in the DB,\nCrustdata enriches it within ~10 minutes. Default: **false**.\n"
    required: false
    schema:
      type: boolean
      default: false
      example: "true"

  ExactMatch:
    name: exact_match
    in: query
    description: "If **true**, identifiers must match exactly;\nif **false**, best-match logic applies. Default: **false**.\n"
    required: false
    schema:
      type: boolean
      default: false
      example: "true"

```

## Response Schema Components

```yaml
schemas:
  CompanyData:
    type: object
    properties:
      company_id:
        type: integer
        description: "Unique identifier for the company"
      company_name:
        type: string
        description: "Name of the company."
      linkedin_profile_url:
        type: string
        description: "URL of the company's LinkedIn profile."
      company_twitter_url:
        type: string
        description: "URL of the company's Twitter profile."
      company_website_domain:
        type: string
        description: "Domain name of the company's website."
      # ... (13 more properties)

  CompanyEnrichmentStatusEnriching:
    type: array
    description: "An array of objects describing companies currently under enrichment."
    items:
      type: object
      properties:
        status:
          type: string
          example: "enriching"
        message:
          type: string
          example: "The following companies will be enriched in the next 24 hours"
        companies:
          type: array

  CompanyEnrichmentStatusNotFound:
    type: array
    description: "An array of objects describing companies that could not be found even after enrichment."
    items:
      type: object
      properties:
        status:
          type: string
          example: "not_found"
        message:
          type: string
          example: "The requested company was not found and no data is available"
        companies:
          type: array

  Taxonomy:
    type: object
    title: Taxonomy
    description: "Classifies the company across various categories"
    properties:
      linkedin_specialities:
        type: array
        description: "Specialties listed on LinkedIn profile"
      linkedin_industries:
        type: array
        description: "Industries listed on LinkedIn profile"
      crunchbase_categories:
        type: array
        description: "Categories listed on Crunchbase"

  HeadCount:
    type: object
    title: Headcount
    description: "Information about the company employee count"
    properties:
      linkedin_headcount:
        type: integer
      linkedin_headcount_total_growth_percent:
        type: object
      linkedin_headcount_total_growth_absolute:
        type: object
      linkedin_headcount_by_role_percent:
        type: object
      linkedin_headcount_by_role_six_months_growth_percent:
        type: object
      # ... (7 more properties)

```

---

# Comprehensive API Documentation: company-identification-api

## 📋 Documentation Metadata

- **API Path:** `POST /screener/identify/`
- **Category:** Company API
- **Operation:** api
- **Documentation File:** company-identification-api.md
- **Data Dictionary:** company-identification.md
- **Main Documentation:** discover/company-apis/company-identification-api.md
- **Generated:** 2025-11-27T14:03:48.573Z

---

## 📖 Original Documentation

# Company Identification API

### [ 🚀 Try Now ](/api#tag/company-api/post/screener/identify/)

Given a company's name, website, LinkedIn profile, Crunchbase profile, or company ID, you can identify the company in Crustdata's database with company identification API.

## Endpoint

```
POST /screener/identify
```

## Data Dictionary

[Explore the data dictionary for this endpoint here](/docs/dictionary/company-identification)

## Request Parameters

| Payload Keys                    | Description                         | Required | Default |
| ---------------------------- | ----------------------------------- | -------- | ------- |
| `query_company_name`         | Name of the company                 | No       | -       |
| `query_company_website`      | Website of the company              | No       | -       |
| `query_company_linkedin_url` | LinkedIn profile URL of the company | No       | -       |
| `query_company_crunchbase_url` | Crunchbase profile URL of the company | No       | -       |
| `query_company_id`           | Company ID in Crustdata's database  | No       | -       |
| `exact_match`                | Whether to perform exact matching   | No       | false   |
| `count`                      | Maximum number of results (1-25)    | No       | 10      |
:::info
You can pass one of the five parameters to identify a company.

Note: 
- `query_company_crunchbase_url` :
This parameter accepts both versions of the Crunchbase URL, i.e., vanity url and UUID url. For example:
  1. `https://www.crunchbase.com/organization/retool`
  2. `https://crunchbase.com/organization/78d1acfa-b69f-1b14-2daf-c8af53089997`

- `query_company_linkedin_url` :
This parameter accepts both versions of the LinkedIn URL, i.e., vanity url and URL with LinkedIn ID. For example:
  1. `https://www.linkedin.com/company/tryretool`
  2. `https://www.linkedin.com/company/11869260`

:::
## Credit Usage

- No credits are consumed for this API endpoint

## Example Requests

<details id="1-identify-by-website-domain">
<summary>1. Identify a company by website domain</summary>

### 1. Identify a company by website domain
```bash
curl 'https://api.crustdata.com/screener/identify/' \
--header 'Accept: application/json, text/plain, */*' \
--header 'Authorization: Token $api_token' \
--header 'Content-Type: application/json' \
--data '{"query_company_website": "serverobotics.com", "count": 1}'
```
</details>

<details id="2-identify-by-linkedin-url">
<summary>2. Identify a company by LinkedIn URL</summary>

### 2. Identify a company by LinkedIn URL
```bash
curl 'https://api.crustdata.com/screener/identify/' \
--header 'Accept: application/json, text/plain, */*' \
--header 'Authorization: Token $api_token' \
--header 'Content-Type: application/json' \
--data '{"query_company_linkedin_url": "https://www.linkedin.com/company/serve-robotics", "count": 1}'
```
</details>

<details id="3-identify-by-crunchbase-url">
<summary>3. Identify a company by Crunchbase URL</summary>

### 3. Identify a company by Crunchbase URL
```bash
curl 'https://api.crustdata.com/screener/identify/' \
--header 'Accept: application/json, text/plain, */*' \
--header 'Authorization: Token $api_token' \
--header 'Content-Type: application/json' \
--data '{"query_company_crunchbase_url": "https://www.crunchbase.com/organization/crustdata", "count": 1}'
```
</details>

<details id="4-identify-by-company-name">
<summary>4. Identify a company by name</summary>

### 4. Identify a company by name
```bash
curl 'https://api.crustdata.com/screener/identify/' \
--header 'Accept: application/json, text/plain, */*' \
--header 'Authorization: Token $api_token' \
--header 'Content-Type: application/json' \
--data '{"query_company_name": "Serve Robotics", "count": 1}'
```
</details>

<details id="5-identify-by-company-id">
<summary>5. Identify a company by company ID</summary>

### 5. Identify a company by company ID
```bash
curl 'https://api.crustdata.com/screener/identify/' \
--header 'Accept: application/json, text/plain, */*' \
--header 'Authorization: Token $api_token' \
--header 'Content-Type: application/json' \
--data '{"query_company_id": "5702", "count": 1}'
```
</details>

## Example Responses

<details id="1-response">
<summary>Response</summary>

### Response
The API returns an array of matching companies, ranked by matching score. 

```json
[
    {
        "company_id": 681759,
        "company_name": "Salesforce",
        "linkedin_profile_name": "Salesforce",
        "company_slug": "salesforce",
        "score": 1.5961714285714286,
        "is_full_domain_match": true,
        "total_rows": 1,
        "company_website_domain": "salesforce.com",
        "company_website": "http://www.salesforce.com",
        "domains": ["salesforce.com", "force.com"],
        "linkedin_profile_url": "https://www.linkedin.com/company/salesforce",
        "linkedin_profile_id": "3185",
        "linkedin_headcount": 87249,
        "employee_count_range": "10001+",
        "estimated_revenue_lower_bound_usd": 1000000000,
        "estimated_revenue_upper_bound_usd": 1000000000000,
        "hq_country": "USA",
        "headquarters": "San Francisco, California, United States",
        "linkedin_industries": [
            "Computer Software",
            "Internet",
            "Software Development"
        ],
        "acquisition_status": "acquired",
        "linkedin_logo_url": "https://media.licdn.com/dms/image/v2/C560BAQHZ9xYomLW7zg/company-logo_200_200/company-logo_200_200/0/1630658255326/salesforce_logo?e=1754524800&v=beta&t=Ed5Djqrnss_y6ki9zphXUp2RehvZX4zdkZh80-EVGb4",
        "crunchbase_profile_url": "https://crunchbase.com/organization/radian6",
        "crunchbase_total_investment_usd": 9000000,
        "last_job_listings_parser_run": "2025-06-14T11:29:30.397131Z"
    }
]
```
</details>

---

## 📊 Data Dictionary

# Company Identification Dictionary

This dictionary describes the data returned by the Company Identification API (`/screener/identify` endpoint). It provides information about companies identified from a name, website, LinkedIn profile, or Crunchbase profile.

## Response Structure

The API returns an array of company objects that match the search criteria, ranked by matching score. Each company object contains the following fields:

| Field                           | Type      | Description                                                     |
|---------------------------------|-----------|-----------------------------------------------------------------|
| company_id                      | integer   | Unique identifier for the company in Crustdata's database       |
| company_name                    | string    | Name of the company                                             |
| company_slug                    | string    | URL-friendly version of the company name                        |
| company_website_domain          | string    | Domain of the company's website                                 |
| company_website                 | string    | Full URL of the company's website                               |
| domains                         | array     | All known domains associated with the company                   |
| linkedin_profile_url            | string    | URL to the company's LinkedIn profile                           |
| linkedin_headcount              | integer   | Number of employees listed on LinkedIn                          |
| acquisition_status              | string    | Status if the company has been acquired (null if not acquired)  |
| linkedin_logo_url               | string    | URL to the company's logo from LinkedIn                         |
| crunchbase_profile_url          | string    | URL to the company's Crunchbase profile                         |
| crunchbase_total_investment_usd | integer   | Total investment amount in USD from Crunchbase                  |
| score                           | float     | Matching score (0-1) indicating confidence in the identification|
| is_full_domain_match            | boolean   | Whether the domain exactly matches the query                    |
| total_rows                      | integer   | Total number of matching rows in the result set                 |
| last_job_listings_parser_run    | string    | ISO timestamp of the last time job listings were parsed         | 

---

## 🔧 OpenAPI Specification

# Identification API (in-db)

**Category:** Company API
**Base URL:** https://api.crustdata.com
**Official Docs:** /docs/discover/company-apis/company-identification-api

**Endpoint:** `POST /screener/identify/`

**Description:** Identifies one or more companies in Crustdata's database based on the provided query parameters (e.g., domain, name). The API returns an array of matching companies, each with a matching score, sorted by relevance.
> [Show Docs](/docs/discover/company-apis/company-identification-api)

## Authentication
This endpoint requires a Bearer token in the `Authorization` header:

```
Authorization: Token <YOUR_TOKEN>
```
## Request Body Schema

| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `query_company_name` | string | No | Name of the company. |  | HubSpot |
| `query_company_website` | string | No | Company website domain. |  | hubspot.com |
| `query_company_linkedin_url` | string | No | LinkedIn profile URL of the company. |  | https://www.linkedin.com/company/hubspot/ |
| `query_company_crunchbase_url` | string | No | Crunchbase profile URL of the company. |  | https://www.crunchbase.com/organization/hubspot |
| `query_company_id` | string | No | Company ID in Crustdata's database. |  | 5702 |
| `count` | integer | No | Maximum number of results to return. |  | 1 |

## Example Request

```bash
curl -X POST "https://api.crustdata.com/screener/identify/" \
  -H "Authorization: Token &lt;YOUR_TOKEN&gt;" \
  -H "Content-Type: application/json" \
  -d '{
    "query_company_name": "HubSpot",
    "query_company_website": "hubspot.com",
    "query_company_linkedin_url": "https://www.linkedin.com/company/hubspot/",
    "query_company_crunchbase_url": "https://www.crunchbase.com/organization/hubspot",
    "query_company_id": "5702",
    "count": 1
  }'
```

## Rate Limiting
All Crustdata API requests count toward your per-minute quota. Inspect the response headers `X-RateLimit-Limit` and `X-RateLimit-Remaining` to monitor usage. Implement exponential back-off or retries when you receive a **429 Too Many Requests** response.

## Responses
### Status 200
**Description:** Success response returning an array of matching companies
**Response Schema:**
Array of:
| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `company_id` | integer | Yes |  |  |  |
| `company_name` | string | Yes |  |  |  |
| `company_slug` | string | No |  |  |  |
| `company_website_domain` | string | No |  |  |  |
| `company_website` | string | No |  |  |  |
| `linkedin_profile_url` | string | No |  |  |  |
| `linkedin_headcount` | integer | No |  |  |  |
| `acquisition_status` | string | No |  |  |  |
| `linkedin_logo_url` | string | No |  |  |  |
| `score` | number | No |  |  |  |
| `is_full_domain_match` | boolean | No |  |  |  |
| `total_rows` | integer | No |  |  |  |
| `last_job_listings_parser_run` | string | No |  |  |  |

### Status 400
**Description:** Bad request. Please check your request body.
**Response Schema:**
| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `error` | string | No |  |  | Bad Request: Missing required field |

### Status 404
**Description:** Company not found in Crustdata's database.

**Response Schema:**
| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `error` | string | No |  |  | Not found |
| `enriched_company_ids` | string | No |  |  |  |
| `last_tried_company_enrichment_date` | string | No |  |  |  |
| `did_last_company_enrichment_succeed` | string | No |  |  |  |

## 📋 OpenAPI Components

## Response Schema Components

```yaml
schemas:
  BasicError:
    type: object
    properties:
      error:
        type: string
        example: "Bad Request: Missing required field"

  IdentifyNotFound:
    type: object
    properties:
      error:
        type: string
        example: "Not found"
      enriched_company_ids:
        type: string
        example: null
      last_tried_company_enrichment_date:
        type: string
        example: null
      did_last_company_enrichment_succeed:
        type: string
        example: null

  IdentifyRequest:
    type: object
    description: "Request body for the Company Identification API.\nYou only need to supply one of the five identifier fields\n(`query_company_name`, `query_company_website`,\n `query_company_linkedin_url`, `query_company_crunchbase_url`, `query_company_id`).\n"
    properties:
      query_company_name:
        type: string
        description: "Name of the company."
        example: "HubSpot"
      query_company_website:
        type: string
        description: "Company website domain."
        example: "hubspot.com"
      query_company_linkedin_url:
        type: string
        description: "LinkedIn profile URL of the company."
        example: "https://www.linkedin.com/company/hubspot/"
      query_company_crunchbase_url:
        type: string
        description: "Crunchbase profile URL of the company."
        example: "https://www.crunchbase.com/organization/hubspot"
      query_company_id:
        type: string
        description: "Company ID in Crustdata's database."
        example: "5702"
      # ... (1 more properties)

  IdentifyResult:
    type: object
    properties:
      company_id:
        type: integer
      company_name:
        type: string
      company_slug:
        type: string
      company_website_domain:
        type: string
      company_website:
        type: string
      # ... (8 more properties)

```

---

# Comprehensive API Documentation: company-linkedin-post-by-keyword

## 📋 Documentation Metadata

- **API Path:** `POST /screener/linkedin_posts/keyword_search/`
- **Category:** Company API
- **Operation:** keyword
- **Documentation File:** company-linkedin-post-by-keyword.md
- **Main Documentation:** discover/company-apis/company-linkedin-post-by-keyword.md
- **Generated:** 2025-11-27T14:03:48.603Z

---

## 📖 Original Documentation

# Realtime: LinkedIn Posts Keyword Search

### [ 🚀 Try Now ](/api#tag/company-api/post/screener/linkedin_posts/keyword_search/)

This endpoint retrieves LinkedIn posts containing specified keywords along with related engagement metrics.

## Endpoint

```
POST /screener/linkedin_posts/keyword_search/
```

## Data Dictionary

[Explore the data dictionary for this endpoint here](/docs/dictionary/linkedin-posts-keyword-search)

## Request Parameters
| **Field** | **Type** | **Default** | **Description** |
|-----------|----------|-------------|----------------|
| **keyword** | string | - | The keyword or phrase to search for in LinkedIn posts. Supports Boolean filtering using "OR" and "AND" operators with a maximum of 6 keywords (e.g., "AI OR Documentation OR ai-safety"). |
| **page** | integer | 1* | Page number for pagination. Max allowed value 100. |
| **limit** | integer | 5* |  Exact number of posts to return. Max allowed value 500.  |
| **sort_by** | string | `relevance` | <br/> Defines how the results should be sorted. Possible values:<br/>• **"relevance"** — Sort by top match<br/>• **"date_posted"** (Deprecated) — Sort by latest posts |
| **date_posted** | string | `past-month` | Filters posts by the date they were posted. Possible values:<br/>• **"past-24h"** — Posts from last 24 hours<br/>• **"past-week"** — Posts from last 7 days<br/>• **"past-month"** — Posts from last 30 days<br/>• **"past-quarter"** — Posts from last 3 months<br/>• **"past-year"** — Posts from last 1 year |
| **exact_keyword_match** | boolean | False | When `True`, returns posts that contain exact keyword in the post content. **Important:** When using `exact_keyword_match=true`, you must use the `limit` parameter instead of `page`. The API will scan the first *n* posts (where *n* = `limit`) and return only those containing the exact keyword match. |
| **content_type** | array | - | Filter posts by content type. Allowed values:<br/>• **"photos"** — Posts with photos<br/>• **"videos"** — Posts with videos<br/>• **"documents"** — Posts with documents<br/>• **"jobs"** — Job postings<br/>• **"collaborativeArticles"** — Collaborative articles<br/>• **"liveVideos"** — Live video posts |
| **filters** | array | - | List of filter to narrow down the results. These filters are combined with **AND** logic, so a post must satisfy all of them. <br/> Refer to [How to Build LinkedIn Post Filters for more details](/docs/discover/company-apis/how-to-build-linkedin-post-by-keyword-filters) |
| **fields** | string | - | Comma-separated list of fields to include in the response. By default, returns core post data. Add "reactors" to fetch users who reacted, and "comments" to fetch comments. Example: `"reactors,comments"` |
| **max_reactors** | integer | 5 | Maximum number of reactors to fetch per post when "reactors" is included in fields. Range: 0-5000. |
| **max_comments** | integer | 5 | Maximum number of comments to fetch per post when "comments" is included in fields. Range: 0-5000. |

*\* At least one of `page` or `limit` must be provided

#### Key Points  
  - **Pagination:**
    - Increment the value of `page` query param (starts from 1) to fetch the next set of posts. Each page has 5 posts.
    - `limit` can not exceed 5 when `page` is provided in the payload. To retrieve posts in bulk, use the `limit` parameter (with value over 5 allowed here) without the `page` parameter.
    - **Important:** When `exact_keyword_match` is set to `true`, pagination with `page` is not supported. You must use `limit` to specify how many posts to scan.
  - **Exact Keyword Match Behavior:**
    - When `exact_keyword_match=true`, the API continues post-processing fetched posts until the requested `limit` is reached.  
    - If all available posts are processed and the total still falls short, the API will return only the number of matched posts found (which may be fewer than the requested limit).
    - If no posts match the exact keyword, the API returns a 404 error with details about the total posts fetched and processed.  

  - **Latency:** The data is fetched in real-time from Linkedin and the latency for this endpoint is between 5 to 10 seconds depending on number of posts fetched in a request.

## Credit Usage
  - **Default requests**: 1 credit per post returned
  - **Requests with `fields="reactors"`**: 5 credits per post returned
  - **Requests with `fields="comments"`**: 5 credits per post returned  
  - **Requests with `fields="reactors,comments"`**: 10 credits per post returned
  - **Requests with `exact_keyword_match=true`**: 3 credits per post returned
  - **No Results, No Charges**: You are never charged credits when our APIs return no results. Credits are only deducted when data is successfully returned from your API requests.

## Example Requests

<details id="1-posts-with-llm-evaluation-keyword">
<summary>1. Posts with `LLM evaluation` keyword</summary>

### 1. Posts with `LLM evaluation` keyword
```bash
curl -X POST 'https://api.crustdata.com/screener/linkedin_posts/keyword_search/' \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/plain, */*" \
-H "Authorization: Token $auth_token" \
--data-raw '{
  "keyword": "LLM Evaluation",
  "page": 1,
  "date_posted": "past-quarter"
}'
```
</details>

<details id="2-posts-with-series-a-keyword-and-mentioning-an-investor">
<summary>2. Posts with `Series A` keyword and mentioning an investor</summary>

### 2. Posts with `Series A` keyword and mentioning an investor
```bash
curl -X POST 'https://api.crustdata.com/screener/linkedin_posts/keyword_search/' \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/plain, */*" \
-H "Authorization: Token $auth_token" \
--data-raw '{
  "keyword": "Series A",
  "page": 1,
  "filters": [
    {
      "filter_type": "AUTHOR_INDUSTRY",
      "type": "in",
      "value": [
        "Software Development"
      ]
    },
    {
      "filter_type": "MENTIONING_COMPANY",
      "type": "in",
      "value": [
        "https://www.linkedin.com/company/sequoia"
      ]
    },
    {
      "filter_type": "AUTHOR_TITLE",
      "type": "in",
      "value": [
        "Co-Founder"
      ]
    }
  ]
}'
```
</details>

<details id="3-exact-match-on-keyword">
<summary>3. Exact match on keyword</summary>

### 3. Posts with exact match on keyword
Pull LinkedIn posts that exactly match your keyword phrase (no partial matches). 

```bash
curl -X POST 'https://api.crustdata.com/screener/linkedin_posts/keyword_search/' \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/plain, */*" \
-H "Authorization: Token $auth_token" \
--data-raw '{
  "keyword": "Starting a new position",
  "limit": 100,
  "exact_keyword_match": true,
  "filters": [
    {
      "filter_type": "AUTHOR_INDUSTRY",
      "type": "in",
      "value": [
        "Software Development",
        "Technology, Information and Internet"
      ]
    },
    {
      "filter_type": "MENTIONING_COMPANY",
      "type": "in",
      "value": [
        "https://www.linkedin.com/company/googledeepmind/",
        "https://www.linkedin.com/company/openai/"
      ]
    }
  ]
}'
```
</details>

<details id="4-posts-by-specific-linkedin-members">
<summary>4. Posts by specific LinkedIn members in last 24 hours</summary>

### 4. Posts by specific LinkedIn members in last 24 hours
```bash
curl -X POST 'https://api.crustdata.com/screener/linkedin_posts/keyword_search/' \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/plain, */*" \
-H "Authorization: Token $auth_token" \
--data-raw '{
  "keyword": "tech",
  "page": 1,
  "date_posted": "past-24h",
  "filters": [
    {
      "filter_type": "MEMBER",
      "type": "in",
      "value": [
        "https://www.linkedin.com/in/satyanadella",
        "https://www.linkedin.com/in/danielahmadizadeh/"
      ]
    }
  ]
}'
```

:::note
The `keyword` field is required by the API. When searching by specific members, you can use a high-frequency character like "a" as a placeholder since the actual filtering will be done by the member filter.
:::
</details>

<details id="5-posts-with-specific-content-types">
<summary>5. Posts with specific content types</summary>

### 5. Posts with specific content types
Filter posts by content type - useful for finding video announcements, job postings, or posts with photos.

```bash
curl -X POST 'https://api.crustdata.com/screener/linkedin_posts/keyword_search/' \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/plain, */*" \
-H "Authorization: Token $auth_token" \
--data-raw '{
  "keyword": "product launch",
  "page": 1,
  "date_posted": "past-week",
  "content_type": ["videos", "photos"],
  "filters": [
    {
      "filter_type": "AUTHOR_INDUSTRY",
      "type": "in",
      "value": [
        "Software Development"
      ]
    }
  ]
}'
```

This example searches for "product launch" posts from the past week that contain either videos or photos from companies in the Software Development industry.
</details>

<details id="6-posts-with-reactors-and-comments">
<summary>6. Posts with reactors and comments</summary>

### 6. Posts with reactors and comments
Fetch posts along with users who reacted and comments by using the `fields` parameter.

```bash
curl -X POST 'https://api.crustdata.com/screener/linkedin_posts/keyword_search/' \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/plain, */*" \
-H "Authorization: Token $auth_token" \
--data-raw '{
  "keyword": "AI innovation",
  "page": 1,
  "date_posted": "past-week",
  "fields": "reactors,comments",
  "max_reactors": 100,
  "max_comments": 50,
  "filters": [
    {
      "filter_type": "AUTHOR_INDUSTRY",
      "type": "in",
      "value": [
        "Software Development",
        "Technology, Information and Internet"
      ]
    }
  ]
}'
```

This example searches for "AI innovation" posts from the past week and fetches up to 100 reactors and 50 comments per post. The response will include additional `reactors` and `comments` arrays for each post with detailed information about users who reacted and their comments.
</details>

<details id="7-boolean-filtering-with-keywords">
<summary>7. Boolean filtering with keywords</summary>

### 7. Boolean filtering with keywords
Use Boolean operators "OR" and "AND" to create more flexible keyword searches.

```bash
curl -X POST 'https://api.crustdata.com/screener/linkedin_posts/keyword_search/' \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/plain, */*" \
-H "Authorization: Token $auth_token" \
--data-raw '{
  "keyword": "fundraise OR raised",
  "page": 1,
  "date_posted": "past-week",
  "filters": [
    {
      "filter_type": "AUTHOR_INDUSTRY",
      "type": "in",
      "value": [
        "Software Development",
        "Technology, Information and Internet"
      ]
    }
  ]
}'
```

</details>

<details id="4-posts-with-reactors-and-comments">
<summary>4. Posts with keyword including reactors and comments</summary>

### 4. Posts with keyword including reactors and comments
```bash
curl -X POST 'https://api.crustdata.com/screener/linkedin_posts/keyword_search/' \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/plain, */*" \
-H "Authorization: Token $auth_token" \
--data-raw '{
  "keyword": "AI breakthrough",
  "page": 1,
  "fields": "reactors,comments",
  "date_posted": "past-month"
}'
```

</details>

## Example Responses

<details id="1-response">
<summary>Response</summary>

### Response
The response provides a list of recent LinkedIn posts for the specified company, including post content, engagement metrics, and information about users who interacted with the posts.
Refer to `actor_type` field to identify if the post is published by a person or a company.

Response sample: [View example response](/examples/linkedin-posts/keyword-search-response.json)
</details>

<details id="2-error-response">
<summary>Error Response (404 - No Exact Matches Found)</summary>

### 404 Error Response
When `exact_keyword_match=true` and no posts are found matching the keyword exactly, the API returns a 404 status with the following response format:

```json
{
  "total_fetched_posts": 150,
  "error": "No matching posts found. With 'exact_keyword_match', the API post-processed 150 posts but found no exact keyword matches."
}
```

Where `total_fetched_posts` indicates the number of posts that were fetched and processed before determining no exact matches were found.
</details>

---

## 🔧 OpenAPI Specification

# LinkedIn Posts by Keyword API (real-time)

**Category:** Company API
**Base URL:** https://api.crustdata.com
**Official Docs:** /docs/discover/company-apis/company-linkedin-post-by-keyword

**Endpoint:** `POST /screener/linkedin_posts/keyword_search/`

**Description:** Search for LinkedIn posts containing specific keywords or phrases. Results can be sorted by relevance 
or recency and filtered by date posted.
> [Show Docs](/docs/discover/company-apis/company-linkedin-post-by-keyword)

## Authentication
This endpoint requires a Bearer token in the `Authorization` header:

```
Authorization: Token <YOUR_TOKEN>
```
## Request Body Schema

| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `keyword` | string | Yes | The keyword or phrase to search for in LinkedIn posts |  | LLM Evaluation |
| `page` | integer | No | Page number for pagination (starts from 1). Cannot be used when exact_keyword_match is true. |  | 1 |
| `limit` | integer | No | Exact number of posts to return or scan. Required when exact_keyword_match is true. |  | 100 |
| `exact_keyword_match` | boolean | No | When true, returns posts that contain the exact keyword phrase. Must use 'limit' parameter instead of 'page' when enabled. The API will scan the first 'limit' posts and return only those containing exact matches. |  | true |
| `sort_by` | string | No | How to sort the results | relevance, date_posted | relevance |
| `date_posted` | string | No | Filter posts by when they were posted | past-24h, past-week, past-month, past-quarter, past-year | past-24h |
| `content_type` | array | No | Filter posts by content type |  | videos,photos |
| `filters` | array | No | Optional filters for posts by specific criteria |  |  |
| `fields` | string | No | Comma-separated list of fields to include in the response. By default, returns core post data. Add "reactors" to fetch users who reacted, and "comments" to fetch comments. |  | reactors,comments |
| `max_reactors` | integer | No | Maximum number of reactors to fetch per post when "reactors" is included in fields. Range 0-5000. |  | 100 |
| `max_comments` | integer | No | Maximum number of comments to fetch per post when "comments" is included in fields. Range 0-5000. |  | 50 |

## Example Request

```bash
curl -X POST "https://api.crustdata.com/screener/linkedin_posts/keyword_search/" \
  -H "Authorization: Token &lt;YOUR_TOKEN&gt;" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "LLM Evaluation",
    "page": 1,
    "limit": 100,
    "exact_keyword_match": true,
    "sort_by": "relevance",
    "date_posted": "past-24h",
    "content_type": ["videos","photos"],
    "filters": [{"filter_type":"AUTHOR_TITLE","type":"in","value":["Co-Founder"]}],
    "fields": "reactors,comments",
    "max_reactors": 100,
    "max_comments": 50
  }'
```

## Rate Limiting
All Crustdata API requests count toward your per-minute quota. Inspect the response headers `X-RateLimit-Limit` and `X-RateLimit-Remaining` to monitor usage. Implement exponential back-off or retries when you receive a **429 Too Many Requests** response.

## Responses
### Status 200
**Description:** A list of LinkedIn posts matching the search criteria
**Response Schema:**
| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `posts` | array | No |  |  |  |
| `total_count` | integer | No | Total number of posts matching the search criteria |  |  |

### Status 400
**Description:** Bad request. Check your request body.
**Response Schema:**
| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `error` | string | No |  |  |  |

### Status 404
**Description:** No matching posts found
**Response Schema:**
| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `error` | string | No |  |  |  |

## 📋 OpenAPI Components

## Response Schema Components

```yaml
schemas:
  PostWithKeywords:
    type: object
    properties:
      backend_urn:
        type: string
        description: "Unique identifier for the post in LinkedIn's backend system"
      uid:
        type: string
        description: "Unique identifier for the post in the system"
      share_urn:
        type: string
        description: "Unique identifier for the shared content"
      share_url:
        type: string
        description: "Direct URL to the post on LinkedIn"
      text:
        type: string
        description: "The full content of the post"
      # ... (16 more properties)

  Reactor:
    type: object
    properties:
      name:
        type: string
        description: "Full name of the person who reacted"
      linkedin_profile_url:
        type: string
        description: "URL to the reactor's LinkedIn profile"
      reaction_type:
        type: string
        description: "Type of reaction given (e.g., \"LIKE\", \"EMPATHY\")"
      profile_image_url:
        type: string
        description: "URL to the reactor's profile image (100x100 size)"
      title:
        type: string
        description: "Current professional title of the reactor"
      # ... (23 more properties)

  Employment:
    type: object
    properties:
      title:
        type: string
        description: "Job title"
      company_name:
        type: string
        description: "Name of the employer"
      company_linkedin_id:
        type: string
        description: "LinkedIn ID of the company"
      company_logo_url:
        type: string
        description: "URL to the company logo image"
      start_date:
        type: string
        description: "Start date of employment"
      # ... (5 more properties)

  Education:
    type: object
    properties:
      degree_name:
        type: string
        description: "Type of degree obtained"
      institute_name:
        type: string
        description: "Name of the educational institution"
      field_of_study:
        type: string
        description: "Area of study"
      start_date:
        type: string
        description: "Start date of education"
      end_date:
        type: string
        description: "End date of education"
      # ... (3 more properties)

  Post:
    type: object
    properties:
      backend_urn:
        type: string
        description: "Unique identifier for the post in LinkedIn's backend system"
      actor_backend_urn:
        type: string
        description: "Unique identifier for the actor's post in LinkedIn's backend system"
      share_urn:
        type: string
        description: "Unique identifier for the shared content"
      share_url:
        type: string
        description: "Direct URL to the post on LinkedIn"
      text:
        type: string
        description: "The full content of the post"
      # ... (9 more properties)

```

---

# Comprehensive API Documentation: company-linkedin-post

## 📋 Documentation Metadata

- **API Path:** `GET /screener/linkedin_posts`
- **Category:** People API
- **Operation:** post
- **Documentation File:** company-linkedin-post.md
- **Main Documentation:** discover/company-apis/company-linkedin-post.md
- **Generated:** 2025-11-27T14:03:48.600Z

---

## 📖 Original Documentation

# Realtime: LinkedIn Posts by Company API

### [ 🚀 Try Now ](/api#tag/company-api/get/screener/linkedin_posts)

This endpoint retrieves recent LinkedIn posts and related engagement metrics for a specified company.

**Use Case:** Ideal for users who want to fetch recent LinkedIn posts and engagement data for a specific company.

## Endpoint

```
GET /screener/linkedin_posts/
```

## Data Dictionary

[Explore the data dictionary for this endpoint here](/docs/dictionary/linkedin-posts-company)

## Request Parameters

  | **Payload Keys**          | **Type** | **Required?** | **Default**           | **Description**                                                                      | **Possible Values**                                                              |
  | ---------------------- | -------- | ------------- | --------------------- | ------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------- |
  | `company_name`         | string   | optional      | _(none)_              | Company name. Provide only one of the company identifiers.                           | _(any valid company name)_                                                       |
  | `company_domain`       | string   | optional      | _(none)_              | Company domain. Provide only one of the company identifiers.                         | _(any valid domain)_                                                             |
  | `company_id`           | string   | optional      | _(none)_              | Company ID. Provide only one of the company identifiers.                             | _(any valid company ID)_                                                         |
  | `company_linkedin_url` | string   | optional      | _(none)_              | Company LinkedIn URL. Provide only one of the company identifiers.                   | _(any valid LinkedIn company URL)_                                               |
  | `linkedin_post_url`    | string   | optional      | _(none)_              | Direct LinkedIn post URL to fetch a single post. Cannot be used with company identifiers. | _(any valid LinkedIn post URL)_                                                  |
  | `fields`               | string   | optional      | all except `reactors` | Comma-separated list of fields to include in the response.                           |  For a complete list of valid LinkedIn post fields, see [Linkedin Post Fields](/docs/dictionary/linkedin-posts-company#linkedin-post-fields)|
  | `page`                 | number   | optional*     | 1                     | Page number for pagination. Up to 20 pages of latest posts are supported by default. | _1 ≤ integer_                                                        |
  | `limit`                | number   | optional*     | 5                     | Exact number of posts to return.                                           |  _1 ≤ integer ≤ 100_                                                                |
  | `post_types`           | string   | optional      | `repost, original`    | Determines whether to retrieve reposted content, original posts, or both.            | `original` or `repost` (or both, separated by commas)  
| `max_reactors`        | number | optional | 100                   | Maximum number of reactors to fetch for each post  (person posts only).    | _1 ≤ integer ≤ 5,000_                                                                               |
| `max_comments`        | number | optional | 100                   | Maximum number of comments to fetch for each post  (person posts only).    | _1 ≤ integer ≤ 5,000_                                                                               |

  *\* At least one of `page` or `limit` must be provided

    #### Key Points
        - Provide only one of the company identifiers per request OR use `linkedin_post_url` to fetch a single post
        - **Single Post Fetching:** When using `linkedin_post_url`, only one post is returned and pagination is not applicable
        - **Pagination:**
            - Increment the value of `page` query param (starts from 1) to fetch the next set of posts.
            - Most recent posts will be in first page and then so on.
            - Currently, you can only fetch only upto 20 pages of latest posts. In case you want to fetch more, contact Crustdata team at [info@crustdata.com](mailto:info@crustdata.com) .
        - External urls or Company/Person LinkedIn urls mentioned in text:
            - `hyperlinks` contains list of links (categorized as `company_linkedin_urls` , `person_linkedin_urls` and `other_urls` ) mentioned in the post
        - **Latency:** The data is fetched in real-time from Linkedin and the latency for this endpoint is between 30 to 60 seconds depending on number of reactions for all the posts in the page

## Credit Usage
    - Default (without reactors/comments): 1 credit per post returned in the response
    - With reactors only (`fields=reactors`): 5 credits per post returned in the response
    - With comments only (`fields=comments`): 5 credits per post returned in the response
    - With both reactors and comments (`fields=reactors,comments`): 10 credits per post returned in the response
    - **No Results, No Charges**: You are never charged credits when our APIs return no results. Credits are only deducted when data is successfully returned from your API requests.

## Examples Requests

<details id="1-posts-using-domain">
<summary>1. Posts using domain</summary>

### 1. Posts using domain
```bash
curl 'https://api.crustdata.com/screener/linkedin_posts?company_domain=https://crustdata.com&page=1' \
  --header 'Accept: application/json, text/plain, */*' \
  --header 'Accept-Language: en-US,en;q=0.9' \
  --header 'Authorization: Token $auth_token'
```
</details>

<details id="2-posts-using-domain-with-reactors">
<summary>2. Posts using domain w/ reactors</summary>

### 2. Posts using domain w/ reactors
```bash
curl 'https://api.crustdata.com/screener/linkedin_posts?company_domain=https://crustdata.com&page=1&fields=reactors' \
  --header 'Accept: application/json, text/plain, */*' \
  --header 'Accept-Language: en-US,en;q=0.9' \
  --header 'Authorization: Token $auth_token'
```
</details>

<details id="3-posts-using-domain-with-default-post-types">
<summary>3. Posts using domain with default post_types</summary>

### 3. Posts using domain with default post_types
```bash
curl 'https://api.crustdata.com/screener/linkedin_posts?company_domain=https://crustdata.com&page=1&post_types=repost%2C%20original' \
  --header 'Accept: application/json, text/plain, */*' \
  --header 'Accept-Language: en-US,en;q=0.9' \
  --header 'Authorization: Token $auth_token'
```
</details>

<details id="4-single-post-using-linkedin-post-url">
<summary>4. Single post using linkedin_post_url</summary>

### 4. Single post using linkedin_post_url
```bash
curl --location 'https://api.crustdata.com/screener/linkedin_posts?fields=reactors&linkedin_post_url=https://www.linkedin.com/feed/update/urn:li:activity:7345843680987049986' \
  --header 'Authorization: Token $auth_token'
```
</details>

<details id="5-posts-with-reactors-and-comments">
<summary>5. Posts using domain with reactors and comments</summary>

### 5. Posts using domain with reactors and comments
```bash
curl 'https://api.crustdata.com/screener/linkedin_posts?company_domain=https://crustdata.com&page=1&fields=reactors,comments' \
  --header 'Accept: application/json, text/plain, */*' \
  --header 'Accept-Language: en-US,en;q=0.9' \
  --header 'Authorization: Token $auth_token'
```
</details>

## Example Responses

<details id="1-response">
<summary>Response</summary>

### Response
The response provides a list of recent LinkedIn posts for the specified company, including post content, engagement metrics, and information about users who interacted with the posts.

Response sample: [View example response](/examples/linkedin-posts/company-posts-response.json)

**Response Structure:**
```json
{
  "posts": [
    {
      "backend_urn": "urn:li:activity:7236812027275419648",
      "actor_backend_urn": null,
      "share_urn": "urn:li:share:7236812026038083584",
      "share_url": "https://www.linkedin.com/posts/crustdata_y-combinators-most-popular-startups-from-activity-7236812027275419648-4fyw?utm_source=combined_share_message&utm_medium=member_desktop",
      "text": "Y Combinator's most popular startups.\nFrom the current S24 batch.\n\nHow do you gauge the buzz around these startups when most are pre-product?\n\nWe've defined web traffic as the metric to go by.\n\nHere are the most popular startups from YC S24:  \n\n𝟭. 𝗡𝗲𝘅𝘁𝗨𝗜: Founded by Junior Garcia\n𝟮. 𝗪𝗼𝗿𝗱𝘄𝗮𝗿𝗲: Filip Kozera, Robert Chandler\n𝟯. 𝗨𝗻𝗿𝗶𝗱𝗱𝗹𝗲: Naveed Janmohamed\n𝟰. 𝗨𝗻𝗱𝗲𝗿𝗺𝗶𝗻𝗱: Thomas Hartke, Joshua Ramette\n𝟱. 𝗖𝗼𝗺𝗳𝘆𝗱𝗲𝗽𝗹𝗼𝘆: Nick Kao, Benny Kok\n𝟲. 𝗕𝗲𝗲𝗯𝗲𝘁𝘁𝗼𝗿: Jordan Murphy, Matthew Wolfe\n𝟳. 𝗠𝗲𝗿𝘀𝗲: Kumar A., Mark Rachapoom\n𝟴. 𝗟𝗮𝗺𝗶𝗻𝗮𝗿: Robert Kim, Din Mailibay, Temirlan Myrzakhmetov\n𝟵. 𝗠𝗶𝘁𝗼𝗛𝗲𝗮𝗹𝘁𝗵: Kenneth Lou, Tee-Ming C., Joel Kek, Ryan Ware\n𝟭𝟬. 𝗔𝘂𝘁𝗮𝗿𝗰: Etienne-Noel Krause,Thies Hansen, Marius Seufzer\n\n🤔 Interested in reading more about the YC S24 batch?\n\nRead our full breakdown from the link in the comments 👇",
      "actor_name": "Crustdata",
      "date_posted": "2024-09-03",
      "hyperlinks": {
          "company_linkedin_urls": [],
          "person_linkedin_urls": [
              "https://www.linkedin.com/in/ACoAAAKoldoBqSsiXY_DHsXdSk1slibabeTvDDY"
          ],
          "other_urls": []
      },
      "total_reactions": 37,
      "total_comments": 7,
      "reactions_by_type": {
        "LIKE": 28,
        "EMPATHY": 4,
        "PRAISE": 4,
        "INTEREST": 1
      },
      "num_shares": 5,
      "is_repost_without_thoughts": false,
      "reactors": [
        {
          "name": "Courtney May",
          "linkedin_profile_url": "https://www.linkedin.com/in/ACwAACkMyzkBYncrCuM2rzhc06iz6oj741NL-98",
          "reaction_type": "LIKE",
          "profile_image_url": "https://media.licdn.com/dms/image/v2/D5603AQF-8vL_c5H9Zg/profile-displayphoto-shrink_100_100/profile-displayphoto-shrink_100_100/0/1690558480623?e=1730937600&v=beta&t=Lm2hHLTFiEVlHWdTt-Vh3vDYevK8U8SlPqaFdNu3R6A",
          "title": "GTM @ Arc (YC W22)",
          "additional_info": "3rd+",
          "location": "San Francisco, California, United States",
          "linkedin_profile_urn": "ACwAACkMyzkBYncrCuM2rzhc06iz6oj741NL-98",
          "default_position_title": "GTM @ Arc (YC W22)",
          "default_position_company_linkedin_id": "74725230",
          "default_position_is_decision_maker": false,
          "flagship_profile_url": "https://www.linkedin.com/in/courtney-may-8a178b172",
          "profile_picture_url": "https://media.licdn.com/dms/image/v2/D5603AQF-8vL_c5H9Zg/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1690558480623?e=1730937600&v=beta&t=vHg233746zA00m3q2vHKSFcthL3YKiagTtVEZt1qqJI",
          "headline": "GTM @ Arc (YC W22)",
          "summary": null,
          "num_of_connections": 786,
          "related_colleague_company_id": 74725230,
          "skills": [
            "Marketing Strategy",
            "Product Support",
            "SOC 2"
          ],
          "employer": [
            {
              "title": "GTM @ Arc (YC W22)",
              "company_name": "Arc",
              "company_linkedin_id": "74725230",
              "start_date": "2024-07-01T00:00:00",
              "end_date": null,
              "description": null,
              "location": "San Francisco, California, United States",
              "rich_media": []
            }
          ],
          "education_background": [
            {
              "degree_name": "Bachelor of Applied Science - BASc",
              "institute_name": "Texas Christian University",
              "field_of_study": "Economics",
              "start_date": "2016-01-01T00:00:00",
              "end_date": "2020-01-01T00:00:00"
            }
          ],
          "emails": [
            "email@example.com"
          ],
          "websites": [],
          "twitter_handle": null,
          "languages": [],
          "pronoun": null,
          "current_title": "GTM @ Arc (YC W22)"
        }
      ]
    }
  ]
}
```
</details>

---

## 🔧 OpenAPI Specification

# LinkedIn Posts API (realtime)

**Category:** People API
**Base URL:** https://api.crustdata.com

**Endpoint:** `GET /screener/linkedin_posts`

**Description:** Retrieve recent LinkedIn posts plus engagement metrics for either a **person** or a **company**.<br/><br/> **Exactly one** of `person_linkedin_url`, `company_domain`, `company_linkedin_url`, `company_name`, or `company_id` must be supplied.<br/><br/> [Show Docs (People API)](/docs/discover/people-apis/people-linkedin-post-api)<br/> [Show Docs (Company API)](/docs/discover/company-apis/company-linkedin-post)

## Authentication
This endpoint requires a Bearer token in the `Authorization` header:

```
Authorization: Token <YOUR_TOKEN>
```
## Query Parameters
| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|

## Example Request

```bash
curl -X GET "https://api.crustdata.com/screener/linkedin_posts?person_linkedin_url=https%3A%2F%2Fwww.linkedin.com%2Fin%2Fsatyanadella&company_domain=hubspot.com%2Cgithub.com&company_linkedin_url=https%3A%2F%2Fwww.linkedin.com%2Fcompany%2Ftryretool%2Chttps%3A%2F%2Fwww.linkedin.com%2Fcompany%2Fmintlify" \
  -H "Authorization: Token &lt;YOUR_TOKEN&gt;"
```

## Rate Limiting
All Crustdata API requests count toward your per-minute quota. Inspect the response headers `X-RateLimit-Limit` and `X-RateLimit-Remaining` to monitor usage. Implement exponential back-off or retries when you receive a **429 Too Many Requests** response.

## Responses
### Status 200
**Description:** The response provides a list of recent LinkedIn posts for the specified company or person, including post content, engagement metrics, and information about users who interacted with the posts.
**Response Schema:**
Array of:
| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `backend_urn` | string | No | Unique identifier for the post in LinkedIn's backend system |  |  |
| `actor_backend_urn` | string | No | Unique identifier for the actor's post in LinkedIn's backend system |  |  |
| `share_urn` | string | No | Unique identifier for the shared content |  |  |
| `share_url` | string | No | Direct URL to the post on LinkedIn |  |  |
| `text` | string | No | The full content of the post |  |  |
| `hyperlinks` | object | No | URLs found in the post content, categorized by type |  |  |
| `actor_name` | string | No | Name of the company or person who created the post |  |  |
| `date_posted` | string | No | Date when the post was published, in "YYYY-MM-DD" format |  |  |
| `is_repost_without_thoughts` | boolean | No | Indicates if this is a repost without any additional commentary |  |  |
| `total_reactions` | integer | No | Total number of reactions on the post |  |  |
| `total_comments` | integer | No | Total number of comments on the post |  |  |
| `reactions_by_type` | object | No | Breakdown of reactions by type (e.g., "LIKE", "EMPATHY", "PRAISE", "INTEREST") |  |  |
| `num_shares` | integer | No | Number of times the post has been shared |  |  |
| `reactors` | array | No | List of users who reacted to the post |  |  |

### Status 400
**Description:** Bad request, please check your request body to fix this error.
**Response Schema:**
| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `error` | string | No |  |  |  |

## 📋 OpenAPI Components

## Query Parameters Components

```yaml
parameters:
  PersonLinkedInURL:
    name: person_linkedin_url
    in: query
    description: "LinkedIn profile URL of the person.<br/> Flagship (`https://linkedin.com/in/name`) or FSD (`.../in/ACoAAA...`) formats are both accepted.\n"
    required: false
    schema:
      type: string
      example: "https://www.linkedin.com/in/satyanadella"

  CompanyDomain:
    name: company_domain
    in: query
    description: "Comma-separated list (max 25) of company domains."
    required: false
    schema:
      type: string
      example: "hubspot.com,github.com"

  CompanyLinkedInURL:
    name: company_linkedin_url
    in: query
    description: "Comma-separated list (max 25) of LinkedIn company profile URLs."
    required: false
    schema:
      type: string
      example: "https://www.linkedin.com/company/tryretool,https://www.linkedin.com/company/mintlify"

  CompanyName:
    name: company_name
    in: query
    description: "Comma-separated list (max 25) of company names. If a name itself contains a comma, wrap it in double quotes.\n"
    required: false
    schema:
      type: string
      example: "retool,mintlify"

  CompanyID:
    name: company_id
    in: query
    description: "Comma-separated list (max 25) of Crustdata company IDs."
    required: false
    schema:
      type: string
      example: "12345,67890"

  PostPage:
    name: page
    in: query
    description: "Page number for pagination (starts from 1, max 20)."
    required: false
    schema:
      type: integer
      default: 1
      example: "1"

  PostLimit:
    name: limit
    in: query
    description: "Number of posts to return (1-100)."
    required: false
    schema:
      type: integer
      default: 5
      example: "10"

  PostTypes:
    name: post_types
    in: query
    description: "Specify `\"original\"`, `\"repost\"`, or `\"repost,original\"`.\n"
    required: false
    schema:
      type: string
      default: repost,original
      example: "original"

  PostFields:
    name: fields
    in: query
    description: "Comma-separated list of fields to include in the response."
    required: false
    schema:
      type: string
      example: "id,created_at,stats.like_count"

  PostMaxReactors:
    name: max_reactors
    in: query
    description: "Maximum reactors to fetch per post (people posts only, 1-5000).\n"
    required: false
    schema:
      type: integer
      default: 100
      example: "250"

  PostMaxComments:
    name: max_comments
    in: query
    description: "Maximum comments to fetch per post (people posts only, 1-5000).\n"
    required: false
    schema:
      type: integer
      default: 100
      example: "250"

```

## Response Schema Components

```yaml
schemas:
  Post:
    type: object
    properties:
      backend_urn:
        type: string
        description: "Unique identifier for the post in LinkedIn's backend system"
      actor_backend_urn:
        type: string
        description: "Unique identifier for the actor's post in LinkedIn's backend system"
      share_urn:
        type: string
        description: "Unique identifier for the shared content"
      share_url:
        type: string
        description: "Direct URL to the post on LinkedIn"
      text:
        type: string
        description: "The full content of the post"
      # ... (9 more properties)

  Reactor:
    type: object
    properties:
      name:
        type: string
        description: "Full name of the person who reacted"
      linkedin_profile_url:
        type: string
        description: "URL to the reactor's LinkedIn profile"
      reaction_type:
        type: string
        description: "Type of reaction given (e.g., \"LIKE\", \"EMPATHY\")"
      profile_image_url:
        type: string
        description: "URL to the reactor's profile image (100x100 size)"
      title:
        type: string
        description: "Current professional title of the reactor"
      # ... (23 more properties)

  Employment:
    type: object
    properties:
      title:
        type: string
        description: "Job title"
      company_name:
        type: string
        description: "Name of the employer"
      company_linkedin_id:
        type: string
        description: "LinkedIn ID of the company"
      company_logo_url:
        type: string
        description: "URL to the company logo image"
      start_date:
        type: string
        description: "Start date of employment"
      # ... (5 more properties)

  Education:
    type: object
    properties:
      degree_name:
        type: string
        description: "Type of degree obtained"
      institute_name:
        type: string
        description: "Name of the educational institution"
      field_of_study:
        type: string
        description: "Area of study"
      start_date:
        type: string
        description: "Start date of education"
      end_date:
        type: string
        description: "End date of education"
      # ... (3 more properties)

  DataLabFundingTimeseriesResponse:
    type: object
    properties:
      fields:
        type: array
        description: "An array describing the columns in the dataset"
      rows:
        type: array
        description: "Each row is an array of values, in the same order as `fields`"
      is_trial_user:
        type: boolean
        description: "Indicates if the current user is on a trial subscription"

  PostsResponse:
    type: object
    properties:
      posts:
        type: array
        description: "An array of LinkedIn posts"

  PostWithKeywords:
    type: object
    properties:
      backend_urn:
        type: string
        description: "Unique identifier for the post in LinkedIn's backend system"
      uid:
        type: string
        description: "Unique identifier for the post in the system"
      share_urn:
        type: string
        description: "Unique identifier for the shared content"
      share_url:
        type: string
        description: "Direct URL to the post on LinkedIn"
      text:
        type: string
        description: "The full content of the post"
      # ... (16 more properties)

```

---

<!-- Error loading /docs/discover/company-apis/company-request-fields -->

# Comprehensive API Documentation: company-search-api

## 📋 Documentation Metadata

- **API Path:** `POST /screener/company/search`
- **Category:** Company API
- **Operation:** api
- **Documentation File:** company-search-api.md
- **Data Dictionary:** company-search.md
- **Main Documentation:** discover/company-apis/company-search-api.md
- **Generated:** 2025-11-27T14:03:48.591Z

---

## 📖 Original Documentation

# Realtime: Company Search API

### [ 🚀 Try Now ](/api#tag/company-api/POST/screener/company/search)

The Company Search API allows you to search for company profiles based on various filters, providing detailed information about companies that match your criteria. This guide will help you understand how to make queries to the API using filters, with easy-to-follow examples.

## Endpoint

```
POST /screener/company/search
```

## Data Dictionary

[Explore the data dictionary for this endpoint here](/docs/dictionary/company-search)

## Request Parameters

| Payload Keys                             | Type    | Description                                                |
| ------------------------------------- | ------- | ---------------------------------------------------------- |
| `filters`                             | array   | An array of filter objects specifying your search criteria. Refer to [How to Build Company Filters](/docs/discover/company-apis/how-to-build-company-filters) for more details. |
| `page`                                | integer | The page number for pagination. Has to be between 1 - 65                           |
:::info
- `page` must be between 1 to 65. If your query has more than 65 pages, please split filters into smaller sets. For example, make individual requests per `INDUSTRY` instead of sending a list in a single request.
:::

#### Key Points
- **Pagination**: Each request returns up to 25 results. Use the `page` parameter (starts from 1) to access additional results.
- **Combining Filters**: You can combine multiple filters to narrow down your search. Filters are combined using logical `AND` operations.
- **Valid Values**: Ensure you're using valid values for each `filter_type`. Refer to [How to Build Filters](/docs/discover/how-to-build-company-filters) for a comprehensive list of filter types and acceptable values.

## Credit Usage
- Each company returned in the search results costs 1 credit
- This endpoint returns 25 companies per page by default
- **No Results, No Charges**: You are never charged credits when our APIs return no results. Credits are only deducted when data is successfully returned from your API requests.

## Finding Valid Filter Values with Autocomplete

Before building your search filters, use the **Filters Autocomplete API** to discover valid field values. This ensures your filters work correctly and helps you find the exact values you need.

### 🔍 Available Autocomplete APIs for Different Filter Types

| Filter Type | Use Case |
|-------------|-----------------|
| Region |  Geographic regions and locations |
| Industry |  Industry categories |
| Title |  Job titles |
| School |  Educational institutions and schools |

### Quick Example: Finding Company Regions

####  Step 1: Get region suggestions
```bash
curl 'https://api.crustdata.com/screener/linkedin_filter/autocomplete?filter_type=region&query=united&count=5' \
--header 'Authorization: Token $authToken'
```

#### Step 2: Use exact value in your search

```bash
curl -X POST 'https://api.crustdata.com/screener/company/search' \
  -H "Authorization: Token $auth_token" \
  --data '{
    "filters": [
      {
        "filter_type": "REGION",
        "type": "in",
        "value": ["United States"]
      }
    ]
  }'
```

**💡 Pro Tip**: Always use the autocomplete API first to get exact field values. This prevents filter errors and ensures your searches return the expected results.

## Example Requests

<details id="1-via-custom-search-filters">
<summary>1. Via Custom Search Filters</summary>

### 1. Via Custom Search Filters

To find companies with headcounts over 1,000 employees, annual revenue between $1 million and $500 million USD, excluding companies in the United States:

```json
curl -X POST 'https://api.crustdata.com/screener/company/search' \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $auth_token" \
  --data-raw '{
    "filters": [
      {
        "filter_type": "COMPANY_HEADCOUNT",
        "type": "in",
        "value": [
          "1,001-5,000",
          "5,001-10,000",
          "10,001+"
        ]
      },
      {
        "filter_type": "ANNUAL_REVENUE",
        "type": "between",
        "value": {
          "min": 1,
          "max": 500
        },
        "sub_filter": "USD"
      },
      {
        "filter_type": "REGION",
        "type": "not in",
        "value": [
          "United States"
        ]
      }
    ],
    "page": 1
  }'
```

</details>

<details id="2-actively-hiring-tech-companies">
<summary>2. Actively Hiring Tech Companies</summary>

### 2. Technology Companies Hiring on LinkedIn

To find technology companies that are currently hiring on LinkedIn:

```json
curl -X POST 'https://api.crustdata.com/screener/company/search' \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $auth_token" \
  --data-raw '{
    "filters": [
      {
        "filter_type": "INDUSTRY",
        "type": "in",
        "value": [
          "Technology",
          "Information Technology and Services"
        ]
      },
      {
        "filter_type": "JOB_OPPORTUNITIES",
        "type": "in",
        "value": [
          "Hiring on Linkedin"
        ]
      }
    ],
    "page": 1
  }'
```

</details>

<details id="3-companies-with-recent-funding-events">
<summary>3. Recently Funded</summary>

### 3. Companies with Recent Funding Events

To find companies that have had funding events in the past 12 months:

```json
curl -X POST 'https://api.crustdata.com/screener/company/search' \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $auth_token" \
  --data-raw '{
    "filters": [
      {
        "filter_type": "ACCOUNT_ACTIVITIES",
        "type": "in",
        "value": [
          "Funding events in past 12 months"
        ]
      }
    ],
    "page": 1
  }'
```

</details>

## Example Responses

<details id="1-success-200-ok">
<summary>Success (200 OK)</summary>

### Successful Response (200 OK)

A successful response returns a JSON object containing:

- `companies`: An array of company objects matching your filters.
- `total_display_count`: The total number of results available for your query.

```json
{
  "companies": [
    {
      "name": "Mashreq",
      "description": "Disclaimer: Mashreq will never ask for your bank related information via phone call, SMS or email. We will also never contact you from a mobile number to resolve your query.\n\nWelcome to the LinkedIn page of Mashreq. More than half a century old, we proudly think like a challenger, startup, and innovator in banking and finance, powered by a diverse and dynamic team who put customers first. Together, we pioneer key innovations and developments in banking and financial services. Our mandate? To help customers find their way to Rise Every Day, partnering with them through the highs and lows to help them reach their goals and unlock their unique vision of success. Join Mashreq and find your way to Rise Every Day.",
      "linkedin_company_url": "https://www.linkedin.com/company/mashreq-uae/",
      "linkedin_company_id": "11425",
      "website": "http://www.mashreq.com/rise",
      "industry": "Banking",
      "company_type": "Public Company",
      "founded_year": 1967,
      "location": "Dubai, Dubai, United Arab Emirates",
      "headquarters": {
        "country": "United Arab Emirates",
        "geographicArea": "UAE",
        "city": "Dubai",
        "line1": "Mashreq Bank PSC, Umniyati Street (off Al Asayel Street Burj Khalifa Community"
      },
      "employee_count": 9085,
      "employee_count_range": "1001-5000",
      "employee_growth_percentages": [
        {
          "timespan": "SIX_MONTHS",
          "percentage": 2
        },
        {
          "timespan": "YEAR",
          "percentage": 5
        },
        {
          "timespan": "TWO_YEAR",
          "percentage": 15
        }
      ],
      "specialties": [
        "Retail Banking",
        "Corporate Banking",
        "SME Banking",
        "Islamic Banking",
        "Treasury and Capital Markets",
        "Digital Banking",
        "Financial Institutions",
        "Global Trade Banking",
        "Wholesale Banking",
        "International Banking"
      ],
      "revenue_range": {
        "estimatedMinRevenue": {
          "amount": 500.0,
          "unit": "MILLION",
          "currencyCode": "USD"
        },
        "estimatedMaxRevenue": {
          "amount": 1.0,
          "unit": "BILLION",
          "currencyCode": "USD"
        }
      },
      "decision_makers_count": "681",
      "logo_urls": {
        "200x200": "...",
        "100x100": "...",
        "400x400": "..."
      }
    }
    // More company objects...
  ],
  "total_display_count": 120
}
```

</details>

<details id="2-error-400-bad-request">
<summary>Error (400 Bad Request)</summary>

### Error Response (400 Bad Request)

If your filters are invalid or there is an error processing your request, you will receive an error message:

```json
{
  "error": "Failed to parse filters"
}
```

</details>

---

## 📊 Data Dictionary

# Company Search API Dictionary

This dictionary describes the data returned by the Company Search API (`/screener/company/search` endpoint). It provides details about company objects returned when searching companies based on various filters.

## Response Structure

The API returns a JSON object containing:
- `companies`: An array of company objects matching your filters
- `total_display_count`: The total number of results available for your query

## Company Object Structure

Each company object in the response contains the following fields:

| Field                      | Type     | Description                                                     |
|----------------------------|----------|-----------------------------------------------------------------|
| name                       | string   | Name of the company                                             |
| description                | string   | Detailed description of the company, typically from LinkedIn    |
| linkedin_company_url       | string   | URL to the company's LinkedIn profile                           |
| linkedin_company_id        | string   | Unique LinkedIn identifier for the company                      |
| website                    | string   | Company's official website URL                                  |
| industry                   | string   | Primary industry in which the company operates                  |
| company_type               | string   | Type of company (e.g., "Privately Held", "Public Company")     |
| founded_year               | integer  | Year the company was founded                                    |
| location                   | string   | General location of the company                                 |

## Headquarters Information

| Field                      | Type     | Description                                                     |
|----------------------------|----------|-----------------------------------------------------------------|
| headquarters               | object   | Object containing headquarters location details                 |
| headquarters.country       | string   | Country where headquarters is located                           |
| headquarters.geographicArea| string   | Geographic area/region within the country                       |
| headquarters.city          | string   | City where headquarters is located                              |
| headquarters.line1         | string   | Street address of headquarters                                  |

## Employee Information

| Field                      | Type     | Description                                                     |
|----------------------------|----------|-----------------------------------------------------------------|
| employee_count             | integer  | Approximate number of employees                                 |
| employee_count_range       | string   | Range of employee count (e.g., "2-10", "11-50")                |
| employee_growth_percentages| array    | Array of objects showing growth over different time periods     |

### Employee Growth Percentages

| Field                                  | Type     | Description                                           |
|----------------------------------------|----------|-------------------------------------------------------|
| employee_growth_percentages[].timespan | string   | Time period for growth measurement (SIX_MONTHS, YEAR, TWO_YEAR) |
| employee_growth_percentages[].percentage | integer | Growth percentage for the specified timespan         |

## Specialties and Revenue

| Field                      | Type     | Description                                                     |
|----------------------------|----------|-----------------------------------------------------------------|
| specialties                | array    | List of company specialties or focus areas                      |
| revenue_range              | object   | Object containing revenue range information                     |
| decision_makers_count      | string   | Number of identified decision makers at the company             |

### Revenue Range Details

| Field                                         | Type     | Description                                   |
|-----------------------------------------------|----------|-----------------------------------------------|
| revenue_range.estimatedMinRevenue             | object   | Object with minimum revenue estimation        |
| revenue_range.estimatedMinRevenue.amount      | number   | Numeric value of minimum revenue              |
| revenue_range.estimatedMinRevenue.unit        | string   | Unit multiplier (ONE, THOUSAND, MILLION, etc.)|
| revenue_range.estimatedMinRevenue.currencyCode| string   | Currency code (e.g., "USD")                   |
| revenue_range.estimatedMaxRevenue             | object   | Object with maximum revenue estimation        |
| revenue_range.estimatedMaxRevenue.amount      | number   | Numeric value of maximum revenue              |
| revenue_range.estimatedMaxRevenue.unit        | string   | Unit multiplier (ONE, THOUSAND, MILLION, etc.)|
| revenue_range.estimatedMaxRevenue.currencyCode| string   | Currency code (e.g., "USD")                   |

## Logo Information

| Field                      | Type     | Description                                                     |
|----------------------------|----------|-----------------------------------------------------------------|
| logo_urls                  | object   | Object containing URLs to company logos in different sizes      |
| logo_urls.200x200          | string   | URL to 200x200 pixel logo image                                |
| logo_urls.100x100          | string   | URL to 100x100 pixel logo image                                |
| logo_urls.400x400          | string   | URL to 400x400 pixel logo image                                | 

---

## 🔧 OpenAPI Specification

# Search API (realtime)

**Category:** Company API
**Base URL:** https://api.crustdata.com
**Official Docs:** /docs/discover/company-apis/company-search-api

**Endpoint:** `POST /screener/company/search`

**Description:** Searches for company profiles on the web in real-time. Accepts a set of filters for search criteria. See [How to Build Filters](/docs/discover/company-apis/how-to-build-company-filters).
> [Show Docs](/docs/discover/company-apis/company-search-api)

## Authentication
This endpoint requires a Bearer token in the `Authorization` header:

```
Authorization: Token <YOUR_TOKEN>
```
## Request Body Schema

| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `filters` | array | No |  |  |  |
| `page` | integer | No |  |  | 1 |

## Example Request

```bash
curl -X POST "https://api.crustdata.com/screener/company/search" \
  -H "Authorization: Token &lt;YOUR_TOKEN&gt;" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{"filter_type":"COMPANY_HEADCOUNT","type":"in","value":["5,001-10,000","1-10","11-50"]}],
    "page": 1
  }'
```

## Rate Limiting
All Crustdata API requests count toward your per-minute quota. Inspect the response headers `X-RateLimit-Limit` and `X-RateLimit-Remaining` to monitor usage. Implement exponential back-off or retries when you receive a **429 Too Many Requests** response.

## Responses
### Status 200
**Description:** A JSON response containing a list of company profiles found and the total number of profiles available.
**Response Schema:**
| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `companies` | array | No |  |  |  |
| `total_display_count` | string | No | Short scale notation (like 1M+ or 1.5K) representing the total number of profiles available for the search. |  |  |

### Status 400
**Description:** Bad request, please check your request body to fix this error.
**Response Schema:**
| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `error` | string | No |  |  |  |

## 📋 OpenAPI Components

## Response Schema Components

```yaml
schemas:
  CompanySearchByFilters:
    type: object
    properties:
      filters:
        type: array
      page:
        type: integer
        example: 1

  CompanySearchResponse:
    type: object
    properties:
      name:
        type: string
      description:
        type: string
      linkedin_company_url:
        type: string
      linkedin_company_id:
        type: string
      website:
        type: string
      # ... (12 more properties)

```

---

