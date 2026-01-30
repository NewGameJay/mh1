# Four-Tier Scrape Workflow

<objective>
Retrieve web content by escalating through four tiers until successful.
Now with full browser control via browser-use and agent-browser.
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

## Tier 2: Headless Browser (browser-use chromium)

```bash
# Fast headless browser for JS-rendered content
browser-use open "[URL]"
browser-use state                              # Get page elements
browser-use eval "document.body.innerText"     # Extract text
browser-use screenshot page.png                # Visual capture if needed
```

**Success indicators:**
- Full page content rendered
- Dynamic elements loaded
- No CAPTCHA or login wall

**Escalate to Tier 3 if:**
- Site requires authentication
- Login wall detected
- Content behind paywall
- Cookies/session required

---

## Tier 3: Real Browser (browser-use real)

**The killer feature:** Uses your actual Chrome with existing logins.

```bash
# Ensure you're logged into the target site in Chrome first
browser-use --browser real open "[URL]"
browser-use state
browser-use eval "document.body.innerText"
```

**For complex interactions:**
```bash
agent-browser open "[URL]"
agent-browser snapshot -i                    # Get interactive elements with @refs
agent-browser click @e1                     # Click element
agent-browser fill @e2 "search term"        # Fill input
agent-browser wait --network-idle
```

**Works for:**
- Google Docs/Sheets (if logged in)
- Paid Substack (if subscribed)
- LinkedIn (if logged in)
- Notion, Figma, any authenticated site

**Escalate to Tier 4 if:**
- Advanced bot detection (Cloudflare, Akamai)
- CAPTCHA even with real browser
- Geographic restrictions
- Site explicitly blocks automation

---

## Tier 4: Remote/Bright Data (Paid)

**For hardcore anti-bot sites only**

```bash
# browser-use remote mode
browser-use --browser remote --api-key $BRIGHT_DATA_API_KEY open "[URL]"
browser-use state
browser-use eval "document.body.innerText"
```

**Or Bright Data MCP:**
```
Use mcp__brightdata__scrape_as_markdown:
- url: [target URL]
```

**Bright Data handles:**
- CAPTCHA solving
- Residential proxy rotation
- Browser fingerprint management
- Geographic targeting

**Cost:** ~$0.01 per request - use sparingly

</process>

<decision_tree>

```
Start with URL
    │
    ▼
[Tier 1: WebFetch]
    │
    ├── Success? → Done
    │
    ├── JS required / SPA? → Tier 2
    │
    ├── Auth required? → Tier 3
    │
    └── Bot blocked? → Tier 4

[Tier 2: Headless Chromium]
    │
    ├── Success? → Done
    │
    ├── Login wall? → Tier 3
    │
    └── CAPTCHA? → Tier 4

[Tier 3: Real Browser]
    │
    ├── Success? → Done
    │
    └── Still blocked? → Tier 4

[Tier 4: Remote/Bright Data]
    │
    ├── Success? → Done
    │
    └── All failed → Report & suggest alternatives
```

</decision_tree>

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
   - Ask user to manually log in first for Tier 3

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

<quick_commands>

```bash
# Tier 1 - via WebFetch tool

# Tier 2 - Headless
browser-use open "URL" && browser-use eval "document.body.innerText"

# Tier 3 - Real browser (authenticated)
browser-use --browser real open "URL" && browser-use eval "document.body.innerText"

# Tier 3 - Complex interaction
agent-browser open "URL"
agent-browser snapshot -i
agent-browser click @e1

# Tier 4 - Remote
browser-use --browser remote --api-key $KEY open "URL"
```

</quick_commands>

<success_criteria>
- Content successfully retrieved
- Lowest possible tier used
- Output in clean markdown format
- Errors clearly reported if failed
</success_criteria>
