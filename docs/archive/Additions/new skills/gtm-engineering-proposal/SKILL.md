---
name: gtm-engineering-proposal
description: Executes Crustdata APIs for TAM mapping (Company Discovery), decision maker discovery (People Discovery), and watcher configuration. This is a data retrieval skill - for strategic GTM analysis and proposal generation, use with the gtm-strategy-consultant agent.
---

<essential_principles>
## What This Skill Does

This skill provides Crustdata API procedures for GTM data collection:
1. TAM mapping using Company Discovery API
2. Decision maker counts using People Discovery API
3. Watcher configuration guidance

**For strategic analysis, ICP research, and proposal generation, use the `gtm-strategy-consultant` agent**, which loads this skill for data retrieval.

### API Execution - CRITICAL

**ALWAYS use the Crustdata API directly via Bash tool with curl.** The `CRUSTDATA_API_KEY` environment variable is available.

```bash
curl -X POST "https://api.crustdata.com/screener/companydb/search" \
  -H "Authorization: Bearer $CRUSTDATA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "filters": {...}, "limit": 1 }'
```

**DO NOT use Rube MCP tools** (RUBE_SEARCH_TOOLS, RUBE_MULTI_EXECUTE_TOOL, etc.) for Crustdata API calls. The API key is already configured - use it directly.

### Credit-Efficient Approach

- Company Discovery: 1 query with `limit: 1` = 1 credit (gets total_count)
- People Discovery: 1 query with `limit: 1` = 1 credit per seniority level
- Total for full TAM + decision maker preview: ~5 credits
</essential_principles>

<intake>
To execute GTM data collection, I need:

1. **Query type**: TAM mapping, decision maker discovery, or both
2. **ICP filters**: Industry, company size, geography, etc.
3. **Persona filters** (for decision makers): Titles, seniority levels

**For strategic proposals**, use the `gtm-strategy-consultant` agent which will invoke this skill with appropriate filters.
</intake>

<routing>
| Input | Workflow |
|-------|----------|
| TAM count query with ICP filters | `workflows/map-tam.md` |
| Decision maker count query | `workflows/find-decision-makers.md` |
| Watcher configuration guidance | Reference `references/watcher-api.md` |
| Full GTM proposal request | Redirect to `gtm-strategy-consultant` agent |
| ICP research / analysis | Redirect to `gtm-strategy-consultant` agent |
| Watcher recommendations | Redirect to `gtm-strategy-consultant` agent |
</routing>

<reference_index>
## API Documentation

All in `references/`:

- `company-api.md` - Company Discovery API v2 for TAM mapping
- `people-api.md` - People Discovery API for decision makers
- `watcher-api.md` - Watcher types, filters, payloads
</reference_index>

<workflows_index>
| Workflow | Purpose |
|----------|---------|
| `map-tam.md` | Execute Company Discovery API for TAM counts |
| `find-decision-makers.md` | Execute People Discovery API for decision maker counts |
</workflows_index>

<quick_reference>
## Quick API Reference

### Company Discovery API (TAM Mapping)

**Endpoint:** `POST https://api.crustdata.com/screener/companydb/search`

**Common Filters:**
```json
{
  "filters": [
    {"filter_type": "KEYWORD", "type": "in", "value": ["artificial intelligence"]},
    {"filter_type": "COMPANY_HEADCOUNT", "type": "in", "value": ["11-50", "51-200", "201-500"]},
    {"filter_type": "COMPANY_INDUSTRY", "type": "in", "value": ["Software Development"]},
    {"filter_type": "COMPANY_COUNTRY", "type": "in", "value": ["United States"]}
  ],
  "limit": 1
}
```

**Response:** Returns `total_count` and sample company data.

### People Discovery API (Decision Makers)

**Endpoint:** `POST https://api.crustdata.com/screener/person/search`

**Common Filters:**
```json
{
  "filters": [
    {"filter_type": "CURRENT_TITLE", "type": "in", "value": ["CTO", "VP Engineering", "Head of ML"]},
    {"filter_type": "COMPANY_HEADCOUNT", "type": "in", "value": ["11-50", "51-200", "201-500"]},
    {"filter_type": "SENIORITY", "type": "in", "value": ["CXO"]}
  ],
  "limit": 1
}
```

**Seniority Options:** `CXO`, `VP`, `Director`, `Manager`, `Individual Contributor`

**Response:** Returns `total_count` and sample person data.

### Watcher API (Signal Monitoring)

**Endpoint:** `POST https://api.crustdata.com/watcher/watches`

**See `references/watcher-api.md`** for full watcher types and filter options.
</quick_reference>

<success_criteria>
API execution is complete when:
- [ ] Query executed with `limit: 1` for credit efficiency
- [ ] `total_count` extracted from response
- [ ] Sample record documented (company or person)
- [ ] Exact filters used are documented for transparency
</success_criteria>
