# Stage 02: Transform & Process

## Purpose

Analyze extracted content using LLM to build structured company intelligence. This stage transforms raw website content into actionable insights about the company's profile, market positioning, products/services, and brand voice.

## Model

`claude-sonnet-4` - Complex reasoning for analysis and synthesis

## Inputs

| Name | Source | Description |
|------|--------|-------------|
| `scraped_pages` | Stage 01 | Array of scraped page objects |
| `raw_text_corpus` | Stage 01 | Combined text content |
| `extraction_metadata` | Stage 01 | Metrics about extraction |
| `company_name` | Stage 00 | Company name for context |
| `industry` | Stage 00 | Industry hint (if provided) |

## Process

### 1. Build Company Profile

Extract core company information:

```python
company_profile_prompt = """
Analyze the following website content for {company_name} and extract:

1. **Company Overview**
   - Official company name
   - One-paragraph description
   - Founded date (if available)
   - Headquarters location
   - Company size/employees (if mentioned)

2. **Mission & Vision**
   - Mission statement (exact if found, summarized if implied)
   - Vision statement (if available)
   - Core values (if stated)

Be precise and cite the source URL for each piece of information.
Only include information explicitly stated or clearly implied in the content.
Mark uncertain items as [inferred] or [not found].

Website Content:
{content}
"""

company_profile = llm_analyze(
    prompt=company_profile_prompt,
    content=get_pages(["home", "about"]),
    model="claude-sonnet-4"
)
```

### 2. Analyze Market Positioning

```python
positioning_prompt = """
Analyze how {company_name} positions itself in the market:

1. **Target Audience**
   - Who are they selling to?
   - Industry segments mentioned
   - Company sizes targeted (SMB, mid-market, enterprise)
   - Job titles/roles mentioned

2. **Ideal Customer Profile (ICP)**
   - Explicit ICP characteristics
   - Problems they solve for customers
   - Use cases highlighted

3. **Value Proposition**
   - Main value proposition (1-2 sentences)
   - Key benefits emphasized

4. **Differentiators**
   - How do they distinguish from competitors?
   - Unique features or approaches
   - Competitive advantages claimed

5. **Social Proof**
   - Customer logos/names
   - Testimonials themes
   - Case study highlights
   - Metrics/results mentioned

Website Content:
{content}
"""

market_positioning = llm_analyze(
    prompt=positioning_prompt,
    content=get_pages(["home", "products", "solutions", "customers"]),
    model="claude-sonnet-4"
)
```

### 3. Extract Products & Services

```python
products_prompt = """
Extract all products and services offered by {company_name}:

For each product/service, capture:
- **Name**: Product/service name
- **Description**: What it does (1-2 sentences)
- **Key Features**: Main features/capabilities
- **Pricing**: Pricing model if available (free, freemium, paid, enterprise, etc.)
- **Target User**: Who this is for

Also identify:
- Product tiers or editions
- Add-ons or modules
- Platform/integrations

Website Content:
{content}
"""

products_services = llm_analyze(
    prompt=products_prompt,
    content=get_pages(["products", "services", "solutions", "pricing"]),
    model="claude-sonnet-4"
)
```

### 4. Detect Brand Voice

```python
voice_prompt = """
Analyze the brand voice and messaging style of {company_name}:

1. **Tone Attributes**
   - Primary tone (e.g., professional, casual, authoritative, friendly)
   - Secondary tones
   - Emotional register

2. **Personality**
   - Brand personality traits
   - How they want to be perceived

3. **Formality Level**
   - Scale: Very Formal | Formal | Neutral | Casual | Very Casual
   - Consistency across pages

4. **Key Terms & Phrases**
   - Repeated words/phrases
   - Industry jargon used
   - Proprietary terms
   - Avoided language (if apparent)

5. **Messaging Themes**
   - Recurring themes in messaging
   - Core narrative elements
   - Brand promises

Provide 3-5 example quotes that exemplify their voice.

Website Content:
{content}
"""

brand_voice = llm_analyze(
    prompt=voice_prompt,
    content=get_pages(["home", "about", "blog"]),
    model="claude-sonnet-4"
)
```

### 5. Extract Key Messages

