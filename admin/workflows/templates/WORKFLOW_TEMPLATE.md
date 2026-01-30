# Workflow: [WORKFLOW_NAME]

Version: v1.0.0  
Type: [audit | content | analysis | automation]  
Author: [name]  
Created: [YYYY-MM-DD]

---

## Purpose

[Describe what this workflow accomplishes and when to use it.]

---

## Trigger

- **Manual:** `/run-workflow [workflow-name] --input [input-file]`
- **Scheduled:** [cron expression, if applicable]
- **Event:** [trigger event, if applicable]

---

## Inputs

| Name        | Type     | Required | Description                      |
|-------------|----------|----------|----------------------------------|
| `input_1`   | object   | yes      | Description                      |
| `input_2`   | string   | no       | Description                      |

**Input schema:** `schemas/workflow-input.json`

---

## Outputs

| Name        | Type     | Description                      |
|-------------|----------|----------------------------------|
| `output_1`  | object   | Description                      |
| `status`    | string   | "success" | "failed" | "review"  |

**Output schema:** `schemas/workflow-output.json`

---

## Steps

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Input validation                                    │
│  Agent: orchestrator                                         │
│  Checkpoint: yes                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: Data extraction                                     │
│  Agent: worker-extractor                                     │
│  Skills: [skill-1, skill-2]                                  │
│  Checkpoint: no                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3: Analysis                                            │
│  Agent: worker-analyzer                                      │
│  Skills: [skill-3]                                           │
│  Checkpoint: yes                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 4: Quality gate                                        │
│  Agent: evaluator                                            │
│  Checkpoint: yes (human if score < 0.7)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 5: Output formatting                                   │
│  Agent: worker-formatter                                     │
│  Checkpoint: no                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Step details

### Step 1: Input validation + Context sizing

**Purpose:** Validate input against schema, check required fields, determine context handling strategy.

**Agent:** orchestrator  
**Model:** claude-haiku (fast validation)

**Actions:**
1. Parse input JSON
2. Validate against input schema
3. Check for missing required fields
4. Normalize field names
5. **Estimate input size and determine context strategy**

**Context handling decision:**
```python
from lib import should_offload_context, ContextStrategy

should_offload, strategy = should_offload_context(input_data)

if strategy == ContextStrategy.INLINE:
    # Process directly in subsequent steps
    pass
elif strategy == ContextStrategy.CHUNKED:
    # Enable chunked processing for Step 2
    workflow_config["use_chunking"] = True
    workflow_config["chunk_size"] = 500
elif strategy == ContextStrategy.OFFLOADED:
    # Use full context manager
    workflow_config["use_context_manager"] = True
```

**On success:** Proceed to Step 2 with context strategy  
**On failure:** Return error with validation details

---

### Step 2: Data extraction

**Purpose:** Extract relevant data from input sources.

**Agent:** worker-extractor  
**Skills:** `skill-1`, `skill-2`  
**Model:** claude-haiku (for extraction sub-tasks)

**Actions:**
1. Check context strategy from Step 1
2. If chunked/offloaded:
   - Initialize ContextManager
   - Process chunks with haiku
   - Aggregate results
3. If inline:
   - Load skill-1, execute extraction
   - Load skill-2, execute extraction
4. Combine results

**Context handling pattern:**
```python
if workflow_config.get("use_context_manager"):
    ctx = ContextManager(input_data, ContextConfig())
    for chunk in ctx.chunk(size=workflow_config.get("chunk_size", 500)):
        result = run_skill("skill-1", chunk, model="claude-haiku")
        ctx.aggregate_buffer("extracted", result)
    extraction_output = ctx.get_aggregated("extracted")
else:
    extraction_output = run_skill("skill-1", input_data)
```

**On success:** Proceed to Step 3  
**On failure:** Retry once, then fail with partial output

---

### Step 3: Analysis

**Purpose:** Analyze extracted data and generate insights.

**Agent:** worker-analyzer  
**Skills:** `skill-3`  
**Model:** claude-sonnet-4 (high reasoning)

**Actions:**
1. Load skill-3 with extraction output
2. Perform analysis
3. Generate structured insights

**Checkpoint:** Review analysis before proceeding

**On success:** Proceed to Step 4  
**On failure:** Route to human review

---

### Step 4: Quality gate

**Purpose:** Evaluate output quality before delivery.

**Agent:** evaluator  
**Model:** claude-sonnet-4

**Actions:**
1. Load output from Step 3
2. Run evaluation checks
3. Score each dimension
4. Return pass/fail

**On pass (score >= 0.8):** Proceed to Step 5  
**On marginal (score 0.6-0.8):** Retry Step 3 with stricter constraints  
**On fail (score < 0.6):** Route to human review

---

### Step 5: Output formatting

**Purpose:** Format final output for delivery.

**Agent:** worker-formatter  
**Model:** claude-haiku

**Actions:**
1. Convert to delivery format (Markdown/JSON)
2. Add metadata (run ID, timestamp, version)
3. Return final output

---

## Error handling

| Error type           | Step | Action                                      |
|----------------------|------|---------------------------------------------|
| Input validation     | 1    | Return error immediately                    |
| Extraction failure   | 2    | Retry once, then partial output             |
| Analysis failure     | 3    | Route to human                              |
| Eval failure         | 4    | Retry or route to human                     |
| Formatting failure   | 5    | Return raw output with warning              |

---

## Telemetry

Log for each run:
- `workflow_id`: unique identifier
- `workflow_name`: name of this workflow
- `start_time`, `end_time`: timestamps
- `step_timings`: time per step
- `tokens_used`: total and per step
- `tool_calls`: list of MCP/API calls
- `status`: success | failed | review
- `error`: error message if failed
- `eval_score`: quality gate score
- `context_handling`: strategy, input_size, chunks_processed, sub_calls

**Context handling telemetry example:**
```json
{
  "context_handling": {
    "strategy": "chunked",
    "input_size_tokens": 35000,
    "chunks_processed": 70,
    "sub_calls": [
      {"model": "claude-haiku", "task_type": "extraction", "tokens_in": 500, "tokens_out": 150}
    ],
    "total_sub_call_tokens": 45500,
    "sub_call_cost_estimate_usd": 0.01
  }
}
```

---

## Example run

**Input:**
```json
{
  "input_1": { "data": "..." },
  "input_2": "optional value"
}
```

**Command:**
```
/run-workflow [workflow-name] --input input.json
```

**Output:**
```json
{
  "output_1": { "result": "..." },
  "status": "success",
  "metadata": {
    "workflow_id": "abc123",
    "run_time_seconds": 45,
    "eval_score": 0.92
  }
}
```

---

## Notes

[Any additional context, known limitations, or tips.]
