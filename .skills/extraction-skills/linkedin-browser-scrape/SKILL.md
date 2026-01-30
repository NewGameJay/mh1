---
name: linkedin-browser-scrape
description: |
  Scrape LinkedIn profiles and posts using browser automation when APIs fail or return incomplete data.
  Use when asked to 'scrape LinkedIn profile', 'get LinkedIn reactions', 'browser scrape LinkedIn',
  'fetch full profile', or 'get post reactors'.
license: Proprietary
compatibility:
  - agent-browser CLI
  - Kernel provider (optional, for stealth)
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: experimental
  estimated_runtime: "30s-2min"
  max_cost: "$0.10"
  client_facing: false
  tags:
    - linkedin
    - browser
    - scraping
    - fallback
allowed-tools: Read Write Shell
---

# LinkedIn Browser Scrape Skill

Browser-based LinkedIn scraping for scenarios where APIs fail or return incomplete data.

## When to Use

Use this skill when:
- Crustdata API returns no results but profile/post exists
- Need reactor list (not available via API)
- Need full profile details (About, Experience, Skills)
- Need to scrape company employee lists
- API rate limits have been hit

Do NOT use when:
- Crustdata API is working (API is faster and more reliable)
- Simple post content collection (use API)
- High-volume scraping (use API with pagination)

## Prerequisites

1. **agent-browser installed:**
   ```bash
   npm install -g agent-browser
   agent-browser install
   ```

2. **LinkedIn profile authenticated (optional but recommended):**
   ```bash
   # Create persistent profile
   mkdir -p ~/.mh1/profiles/linkedin
   
   # Login manually once (headed mode)
   agent-browser --profile ~/.mh1/profiles/linkedin --headed open https://linkedin.com/login
   # ... login manually ...
   agent-browser close
   ```

3. **For stealth mode (production):**
   ```bash
   export KERNEL_API_KEY="your-key"
   export KERNEL_STEALTH=true
   ```

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `url` | string | yes | LinkedIn URL (profile or post) |
| `action` | string | yes | "profile", "post", "reactions", "comments" |
| `use_stealth` | boolean | no | Use Kernel stealth provider (default: false) |
| `authenticated` | boolean | no | Use authenticated session (default: true) |

## Outputs

| Name | Type | Description |
|------|------|-------------|
| `data` | object | Scraped data matching action type |
| `success` | boolean | Whether scrape succeeded |
| `error` | string | Error message if failed |

## Process

### Action: profile

1. Navigate to profile URL
2. Wait for page load
3. Take snapshot of interactive elements
4. Extract: name, headline, about, experience, education, skills
5. Return structured profile object

### Action: post

1. Navigate to post URL
2. Wait for content load
3. Extract: author, content, reactions count, comments count, timestamp
4. Return structured post object

### Action: reactions

1. Navigate to post URL
2. Click "reactions" to expand modal
3. Scroll through reactor list
4. Extract: name, headline, profile URL, reaction type
5. Return array of reactors

### Action: comments

1. Navigate to post URL
2. Click "load more comments" until exhausted
3. Extract: author, content, timestamp, replies
4. Return array of comments

## Example Usage

```python
from lib.browser_automation import MH1BrowserClient
from lib.browser_rate_limiter import get_rate_limiter

limiter = get_rate_limiter()
url = "https://linkedin.com/in/janedoe"

# Wait for rate limit slot
limiter.wait_for_slot(url)

# Scrape with browser
with MH1BrowserClient(
    session="linkedin-scrape",
    profile_path="~/.mh1/profiles/linkedin"
) as browser:
    browser.open(url)
    browser.wait(3000)  # Wait for JS
    
    snapshot = browser.snapshot(interactive_only=True)
    # Parse snapshot for profile data...
    
    limiter.record_request(url)
```

## Rate Limits

| Platform | Requests/min | Min delay | Daily limit |
|----------|-------------|-----------|-------------|
| linkedin.com | 10 | 3000ms | 100 |

**Use `lib/browser_rate_limiter.py` to enforce limits.**

## Fallback Pattern

Integrate with existing tools:

```python
# In fetch_linkedin_posts.py
def fetch_profile(url, api_key):
    # Try API first
    result = fetch_via_crustdata(url, api_key)
    
    if result is None and USE_BROWSER_FALLBACK:
        print("API failed, trying browser fallback...")
        result = fetch_via_browser(url)
    
    return result
```

## Quality Criteria

- [ ] Data matches expected schema
- [ ] No CAPTCHA triggered
- [ ] Rate limits respected
- [ ] Session not banned

## Failure Modes

| Mode | Trigger | Action |
|------|---------|--------|
| CAPTCHA | Bot detection | Abort, log, use Kernel stealth |
| Login required | Session expired | Re-authenticate profile |
| Rate limited | Too many requests | Back off, retry after delay |
| Element not found | Page structure changed | Log, return partial data |

## Notes

- Always prefer API over browser scraping
- Use authenticated sessions for better access
- Consider Kernel provider for production (stealth mode)
- Monitor for LinkedIn UI changes that break selectors
