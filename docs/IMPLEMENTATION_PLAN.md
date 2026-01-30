# MH1 Vercel Integration - Optimized Implementation Plan

**Created:** January 28, 2026  
**Duration:** 6 weeks (optimized from 10)  
**Parallelization:** 60% of work streams run concurrently

---

## Optimization Strategy

The original 10-week plan assumed sequential execution. This optimized plan:
1. **Parallelizes independent streams** (format + browser + UI scaffolding)
2. **Front-loads high-value items** (skill format enables everything else)
3. **Defers nice-to-haves** (publishing can happen anytime)
4. **Creates clear milestones** with validation gates

---

## Phase Overview

```
Week 1     Week 2     Week 3     Week 4     Week 5     Week 6
──────────────────────────────────────────────────────────────
STREAM A: Skill Format ████████████░░░░░░░░░░░░░░░░░░░░░░░░
STREAM B: Browser      ░░░░░░░░████████████░░░░░░░░░░░░░░░░
STREAM C: UI Foundation░░░░░░░░░░░░░░░░████████████████████
STREAM D: Publishing   ░░░░░░░░░░░░░░░░░░░░░░░░████████████
                                         ^
                                    Milestone 1
```

---

## Stream A: Skill Format Migration (Week 1-2)

**Goal:** All 25 skills use AgentSkills.io YAML frontmatter

### Week 1: Foundation

| Day | Deliverable | Owner | Validation |
|-----|-------------|-------|------------|
| 1 | `schemas/skill-frontmatter.json` - JSON Schema for YAML validation | Dev | Schema validates against spec |
| 1 | `scripts/validate_skill.py` - Validation script | Dev | Runs on template |
| 2 | Updated `SKILL_TEMPLATE/SKILL.md` with hybrid format | Dev | Passes validation |
| 2-3 | Migrate 5 core skills: `ghostwrite-content`, `lifecycle-audit`, `social-listening-collect`, `get-client`, `firestore-nav` | Dev | All pass validation |
| 4-5 | Migrate 10 extraction skills: `extract-*`, `research-*`, `generate-*` | Dev | All pass validation |

### Week 2: Completion

| Day | Deliverable | Owner | Validation |
|-----|-------------|-------|------------|
| 1-2 | Migrate remaining 10 skills: `linkedin-*`, `twitter-*`, `reddit-*`, `icp-*`, `qualify-*`, `incorporate-*`, `create-*`, `upload-*`, `firebase-*` | Dev | All pass validation |
| 3 | Add "When to Use" trigger phrases to all skills | Dev | Each has 3+ triggers |
| 4 | Create migration report: before/after comparison | Dev | Documented |
| 5 | **MILESTONE 1 GATE:** All skills validated, tested with Claude | QA | 100% pass rate |

### Deliverables Checklist

- [ ] `schemas/skill-frontmatter.json` - AgentSkills.io compliant schema
- [ ] `scripts/validate_skill.py` - Batch validation tool
- [ ] 25 migrated SKILL.md files
- [ ] Migration report in `docs/skill-migration-report.md`

---

## Stream B: Browser Automation (Week 2-3)

**Goal:** `agent-browser` integrated as fallback for LinkedIn scraping

**Prerequisite:** None (runs parallel to Stream A Week 2)

### Week 2: Setup & Wrapper

| Day | Deliverable | Owner | Validation |
|-----|-------------|-------|------------|
| 1 | Install agent-browser globally, create profile dirs | Dev | `agent-browser --help` works |
| 2 | `lib/browser_automation.py` - MH1 wrapper class | Dev | Unit tests pass |
| 3 | `lib/browser_rate_limiter.py` - Platform-specific limits | Dev | Rate limits enforced |
| 4 | LinkedIn authentication profile setup | Dev | Authenticated session persists |
| 5 | Test basic scraping: profile, post, reactions | Dev | Data extracted correctly |

### Week 3: Integration

| Day | Deliverable | Owner | Validation |
|-----|-------------|-------|------------|
| 1-2 | `skills/linkedin-browser-scrape/SKILL.md` - New skill | Dev | Passes validation |
| 3 | Update `fetch_linkedin_posts.py` with browser fallback | Dev | Fallback triggers on API failure |
| 4 | Update `tools/get-post-reactors.py` to use browser | Dev | Returns reactor list |
| 5 | **MILESTONE 2 GATE:** Browser fallback working in test | QA | 3 successful scrapes |

### Deliverables Checklist

