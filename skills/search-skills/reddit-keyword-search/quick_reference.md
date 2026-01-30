# Reddit Keyword Search - Quick Reference

Quick reference for common configurations and parameters.

---

## Required Setup

### 1. Install Dependencies
```bash
pip install praw
```

### 2. Reddit API Credentials
Get from: https://www.reddit.com/prefs/apps

```python
REDDIT_CLIENT_ID = "your_client_id"
REDDIT_CLIENT_SECRET = "your_client_secret"
REDDIT_USER_AGENT = "YourApp/1.0"
```

---

## Collection Script Parameters

### Keywords
```python
KEYWORDS = ["keyword1", "keyword2", "keyword3"]
```

**Tips:**
- Use exact phrases for brands/products
- Include common misspellings
- Add comparison terms ("X vs Y")
- Max recommended: 10-15 keywords per run

### Subreddits
```python
SUBREDDITS = [
    ("SubredditName", expected_count),  # No r/ prefix
]
```

**Common Subreddits by Category:**
- **SaaS/Tech:** SaaS, startups, Entrepreneur, technology
- **Research:** UXResearch, Marketresearch, research
- **Product:** ProductManagement, product_design
- **Business:** smallbusiness, freelance, consulting
- **Customer:** CustomerSuccess, customerexperience

### Time Range
```python
MONTHS_BACK = 12  # 1-12 months typical
```

**Guidelines:**
- 1 month: Brand monitoring, recent trends
- 3 months: Quarterly analysis
- 6 months: Semi-annual review
- 12 months: Annual comprehensive view

### Exclusion Patterns
```python
EXCLUSION_PATTERNS = [
    "/jfe/form",              # Qualtrics surveys
    "typeform.com/to/",       # Typeform surveys
    "surveymonkey.com/r/",    # SurveyMonkey
    "forms.gle/",             # Google Forms
    "we're hiring",           # Job posts
    "job opening",            # Job posts
    "apply now",              # Job posts
    "discount code",          # Promotions
    "affiliate",              # Promotions
]
```

---

## Filtering Script Parameters

### Minimum Score
```python
MIN_RELEVANCE_SCORE = 8  # Adjust 5-15
```

**Recommendations:**
- 5: Loose (high recall, more noise)
- 8: Balanced (recommended default)
- 12: Strict (high precision, may miss posts)

### Strong Indicators (+15 points)
```python
STRONG_RELEVANCE_INDICATORS = [
    "exact match phrases",
    "category keywords",
]
```

**Examples by Use Case:**
- **Tool research:** "survey platform", "form builder"
- **Competitor:** "alternative to", "competitor name"
- **Feature:** "feature request", "use case"

### High Relevance (+10 points)
```python
HIGH_RELEVANCE_PHRASES = [
    "alternative to",
    "better than",
    "pain point",
    "frustrated with",
    "looking for",
    "recommendation",
]
```

### Themes (+2 points each)
```python
RELEVANT_THEMES = [
    "pricing",
    "integration",
    "feature",
    "support",
    "ease of use",
]
```

---

## Comment Collection Parameters

### Max Comments
```python
MAX_COMMENTS_PER_POST = 20  # 10-50 typical
```

**Guidelines:**
- 10: Quick overview
- 20: Good balance (recommended)
- 50: Deep analysis
- 100+: Viral posts only

---

## Common Configurations

### Competitor Monitoring
```python
KEYWORDS = ["Competitor1", "Competitor2", "Competitor3"]
SUBREDDITS = [("SaaS", 0), ("startups", 0)]
MONTHS_BACK = 6
MIN_RELEVANCE_SCORE = 8
```

### Market Research
```python
KEYWORDS = ["problem keyword", "solution keyword"]
SUBREDDITS = [("niche_subreddit", 0), ("industry_subreddit", 0)]
MONTHS_BACK = 12
MIN_RELEVANCE_SCORE = 10
```

### Brand Monitoring
```python
KEYWORDS = ["YourBrand"]
SUBREDDITS = [("all", 0)]  # Search everywhere
MONTHS_BACK = 1
MIN_RELEVANCE_SCORE = 5
```

