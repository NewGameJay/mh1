# Crustdata People Discovery API

<overview>
The People Discovery API (`POST /screener/persondb/search`) enables searching for professionals matching specific criteria.

**Key Feature for Decision Maker Counts:** The response includes `total_count` which returns the total number of matching people even when using `limit: 1`. This enables decision maker counting with minimal credit consumption.
</overview>

<endpoint>
## Endpoint

**URL:** `https://api.crustdata.com/screener/persondb/search`
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
        "column": "<filter_name>",
        "type": "<operator>",
        "value": "<value>"
      }
    ]
  },
  "offset": 0,
  "limit": 1,
  "sorts": [
    {
      "column": "<field>",
      "type": "asc|desc"
    }
  ]
}
```

**Key Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `filters` | object | Filter conditions with `op` (and/or) and `conditions` array |
| `limit` | integer | Number of results to return. **Use `1` for decision maker counts** |
| `offset` | integer | Pagination offset |
| `sorts` | array | Sort criteria |

**Note:** People API uses `column` instead of `filter_type` in conditions.
</request_schema>

<response_schema>
## Response Schema

```json
{
  "profiles": [
    {
      "person_id": "string",
      "full_name": "string",
      "linkedin_url": "string",
      "title": "string",
      "seniority_level": "string",
      "region": "string",
      "current_company_name": "string",
      "current_company_linkedin_url": "string",
      "skills": ["string"],
      "experience_years": 10
    }
  ],
  "next_cursor": "string",
  "total_count": 567
}
```

**Key Fields:**
| Field | Description |
|-------|-------------|
| `total_count` | **Total matching people** - use for decision maker counts |
| `profiles` | Array of person records (limited by `limit` param) |
| `next_cursor` | Pagination cursor for next page |
</response_schema>

<filters>
## Available Filters

### Seniority & Role

| Filter (column) | Operator | Value Example | Description |
|-----------------|----------|---------------|-------------|
| `current_employers.seniority_level` | `=`, `in` | `"CXO"` or `["VP", "Director"]` | Seniority level |
| `current_employers.title` | `=`, `(.)` | `"VP Engineering"` | Job title (exact or contains) |

**Seniority Levels:**
- `CXO` - C-suite (CEO, CTO, CFO, etc.)
- `VP` - Vice President
- `Director` - Director level
- `Manager` - Manager level
- `Individual Contributor` - IC roles

### Geography

| Filter (column) | Operator | Value Example | Description |
|-----------------|----------|---------------|-------------|
| `region` | `=`, `(.)` | `"San Francisco Bay Area"` | Geographic region |
| `country` | `=` | `"United States"` | Country |

### Skills & Expertise

| Filter (column) | Operator | Value Example | Description |
|-----------------|----------|---------------|-------------|
| `skills` | `(.)` | `["Python", "Machine Learning"]` | LinkedIn skills |

### Company Context

| Filter (column) | Operator | Value Example | Description |
|-----------------|----------|---------------|-------------|
| `current_employers.company_name` | `=`, `(.)` | `"Acme Corp"` | Current employer name |
| `current_employers.company_linkedin_url` | `=` | `"linkedin.com/company/acme"` | Employer LinkedIn URL |
| `current_employers.company_headcount` | `>=`, `<=` | `100` | Employer size |
| `current_employers.company_industry` | `(.)` | `["Technology"]` | Employer industry |
</filters>

<operators>
## Filter Operators

| Operator | Meaning | Use Case |
|----------|---------|----------|
| `=` | Equals | Exact match |
| `in` | In list | Multiple values |
| `>=` | Greater than or equal | Minimum threshold |
| `<=` | Less than or equal | Maximum threshold |
| `(.)` | Contains | Partial match / array contains |
</operators>

<persona_filter_mappings>
## Persona to Filter Mapping Guide

Use this to translate buyer personas into API filters:

### By Seniority Level

| Persona Type | Recommended Filters |
|--------------|---------------------|
| Decision Makers | `current_employers.seniority_level: ["CXO", "VP"]` |
| Evaluators | `current_employers.seniority_level: ["Director"]` |
| Champions | `current_employers.seniority_level: ["Manager"]` |
| End Users | `current_employers.seniority_level: ["Individual Contributor"]` |

### By Function/Department

| Department | Title Patterns |
|------------|----------------|
| Engineering | `"VP Engineering"`, `"CTO"`, `"Head of Engineering"`, `"Director Engineering"` |
| Sales | `"VP Sales"`, `"CRO"`, `"Head of Sales"`, `"Director Sales"` |
| Marketing | `"VP Marketing"`, `"CMO"`, `"Head of Marketing"`, `"Director Marketing"` |
| Product | `"VP Product"`, `"CPO"`, `"Head of Product"`, `"Director Product"` |
| Data/ML | `"Head of Data"`, `"VP Data"`, `"Director ML"`, `"Head of ML"` |

### By Technical Stack

| Stack Focus | Skills Filter |
|-------------|---------------|
| ML/AI Buyers | `skills: ["Machine Learning", "TensorFlow", "PyTorch"]` |
| DevOps Buyers | `skills: ["Kubernetes", "Docker", "AWS", "Terraform"]` |
| Data Buyers | `skills: ["Python", "SQL", "Data Engineering", "Spark"]` |
| Security Buyers | `skills: ["Security", "Compliance", "SOC 2", "GDPR"]` |
</persona_filter_mappings>

<example_queries>
## Example Queries for Common Personas

### Engineering Leaders at SaaS Companies

```json
{
  "filters": {
    "op": "and",
    "conditions": [
      {"column": "current_employers.seniority_level", "type": "in", "value": ["CXO", "VP", "Director"]},
      {"column": "current_employers.title", "type": "(.)", "value": "Engineering"},
      {"column": "current_employers.company_industry", "type": "(.)", "value": ["Software", "Technology"]},
      {"column": "region", "type": "=", "value": "San Francisco Bay Area"}
    ]
  },
  "limit": 1
}
```

### ML/AI Decision Makers

```json
{
  "filters": {
    "op": "and",
    "conditions": [
      {"column": "current_employers.seniority_level", "type": "in", "value": ["CXO", "VP"]},
      {"column": "skills", "type": "(.)", "value": ["Machine Learning", "AI", "Deep Learning"]},
      {"column": "current_employers.company_headcount", "type": ">=", "value": 50}
    ]
  },
  "limit": 1
}
```

### VPs at Fast-Growing Startups

```json
{
  "filters": {
    "op": "and",
    "conditions": [
      {"column": "current_employers.seniority_level", "type": "=", "value": "VP"},
      {"column": "current_employers.company_headcount", "type": ">=", "value": 50},
      {"column": "current_employers.company_headcount", "type": "<=", "value": 500},
      {"column": "country", "type": "=", "value": "United States"}
    ]
  },
  "limit": 1
}
```

### CTOs and Heads of Engineering

```json
{
  "filters": {
    "op": "or",
    "conditions": [
      {"column": "current_employers.title", "type": "=", "value": "CTO"},
      {"column": "current_employers.title", "type": "=", "value": "Chief Technology Officer"},
      {"column": "current_employers.title", "type": "(.)", "value": "Head of Engineering"},
      {"column": "current_employers.title", "type": "(.)", "value": "VP Engineering"}
    ]
  },
  "limit": 1
}
```
</example_queries>

<decision_maker_preview_strategy>
## Decision Maker Preview Strategy (Minimal Credits)

To get decision maker counts for proposals without burning significant credits:

1. Build filters matching the prospect's buyer personas
2. Set `limit: 1` in the request
3. Extract `total_count` from response for decision maker count
4. Use the single returned profile as a sample/proof point

**Multi-Query Strategy for Persona Breakdown:**

Run separate queries with `limit: 1` for each seniority level:
- Query 1: `seniority_level = "CXO"` → Count of C-level
- Query 2: `seniority_level = "VP"` → Count of VPs
- Query 3: `seniority_level = "Director"` → Count of Directors
- Query 4: `seniority_level = "Manager"` → Count of Managers

This gives you a breakdown like:
> **Decision Makers at Scale:**
> - 234 CXO/C-level executives
> - 1,892 VP-level buyers
> - 4,567 Director-level evaluators
> - 12,345 Manager-level champions

**Example Response with limit:1:**
```json
{
  "profiles": [
    {
      "full_name": "Jane Smith",
      "title": "VP Engineering",
      "seniority_level": "VP",
      "current_company_name": "Acme Corp",
      "region": "San Francisco Bay Area"
    }
  ],
  "total_count": 2847
}
```

This tells you: "2,847 people match this persona" while only retrieving 1 record.
</decision_maker_preview_strategy>

<combining_with_company_filters>
## Combining with Company Context

To find decision makers at companies matching a specific ICP, layer company filters:

```json
{
  "filters": {
    "op": "and",
    "conditions": [
      {"column": "current_employers.seniority_level", "type": "in", "value": ["VP", "Director"]},
      {"column": "current_employers.title", "type": "(.)", "value": "Engineering"},
      {"column": "current_employers.company_industry", "type": "(.)", "value": ["Software"]},
      {"column": "current_employers.company_headcount", "type": ">=", "value": 50},
      {"column": "current_employers.company_headcount", "type": "<=", "value": 500}
    ]
  },
  "limit": 1
}
```

This finds: "Engineering leaders at software companies with 50-500 employees"
</combining_with_company_filters>


# People API - Complete Documentation
This document contains the complete documentation for all endpoints in the People API section.
Generated by combining 6 individual endpoint documentation files.

---

<!-- Error loading /docs/discover/people-apis/people-api-migration-guide -->

# Comprehensive API Documentation: people-discovery-api-in-db

## 📋 Documentation Metadata

- **API Path:** `POST /screener/persondb/search`
- **Category:** People API
- **Operation:** db
- **Documentation File:** people-discovery-api-in-db.md
- **Main Documentation:** discover/people-apis/people-discovery-api-in-db.md
- **Generated:** 2025-11-27T14:03:48.597Z

---

## 📖 Original Documentation

# In-DB: People Search API 

### [ 🚀 Try Now ](/api#tag/people-api/post/screener/persondb/search)

Search and filter people based on various professional criteria.

## Endpoint

```
POST /screener/persondb/search
```

## Data Dictionary

[Explore the complete data dictionary for this endpoint here](/docs/dictionary/people-discovery)

## Request Parameters

| **Payload Keys** | **Description**                                                                                      | **Required** |
| ------------- | ---------------------------------------------------------------------------------------------------- | ------------ |
| `filters`     | An object containing the filter conditions. See the Building Complex Filters section below for details.                                                          | Yes         |
| `cursor`      | Pagination cursor from previous response. Used for fetching the next page of results.                 | No          |
| `limit`       | The number of results to return in a single request. Default value is `20`. Maximum is `1,000`.      | No          |
| `post_processing` | Extra filtering rules applied to the search query. See Post-processing options below.             | No          |
| `preview` | [**Access controlled**] <br/>Provides basic profile details lookup. Default is `false` | No          |

## Credit Usage

- **People Discovery**: 3 credit per 100 results returned
- **Preview Mode**: 0 credits when `preview=true` is used
- **No Results, No Charges**: You are never charged credits when our APIs return no results. Credits are only deducted when data is successfully returned from your API requests.

## Finding Valid Filter Values with Autocomplete

Use the **[PersonDB Autocomplete API](/docs/discover/auxiliary-apis/persondb-autocomplete)** to find exact field values for your search filters. This dedicated autocomplete endpoint helps you discover what values exist in our database.

### 🔍 When to Use PersonDB Autocomplete API

**Use Case 1: Discover Valid Field Values**
- Get possible values for any field returned by the PersonDB search endpoint
- Convert partial or fuzzy text into matching value stored in our data for a field

**Use Case 2: Build Dynamic Search Interfaces**  
- Power autocomplete dropdowns and search suggestions in your UI
- Create responsive search experiences with accurate field matching

### Quick Example: Finding Region Values

#### Step 1: Get region suggestions
```bash
curl -X POST 'https://api.crustdata.com/screener/persondb/autocomplete' \
--header 'Authorization: Token $authToken' \
--header 'Content-Type: application/json' \
--data '{
    "field": "region",
    "query": "san franci",
    "limit": 5
}'
```

#### Step 2: Use exact value in your search
```bash
curl -X POST 'https://api.crustdata.com/screener/persondb/search' \
--header 'Authorization: Token $authToken' \
--header 'Content-Type: application/json' \
--data '{
    "filters": {
        "filter_type": "region",
        "type": "=",
        "value": "San Francisco"
    }
}'
```

**💡 Tip**: The autocomplete API works with **any field** from the [data dictionary](/docs/dictionary/people-discovery)

## Filter Operators

### Matching Operators
| **Operator** | **Description** | **Example** | **Field Types** |
| ------------ | --------------- | ----------- | --------------- |
| `=` | Exact match | `{"type": "=", "value": "CEO"}` | All |
| `!=` | Not equal to | `{"type": "!=", "value": "Intern"}` | All |
| `in` | Matches any value in list | `{"type": "in", "value": ["CEO", "CTO", "CFO"]}` | All |
| `not_in` | Doesn't match any value in list | `{"type": "not_in", "value": ["Intern", "Junior"]}` | All |

:::note Case Sensitivity
The `=` operator performs **case-insensitive** matching for text fields (e.g., searching for "CEO" will match "ceo", "Ceo", or "CEO"). 

The `IN` operator performs **exact, case-sensitive** matching. When using `IN`, ensure your values match the exact casing in the data.
:::

:::tip Getting Exact Values for Filters
For best results with `=` and `in` operators, use the [PersonDB Autocomplete API](/docs/discover/auxiliary-apis/persondb-autocomplete) to get exact field values. This is especially useful for fields like:
- `region` - Get exact location names
- `current_employers.name` - Get exact company names  
- `education_background.institute_name` - Get exact institution names
- `current_employers.title` - Get standardized job titles
- And many other text fields

**Example workflow:**
1. Call autocomplete API: `POST /screener/persondb/autocomplete` with `{"field": "region", "query": "san francisco"}`
2. Get exact value: `"San Francisco Bay Area"`
3. Use in filter: `{"column": "region", "type": "=", "value": "San Francisco Bay Area"}`
:::

### Comparison Operators
| **Operator** | **Description** | **Example** | **Field Types** |
| ------------ | --------------- | ----------- | --------------- |
| `>` | Greater than | `{"type": ">", "value": 5}` | Number, Date |
| `<` | Less than | `{"type": "<", "value": 100}` | Number, Date |
| `=>` | Greater than or equal | `{"type": "=>", "value": 10}` | Number, Date |
| `=<` | Less than or equal | `{"type": "=<", "value": 50}` | Number, Date |

### Text Search Operators
| **Operator** | **Description** | **Example** | **Field Types** |
| ------------ | --------------- | ----------- | --------------- |
| `(.)` | Text search with fuzzy matching (allows typos) | `{"type": "(.)", "value": "engineer"}` | Text |
| `[.]` | Exact token matching (no typos allowed) | `{"type": "[.]", "value": "Software Engineer"}` | Text |

:::tip Text Search Operators Best Practices
**Understanding the difference between `(.)` and `[.]`:**

- **`(.)` Fuzzy matching**: 
  - Allows typos and word edits (fuzzy matching)
  - Doesn't strictly respect word order
  - Multi-word searches: Each word is searched independently (all must be present but in any order)
  - Example: "Software Engineer" may match "Engineer Software" or "Sr Software Engineer"
  
- **`[.]` Exact token matching**: 
  - No typos allowed, requires exact tokens

**When to use which:**
- Use `(.)` for flexible searching when you want to find variations and don't mind typos
- Use `[.]` when you need exact matches without any variations (useful for specific titles, names, or technical terms)
- Prefer `(.)` over `IN` or `=` unless you have exact values from the [PersonDB Autocomplete API](/docs/discover/auxiliary-apis/persondb-autocomplete)
:::

:::info Usage Notes
- **Text fields**: Prefer the fuzzy operator `(.)` for partial matches with automatic typo handling. Use exact match (`=`) or `IN` only when you have exact values from the [PersonDB Autocomplete API](/docs/discover/auxiliary-apis/persondb-autocomplete)
- **Numeric fields**: All operators work with numeric values like `years_of_experience_raw`, `num_of_connections`
- **Date fields**: Comparison operators work with ISO date strings like `"2024-01-01"`. Note that date fields will only appear in the response if they exist in the data
- **Boolean fields**: Use `=` with `true` or `false` values
:::

## Location Filtering

### How It Works

When you filter by location fields, the API automatically searches across both:
1. **Main location field** - The complete location string (e.g., "San Francisco Bay Area")
2. **Address components field** - Individual location hierarchy components (city, state, country)

This dual-search approach ensures you can find matches regardless of how locations are formatted in the data.

### Supported Location Fields

The following fields support automatic address component searching:
- `region` → automatically searches both `region` and `region_address_components`
- `current_employers.company_hq_location` → automatically includes address components
- `past_employers.company_hq_location` → automatically includes address components
- `all_employers.company_hq_location` → automatically includes address components

### Example

When you search for "California", the API automatically searches for matches in both the full location string and address components:
```json
{
  "column": "region",
  "type": "(.)",
  "value": "California"
}
```

This will match profiles with:
- Full location: "San Francisco Bay Area, California, United States"
- Address components containing: "California"

**Note:** This automatic expansion applies to ALL filter operators (=, !=, in, not_in, (.), [.]), not just fuzzy search. You don't need to explicitly filter on the address_components fields - the API handles this automatically for better matching.

## Post-processing Options

Additional filtering options that are applied to your search query:

| **Key** | **Type** | **Description** | **Example** |
| ------- | -------- | --------------- | ----------- |
| `exclude_profiles` | array | List of LinkedIn profile URLs to exclude from results. <br/> <br/>  **Maximum: 50,000 profiles per request** <br/> **Request size limit: 10MB total payload** <br/> <br/>  **Note: Profile URLs must be in the format `https://www.linkedin.com/in/{slug}` for post-processing to work correctly.** | `["https://www.linkedin.com/in/john-doe"]` |
| `exclude_names` | array | List of names to exclude from results | `["Test User", "Demo Account"]` |