- [ ] `lib/browser_automation.py` - MH1BrowserClient class
- [ ] `lib/browser_rate_limiter.py` - Platform rate limits
- [ ] `skills/linkedin-browser-scrape/SKILL.md` - New skill
- [ ] Updated `tools/fetch_linkedin_posts.py` with fallback
- [ ] Profile directory at `~/.mh1/profiles/linkedin/`

---

## Stream C: Web UI Foundation (Week 3-6)

**Goal:** Marketers can view task progress and content

**Prerequisite:** Stream A complete (needs validated skill format)

### Week 3-4: Scaffolding

| Day | Deliverable | Owner | Validation |
|-----|-------------|-------|------------|
| W3D1-2 | Next.js 15 app scaffold in `ui/` | Dev | `npm run dev` works |
| W3D3 | shadcn/ui components installed | Dev | Components render |
| W3D4-5 | Firebase Firestore connection | Dev | Read/write works |
| W4D1-2 | Task list component | Dev | Shows mock tasks |
| W4D3 | Task detail view with logs | Dev | Logs display |
| W4D4-5 | SSE endpoint for real-time progress | Dev | Updates stream live |

### Week 5: Content Management

| Day | Deliverable | Owner | Validation |
|-----|-------------|-------|------------|
| 1-2 | Content library view | Dev | Shows generated content |
| 3 | Approval workflow (draft→review→approved) | Dev | Status transitions work |
| 4 | Client selector dropdown | Dev | Filters by client |
| 5 | **MILESTONE 3 GATE:** End-to-end task visibility | QA | Create task, see in UI |

### Week 6: Polish

| Day | Deliverable | Owner | Validation |
|-----|-------------|-------|------------|
| 1-2 | Basic analytics dashboard | Dev | Shows task counts, costs |
| 3 | Notification integration (Slack webhook) | Dev | Notifications fire |
| 4 | Mobile responsiveness | Dev | Works on phone |
| 5 | **FINAL GATE:** Production deploy | QA | UI live and stable |

### Deliverables Checklist

- [ ] `ui/` - Next.js 15 app directory
- [ ] Task dashboard with real-time updates
- [ ] Content library with approval workflow
- [ ] Client selector
- [ ] Basic analytics
- [ ] Slack integration

---

## Stream D: Ecosystem Publishing (Week 5-6)

**Goal:** 5 open-source skills published to skills.sh

**Prerequisite:** Stream A complete (skills in new format)

### Week 5: Preparation

| Day | Deliverable | Owner | Validation |
|-----|-------------|-------|------------|
| 1 | Create `mh1-hq/public-skills` GitHub repo | Dev | Repo exists |
| 2 | Select and sanitize 5 skills for open source | Dev | No proprietary code |
| 3 | Strip MH1-specific metadata from public versions | Dev | Clean SKILL.md files |
| 4 | Add MIT licenses and READMEs | Dev | License in each skill |
| 5 | Test installation via `npx skills add` | Dev | Skills install correctly |

### Week 6: Launch

| Day | Deliverable | Owner | Validation |
|-----|-------------|-------|------------|
| 1 | Submit to skills.sh registry | Dev | Listed on site |
| 2 | Create documentation/examples | Dev | README complete |
| 3 | Write announcement blog post | Marketing | Draft complete |
| 4-5 | Monitor installs, fix issues | Dev | No critical bugs |

### Skills to Publish

| Skill | License | Why Open |
|-------|---------|----------|
| `extract-pov` | MIT | Generic utility |
| `research-company` | MIT | Basic research |
| `research-competitors` | MIT | Basic research |
| `generate-interview-questions` | MIT | Widely useful |
| `extract-writing-guideline` | MIT | Generic utility |

### Deliverables Checklist

- [ ] `mh1-hq/public-skills` GitHub repo
- [ ] 5 MIT-licensed skills
- [ ] skills.sh registry listing
- [ ] Announcement/documentation

---

## Validation Schema

### Milestone 1: Skill Format Complete (End of Week 2)

```yaml
gate: skill_format_complete
criteria:
  - all_skills_pass_validation: true
  - trigger_phrases_added: true
  - template_updated: true
  - migration_report_generated: true
validation_command: |
  python scripts/validate_skill.py --all
  # Expected: 25/25 skills pass
```

### Milestone 2: Browser Integration Complete (End of Week 3)

```yaml
gate: browser_integration_complete
criteria:
  - wrapper_tests_pass: true
  - skill_validated: true
  - fallback_tested: true
  - rate_limiting_verified: true
validation_command: |
  python -m pytest lib/test_browser_automation.py
  python scripts/validate_skill.py skills/linkedin-browser-scrape
```

