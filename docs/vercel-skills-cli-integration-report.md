# Vercel Labs Skills CLI Integration Report

**Date:** January 27, 2026  
**Prepared for:** MH1 Marketing Intelligence System  
**Repository Analyzed:** https://github.com/vercel-labs/skills

---

## Executive Summary

The Vercel Labs skills CLI (`npx skills`) has emerged as the de facto standard for agent skill management, with **2,766 stars**, support for **33+ AI agents**, and a **public skill registry** at skills.sh with 29,000+ total skill installations tracked.

**Key Finding:** MH1 should adopt the open Agent Skills format for compatibility while building marketing-specific extensions. The ecosystem already has marketing skills (coreyhaines31/marketingskills with 40K+ installs), but they're basic compared to MH1's enterprise capabilities.

**Recommendation:** Hybrid approach — use `npx skills` for generic skill management while maintaining proprietary extensions for MH1's advanced marketing workflows.

---

## Part A: What to Adopt

### 1. Skill Discovery/Search Patterns

**Their Approach:**
```bash
# Interactive fuzzy search
npx skills find

# Keyword search
npx skills find typescript

# List skills in any repo
npx skills add owner/repo --list
```

**Adoption Recommendation:** ✅ Adopt

The discovery pattern is elegant and well-designed:
- GitHub-native (any repo can be a skill source)
- Supports multiple source formats (shorthand, URL, local path)
- Interactive selection with fuzzy search

**For MH1:**
Create `commands/find-skill.md`:
```bash
# Find skills globally
npx skills find marketing

# List MH1 skills
npx skills add mh1-hq/skills --list
```

### 2. Version Management Approach

**Their Approach:**
```bash
npx skills check      # Check for updates
npx skills update     # Update all skills
npx skills generate-lock  # Track skill sources
```

**Adoption Recommendation:** ✅ Adopt

- Lock file tracks source repos for each installed skill
- Version management via git (skills are git repos)
- No complex versioning scheme — just `git pull`

**Gap for MH1:** No semantic versioning. MH1's `v1.0.0` in SKILL.md isn't enforced.

### 3. Multi-Agent Compatibility Format

**Their Approach:**

| Agent | Project Path | Global Path |
|-------|--------------|-------------|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Cursor | `.cursor/skills/` | `~/.cursor/skills/` |
| Codex | `.codex/skills/` | `~/.codex/skills/` |
| 30+ more... | varies | varies |

**Installation Methods:**
1. **Symlink (recommended)** — single source of truth
2. **Copy** — independent copies per agent

**Adoption Recommendation:** ✅ Adopt

MH1 currently uses `skills/` at repo root. This is compatible with the ecosystem (Moltbot uses this pattern). However, we should also support `.cursor/skills/` for Cursor users.

---

## Part B: What to Import

### 1. Should MH1 be Compatible with Their Skill Format?

**Their SKILL.md Format (minimal):**
```yaml
---
name: skill-name
description: What this skill does and when to use it.
---

# Instructions for the agent
```

**MH1's Current Format (extensive):**
```yaml
# Skill: [SKILL_NAME]
Version: v1.0.0
Status: active | deprecated | experimental
Author: [name]
---
## Purpose
## Inputs (with schema)
## Data Requirements
## Outputs (with schema)
## SLA (Service Level Agreement)
## Failure Modes
## Human Review Triggers
## Dependencies
## Context Handling
## Process
## Quality Criteria
...
```

**Compatibility Analysis:**

| Aspect | Vercel Format | MH1 Format | Compatible? |
|--------|---------------|------------|-------------|
| File name | `SKILL.md` | `SKILL.md` | ✅ Yes |
| Required fields | `name`, `description` | Many required | ⚠️ Partial |
| Frontmatter | YAML | Markdown headers | ❌ No |
| Body content | Free-form | Structured sections | ✅ Yes |

**Recommendation:** Create adapter format

MH1 skills should have **two representations**:
1. `SKILL.md` — Open format for external compatibility
2. `SKILL-INTERNAL.md` — MH1's extended format with schemas, SLAs, etc.

Or use a single file with **optional MH1 extensions**:
```yaml
---
name: ghostwrite-content
description: Generate LinkedIn posts in founder's voice using social signals.
license: Proprietary
compatibility: Requires MH1 system with Firebase, HubSpot MCP
metadata:
  author: mh1
  version: "1.0.0"
  mh1-extended: true
  sla-runtime: 120s
  sla-cost: $2.00
---

# Ghostwrite Content
[Standard instructions here...]

## MH1 Extensions
[Extended metadata for MH1 system...]
```

### 2. Should We Publish MH1 Skills to Their Ecosystem?

**Current Marketing Skills in Ecosystem:**

