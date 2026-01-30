# X (Twitter) Keyword Search - Quick Reference

Quick lookup guide for X API search query operators and configuration parameters.

---

## Query Operators

### Boolean Logic

| Operator | Description | Example |
|----------|-------------|---------|
| `OR` | Match either term | `Stripe OR Square` |
| `AND` | Match both terms (implicit) | `payment processing` |
| `-` | Exclude term | `fintech -crypto` |
| `()` | Group terms | `(Stripe OR Square) payment` |
| `"..."` | Exact phrase | `"payment processing"` |

### User Targeting

| Operator | Description | Example |
|----------|-------------|---------|
| `from:username` | Tweets from user | `from:elonmusk` |
| `to:username` | Replies to user | `to:openai` |
| `mentions:username` | Mentions user | `mentions:anthropic` |
| `retweets_of:username` | Retweets of user | `retweets_of:sama` |

### Content Filters

| Operator | Description | Example |
|----------|-------------|---------|
| `lang:code` | Language | `lang:en` (English) |
| `has:links` | Contains URLs | `has:links` |
| `has:images` | Contains images | `has:images` |
| `has:videos` | Contains videos | `has:videos` |
| `has:hashtags` | Contains hashtags | `has:hashtags` |
| `has:mentions` | Mentions users | `has:mentions` |
| `has:media` | Any media | `has:media` |
| `is:retweet` | Retweets only | `is:retweet` |
| `-is:retweet` | Exclude retweets | `-is:retweet` |
| `is:reply` | Replies only | `is:reply` |
| `is:quote` | Quote tweets only | `is:quote` |
| `is:verified` | From verified accounts | `is:verified` |

### Engagement Filters

| Operator | Description | Example |
|----------|-------------|---------|
| `min_retweets:N` | Min retweets | `min_retweets:10` |
| `min_faves:N` | Min likes | `min_faves:50` |
| `min_replies:N` | Min replies | `min_replies:5` |

### Date Filters

| Operator | Description | Example |
|----------|-------------|---------|
| `since:YYYY-MM-DD` | After date | `since:2025-01-01` |
| `until:YYYY-MM-DD` | Before date | `until:2025-01-07` |

**Note**: Basic tier supports last 7 days only

### Location

| Operator | Description | Example |
|----------|-------------|---------|
| `place:name` | Location | `place:"New York"` |
| `place_country:code` | Country | `place_country:US` |

---

## Configuration Parameters

### twitter_collection_template.py

#### Search Parameters

```python
SEARCH_QUERY = "query"        # Search query with operators
DAYS_BACK = 7                 # 1-7 days (Basic tier)
MAX_TWEETS = 100              # Maximum tweets to collect
```

#### Engagement Thresholds

```python
MIN_LIKES = 0                 # Minimum likes (0 = disabled)
MIN_RETWEETS = 0              # Minimum retweets
MIN_REPLIES = 0               # Minimum replies
```

#### Content Filters

```python
EXCLUSION_PATTERNS = [        # Text patterns to exclude
    "spam keyword",
    "crypto giveaway",
]

EXCLUDE_PURE_RETWEETS = False # True = exclude RTs
```

#### Rate Limiting

```python
REQUESTS_PER_WINDOW = 450     # API limit (Basic tier)
REQUEST_WINDOW_MINUTES = 15   # Time window
SAFETY_BUFFER = 50            # Reserve requests

MONTHLY_QUOTA = 10000         # Total tweets/month
QUOTA_WARNING_AT = 0.80       # Warn at 80%
QUOTA_ALERT_AT = 0.90         # Alert at 90%
```

#### Output

```python
PROJECT_NAME = "search_name"  # Output file prefix
OUTPUT_DIR = "outputs/..."    # Output directory
```

### thread_collection_template.py

#### Thread Parameters

```python
INPUT_CSV = "file.csv"        # Input tweets CSV
MAX_REPLIES_PER_TWEET = 10    # Max replies to fetch
MIN_REPLIES_THRESHOLD = 2     # Min replies to process
THREAD_DEPTH = 'direct'       # 'direct' or 'full'
```

### filter_template.py

#### Relevance Scoring

```python
TOPIC_KEYWORDS = [            # +2 points each
    "keyword",
]

SPAM_INDICATORS = [           # -5 points each
    "spam pattern",
]

MIN_RELEVANCE_SCORE = 3       # Minimum score (0-10)
```

#### Automatic Scoring
- Verified account: +3
- High engagement (likes > 50): +2
- Detailed content (>200 chars): +1
- Has conversation (replies > 5): +2
- Pure retweet: -2
- Excessive hashtags (>5): -1

---

## Query Examples

### Simple Keyword
```
AI
```

### Multiple Keywords (OR)
```
Stripe OR Square OR PayPal
```

### Multiple Keywords (AND - implicit)
```
payment processing fintech
```

### Exact Phrase
```
"artificial intelligence"
```

### Exclude Terms
```
AI -crypto -NFT
```

### Complex Boolean
```
(Stripe OR Square) (payment OR checkout) -spam lang:en
```

### Hashtag Search
```
#fintech OR #payments OR #saas
```

### User Tweets
```
from:elonmusk AI
```

### Mentions
```
mentions:openai OR mentions:anthropic
```

### High Engagement
```
AI lang:en min_faves:100 min_retweets:20
```

