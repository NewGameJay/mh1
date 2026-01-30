# Workflow: Generate Full GTM Proposal

<redirect>
**This workflow has been moved to the `gtm-strategy-consultant` agent.**

Generating full GTM proposals requires strategic analysis, ICP research, buyer persona development, and professional expertise - work that belongs in an agent, not a skill.

## To Generate a Full GTM Proposal

Use the `gtm-strategy-consultant` agent which will:
1. Deep research the company (website, news, LinkedIn)
2. Identify their ICP and sales motion
3. Define buyer personas with titles and triggers
4. Use this skill's API workflows to:
   - Map TAM with Company Discovery API
   - Count decision makers with People Discovery API
5. Recommend 3-5 watchers with business rationale
6. Generate a comprehensive proposal with real data

## How to Invoke

Via Task tool:
```
Task(
  subagent_type="gtm-strategy-consultant",
  prompt="Create a full GTM engineering proposal for [company name] at [website]"
)
```

Or via direct agent invocation:
- "Create a full GTM proposal for [company]"
- "Generate a GTM engineering proposal for [prospect]"
- "Map the TAM and identify decision makers for [company's] ICP"

## What This Skill Provides

This skill handles the API execution portions:
- `workflows/map-tam.md` - Company Discovery API for TAM counts
- `workflows/find-decision-makers.md` - People Discovery API for decision maker counts
- `references/watcher-api.md` - Watcher configuration reference

The agent uses these workflows for data collection while handling the strategic analysis, ICP research, and proposal generation itself.

## GTM Proposal Components

A full GTM proposal includes:
- Executive Summary
- Company Analysis (demonstrates understanding)
- ICP & Buyer Personas (who they sell to)
- TAM Mapping (X companies matching ICP)
- Decision Maker Discovery (Y buyers by seniority)
- Watcher Recommendations (3-5 with signal → outcome)
- Expected Outcomes
- Pilot Proposal

All of these require strategic synthesis performed by the agent, not procedural execution.
</redirect>
