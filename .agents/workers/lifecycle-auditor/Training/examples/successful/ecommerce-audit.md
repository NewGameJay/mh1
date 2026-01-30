# Successful Interaction Example: E-commerce Lifecycle Audit

## Context

**Client**: StyleBox (D2C E-commerce, Fashion Subscription)
**Date**: 2024-12-03
**Agent**: lifecycle-auditor v1.0.0

## User Request

```
We need a quarterly lifecycle audit for StyleBox. Focus on subscriber retention and identifying our best customers for a referral program.
```

## Agent Analysis

### Intent Recognition
- **Primary intent**: Quarterly audit with retention and referral program focus
- **Confidence**: 0.89
- **Skills identified**: lifecycle-audit (with retention and upsell emphasis)

### Context Loaded
- Voice contract: No
- Company research: Yes (D2C subscription, $8M ARR, avg order $75)
- Recent signals: High CAC concerns in Q3
- Previous interactions: 1 (Q3 audit available for comparison)

## Plan Created

```markdown
## Execution Plan

**Request:** Quarterly lifecycle audit focused on retention and referral program targeting

### Steps:
1. **Data Discovery** - Fetch all contacts from HubSpot
   - Expected: 5000+ contacts (D2C high volume)
   - Duration: 15s

2. **Cohort Analysis** - Compare Q4 to Q3 metrics
   - Expected: Trend comparison
   - Duration: 20s

3. **Retention Analysis** - Identify churn patterns and at-risk segments
   - Expected: At-risk list with risk scores
   - Duration: 15s

4. **Evangelist Identification** - Find best customers for referral
   - Expected: Referral program candidate list
   - Duration: 10s

5. **Recommendations** - Retention + referral strategies
   - Expected: Segment-specific recommendations
   - Duration: 10s

### Expected Outcomes:
- Q4 vs Q3 trend comparison
- At-risk customer segments with intervention strategies
- Referral program candidate list with criteria
- Actionable recommendations for both retention and growth

Proceed? [Y/n]
```

## Execution

### Step 1: Data Discovery
- **Status**: Success
- **Output**: 8,234 contacts retrieved (chunked processing used)
- **Quality score**: 0.91

### Step 2: Cohort Analysis
- **Status**: Success
- **Output**: Q3 vs Q4 comparison with 12% improvement in subscriber retention
- **Quality score**: 0.93

### Step 3: Retention Analysis
- **Status**: Success
- **Output**: 847 at-risk customers identified across 3 segments
- **Quality score**: 0.88

### Step 4: Evangelist Identification
- **Status**: Success
- **Output**: 234 referral candidates identified (top 3% of customers)
- **Quality score**: 0.90

### Step 5: Recommendations
- **Status**: Success
- **Output**: 6 recommendations (3 retention, 3 referral)
- **Quality score**: 0.86

## Final Output

