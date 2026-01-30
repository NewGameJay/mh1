# Company Research: {{ company_name }}

**Client:** {{ client_id }}
**Generated:** {{ timestamp }}
**Skill Version:** {{ version }}

---

## Executive Summary

{{ company_profile.description }}

### Key Metrics

| Metric | Value |
|--------|-------|
| Industry | {{ industry }} |
| Pages Analyzed | {{ _meta.pages_scraped }} |
| Confidence Score | {{ evaluation.score | percentage }} |
| Execution Time | {{ _meta.runtime_seconds | duration }} |

---

## Company Profile

| Field | Value |
|-------|-------|
| **Name** | {{ company_profile.name }} |
| **Website** | {{ website_url }} |
| **Industry** | {{ industry }} |
| **Founded** | {{ company_profile.founded | default: "Not available" }} |
| **Headquarters** | {{ company_profile.headquarters | default: "Not available" }} |
| **Company Size** | {{ company_profile.size | default: "Not available" }} |

### Description

{{ company_profile.description }}

{{ #if company_profile.mission }}
### Mission

{{ company_profile.mission }}
{{ /if }}

{{ #if company_profile.vision }}
### Vision

{{ company_profile.vision }}
{{ /if }}

{{ #if company_profile.core_values.length }}
### Core Values

{{ #each company_profile.core_values }}
- {{ this }}
{{ /each }}
{{ /if }}

---

## Market Positioning

### Target Audience

{{ market_positioning.target_audience }}

{{ #if market_positioning.icp }}
### Ideal Customer Profile (ICP)

{{ #if market_positioning.icp.industries.length }}
**Industries:**
{{ #each market_positioning.icp.industries }}
- {{ this }}
{{ /each }}
{{ /if }}

{{ #if market_positioning.icp.company_sizes.length }}
**Company Sizes:**
{{ #each market_positioning.icp.company_sizes }}
- {{ this }}
{{ /each }}
{{ /if }}

{{ #if market_positioning.icp.job_titles.length }}
**Key Personas:**
{{ #each market_positioning.icp.job_titles }}
- {{ this }}
{{ /each }}
{{ /if }}

{{ #if market_positioning.icp.pain_points.length }}
**Pain Points Addressed:**
{{ #each market_positioning.icp.pain_points }}
- {{ this }}
{{ /each }}
{{ /if }}
{{ /if }}

### Value Proposition

{{ market_positioning.value_proposition }}

{{ #if market_positioning.differentiators.length }}
### Differentiators

{{ #each market_positioning.differentiators }}
- {{ this }}
{{ /each }}
{{ /if }}

{{ #if market_positioning.competitive_advantages.length }}
### Competitive Advantages

{{ #each market_positioning.competitive_advantages }}
- {{ this }}
{{ /each }}
{{ /if }}

{{ #if market_positioning.social_proof }}
### Social Proof

{{ #if market_positioning.social_proof.customer_logos.length }}
**Notable Customers:**
{{ #each market_positioning.social_proof.customer_logos }}
- {{ this }}
{{ /each }}
{{ /if }}

{{ #if market_positioning.social_proof.metrics.length }}
**Key Metrics:**
{{ #each market_positioning.social_proof.metrics }}
- {{ this }}
{{ /each }}
{{ /if }}
{{ /if }}

---

## Products & Services

{{ #each products_services }}
### {{ this.name }}

{{ this.description }}

{{ #if this.features.length }}
**Key Features:**
{{ #each this.features }}
- {{ this }}
{{ /each }}
{{ /if }}

{{ #if this.pricing }}
**Pricing:** {{ this.pricing }}
{{ /if }}

{{ #if this.target_user }}
**Target User:** {{ this.target_user }}
{{ /if }}

---
{{ /each }}

## Brand Voice

### Tone & Personality

**Primary Tone:** {{ brand_voice.tone | join: ", " }}

**Personality:** {{ brand_voice.personality }}

**Formality Level:** {{ brand_voice.formality_level | humanize }}

{{ #if brand_voice.key_terms.length }}
### Key Terms & Phrases

{{ #each brand_voice.key_terms }}
- {{ this }}
{{ /each }}
{{ /if }}

{{ #if brand_voice.messaging_themes.length }}
### Messaging Themes

{{ #each brand_voice.messaging_themes }}
- {{ this }}
{{ /each }}
{{ /if }}

{{ #if brand_voice.example_quotes.length }}
### Example Quotes

{{ #each brand_voice.example_quotes }}
> "{{ this }}"

{{ /each }}
{{ /if }}

---

## Key Messages

{{ #each key_messages }}
{{ @index | plus: 1 }}. {{ this }}
{{ /each }}

---

## Quality Assessment

| Gate | Status | Score |
|------|--------|-------|
| Schema Validation | {{ quality_gates.schema_valid | check }} | - |
| Completeness | {{ quality_gates.completeness_score >= 0.7 | check }} | {{ quality_gates.completeness_score | percentage }} |
| Sources Cited | {{ sources.length >= 3 | check }} | {{ sources.length }} sources |

**Overall Score:** {{ evaluation.score | percentage }}
**Release Action:** {{ release_action }}

{{ #if _meta.warnings.length }}
### Warnings

{{ #each _meta.warnings }}
- {{ this }}
{{ /each }}
{{ /if }}

---

## Sources

{{ #each sources }}
- [{{ this.title }}]({{ this.url }}) - {{ this.section }}
{{ /each }}

---

## Research Methodology

This research was conducted using automated website analysis with the following stages:

1. **Setup & Validation** - Verified website accessibility and input parameters
2. **Data Extraction** - Scraped {{ _meta.pages_scraped }} pages using Firecrawl
3. **Transform & Process** - Analyzed content for company insights
4. **Output Generation** - Synthesized findings into structured format

### Execution Details

- **Total API Calls:** {{ _meta.tokens.total | number }}
- **Tokens Used:** {{ _meta.tokens.total | number }}
- **Cost:** ${{ _meta.cost_usd | number: 2 }}
- **Runtime:** {{ _meta.runtime_seconds | duration }}

---

## Next Steps

Based on this research, recommended next actions:

1. **Validate Key Findings** - Review extracted information with client
2. **Competitor Research** - Run competitor analysis using identified differentiators
3. **Founder Research** - Research key leadership for interview preparation
4. **Voice Contract** - Use brand voice findings to build voice contract

---

*Generated by MH1 research-company v{{ version }}*
*Run ID: {{ _meta.run_id }}*