### Trend Analysis
```python
KEYWORDS = ["trending_topic"]
SUBREDDITS = [("relevant_sub1", 0), ("relevant_sub2", 0)]
MONTHS_BACK = 3
MIN_RELEVANCE_SCORE = 8
```

---

## Output Files

### Naming Convention
- Posts: `{project}_posts_{YYYYMMDD_HHMMSS}.csv`
- Comments: `{project}_comments_{YYYYMMDD_HHMMSS}.csv`
- Stats: `{project}_stats_{YYYYMMDD_HHMMSS}.txt`

### CSV Columns

**Posts CSV:**
- post_id, matched_keyword, created_date
- title, selftext, subreddit, author
- score, upvote_ratio, num_comments
- url, permalink, is_self, link_flair_text

**Comments CSV:**
- post_id, post_title, comment_id
- comment_author, comment_body
- comment_score, comment_created_date
- comment_permalink, is_submitter

---

## Rate Limits

### Reddit API Limits
- 60 requests per minute
- ~1000 results per search query

### Script Delays
```python
time.sleep(1)   # Between comments
time.sleep(2)   # Between subreddits
```

### Estimated Times
- 5 subreddits × 3 keywords = ~5-10 minutes
- 100 posts × comment fetch = ~5 minutes
- Total for full collection: ~15-30 minutes

---

## Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| No results | Check keyword spelling, expand time range |
| Too many results | Add exclusion patterns, tighten filter |
| Rate limit error | Increase sleep delays, wait 60 seconds |
| API authentication | Verify credentials, check app status |
| Missing comments | Check posts on Reddit manually first |
| Encoding errors | Scripts include UTF-8 fixes for Windows |

---

## Best Practices

1. **Start Small**
   - Test 1-2 subreddits first
   - Verify results before scaling

2. **Document Everything**
   - Save search parameters
   - Note filtering decisions
   - Record rationale for future runs

3. **Iterate**
   - Review initial results
   - Adjust keywords/filters
   - Re-run with refined parameters

4. **Respect Rate Limits**
   - Don't decrease sleep delays
   - Split large collections
   - Run during off-peak hours

5. **Quality Over Quantity**
   - Better to have 100 relevant posts than 1000 mixed
   - Always apply relevance filtering
   - Manual review of top posts recommended

---

## Quick Start Checklist

- [ ] Install `praw` library
- [ ] Get Reddit API credentials
- [ ] Define keywords (3-10 terms)
- [ ] Select subreddits (3-7 communities)
- [ ] Set time range (6-12 months)
- [ ] Configure exclusion patterns
- [ ] Run collection script
- [ ] Review results sample
- [ ] Apply relevance filter (optional)
- [ ] Collect comments (optional)
- [ ] Analyze output files
- [ ] Extract insights and action items

---

## Command Shortcuts

### Installation
```bash
pip install praw
```

### Run Collection
```bash
python reddit_keyword_search.py
```

### Run Filter
```bash
python reddit_filter.py
```

### Collect Comments
```bash
python reddit_comments.py
```

### Quick Analysis
```bash
# Count posts by keyword
python -c "import csv; import sys; from collections import Counter; posts = list(csv.DictReader(open('posts.csv', encoding='utf-8'))); print(Counter([p['matched_keyword'] for p in posts]))"
```

---

## Next Steps After Collection

1. **Immediate Review**
   - Check stats file for overview
   - Read top 10 posts by score
   - Verify data quality

2. **Analysis**
   - Identify common themes
   - Extract pain points
   - Note feature requests
   - Map competitive insights

3. **Action**
   - Share findings with team
   - Update product roadmap
   - Inform marketing messaging
   - Address customer pain points

4. **Recurring**
   - Schedule next collection
   - Track metrics over time
   - Monitor trends

---

## Support

- Main documentation: `SKILL.md`
- Usage examples: `reddit_examples.md`
- Reddit API: https://www.reddit.com/dev/api/
- PRAW docs: https://praw.readthedocs.io/