```json
{
  "summary": {
    "total_accounts": 8234,
    "by_stage": {
      "subscriber": 2145,
      "lead": 1876,
      "customer": 3421,
      "evangelist": 234,
      "churned": 558
    },
    "health_score": 0.71,
    "trend": "improving"
  },
  "cohort_comparison": {
    "metric": "subscriber_to_customer_90d",
    "q3_2024": 0.28,
    "q4_2024": 0.31,
    "change": "+10.7%",
    "note": "Improvement correlates with welcome sequence update in October"
  },
  "at_risk": [
    {
      "segment": "Lapsed Subscribers",
      "count": 423,
      "criteria": "Subscribed but no purchase in 60+ days",
      "risk_score": 0.82,
      "revenue_at_risk": "$31,725",
      "recommended_action": "Win-back sequence with 15% discount"
    },
    {
      "segment": "One-Time Buyers",
      "count": 312,
      "criteria": "Single purchase >90 days ago, no repeat",
      "risk_score": 0.68,
      "revenue_at_risk": "$23,400 LTV potential",
      "recommended_action": "Second purchase incentive campaign"
    },
    {
      "segment": "Subscription Cancellation Risk",
      "count": 112,
      "criteria": "Active subscriber, skip rate >50% last 3 months",
      "risk_score": 0.75,
      "revenue_at_risk": "$67,200 ARR",
      "recommended_action": "Proactive outreach offering plan flexibility"
    }
  ],
  "referral_candidates": {
    "total": 234,
    "criteria": [
      "Customer >6 months",
      "LTV >$300",
      "NPS promoter (9-10) or high engagement",
      "No support tickets in 90 days"
    ],
    "segments": [
      {
        "name": "Super Fans",
        "count": 67,
        "avg_ltv": "$892",
        "description": "Highest LTV, social media mentions, repeat gifters"
      },
      {
        "name": "Steady Subscribers",
        "count": 134,
        "avg_ltv": "$456",
        "description": "Long tenure, consistent orders, no skips"
      },
      {
        "name": "Rising Stars",
        "count": 33,
        "avg_ltv": "$312",
        "description": "Newer customers with high engagement trajectory"
      }
    ],
    "estimated_referral_value": "$175 per referral (based on industry avg)"
  },
  "recommendations": [
    {
      "priority": "high",
      "category": "retention",
      "action": "Launch automated win-back sequence for 423 lapsed subscribers with personalized product recommendations",
      "impact": "Recover 15-20% ($4,800-6,300) at minimal cost",
      "timeline": "Implement in 2 weeks"
    },
    {
      "priority": "high",
      "category": "retention",
      "action": "Implement subscription flexibility options (pause, frequency change) for at-risk subscribers",
      "impact": "Reduce cancellation rate by 20-30%, save $13,400-20,100 ARR",
      "timeline": "Implement in 4 weeks"
    },
    {
      "priority": "high",
      "category": "expansion",
      "action": "Launch referral program targeting 67 Super Fans first with premium incentives ($25 credit vs standard $10)",
      "impact": "Expected 40% participation, 2.3 referrals/participant = ~62 new customers ($10,850 LTV)",
      "timeline": "Soft launch in 3 weeks"
    },
    {
      "priority": "medium",
      "category": "retention",
      "action": "Create second-purchase trigger campaign for 312 one-time buyers with curated product bundles",
      "impact": "Convert 10-15% to repeat buyers, unlock $23K+ LTV potential",
      "timeline": "Implement in 2 weeks"
    },
    {
      "priority": "medium",
      "category": "expansion",
      "action": "Expand referral program to Steady Subscribers after Super Fan pilot",
      "impact": "Additional 134 participants, ~200 referrals projected",
      "timeline": "Expand in 6 weeks"
    },
    {
      "priority": "low",
      "category": "expansion",
      "action": "Develop Rising Stars nurture track to accelerate to Super Fan status",
      "impact": "Long-term LTV optimization",
      "timeline": "Design in Q1"
    }
  ],
  "_meta": {
    "tenant_id": "stylebox",
    "run_id": "audit_2024120301",
    "execution_mode": "suggest",
    "runtime_seconds": 68.4,
    "cost_usd": 0.78,
    "release_action": "auto_deliver",
    "evaluation_score": 0.85,
    "context_strategy": "chunked",
    "chunks_processed": 9
  }
}
```

## User Feedback

**Rating**: Positive
**Comment**: "Perfect timing on the referral candidates - we were about to pick randomly. The segment breakdown with Super Fans vs Steady Subscribers gives us a clear pilot strategy."

## Why This Worked

### Key Success Factors

1. **Understood D2C context**: Used appropriate metrics for e-commerce (LTV, purchase frequency, skip rate) rather than B2B pipeline stages.

2. **Actionable referral targeting**: Didn't just identify "good customers" - segmented into launchable cohorts with specific characteristics.

3. **Revenue impact quantification**: Every at-risk segment and recommendation tied to dollar amounts.

4. **Trend context**: Included Q3 comparison to show improvement, validating past changes.

### Patterns to Replicate

- For D2C/subscription, focus on purchase behavior and skip patterns over pipeline stages
- Segment referral candidates by launch priority (pilot group first)
- Include timeline estimates for recommendations
- Quantify "revenue at risk" for retention segments
- Note correlations between metrics and known changes (welcome sequence update)

## Metrics

| Metric | Value |
|--------|-------|
| Total time | 68.4s |
| Model calls | 6 (chunked processing) |
| Tokens used | 24,670 |
| User satisfaction | Positive |
| Evaluation score | 0.85 |
| Context strategy | Chunked (9 chunks) |