:::warning Exclusion Limits
- **Maximum exclusions**: 50,000 profile URLs per request
- **Payload size**: Total request size must be under 10MB
- **Performance**: Response time increases with exclusion list size. For optimal performance, keep exclusions under 10,000 profiles.
- **URL format**: Profile URLs must start with "https://www.linkedin.com" or "https://linkedin.com" (missing www or https may not give expected results)
:::

:::tip Managing Large Exclusion Lists
If you need to exclude more than 50,000 profiles or maintain persistent exclusion state across multiple searches, consider implementing your own filtering logic on the client side after receiving the API response.
:::

:::tip Response Format Migration
**Migrating from Realtime to In-DB API?** See our [**API Migration Guide**](/docs/discover/people-apis/people-api-migration-guide) to transform In-DB response structure to Realtime format.
:::

## Building Complex Filters

### Basic Filter Structure

Each filter condition requires three components:
- `column`: The field to filter on (e.g., "current_employers.title")
- `type`: The operator to use (e.g., "=", "in", "(.)")
- `value`: The value(s) to match

```json
{
    "column": "current_employers.title",
    "type": "=",
    "value": "Software Engineer"
}
```

### Combining Multiple Conditions

Use `op` with "and" or "or" to combine multiple filter conditions:

```json
{
    "op": "and",
    "conditions": [
        {
            "column": "region",
            "type": "=",
            "value": "San Francisco Bay Area"
        },
        {
            "column": "years_of_experience_raw",
            "type": ">",
            "value": 5
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
            "column": "current_employers.company_industries",
            "type": "in",
            "value": ["Technology", "Software"]
        },
        {
            "op": "or",
            "conditions": [
                {
                    "column": "current_employers.title",
                    "type": "(.)"  ,
                    "value": "engineer"
                },
                {
                    "column": "current_employers.title",
                    "type": "(.)"  ,
                    "value": "developer"
                }
            ]
        }
    ]
}
```

:::warning Important: AND Operator with Nested Fields
When using AND with nested array fields (like honors, employers, education), ALL conditions must match within the SAME array object.

**Example:** 
- `current_employers.title = "Software Engineer" AND current_employers.name = "Capital One"` 
  - ✅ Matches if a SINGLE employment object has both title="Software Engineer" AND company name="Capital One"
  - ❌ Does NOT match if "Software Engineer" is at one company and "Capital One" is a different employment entry

**For matching across different objects, use OR:**
- `current_employers.title = "Software Engineer" OR current_employers.name = "Capital One"`
  - ✅ Matches if ANY employment has title="Software Engineer" OR ANY employment has company name="Capital One"
:::

### Querying Multiple Employers with AND Conditions

<details id="querying-multiple-employers-with-and-conditions">
<summary><strong>Click to expand: How to query for people who worked at multiple companies</strong></summary>

When querying for people who have worked at multiple specific companies (across different employment records), you need to use a **nested AND structure** where each employer condition is wrapped in its own AND group.

:::danger Common Mistake
**❌ INCORRECT - This returns 0 results:**
```json
{
  "op": "and",
  "conditions": [
    {
      "column": "all_employers.name",
      "type": "[.]",
      "value": "Hyperscan"
    },
    {
      "column": "all_employers.name",
      "type": "[.]",
      "value": "Antler"
    }
  ]
}
```
This fails because it's trying to find a SINGLE employment record with both "Hyperscan" AND "Antler" as the company name, which is impossible.
:::

:::tip ✅ CORRECT Syntax
**Each employer must be in its own nested AND condition:**
```json
{
  "op": "and",
  "conditions": [
    {
      "op": "and",
      "conditions": [
        {
          "column": "all_employers.name",
          "type": "[.]",
          "value": "Hyperscan"
        }
      ]
    },
    {
      "op": "and",
      "conditions": [
        {
          "column": "all_employers.name",
          "type": "[.]",
          "value": "Antler"
        }
      ]
    }
  ]
}
```
This correctly finds people who have "Hyperscan" in ONE employment record AND "Antler" in ANOTHER employment record.
:::

#### Why is the nested structure required?

When you filter on array fields like `all_employers`, the API evaluates each array element independently. The nested structure ensures that:
1. Each inner AND group is evaluated against separate array elements
2. The outer AND combines the results, finding people who match ALL the employer criteria across their employment history
3. Without nesting, the API tries to match all conditions within a single array element, which fails for multiple distinct employer names

#### Complete Example: People who worked at both Hyperscan and Antler

```bash
curl 'https://api.crustdata.com/screener/persondb/search' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Token $token' \
  --data '{
  "filters": {
    "op": "and",
    "conditions": [
      {
        "op": "and",
        "conditions": [
          {
            "column": "all_employers.name",
            "type": "[.]",
            "value": "Hyperscan"
          }
        ]
      },
      {
        "op": "and",
        "conditions": [
          {
            "column": "all_employers.name",
            "type": "[.]",
            "value": "Antler"
          }
        ]
      }
    ]
  },
  "limit": 100
}'
```

#### Adding additional filters with multiple employers

You can combine multiple employer queries with other filters at the same level:

```bash
curl 'https://api.crustdata.com/screener/persondb/search' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Token $token' \
  --data '{
  "filters": {
    "op": "and",
    "conditions": [
      {
        "op": "and",
        "conditions": [
          {
            "column": "all_employers.name",
            "type": "[.]",
            "value": "Hyperscan"
          }
        ]
      },
      {
        "op": "and",
        "conditions": [
          {
            "column": "all_employers.name",
            "type": "[.]",
            "value": "Antler"
          },
          {
            "column": "first_name",
            "type": "=",
            "value": "Roberts"
          }
        ]
      }
    ]
  },
  "limit": 100
}'
```

This query finds people who:
- Have worked at "Hyperscan" (in any employment record)
- AND have worked at "Antler" (in a different employment record), and the person's first name is "Roberts"

:::info Key Takeaway
When querying for multiple distinct values in array fields (like different company names in `all_employers`), always use nested AND conditions to ensure each value is matched against separate array elements.
:::

</details>

## Example Requests

<details>
<summary>1. Basic filter examples</summary>

### 1. Basic filter examples

Find people by exact title match:

```bash
curl 'https://api.crustdata.com/screener/persondb/search/' \
-H "Authorization: Token $auth_token" \
-H "Accept: application/json, text/plain, */*" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "column": "current_employers.title",
        "type": "=",
        "value": "Chief Executive Officer"
    },
    "limit": 100
}' \
--compressed
```

Find people whose headline contains "founder" (text search with fuzzy matching):

```bash
curl 'https://api.crustdata.com/screener/persondb/search/' \
-H "Authorization: Token $auth_token" \
-H "Accept: application/json, text/plain, */*" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "column": "headline",
        "type": "(.)",
        "value": "founder"
    },
    "limit": 100
}' \
--compressed
```

Find people with more than 10 years of experience:

```bash
curl 'https://api.crustdata.com/screener/persondb/search/' \
-H "Authorization: Token $auth_token" \
-H "Accept: application/json, text/plain, */*" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "column": "years_of_experience_raw",
        "type": ">",
        "value": 10
    },
    "limit": 100
}' \
--compressed
```
</details>

<details>
<summary>2. Filter with comparison operators</summary>

### 2. Filter with comparison operators

Find people with significant LinkedIn connections:

```bash
curl 'https://api.crustdata.com/screener/persondb/search/' \
-H "Authorization: Token $auth_token" \
-H "Accept: application/json, text/plain, */*" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "op": "and",
        "conditions": [
            {
                "column": "num_of_connections",
                "type": ">",
                "value": 500
            },
            {
                "column": "recently_changed_jobs",
                "type": "=",
                "value": true
            }
        ]
    },
    "limit": 50
}' \
--compressed
```
</details>

<details>
<summary>3. Filter with NOT operators</summary>

### 3. Filter with NOT operators

Find professionals excluding certain companies and titles:

```bash
curl 'https://api.crustdata.com/screener/persondb/search/' \
-H "Authorization: Token $auth_token" \
-H "Accept: application/json, text/plain, */*" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "op": "and",
        "conditions": [
            {
                "column": "current_employers.name",
                "type": "not_in",
                "value": ["Google", "Meta", "Amazon"]
            },
            {
                "column": "current_employers.title",
                "type": "!=",
                "value": "Intern"
            },
            {
                "column": "region",
                "type": "=",
                "value": "San Francisco Bay Area"
            }
        ]
    },
    "limit": 100
}' \
--compressed
```
</details>

<details>
<summary>4. Complex nested filter example</summary>

### 4. Complex nested filter example

