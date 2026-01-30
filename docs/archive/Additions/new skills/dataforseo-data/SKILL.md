---
name: dataforseo-data
description: Fetch SEO data including SERP results, keyword data, and competitor analysis from DataForSEO API. Activates when user needs to analyze search engine results, track keyword rankings, check competitor backlinks, or gather SEO metrics. Handles API authentication and data retrieval automatically.
allowed-tools: Read, Write, Edit, Bash, Glob
---

# DataForSEO Data Skill

This skill helps you collect and analyze SEO data using the DataForSEO API. Perfect for competitive intelligence, rank tracking, keyword research, and SERP analysis.

## What This Skill Does

1. **SERP Analysis**: Get Google search results (organic, paid, featured snippets) for specific keywords
2. **Keyword Research**: Get search volume, CPC, and competition data
3. **Competitor Analysis**: Track competitor rankings and visibility
4. **Data Export**: Generate clean CSV/JSON files with SEO metrics
5. **Automated Reporting**: Create summary reports on search visibility

## When to Use This Skill

- Analyzing search engine results pages (SERPs)
- checking keyword search volumes and trends
- Monitoring competitor rankings
- Gathering data for SEO audits
- researching content topics based on search intent

## Prerequisites

Before using this skill, ensure you have:
- Python 3.7+ installed
- The `requests` library installed (`pip install requests`)
- DataForSEO API credentials (login and password)

**Note:** Credentials are pre-configured in the templates.

## Instructions

### Step 1: Gather Requirements

Ask the user for the following information:

**Required:**
- **Target Keywords**: Keywords to analyze (e.g., "marketing automation", "crm software")
- **Location**: Target location code or name (e.g., "United States", "London")
- **Language**: Target language code or name (e.g., "en", "English")

**Optional:**
- **Search Engine**: Google, Bing, etc. (default: Google)
- **Device**: Desktop or Mobile (default: Desktop)
- **Depth**: Top 10, Top 100, etc.

### Step 2: Create or Update Collection Script

Using the template in `dataforseo_template.py`, create a customized script:

1. **Configure API credentials** (use existing)
2. **Set target parameters** (keywords, location, language)
3. **Choose API endpoint** (SERP, Keyword Data, etc.)

### Step 3: Run Collection

Execute the collection script:
```bash
python dataforseo_task.py
```

### Step 4: Generate Report

Create a summary document including:
- Top ranking URLs for target keywords
- Search volume and CPC data
- Competitor visibility analysis
- SERP feature analysis (snippets, maps, etc.)

## Output Files

Standard naming convention:
- `{project}_serp_{timestamp}.csv` - SERP data
- `{project}_keywords_{timestamp}.csv` - Keyword data
- `{project}_seo_report_{timestamp}.md` - Analysis report
- `dataforseo_task.py` - Collection script (reusable)

## Tips for Success

1. **Rate Limiting**: DataForSEO charges per request. Use specific targeting to avoid waste.
2. **Asynchronous vs Live**: The Live API is faster for small checks; Standard API is better for bulk.
3. **Location Precision**: You can target specific cities or coordinates.

