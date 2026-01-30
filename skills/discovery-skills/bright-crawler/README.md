# Bright Data Four-Tier Web Scraping

Progressive web scraping skill that escalates through four tiers to retrieve content while minimizing costs.

## Tiers Overview

| Tier | Method | Cost | Speed | Success Rate |
|------|--------|------|-------|--------------|
| 1 | WebFetch | Free | 2-5s | ~60% |
| 2 | cURL + headers | Free | 3-7s | ~75% |
| 3 | Playwright | Free | 10-20s | ~85% |
| 4 | Bright Data | Paid | 5-15s | ~99% |

## Setup

### Tiers 1-2: No Setup Required

WebFetch and cURL are available by default.

### Tier 3: Playwright

If not already installed:

```bash
# Install Playwright
npm install playwright

# Download browsers
npx playwright install chromium
```

Or use the Playwright MCP server if configured.

### Tier 4: Bright Data MCP

1. **Create Bright Data account** at [brightdata.com](https://brightdata.com)

2. **Get API token** from your dashboard

3. **Add to MCP config** (`.mcp.json`):

```json
{
  "mcpServers": {
    "brightdata": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-brightdata"],
      "env": {
        "BRIGHTDATA_API_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

4. **Restart Claude Code** to load the MCP server

## Usage

Invoke the skill when you need to scrape a URL:

```
"Scrape https://example.com for me"
"I can't access this page: [URL]"
"Fetch the content from [URL]"
```

The skill automatically:
1. Starts at Tier 1
2. Escalates on failure
3. Returns content in markdown format

## Cost Tracking

Bright Data charges per request. Typical costs:
- Web Unlocker: ~$0.001-0.005 per request
- SERP API: ~$0.002-0.01 per request

With the four-tier approach, most requests resolve at free tiers. Real-world usage shows ~$0.30 over 3 weeks of heavy use.

## Troubleshooting

**Tier 1 always fails:**
- Site may have basic bot detection
- Try Tier 2 as starting point for that domain

**Tier 3 times out:**
- Increase wait time for JavaScript rendering
- Check if site requires login

**Tier 4 returns errors:**
- Verify API token is valid
- Check Bright Data dashboard for quota
- Some sites may be completely blocked

## Known Difficult Sites

Sites that typically require Tier 3+:
- LinkedIn (any page)
- Twitter/X
- Instagram
- Most SPAs (React, Vue, Angular apps)

Sites that typically require Tier 4:
- Sites with Cloudflare protection
- Sites with aggressive CAPTCHA
- Rate-limited APIs
