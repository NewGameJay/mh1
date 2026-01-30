# Workflow: Map TAM with Company Discovery API

<objective>
Execute the Crustdata Company Discovery API to get a TAM count for a given set of ICP filters. Returns `total_count` and a sample company.

**For ICP research and filter selection**, use the `gtm-strategy-consultant` agent first, which will invoke this workflow with appropriate filters.
</objective>

<required_inputs>
Before executing, you need:
1. **ICP filters** - Industry, company size, geography, keywords, etc.
2. **Limit** - Use `limit: 1` for credit-efficient counts (default)

If you don't have ICP filters defined, redirect to the `gtm-strategy-consultant` agent.
</required_inputs>

<process>
## Step 1: Build the Query

Translate ICP characteristics to Company API filters:

| ICP Dimension | API Filter | Example Value |
|---------------|------------|---------------|
| Industry keyword | `KEYWORD` | `["artificial intelligence"]` |
| Industry category | `COMPANY_INDUSTRY` | `["Software Development"]` |
| Company Size | `COMPANY_HEADCOUNT` | `["11-50", "51-200", "201-500"]` |
| Geography | `COMPANY_COUNTRY` | `["United States"]` |
| Funding Stage | `LAST_FUNDING_ROUND` | `["Seed", "Series A", "Series B"]` |

## Step 2: Execute the Query

```bash
curl -X POST "https://api.crustdata.com/screener/companydb/search" \
  -H "Authorization: Bearer $CRUSTDATA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [
      {"filter_type": "KEYWORD", "type": "in", "value": ["your keyword"]},
      {"filter_type": "COMPANY_HEADCOUNT", "type": "in", "value": ["11-50", "51-200", "201-500"]}
    ],
    "limit": 1
  }'
```

## Step 3: Extract Results

From the response, extract:
1. **`total_count`** - The TAM size
2. **Sample company** - Name, headcount, industry, location from the first result

## Step 4: Document Output

Return:
- TAM count
- Filters used (for transparency)
- Sample company details
</process>

<segmented_queries>
## Optional: Segmented TAM Breakdown

For detailed analysis, run additional queries to break down TAM by segments:

**By Industry Vertical:**
- Add industry filter to base query, run for each vertical

**By Funding Stage:**
- Add `LAST_FUNDING_ROUND` filter for each stage (Seed, Series A, B, C+)

**By Company Size:**
- Adjust `COMPANY_HEADCOUNT` range for each segment

**Credit Budget:** ~10-12 queries for full segmented view (1 credit each)
</segmented_queries>

<common_filters>
## Common Filter Combinations

### Tech/SaaS Companies (Growth Stage)
```json
{
  "filters": [
    {"filter_type": "COMPANY_INDUSTRY", "type": "in", "value": ["Software Development", "Technology"]},
    {"filter_type": "COMPANY_HEADCOUNT", "type": "in", "value": ["11-50", "51-200", "201-500"]}
  ],
  "limit": 1
}
```

### AI/ML Companies
```json
{
  "filters": [
    {"filter_type": "KEYWORD", "type": "in", "value": ["artificial intelligence", "machine learning"]},
    {"filter_type": "COMPANY_HEADCOUNT", "type": "in", "value": ["11-50", "51-200"]}
  ],
  "limit": 1
}
```

### Recently Funded Startups
```json
{
  "filters": [
    {"filter_type": "LAST_FUNDING_ROUND", "type": "in", "value": ["Seed", "Series A", "Series B"]},
    {"filter_type": "COMPANY_HEADCOUNT", "type": "in", "value": ["11-50", "51-200"]}
  ],
  "limit": 1
}
```

### US-Based Companies
```json
{
  "filters": [
    {"filter_type": "COMPANY_COUNTRY", "type": "in", "value": ["United States"]},
    {"filter_type": "COMPANY_HEADCOUNT", "type": "in", "value": ["51-200", "201-500"]}
  ],
  "limit": 1
}
```
</common_filters>

<api_reference>
See `references/company-api.md` for complete filter documentation.
</api_reference>

<success_criteria>
TAM mapping is complete when:
- [ ] Query executed with `limit: 1`
- [ ] `total_count` extracted from response
- [ ] Sample company documented
- [ ] Filters documented for transparency
</success_criteria>