### Milestone 3: UI MVP Complete (End of Week 5)

```yaml
gate: ui_mvp_complete
criteria:
  - task_list_renders: true
  - real_time_updates_work: true
  - content_library_functional: true
  - approval_workflow_works: true
validation_command: |
  cd ui && npm run test
  # Manual: create task via CLI, verify appears in UI
```

### Final Gate: Production Ready (End of Week 6)

```yaml
gate: production_ready
criteria:
  - all_milestones_passed: true
  - no_critical_bugs: true
  - documentation_complete: true
  - public_skills_published: true
```

---

## Resource Allocation

### Parallel Execution Map

```
        Week 1    Week 2    Week 3    Week 4    Week 5    Week 6
Dev 1:  [Stream A───────────][Stream C────────────────────────────]
Dev 2:            [Stream B───────────][Stream D──────────────────]
QA:     [        ][M1 Gate ][M2 Gate ][        ][M3 Gate ][Final ]
```

### Estimated Hours

| Stream | Hours | Critical Path? |
|--------|-------|----------------|
| A: Skill Format | 40h | YES |
| B: Browser | 30h | No |
| C: UI | 60h | YES (after A) |
| D: Publishing | 20h | No |
| **Total** | **150h** | |

---

## Risk Mitigation

| Risk | Mitigation | Trigger |
|------|------------|---------|
| Skill migration breaks existing workflows | Keep backup of original files, run regression tests | Any skill fails after migration |
| Browser gets blocked by LinkedIn | Use Kernel stealth mode, reduce scrape frequency | 3+ blocks in 24h |
| UI scope creep | Strict MVP features only, defer requests to Phase 2 | Any feature request outside spec |
| Publishing delays ecosystem work | Can launch internally without publishing | Milestone 3 complete |

---

## Quick Reference: Key Files

### New Files to Create

```
schemas/
  skill-frontmatter.json          # YAML validation schema

scripts/
  validate_skill.py               # Batch validation

lib/
  browser_automation.py           # MH1BrowserClient
  browser_rate_limiter.py         # Platform limits

skills/
  linkedin-browser-scrape/
    SKILL.md                      # New browser scrape skill

ui/
  app/                            # Next.js pages
  components/                     # shadcn/ui components
  lib/                            # Firebase, SSE utils

docs/
  skill-migration-report.md       # Migration documentation
```

### Files to Modify

```
skills/_templates/SKILL_TEMPLATE/SKILL.md   # Add YAML frontmatter
skills/*/SKILL.md                           # All 25 skills
tools/fetch_linkedin_posts.py               # Add browser fallback
```

---

## Commands to Run

### Setup (Day 1)

```bash
# Set up Python virtual environment (required)
cd /Users/jflo7006/Downloads/Marketerhire/mh1-hq
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install agent-browser
npm install -g agent-browser
agent-browser install

# Create profile directories
mkdir -p ~/.mh1/profiles/linkedin
mkdir -p ~/.mh1/profiles/twitter

# Initialize UI
cd ui
npx create-next-app@latest . --typescript --tailwind --app
npx shadcn@latest init
```

### Validation (Throughout)

```bash
# Validate all skills
python scripts/validate_skill.py --all

# Validate single skill
python scripts/validate_skill.py skills/ghostwrite-content

# Test browser wrapper
python -m pytest lib/test_browser_automation.py

# Run UI tests
cd ui && npm run test
```

### Publishing (Week 5-6)

```bash
# Test skill installation
npx skills add ./public-skills --list
npx skills add ./public-skills -s extract-pov -a cursor

# Submit to registry
# (Manual via skills.sh interface)
```

---

## Success Criteria

### Week 2 Checkpoint
- [ ] All 25 skills pass YAML frontmatter validation
- [ ] Each skill has 3+ trigger phrases
- [ ] Migration report complete

### Week 3 Checkpoint  
- [ ] Browser wrapper tests passing
- [ ] LinkedIn scrape skill created
- [ ] Fallback logic integrated

### Week 5 Checkpoint
- [ ] UI shows real-time task progress
- [ ] Content approval workflow functional
- [ ] Client selector working

### Week 6 Final
- [ ] 5 skills published to skills.sh
- [ ] UI deployed to production
- [ ] All documentation complete

---

## Next Steps

1. **Today:** Create `schemas/skill-frontmatter.json` and `scripts/validate_skill.py`
2. **This week:** Migrate top 5 skills, update template
3. **Parallel:** Start browser wrapper setup

Ready to begin?