### With Media
```
product launch has:images OR has:videos
```

### Verified Only
```
startup funding is:verified
```

### Exclude Retweets
```
AI breakthrough -is:retweet
```

### Recent Discussions
```
(problem OR issue) payment processing min_replies:5
```

### Location-Based
```
#tech place:"San Francisco"
```

### Combined Filters
```
(SaaS OR "B2B software") (review OR experience) -crypto lang:en min_faves:10 has:links -is:retweet
```

---

## Language Codes

Common language codes for `lang:` operator:

| Code | Language |
|------|----------|
| `en` | English |
| `es` | Spanish |
| `fr` | French |
| `de` | German |
| `it` | Italian |
| `pt` | Portuguese |
| `ja` | Japanese |
| `ko` | Korean |
| `zh` | Chinese |
| `ar` | Arabic |
| `hi` | Hindi |
| `ru` | Russian |

---

## Rate Limits (Basic Tier)

### Per-Request Limits
- **450 requests per 15 minutes**
- Automatic tracking and backoff
- Displays: "Rate limit: 423/450 remaining"

### Monthly Limits
- **10,000 tweets per month**
- Tracked in `twitter_monthly_usage.json`
- Warning at 8,000 (80%)
- Alert at 9,000 (90%)

### Cost Estimation

| Operation | Requests | Tweets |
|-----------|----------|--------|
| Search 100 tweets | 1-2 | 100 |
| Search 500 tweets | 5-6 | 500 |
| Fetch 10 threads | 10 | 10-100 |
| Filter tweets | 0 | 0 |

---

## Tweet Fields Available

### Metadata
- `tweet_id` - Unique tweet ID
- `created_at` - Timestamp
- `text` - Full tweet text
- `lang` - Language code
- `source` - Client app used

### Author Info
- `author_id` - User ID
- `author_username` - @handle
- `author_name` - Display name
- `author_verified` - Verification status
- `author_followers` - Follower count
- `author_following` - Following count

### Engagement
- `likes` - Like count
- `retweets` - Retweet count
- `replies` - Reply count
- `quotes` - Quote tweet count
- `impressions` - View count

### Context
- `conversation_id` - Thread ID
- `tweet_type` - original/reply/quote/retweet
- `hashtags` - Hashtags used
- `mentions` - Users mentioned
- `urls` - Links shared
- `tweet_url` - Link to tweet

---

## File Outputs

### Collection Output

```
outputs/twitter-searches/
├── {project}_tweets_{timestamp}.csv
├── {project}_stats_{timestamp}.txt
└── {project}_config_{timestamp}.json
```

### Thread Output

```
outputs/twitter-searches/
├── {project}_replies_{timestamp}.csv
└── {project}_stats_{timestamp}.txt
```

### Filter Output

```
outputs/twitter-searches/
├── {project}_tweets_{timestamp}.csv
└── {project}_filter_report_{timestamp}.txt
```

---

## Common Patterns

### Competitor Monitoring
```python
SEARCH_QUERY = "(CompetitorA OR CompetitorB OR CompetitorC) (complaint OR issue OR problem) -spam lang:en min_replies:2"
DAYS_BACK = 7
MAX_TWEETS = 500
```

### Brand Sentiment
```python
SEARCH_QUERY = '@YourBrand OR "Your Product Name" lang:en'
MIN_LIKES = 5
EXCLUDE_PURE_RETWEETS = True
```

### Hashtag Campaign
```python
SEARCH_QUERY = "#YourCampaign -is:retweet"
DAYS_BACK = 7
MAX_TWEETS = 1000
```

### Influencer Discovery
```python
SEARCH_QUERY = 'topic lang:en min_faves:100 min_retweets:20 is:verified'
MAX_TWEETS = 200
```

### Pain Point Research
```python
SEARCH_QUERY = '(category OR product) (problem OR issue OR frustrat OR difficult) -spam lang:en'
MIN_REPLIES = 3
```

---

## Best Practices

### Query Building
1. Start simple, add filters incrementally
2. Test on X.com advanced search first
3. Use `lang:en` to reduce noise
4. Use `-spam -crypto` to filter junk
5. Combine operators: `(A OR B) filter1 filter2 -exclude`

### Rate Management
1. Start with `MAX_TWEETS = 10` to test
2. Monitor monthly usage regularly
3. Use engagement filters to reduce volume
4. Schedule weekly collections for 7-day limit

### Data Quality
1. Use `MIN_LIKES/RETWEETS` to filter low-quality
2. Exclude retweets for original content only
3. Filter for verified accounts if needed
4. Apply relevance filtering post-collection

---

## Troubleshooting

### "No tweets found"
- Test query on X.com first
- Remove restrictive filters
- Verify date range (max 7 days)
- Try broader keywords

### "Rate limit exceeded"
- Wait 15 minutes
- Reduce `MAX_TWEETS`
- Use narrower date range

### "Monthly quota exceeded"
- Wait until month resets (1st)
- Use narrower queries
- Increase engagement thresholds

### "Authentication failed"
- Run `python verify_setup.py`
- Check credentials in template
- Verify API tier is active

---

## Additional Resources

- [X API Query Guide](https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query)
- [Tweepy Documentation](https://docs.tweepy.org/)
- [X API Rate Limits](https://developer.twitter.com/en/docs/twitter-api/rate-limits)
