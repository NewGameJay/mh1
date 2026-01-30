# Workflow: Generate Watcher Proposal

<redirect>
**This workflow has been moved to the `gtm-strategy-consultant` agent.**

Generating proposals requires strategic analysis, ICP research, and professional expertise - work that belongs in an agent, not a skill.

## To Generate a Proposal

Use the `gtm-strategy-consultant` agent which will:
1. Research the company and understand their business
2. Identify their ICP and buyer personas
3. Map buying triggers to appropriate watchers
4. Use this skill's API workflows for data collection
5. Generate a strategic proposal with recommendations

## How to Invoke

Via Task tool:
```
Task(
  subagent_type="gtm-strategy-consultant",
  prompt="Create a GTM proposal for [company name] at [website]"
)
```

Or via direct agent invocation:
- "Create a GTM proposal for [company]"
- "What watchers should [company] use?"
- "Build a sales intelligence proposal for [prospect]"

## What This Skill Provides

This skill handles the API execution portions:
- `workflows/map-tam.md` - Company Discovery API for TAM counts
- `workflows/find-decision-makers.md` - People Discovery API for decision maker counts
- `references/watcher-api.md` - Watcher configuration reference

The agent uses these workflows for data collection while handling the strategic analysis itself.
</redirect>
