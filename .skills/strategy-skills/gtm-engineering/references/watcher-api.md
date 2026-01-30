<api_overview>
## Crustdata Watcher API Reference

Watchers are automated monitors that send webhook notifications when specific events occur. This reference documents all watcher types, their filters, and sample payloads.

**Base URL:** `https://api.crustdata.com`
**Authentication:** `Authorization: Token $api_token`
</api_overview>

<account_watchers>
## Account-Level Watchers

These watchers monitor company-level signals.

<watcher type="job-posting-by-company">
### Job Posting by Company

**Slug:** `company-watch-linkedin-job-postings`

**Use Cases:**
- Company is hiring for specific roles
- Company posting jobs in target locations
- Company hiring signals indicate growth/expansion

**Event Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `COMPANY_DOMAIN` | list(max 1) | Domain of company. Example: `["artisan.co"]` |
| `COMPANY_LINKEDIN_URL` | list(max 1) | LinkedIn URL. Example: `["https://linkedin.com/company/signalhq"]` |
| `COMPANY_ID` | list(max 1) | Crustdata company ID. Example: `["1403180"]` |
| `REGION` | list(max 1) | Job location. Example: `["United States"]`, `["India"]` |
| `TITLE` | list(max 1) | Job title to track. Example: `["Software Engineer"]` |
| `DESCRIPTION` | list(max 1) | Keywords in description. Example: `["Machine Learning"]` |

**Sample Notification:**
```json
{
  "uid": "jobposting_linkedin_5cdf0a96c1981364...",
  "url": "https://www.linkedin.com/jobs/view/4106896337",
  "title": "Operations Associate (Part-Time)",
  "category": "Operations",
  "country_id": "US",
  "date_added": "2024-12-23T22:36:17+00:00",
  "description": "Full job description text...",
  "company_name": "Alo Yoga",
  "location_text": "Schaumburg, Illinois, United States",
  "company_domain": "aloyoga.com",
  "workplace_type": "On-site",
  "company_linkedin_url": "https://www.linkedin.com/company/aloyoga",
  "crustdata_company_id": 1126745
}
```

**Example Request:**
```bash
curl --location 'https://api.crustdata.com/watcher/watches' \
--header 'Authorization: Token $api_token' \
--header 'Content-Type: application/json' \
--data '{
    "event_type_slug": "company-watch-linkedin-job-postings",
    "event_filters": [
        {"filter_type": "COMPANY_DOMAIN", "type": "in", "value": ["microsoft.com"]},
        {"filter_type": "REGION", "type": "in", "value": ["India"]}
    ],
    "notification_endpoint": "https://your-webhook.com/notify",
    "frequency": 1,
    "expiration_date": "2025-12-31"
}'
```
</watcher>

<watcher type="company-linkedin-posts">
### Company LinkedIn Posts

**Slug:** `company-watch-linkedin-posts`

**Use Cases:**
- Monitor competitor content strategy
- Track customer/prospect engagement
- Identify trending topics in industry

**Event Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `COMPANY_DOMAIN` | list(max 1) | Domain of company |
| `COMPANY_LINKEDIN_URL` | list(max 1) | LinkedIn URL |
| `COMPANY_ID` | list(max 1) | Crustdata company ID |
| `POST_CATEGORY` | list(max 10) | Categories: `["Business", "Personal", "Events", "Social Commentary"]` |

**Sample Notification:**
```json
{
  "uid": "post_linkedin_c499e444174f45c3...",
  "text": "Full post content here...",
  "share_url": "https://www.linkedin.com/posts/groww...",
  "actor_name": "Groww",
  "actor_type": "company",
  "num_shares": 6,
  "date_posted": "2024-11-23",
  "company_name": "Groww",
  "total_comments": 3,
  "total_reactions": 443,
  "reactions_by_type": {
    "LIKE": 425,
    "PRAISE": 1,
    "INTEREST": 13
  },
  "company_linkedin_url": "https://www.linkedin.com/company/groww.in",
  "reactors": [/* Array of reactor profiles */]
}
```
</watcher>

<watcher type="company-press-mentions">
### Company News/Press Mentions

**Slug:** `company-watch-press-mentions`

