# LinkedIn Keyword Search Skill

A comprehensive Claude Code skill for collecting and analyzing LinkedIn posts using the Crustdata API.

## Overview

This skill enables sophisticated LinkedIn post collection with:
- **Boolean keyword search** (OR, AND operators)
- **7 filter types** (author, company, industry, mentions, job titles)
- **Exact phrase matching**
- **Engagement data collection** (reactors, comments)
- **Credit usage tracking**
- **CSV export with statistics**

## Quick Start

1. **Activate the skill:**
   ```
   User: "I need to search LinkedIn for posts about AI"
   ```

2. **Claude will ask for:**
   - Keywords (with Boolean operators if needed)
   - Date range (past-24h, past-week, past-month, past-quarter, past-year)
   - Number of posts (limit, max 500)
   - Optional filters

3. **Script generated and executed:**
   - `linkedin_keyword_search.py` created
   - Validation of filters
   - API call with retry logic
   - CSV and stats exported

## Files in This Skill

- **SKILL.md** - Main skill documentation with step-by-step instructions
- **linkedin_collection_template.py** - Customizable Python collection script
- **quick_reference.md** - Quick guide to API parameters and filters
- **linkedin_examples.md** - Real-world use cases and examples
- **verify_setup.py** - Test script to verify API credentials
- **README.md** - This file

## Prerequisites

- Python 3.7+
- `requests` library: `pip install requests`
- Crustdata API key (pre-configured in template)

## Features

### Advanced Filtering

7 filter types available:

| Filter | Description | Incompatible With |
|--------|-------------|-------------------|
| MEMBER | Posts by specific people | COMPANY |
| COMPANY | Posts from company pages | MEMBER, AUTHOR_* |
| AUTHOR_COMPANY | Posts by employees | COMPANY |
| AUTHOR_INDUSTRY | Posts by industry | COMPANY |
| AUTHOR_TITLE | Posts by job title | COMPANY |
| MENTIONING_MEMBER | Posts mentioning people | None |
| MENTIONING_COMPANY | Posts mentioning companies | None |

### Credit Cost Model

- **Base:** 1 credit per post
- **With reactors:** 5 credits per post
- **With comments:** 5 credits per post
- **With both:** 10 credits per post
- **Exact match:** 3 credits per post
- **No results:** 0 credits

### Boolean Keywords

Supports complex searches:
```
"AI OR machine learning OR artificial intelligence"
"Series A AND fundraise AND startup"
```

### Engagement Data

Optional collection of:
- **Reactors:** People who liked/reacted (with profiles)
- **Comments:** All comments with author details
- **Cost warning:** Automatically calculated and displayed

## Example Use Cases

1. **Competitor Monitoring:** Track mentions of competitors
2. **Thought Leadership:** Collect posts from industry leaders
3. **Product Launches:** Monitor new product announcements
4. **Fundraising:** Track funding announcements
5. **Trend Analysis:** Analyze industry discussions
6. **Influencer Research:** Find key opinion leaders
7. **Content Research:** Discover high-performing content

See `linkedin_examples.md` for detailed configurations.

## Safety Features

- ✅ **Filter validation:** Prevents incompatible filter combinations
- ✅ **Credit warnings:** Shows estimated costs before running
- ✅ **Engagement data confirmation:** Requires explicit confirmation for high-cost operations
- ✅ **Retry logic:** Handles rate limits with exponential backoff
- ✅ **Configuration export:** Saves search parameters for reproducibility

## Output Files

Each search generates files in `outputs/linkedin-searches/`:
```
outputs/linkedin-searches/
├── {project}_search.py                  # Customized search script
├── {project}_posts_{timestamp}.csv      # All posts with metadata
├── {project}_stats_{timestamp}.txt      # Summary statistics
└── {project}_config_{timestamp}.json    # Search configuration
```

## Filter Constraints

⚠️ **Important:** Some filters cannot be combined:

- ❌ AUTHOR_COMPANY + COMPANY
- ❌ MEMBER + COMPANY
- ❌ AUTHOR_INDUSTRY + COMPANY
- ❌ AUTHOR_TITLE + COMPANY

**Why?** A LinkedIn post is either from a company page OR from an individual, never both.

## Credit Optimization Tips

1. **Start without engagement data** - Test with 1 credit/post first
2. **Use small limits for testing** - Try 10-20 posts initially
3. **Avoid exact match for exploration** - Save 3x credit cost
4. **Combine filters strategically** - Narrow results to reduce count
5. **Run during off-peak hours** - Better rate limit availability

## Troubleshooting

**No results?**
- Verify keyword spelling
- Try broader date range
- Remove filters temporarily
- Test keywords on LinkedIn search

**400 Bad Request?**
- Check for incompatible filter combinations
- Validate LinkedIn URL formats
- Ensure AUTHOR_TITLE has single value only

**High credit usage?**
- Disable reactors/comments
- Reduce limit value
- Use standard search (not exact match)

## API Documentation

- **Full docs:** https://fulldocs.crustdata.com/
- **Filter guide:** See reference materials in `/external_project_references/`
- **Industry values:** https://crustdata-docs-region-json.s3.us-east-2.amazonaws.com/industry_values.json

## Related Skills

- **reddit-keyword-search** - Similar skill for Reddit
- **social-listening** - Multi-platform social monitoring
- **competitive-intelligence** - Advanced competitive analysis

## Testing

Run the verification script to test your setup:
```bash
python verify_setup.py
```

This will:
- Test API connectivity
- Verify credentials
- Run a simple test query
- Report credit usage

## Support

For issues or questions:
1. Check `quick_reference.md` for syntax help
2. Review `linkedin_examples.md` for use case patterns
3. Consult API documentation at https://fulldocs.crustdata.com/
4. Review filter constraints in reference materials

## Version History

- **v1.0** (2025-11-13)
  - Initial release
  - Support for all 7 filter types
  - Boolean keyword search
  - Engagement data collection
  - Credit tracking and warnings
  - Comprehensive examples and documentation