Find senior professionals with specific criteria:

```bash
curl 'https://api.crustdata.com/screener/persondb/search/' \
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
                        "column": "current_employers.title",
                        "type": "(.)"  ,
                        "value": "VP"
                    },
                    {
                        "column": "current_employers.title",
                        "type": "(.)"  ,
                        "value": "Director"
                    },
                    {
                        "column": "current_employers.seniority_level",
                        "type": "=",
                        "value": "CXO"
                    }
                ]
            },
            {
                "column": "years_of_experience_raw",
                "type": "=>",
                "value": 10
            },
            {
                "column": "current_employers.company_headcount_latest",
                "type": "<",
                "value": 1000
            }
        ]
    },
    "limit": 50
}' \
--compressed
```
</details>

<details>
<summary>5. Filter by date ranges</summary>

### 5. Filter by date ranges

Find people who started their current position recently:

```bash
curl 'https://api.crustdata.com/screener/persondb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "op": "and",
        "conditions": [
            {
                "column": "current_employers.start_date",
                "type": "=>",
                "value": "2023-01-01"
            },
            {
                "column": "current_employers.company_type",
                "type": "=",
                "value": "Public Company"
            },
            {
                "column": "years_of_experience_raw",
                "type": "=<",
                "value": 15
            }
        ]
    },
    "limit": 50
}' \
--compressed
```
</details>

<details>
<summary>6. Filter by education and skills</summary>

### 6. Filter by education and skills

Find alumni with specific skills:

```bash
curl 'https://api.crustdata.com/screener/persondb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "op": "and",
        "conditions": [
            {
                "column": "education_background.institute_name",
                "type": "(.)"  ,
                "value": "Stanford"
            },
            {
                "column": "education_background.degree_name",
                "type": "!=",
                "value": "Bachelor"
            },
            {
                "column": "skills",
                "type": "(.)"  ,
                "value": "machine learning"
            }
        ]
    },
    "limit": 100
}' \
--compressed
```
</details>

<details>
<summary>7. Filter by certifications and honors</summary>

### 7. Filter by certifications and honors

Find certified professionals with recognition:

```bash
curl 'https://api.crustdata.com/screener/persondb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "op": "and",
        "conditions": [
            {
                "column": "certifications.name",
                "type": "(.)"  ,
                "value": "AWS"
            },
            {
                "column": "certifications.issued_date",
                "type": "=>",
                "value": "2022-01-01"
            },
            {
                "column": "honors.title",
                "type": "(.)"  ,
                "value": "award"
            }
        ]
    },
    "limit": 50
}' \
--compressed
```
</details>

<details>
<summary>8. Filter across all employment history</summary>

### 8. Filter across all employment history

Find people with experience at specific companies (past or present):

```bash
curl 'https://api.crustdata.com/screener/persondb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "op": "and",
        "conditions": [
            {
                "column": "all_employers.name",
                "type": "in",
                "value": ["Google", "Facebook", "Apple", "Amazon"]
            },
            {
                "column": "all_employers.years_at_company_raw",
                "type": "=>",
                "value": 2
            },
            {
                "column": "current_employers.company_headcount_range",
                "type": "!=",
                "value": "10,001+"
            }
        ]
    },
    "limit": 50
}' \
--compressed
```
</details>

<details>
<summary>9. Find people at a company by LinkedIn URL</summary>

### 9. Find people at a company by LinkedIn URL

Find all people currently working at a company using its LinkedIn profile URL:

```bash
curl 'https://api.crustdata.com/screener/persondb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "column": "current_employers.company_linkedin_profile_url",
        "type": "=",
        "value": "https://www.linkedin.com/company/tesla-motors"
    },
    "limit": 100
}' \
--compressed
```

Alternatively, you can use the LinkedIn ID:

```bash
curl 'https://api.crustdata.com/screener/persondb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "column": "current_employers.linkedin_id",
        "type": "=",
        "value": "1441"
    },
    "limit": 100
}' \
--compressed
```

Note: The LinkedIn ID is the numeric identifier from the company's LinkedIn URL. For example, if the LinkedIn URL is `https://www.linkedin.com/company/1441/`, the LinkedIn ID is `1441`.

