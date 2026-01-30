# Vercel Labs Agent-Skills Analysis Report

**Date:** 2026-01-27  
**Analyst:** MH1 System Analysis  
**Subject:** Integration potential of vercel-labs/agent-skills into MH1

---

## Executive Summary

The Vercel Labs agent-skills repository (17K+ stars) follows the emerging [AgentSkills.io](https://agentskills.io) open standard—an Anthropic-developed specification for portable AI agent capabilities. While their skills focus on frontend development (React, Next.js, web design), their **structural patterns and discovery mechanisms** offer valuable improvements for MH1's marketing-focused skill system.

**Bottom line:** MH1 should adopt the AgentSkills.io frontmatter standard for better tooling compatibility while preserving our operational rigor (SLAs, budgets, quality gates) as an MH1 extension.

---

## Part A: What to Adopt (Copy Their Approach)

### 1. Standardized YAML Frontmatter

**Current MH1 approach:**
```markdown
# Skill: social-listening-collect

Version: v1.0.0  
Status: active  
Author: MH1 Engineering  
Created: 2026-01-27  
```

**AgentSkills.io standard (Vercel uses):**
```yaml
---
name: social-listening-collect
description: Collect social posts matching client keywords, score for ICP relevance, and store to Firestore. Use when the user says "collect signals", "run social listening", or "find mentions".
license: MIT
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  created: "2026-01-27"
---
```

**Why adopt:**
- Enables compatibility with skills-ref validation tooling
- Makes skills portable across Claude Code, Cursor, Copilot
- Enables programmatic skill discovery and indexing
- `npx add-skill` ecosystem compatibility

**Recommendation:** Migrate all 25 SKILL.md files to use YAML frontmatter with AgentSkills.io required fields, plus MH1-specific metadata extensions.

---

### 2. Description-Driven Skill Activation

**Vercel pattern:** Embed trigger phrases directly in description:
```yaml
description: Review UI code for Web Interface Guidelines compliance. Use when asked to "review my UI", "check accessibility", "audit design", "review UX".
```

**MH1 current:** Skills are invoked explicitly via `/run-skill [name]` or imported directly.

**Why adopt:**
- Enables natural language skill activation ("help me write a LinkedIn post" → ghostwrite-content)
- Better for non-technical users (marketers)
- Aligns with agentic workflows where Claude chooses appropriate skill

**Recommendation:** Add trigger phrases to all skill descriptions:
```yaml
description: Generate LinkedIn posts in founder's voice from social signals. Use when asked to "write posts", "create content calendar", "ghostwrite for [founder]", or "generate LinkedIn content".
```

---

### 3. Progressive Disclosure Structure

**Vercel pattern:**
1. Frontmatter (~100 tokens) → loaded at startup for all skills
2. SKILL.md body (<5000 tokens) → loaded when skill activated
3. references/, scripts/ → loaded only when needed

**Key constraint:** Keep SKILL.md under 500 lines. Move detailed reference to separate files.

**MH1 current:** Some skills exceed 500 lines with comprehensive inline documentation.

**Files exceeding guideline:**
- `ghostwrite-content/SKILL.md` - 260 lines (good)
- `_templates/SKILL_TEMPLATE/SKILL.md` - 261 lines (good)
- `extract-founder-voice/SKILL.md` - 372 lines (at risk)

**Recommendation:** 
- Move detailed extraction rules to `references/extraction-rules.md`
- Move example JSON structures to `references/output-examples.md`
- Keep SKILL.md focused on: purpose, when to use, inputs/outputs, process overview

---

### 4. "When to Apply" Section

**Vercel pattern:** Explicit section with bullet points:
```markdown
## When to Apply

Reference these guidelines when:
- Writing new React components or Next.js pages
- Implementing data fetching (client or server-side)
- Reviewing code for performance issues
```

**Why adopt:** Clear activation criteria help both humans and agents understand when to use the skill.

**Recommendation:** Add `## When to Use` section to all skills immediately after Purpose.

---

### 5. Rule Categorization by Priority/Impact

**Vercel pattern:** Rules organized by impact level:
```markdown
| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Eliminating Waterfalls | CRITICAL | `async-` |
| 2 | Bundle Size Optimization | CRITICAL | `bundle-` |
| 3 | Server-Side Performance | HIGH | `server-` |
```

**Marketing application:** Could apply to content guidelines:
```markdown
| Priority | Category | Impact |
|----------|----------|--------|
| 1 | Voice Authenticity | CRITICAL |
| 2 | AI Tell Elimination | CRITICAL |
| 3 | Hook Strength | HIGH |
| 4 | CTA Clarity | MEDIUM |
```

**Recommendation:** Implement priority-based rule organization for QA/review skills.

---

## Part B: What to Import (Directly Use)

### Skills Analysis: Direct Applicability

| Skill | Relevance to MH1 | Recommendation |
|-------|------------------|----------------|
| `react-best-practices` | LOW - We don't build React apps | Skip |
| `react-native-guidelines` | LOW - No mobile development | Skip |
| `web-design-guidelines` | MEDIUM - Landing page reviews | Consider for future |
| `composition-patterns` | LOW - Code architecture | Skip |
| `vercel-deploy-claimable` | LOW - We use Firebase | Skip |

### web-design-guidelines: Partial Import

**Potential use case:** When MH1 reviews client landing pages or email designs.

**Interesting pattern:** This skill fetches rules from an external URL at runtime:
```markdown
## Guidelines Source

Fetch fresh guidelines before each review:
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
```

**Why this matters:** We could apply the same pattern for:
- Fetching latest LinkedIn algorithm guidelines
- Fetching platform-specific content rules
- Keeping brand guidelines in a single source of truth

**Recommendation:** Create `marketing-platform-guidelines` skill using this pattern that fetches latest platform rules before content review.

---

### Valuable Patterns to Borrow (Not Whole Skills)

**1. External Rule Fetching:**
```markdown
## Guidelines Source
Fetch fresh guidelines before each review:
https://raw.githubusercontent.com/mh1-hq/marketing-rules/main/linkedin-2026.md
```

**2. Terse Output Format:**
```markdown
## Output Format
Output findings in the terse `file:line` format
```
Adapt to: `post-id:issue:severity` for content QA.

**3. Rule Prefix System:**
```markdown
- `voice-001` - Voice authenticity violation
- `hook-001` - Weak opening hook
- `cta-001` - Missing call to action
```

---

## Part C: What to Improve Upon (Take and Enhance)

### 1. Add Operational Metadata (MH1 Advantage)

Vercel skills are pure knowledge containers. MH1 skills need operational rigor.

**Preserve these MH1 extensions in metadata:**
```yaml
metadata:
  # AgentSkills.io standard
  author: mh1-engineering
  version: "1.0.0"
  
  # MH1 extensions
  status: active | deprecated | experimental
  created: "2026-01-27"
  updated: "2026-01-27"
  
  # Operational (unique to MH1)
  estimated_runtime: "10-15min"
  max_runtime: "25min"
  estimated_cost: "$0.50"
  max_cost: "$2.00"
  requires_human_review: false
  client_facing: true
```

**Recommendation:** Keep operational metadata but move it into YAML `metadata` block for consistency.

---

### 2. Stage Pipeline Notation (MH1 Advantage)

Vercel skills are stateless. MH1 workflows have stages with quality gates.

**Keep MH1 pattern but standardize:**
```markdown
## Pipeline

| Stage | Name | Duration | Quality Gate |
|-------|------|----------|--------------|
| 0 | ID Resolution | instant | CLIENT_ID resolved |
| 1 | Context Loading | 2-3min | 5+ source posts loaded |
| 2 | Topic Curation | 3-5min | Topics selected |
| 3 | Ghostwriting | 5-10min | Posts generated |
| 4 | QA Review | 2-3min | Zero critical violations |
| 5 | Output | 1min | Calendar compiled |

See `stages/*.md` for detailed stage instructions.
```

**This is a capability Vercel skills lack** and is valuable for complex marketing workflows.

---

### 3. Context Handling Strategy (MH1 Advantage)

Vercel doesn't address token limits. MH1 does.

**Preserve but standardize:**
```yaml
metadata:
  # ... other fields ...
  context_strategy: inline | chunked | offloaded
  max_input_tokens: 50000
```

Then document in body:
```markdown
## Context Handling

| Input Size | Strategy | Model |
|------------|----------|-------|
| < 8K tokens | Inline | claude-sonnet-4 |
| 8K-50K tokens | Chunked | Haiku chunks, Sonnet synthesis |
| > 50K tokens | ContextManager | Haiku chunks, Sonnet synthesis |
```

---

### 4. Enhanced Dependency Declaration

**Vercel pattern:** Minimal dependencies (scripts referenced by path)

**MH1 enhancement:** Explicit dependency types
```markdown
## Dependencies

| Type | Name | Purpose |
|------|------|---------|
| Skill | linkedin-keyword-search | Platform scraping |
| Agent | linkedin-ghostwriter | Content generation |
| MCP | user-hubspot | CRM data access |
| API | Crustdata | LinkedIn search |
| Script | preload_context.py | Context loading |
```

This is more rigorous than Vercel's approach and should be preserved.

---

## Part D: Specific Recommendations

### D1. Should We Change Our Skill Structure?

**Yes, partially.** Adopt AgentSkills.io frontmatter standard, preserve MH1 operational extensions.

**New hybrid structure:**
```markdown
---
name: skill-name
description: What it does. Use when [trigger phrases].
license: MIT
compatibility: Requires Firebase MCP, HubSpot MCP
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  created: "2026-01-27"
  estimated_runtime: "10min"
  client_facing: true
allowed-tools: Read Write Shell CallMcpTool
---

# Skill Name

## When to Use
- Bullet points of activation scenarios

## Inputs
| Name | Type | Required | Description |

## Outputs
| Name | Type | Description |

## Pipeline (if multi-stage)
| Stage | Name | Gate |

## Process
1. Step 1
2. Step 2

## Quality Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Dependencies
| Type | Name | Purpose |

## References
- See `references/detailed-rules.md` for extended guidelines
- See `scripts/` for automation scripts
```

---

### D2. Are There Frontmatter Fields We're Missing?

**Yes. Add these:**

| Field | Purpose | Example |
|-------|---------|---------|
| `description` | Activation triggers | "Use when asked to 'write posts'" |
| `license` | IP clarity | "MIT" or "Proprietary" |
| `compatibility` | Requirements | "Requires Firebase MCP" |
| `allowed-tools` | Tool pre-approval | "Read Write CallMcpTool" |

**Remove these from body, move to metadata:**
- Version (→ `metadata.version`)
- Status (→ `metadata.status`)
- Author (→ `metadata.author`)
- Created/Updated dates (→ `metadata.created`, `metadata.updated`)

---

### D3. How Does Their Skill Discovery Work vs Ours?

| Aspect | Vercel/AgentSkills.io | MH1 Current |
|--------|----------------------|-------------|
| **Discovery** | Description scanning at startup | Listed in available_skills section |
| **Activation** | Automatic via description matching | Explicit /run-skill command |
| **Loading** | Progressive (frontmatter → body → files) | Full file on activation |
| **Install** | `npx add-skill repo/skill` | Manual copy to skills/ |

**Recommendation:** 

1. **Short-term:** Add description-based triggers to current skills
2. **Medium-term:** Implement progressive loading (frontmatter index)
3. **Long-term:** Consider compatibility with `npx add-skill` ecosystem

---

## Action Items

### Immediate (This Week)
- [ ] Create `schemas/skill-frontmatter.json` with AgentSkills.io + MH1 extensions
- [ ] Update SKILL_TEMPLATE with new hybrid format
- [ ] Add `description` with trigger phrases to top 5 most-used skills

### Short-term (2 Weeks)
- [ ] Migrate all 25 skills to new frontmatter format
- [ ] Add "When to Use" sections to all skills
- [ ] Move detailed documentation to `references/` for large skills

### Medium-term (1 Month)
- [ ] Implement skill discovery based on description matching
- [ ] Create marketing-platform-guidelines skill with external fetch pattern
- [ ] Add priority-based rule categorization to QA skills

### Optional/Future
- [ ] Evaluate `npx add-skill` ecosystem publishing
- [ ] Consider public skill registry for marketing-specific skills

---

## Appendix: Side-by-Side Comparison

### Vercel react-best-practices
```yaml
---
name: vercel-react-best-practices
description: React and Next.js performance optimization guidelines. Triggers on tasks involving React components, data fetching, bundle optimization.
license: MIT
metadata:
  author: vercel
  version: "1.0.0"
---
```
- 57 rules across 8 categories
- Priority-based organization
- References external rule files
- ~200 lines main file

### MH1 ghostwrite-content
```markdown
# Ghostwrite Content Skill
Version: v1.0.0 (mh1-hq)
```
- 7-stage pipeline
- Quality gates between stages
- Budget/cost tracking
- Firebase integration
- ~260 lines main file

### Proposed MH1 Hybrid
```yaml
---
name: ghostwrite-content
description: Generate LinkedIn posts in founder's voice from social signals. Use when asked to "write posts", "ghostwrite", "create content calendar".
license: Proprietary
compatibility: Requires Firebase MCP, HubSpot MCP
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  estimated_runtime: "15-25min"
  max_cost: "$2.00"
  client_facing: true
allowed-tools: Read Write Shell CallMcpTool
---

# Ghostwrite Content

## When to Use
- Client requests LinkedIn content calendar
- Scheduled weekly content generation
- Ad-hoc post creation from signals

## Pipeline
| Stage | Name | Duration | Gate |
|-------|------|----------|------|
| 0 | ID Resolution | instant | CLIENT_ID resolved |
...

## Dependencies
| Type | Name | Purpose |
|------|------|---------|
| Agent | linkedin-ghostwriter | Generation |
...

## References
- `stages/*.md` - Detailed stage instructions
- `templates/*.md` - Output templates
```

---

## Conclusion

The Vercel/AgentSkills.io approach prioritizes **portability and discovery** while MH1's approach prioritizes **operational reliability**. The optimal path forward is a hybrid: adopt the AgentSkills.io frontmatter standard for ecosystem compatibility while preserving MH1's operational rigor as metadata extensions.

This positions MH1 skills to:
1. Work with emerging agent skill ecosystems
2. Enable natural language activation for non-technical users
3. Maintain the operational guarantees marketing workflows require
4. Potentially publish marketing-specific skills publicly in the future
