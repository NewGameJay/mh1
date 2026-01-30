# Skill Implementation Plan

**Date:** 2026-01-29
**Current State:** 22/65 skills executable (34%)
**Target State:** 65/65 skills executable (100%)

---

## Why This Matters

### The Problem
Skills without `run.py` are **documentation-only**. They describe what should happen but can't actually execute. This means:
- Marketers can't run them from CLI
- Workflows can't chain them automatically
- No programmatic access for agents
- No telemetry/tracking on execution
- Can't be tested or validated

### The Value of Executable Skills
Each `run.py` provides:
1. **CLI execution** - `./mh1 run skill-name --inputs`
2. **Programmatic API** - `from skills.skill_name.run import run_skill_name`
3. **Workflow integration** - Can be chained in multi-step workflows
4. **Telemetry** - Token usage, runtime, success/failure tracking
5. **Budget enforcement** - Cost tracking per tenant
6. **Intelligence integration** - Learning from outcomes

---

## Implementation Phases

### Phase 1: Revenue-Critical Skills (8 skills)
**Priority:** P0 - These directly impact client revenue outcomes
**Timeline:** First batch

| Skill | Why It's Critical |
|-------|------------------|
| `churn-prediction` | Identifies at-risk customers before they leave. Direct revenue protection. |
| `upsell-candidates` | Finds expansion opportunities in existing customers. Revenue growth. |
| `pipeline-analysis` | Analyzes sales pipeline health. Forecasting accuracy. |
| `deal-velocity` | Tracks how fast deals move through stages. Sales optimization. |
| `at-risk-detection` | Real-time risk signals on accounts. Retention campaigns. |
| `renewal-tracker` | Monitors upcoming renewals. Prevents surprise churn. |
| `reactivation-detection` | Identifies dormant customers showing new signals. Win-back campaigns. |
| `dormant-detection` | Flags accounts going quiet. Early intervention. |

**Business Impact:** These 8 skills form the core of lifecycle marketing automation. Without them, clients can't run proactive retention or expansion programs.

---

### Phase 2: Content Production Skills (5 skills)
**Priority:** P1 - High-volume daily use by marketers
**Timeline:** Second batch

| Skill | Why It's Critical |
|-------|------------------|
| `email-copy-generator` | Generates email copy from briefs. Daily marketer workflow. |
| `direct-response-copy` | Creates conversion-focused copy. Ad campaigns, landing pages. |
| `seo-content` | Generates SEO-optimized articles. Organic traffic. |
| `lead-magnet` | Creates lead magnet content (guides, checklists). Lead gen. |
| `cohort-email-builder` | Builds segment-specific email campaigns. Personalization at scale. |

**Business Impact:** Content production is the #1 time sink for marketers. These skills can 10x output.

---

### Phase 3: Research & Extraction Skills (5 skills)
**Priority:** P1 - Foundation for personalized content
**Timeline:** Third batch

| Skill | Why It's Critical |
|-------|------------------|
| `extract-company-profile` | Pulls structured company data. Account research. |
| `extract-founder-voice` | Captures founder's communication style. Authentic ghostwriting. |
| `extract-pov` | Extracts point-of-view and opinions. Thought leadership content. |
| `extract-writing-guideline` | Parses brand voice guidelines. Consistent content. |
| `generate-context-summary` | Creates context summaries for other skills. Skill chaining. |

**Business Impact:** Without these, every skill starts from scratch. These enable context-aware execution.

---

### Phase 4: Platform Integration Skills (7 skills)
**Priority:** P2 - Enable data flow between systems
**Timeline:** Fourth batch

| Skill | Why It's Critical |
|-------|------------------|
| `bright-crawler` | Web scraping via BrightData. Competitor monitoring. |
| `linkedin-browser-scrape` | Browser-based LinkedIn extraction. When API fails. |
| `dataforseo` | SEO data extraction. Keyword/ranking data. |
| `foreplay-ads` | Ad creative inspiration library. Campaign ideation. |
| `firebase-bulk-upload` | Batch upload to Firebase. Data migration. |
| `firestore-nav` | Navigate Firestore collections. Data exploration. |
| `upload-posts-to-notion` | Push content to Notion. Content calendar sync. |

**Business Impact:** MH1 needs to read/write to many platforms. These are the data pipes.

---

### Phase 5: Discovery & Audit Skills (6 skills)
**Priority:** P2 - Onboarding and health checks
**Timeline:** Fifth batch

| Skill | Why It's Critical |
|-------|------------------|
| `crm-discovery` | Maps CRM schema and data. New client onboarding. |
| `data-warehouse-discovery` | Explores warehouse tables. Analytics setup. |
| `data-quality-audit` | Checks data completeness. Identifies gaps. |
| `identity-mapping` | Links identities across systems. Single customer view. |
| `call-analytics` | Analyzes call transcripts. Sales insights. |
| `sales-rep-performance` | Scores rep effectiveness. Sales coaching. |