**How to get the LinkedIn ID or URL:** You can use the free [Company Identification API](/docs/discover/company-apis/company-identification-api) to get a company's `linkedin_id` and `linkedin_url` by providing its website domain:
- Example input: `query_company_website`: `"tesla.com"` or `query_company_linkedin_url`: `"https://www.linkedin.com/company/tesla-motors"`
- Example output: `linkedin_id`: `"15564"` (Tesla's LinkedIn ID), `linkedin_url`: `"https://www.linkedin.com/company/tesla-motors"`

You can also filter by past employers or all employers:

```bash
# Find people who previously worked at a company using LinkedIn URL
curl 'https://api.crustdata.com/screener/persondb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "column": "past_employers.company_linkedin_profile_url",
        "type": "=",
        "value": "https://www.linkedin.com/company/tesla-motors"
    },
    "limit": 100
}' \
--compressed
```

```bash
# Find people who previously worked at a company using LinkedIn ID
curl 'https://api.crustdata.com/screener/persondb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "column": "past_employers.linkedin_id",
        "type": "=",
        "value": "1441"
    },
    "limit": 100
}' \
--compressed
```
</details>

<details>
<summary>10. Find people at a company by domain</summary>

### 10. Find people at a company by domain

Find all people currently working at companies with a specific website domain.

**Example values:**
- `company_website_domain`: `"tesla.com"`, `"apple.com"`, `"google.com"`, `"microsoft.com"`

You can obtain a company's website domain from their LinkedIn ID using the free [Company Identification API](/docs/discover/company-apis/company-identification-api):

```bash
curl 'https://api.crustdata.com/screener/persondb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "column": "current_employers.company_website_domain",
        "type": "=",
        "value": "tesla.com"
    },
    "limit": 100
}' \
--compressed
```

Find people at multiple companies by their domains:

```bash
curl 'https://api.crustdata.com/screener/persondb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "column": "current_employers.company_website_domain",
        "type": "in",
        "value": ["tesla.com", "spacex.com", "neuralink.com"]
    },
    "limit": 100
}' \
--compressed
```

You can also combine domain search with other filters:

```bash
# Find senior executives at a company by domain
curl 'https://api.crustdata.com/screener/persondb/search/' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "op": "and",
        "conditions": [
            {
                "column": "current_employers.company_website_domain",
                "type": "=",
                "value": "apple.com"
            },
            {
                "column": "current_employers.seniority_level",
                "type": "in",
                "value": ["CXO", "Vice President", "Director"]
            }
        ]
    },
    "limit": 100
}' \
--compressed
```

</details>

<details>
<summary>11. Using post-processing to exclude specific profiles and names</summary>

### 11. Using post-processing to exclude specific profiles and names

Find senior executives excluding specific people:

```bash
curl 'https://api.crustdata.com/screener/persondb/search' \
-H "Authorization: Token $auth_token" \
-H 'Content-Type: application/json' \
--data-raw '{
    "filters": {
        "column": "current_employers.seniority_level",
        "type": "in",
        "value": ["CXO", "Vice President", "Director"]
    },
    "limit": 100,
    "post_processing": {
        "exclude_profiles": [
            "https://linkedin.com/in/john-doe",
            "https://linkedin.com/in/jane-smith"
        ],
        "exclude_names": [
            "Test User",
            "Demo Account"
        ]
    }
}' \
--compressed
```
</details>

<details>
<summary>12. Excluding senior executives with not_in</summary>

### 12. Excluding Senior Executives with `not_in`

To find individual contributors and exclude anyone who has held executive positions:

```bash
curl 'https://api.crustdata.com/screener/persondb/search' \
  -H 'Authorization: Token $auth_token' \
  -H 'Content-Type: application/json' \
  --data '{
    "filter": {
      "op": "and",
      "conditions": [
        {
          "column": "all_employers.seniority_level",
          "type": "not_in",
          "value": ["Owner / Partner", "CXO", "Vice President", "Director"]
        },
        {
          "column": "all_employers.title",
          "type": "not_in",
          "value": ["CEO", "President", "Chairman", "Founder", "Co-Founder"]
        }
      ]
    },
    "limit": 100
  }' \
--compressed
```

This will exclude anyone who:
- Currently has or previously had a seniority level of VP or above AND
- Ever held a title like CEO, President, Chairman, Founder, or Co-Founder

:::info How `not_in` Works with Employment History
When using `not_in` on employment history fields (like `all_employers.title` or `all_employers.company_name`), the filter excludes profiles where the person has **ever** held that title or worked at that company at any point in their career.
:::
</details>

<details>
<summary>13. Excluding specific companies with not_in</summary>

### 13. Excluding Specific Companies with `not_in`

To find people who have never worked at certain competitors:

```bash
curl 'https://api.crustdata.com/screener/persondb/search' \
  -H 'Authorization: Token $auth_token' \
  -H 'Content-Type: application/json' \
  --data '{
    "filter": {
      "op": "and",
      "conditions": [
        {
          "column": "all_employers.company_name",
          "type": "not_in",
          "value": ["Google", "Meta"]
        }
      ]
    },
    "limit": 100
  }' \
--compressed
```

This excludes anyone who currently works at Google/Meta OR has ever worked at Google/Meta in the past.

**Note:** Use exact company names as they appear in LinkedIn profiles for best results.
</details>

## Example Response
<details id="1-response-when-profiles-are-in-database">
<summary>1. CEO's in companies located in New York</summary>

[View example response](/examples/people-search/persondb-ceo.json)
</details>

<details id="2-response-preview">
<summary>2. Response with `preview=true`</summary>

[View example response](//examples/people-search/persondb-preview.json)
</details>

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
3. **End of Results**: When no more results exist, the next request returns an empty `profiles` array

:::info Important
- The cursor is tied to your specific query (filters + sorts). Using a cursor with different query parameters will return an error.
- Cursors should be treated as opaque strings and not modified.
:::

<details>
<summary>Paginating through results</summary>

```bash
# First page (people 1-100)
curl 'https://api.crustdata.com/screener/persondb/search/' \
-H "Authorization: Token $auth_token" \
--data-raw '{
    "filters": { ... },
    "limit": 100
}'
# Response: { "profiles": [...], "next_cursor": "eJx1jjEOwjAMRe...", "total_count": 250 }

# Second page (people 101-200)
curl 'https://api.crustdata.com/screener/persondb/search/' \
-H "Authorization: Token $auth_token" \
--data-raw '{
    "filters": { ... },
    "limit": 100,
    "cursor": "eJx1jjEOwjAMRe..."
}'
# Response: { "profiles": [...], "next_cursor": "eJx2kLEOwjAMRe...", "total_count": 250 }

# Eventually, when no more results:
# Response: { "profiles": [], "total_count": 250 }
```
</details>

**Best Practices:**
- Use consistent filters across all pagination requests
- Check if `profiles` array is empty to determine end of results
- Store the cursor if you need to resume pagination later

## Best Practices

1. **Use specific filters** to reduce result set size and improve performance
2. **Combine multiple criteria** for more targeted searches
3. **Use pagination** for large result sets
4. **Cache results** when appropriate to reduce API calls

## Common Use Cases

1. **Executive Search**: Filter by `seniority_level` and `current_title`
2. **Industry Experts**: Combine `industry`, `years_of_experience`, and `skills`
3. **Alumni Networks**: Use `school` filter with company or location filters
4. **Job Function Analysis**: Filter by `function` and `company_type`
5. **Geographic Talent Pool**: Use `region` with experience or skill filters
6. **Excluding Senior Roles**: Use `not_in` with `all_employers.seniority_level` and `all_employers.title` (see Example 12)
7. **Competitor Analysis**: Use `not_in` with `all_employers.company_name` to exclude specific companies (see Example 13)

## Rate Limits and Performance

- **Rate limit**: 60 requests per minute (RPM)
- **Maximum profiles per response**: 1,000 profiles per request
- **Maximum exclusions**: 50,000 profiles in `post_processing.exclude_profiles`
- **Request payload limit**: 10MB total request size
- **Performance tip**: Use specific filters to improve response time. Exclusion lists over 10,000 profiles may increase response time significantly.

---

## 🔧 OpenAPI Specification

# People Discovery API (In-DB)

**Category:** People API
**Base URL:** https://api.crustdata.com
**Official Docs:** /docs/discover/people-apis/people-discovery-api-in-db

**Endpoint:** `POST /screener/persondb/search`

**Description:** In-database search API for people data, enabling you to search across millions of 
professional profiles with advanced filtering capabilities.
> [Show Docs](/docs/discover/people-apis/people-discovery-api-in-db)

## Authentication
This endpoint requires a Bearer token in the `Authorization` header:

```
Authorization: Token <YOUR_TOKEN>
```
## Request Body Schema

| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `filters` | string | Yes | Filter conditions for searching people. Can be a simple condition or complex nested conditions with AND/OR logic. |  |  |
| `cursor` | string | No | Pagination cursor from previous response. Used for fetching the next page of results. |  |  |
| `limit` | integer | No | The number of results to return in a single request. Default value is 20. Maximum is 1,000. |  |  |
| `post_processing` | object | No | Additional filtering options applied to search results. |  |  |

## Example Request

```bash
curl -X POST "https://api.crustdata.com/screener/persondb/search" \
  -H "Authorization: Token &lt;YOUR_TOKEN&gt;" \
  -H "Content-Type: application/json" \
  -d '
    {
      "filters": {
        "op": "and",
        "conditions": [
          {
            "column": "current_employers.seniority_level",
            "type": "=",
            "value": "CXO"
          },
          {
            "column": "region",
            "type": "=",
            "value": "San Francisco Bay Area"
          }
        ]
      },
      "limit": 100
    }
  '
```

## Rate Limiting
All Crustdata API requests count toward your per-minute quota. Inspect the response headers `X-RateLimit-Limit` and `X-RateLimit-Remaining` to monitor usage. Implement exponential back-off or retries when you receive a **429 Too Many Requests** response.

## Responses
### Status 200
**Description:** A JSON response containing a list of people profiles with pagination support.
**Response Schema:**
| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `profiles` | array | Yes | Array of person profiles matching the search criteria |  |  |
| `next_cursor` | string | No | Cursor for fetching the next page of results |  |  |
| `total_count` | integer | Yes | Total number of profiles matching the search criteria |  |  |

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
  PersonDBSearchResponse:
    type: object
    properties:
      profiles:
        type: array
        description: "Array of person profiles matching the search criteria"
      next_cursor:
        type: string
        description: "Cursor for fetching the next page of results"
      total_count:
        type: integer
        description: "Total number of profiles matching the search criteria"

  PersonDBSearchRequest:
    type: object
    properties:
      filters:
        type: string
        description: "Filter conditions for searching people. Can be a simple condition or complex nested conditions with AND/OR logic."
      cursor:
        type: string
        description: "Pagination cursor from previous response. Used for fetching the next page of results."
      limit:
        type: integer
        description: "The number of results to return in a single request. Default value is 20. Maximum is 1,000."
      post_processing:
        type: object
        description: "Additional filtering options applied to search results."

  PersonDBCondition:
    type: object
    description: "Basic filter condition for PersonDB search"
    properties:
      column:
        type: string
        description: "The field to filter on (e.g., \"current_employers.title\", \"region\", \"skills\")"
      type:
        type: string
        description: "The operator to use for comparison. Use (.) for fuzzy text matching."
      value:
        type: string
        description: "The value(s) to match against"

  PersonDBConditionGroup:
    type: object
    description: "Complex filter group for PersonDB search with AND/OR logic"
    properties:
      op:
        type: string
        description: "Logical operator to combine conditions"
      conditions:
        type: array
        description: "Array of conditions to combine"

  PersonDBProfile:
    type: object
    description: "Comprehensive professional profile from PersonDB"
    properties:
      person_id:
        type: integer
        description: "Unique identifier for the person"
      name:
        type: string
        description: "Full name of the person"
      first_name:
        type: string
        description: "First name"
      last_name:
        type: string
        description: "Last name"
      region:
        type: string
        description: "Current location/region"
      # ... (23 more properties)

```

---

# Comprehensive API Documentation: people-enrichment-api

## 📋 Documentation Metadata

- **API Path:** `GET /screener/person/enrich`
- **Category:** People API
- **Operation:** api
- **Documentation File:** people-enrichment-api.md
- **Data Dictionary:** people-enrichment.md
- **Main Documentation:** discover/people-apis/people-enrichment-api.md
- **Generated:** 2025-11-27T14:03:48.593Z

---

## 📖 Original Documentation

# People Enrichment API

### [ 🚀 Try Now ](/api#tag/people-api/get/screener/person/enrich)

This API allows you to retrieve enriched data for one or more LinkedIn profiles in a single request.

## Endpoint

```
GET /screener/person/enrich
```

## Data Dictionary

[People Enrichment API Data Dictionary](/docs/dictionary/people-enrichment)

## Request Parameters

| Parameter | Type | Required | Default | Description | Example|
|-----------|------|-------|---------|-------------------| -----|
| `linkedin_profile_url` | string | Yes | — | Comma-separated list of LinkedIn profile URLs (25 max limit) of the person to enrich | `https://www.linkedin.com/in/dvdhsu/`,<br></br>`https://www.linkedin.com/in/jonnilundy/` |
| `enrich_realtime` | boolean | No | `false` | Whether to enrich the profile in real-time | `true` |
| `business_email` | string | No | — | Business email of the person to enrich | `abhilash@crustdata.com` |
| `fields` | string | No | - | Specify the fields to include in the response | `all_degrees,education_background` |
| `preview` | boolean | No | `false` | [**Access controlled**] <br/>Provides basic profile details lookup | `true` |

<details id="mapping-multiple-profiles">
<summary><strong>Mapping Multiple LinkedIn URLs to Response Objects</strong></summary>

When providing multiple LinkedIn URLs, each response object includes a **`query_linkedin_profile_urn_or_slug`** field containing the profile slug (the part after `/in/` in the URL) to identify which input URL it corresponds to.

**Example:** Request `linkedin_profile_url=https://www.linkedin.com/in/siqic,https://www.linkedin.com/in/neelesh-soni` returns:
```json
[
  {"name": "Siqi Chen", "query_linkedin_profile_urn_or_slug": ["siqic"]},
  {"name": "Neelesh Soni", "query_linkedin_profile_urn_or_slug": ["neelesh-soni"]}
]
```

</details>

#### Key Features
- Latency
    - **Database Search:** Less than **10 seconds** per profile.
    - **Real-Time Search:** May take longer due to fetching data from the web.
    
- Limits
    
    - **Profiles/Emails per Request:** Up to **25**.
    - **Exceeding Limits:** Requests exceeding this limit will be rejected with an error message.
- Constraints
    - **Valid Input:** Ensure all LinkedIn URLs and email addresses are correctly formatted.
        - Invalid inputs result in validation errors.
    - **Mutually Exclusive Parameters:** Do not include both linkedin_profile_url and business_email in the same request.
    - **Independent Processing:** Each profile or email is processed independently.
        - Found entries are returned immediately
        - Not found entries trigger the enrichment process (if enrich_realtime=False)

:::info
##### Business Email Enrichment 
    
    - **Discovery:** Discover business email addresses of professionals based on their LinkedIn profiles.
    - **Implementation:** To enable, include `business_email` in the `fields` parameter:
      ```
      GET /screener/person/enrich?linkedin_profile_url=https://www.linkedin.com/in/example&fields=business_email
      ```
:::

## Credit Usage
- **Database Enrichment:**
        - **3 credits** per LinkedIn profile or email.
- **Real-Time Enrichment (enrich_realtime=True):**
    - **5 credits** per LinkedIn profile or email.
- **Email Enrichment:**
    - **2 additional credits** when requesting business email
- **Preview Mode:**
    - **0 credits** when `preview=true` is used
- **No Results, No Charges**: You are never charged credits when our APIs return no results. Credits are only deducted when data is successfully returned from your API requests.

## Example Requests

<details id="1-get-all-fields-example">
<summary>1. Get all fields example</summary>

### 1. Get all fields example
- Usecase: Retrieve comprehensive profile data including all available fields for a single LinkedIn profile
    
```bash
curl --location 'https://api.crustdata.com/screener/person/enrich?fields=linkedin_profile_url,linkedin_flagship_url,name,location,email,title,last_updated,headline,summary,num_of_connections,skills,profile_picture_url,profile_picture_permalink,twitter_handle,languages,all_employers,past_employers,current_employers,education_background,all_employers_company_id,all_titles,all_schools,all_degrees&linkedin_profile_url=https://www.linkedin.com/in/manmohitgrewal/' \
--header 'Authorization: Token $auth' \
--header 'Accept: application/json, text/plain, */*' \
--header 'Content-Type: application/json'
```
</details>

<details id="2-real-time-enrichment">
<summary>2. Real-time enrichment</summary>

### 2. Real-time enrichment 
- Usecase: Ideal for users who wants to enrich a profile in realtime from LinkedIn
    
```bash
curl -X GET "https://api.crustdata.com/screener/person/enrich?linkedin_profile_url=https://www.linkedin.com/in/abhilashchowdhary&enrich_realtime=true" \
-H "Authorization: Token auth_token" \
-H "Accept: application/json, text/plain, */*" \
-H "Content-Type: application/json"
```
</details>

<details id="3-request-for-business-email-and-all-default-fields">
<summary>3. Request with business email enrichment</summary>

### 3. Request for business email and all default fields
:::info
1. Only email enrichment
    - If you only request for `fields=business_email`, the endpoint will return just the email—no default profile fields (name, location, LinkedIn URL, headline, etc.).
    - This keeps the call cheap: 2 credits for email enrichment.
2. Email enrichment with profile enrichment
    - If you want to get the profile details along with business email you can add them to fields param in the request as shown in this example.
    - Cost: 2 credits for the email + 3 credits for profile enrichment (5 if realtime=true).
:::    

```bash
curl -X GET "https://api.crustdata.com/screener/person/enrich?linkedin_profile_url=https://www.linkedin.com/in/sasikumarm00&enrich_realtime=true&fields=business_email,linkedin_profile_url,linkedin_flagship_url,name,location,email,title,last_updated,headline,summary,num_of_connections,skills,profile_picture_url,twitter_handle,languages,linkedin_joined_date,all_employers,past_employers,current_employers,education_background,all_employers_company_id,all_titles,all_schools,all_degrees" \
-H "Authorization: Token auth_token" \
-H "Accept: application/json, text/plain, */*" \
-H "Content-Type: application/json"
```
</details>

<details id="4-request-with-all-default-fields-and-education-background-activities-and-societies">
<summary>4. Request with activities and societies</summary>

### 4. Request with all default fields AND `education_background.activities_and_societies`
        
```bash
curl -X GET "https://api.crustdata.com/screener/person/enrich?linkedin_profile_url=https://www.linkedin.com/in/sasikumarm00&enrich_realtime=true&fields=education_background.activities_and_societies,linkedin_profile_url,linkedin_flagship_url,name,location,email,title,last_updated,headline,summary,num_of_connections,skills,profile_picture_url,twitter_handle,languages,all_employers,past_employers,current_employers,education_background.degree_name,education_background.end_date,education_background.field_of_study,education_background.institute_linkedin_id,education_background.institute_linkedin_url,education_background.institute_logo_url,education_background.institute_name,education_background.start_date,all_employers_company_id,all_titles,all_schools,all_degrees" \
-H "Authorization: Token auth_token" \
-H "Accept: application/json, text/plain, */*" \
-H "Content-Type: application/json"
```
</details>

<details id="5-request-with-all-default-fields-and-certifications-honors-and-linkedin-open-to-cards">
<summary>5. Request with certifications and honors</summary>

### 5. Request with all default fields AND `certifications`, `honors`  and `linkedin_open_to_cards`
:::warning
  `certifications` , `honors`  and `linkedin_open_to_cards`  fields are not available by default. To gain access chat with [Abhilash](mailto:abhilash@crustdata.com) or [Chris](mailto:chris@crustdata.com) on your dedicated Crustdata's slack channel.
:::

```bash
curl -X GET "https://api.crustdata.com/screener/person/enrich?linkedin_profile_url=https://www.linkedin.com/in/sasikumarm00&enrich_realtime=true&fields=linkedin_profile_url,linkedin_flagship_url,name,location,email,title,last_updated,headline,summary,num_of_connections,skills,profile_picture_url,twitter_handle,languages,all_employers,past_employers,current_employers,education_background.degree_name,education_background.end_date,education_background.field_of_study,education_background.institute_linkedin_id,education_background.institute_linkedin_url,education_background.institute_logo_url,education_background.institute_name,education_background.start_date,all_employers_company_id,all_titles,all_schools,all_degrees,linkedin_open_to_cards,certifications,honors" \
-H "Authorization: Token auth_token" \
-H "Accept: application/json, text/plain, */*" \
-H "Content-Type: application/json"
```
</details>

<details id="6-request-with-all-default-fields-and-joined-date-and-verifications">
<summary>6. Request with joined date and verifications</summary>

### 6. Request with all default fields AND `joined_date` and `verifications`
:::warning
  `joined_date` and `verifications` fields are not available by default. To gain access chat with [Abhilash](mailto:abhilash@crustdata.com) or [Chris](mailto:chris@crustdata.com) on your dedicated Crustdata's slack channel.
:::
```bash
curl -X GET "https://api.crustdata.com/screener/person/enrich?force_fetch=True&linkedin_profile_url=https://www.linkedin.com/in/sasikumarm00&enrich_realtime=true&fields=linkedin_profile_url,linkedin_flagship_url,name,location,email,title,last_updated,headline,summary,num_of_connections,skills,profile_picture_url,twitter_handle,languages,all_employers,past_employers,current_employers,education_background.degree_name,education_background.end_date,education_background.field_of_study,education_background.institute_linkedin_id,education_background.institute_linkedin_url,education_background.institute_logo_url,education_background.institute_name,education_background.start_date,all_employers_company_id,all_titles,all_schools,all_degrees,linkedin_joined_date,linkedin_verifications" \
-H "Authorization: Token auth_token" \
-H "Accept: application/json, text/plain, */*" \
-H "Content-Type: application/json"
```
</details>

<details id="7-reverse-lookup-using-business-email">
<summary>7. Reverse lookup using business email</summary>

### 7. Reverse lookup using business email
        
```bash
curl -X GET "https://api.crustdata.com/screener/person/enrich?business_email=zoe.perret@initialized.com&enrich_realtime=true" \
-H "Authorization: Token auth_token" \
-H "Accept: application/json, text/plain, */*" \
-H "Content-Type: application/json"
```
</details>

<details id="8-profile-preview">
<summary>8. Preview profile</summary>

### 8. Preview profile
:::info
Access to this feature is controlled - contact [Abhilash](mailto:abhilash@crustdata.co) or [Chris](mailto:chris@crustdata.co) to enable it for your account.
:::

```bash
curl -X GET "https://api.crustdata.com/screener/person/enrich?linkedin_profile_url=https://www.linkedin.com/in/dvdhsu&preview=true" \
-H "Authorization: Token auth_token" \
-H "Accept: application/json, text/plain, */*" \
-H "Content-Type: application/json"
```
</details>

## Understanding the Score for Reverse Email Lookup {#score-explanation}

<details>
<summary>Click to view details on score calculation and interpretation</summary>

When you perform a reverse lookup using a `business_email`, the API attempts to find the corresponding professional profile. This is typically done using a request like the following:

```bash
cURL -X GET "https://api.crustdata.com/screener/person/enrich?business_email=zoe.perret@initialized.com&enrich_realtime=true" \
-H "Authorization: Token auth_token" \
-H "Accept: application/json, text/plain, */*" \
-H "Content-Type: application/json"
```

If a potential match is found, the response will include a `score` field, indicating the confidence level of the match based on name similarity.

Here's a simplified example of what the response might look like:

```json
[
  {
    "linkedin_profile_url": "https://www.linkedin.com/in/...",
    "name": "Zoe Perret",
    "location": "New York, New York, United States",
    "title": "Partner",
    "last_updated": "2025-02-11T12:27:08.315174+00:00",
    "headline": "Partner at Initialized Capital",
    // ... other fields ...
    "current_employers": [
        {
            "employer_name": "Initialized Capital",
            // ... employer details ...
            "employee_title": "Partner"
        }
        // ... other employers ...
    ],
    "score": 0.9 // <-- The enrichment score
  }
]
```

The score you receive primarily indicates how well the name on a found profile matches the structure of the input email's handle (the part before the '@'). It's a ranking signal based on name structure, not a direct measure of accuracy.

<h3>How it Works (Simplified):</h3>
1. **Parse & Identify**: We take the input email (e.g., `j.smith@example.com`), separate the handle (`j.smith`) and domain (`example.com`), and identify the likely company associated with the domain from our database.
2. **Search**: We search our database and the web for professional profiles associated with that company whose names might correspond structurally to the email handle (`j.smith`).
3. **Score Matches**: For each potential profile found, we compare the profile's actual name (e.g., "Jane Smith", "John Smith") against the email handle (`j.smith`) using common patterns and name similarity logic. The result of this comparison is the score.

<h3>Interpreting the Score:</h3>
The score reflects the structural similarity between the email handle and the name on the profile we found.
*   **High Score (0.9 - 1.0)**: Suggests a strong, common pattern match based on predefined rules.
    *   _Example 1_: Email `jane.smith@company.com` matching a profile named "Jane Smith" typically gets a score like 0.95 (reflecting the `{first}{last}` pattern).
    *   _Example 2_: Email `jsmith@company.com` matching "Jane Smith" typically gets a score like 0.75 (reflecting the `{f}{last}` pattern).
    *   _Example 3_: Email `jane@company.com` matching "Jane Smith" typically gets 0.9 if the handle is just `jane`, but might get 0.5 if the handle were `jane.marketing` (reflecting a single name pattern).
*   **Lower Score (0.5 - 0.89)**: Often indicates a match based on general name similarity calculated by internal logic, rather than a perfect pattern match.
    *   _Example 1_: Email `janes@company.com` matching "Jane Smith" might score around 0.75 (reflecting a `{first}{l}` pattern match).
    *   _Example 2_: Email `j.smith@company.com` matching "Jane Smith" might score 0.708 based on similarity logic (`j` vs `jane`, `smith` vs `smith`).
    *   _Example 3_: Email `jsmi@company.com` matching "Jane Smith" would likely score lower, calculated based on how well `jsmi` partially matches parts of "Jane Smith".

<h3>Key Takeaway:</h3> 
Use the score to gauge how well the email structurally resembles the name found. A high score means the structure fits well with common email naming conventions for that person's name.

<h3>Recommendation:</h3> 
Always verify the person's identity using other details provided in the API response, like title, `current_employers`, and location, regardless of the score.

</details>

## Example Responses

<details id="1-response-for-only-email-enrichment">
<summary>1. Response for only email enrichment</summary>

### Response when `fields=business_email` is passed in the request
```
[
    {
        "business_email": [
            "chris@crustdata.com"
        ],
        "current_employers": [
            {
                "employer_name": "Crustdata",
                "employer_linkedin_id": "33926293",
                "employer_company_website_domain": [
                    "crustdata.com"
                ],
                "business_emails": {
                    "chris@crustdata.com": {
                        "verification_status": "verified",
                        "last_validated_at": "2025-05-18"
                    }
                }
            }
        ],
        "past_employers": [
            {
                "employer_name": "PrivCo",
                "employer_linkedin_id": "28615661",
                "employer_company_website_domain": [
                    "privco.com"
                ],
                "business_emails": {
                    "chris@privco.com": {
                        "verification_status": "",
                        "last_validated_at": ""
                    }
            }
            ],
        "enriched_realtime": false,
        "query_linkedin_profile_urn_or_slug": [
            "chris-pisarski"
        ]
    }
]
```
</details>

<details id="2-response-when-profiles-are-in-database">
<summary>2. Response when profiles are in database</summary>

### Response when LinkedIn profiles are present in Crustdata's database
- Response will include the enriched data for each profile. [View example response](/examples/people-enrichment/database-response.json)
</details>

<details id="3-response-when-profiles-are-not-found">
<summary>3. Response when profiles are not found</summary>

### Response when one or more LinkedIn profiles are not present in Crustdata's database
- An error message will be returned for each profile not found, along with instructions to query again after 60 minutes. [View example response](/examples/people-enrichment/not-found-response.json)
</details>

<details id="4-response-with-all-fields">
<summary>4. Response with all fields</summary>

### Response with all possible fields
[View example response with all possible fields](/examples/people-enrichment/all-fields-response.json)
</details>

<details id="5-response-with-preview">
<summary>4. Response with `preview=true`</summary>

### Response with `preview=true`
[View example response with all possible fields](/examples/people-enrichment/person-preview.json)
</details>

### Single Profile Requests
| `enrich_realtime` | `force_fetch` | Http Code  | Error Code |API message (example)                                                                            | What it means                                                                          |
| ----------------- | ------------- | ------- | ------------- | ------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------- |
| `false`           | `false`       | **200** | - | *Profile JSON*                                                                                   | Profile returned successfully.                                                         |
| `true`            | `false`       | **200** | - | *Profile JSON*                                                                                   | Served from latest cache if present; otherwise fetched live from LinkedIn.             |
| `true`            | `true`        | **200** | - | *Profile JSON*                                                                                   | Always hits LinkedIn in real-time, ignoring cache.                                     |
| `true`            | `true`        | **404** | `PE01` | “No data found for the LinkedIn profile: \<company\_identifier>. This LinkedIn profile is not available”                                | LinkedIn profile does not exist (unavailable)                                              |
| `true`           | `true`       | **500** | `PE02` | “No data found for the LinkedIn profile: \<company\_identifier>. Internal system error while processing profile. Please try again later.”          | Profile could not be enriched due to internal failure.                                                        |
| `false`           | `false`       | **404** | `PE03` | “No data found for the LinkedIn profile: \<company\_identifier>. Data will be enriched shortly.” | Not in DB yet. Queued for enrichment. Retry later or call with `enrich_realtime=true`. |
| `false`           | `false`       | **400** | - | “Field 'linkedin\_profile\_url': Invalid LinkedIn URL format: \<linkedin\_profile\_id>”          | Malformed LinkedIn profile URL.                                                        |

### Multiple Profile Requests (Batch)
| `enrich_realtime` | `force_fetch` | Status  | API message (example)                                                                                              | What it means                                                                                    |
| ----------------- | ------------- | ------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| `false`           | `false`       | **200** | *Profiles JSON*                                                                                                    | All profiles enriched successfully.                                                              |
| `false`           | `false`       | **200** | *Profiles JSON* + “No data found for the LinkedIn profile: \<company\_identifier>. Data will be enriched shortly.” | Some profiles enriched; the rest queued. Retry missing ones later or use `enrich_realtime=true`. |
| `false`           | `false`       | **200** | *Profiles JSON* + “No data found for the LinkedIn profile: \<company\_identifier>.”                                | Some profiles enriched; others don’t exist.                                                      |
| `false`           | `false`       | **400** | “Field 'linkedin\_profile\_url': Invalid LinkedIn URL format: \<linkedin\_profile\_id>”                            | At least one LinkedIn URL is malformed — entire batch rejected.                                  |

### Common Validation Errors
| Status  | API message                                                           | What it means                                                  |
| ------- | --------------------------------------------------------------------- | -------------------------------------------------------------- |
| **400** | “`force_fetch` can only be used with `enrich_realtime`.”              | `force_fetch` cannot be passed without `enrich_realtime=true`. |
| **400** | “You must provide either a LinkedIn profile URL or a business email.” | Both `linkedin_profile` and `business_email` are missing.      |
| **400** | “You can only enrich up to 25 LinkedIn profiles at a time.”           | More than 25 identifiers in a single request.                  |

### Error Codes

| Error Code | Description | Message |
|-------------|-------------|--------------|
| `PE01` | Profile Unavailable | This LinkedIn profile is not available. |
| `PE02` | Internal System Error | Internal system error while processing profile. Please try again later. |
| `PE03` | Profile Not Found in Database | Data will be enriched shortly. |
| `PE04` | Profile Parsing Error | Unable to process LinkedIn profile data |

---

## 📊 Data Dictionary

# People API Dictionary

This dictionary describes the data returned by the People API. It provides detailed information about professionals including their profile details, employment history, education, and skills.

## Person Profile

Basic profile information about the person:

| Field                     | Type    | Description                                                |
|---------------------------|---------|-----------------------------------------------------------|
| linkedin_profile_url      | string  | LinkedIn profile URL (system format)                       |
| linkedin_flagship_url     | string  | LinkedIn profile URL (human-readable format)               |
| name                      | string  | Full name of the person                                    |
| location                  | string  | Geographic location of the person                          |
| email                     | string  | Email address (if available)                               |
| title                     | string  | Current professional title                                 |
| last_updated              | string  | Date and time when the profile was last updated            |
| headline                  | string  | LinkedIn headline                                          |
| summary                   | string  | Professional summary or bio                                |
| num_of_connections        | integer | Number of LinkedIn connections                             |
| profile_picture_url       | string  | URL to profile picture                                     |
| profile_picture_permalink | string  | URL to persisted profile picture                           |
| twitter_handle            | string  | Twitter username (if available)                            |
| languages                 | array   | Languages spoken by the person                             |
| enriched_realtime         | boolean | Whether the profile was enriched in real-time              |
| business_email            | string  | Business email at current employer                         |
| query_linkedin_profile_urn_or_slug | array | LinkedIn URN or slug used for the query             |

## Skills and Employers

| Field                     | Type    | Description                                                |
|---------------------------|---------|-----------------------------------------------------------|
| skills                    | array   | List of professional skills                                |
| all_employers             | array   | List of all companies the person has worked for            |
| all_employers_company_id  | array   | List of company IDs for all employers                      |
| all_titles                | array   | List of all job titles held                                |
| all_schools               | array   | List of educational institutions attended                  |
| all_degrees               | array   | List of degrees earned                                     |

## Current Employment

Information about current employers:

| Field                                               | Type    | Description                                                                                                                                                                                              |
|-----------------------------------------------------|---------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| current_employers                                   | array   | List of current employer information                                                                                                                                                                     |
| current_employers[].employer_name                   | string  | Name of the employer                                                                                                                                                                                     |
| current_employers[].employer_linkedin_id            | string  | LinkedIn ID of the employer                                                                                                                                                                              |
| current_employers[].employer_logo_url               | string  | URL to employer's logo                                                                                                                                                                                   |
| current_employers[].employer_linkedin_description   | string  | Description of the employer from LinkedIn                                                                                                                                                                |
| current_employers[].employer_company_id             | array   | Company IDs associated with the employer                                                                                                                                                                 |
| current_employers[].employer_company_website_domain | array   | Website domains of the employer                                                                                                                                                                          |
| current_employers[].domains                         | array   | All known domains associated with the employer company                                                                                                                                                   |
| current_employers[].employee_position_id            | integer | Unique ID for the position                                                                                                                                                                               |
| current_employers[].employee_title                  | string  | Job title at the employer                                                                                                                                                                                |
| current_employers[].employee_description            | string  | Job description                                                                                                                                                                                          |
| current_employers[].employee_location               | string  | Job location                                                                                                                                                                                             |
| current_employers[].start_date                      | string  | Start date of employment                                                                                                                                                                                 |
| current_employers[].end_date                        | string  | End date of employment (null if current)                                                                                                                                                                 |
| current_employers[].is_default                      | boolean  | Reflects if the position is the deafult    
| current_employers[].business_emails                 | object  | Business emails associated with the employer, mapping from email address to a metadata dict with "verification_status" and "last_validated_at". (Only available if `fields=business_email` is provided ) |

## Past Employment

Information about previous employers:

| Field                                            | Type    | Description                                                                                                                                                                                             |
|--------------------------------------------------|---------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| past_employers                                   | array   | List of past employer information                                                                                                                                                                       |
| past_employers[].employer_name                   | string  | Name of the previous employer                                                                                                                                                                           |
| past_employers[].employer_linkedin_id            | string  | LinkedIn ID of the employer                                                                                                                                                                             |
| past_employers[].employer_logo_url               | string  | URL to employer's logo                                                                                                                                                                                  |
| past_employers[].employer_linkedin_description   | string  | Description of the employer from LinkedIn                                                                                                                                                               |
| past_employers[].employer_company_id             | array   | Company IDs associated with the employer                                                                                                                                                                |
| past_employers[].employer_company_website_domain | array   | Website domains of the employer                                                                                                                                                                         |
| past_employers[].domains                         | array   | All known domains associated with the employer company                                                                                                                                                  |
| past_employers[].employee_position_id            | integer | Unique ID for the position                                                                                                                                                                              |
| past_employers[].employee_title                  | string  | Job title at the employer                                                                                                                                                                               |
| past_employers[].employee_description            | string  | Job description                                                                                                                                                                                         |
| past_employers[].employee_location               | string  | Job location                                                                                                                                                                                            |
| past_employers[].start_date                      | string  | Start date of employment                                                                                                                                                                                |
| past_employers[].end_date                        | string  | End date of employment                                                                                                                                                                                  |
| past_employers[].business_emails                 | object  | Business emails associated with the employer, mapping from email address to a metadata dict with "verification_status" and "last_validated_at". (Only available if `fields=business_email` is provided) |
## Education

Information about educational background:

| Field                                       | Type    | Description                                      |
|---------------------------------------------|---------|--------------------------------------------------|
| education_background                        | array   | List of education entries                         |
| education_background[].degree_name          | string  | Name of degree earned                             |
| education_background[].institute_name       | string  | Name of educational institution                   |
| education_background[].institute_linkedin_id | string  | LinkedIn ID of the institution                    |
| education_background[].institute_linkedin_url | string  | LinkedIn URL of the institution                   |
| education_background[].institute_logo_url   | string  | URL to institution's logo                         |
| education_background[].field_of_study       | string  | Major or specialization                           |
| education_background[].start_date           | string  | Start date of education                           |
| education_background[].end_date             | string  | End date of education                             |

## Certifications (Limited Access)

Professional certifications earned by the person:

:::warning
The `certifications` field is not available by default. To gain access, please contact [Abhilash](mailto:abhilash@crustdata.com) or [Chris](mailto:chris@crustdata.com) on your dedicated Crustdata slack channel.
:::

| Field                                          | Type    | Description                                      |
|------------------------------------------------|---------|--------------------------------------------------|
| certifications                                 | array   | List of professional certifications              |
| certifications[].name                          | string  | Name of the certification                        |
| certifications[].issued_date                   | string  | Date when certification was issued               |
| certifications[].expiration_date               | string  | Expiration date of certification (if applicable) |
| certifications[].url                           | string  | URL to verify or view the certification          |
| certifications[].issuer_organization           | string  | Name of the issuing organization                 |
| certifications[].issuer_organization_linkedin_id | string | LinkedIn ID of the issuing organization         |
| certifications[].certification_id              | string  | Unique identifier of the certification           |

## Honors (Limited Access)

Awards and honors received by the person:

:::warning
The `honors` field is not available by default. To gain access, please contact [Abhilash](mailto:abhilash@crustdata.com) or [Chris](mailto:chris@crustdata.com) on your dedicated Crustdata slack channel.
:::

| Field                                          | Type    | Description                                      |
|------------------------------------------------|---------|--------------------------------------------------|
| honors                                         | array   | List of awards and honors                        |
| honors[].title                                 | string  | Title of the honor or award                      |
| honors[].issued_date                           | string  | Date when the honor was issued                   |
| honors[].description                           | string  | Description of the honor                         |
| honors[].issuer                                | string  | Organization that issued the honor               |
| honors[].media_urls                            | array   | URLs to media related to the honor               |
| honors[].associated_organization_linkedin_id   | string  | LinkedIn ID of associated organization           |
| honors[].associated_organization               | string  | Name of associated organization                  |

## LinkedIn Open To Cards (Limited Access)

Information about what opportunities the person is open to:

:::warning
The `linkedin_open_to_cards` field is not available by default. To gain access, please contact [Abhilash](mailto:abhilash@crustdata.com) or [Chris](mailto:chris@crustdata.com) on your dedicated Crustdata slack channel.
:::

| Field                     | Type    | Description                                                |
|---------------------------|---------|-----------------------------------------------------------|
| linkedin_open_to_cards    | array   | List of opportunities the person is open to (e.g., "Open to work", "Hiring", "Providing services") |

## LinkedIn Joined Date (Limited Access)

Date when the person joined LinkedIn:

:::warning
The `linkedin_joined_date` field is not available by default. To gain access, please contact [Abhilash](mailto:abhilash@crustdata.com) or [Chris](mailto:chris@crustdata.com) on your dedicated Crustdata slack channel.
:::

| Field                     | Type    | Description                                                |
|---------------------------|---------|-----------------------------------------------------------|
| linkedin_joined_date      | string  | Date when the person joined LinkedIn (ISO format, e.g., "2010-05-15T00:00:00+00:00") |

# Post and Reactor Information

## Post

| Field | Type | Description |
|-------|------|-------------|
| backend_urn | string | Unique identifier for the activity |
| share_urn | string | Unique identifier for the share |
| share_url | string | URL of the shared post |
| text | string | Content of the post |
| actor_name | string | Name of the post author |
| date_posted | string | Date when the post was published (YYYY-MM-DD) |
| total_reactions | integer | Total number of reactions on the post |
| total_comments | integer | Total number of comments on the post |
| reactions_by_type | object | Breakdown of reactions by type |
| num_shares | integer | Number of times the post was shared |

## Reactor

| Field | Type | Description |
|-------|------|-------------|
| name | string | Name of the person who reacted |
| linkedin_profile_url | string | URL of the reactor's profile |
| reaction_type | string | Type of reaction (e.g., LIKE, EMPATHY) |
| profile_image_url | string | URL of the reactor's profile image |
| title | string | Professional title of the reactor |
| additional_info | string | Additional information about the connection |
| location | string | Location of the reactor |
| linkedin_profile_urn | string | Unique identifier for the profile |
| default_position_title | string | Current job title |
| default_position_company_linkedin_id | string | ID of the current employer |
| default_position_is_decision_maker | boolean | Indicates if the person is a decision maker |
| flagship_profile_url | string | Another URL format for the profile |
| profile_picture_url | string | URL of the full-size profile picture |
| headline | string | Professional headline |
| summary | string | Professional summary (can be null) |
| num_of_connections | integer | Number of connections |
| related_colleague_company_id | integer | ID of a related company |
| skills | array | List of professional skills |

---

## 🔧 OpenAPI Specification

# Enrichment API (realtime/in-db)

**Category:** People API
**Base URL:** https://api.crustdata.com
**Official Docs:** /docs/discover/people-apis/people-enrichment-api

**Endpoint:** `GET /screener/person/enrich`

**Description:** Enrich data for one or more individuals using LinkedIn profile URLs
or business email addresses. You must provide at least one of
`linkedin_profile_url` or `business_email`. If `enrich_realtime`
is set to true, and no matching record is found in the database,
a real-time search will be performed.
> [Show Docs](/docs/discover/people-apis/people-enrichment-api)

## Authentication
This endpoint requires a Bearer token in the `Authorization` header:

```
Authorization: Token <YOUR_TOKEN>
```
## Query Parameters
| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `linkedin_profile_url` | string | Yes | Comma-separated list of LinkedIn profile URLs. |  |  |
| `business_email` | string | No | Comma-separated list of business email addresses. |  |  |
| `enrich_realtime` | boolean | No | If set to true, performs a real-time search from the web if data is not found in the database. |  |  |
| `fields` | string | Yes | Comma-separated list of fields to return. |  |  |

## Example Request

```bash
curl -X GET "https://api.crustdata.com/screener/person/enrich?linkedin_profile_url=https%3A%2F%2Fwww.linkedin.com%2Fcompany%2Fcrustdata&business_email=example_value&enrich_realtime=true" \
  -H "Authorization: Token &lt;YOUR_TOKEN&gt;"
```

## Rate Limiting
All Crustdata API requests count toward your per-minute quota. Inspect the response headers `X-RateLimit-Limit` and `X-RateLimit-Remaining` to monitor usage. Implement exponential back-off or retries when you receive a **429 Too Many Requests** response.

## Responses
### Status 200
**Description:** Successful response
**Response Schema:**
| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `linkedin_profile_url` | string | No |  |  |  |
| `linkedin_flagship_url` | string | No |  |  |  |
| `name` | string | No |  |  |  |
| `email` | string | No |  |  |  |
| `title` | string | No |  |  |  |
| `last_updated` | string | No |  |  |  |
| `headline` | string | No |  |  |  |
| `summary` | string | No |  |  |  |
| `num_of_connections` | integer | No |  |  |  |
| `skills` | string | No |  |  |  |
| `profile_picture_url` | string | No |  |  |  |
| `profile_picture_permalink` | string | No |  |  |  |
| `twitter_handle` | string | No |  |  |  |
| `languages` | array | No |  |  |  |
| `all_employers` | array | No |  |  |  |
| `past_employers` | array | No |  |  |  |
| `current_employers` | array | No |  |  |  |
| `all_employers_company_id` | array | No |  |  |  |
| `all_titles` | array | No |  |  |  |
| `all_schools` | array | No |  |  |  |
| `all_degrees` | array | No |  |  |  |

### Status 400
**Description:** Bad request, please check your query parameters.
**Response Schema:**
| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `error` | string | No |  |  |  |

## 📋 OpenAPI Components

## Response Schema Components

```yaml
schemas:
  ProfessionalProfile:
    type: object
    description: "This object contains a detailed professional profile of a person."
    properties:
      linkedin_profile_url:
        type: string
      linkedin_flagship_url:
        type: string
      name:
        type: string
      email:
        type: string
      title:
        type: string
      # ... (16 more properties)

  EmploymentDetail:
    type: object
    description: "This object contains detail about a person's employment information."
    properties:
      employer_name:
        type: string
      employer_linkedin_id:
        type: string
      employer_company_id:
        type: integer
      employee_title:
        type: string
      employee_description:
        type: string
      # ... (3 more properties)

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

```

---

<!-- Error loading /docs/discover/people-apis/people-linkedin-post-api -->

# Comprehensive API Documentation: people-search-api

## 📋 Documentation Metadata

- **API Path:** `POST /screener/person/search`
- **Category:** People API
- **Operation:** api
- **Documentation File:** people-search-api.md
- **Data Dictionary:** people-search.md
- **Main Documentation:** discover/people-apis/people-search-api.md
- **Generated:** 2025-11-27T14:03:48.595Z

---

## 📖 Original Documentation

# Realtime: People Search API 

### [ 🚀 Try Now ](/api#tag/people-api/post/screener/person/search)

Search for people profiles based on custom search criteria as a filter. This endpoint allows you to retrieve detailed information about individuals matching specific criteria.

## Endpoint

```
POST /screener/person/search
```

## Data Dictionary

[Explore the data dictionary for this endpoint here](/docs/dictionary/people-search)

## Request Parameters

| Payload Keys                             | Type    | Required | Description                                              | Notes                                                                                                               |
| ------------------------------------- | ------- | -------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `filters`                             | object  | optional | JSON dictionary defining the search criteria             | Refer to [How to Build Filters](/docs/discover/people-apis/how-to-build-people-filters) for a comprehensive list of filter types and acceptable values. |
| `page`                                | integer | optional | Page number for pagination (starts from 1)                               | Only used with `filters` for synchronous search. Cannot be used with `limit` parameter (mutually exclusive)                                                                                            |
| `preview`                             | boolean | optional | Get preview of profiles                                  | Cannot be used with `page`      
| `limit`                               | integer | optional | Maximum results to return (sync: max 25, async: max 10,000) | Use with `background_job=true` for large searches. Cannot be used with `page` parameter (mutually exclusive)                                                                                        |
| `background_job`                      | boolean | optional | Run search asynchronously for large result sets         | Required when `limit` > 25                                                                                        |
| `job_id`                              | string  | optional | Check status of a background job                         | Returns job status and results when ready                                                                                        |
| `post_processing`                     | object | optional | Extra rules applied *after* the search completes | See **Post-processing options** below                                                                                        |

### Post-processing options
| Key                 | Type | Default | Description                                                                                                                        |
| ------------------- | ---- | ------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `strict_title_and_company_match` | bool | `false` | When `true`, results are filtered so a profile’s titles **exactly** match the `CURRENT_TITLE` / `PAST_TITLE` filters you supplied. **Cannot be used with `fuzzy_match: true`.** |
| `exclude_profiles` | array | `[]` | List of LinkedIn profile URLs to exclude from results |
| `exclude_names` | array | `[]` | List of names to exclude from results |

:::warning Parameter Incompatibility
`strict_title_and_company_match` cannot be used when any `CURRENT_TITLE` or `PAST_TITLE` filter has `fuzzy_match: true`. These are mutually exclusive options:
- Use `strict_title_and_company_match: true` for exact title matching with post-processing
- Use `fuzzy_match: true` for broader title matching during the search
:::

#### Key Points
- **Synchronous search**: Each page returns up to 25 results. To fetch all results, iterate over pages until you cover the value of `total_display_count` in the response from first page. **Recommended for searches requiring up to 500 total results.**
- **Asynchronous search**: For large result sets (>500 results), use `background_job=true` with `limit` parameter to retrieve up to 10,000 profiles in a single request. Check job status using the returned `job_id`.
- **Parameter constraints**: 
  - `page` and `limit` parameters are mutually exclusive - use `page` for synchronous pagination or `limit` for async bulk retrieval
  - `background_job` is required when `limit` is greater than 25
  - **Use synchronous search for up to 500 results, asynchronous for 500+ results**

:::tip **Recommended: Use Synchronous Search**
For most use cases, **synchronous search is recommended** because it:
- ✅ **Returns results immediately** (10-30 seconds)
- ✅ **Simpler to implement** - no need to poll for job status
- ✅ **More predictable** - you know exactly when you'll get results
- ✅ **Better for real-time applications** - perfect for user-facing features

**What synchronous search looks like:**
```bash
# Simple synchronous search - returns results immediately
curl 'https://api.crustdata.com/screener/person/search/' \
  --header 'Authorization: Token $token' \
  --header 'Content-Type: application/json' \
  --data '{
    "filters": [
      {
        "filter_type": "CURRENT_COMPANY",
        "type": "in",
        "value": ["https://www.linkedin.com/company/google/"]
      }
    ],
    "page": 1
  }'

# Response comes back in 10-30 seconds with up to 25 profiles
```

**When to use asynchronous search:**
- When you need **more than 500 results** total (across multiple pages or in a single request)
- For **bulk data processing** where immediate results aren't required
- When you have **very large result sets** (thousands of profiles)
:::

- **Pagination:** If the total number of results for the query is more than 25 (value of `total_display_count` param), you can paginate the response in the following ways (depending on your request)
  - When passing `filters` :
    - provide `page` as one of the keys in the payload itself

- **Latency:** The data is fetched in real-time from Linkedin and the latency for this endpoint is between 10 to 30 seconds.
- **Response schema:** Because the data is fetched realtime, and the results may not be in Crustdata's database already, the response schema will be different from [person enrichment endpoint](/docs/discover/people-apis/people-enrichment-api) . But all the results will be added to Crustdata's database in 10 min of your query and the data for a specific person profile can be enriched via [person enrichment endpoint](/docs/discover/people-apis/people-enrichment-api)
- **Total number of records:** `total_display_count` field in the response tells the total number of people that match the search criteria. Use that if you just want to get the total number of people for a given criteria.

#### Rate Limits & Constraints
- **Rate limit**: starting at 15 requests per minute for synchronous searches. Reach out to Abhilash or Chris over Slack
- **Background job limit**: 3 concurrent background jobs per account
- **Maximum page number**: 100
- **Maximum profiles per background job**: 10,000. Reach out to Abhilash or Chris if you want to fetch more profiles in 1 request

## Credit Usage
- **Synchronous search** (both `page` and `limit` parameters): Charged 1 credit per profile returned in the API response. If fewer than 5 profiles are returned, a minimum of 5 credits is charged
- **Preview mode**: A successful request with `preview=true` costs 5 credits
- **Background jobs**: Charged based on the actual number of profiles returned (1 credit per profile)
  - Example: A background job with `limit=1000` that returns 750 profiles will cost 750 credits
  - Maximum limit is 10,000 profiles per background job
- **No Results, No Charges**: You are never charged credits when our APIs return no results. Credits are only deducted when data is successfully returned from your API requests.

## Example Requests

<details id="1-via-custom-search-filters">
<summary>1. Via Custom Search Filters</summary>

### 1. Via Custom Search Filters
This query retrieves people working at `Google` or `Microsoft`, excluding those with the titles `Software Engineer` or `Data Scientist`, based in companies headquartered in `United States` or `Canada`, from the `Software Development` or `Hospitals and Health Care` industries, while excluding people located in `California, United States` or `New York, United States`

```bash
curl 'https://api.crustdata.com/screener/person/search/' \
--header 'Authorization: Token $token' \
--data '{
    "filters": [
        {
            "filter_type": "CURRENT_COMPANY",
            "type": "in",
            "value": ["Google", "Microsoft"]
        },
        {
            "filter_type": "CURRENT_TITLE",
            "type": "not in",
            "value": ["Software Engineer", "Data Scientist"]
        },
        {
            "filter_type": "COMPANY_HEADQUARTERS",
            "type": "in",
            "value": ["United States", "Canada"]
        },
        {
            "filter_type": "INDUSTRY",
            "type": "in",
            "value": ["Software Development", "Hospitals and Health Care"]
        },
        {
            "filter_type": "REGION",
            "type": "not in",
            "value": ["California, United States", "New York, United States"]
        }
    ],
    "page": 1
}'
```
</details>

<details id="2-profile-with-specific-titles-in-region">
<summary>2. Profile with specific titles in Region</summary>

### 2. Profile with specific titles in Region
Retrieve people profies matching set of past/current titles **and** in specific location.  
For both `CURRENT_TITLE` and `REGION`, use the canonical values fromm static static [Region](/examples/people-search/static-region-filter-values.json)/[Title](/examples/people-search/linkedin_titles.json) list or fetch them via [Auto-complete API](/docs/discover/auxiliary-apis/filters-autocomplete).

```bash
curl 'https://api.crustdata.com/screener/person/search/' \
  --header 'Authorization: Token $token' \
  --header 'Content-Type: application/json' \
  --data '{
    "filters": [
      {
        "filter_type": "CURRENT_TITLE",
        "type": "in",
        "value": ["Co-Founder"]
      },
      {
        "filter_type": "REGION",
        "type": "in",
        "value": ["San Francisco Bay Area"]
      }
    ],
    "page": 1
  }`
```
</details>

<details id="3-current-employees-of-a-company-with-exact-title">
<summary>3. Current employees of a company with exact title</summary>

### 3. Current employees of a company with exact title
Need an **exact** title match at a specific company?  
Set the post-processing flag `strict_title_and_company_match` to `true`.

#### `CURRENT_TITLE` filter
- **Exact matching enabled:** When `strict_title_and_company_match=true`, the API keeps **only** those people whose current job title matches the string you provide.  
- **Fuzzy matching (default):** By default the API uses fuzzy logic and may return profile with close matching titles. 

#### `CURRENT_COMPANY` filter  
Accepts any of the following identifiers for the company:
1. LinkedIn company profile URL (**preferred**)
2. Company domain (e.g. `codeant.ai`)
3. Plain company name

```bash
curl 'https://api.crustdata.com/screener/person/search/' \
  --header 'Authorization: Token $token' \
  --header 'Content-Type: application/json' \
  --data '{
    "filters": [
      {
        "filter_type": "CURRENT_TITLE",
        "type": "in",
        "value": ["Founder"]
      },
      {
        "filter_type": "CURRENT_COMPANY",
        "type": "in",
        "value": [
          "https://linkedin.com/company/reducto-ai"
        ]
      }
    ],
    "page": 1,
    "post_processing": {
      "strict_title_and_company_match": true
    }
  }`
```

:::warning
When using `strict_title_and_company_match: true`, do not set `fuzzy_match: true` on any `CURRENT_TITLE` or `PAST_TITLE` filters. These options are mutually exclusive.
:::
</details>

<details id="4-exact-title-matching">
<summary>4. Exact title matching using LinkedIn's predefined titles</summary>

### 4. Exact title matching using LinkedIn's predefined titles

For precise title matching, use LinkedIn's official title enumeration. You must select from the predefined title list - either from the [static title values](/examples/people-search/linkedin_titles.json) or by using the [Filters Autocomplete API](/docs/discover/auxiliary-apis/filters-autocomplete).

**Step 1: Get the exact title using Autocomplete API**
```bash
curl 'https://api.crustdata.com/screener/filters/autocomplete/' \
--header 'Authorization: Token $token' \
--header 'Content-Type: application/json' \
--data '{
  "filter_type": "CURRENT_TITLE",
  "query": "Chief Executive"
}'
```

**Step 2: Use the exact title from the response in your search**
```bash
curl 'https://api.crustdata.com/screener/person/search/' \
--header 'Authorization: Token $token' \
--header 'Content-Type: application/json' \
--data '{
  "filters": [
    {
      "filter_type": "CURRENT_TITLE",
      "type": "in",
      "value": ["Chief Executive Officer"]
    },
    {
      "filter_type": "CURRENT_COMPANY",
      "type": "in",
      "value": ["https://linkedin.com/company/openai"]
    }
  ],
  "page": 1
}'
```

:::info
**Important:** The `CURRENT_TITLE` and `PAST_TITLE` filters accept LinkedIn's predefined title values for exact search. Always use the predefined title string from either the [static title list](/examples/people-search/linkedin_titles.json) or the autocomplete API response.
:::
</details>

<details id="5-people-with-specific-first-name-from-a-specific-company">
<summary>5. People with specific first name from a specific company</summary>

### 5. People with specific first name from a specific company given company's domain
```bash
curl 'https://api.crustdata.com/screener/person/search/' \
--header 'Authorization: Token $token' \
--data '{
  "filters": [
    {
      "filter_type": "FIRST_NAME",
      "type": "in",
      "value": ["steve"]
    },
    {
      "filter_type": "CURRENT_COMPANY",
      "type": "in",
      "value": ["buzzbold.com"]
    }
  ],
"page": 1
}'
```
</details>

<details id="6-preview-list-of-people-given-filter-criteria">
<summary>6. Preview list of people given filter criteria</summary>

### 6. Preview list of people given filter criteria
```bash
curl 'https://api.crustdata.com/screener/person/search/' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json, text/plain, */*' \
--header 'Authorization: Token $token' \
--data '{"filters":[
    {
      "filter_type": "CURRENT_COMPANY",
      "type": "in",
      "value": ["serverobotics.com"]
    },
    {
      "filter_type": "REGION",
      "type": "in",
      "value": ["United States"]
    }
  ],
  "preview": true
}'
```
</details>

<details id="7-people-that-recently-changed-jobs">
<summary>7. People that recently changed jobs</summary>

### 7. People that recently changed jobs and are currently working at a specific company
People that have changed jobs in last 90 days and are currently working at Serve Robotics

```bash
curl 'https://api.crustdata.com/screener/person/search/' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json, text/plain, */*' \
--header 'Authorization: Token $token' \
--data '{"filters":[
    {
      "filter_type": "CURRENT_COMPANY",
      "type": "in",
      "value": ["serverobotics.com"]
    },
    {
      "filter_type": "RECENTLY_CHANGED_JOBS"
    }
  ]
}'
```
</details>

<details id="8-all-people-working-at-a-specific-company">
<summary>8. All people working at a specific company (upto 2500)</summary>

### 8. All people working at a specific company (upto 2500)
```bash
curl 'https://api.crustdata.com/screener/person/search/' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json, text/plain, */*' \
--header 'Authorization: Token $token' \
--data '{"filters":[
    {
      "filter_type": "CURRENT_COMPANY",
      "type": "in",
      "value": ["serverobotics.com"]
    }
  ],
  "limit": 200
}'
```
</details>

<details id="9-all-people-with-specific-titles-at-a-specific-company">
<summary>9. All people with specific titles at a specific company (boolean filters)</summary>

### 9. All people with specific titles at a specific company (boolean filters)
```bash
curl 'https://api.crustdata.com/screener/person/search/' \
--header 'Authorization: Token $token' \
--data '
{
    "filters": [
        {
            "filter_type": "CURRENT_TITLE",
            "type": "in",
            "value": ["(((staff AND infrastructure AND engineer) OR (cloud AND infrastructure AND architect) OR (principal AND devops AND engineer) OR ccoe OR (cloud AND center AND of AND excellence) OR (site AND reliability AND engineer) OR (finops AND architect) OR (cloud AND platform AND architect) OR (devops AND engineer) OR (sre AND devops) OR (finops AND engineer) OR (cost AND engineer) OR finops OR (cloud AND architect) OR (infra AND architect) OR (cloud AND engineer) OR (infrastructure AND engineer) OR (infra AND engineer) OR (sre AND devops) OR (platform AND engineer) OR (cloud AND cost AND engineer) OR (infrastructure AND architect) OR sre OR (devops AND architect)) AND NOT (solution))"]
        },
        {
            "filter_type": "CURRENT_TITLE",
            "type": "not in",
            "value": [
                "solution"
            ]
        },
        {
            "filter_type": "REGION",
            "type": "in",
            "value": [
                "United States"
            ]
        },
        {
            "filter_type": "CURRENT_COMPANY",
            "type": "in",
            "value": [
                "gorgias.com"
            ]
        }
    ],
    "limit": 5
}'
```
</details>

<details id="10-director-level-or-above-people-in-sales-function">
<summary>10. Director level or above people in Sales function at a specific company</summary>

### 10. Director level or above people in Sales function at a specific company
```bash
curl 'https://api.crustdata.com/screener/person/search/' \
--header 'Authorization: Token $token' \
--data '
{"filters":[
    {
      "filter_type": "CURRENT_COMPANY",
      "type": "in",
      "value": ["rippling.com"]
    },
    {
      "filter_type": "FUNCTION",
      "type": "in",
      "value": ["Sales"]
    },
    {
      "filter_type": "SENIORITY_LEVEL",
      "type": "in",
      "value": ["Vice President", "Director"]
    }
  ],
  "page": 1
}'
```

:::tip
See all possible values for `SENIORITY_LEVEL` and `FUNCTION` filters in the [How to Build People Filters](/docs/discover/people-apis/how-to-build-people-filters) documentation.
:::
</details>

<details id="11-paginated-background-job-search">
<summary>11. Paginated background job search</summary>

### 11. Paginated background job search

Use `page` with `background_job=true` to process large searches page by page asynchronously. This is useful when you want to process results in batches rather than all at once.

```bash
curl 'https://api.crustdata.com/screener/person/search/' \
--header 'Authorization: Token $token' \
--data '{
  "filters": [
    {
      "filter_type": "FIRST_NAME",
      "type": "in",
      "value": ["Ali"]
    },
    {
      "filter_type": "LAST_NAME",
      "type": "in",
      "value": ["Kashani"]
    },
    {
      "filter_type": "CURRENT_COMPANY",
      "type": "in",
      "value": ["serverobotics.com"]
    },
    {
      "filter_type": "REGION",
      "type": "in",
      "value": ["United States"]
    }
  ],
  "page": 1,
  "background_job": "True"
}'
```
</details>

<details id="12-limited-results-with-exclusions">
<summary>12. Limited results with exclusions</summary>

### 12. Limited results with exclusions

Combine `limit` with `post_processing` to exclude specific profiles or names from your results. This example searches for founders but excludes specific individuals.

```bash
curl 'https://api.crustdata.com/screener/person/search/' \
--header 'Authorization: Token $token' \
--data '{
  "filters": [
    {
      "filter_type": "CURRENT_COMPANY",
      "type": "in",
      "value": ["serverobotics.com"]
    },
    {
      "filter_type": "CURRENT_TITLE",
      "type": "in",
      "value": ["founder"]
    },
    {
      "filter_type": "REGION",
      "type": "in",
      "value": ["United States"]
    }
  ],
  "limit": 5,
  "post_processing": {
    "exclude_names": ["Ali Kashani"],
    "exclude_profiles": ["https://www.linkedin.com/in/alikashani"]
  }
}'
```
</details>

<details id="13-large-synchronous-search">
<summary>13. Large synchronous search</summary>

### 13. Large synchronous search

For searches with `limit` > 25 but ≤ 2000, the API automatically processes them synchronously without requiring `background_job`. This example retrieves up to 2000 dermatologists with "medical imaging" keyword.

```bash
curl 'https://api.crustdata.com/screener/person/search/' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json, text/plain, */*' \
--header 'Authorization: Token $token' \
--data '{
  "filters": [
    {
      "filter_type": "CURRENT_TITLE",
      "type": "in",
      "value": ["Dermatologist"]
    },
    {
      "filter_type": "REGION",
      "type": "in",
      "value": ["United States"]
    },
    {
      "filter_type": "KEYWORD",
      "type": "in",
      "value": ["medical imaging"]
    }
  ],
  "limit": 2000
}'
```

:::warning
This synchronous request may take 30-60 seconds to complete due to the large result set. Consider using `background_job=true` for better performance.
:::
</details>

<details id="14-large-background-search">
<summary>14. Large background search (3000+ results)</summary>

### 14. Large background search (3000+ results)

For very large result sets (limit > 2000), use `background_job=true` to process asynchronously. This example retrieves up to 3000 profiles matching specific criteria.

```bash
curl 'https://api.crustdata.com/screener/person/search/' \
--header 'Authorization: Token $token' \
--data '{
  "filters": [
    {
      "filter_type": "FIRST_NAME",
      "type": "in",
      "value": ["Ali"]
    },
    {
      "filter_type": "LAST_NAME",
      "type": "in",
      "value": ["Kashani"]
    },
    {
      "filter_type": "CURRENT_COMPANY",
      "type": "in",
      "value": ["serverobotics.com"]
    },
    {
      "filter_type": "REGION",
      "type": "in",
      "value": ["United States"]
    }
  ],
  "limit": 3000,
  "background_job": "True"
}'
```

Response:
```json
{
  "job_id": "342206ab-0921-4555-833b-e1794b3b674f",
  "status": "processing",
  "message": "Your search is being processed. Use the job_id to retrieve results."
}
```
</details>

<details id="15-retrieve-background-job-results">
<summary>15. Retrieve background job results</summary>

### 15. Retrieve background job results

Check the status and retrieve results of a background job using its `job_id`. The job will return all matching profiles when complete.

```bash
curl 'https://api.crustdata.com/screener/person/search/' \
--header 'Authorization: Token $token' \
--data '{
  "job_id": "342206ab-0921-4555-833b-e1794b3b674f"
}'
```

Possible status values:
- `processing`: Job is still running
- `completed`: Results are ready (will include profile data)
- `failed`: Job encountered an error

:::tip
Poll this endpoint every 10-30 seconds until the status changes from `processing` to `completed`.
:::
</details>

<details id="16-fuzzy-title-matching">
<summary>16. Fuzzy title matching</summary>

### 16. Fuzzy title matching

Use `fuzzy_match=true` with `CURRENT_TITLE` or `PAST_TITLE` filters to enable broader title matching. This allows for more wider search results when looking for people with similar titles.

```bash
curl 'https://api.crustdata.com/screener/person/search/' \
--header 'Authorization: Token $token' \
--header 'Content-Type: application/json' \
--data '{
  "filters": [
    {
      "filter_type": "CURRENT_TITLE",
      "type": "in",
      "value": ["Founder", "Co-Founder"],
      "fuzzy_match": true
    },
    {
      "filter_type": "SCHOOL",
      "type": "in",
      "value": ["Stanford University"]
    }
  ],
  "page": 1
}'
```

:::info
The `fuzzy_match` parameter is only available for `CURRENT_TITLE` and `PAST_TITLE` filters. When set to `true`, it enables broader matching beyond the default fuzzy logic.
:::

:::warning
When using `fuzzy_match: true` on title filters, do not use `strict_title_and_company_match: true` in post-processing. These options are mutually exclusive.
:::
</details>

## Example Responses

<details id="1-default-response">
<summary>1. Default (without preview=True)</summary>

### 1. Default (without `preview=True`)
[View example response](/examples/people-search/default-response.json)
</details>

<details id="2-preview-response">
<summary>2. With preview=True</summary>

### 2. With `preview=True`
[View example response](/examples/people-search/preview-response.json)
</details>

<details id="3-preview-response-2">
<summary>3. With preview=True (Alternative)</summary>

### 3. With `preview=True`
[View example response](/examples/people-search/preview-response-2.json)
</details>

## Error Responses

Common error scenarios and their responses:

### Invalid Filter Type
```json
{
  "error": "Invalid filter_type: INVALID_TYPE. Valid types are: CURRENT_COMPANY, PAST_COMPANY, CURRENT_TITLE, PAST_TITLE, FIRST_NAME, LAST_NAME, RECENTLY_CHANGED_JOBS, FUNCTION, SENIORITY_LEVEL, COMPANY_HEADQUARTERS, INDUSTRY, REGION"
}
```

### Rate Limit Exceeded
```json
{
  "error": "Rate limit exceeded. Maximum 10 requests per minute.",
  "retry_after": 30
}
```

### Background Job Limit Exceeded
```json
{
  "error": "Maximum concurrent background jobs (3) reached. Please wait for existing jobs to complete."
}
```

### Invalid Parameter Combination
```json
{
  "error": "Cannot use 'preview' with 'page' parameter"
}
```

---

## 📊 Data Dictionary

# People Search API Dictionary

This dictionary describes the data returned by the People Search API (`/screener/person/search` endpoint). It provides information about professionals matching your search criteria.

## Response Structure

The API returns an object with the following main components:

| Field              | Type    | Description                                           |
|--------------------|---------|-------------------------------------------------------|
| profiles           | array   | Array of person profiles matching the search criteria  |
| total_display_count| string  | Total number of search results found                   |

## Profile Information

Each profile in the response contains the following fields:

| Field                        | Type    | Description                                                |
|------------------------------|---------|-----------------------------------------------------------|
| name                         | string  | Full name of the person                                    |
| location                     | string  | Geographic location of the person                          |
| linkedin_profile_url         | string  | LinkedIn profile URL (system format)                       |
| linkedin_profile_urn         | string  | LinkedIn profile unique identifier                         |
| default_position_title       | string  | Current job title                                          |
| default_position_company_linkedin_id | string | LinkedIn ID of the current employer                 |
| default_position_is_decision_maker | boolean | Whether the person is a decision maker               |
| flagship_profile_url         | string  | Human-readable LinkedIn profile URL                        |
| profile_picture_url          | string  | URL to profile picture                                     |
| headline                     | string  | LinkedIn headline                                          |
| summary                      | string  | Professional summary or bio                                |
| num_of_connections           | integer | Number of LinkedIn connections                             |
| related_colleague_company_id | integer | ID of related company                                      |
| skills                       | array   | List of professional skills                                |
| current_title                | string  | Current job title (normalized)                             |
| emails                     | array   | List of email addresses                         |
| websites                   | array   | List of personal websites                       |
| twitter_handle             | string  | Twitter username (can be null)                  |
| languages                  | array   | Languages spoken by the person                  |
| pronoun                    | string  | Preferred pronouns (can be null)                |
| query_person_linkedin_urn  | string  | LinkedIn URN used in the query                  |
| linkedin_slug_or_urns      | array   | Alternative LinkedIn identifiers                | 

## Employment History

The `employer` array contains the person's work history:

| Field                    | Type    | Description                                      |
|--------------------------|---------|--------------------------------------------------|
| employer                 | array   | List of employment entries                        |
| employer[].title         | string  | Job title                                         |
| employer[].company_name  | string  | Name of the employer                              |
| employer[].company_linkedin_id | string | LinkedIn ID of the company                   |
| employer[].company_logo_url | string | URL to company's logo                           |
| employer[].start_date    | string  | Employment start date (ISO format)                |
| employer[].end_date      | string  | Employment end date (ISO format, null if current) |
| employer[].position_id   | integer | Unique ID for the position                        |
| employer[].description   | string  | Job description (can be null)                     |
| employer[].location      | string  | Job location (can be null)                        |
| employer[].rich_media    | array   | Media associated with the position                |

## Education Background

The `education_background` array contains educational history:

| Field                                    | Type    | Description                                 |
|------------------------------------------|---------|---------------------------------------------|
| education_background                     | array   | List of education entries                    |
| education_background[].degree_name       | string  | Name of degree earned (can be null)          |
| education_background[].institute_name    | string  | Name of educational institution              |
| education_background[].field_of_study    | string  | Major or specialization                      |
| education_background[].start_date        | string  | Start date of education (can be null)        |
| education_background[].end_date          | string  | End date of education (can be null)          |
| education_background[].institute_linkedin_id | string | LinkedIn ID of the institution            |
| education_background[].institute_linkedin_url | string | LinkedIn URL of the institution          |
| education_background[].institute_logo_url | string | URL to institution's logo                    |

---

## 🔧 OpenAPI Specification

# Search API (realtime)

**Category:** People API
**Base URL:** https://api.crustdata.com
**Official Docs:** /docs/discover/people-apis/people-search-api

**Endpoint:** `POST /screener/person/search`

**Description:** Searches for people based on either a set of filters.
- **Filters**: Provide an array of filter_type, type, and value. 
  See [How to Build Filters](/docs/discover/people-apis/how-to-build-people-filters).
> [Show Docs](/docs/discover/people-apis/people-search-api)

## Authentication
This endpoint requires a Bearer token in the `Authorization` header:

```
Authorization: Token <YOUR_TOKEN>
```
## Request Body Schema

## Example Request

```bash
curl -X POST "https://api.crustdata.com/screener/person/search" \
  -H "Authorization: Token &lt;YOUR_TOKEN&gt;" \
  -H "Content-Type: application/json"
```

## Rate Limiting
All Crustdata API requests count toward your per-minute quota. Inspect the response headers `X-RateLimit-Limit` and `X-RateLimit-Remaining` to monitor usage. Implement exponential back-off or retries when you receive a **429 Too Many Requests** response.

## Responses
### Status 200
**Description:** A JSON response containing a list of people profiles found and the total number of profiles available.
**Response Schema:**
| Field | Type | Required | Description | Enum | Example |
|-------|------|----------|-------------|------|---------|
| `profiles` | array | No |  |  |  |
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
  PersonSearchRealtimeRequest:
    type: object

  FiltersPayload:
    type: object
    properties:
      filters:
        type: array
        description: "Each item contains filter_type, type, value. \nFor details, see [How to Build Filters](/docs/discover/people-apis/how-to-build-people-filters).\n"
      page:
        type: integer
        description: "The page number for pagination (starts from 1). Default is 1."

  PersonSearchResponse:
    type: object
    properties:
      name:
        type: string
        description: "Full name of the individual."
      location:
        type: string
        description: "Current location of the individual."
      linkedin_profile_url:
        type: string
        description: "URL of the individual's LinkedIn profile."
      linkedin_profile_urn:
        type: string
        description: "Unique identifier for the LinkedIn profile."
      default_position_title:
        type: string
        description: "Title of the individual's current position."
      # ... (17 more properties)

```

---

<!-- Error loading /docs/discover/people-apis/person-basic-profile-api -->