| Skill | Author | Installs | Capability |
|-------|--------|----------|------------|
| seo-audit | coreyhaines31 | 5.9K | Basic SEO analysis |
| copywriting | coreyhaines31 | 4.5K | Copy guidelines |
| marketing-psychology | coreyhaines31 | 3.5K | Persuasion principles |
| email-sequence | coreyhaines31 | 2.1K | Email templates |
| social-content | coreyhaines31 | 2.6K | Social post templates |
| programmatic-seo | coreyhaines31 | 2.9K | pSEO strategy |

**MH1's Unique Capabilities (not in ecosystem):**

| MH1 Skill | Differentiator |
|-----------|----------------|
| `ghostwrite-content` | Multi-stage pipeline, founder voice modeling, Firebase integration |
| `social-listening-collect` | Real-time signal collection with scoring |
| `extract-founder-voice` | Voice contract extraction with pattern analysis |
| `lifecycle-audit` | Enterprise lifecycle marketing analysis |
| `icp-historical-analysis` | ICP evolution from CRM data |

**Recommendation:** Selective publishing

**Publish (open source):**
- `extract-pov` — Basic but useful
- `extract-writing-guideline` — Generic value
- `generate-interview-questions` — Widely applicable

**Keep proprietary:**
- `ghostwrite-content` — Core competitive advantage
- `lifecycle-audit` — Client-specific value
- `social-listening-collect` — MCP-dependent

### 3. Can We Use Their CLI for Skill Management?

**Yes, with caveats:**

```bash
# Install external skills to MH1 project
npx skills add coreyhaines31/marketingskills -a cursor

# Install MH1 skills globally
npx skills add mh1-hq/public-skills -g

# Create new skill with their template
npx skills init my-new-skill
```

**Limitations for MH1:**
1. **No MCP awareness** — Won't validate MCP dependencies
2. **No schema validation** — Won't check input.json/output.json
3. **No SLA tracking** — No cost/runtime budgets
4. **No internal routing** — Won't respect MH1's model routing config

**Recommendation:** Use `npx skills` for external skills, build MH1 wrapper for internal skills.

---

## Part C: What to Improve Upon

### 1. Marketing-Specific Skill Registry

**Current State:** skills.sh is generic (React, Expo, Supabase dominate)

**MH1 Opportunity:** Create `mh1.skills.sh` or contribute to categorization

**Proposed Categories for Marketing Skills:**

| Category | Example Skills |
|----------|----------------|
| **Voice & Positioning** | extract-founder-voice, extract-pov, brand-voice-audit |
| **Content Production** | ghostwrite-content, content-calendar, social-content |
| **Lifecycle Marketing** | lifecycle-audit, nurture-sequence, churn-prediction |
| **Research & Analysis** | research-company, research-competitors, icp-analysis |
| **Social Intelligence** | social-listening-collect, thought-leader-discover |
| **CRM Integration** | hubspot-sync, salesforce-sync, segment-audience |

**Implementation Path:**
1. Create `mh1-hq/marketing-skills` public repo
2. Contribute tagging system to skills.sh (PR)
3. Build category-filtered search: `npx skills find --category marketing`

### 2. Team/Organization Skill Sharing

**Current Limitation:** No organization-scoped skill management

**MH1 Requirement:** Client-specific skills with access control

**Proposed Architecture:**

```
mh1-hq/                           # Org root
├── skills/                       # Core MH1 skills (public/private)
├── clients/
│   └── {clientId}/
│       └── skills/               # Client-specific skills (private)
│           └── custom-voice/
│               └── SKILL.md
└── .mh1/
    └── skill-registry.json       # Org-level skill inventory
```

**skill-registry.json:**
```json
{
  "org_skills": ["ghostwrite-content", "lifecycle-audit"],
  "client_skills": {
    "client-abc": ["custom-voice-abc", "industry-jargon-abc"],
    "client-xyz": ["custom-templates-xyz"]
  },
  "external_skills": [
    {"source": "coreyhaines31/marketingskills", "skills": ["seo-audit"]}
  ]
}
```

**Features to Build:**
1. `mh1 skills list` — Show all available skills by scope
2. `mh1 skills install --client abc123` — Install to client scope
3. `mh1 skills share --from client-abc --to client-xyz` — Cross-client sharing
4. Permissions: org-admin, client-editor, viewer

---

## Part D: Strategic Questions

### 1. Should MH1 Skills be Installable via `npx skills add`?

**Answer: Yes, for public skills**

**Implementation:**
1. Create `mh1-hq/public-skills` repo with open-format skills
2. Add MH1 as discoverable source in ecosystem
3. Users can: `npx skills add mh1-hq/public-skills`

**For proprietary skills:**
- Keep in private repo
- Require MH1 auth for access
- Use custom CLI: `mh1 skills add ghostwrite-content --client abc`

