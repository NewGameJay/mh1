# Multi-Agent Pipeline Template

> **Research Source:** r5.pdf "MAGE-KT: Multi-Agent Graph-Enhanced Knowledge Tracing"
> **Evidence:** 13%+ improvement over single-agent approaches
> **Pattern:** Semantic → Scoring → Arbitration

## Overview

The Multi-Agent Pipeline coordinates specialized agents in sequence, with each agent contributing distinct capabilities. This pattern reduces variance across model families and improves reliability.

## Architecture

```
Input → [Semantic Agent] → [Scoring Agent] → [Arbitration Agent] → Output
              ↓                   ↓                   ↓
         Understanding      Evaluation          Synthesis
         (Haiku)           (Haiku)             (Sonnet)
```

## Agent Roles

### Agent 1: Semantic Agent
- **Model:** claude-haiku (cost-effective)
- **Purpose:** Initial understanding and extraction
- **Tasks:**
  - Parse input structure
  - Extract key entities and relationships
  - Generate initial interpretations
  - Flag ambiguities for downstream agents

### Agent 2: Scoring Agent
- **Model:** claude-haiku (cost-effective)
- **Purpose:** Multi-dimensional evaluation
- **Tasks:**
  - Apply SRAC framework
  - Score quality dimensions
  - Identify gaps and issues
  - Generate improvement suggestions

### Agent 3: Arbitration Agent
- **Model:** claude-sonnet-4 (high-capability)
- **Purpose:** Final synthesis and decision
- **Tasks:**
  - Resolve conflicts between agents
  - Synthesize final output
  - Ensure quality threshold met
  - Make go/no-go decision

## Configuration

```yaml
orchestrator:
  name: multi-agent-pipeline
  type: orchestrator
  pattern: sequential
  
agents:
  semantic:
    model: claude-haiku
    role: understanding
    timeout: 30s
    retry: 2
    
  scoring:
    model: claude-haiku
    role: evaluation
    timeout: 30s
    retry: 2
    framework: srac
    
  arbitration:
    model: claude-sonnet-4
    role: synthesis
    timeout: 60s
    retry: 1
    
handoff:
  semantic_to_scoring:
    include:
      - extracted_entities
      - relationships
      - interpretations
      - ambiguity_flags
    
  scoring_to_arbitration:
    include:
      - semantic_output
      - dimension_scores
      - improvement_suggestions
      - confidence_scores

quality_gate:
  threshold: 3.5
  dimensions: srac
  require_unanimous: false
```

## Execution Flow

### Phase 1: Semantic Processing
```python
semantic_result = semantic_agent.process(input_data)
# Output: entities, relationships, interpretations
```

### Phase 2: Quality Scoring
```python
scoring_result = scoring_agent.evaluate(
    content=semantic_result,
    framework="srac"
)
# Output: dimension scores, suggestions
```

### Phase 3: Arbitration
```python
final_result = arbitration_agent.synthesize(
    semantic=semantic_result,
    scoring=scoring_result,
    quality_threshold=3.5
)
# Output: final decision, synthesized content
```

## Cost Optimization

| Agent | Model | Cost/1K tokens | Purpose |
|-------|-------|----------------|---------|
| Semantic | Haiku | $0.25 | High volume, extraction |
| Scoring | Haiku | $0.25 | Evaluation, scoring |
| Arbitration | Sonnet | $3.00 | Quality-critical synthesis |

**Expected cost reduction:** 60-70% vs using Sonnet for all stages

## Performance Metrics

From r5.pdf and r12.pdf research:

| Metric | Single Agent | Multi-Agent Pipeline | Improvement |
|--------|--------------|---------------------|-------------|
| Accuracy | Baseline | +13% | Significant |
| Variance | High | Low | More consistent |
| Cost | $X | $0.4X | 60% reduction |
| Reliability | 92% | 98% | More robust |

## Error Handling

### Semantic Agent Failure
- Retry with simplified input
- Fall back to basic extraction
- Log for analysis

### Scoring Agent Failure
- Use default scoring
- Flag for human review
- Continue to arbitration with caveat

### Arbitration Agent Failure
- Return best effort from scoring
- Require human approval
- Never auto-approve without arbitration

## Integration with Issue-First

```
[Issue-First Agent] → Issues → [Multi-Agent Pipeline] → Solutions
                                      ↓
                              Semantic → Scoring → Arbitration
```

## Checkpointing

Save state after each agent:
1. `checkpoint_semantic.json` - After semantic processing
2. `checkpoint_scoring.json` - After scoring
3. `checkpoint_final.json` - After arbitration

Enables resume from any point on failure.

## Telemetry

Track for each run:
- Agent execution times
- Token usage per agent
- Quality scores progression
- Retry counts
- Final pass/fail status

## Example Output

```json
{
  "pipeline_id": "pipe_20260125_001",
  "status": "completed",
  "agents": {
    "semantic": {
      "duration_ms": 2340,
      "tokens": 1523,
      "entities_extracted": 12
    },
    "scoring": {
      "duration_ms": 1890,
      "tokens": 987,
      "srac_score": 4.2
    },
    "arbitration": {
      "duration_ms": 4560,
      "tokens": 2341,
      "decision": "approved"
    }
  },
  "total_cost": "$0.0089",
  "quality_score": 4.2,
  "passed": true
}
```
