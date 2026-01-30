# Orchestrator Agent: [AGENT_NAME]

Version: v1.0.0  
Type: orchestrator  
Author: [name]  
Created: [YYYY-MM-DD]

---

## Purpose

[Describe the orchestrator's role and what workflows it coordinates.]

---

## Capabilities

- [Capability 1: e.g., "Schedules and routes tasks to worker agents"]
- [Capability 2: e.g., "Manages workflow state and checkpoints"]
- [Capability 3: e.g., "Enforces quality gates before output"]

---

## Sub-agents (workers)

| Agent name       | Role                          | When invoked                |
|------------------|-------------------------------|-----------------------------|
| `worker_1`       | [role description]            | [trigger condition]         |
| `worker_2`       | [role description]            | [trigger condition]         |
| `eval_agent`     | Quality gate evaluation       | After every output          |

---

## Workflow pattern

```
[Describe the orchestration pattern]

1. Receive input
2. Parse and validate input
3. Check context size, determine handling strategy
4. Route to appropriate worker(s)
5. Collect worker outputs
6. Run evaluation agent
7. If eval passes: return output
8. If eval fails: retry with constraints OR route to human
```

---

## Subagent spawning

For complex tasks, the orchestrator may spawn isolated subagents. This follows patterns from Cursor 2.4 and the RLM paper.

### When to use subagents

| Pattern | When to use | Example |
|---------|-------------|---------|
| **Sequential** | Steps depend on each other | Audit → Analyze → Report |
| **Parallel** | Independent subtasks | Analyze 5 accounts simultaneously |
| **Recursive** | Self-similar decomposition | Chunk 50K records → process each → aggregate |

### Subagent configuration

```yaml
subagent_config:
  max_parallel: 5          # Max concurrent subagents
  timeout_per_agent: 60    # Seconds per subagent
  model: "claude-haiku"    # Default model for subagents (cheaper)
  synthesis_model: "claude-sonnet-4"  # Model for final synthesis
  inherit_context: false   # Subagents get isolated context (prevents pollution)
  report_to_parent: true   # Results bubble up to orchestrator
```

### Context isolation

Each subagent receives ONLY:
- The data it needs (not full parent context)
- The specific subtask prompt
- Schema for its expected output

This prevents context pollution and enables:
- Parallel execution without interference
- Cheaper model usage per subagent
- Better error isolation

### Subagent telemetry

Log for each subagent:
- `subagent_id`: Unique identifier
- `parent_run_id`: Parent workflow run ID
- `model`: Model used
- `tokens_in`, `tokens_out`: Token usage
- `duration_ms`: Execution time
- `status`: success | failed

---

## Inputs

| Name        | Type     | Required | Description                      |
|-------------|----------|----------|----------------------------------|
| `task`      | string   | yes      | Task description                 |
| `context`   | object   | no       | Additional context               |
| `config`    | object   | no       | Override default configuration   |

---

## Outputs

| Name        | Type     | Description                      |
|-------------|----------|----------------------------------|
| `result`    | object   | Final output from workflow       |
| `status`    | string   | "success" | "failed" | "review"  |
| `logs`      | array    | Execution logs                   |

---

## Configuration

```yaml
max_retries: 3
timeout_seconds: 300
human_review_threshold: 0.7  # confidence below this triggers review
model: claude-sonnet-4
worker_model: claude-haiku
```

---

## Error handling

| Error type           | Action                                      |
|----------------------|---------------------------------------------|
| Worker timeout       | Retry once, then fail with partial output   |
| Eval failure         | Retry with stricter constraints (max 2x)    |
| Schema validation    | Reject and log; do not retry                |
| API rate limit       | Exponential backoff, max 3 retries          |

---

## Telemetry

Log the following for every run:
- `workflow_id`: unique identifier
- `start_time`, `end_time`: timestamps
- `tokens_used`: total across all agents
- `tool_calls`: list of MCP/API calls
- `status`: pass | fail | review
- `error`: error message if failed

---

## Example invocation

```
/orchestrate [agent-name] --task "Analyze lifecycle data for Acme Corp" --context context.json
```

---

## Checkpoints

| Checkpoint | Description                     | Human review? |
|------------|---------------------------------|---------------|
| After step 3 | Validate worker routing         | No            |
| After step 5 | Eval agent result               | If score < 0.7|
| After step 7 | Final output                    | If flagged    |

---

## Notes

[Any additional context, known limitations, or tips.]