**Use Cases:**
- Track when target accounts are in the news
- Monitor competitor announcements
- Identify trigger events (expansion, partnerships)

**Event Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `COMPANY_DOMAIN` | list(max 1) | Domain of company |
| `COMPANY_LINKEDIN_URL` | list(max 1) | LinkedIn URL |
| `COMPANY_ID` | list(max 1) | Crustdata company ID |

**Sample Notification:**
```json
{
  "uid": "press_mention_513ac3dc8e7a0f64...",
  "article_url": "https://www.businessinsider.com/fintech-finix...",
  "article_title": "Fintech Finix just became a payments processor...",
  "article_publish_date": "2023-05-02T00:00:00+00:00",
  "article_publisher_name": "Business Insider",
  "company_name": "Finix Payments",
  "company_linkedin_url": "https://www.linkedin.com/company/finix-payments/",
  "company_domain": "finixpayments.com",
  "company_id": 632904
}
```
</watcher>

<watcher type="company-funding">
### Company Funding Announcements

**Slug:** `company-watch-funding-milestones`

**Use Cases:**
- Track when targets raise funding (buying signal)
- Monitor competitor funding
- Identify fast-growing companies in ICP

**Event Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `COMPANY_DOMAIN` | list(max 1) | Domain of company |
| `COMPANY_LINKEDIN_URL` | list(max 1) | LinkedIn URL |
| `COMPANY_ID` | list(max 1) | Crustdata company ID |

**Sample Notification:**
```json
{
  "uid": "funding_milestone_7e1b8a2dc1dc021f...",
  "funding_date": "2017-10-10T00:00:00+00:00",
  "funding_round": "Seed Round - Finix",
  "funding_investors": "Homebrew",
  "funding_amount_usd": 3500000,
  "company_domain": "finixpayments.com",
  "company_id": 632904,
  "company_name": "Finix Payments",
  "company_linkedin_url": "https://www.linkedin.com/company/finix-payments/"
}
```
</watcher>

<watcher type="company-headcount-growth">
### Company Headcount Growth

**Slug:** `company-watch-headcount-growth`

**Use Cases:**
- Track companies growing quickly (expansion signal)
- Monitor specific growth thresholds
- Identify scaling companies in ICP

**Event Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `COMPANY_DOMAIN` | list(max 1) | Domain of company |
| `COMPANY_LINKEDIN_URL` | list(max 1) | LinkedIn URL |
| `COMPANY_ID` | list(max 1) | Crustdata company ID |
| `COMPANY_HEADCOUNT_GROWTH` | dict | Threshold growth %. Example: `{"min":0, "max": 1000}` |
| `TIMEFRAME` | list(max 1) | Period: `["MoM"]`, `["QoQ"]`, `["6M"]`, `["YoY"]`, `["2Y"]` |

**Sample Notification:**
```json
{
  "YoY": 53.29,
  "uid": "company_headcount_growth_10dd2c47ff85...",
  "company_id": 681012,
  "company_name": "Amazon",
  "company_domain": "amazon.com",
  "company_linkedin_id": "89387262",
  "company_linkedin_url": "http://www.linkedin.com/company/amazon"
}
```
</watcher>
</account_watchers>

<lead_watchers>
## Lead-Level Watchers

These watchers monitor individual people.

<watcher type="person-job-change">
### Person Job Change/Promotion

**Slug:** `linkedin-person-profile-updates`

**Use Cases:**
- Track when champions change jobs (new opportunity)
- Monitor key prospects for promotions
- Identify decision-maker movements

**Event Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `LINKEDIN_PROFILE_URL` | list | LinkedIn profile URLs to track |
| `FIELDS_TO_TRACK` | list | Fields: `['employer_change', 'summary', 'headline', 'skills', 'location']` |

**Trackable Fields:**
- `employer_change`: New positions, removed positions, title/company changes
- `summary`: Changes to "About" section
- `headline`: Professional tagline updates
- `skills`: Skill additions/removals
- `location`: Geographic changes

