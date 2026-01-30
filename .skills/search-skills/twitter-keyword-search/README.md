# X (Twitter) Keyword Search Skill

**Status:** ✅ Production Ready

A Claude Code skill for searching X (formerly Twitter) posts by keywords, hashtags, and user filters with engagement data collection and conversation thread analysis.

---

## Quick Start

### 1. Install Dependencies

```bash
pip install tweepy
```

### 2. Verify Setup

```bash
python verify_setup.py
```

This will check:
- ✅ Python version (3.7+)
- ✅ tweepy library installation
- ✅ X API credentials
- ✅ API connectivity
- ✅ Search functionality

### 3. Use the Skill

In Claude Code, simply describe what you need:

```
"Search X for mentions of [keywords] over the last [N] days"
```

Claude will handle the rest!

---

## What This Skill Does

### Core Capabilities

1. **Keyword & Hashtag Search** - Search X for specific keywords and hashtags with Boolean operators
2. **User Filtering** - Filter by accounts (from:, to:, mentions:)
3. **Advanced Filtering** - Language, engagement thresholds, content types
4. **Thread Collection** - Fetch conversation replies for context
5. **Smart Filtering** - Remove spam, bots, and irrelevant content
6. **Engagement Data** - Complete metrics (likes, retweets, replies, quotes, impressions)
7. **Rate Limit Management** - Automatic tracking and quota management
8. **Data Export** - CSV files with full tweet and engagement data
9. **Statistics** - Summary reports with insights and top content

### Use Cases

- 🎯 Competitor monitoring and brand mentions
- 📊 Market research and trend analysis
- 👂 Social listening and sentiment tracking
- 💡 Customer feedback and pain point discovery
- 🔍 Hashtag campaign tracking
- ✅ Product validation and feature requests
- 📈 Influencer identification
- ⚡ Real-time event monitoring

---

## Configuration

### X API Credentials

✅ **Pre-configured** - The skill includes working X API credentials (Basic tier).

If you need to use your own credentials:
1. Get them from: https://developer.twitter.com/en/portal/dashboard
2. Update the templates:
   - `twitter_collection_template.py`
   - `thread_collection_template.py`
   - `verify_setup.py`

### API Tier: Basic ($100/mo)

- **10,000 tweets per month**
- **450 requests per 15 minutes**
- **Recent search (last 7 days)**
- **Full tweet metadata and metrics**

### Templates

Four customizable templates included:

1. **twitter_collection_template.py** - Main tweet search
2. **thread_collection_template.py** - Conversation thread fetching
3. **filter_template.py** - Relevance filtering
4. **verify_setup.py** - API connectivity tester

---

## Documentation

- **SKILL.md** - Complete usage guide for Claude
- **twitter_examples.md** - 5 real-world examples
- **quick_reference.md** - Query syntax and parameter lookup
- **README.md** - This file (setup and overview)

---

## Example Usage

### Via Claude (Recommended)

```
"I need to monitor mentions of Stripe, Square, and PayPal
on X over the last 7 days, focusing on customer complaints"
```

### Manual Script Usage

1. Edit configuration section in `twitter_collection_template.py`
2. Set search query: `SEARCH_QUERY = "(Stripe OR Square OR PayPal) (complaint OR issue) -crypto lang:en"`
3. Run: `python twitter_collection_template.py`

---

## Query Syntax

### Boolean Operators
- `OR` - Either keyword: `Stripe OR Square`
- `AND` - Both keywords (implicit): `payment processing`
- `-` - Exclude: `-crypto`
- `()` - Grouping: `(Stripe OR Square) payment`

### User Operators
- `from:username` - Tweets from user
- `to:username` - Replies to user
- `mentions:username` - Mentions user

### Content Filters
- `lang:en` - English language
- `has:links` - Contains URLs
- `has:images` - Contains images
- `has:videos` - Contains videos
- `has:hashtags` - Contains hashtags
- `is:verified` - From verified accounts

### Engagement Filters
- `min_faves:10` - At least 10 likes
- `min_retweets:5` - At least 5 retweets
- `min_replies:2` - At least 2 replies

---

## Output Files

Each run generates:

- `{project}_tweets_{timestamp}.csv` - Tweets with full metadata
- `{project}_stats_{timestamp}.txt` - Summary statistics
- `{project}_config_{timestamp}.json` - Search configuration
- `{project}_replies_{timestamp}.csv` - Conversation threads (if collected)
- `{project}_filter_report_{timestamp}.txt` - Filtering analysis (if filtered)

---

## Rate Limits & Quota

### Per-Request Limits (Basic Tier)
- 450 requests per 15-minute window
- Automatic backoff and retry
- Real-time tracking displayed

### Monthly Limits (Basic Tier)
- 10,000 tweets per month
- Automatic usage tracking
- Warnings at 80% and 90%

