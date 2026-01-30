# Stage 01: Data Extraction

## Purpose

Scrape and extract raw content from the company website and any additional URLs using Firecrawl MCP. This stage focuses on gathering as much relevant content as possible within the configured depth limits.

## Model

`claude-haiku` - Fast, efficient for initial content processing and filtering

## Inputs

| Name | Source | Description |
|------|--------|-------------|
| `validated_inputs` | Stage 00 | Validated input parameters |
| `website_url` | Stage 00 | Primary website URL |
| `additional_urls` | Stage 00 | Validated additional URLs |
| `depth_config` | Stage 00 | Depth configuration (max_pages, timeout) |

## Process

### 1. Initialize Firecrawl Scraper

```python
from lib.mcp import firecrawl

scraper = firecrawl.create_scraper(
    max_pages=depth_config["max_pages"],
    timeout=depth_config["timeout_seconds"],
    respect_robots_txt=True
)
```

### 2. Scrape Primary Website

```python
# Define priority paths for structured scraping
priority_paths = [
    "/",              # Home page
    "/about",         # About page
    "/about-us",      # About page variant
    "/products",      # Products page
    "/services",      # Services page
    "/solutions",     # Solutions page
    "/pricing",       # Pricing page
    "/team",          # Team page
    "/customers",     # Customer case studies
    "/blog"           # Blog for voice analysis
]

# Start with priority pages
scraped_pages = []
for path in priority_paths:
    full_url = urljoin(website_url, path)
    try:
        page_content = scraper.scrape(full_url)
        if page_content and page_content.text:
            scraped_pages.append({
                "url": full_url,
                "title": page_content.title,
                "content": page_content.text,
                "html": page_content.html,
                "metadata": page_content.metadata,
                "scraped_at": datetime.now().isoformat()
            })
    except ScrapingError as e:
        log_warning(f"Could not scrape {full_url}: {e}")

# If under max_pages, crawl additional discovered pages
remaining_budget = depth_config["max_pages"] - len(scraped_pages)
if remaining_budget > 0:
    additional_pages = scraper.crawl(
        website_url,
        max_pages=remaining_budget,
        exclude_paths=[p["url"] for p in scraped_pages]
    )
    scraped_pages.extend(additional_pages)
```

### 3. Scrape Additional URLs

```python
for url in additional_urls:
    if len(scraped_pages) < depth_config["max_pages"]:
        try:
            page_content = scraper.scrape(url)
            if page_content and page_content.text:
                scraped_pages.append({
                    "url": url,
                    "title": page_content.title,
                    "content": page_content.text,
                    "source": "additional_url"
                })
        except ScrapingError as e:
            log_warning(f"Could not scrape additional URL {url}: {e}")
```

### 4. Extract Structured Content

For each scraped page, extract structured elements:

```python
for page in scraped_pages:
    # Extract using Haiku for fast processing
    page["extracted"] = extract_page_elements(page["html"], model="claude-haiku")

    # Elements to extract:
    # - Headlines and subheadlines
    # - Product/service descriptions
    # - Feature lists
    # - Testimonials and quotes
    # - CTAs and value propositions
    # - Team member info
    # - Contact information
```

### 5. Calculate Extraction Metrics

```python
extraction_metadata = {
    "pages_scraped": len(scraped_pages),
    "total_content_kb": sum(len(p["content"]) for p in scraped_pages) / 1024,
    "urls_attempted": len(priority_paths) + len(additional_urls),
    "scraping_time_seconds": scraper.elapsed_time,
    "pages_by_section": categorize_pages(scraped_pages)
}

# Check data sufficiency
if extraction_metadata["pages_scraped"] < config["min_pages_scraped"]:
    log_warning(f"Only scraped {extraction_metadata['pages_scraped']} pages (minimum: {config['min_pages_scraped']})")

if extraction_metadata["total_content_kb"] < config["min_content_kb"]:
    log_warning(f"Only extracted {extraction_metadata['total_content_kb']:.1f}KB (minimum: {config['min_content_kb']}KB)")
```

## Output

| Name | Type | Description |
|------|------|-------------|
| `scraped_pages` | array | Array of scraped page objects |
| `extraction_metadata` | object | Metrics about the extraction |
| `content_by_type` | object | Content organized by type (about, products, blog, etc.) |
| `raw_text_corpus` | string | Combined text content for analysis |

## Checkpoint

Creates checkpoint at `checkpoints/01-extract.json`

```json
{
  "stage": "01-extract",
  "timestamp": "2024-01-15T10:30:00Z",
  "pages_scraped": 15,
  "content_kb": 45.2,
  "data": {
    "scraped_pages": [...],
    "extraction_metadata": {...}
  }
}
```

Can resume from this checkpoint if later stages fail.

## Context Management

| Content Size | Strategy |
|-------------|----------|
| < 8K tokens | Pass directly to Stage 02 |
| 8K-50K tokens | Chunk by page, summarize with Haiku |
| > 50K tokens | Use ContextManager, extract key sections only |

## Error Handling

| Error | Trigger | Action |
|-------|---------|--------|
| Scraping blocked | Cloudflare, CAPTCHA, rate limit | Log error, mark for human review |
| Partial scrape | Some pages failed | Continue with available pages, log warnings |
| Insufficient content | Below minimum threshold | Continue with warning, lower confidence score |
| Timeout | Exceeded depth timeout | Save partial results, continue |
| No content | Zero pages successfully scraped | Abort with error |

## Data Sufficiency Checks

| Requirement | Minimum | Recommended | On Insufficient |
|-------------|---------|-------------|-----------------|
| Pages scraped | 3 | 20+ | warn_and_continue |
| Content extracted | 5KB | 50KB+ | warn_and_continue |
| Home page | Yes | Yes | warn_and_continue |
| About page | No | Yes | continue |

## Success Criteria

- [ ] At least 3 pages successfully scraped
- [ ] Home page content extracted
- [ ] At least 5KB of content extracted
- [ ] No critical scraping errors
- [ ] Checkpoint saved