**Business Impact:** These are the "eyes" of MH1 - they help understand what data exists and its quality.

---

### Phase 6: Meta/System Skills (7 skills)
**Priority:** P2 - System capabilities and self-improvement
**Timeline:** Sixth batch

| Skill | Why It's Critical |
|-------|------------------|
| `client-onboarding` | Orchestrates new client setup. First-run experience. |
| `needs-assessment` | Evaluates if MH1 can help a prospect. Qualification. |
| `skill-builder` | Creates new skills from templates. Self-evolution. |
| `playbook-executor` | Runs multi-skill playbooks. Workflow automation. |
| `artifact-manager` | Manages outputs and versions. Asset tracking. |
| `marketing-orchestrator` | Coordinates marketing campaigns. Campaign management. |
| `get-client` | Retrieves client configuration. Context loading. |

**Business Impact:** These make MH1 self-sufficient and scalable.

---

### Phase 7: Analysis Skills (5 skills)
**Priority:** P3 - Advanced analytics
**Timeline:** Seventh batch

| Skill | Why It's Critical |
|-------|------------------|
| `cohort-retention-analysis` | Analyzes retention by cohort. Strategic planning. |
| `cold-email-personalization` | Personalizes outbound at scale. Sales outreach. |
| `account-360` | Complete account view. Customer success. |
| `conversion-funnel` | Funnel analysis and optimization. Growth. |
| `engagement-velocity` | Tracks engagement momentum. Lead scoring. |

**Business Impact:** Deep analytics for strategic decisions.

---

## Implementation Pattern

Each `run.py` follows this structure:

```python
#!/usr/bin/env python3
"""
{Skill Name} - Execution Script (v1.0.0)

{Description of what it does}

Usage:
    python skills/{skill-name}/run.py --param value

    from skills.{skill_name}.run import run_{skill_name}
    result = run_{skill_name}({"param": "value"})
"""

import argparse
import json
import sys
import time
import uuid
from pathlib import Path
from typing import Dict

# Standard imports and runner setup
SKILL_NAME = "{skill-name}"
SKILL_VERSION = "v1.0.0"

class {SkillName}Skill:
    """Main skill class."""

    def __init__(self, client_id: str = None):
        self.client_id = client_id or "standalone"
        self.run_id = str(uuid.uuid4())[:8]
        self.start_time = time.time()

    def run(self, inputs: Dict) -> Dict:
        """Main execution method."""
        # 1. Validate inputs
        # 2. Execute skill logic
        # 3. Return structured result
        pass

def run_{skill_name}(inputs: Dict) -> Dict:
    """Main entry point."""
    skill = {SkillName}Skill(client_id=inputs.get("client_id"))
    return skill.run(inputs)

def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser()
    # Add arguments
    args = parser.parse_args()
    result = run_{skill_name}(vars(args))
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
```

---

## Execution Order

```
Phase 1: Revenue-Critical (8)  ─┬─► Immediate client value
Phase 2: Content (5)           ─┤
Phase 3: Research (5)          ─┴─► Daily marketer workflow

Phase 4: Platform (7)          ─┬─► System integration
Phase 5: Discovery (6)         ─┤
Phase 6: Meta (7)              ─┴─► System capabilities

Phase 7: Analysis (5)          ───► Advanced features
                               ═══
                               43 skills total
```

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Executable skills | 22 (34%) | 65 (100%) |
| Skills with tests | ~10 | 65 |
| Avg execution time | N/A | <30s |
| API fallback rate | 0% | 100% |

---

## Dependencies

Before implementing, ensure:
1. ✅ `lib/runner.py` - WorkflowRunner, SkillRunner available
2. ✅ `lib/evaluator.py` - Output evaluation
3. ✅ `lib/telemetry.py` - Run logging
4. ✅ `lib/mcp_client.py` - MCP integrations
5. ⚠️ API keys configured (Crustdata, etc.)

---

## Estimated Effort

| Phase | Skills | Est. Time | Complexity |
|-------|--------|-----------|------------|
| Phase 1 | 8 | 2-3 hours | Medium (CRM logic) |
| Phase 2 | 5 | 1-2 hours | Low (template-based) |
| Phase 3 | 5 | 1-2 hours | Medium (parsing) |
| Phase 4 | 7 | 2-3 hours | High (API integration) |
| Phase 5 | 6 | 2-3 hours | Medium (discovery) |
| Phase 6 | 7 | 2-3 hours | Medium (orchestration) |
| Phase 7 | 5 | 1-2 hours | Medium (analytics) |
| **Total** | **43** | **12-18 hours** | |

---

## Next Steps

1. **Approve this plan** - Confirm priority order makes sense
2. **Execute Phase 1** - Revenue-critical skills first
3. **Test each phase** - Ensure skills work before moving on
4. **Update tests** - Add test coverage for new skills
5. **Update docs** - Document new capabilities

---

*Plan created 2026-01-29*
