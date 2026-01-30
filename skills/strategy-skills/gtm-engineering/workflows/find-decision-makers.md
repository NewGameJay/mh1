# Workflow: Find Decision Makers with People Discovery API

<objective>
Execute the Crustdata People Discovery API to get decision maker counts by seniority level. Returns `total_count` and sample profiles.

**For buyer persona research and filter selection**, use the `gtm-strategy-consultant` agent first, which will invoke this workflow with appropriate filters.
</objective>

<required_inputs>
Before executing, you need:
1. **Title filters** - Job titles to target (e.g., "CTO", "VP Engineering")
2. **Seniority filters** - Levels to count (CXO, VP, Director, Manager)
3. **Company filters** - Industry, size, geography to match TAM

If you don't have persona filters defined, redirect to the `gtm-strategy-consultant` agent.
</required_inputs>

<process>
## Step 1: Build Seniority Breakdown Queries

Create separate queries for each seniority level:

### Query 1: CXO Count
```bash
curl -X POST "https://api.crustdata.com/screener/person/search" \
  -H "Authorization: Bearer $CRUSTDATA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [
      {"filter_type": "CURRENT_TITLE", "type": "in", "value": ["CTO", "CEO", "Chief Technology Officer"]},
      {"filter_type": "COMPANY_HEADCOUNT", "type": "in", "value": ["11-50", "51-200", "201-500"]},
      {"filter_type": "SENIORITY", "type": "in", "value": ["CXO"]}
    ],
    "limit": 1
  }'
```

### Query 2: VP Count
```bash
curl -X POST "https://api.crustdata.com/screener/person/search" \
  -H "Authorization: Bearer $CRUSTDATA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [
      {"filter_type": "CURRENT_TITLE", "type": "in", "value": ["VP Engineering", "VP Product", "VP Sales"]},
      {"filter_type": "COMPANY_HEADCOUNT", "type": "in", "value": ["11-50", "51-200", "201-500"]},
      {"filter_type": "SENIORITY", "type": "in", "value": ["VP"]}
    ],
    "limit": 1
  }'
```

### Query 3: Director Count
```bash
curl -X POST "https://api.crustdata.com/screener/person/search" \
  -H "Authorization: Bearer $CRUSTDATA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [
      {"filter_type": "CURRENT_TITLE", "type": "in", "value": ["Director Engineering", "Director Product"]},
      {"filter_type": "COMPANY_HEADCOUNT", "type": "in", "value": ["11-50", "51-200", "201-500"]},
      {"filter_type": "SENIORITY", "type": "in", "value": ["Director"]}
    ],
    "limit": 1
  }'
```

### Query 4: Manager Count
```bash
curl -X POST "https://api.crustdata.com/screener/person/search" \
  -H "Authorization: Bearer $CRUSTDATA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [
      {"filter_type": "CURRENT_TITLE", "type": "in", "value": ["Engineering Manager", "Product Manager"]},
      {"filter_type": "COMPANY_HEADCOUNT", "type": "in", "value": ["11-50", "51-200", "201-500"]},
      {"filter_type": "SENIORITY", "type": "in", "value": ["Manager"]}
    ],
    "limit": 1
  }'
```

## Step 2: Execute Queries

For each query, execute and extract:
1. **`total_count`** - Decision maker count for that seniority
2. **Sample profile** - Name, title, company from first result

## Step 3: Document Output

Return:
- Total count (sum of all seniority levels)
- Breakdown by seniority level
- Sample profiles for each level
- Filters used (for transparency)

**Credit Budget:** 4 seniority queries = 4 credits
</process>

<common_filters>
## Common Persona Filter Combinations

### Engineering Leaders
```json
{
  "filters": [
    {"filter_type": "CURRENT_TITLE", "type": "in", "value": ["CTO", "VP Engineering", "Head of Engineering", "Director Engineering"]},
    {"filter_type": "COMPANY_HEADCOUNT", "type": "in", "value": ["51-200", "201-500"]},
    {"filter_type": "SENIORITY", "type": "in", "value": ["CXO", "VP", "Director"]}
  ],
  "limit": 1
}
```

### ML/Data Leaders
```json
{
  "filters": [
    {"filter_type": "CURRENT_TITLE", "type": "in", "value": ["Head of ML", "VP Data", "Chief AI Officer", "Director Data Science"]},
    {"filter_type": "COMPANY_HEADCOUNT", "type": "in", "value": ["51-200", "201-500"]}
  ],
  "limit": 1
}
```

### Sales Leaders
```json
{
  "filters": [
    {"filter_type": "CURRENT_TITLE", "type": "in", "value": ["VP Sales", "CRO", "Head of Sales", "Director Sales"]},
    {"filter_type": "COMPANY_HEADCOUNT", "type": "in", "value": ["51-200", "201-500"]}
  ],
  "limit": 1
}
```

### Marketing Leaders
```json
{
  "filters": [
    {"filter_type": "CURRENT_TITLE", "type": "in", "value": ["CMO", "VP Marketing", "Head of Marketing", "Director Marketing"]},
    {"filter_type": "COMPANY_HEADCOUNT", "type": "in", "value": ["51-200", "201-500"]}
  ],
  "limit": 1
}
```
</common_filters>

<optional_department_breakdown>
## Optional: Department Breakdown

For function-specific segmentation, run additional queries:

```bash
# Engineering function
curl -X POST "https://api.crustdata.com/screener/person/search" \
  -H "Authorization: Bearer $CRUSTDATA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [
      {"filter_type": "CURRENT_TITLE", "type": "in", "value": ["Engineering"]},
      {"filter_type": "SENIORITY", "type": "in", "value": ["VP", "Director"]}
    ],
    "limit": 1
  }'
```

**Additional Credit Budget:** 3-4 function queries = 3-4 credits
</optional_department_breakdown>

<api_reference>
See `references/people-api.md` for complete filter documentation.
</api_reference>

<success_criteria>
Decision maker discovery is complete when:
- [ ] Seniority breakdown queries executed (CXO, VP, Director, Manager)
- [ ] `total_count` extracted from each query
- [ ] Sample profiles documented for each level
- [ ] Filters documented for transparency
</success_criteria>
