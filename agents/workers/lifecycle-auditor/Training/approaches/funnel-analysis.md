# Approach: Funnel Analysis

## Overview

The standard methodology for auditing customer lifecycle stages. Treats the customer journey as a funnel with measurable conversion rates between each stage.

## When to Use

Use this approach when:
- You have 100+ contacts with populated lifecycle stages
- Client wants a comprehensive pipeline health assessment
- No specific concern area has been identified
- Standard lifecycle stages are in use

Do NOT use when:
- Dataset has <50 contacts (use individual account review)
- Client has highly custom/non-linear journey
- Specific concern area already identified (use targeted analysis)

## Process

### Step 1: Stage Distribution Analysis

Count contacts in each lifecycle stage and calculate percentages.

**Example:**
```json
{
  "total_accounts": 1250,
  "by_stage": {
    "subscriber": 450,
    "lead": 320,
    "mql": 180,
    "sql": 120,
    "opportunity": 85,
    "customer": 95
  },
  "percentages": {
    "subscriber": 36.0,
    "lead": 25.6,
    "mql": 14.4,
    "sql": 9.6,
    "opportunity": 6.8,
    "customer": 7.6
  }
}
```

### Step 2: Conversion Rate Calculation

Calculate the conversion rate between each adjacent stage.

**Formula:**
```
conversion_rate = (contacts_in_next_stage / contacts_in_current_stage) * 100
```

**Example:**
```
lead -> mql: 180 / 320 = 56.25%
mql -> sql: 120 / 180 = 66.67%
sql -> opportunity: 85 / 120 = 70.83%
opportunity -> customer: 95 / 85 = 111.76% (historical carryover)
```

**Note:** Rates >100% indicate historical customers not reflected in current funnel.

### Step 3: Benchmark Comparison

Compare each conversion rate against industry benchmarks.

**SaaS B2B Benchmarks:**
| Transition | Benchmark | Good | Excellent |
|------------|-----------|------|-----------|
| Visitor -> Lead | 2-5% | 5-8% | >8% |
| Lead -> MQL | 25-35% | 35-50% | >50% |
| MQL -> SQL | 20-30% | 30-40% | >40% |
| SQL -> Opportunity | 30-40% | 40-55% | >55% |
| Opportunity -> Customer | 15-25% | 25-35% | >35% |

### Step 4: Bottleneck Identification

Flag stages with conversion rates significantly below benchmark.

**Severity Calculation:**
```
gap = benchmark - actual_rate
severity = "high" if gap > 0.15 else "medium" if gap > 0.08 else "low"
```

**Example:**
```json
{
  "bottleneck": {
    "from_stage": "mql",
    "to_stage": "sql",
    "actual_rate": 0.15,
    "benchmark": 0.25,
    "gap": 0.10,
    "severity": "medium"
  }
}
```

### Step 5: Root Cause Hypothesis

For each bottleneck, generate hypotheses based on common patterns.

**MQL -> SQL Bottleneck Hypotheses:**
1. Qualification criteria too loose (many false-positive MQLs)
2. Sales team bandwidth constraints
3. Slow response time to MQL signals
4. Geographic/timezone coverage gaps
5. Product-market fit issues in certain segments

## Expected Outcomes

When executed correctly, this approach produces:
- Complete stage distribution with percentages
- Conversion rates between all adjacent stages
- Identified bottlenecks with severity ratings
- Root cause hypotheses for each bottleneck
- Health score (0-1) for overall funnel performance

## Quality Indicators

**Good execution looks like:**
- All stages have minimum 10 contacts for rate calculation
- Conversion rates are compared against appropriate industry benchmarks
- Bottlenecks have specific, testable hypotheses
- Recommendations directly address identified bottlenecks

**Warning signs:**
- Stages with <10 contacts used for rate calculations
- Generic recommendations not tied to specific bottlenecks
- Missing stages in the analysis
- No benchmark context provided

## Real Example

### Input
```json
{
  "tenant_id": "acme_corp",
  "limit": 500,
  "stages": ["subscriber", "lead", "mql", "sql", "opportunity", "customer"]
}
```

### Output
```json
{
  "summary": {
    "total_accounts": 487,
    "health_score": 0.72
  },
  "by_stage": {
    "subscriber": 142,
    "lead": 156,
    "mql": 78,
    "sql": 42,
    "opportunity": 31,
    "customer": 38
  },
  "conversion_rates": {
    "subscriber_to_lead": 1.10,
    "lead_to_mql": 0.50,
    "mql_to_sql": 0.54,
    "sql_to_opportunity": 0.74,
    "opportunity_to_customer": 1.23
  },
  "bottlenecks": [
    {
      "from_stage": "lead",
      "to_stage": "mql",
      "actual": 0.50,
      "benchmark": 0.30,
      "severity": "low",
      "note": "Performing above benchmark"
    }
  ],
  "health_notes": "Funnel performing above average with 0.72 health score. Lead-to-MQL conversion (50%) significantly exceeds 30% benchmark."
}
```

### Why This Works
The example demonstrates good execution because:
1. All stages have sufficient sample sizes (31-156)
2. Rates are calculated correctly and compared to benchmarks
3. Health score reflects overall performance
4. Even "non-bottlenecks" are noted when performing well

## Common Mistakes

1. **Mistake**: Using raw counts instead of conversion rates
   **Fix**: Always express transitions as percentages for comparability

2. **Mistake**: Applying B2C benchmarks to B2B funnels (or vice versa)
   **Fix**: Use industry-appropriate benchmarks; ask about business model if unclear

3. **Mistake**: Ignoring time dimension
   **Fix**: Consider cohort analysis for trend detection; a static snapshot misses velocity

## Related Approaches

- [Cohort-Based Audit](./cohort-based-audit.md) - Use when trend detection is needed
- [Decision Tree](./decision-tree.md) - For choosing between approaches