### 2. Should We Create Our Own Skill Registry?

**Answer: Hybrid approach**

| Registry | Purpose | Skills |
|----------|---------|--------|
| skills.sh | Public discovery | Open-source marketing skills |
| mh1-internal | Client delivery | Proprietary skills, client-specific |
| Firebase | Runtime | Active skills for current client |

**Internal Registry Schema:**
```json
{
  "skill_id": "ghostwrite-content",
  "version": "1.0.0",
  "status": "production",
  "access": "org",
  "dependencies": {
    "mcps": ["firebase", "hubspot"],
    "agents": ["linkedin-ghostwriter", "linkedin-qa-reviewer"],
    "skills": ["extract-founder-voice"]
  },
  "telemetry": {
    "total_runs": 1247,
    "avg_cost": "$1.23",
    "avg_duration": "45s",
    "success_rate": 0.94
  }
}
```

### 3. How Do We Balance Openness vs Proprietary Skills?

**Framework:**

| Criterion | Open Source | Proprietary |
|-----------|-------------|-------------|
| Generic utility | ✅ | |
| No competitive advantage | ✅ | |
| Client-specific customization | | ✅ |
| MH1 system integration | | ✅ |
| Revenue-generating | | ✅ |
| Community building | ✅ | |

**Specific Decisions:**

| Skill | Decision | Rationale |
|-------|----------|-----------|
| extract-pov | Open | Generic, builds community |
| extract-founder-voice | Proprietary | Core differentiator |
| ghostwrite-content | Proprietary | Full pipeline value |
| research-company | Open | Basic utility |
| lifecycle-audit | Proprietary | Enterprise value |
| social-listening-collect | Proprietary | MCP-dependent, unique |

---

## Implementation Roadmap

### Phase 1: Format Compatibility (Week 1-2)

1. **Convert MH1 SKILL.md to hybrid format**
   - Add YAML frontmatter with `name`, `description`
   - Move extended metadata to `metadata.mh1.*`
   - Validate all 25+ skills

2. **Create skill adapter**
   - Script to convert MH1 format ↔ open format
   - Validate against Agent Skills spec

3. **Test with `npx skills`**
   - Verify MH1 skills discoverable
   - Test installation to Cursor

### Phase 2: Public Skills Release (Week 3-4)

1. **Create `mh1-hq/public-skills` repo**
   - 5-10 open-source marketing skills
   - MIT licensed
   - Register on skills.sh

2. **Contribute to ecosystem**
   - PR for marketing category on skills.sh
   - Documentation for marketing skill authors

### Phase 3: Internal Registry (Week 5-6)

1. **Build `mh1 skills` CLI**
   ```bash
   mh1 skills list              # Show available skills
   mh1 skills install <name>    # Install to project
   mh1 skills create <name>     # Create new skill
   mh1 skills validate <name>   # Check schema/deps
   ```

2. **Firebase integration**
   - Skill definitions in `skills/` collection
   - Runtime activation tracking
   - Usage telemetry

### Phase 4: Team Sharing (Week 7-8)

1. **Client-scoped skills**
   - Skills in `clients/{clientId}/skills/`
   - Access control in Firebase

2. **Cross-client sharing**
   - Skill templates (anonymized)
   - Permission workflows

---

## Appendix: Format Conversion Example

**Current MH1 format:**
```markdown
# Skill: extract-pov

Version: v1.0.0
Status: active
Author: mh1

---

## Purpose
Extract point of view and positioning from founder content.
```

**Converted to open format:**
```yaml
---
name: extract-pov
description: Extract point of view and positioning from founder content. Use when analyzing a founder's unique perspective, identifying key themes, or creating positioning statements.
license: MIT
metadata:
  author: mh1
  version: "1.0.0"
  mh1-extended: true
---

# Extract POV

[Full instructions...]

## MH1 Extensions

### Inputs
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `content` | string[] | yes | Array of founder content pieces |

### Output Schema
See `schemas/output.json`
```

---

## Conclusion

The Vercel Labs skills CLI represents the emerging standard for agent skill management. MH1 should:

1. **Adopt** their format for basic compatibility
2. **Extend** with MH1-specific metadata for enterprise features
3. **Publish** generic skills to build community
4. **Protect** proprietary skills that drive revenue
5. **Build** internal tooling for client-specific skill management

The agent skills ecosystem is maturing rapidly (30+ agents supported). Early adoption positions MH1 as a marketing skills leader while the category is still nascent.

---

## References

- [Vercel Skills CLI](https://github.com/vercel-labs/skills)
- [Agent Skills Specification](https://agentskills.io)
- [Skills Directory](https://skills.sh)
- [Anthropic Skills](https://github.com/anthropics/skills)
- [Marketing Skills](https://github.com/coreyhaines31/marketingskills)
