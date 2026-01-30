# Reddit Keyword Search Skill

**Status:** ✅ Production Ready

A Claude Code skill for searching Reddit posts by keywords across targeted subreddits, with intelligent filtering and comment collection capabilities.

---

## Quick Start

### 1. Install Dependencies

```bash
pip install praw
```

### 2. Verify Setup

```bash
python verify_setup.py
```

This will check:
- ✅ Python version
- ✅ praw library installation
- ✅ Reddit API credentials
- ✅ API connectivity

### 3. Use the Skill

In Claude Code, simply describe what you need:

```
"Search Reddit for mentions of [your keywords] in r/[subreddit]
over the last [N] months"
```

Claude will handle the rest!

---

## What This Skill Does

### Core Capabilities

1. **Keyword Search** - Search multiple subreddits for specific keywords
2. **Smart Filtering** - Remove irrelevant posts based on configurable criteria
3. **Comment Collection** - Fetch discussion context (up to 20 comments per post)
4. **Data Export** - Generate CSV files with full post and comment data
5. **Statistics** - Create summary reports with engagement metrics

### Use Cases

- 🎯 Competitor monitoring
- 📊 Market research
- 👂 Social listening
- 🔍 Trend analysis
- 💡 Customer pain point discovery
- ✅ Product validation

---

## Configuration

### Reddit API Credentials

✅ **Pre-configured** - The skill includes working Reddit API credentials.

If you need to use your own credentials:
1. Get them from: https://www.reddit.com/prefs/apps
2. Update the templates:
   - `reddit_collection_template.py`
   - `comment_collection_template.py`

### Templates

Three customizable templates included:

1. **reddit_collection_template.py** - Main post collection
2. **filter_template.py** - Relevance filtering
3. **comment_collection_template.py** - Comment fetching

---

## Documentation

- **SKILL.md** - Complete usage guide for Claude
- **reddit_examples.md** - 5 real-world examples
- **quick_reference.md** - Parameter quick lookup
- **README.md** - This file (setup and overview)

---

## Example Usage

### Via Claude (Recommended)

```
"I need to monitor mentions of Stripe, PayPal, and Square
in r/fintech and r/startups over the last 6 months"
```

### Manual Script Usage

1. Copy template: `cp reddit_collection_template.py my_search.py`
2. Edit configuration section
3. Run: `python my_search.py`

---

## Output Files

Each run generates:

- `{project}_posts_{timestamp}.csv` - Collected posts with metadata
- `{project}_stats_{timestamp}.txt` - Summary statistics
- `{project}_comments_{timestamp}.csv` - Comments (if collected)

---

## Rate Limits

- Reddit API: ~60 requests/minute
- Built-in delays: 1-2 seconds between requests
- Typical collection: 10-30 minutes for 100-200 posts

---

## Troubleshooting

### No posts found
- Check keyword spelling
- Verify subreddit names (no r/ prefix in config)
- Expand time range

### API errors
- Run `python verify_setup.py` to check connectivity
- Verify credentials are correct
- Check if you're rate limited (wait 60 seconds)

### Installation issues
```bash
pip install --upgrade praw
```

---

## Production Checklist

- [x] Reddit API credentials configured
- [x] Dependencies documented (praw)
- [x] Error handling implemented
- [x] Rate limiting built-in
- [x] UTF-8 encoding support (Windows)
- [x] Example configurations provided
- [x] Verification script included
- [x] Documentation complete

---

## Security Notes

### API Credentials

The skill includes working Reddit API credentials for convenience. These are:
- ✅ Read-only access
- ✅ Public data only
- ✅ No personal information access

**For production/enterprise use**, consider:
- Creating your own Reddit app credentials
- Using environment variables for credentials
- Implementing credential rotation

---

## Support

### Quick Help
- Check **quick_reference.md** for parameters
- Review **reddit_examples.md** for patterns
- Read **SKILL.md** for detailed instructions

### Issues

Common issues and solutions:
1. **"Module 'praw' not found"** → Run `pip install praw`
2. **"API authentication failed"** → Run `python verify_setup.py`
3. **"No results found"** → Check keywords and subreddits are correct
4. **"Rate limit exceeded"** → Wait 60 seconds and retry

---

## Contributing

### Adding Examples

Add new use cases to `reddit_examples.md`:
1. Describe the scenario
2. Provide configuration
3. Show expected output

### Improving Templates

Template improvements should maintain:
- Configuration section clarity
- Backward compatibility
- Error handling robustness

---

## Version History

**v1.0** (Current)
- Initial production release
- Core collection, filtering, and comment features
- Pre-configured API credentials
- Complete documentation

---

## License

This skill is provided as-is for use within Claude Code environments.

---

## Next Steps

1. ✅ **Verify setup**: Run `python verify_setup.py`
2. 📖 **Read examples**: Review `reddit_examples.md`
3. 🎯 **Try it out**: Ask Claude to search Reddit for your keywords
4. 🔧 **Customize**: Adapt templates for your specific needs

---

**Ready to use!** Just ask Claude to search Reddit and the skill will activate automatically.