**Sample Notification:**
```json
{
  "uid": "person_profile_updates_linkedin_2305fcd7cf99...",
  "profile_url": "https://www.linkedin.com/in/rishabh-raj-539514330",
  "person_title": "Senior Product Engineer",
  "person_location": "Delhi, India",
  "changes": {
    "field_changes": {
      "skills": {
        "current": [],
        "previous": ["Software Design"]
      }
    },
    "position_changes": {
      "new_positions": [{
        "details": {
          "employer_name": "Fever",
          "employee_title": "Senior Product Engineer",
          "start_date": "2025-03-01T00:00:00+00:00"
        }
      }],
      "changed_positions": [{
        "changes": {
          "end_date": {
            "current": "2025-03-01T00:00:00+00:00",
            "previous": null
          }
        }
      }]
    }
  },
  "current_employers": [/* Current employment details */],
  "past_employers": [/* Previous employment history */]
}
```
</watcher>

<watcher type="person-linkedin-posts">
### Person LinkedIn Posts

**Slug:** `linkedin-person-post-updates`

**Use Cases:**
- Monitor prospect engagement opportunities
- Track thought leader content
- Identify conversation starters

**Event Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `LINKEDIN_PROFILE_URL` | list | LinkedIn profile URLs to track |
| `POST_CATEGORY` | list(max 10) | Categories: `["Business", "Personal", "Events", "Social Commentary"]` |
| `REACTORS` | boolean | Include reactor profiles: `{"filter_type": "REACTORS"}` |

**Sample Notification:**
```json
{
  "uid": "person_post_updates_linkedin_e46c8a06f3ecca...",
  "text": "Full post content...",
  "share_url": "https://www.linkedin.com/feed/update/urn:li:share:735...",
  "actor_name": "Chris Pisarski",
  "actor_type": "person",
  "date_posted": "2025-07-29",
  "person_linkedin_flagship_profile_url": "https://www.linkedin.com/in/chris-pisarski/",
  "person_name": "Chris Pisarski",
  "person_title": "Founder",
  "post_summary": "AI-generated summary of post content",
  "post_category": "Business",
  "total_comments": 7,
  "total_reactions": 33,
  "current_employers": [/* Employment details */],
  "hyperlinks": {
    "person_linkedin_urls": [/* Mentioned people */],
    "company_linkedin_urls": [/* Mentioned companies */]
  }
}
```
</watcher>
</lead_watchers>

<market_watchers>
## Market-Level Watchers

These watchers monitor market-wide signals filtered by criteria.

<watcher type="job-posting-market">
### Job Postings with Keyword/Location (Market)

**Slug:** `job-posting-with-keyword-and-location`

**Use Cases:**
- Track all companies hiring for specific roles
- Monitor hiring trends in a region
- Identify companies investing in specific capabilities

**Event Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `TITLE` | list | Job title keywords. Example: `["Software Engineer"]` |
| `REGION` | list | Location filter. Example: `["United States"]` |

**Account Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `COMPANY_HEADCOUNT` | list | Size filters: `["10,001+", "5,001-10,000", "11-50", "1-10"]` |

**Example Request:**
```bash
curl --location 'https://api.crustdata.com/watcher/watches' \
--header 'Authorization: Token $api_token' \
--header 'Content-Type: application/json' \
--data '{
    "event_type_slug": "job-posting-with-keyword-and-location",
    "event_filters": [
        {"filter_type": "TITLE", "type": "in", "value": "Software Engineer"},
        {"filter_type": "REGION", "type": "in", "value": "Bangladesh"}
    ],
    "account_filters": [
        {"filter_type": "COMPANY_HEADCOUNT", "type": "in", "value": ["10,001+", "5,001-10,000"]}
    ],
    "notification_endpoint": "https://your-webhook.com/notify",
    "frequency": 1,
    "expiration_date": "2026-01-01",
    "max_notifications_per_execution": 100
}'
```
</watcher>

<watcher type="job-posting-location">
### Job Postings by Location Only (Market)

**Slug:** `job-posting-with-location`

**Use Cases:**
- Track all job postings in a specific region
- Monitor hiring activity in target markets
- Identify companies expanding into new geographies

**Event Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `REGION` | list | Location filter. Example: `["Germany"]`, `["San Francisco Bay Area"]` |

**Account Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `COMPANY_HEADCOUNT` | list | Size filters: `["10,001+", "5,001-10,000", "51-200", "11-50"]` |
</watcher>