```python
messages_prompt = """
Identify the key messages {company_name} uses to communicate value:

1. **Headlines**: Main headlines used across the site
2. **Taglines**: Any taglines or slogans
3. **CTAs**: Call-to-action language
4. **Proof Points**: Specific metrics or claims
5. **Core Messages**: 3-5 core messages that summarize their communication

For each message, note:
- The exact text
- Where it appears
- The intent/purpose

Website Content:
{content}
"""

key_messages = llm_analyze(
    prompt=messages_prompt,
    content=get_pages(["home", "products"]),
    model="claude-sonnet-4"
)
```

### 6. Auto-Detect Industry (if not provided)

```python
if not inputs.get("industry"):
    industry_prompt = """
    Based on the website content, classify {company_name} into:

    1. **Primary Industry**: Most specific industry classification
    2. **Industry Category**: Broader category
    3. **Sub-vertical**: Any specific niche
    4. **Confidence**: High/Medium/Low

    Common categories: B2B SaaS, E-commerce, FinTech, HealthTech,
    MarTech, EdTech, HRTech, Manufacturing, Professional Services, etc.

    Website Content:
    {content}
    """

    industry = llm_analyze(
        prompt=industry_prompt,
        content=raw_text_corpus[:5000],
        model="claude-haiku"  # Simple classification
    )
```

### 7. Quality Scoring

```python
# Calculate confidence scores for each section
quality_metrics = {
    "company_profile": score_completeness(company_profile, required_fields=["name", "description"]),
    "market_positioning": score_completeness(market_positioning, required_fields=["target_audience", "value_proposition"]),
    "products_services": 1.0 if len(products_services) >= 1 else 0.5,
    "brand_voice": score_completeness(brand_voice, required_fields=["tone", "personality"]),
    "key_messages": 1.0 if len(key_messages) >= 3 else 0.5,
    "sources_cited": count_source_citations(all_outputs) / expected_citations
}

overall_confidence = weighted_average(quality_metrics)
```

## Output

| Name | Type | Description |
|------|------|-------------|
| `company_profile` | object | Structured company information |
| `market_positioning` | object | Target audience, ICP, value props |
| `products_services` | array | Products and services catalog |
| `brand_voice` | object | Voice attributes and examples |
| `key_messages` | array | Core messaging themes |
| `industry` | string | Detected or provided industry |
| `quality_metrics` | object | Confidence scores per section |
| `transform_metadata` | object | Processing stats |

## Checkpoint

Creates checkpoint at `checkpoints/02-transform.json`

```json
{
  "stage": "02-transform",
  "timestamp": "2024-01-15T10:35:00Z",
  "quality_score": 0.85,
  "data": {
    "company_profile": {...},
    "market_positioning": {...},
    "products_services": [...],
    "brand_voice": {...},
    "key_messages": [...],
    "quality_metrics": {...}
  }
}
```

## Context Management

| Input Size | Strategy |
|------------|----------|
| < 8K tokens per section | Process directly with Sonnet |
| 8K-20K tokens | Summarize first with Haiku, then analyze with Sonnet |
| > 20K tokens | Chunk by page, extract key points, synthesize |

## Error Handling

| Error | Trigger | Action |
|-------|---------|--------|
| LLM extraction failed | Model error or timeout | Retry with backoff, fall back to Haiku |
| Low confidence output | Quality score < 0.6 | Flag for human review |
| Missing required fields | Company name or description empty | Extract from raw text, mark as [inferred] |
| Industry uncertain | Low confidence on auto-detect | Flag for verification |

## Quality Thresholds

| Metric | Minimum | Target | Action if Below |
|--------|---------|--------|-----------------|
| Overall confidence | 0.6 | 0.8+ | Human review |
| Company profile completeness | 0.7 | 0.9 | Attempt re-extraction |
| Products identified | 1 | 3+ | Warn, continue |
| Voice attributes detected | 3 | 5+ | Continue |
| Source citations | 50% | 90% | Flag uncited claims |

## Success Criteria

- [ ] Company name and description extracted
- [ ] At least 1 product/service identified
- [ ] Target audience identified
- [ ] Brand voice attributes detected (3+)
- [ ] Key messages extracted (3+)
- [ ] All claims have source URLs
- [ ] Overall confidence >= 0.6
- [ ] Checkpoint saved