### Best Practices
- Start with narrow queries to estimate results
- Use engagement filters (`min_faves:10`) to reduce volume
- Test searches with `MAX_TWEETS = 10` first
- Monitor monthly quota regularly

---

## Troubleshooting

### No tweets found
- Test query on X.com advanced search first
- Verify date range is within 7 days (Basic tier)
- Try broader keywords
- Remove restrictive filters

### API errors
- Run `python verify_setup.py` to diagnose
- Verify credentials are correct and active
- Check API tier hasn't expired
- Ensure `tweepy` is installed: `pip install tweepy`

### Rate limit exceeded
- Wait 15 minutes for request window reset
- Reduce query scope or use narrower date range
- Check monthly quota: `cat twitter_monthly_usage.json`

### Installation issues
```bash
pip install --upgrade tweepy
```

---

## Feature Comparison

| Feature | Reddit Skill | LinkedIn Skill | X Skill |
|---------|-------------|----------------|---------|
| **Time Range** | 12+ months | Varies | **7 days** |
| **Rate Limits** | 60/min | Credit-based | **450/15min** |
| **Thread Collection** | ✅ Comments | ❌ | **✅ Conversations** |
| **Real-time** | ❌ | ❌ | **✅ Near real-time** |
| **User Filtering** | ❌ | ✅ | **✅ Advanced** |
| **Hashtag Tracking** | ❌ | ❌ | **✅ Native** |
| **Monthly Quota** | Unlimited | Credits | **10K tweets** |

---

## Production Checklist

- [x] X API credentials configured (Basic tier)
- [x] Dependencies documented (tweepy)
- [x] Error handling implemented
- [x] Rate limiting with automatic backoff
- [x] Monthly quota tracking
- [x] UTF-8 encoding support (Windows)
- [x] Example configurations provided
- [x] Verification script included
- [x] Documentation complete
- [x] Thread collection supported
- [x] Relevance filtering included

---

## Security Notes

### API Credentials

The skill includes working X API credentials (Basic tier) for convenience. These provide:
- ✅ Read-only access
- ✅ Public data only
- ✅ No account access or posting

**For production/enterprise use**, consider:
- Creating your own X Developer App
- Using environment variables for credentials
- Implementing credential rotation
- Upgrading to Pro tier for full archive access

---

## Common Use Cases

### 1. Competitor Monitoring
```python
SEARCH_QUERY = "(CompetitorA OR CompetitorB) (complaint OR issue OR problem) -spam lang:en min_replies:2"
DAYS_BACK = 7
MAX_TWEETS = 500
```

### 2. Hashtag Campaign Tracking
```python
SEARCH_QUERY = "#YourHashtag OR #BrandHashtag -is:retweet"
DAYS_BACK = 7
MAX_TWEETS = 1000
```

### 3. Brand Sentiment Analysis
```python
SEARCH_QUERY = '@YourBrand OR "Your Product" lang:en'
MIN_LIKES = 5  # Focus on engaged content
COLLECT_THREADS = True  # Get conversation context
```

### 4. Influencer Identification
```python
SEARCH_QUERY = 'keyword lang:en min_faves:100'
MIN_RETWEETS = 20
# Filter for verified accounts with large following
```

### 5. Crisis Monitoring
```python
SEARCH_QUERY = '@YourBrand (issue OR problem OR outage OR down)'
DAYS_BACK = 1  # Real-time monitoring
MAX_TWEETS = 500
```

---

## Support

### Quick Help
- Check **quick_reference.md** for query syntax
- Review **twitter_examples.md** for patterns
- Read **SKILL.md** for detailed instructions

### Common Issues

1. **"Module 'tweepy' not found"** → Run `pip install tweepy`
2. **"Authentication failed"** → Run `python verify_setup.py`
3. **"No results found"** → Test query on X.com first
4. **"Rate limit exceeded"** → Wait 15 minutes and retry
5. **"Monthly quota exceeded"** → Quota resets on 1st of month

---

## Version History

**v1.0** (Current)
- Initial production release
- Keyword/hashtag search with advanced operators
- Thread collection and conversation analysis
- Relevance filtering with smart spam detection
- Rate limit and monthly quota management
- Pre-configured API credentials (Basic tier)
- Complete documentation and examples

---

## Next Steps

1. ✅ **Verify setup**: Run `python verify_setup.py`
2. 📖 **Read examples**: Review `twitter_examples.md`
3. 🔍 **Test query**: Try on X.com advanced search first
4. 🎯 **Run search**: Ask Claude to search X for your keywords
5. 🔧 **Customize**: Adapt templates for your specific needs

---

**Ready to use!** Just ask Claude to search X and the skill will activate automatically.

## Additional Resources

- [X API v2 Documentation](https://developer.twitter.com/en/docs/twitter-api)
- [Tweepy Documentation](https://docs.tweepy.org/)
- [X Advanced Search Guide](https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query)
- [Query Syntax Reference](https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query)