<watcher type="funding-announcements">
### New Funding Announcements (Market)

**Slug:** `new-funding-announcements`

**Use Cases:**
- Track all funding rounds in target industries
- Monitor Seed-Series B rounds for prospecting
- Identify newly funded companies with buying power

**Event Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `FUNDING_TYPE` | list | Round types: `["Seed", "Series A", "Series B", "Series C+", "Debt"]` |
| `FUNDING_AMOUNT` | dict | Amount range. Example: `{"min": 1000000, "max": 50000000}` |

**Account Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `COMPANY_HEADCOUNT` | list | Size filters |
| `COMPANY_INDUSTRY` | list | Industry verticals |
</watcher>

<watcher type="linkedin-post-keyword">
### LinkedIn Posts with Keyword (Market)

**Slug:** `linkedin-post-with-keyword`

**Use Cases:**
- Track market conversations about specific topics
- Monitor competitor/customer engagement on keywords
- Identify thought leaders discussing relevant topics

**Event Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `KEYWORD` | list | Keywords to track in posts. Example: `["AI infrastructure", "GPU compute"]` |
| `POST_CATEGORY` | list | Categories: `["Business", "Personal", "Events"]` |

**Account Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `COMPANY_HEADCOUNT` | list | Size filters |
</watcher>

<watcher type="market-headcount-growth">
### Company Headcount Growth (Market)

**Slug:** `company-headcount-growth`

**Use Cases:**
- Track all fast-growing companies in a market
- Identify companies scaling engineering teams
- Find expansion signals across industry

**Event Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `COMPANY_HEADCOUNT_GROWTH` | dict | Growth threshold. Example: `{"min": 30, "max": 1000}` (%) |
| `TIMEFRAME` | list | Period: `["MoM"]`, `["QoQ"]`, `["6M"]`, `["YoY"]` |

**Account Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `COMPANY_HEADCOUNT` | list | Base size filters |
| `COMPANY_INDUSTRY` | list | Industry verticals |
</watcher>

<watcher type="headcount-over-baseline">
### Company Headcount Growth Over Baseline (Market)

**Slug:** `company-headcount-growth-over-baseline`

**Use Cases:**
- Track companies exceeding normal growth patterns
- Identify unusual hiring surges
- Detect companies accelerating faster than industry average

**Event Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `GROWTH_BASELINE` | dict | Growth above baseline. Example: `{"min": 20}` (% above normal) |
| `TIMEFRAME` | list | Period: `["MoM"]`, `["QoQ"]`, `["YoY"]` |

**Account Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `COMPANY_HEADCOUNT` | list | Size filters |
| `COMPANY_INDUSTRY` | list | Industry verticals |
</watcher>

<watcher type="person-new-position">
### Person Starting New Position (Market)

**Slug:** `person-starting-new-position`

**Use Cases:**
- Track when people with target titles join new companies
- Monitor VP/C-level movements for outreach timing
- Identify new decision makers entering target accounts

**Event Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `TITLE` | list | Job titles to track. Example: `["VP Engineering", "CTO", "Head of ML"]` |
| `REGION` | list | Location filter |

**Account Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `COMPANY_HEADCOUNT` | list | Size filters |
| `COMPANY_INDUSTRY` | list | Industry verticals |

**Lead Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `SENIORITY` | list | Levels: `["C-Level", "VP", "Director", "Manager"]` |
</watcher>

<watcher type="department-headcount">
### Company Department Headcount Change (Market)

**Slug:** `company-department-headcount`

**Use Cases:**
- Track engineering team growth specifically
- Monitor sales/marketing expansion signals
- Identify companies investing in specific functions

**Event Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `DEPARTMENT` | list | Departments: `["Engineering", "Sales", "Marketing", "Product", "Operations"]` |
| `HEADCOUNT_CHANGE` | dict | Change threshold. Example: `{"min": 10}` (employees or %) |
| `TIMEFRAME` | list | Period: `["MoM"]`, `["QoQ"]`, `["YoY"]` |

**Account Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `COMPANY_HEADCOUNT` | list | Size filters |
</watcher>

<watcher type="first-hire-department">
### First Person Hired in Department (Market)

**Slug:** `first-person-hired-in-company-department`

