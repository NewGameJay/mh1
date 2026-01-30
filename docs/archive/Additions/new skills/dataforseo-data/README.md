# DataForSEO Data Skill

**Status:** ✅ Ready for Testing

A Claude Code skill for fetching SEO data using DataForSEO API. Supports SERP analysis and keyword research.

---

## Quick Start

### 1. Install Dependencies

```bash
pip install requests
```

### 2. Verify Setup

```bash
python verify_setup.py
```

### 3. Use the Skill

In Claude Code:

```
"Get Google search results for 'fractional CMO' and 'marketing consultant' in the US"
```

---

## Configuration

### Credentials
The skill is pre-configured with the provided Base64 credentials:
`am9zZXBoLnF1ZXNhZGFAbWFya2V0ZXJoaXJlLmNvbToxMzk1OGIyNzNkNjZmMDEw`

### Common Parameters

**Location Codes:**
- 2840: United States
- 2826: United Kingdom
- 2124: Canada
- 2036: Australia

**Language Codes:**
- en: English
- es: Spanish
- fr: French
- de: German

---

## Output Files

- `{project}_serp_{timestamp}.csv`: Ranked organic results
- `{project}_serp_raw_{timestamp}.json`: Full raw API response

---

## API Reference

This skill uses DataForSEO V3 API.
- SERP API: `v3/serp/google/organic/live/advanced`
- Keyword API: `v3/dataforseo_labs/google/keyword_suggestions/live` (to be implemented if needed)



