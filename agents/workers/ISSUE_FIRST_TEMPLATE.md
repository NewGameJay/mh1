# Issue-First Agent Template

> **Research Source:** r12.pdf "A Multi-Agent System for Generating Actionable Business Advice"
> **Evidence:** Removing Issue Agent caused largest quality degradation (-2.8 to -3.3 points)
> **Key Finding:** Problem definition is more important than solution generation

## Overview

The Issue-First pattern ensures clear problem definition before solution generation. This is a **critical path component** - ablation studies show it has the highest impact on output quality.

## Architecture

```
Input Data → [Clustering] → [Issue Extraction] → [Validation] → Defined Issues → [Solution Agents]
```

### Step 1: Clustering
- Embed input data points
- Cluster via HDBSCAN (or similar)
- Select representative samples closest to cluster centroids
- **Purpose:** Reduce noise, focus on representative examples

### Step 2: Issue Extraction
- Analyze representative samples
- Extract themes and specific issues
- Categorize by domain/type
- **Output:** Structured issue definitions

### Step 3: Validation
- Confirm issue framing with available context
- Check for completeness and clarity
- Ensure issues are actionable
- **Quality Gate:** Issue clarity score ≥ 0.8

### Step 4: Handoff
- Pass well-defined issues to solution agents
- Include context and constraints
- Specify success criteria

## Configuration

```yaml
agent:
  name: issue-first-worker
  type: worker
  model: claude-haiku  # Cost-effective for extraction
  
clustering:
  method: hdbscan
  min_cluster_size: 3
  selection: centroid_nearest
  max_representatives: 10

extraction:
  dimensions:
    - theme
    - specific_issue
    - severity
    - affected_segment
    - potential_impact
  
validation:
  min_clarity_score: 0.8
  required_fields:
    - issue_statement
    - context
    - success_criteria

output:
  format: structured_json
  schema: issue-definition.json
```

## Issue Definition Schema

```json
{
  "issue_id": "string",
  "theme": "string",
  "specific_issue": "string",
  "severity": "low|medium|high|critical",
  "affected_segment": "string",
  "context": {
    "representative_examples": ["string"],
    "frequency": "number",
    "trend": "increasing|stable|decreasing"
  },
  "success_criteria": ["string"],
  "constraints": ["string"],
  "priority_score": "number"
}
```

## Quality Metrics

| Metric | Threshold | Purpose |
|--------|-----------|---------|
| Issue Clarity | ≥ 0.8 | Can solution agents understand the problem? |
| Scope Definition | ≥ 0.7 | Is the issue well-bounded? |
| Actionability Potential | ≥ 0.7 | Can this issue be addressed? |
| Context Completeness | ≥ 0.8 | Is sufficient context provided? |

## Integration Points

### Upstream
- Data ingestion pipelines
- Customer feedback systems
- Analytics dashboards

### Downstream
- Recommendation agents
- Solution generation agents
- Evaluation agents

## Example Usage

**Input:** 500 customer reviews for a hotel

**Clustering Output:**
- Cluster 1: Check-in experience (127 reviews)
- Cluster 2: Room cleanliness (98 reviews)
- Cluster 3: Staff responsiveness (84 reviews)

**Issue Extraction Output:**
```json
{
  "issue_id": "CHK-001",
  "theme": "Check-in & Reservation",
  "specific_issue": "Long wait times at check-in (30-60+ minutes reported)",
  "severity": "high",
  "affected_segment": "Business travelers, peak hours",
  "context": {
    "representative_examples": [
      "Waited 45 minutes to check in despite having a reservation",
      "Line was out the door at 3pm, only 2 staff members working"
    ],
    "frequency": 127,
    "trend": "increasing"
  },
  "success_criteria": [
    "Reduce average check-in time to under 10 minutes",
    "Eliminate waits over 15 minutes during peak hours"
  ],
  "constraints": [
    "Budget for staffing limited",
    "Physical lobby space constraints"
  ],
  "priority_score": 0.89
}
```

## Why Issue-First Matters

From r12.pdf ablation study:

| Configuration | Quality Score Drop |
|---------------|-------------------|
| Full Framework | Baseline |
| Without Issue Agent | -2.8 to -3.3 points |
| Without Evaluation Agent | -0.6 to -1.1 points |
| Without Both | -3.0 to -4.0 points |

**Conclusion:** Issue definition has 3× more impact than evaluation on final quality.

## Anti-Patterns

❌ **Don't:** Jump directly to solutions without issue framing
❌ **Don't:** Use vague issue statements ("things could be better")
❌ **Don't:** Skip clustering and analyze all data points equally
❌ **Don't:** Omit success criteria from issue definitions

## Related Templates

- `MULTI_AGENT_PIPELINE.md` - Orchestrates Issue-First with solution agents
- `EVALUATOR_TEMPLATE.md` - Evaluates solution quality
- `WORKER_TEMPLATE.md` - Base worker pattern
