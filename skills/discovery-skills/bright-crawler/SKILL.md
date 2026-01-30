---
name: bright-crawler
description: |
  Prompt-driven browser automation for web extraction.
  Accepts natural language prompts or structured prompt files.
  Handles login, navigation, and content extraction autonomously.
license: Proprietary
metadata:
  author: mh1-engineering
  version: "3.0.0"
  status: active
  created: "2026-01-29"
  updated: "2026-01-29"
  tags:
    - browser
    - extraction
    - automation
allowed-tools: Read Write Bash
---

# Bright Crawler

**Prompt-driven browser automation.** Give it a URL and tell it what to extract. It handles the rest.

---

## Usage

### From a User Prompt

```
Extract all courses from Demand Curve. Login with vbp615@gmail.com / Temp1pass!
Save each course to demandcurve-courses/{slug}.md
```

### From a Prompt File

```yaml
# extraction-job.yaml
source: https://www.demandcurve.com
login:
  url: /log-in
  email: vbp615@gmail.com
  password: Temp1pass!

targets:
  - name: courses
    path: /explore-curriculum
    pattern: course-cards → lessons → content
    output: demandcurve-courses/{slug}.md

  - name: tactics
    path: /tactics-vault
    filters: [Ads, Analytics, CRO, Email, SEO]
    count: 3 per filter
    output: demandcurve-tactics/{filter}.md
```

---

## How It Works

### 1. Parse Intent
The skill reads your prompt and identifies:
- **Source URL** - Where to start
- **Credentials** - If login is needed
- **Targets** - What content to extract
- **Output** - Where to save

### 2. Execute Browser Session
```python
from skills.bright_crawler import BrightCrawler

crawler = BrightCrawler()
crawler.run(prompt)  # Natural language or file path
```

### 3. Autonomous Navigation
The crawler:
- Detects login forms and authenticates
- Finds target content via selectors or text matching
- Handles pagination, modals, infinite scroll
- Extracts text/images/structured data
- Saves to specified output format

---

## Python Interface

```python
from skills.bright_crawler import BrightCrawler

# Natural language prompt
crawler = BrightCrawler()
crawler.run("Extract the pricing page from stripe.com, save to stripe-pricing.md")

# Structured job
crawler.run_job({
    "source": "https://example.com",
    "login": {"email": "user@test.com", "password": "pass"},
    "targets": [
        {"path": "/docs", "output": "docs/"}
    ]
})

# Or from YAML file
crawler.run_file("extraction-job.yaml")
```

---

## Extraction Patterns

### Course/Lesson Pattern
```yaml
pattern: course-list → course-page → lessons → content
```
Crawler will:
1. Find all course links on list page
2. Visit each course page
3. Navigate through all lessons
4. Extract lesson content
5. Save to MD files

### Paginated List Pattern
```yaml
pattern: list-page → item-modal
filters: [Category1, Category2]
count: 3 per filter
```
Crawler will:
1. Click each filter
2. Open first 3 items
3. Extract modal content
4. Continue to next filter

### Single Page Pattern
```yaml
pattern: page → content
selector: article.main-content
```
Crawler will:
1. Navigate to page
2. Extract content from selector
3. Save to output

---

## Browser Modes

| Mode | Flag | Use Case |
|------|------|----------|
| **headless** | default | Fast, public sites |
| **headed** | `--headed` | Debug, see what's happening |
| **real** | `--browser real` | Use your Chrome with cookies |

```python
crawler = BrightCrawler(mode="real")  # Use logged-in Chrome
```

---

## CLI Usage

```bash
# From prompt
bright-crawler "Extract all blog posts from company.com/blog"

# From file
bright-crawler --job extraction-job.yaml

# With options
bright-crawler --headed --output ./output "Extract pricing from stripe.com"
```

---

## Output Formats

### Markdown (default)
```yaml
output: docs/{slug}.md
```

### JSON
```yaml
output: data/{slug}.json
format: json
```

### Images
```yaml
output: images/
download: [img, video]
```

---

## Login Handling

The crawler auto-detects login forms by looking for:
- `input[type=email]` or `input[name*=email]`
- `input[type=password]`
- Submit buttons

You provide credentials, it handles the flow:

```yaml
login:
  url: /login  # or /sign-in, /auth, etc.
  email: user@example.com
  password: secret123
  # Optional: handle MFA
  mfa_type: email_code  # or totp, sms
```

---

## State Management

Sessions persist automatically:
```python
crawler = BrightCrawler(session="demandcurve")
crawler.login(url, creds)  # Now authenticated
# Later...
crawler = BrightCrawler(session="demandcurve")  # Still logged in
```

---

## Error Handling

The crawler handles common issues:
- **Bot detection**: Escalates to real browser mode
- **Rate limiting**: Auto-waits and retries
- **Broken selectors**: Falls back to text matching
- **Timeouts**: Retries with exponential backoff

---

## Integration

### With Agents
```python
# In an agent's workflow
from skills.bright_crawler import BrightCrawler

def extract_knowledge(prompt):
    crawler = BrightCrawler()
    results = crawler.run(prompt)
    return results
```

### With Other Skills
- **research-company**: Crawl company resources
- **content-extractor**: Feed extracted content
- **knowledge-ingestion**: Save to knowledge base

---

## Examples

### Extract Demand Curve Courses
```
Extract all 49 courses from Demand Curve.
Login: vbp615@gmail.com / Temp1pass!
Navigate to /explore-curriculum
For each course: extract all lessons
Save to: demandcurve-courses/{course-slug}.md
```

### Extract Newsletter Archive
```
Extract 10 most recent newsletters from demandcurve.com/newsletter-vault
Login first, then open each newsletter card
Save to: newsletters/{number}.md
```

### Extract Competitor Pricing
```
Go to competitor.com/pricing
Extract all plan names, prices, and features
Save as JSON to competitor-pricing.json
```

---

## Rate Limits & Ethics

- **Default delay**: 1-2s between requests
- **Respect robots.txt**: When reasonable
- **Don't overwhelm**: Max 10 concurrent requests
- **Your access only**: Don't bypass auth you don't have