**Use Cases:**
- Track companies starting new functions (first ML hire)
- Identify greenfield opportunities
- Catch companies early in building teams

**Event Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `DEPARTMENT` | list | Departments: `["Engineering", "Data Science", "ML/AI", "DevOps"]` |

**Account Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `COMPANY_HEADCOUNT` | list | Size filters |
| `COMPANY_INDUSTRY` | list | Industry verticals |
</watcher>

<watcher type="first-hire-international">
### First Person Hired Internationally (Market)

**Slug:** `first-person-hired-internationally`

**Use Cases:**
- Track companies expanding into new countries
- Identify international growth signals
- Catch companies as they go global

**Event Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `COUNTRY` | list | Target countries. Example: `["Germany", "UK", "India"]` |

**Account Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `COMPANY_HEADCOUNT` | list | Size filters |
| `COMPANY_HQ_COUNTRY` | list | Headquarters country |
</watcher>

<watcher type="employees-two-countries">
### Company Employees in Two Countries (Market)

**Slug:** `company-employee-job-location-in-two-countries`

**Use Cases:**
- Track companies with distributed teams
- Identify companies with global infrastructure needs
- Find companies expanding internationally

**Event Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `COUNTRY_1` | list | First country. Example: `["United States"]` |
| `COUNTRY_2` | list | Second country. Example: `["India"]` |

**Account Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `COMPANY_HEADCOUNT` | list | Size filters |
</watcher>

<watcher type="person-discovery">
### Person Discovery via Filters (Market)

**Slug:** `person-discovery-via-filters`

**Use Cases:**
- Build lead lists matching specific criteria
- Track new people appearing that match ICP
- Continuous prospecting automation

**Lead Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `TITLE` | list | Job titles. Example: `["ML Engineer", "Data Scientist"]` |
| `SENIORITY` | list | Levels: `["C-Level", "VP", "Director", "Manager", "Individual Contributor"]` |
| `REGION` | list | Location |
| `SKILLS` | list | LinkedIn skills. Example: `["PyTorch", "TensorFlow", "Kubernetes"]` |

**Account Filters:**

| Filter Type | Data Type | Description |
|-------------|-----------|-------------|
| `COMPANY_HEADCOUNT` | list | Size filters |
| `COMPANY_INDUSTRY` | list | Industry verticals |
</watcher>
</market_watchers>

<api_parameters>
## Common API Parameters

All watch creation requests share these parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `event_type_slug` | string | Yes | The watcher type slug |
| `event_filters` | array | Yes | Filters specific to the event type |
| `account_filters` | array | No | Company-level filters (where applicable) |
| `lead_filters` | array | No | Person-level filters (where applicable) |
| `notification_endpoint` | string | Yes | Webhook URL for notifications |
| `frequency` | integer | Yes | Check frequency (in hours) |
| `expiration_date` | string | Yes | When watch expires (YYYY-MM-DD) |
| `approximate_notification_time` | integer | No | Hour of day for notifications (0-23) |
| `max_notifications_per_execution` | integer | No | Limit per execution (multiple of 50) |

**Filter Structure:**
```json
{
  "filter_type": "FILTER_NAME",
  "type": "in",  // or "not_in", "between"
  "value": ["value1", "value2"]
}
```
</api_parameters>

<simulation_api>
## Simulation API (Testing)

Use simulation endpoint to test integrations without creating real watches.

**Endpoint:** `POST /watcher/simulation/watches`

**Why Use It:**
- Instantly sends sample notification to your endpoint
- No wait time (real watches can take 1+ hour)
- Perfect for integration testing

**Example:**
```bash
curl --location 'https://api.crustdata.com/watcher/simulation/watches' \
--header 'Authorization: Token $api_token' \
--header 'Content-Type: application/json' \
--data '{
    "event_type_slug": "job-posting-with-keyword-and-location",
    "event_filters": [
        {"filter_type": "TITLE", "type": "in", "value": "Software Engineer"},
        {"filter_type": "REGION", "type": "in", "value": "United States"}
    ],
    "notification_endpoint": "https://your-webhook.com/test",
    "frequency": 1,
    "expiration_date": "2026-01-01"
}'
```
</simulation_api>


