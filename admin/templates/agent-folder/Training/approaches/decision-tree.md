# Decision Tree: Choosing the Right Approach

Use this decision tree to select the appropriate approach for a given situation.

## Quick Reference

```
START
  │
  ├─ Is this a NEW client? ──────────────────────── Yes ─→ Approach: Discovery First
  │                                                        (research-company, research-founder)
  │
  ├─ Is context COMPLETE? ───────────────────────── No ──→ Approach: Context Gap Fill
  │   (voice contract, company research)                   (identify and fill gaps)
  │
  ├─ Is this CONTENT creation? ──────────────────── Yes ─→ See Content Decision Tree
  │
  ├─ Is this ANALYSIS? ──────────────────────────── Yes ─→ See Analysis Decision Tree
  │
  └─ Is this AUTOMATION? ────────────────────────── Yes ─→ See Automation Decision Tree
```

## Content Decision Tree

```
CONTENT REQUEST
  │
  ├─ Voice contract exists? ─────────────────────── No ──→ Run extract-founder-voice first
  │
  ├─ Single piece or batch? ─────────────────────── Batch → Use assignment briefs
  │                                                  Single → Direct ghostwrite
  │
  ├─ Platform?
  │   ├─ LinkedIn ────────────────────────────────────────→ Use 81 templates
  │   ├─ Email ───────────────────────────────────────────→ Use email templates
  │   ├─ Ad Copy ─────────────────────────────────────────→ Use ad templates
  │   └─ Other ───────────────────────────────────────────→ Generic content skill
  │
  └─ Needs signals? ─────────────────────────────── Yes ─→ Run social-listening-collect first
```

## Analysis Decision Tree

```
ANALYSIS REQUEST
  │
  ├─ Data source?
  │   ├─ CRM (HubSpot/Salesforce) ────────────────────────→ Use crm-discovery
  │   ├─ Warehouse (Snowflake/BQ) ────────────────────────→ Use warehouse queries
  │   ├─ External (LinkedIn/Twitter) ─────────────────────→ Use research skills
  │   └─ Mixed ───────────────────────────────────────────→ Multi-source pipeline
  │
  ├─ Analysis type?
  │   ├─ Lifecycle audit ─────────────────────────────────→ hubspot-lifecycle-audit
  │   ├─ Competitor analysis ─────────────────────────────→ research-competitors
  │   ├─ Audience analysis ───────────────────────────────→ extract-audience-persona
  │   └─ Custom ──────────────────────────────────────────→ Build with skill-builder
  │
  └─ Output format?
      ├─ Report ──────────────────────────────────────────→ Include report template
      ├─ Data ────────────────────────────────────────────→ JSON output only
      └─ Both ────────────────────────────────────────────→ Full output + report
```

## Confidence Levels

| Situation | Required Confidence | Action if Below |
|-----------|--------------------|-----------------|
| Skill selection | 0.7 | Present alternatives, ask user |
| Parameter inference | 0.8 | Ask for clarification |
| Content generation | 0.7 | Generate but flag for review |
| Automated execution | 0.9 | Require explicit approval |

## Escalation Triggers

Always escalate to human when:
- Confidence < 0.5 on any decision
- User expresses dissatisfaction
- Multiple approaches seem equally valid
- Request involves sensitive/legal content
- Request requires capabilities not in skill set
