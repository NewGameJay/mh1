---
name: bright-data
description: Progressive four-tier web scraping with automatic fallback. Use when fetching URLs, scraping websites, or when simpler methods fail due to bot detection, CAPTCHAs, or JavaScript rendering.
---

<objective>
Retrieve web content using progressive escalation: start with fast free methods, escalate to paid services only when necessary.
</objective>

<activation_triggers>
This skill activates for:
- Direct scraping: "scrape this URL", "fetch this page", "pull content from..."
- Access issues: "getting blocked", "can't access", "403 error", "CAPTCHA"
- Content extraction: "extract text from", "get the content of"
- WebFetch failures: When built-in WebFetch returns errors or incomplete content
</activation_triggers>

<four_tiers>
| Tier | Method | Speed | Cost | Use When |
|------|--------|-------|------|----------|
| 1 | WebFetch | 2-5s | Free | Simple public sites |
| 2 | cURL + headers | 3-7s | Free | Basic user-agent checks |
| 3 | Playwright | 10-20s | Free | JavaScript-heavy sites |
| 4 | Bright Data MCP | 5-15s | Paid | CAPTCHAs, advanced bot detection |
</four_tiers>

<quick_start>
**For most URLs, just use Tier 1:**
```
WebFetch tool with the URL
```

**If blocked, escalate through tiers sequentially.**

Read `workflows/four-tier-scrape.md` for the full escalation procedure.
</quick_start>

<routing>
| Situation | Action |
|-----------|--------|
| New URL to scrape | Start at Tier 1, escalate on failure |
| Known difficult site | Start at appropriate tier |
| "Use Bright Data" | Jump to Tier 4 directly |
| Setup questions | See README.md |
</routing>

<cost_optimization>
The cascading approach keeps expenses minimal:
- 60-70% of requests resolve at free tiers
- Only escalate when lower tiers fail
- Bright Data costs ~$0.001-0.01 per request

**Never start at Tier 4 unless explicitly requested or site is known to require it.**
</cost_optimization>

<ethical_boundaries>
DO NOT use this skill to:
- Bypass authentication or login walls
- Violate website terms of service
- Scrape personal data without consent
- Overwhelm servers with rapid requests
</ethical_boundaries>

<success_criteria>
- Content retrieved in markdown format
- Lowest effective tier used
- Clear error reporting if all tiers fail
</success_criteria>
