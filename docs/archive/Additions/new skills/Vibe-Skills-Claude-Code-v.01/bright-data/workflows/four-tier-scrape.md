# Four-Tier Scrape Workflow

<objective>
Retrieve web content by escalating through four tiers until successful.
</objective>

<process>

## Tier 1: WebFetch (Try First)

```
Use WebFetch tool:
- url: [target URL]
- prompt: "Extract the main content from this page"
```

**Success indicators:**
- Returns meaningful content (not error page)
- Content length > 500 characters
- No "blocked", "forbidden", "captcha" in response

**Escalate to Tier 2 if:**
- 403/401/429 status codes
- Empty or minimal content returned
- Error message about access denied
- Response contains CAPTCHA indicators

---

## Tier 2: cURL with Browser Headers

```bash
curl -s -L \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" \
  -H "Accept-Language: en-US,en;q=0.5" \
  -H "Accept-Encoding: gzip, deflate, br" \
  -H "Connection: keep-alive" \
  -H "Upgrade-Insecure-Requests: 1" \
  "[URL]" | gunzip 2>/dev/null || curl -s -L \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  "[URL]"
```

**Success indicators:**
- HTML content returned
- Page title and body present
- No JavaScript-only placeholder content

**Escalate to Tier 3 if:**
- Page requires JavaScript rendering
- Content shows "Please enable JavaScript"
- SPA/React/Vue app detected
- Dynamic content not loading

---

## Tier 3: Playwright Browser Automation

```javascript
// Using Playwright MCP or direct automation
const playwright = require('playwright');

async function scrapeWithPlaywright(url) {
  const browser = await playwright.chromium.launch({ headless: true });
  const page = await browser.newPage();

  await page.goto(url, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000); // Allow dynamic content

  const content = await page.content();
  const text = await page.evaluate(() => document.body.innerText);

  await browser.close();
  return { html: content, text: text };
}
```

**Or use Playwright MCP tools:**
```
1. mcp__playwright__browser_navigate to URL
2. mcp__playwright__browser_snapshot for accessibility tree
3. mcp__playwright__browser_take_screenshot if needed
```

**Success indicators:**
- Full page content rendered
- Dynamic elements loaded
- No CAPTCHA challenge presented

**Escalate to Tier 4 if:**
- CAPTCHA or bot detection challenge
- Cloudflare/Akamai protection
- Rate limiting despite delays
- Geographic restrictions

---

## Tier 4: Bright Data MCP

**Requires setup** (see README.md)

```
Use mcp__brightdata__scrape_as_markdown:
- url: [target URL]
```

**Or for structured data:**
```
Use mcp__brightdata__scrape_as_json:
- url: [target URL]
- schema: { fields you need }
```

**Bright Data handles:**
- CAPTCHA solving
- Residential proxy rotation
- Browser fingerprint management
- Geographic targeting

**Success indicators:**
- Clean markdown/JSON returned
- Content matches expected page
- No error responses

</process>

<failure_handling>

If all tiers fail:

1. **Report the failure clearly:**
   - Which tiers were attempted
   - Error messages from each
   - Suspected cause (geo-block, auth required, etc.)

2. **Suggest alternatives:**
   - Different URL (mobile version, API endpoint)
   - Manual access with user's browser
   - Alternative data source

3. **Do not retry indefinitely** - 4 tiers is the limit

</failure_handling>

<output_format>

Always return scraped content as:

```markdown
# [Page Title]

**Source:** [URL]
**Scraped via:** Tier [N] - [Method]
**Date:** [timestamp]

---

[Main content in markdown format]
```

</output_format>

<success_criteria>
- Content successfully retrieved
- Lowest possible tier used
- Output in clean markdown format
- Errors clearly reported if failed
</success_criteria>
