# Vercel Labs Integration Strategy for MH1

**Date:** January 27, 2026  
**Status:** Approved for Implementation

---

## Executive Summary

After analyzing four Vercel Labs repositories, we've identified strategic opportunities to **accelerate MH1's capabilities** while maintaining our unique marketing-focused value proposition.

**Bottom Line:** MH1 is already more sophisticated than Vercel's offerings for marketing operations. We should adopt their **UX patterns and tooling standards** while preserving our **domain-specific intelligence**.

---

## Strategic Verdict by Repository

| Repository | Verdict | Why |
|------------|---------|-----|
| **agent-skills** | ADOPT FORMAT | Their YAML frontmatter is becoming the industry standard |
| **agent-browser** | ADD AS FALLBACK | Complements our API-first approach for edge cases |
| **skills CLI** | PUBLISH TO ECOSYSTEM | Position MH1 as the marketing skills authority |
| **coding-agent-template** | ADOPT UI PATTERNS | Marketers need visibility; their UX is excellent |


---

## Priority 1: Skill Format Migration

### What We're Doing
Migrating all 25+ skills to the AgentSkills.io YAML frontmatter standard.

### Why It Matters
- Compatible with 33+ AI agents (Cursor, Claude Code, Codex, etc.)
- Enables `npx skills add mh1-hq/public-skills`
- Natural language skill discovery ("write LinkedIn posts" → ghostwrite-content)

### New Hybrid Format

```yaml
---
name: ghostwrite-content
description: Generate LinkedIn posts in founder's voice. Use when asked to "write posts", "ghostwrite", "create content calendar".
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
- Weekly scheduled content generation
- Ad-hoc post creation from signals

## Pipeline
[MH1's detailed stages - our competitive advantage]
```

### What MH1 Has That Vercel Doesn't
| MH1 Advantage | Value |
|---------------|-------|
| SLAs (runtime, cost) | Operational guarantees |
| Stage pipelines | Quality gates between steps |
| Context handling | Token management strategies |
| Dependency declarations | MCP, agent, skill requirements |
| Output schemas | Structured, validated outputs |

---

## Priority 2: Browser Automation Enhancement

### What We're Doing
Adding `agent-browser` as a **fallback layer** for when APIs fail or are insufficient.

### Architecture Decision

```
API Layer (Primary)        Browser Layer (Fallback)
────────────────────       ────────────────────────
Crustdata (LinkedIn)  ──▶  agent-browser + Kernel (stealth)
Twitter API           ──▶  agent-browser (authenticated only)
PRAW (Reddit)         ──▶  [not needed - API excellent]
Firecrawl             ──▶  agent-browser (JS-heavy sites)
```

### Key Use Cases
1. **LinkedIn reactor lists** - Not available via API
2. **Full LinkedIn profiles** - API returns limited fields
3. **Competitor JS-heavy sites** - Firecrawl can't render
4. **Premium tier scraping** - Authenticated content for high-value clients

### Implementation
```bash
npm install -g agent-browser
agent-browser install
```

Then create `lib/browser_automation.py` wrapper and `skills/linkedin-browser-scrape/`.

---

## Priority 3: Skills Ecosystem Publishing

### Strategy: Establish MH1 as Marketing Skills Authority

The skills.sh ecosystem has **40K+ installs** on basic marketing skills, but they're simplistic compared to MH1's enterprise capabilities.

### Publication Plan

| Publish (Open Source) | Keep Proprietary |
|-----------------------|------------------|
| `extract-pov` | `ghostwrite-content` |
| `extract-writing-guideline` | `lifecycle-audit` |
| `research-company` | `social-listening-collect` |
| `generate-interview-questions` | `extract-founder-voice` |
| `research-competitors` | Full pipeline skills |

### Why Publish?
- **Community building** - Establishes MH1 as experts
- **Lead generation** - Users discover MH1 through free skills
- **Ecosystem influence** - Shape marketing skill standards
- **Talent attraction** - Developers see our quality

### CLI Strategy
```bash
# Use their CLI for external skills
npx skills add coreyhaines31/marketingskills

# Build MH1 wrapper for proprietary features
mh1 skills list              # Show available skills
mh1 skills install <name>    # Install with client scoping
mh1 skills validate <name>   # Check MCP deps, schemas
```

---

## Priority 4: Web UI for Marketers

### What We're Doing
Building a minimal web UI so marketers can see task progress, review content, and approve outputs.

### Why It Matters
| Factor | CLI-Only | With Web UI |
|--------|----------|-------------|
| Marketer accessibility | ★☆☆☆☆ | ★★★★★ |
| Content review | ★★☆☆☆ | ★★★★★ |
| Client demos | ★☆☆☆☆ | ★★★★★ |
| Real-time collaboration | ★★☆☆☆ | ★★★★★ |

### Phased Approach

**Phase 1 (2-3 weeks):** Basic task visibility
- Task dashboard (active/completed)
- Real-time progress (SSE streaming)
- Content preview

**Phase 2 (2-3 weeks):** Content management
- Content library
- Approval workflow (draft → review → approved)
- Client selector

**Phase 3 (2-3 weeks):** Campaign management
- Content calendar
- Analytics dashboard
- Slack notifications

**Phase 4 (3-4 weeks):** Self-service
- Task creation wizard for marketers
- Template library

### Tech Stack
- Next.js 15 + shadcn/ui (import from Vercel template)
- Firebase Firestore for real-time sync
- Keep Python backend for task execution

---

## What NOT to Adopt

| Component | Reason |
|-----------|--------|
| **Vercel Sandbox** | Overkill for content generation; no untrusted code execution |
| **Repository-centric model** | Replace with client-centric workflows |
| **PostgreSQL migration** | Keep Firebase + SQLite hybrid; it works well |
| **Their marketing skills** | Ours are significantly more sophisticated |

---

## Implementation Roadmap

### Week 1-2: Skill Format Migration
- [ ] Create `schemas/skill-frontmatter.json` validation schema
- [ ] Update `SKILL_TEMPLATE` with hybrid format
- [ ] Migrate top 5 skills to new format
- [ ] Add "When to Use" sections with trigger phrases

### Week 3-4: Full Migration + Publishing
- [ ] Migrate all 25+ skills
- [ ] Create `mh1-hq/public-skills` repo
- [ ] Publish 5 open-source skills to skills.sh
- [ ] Test installation via `npx skills add`

### Week 5-6: Browser Integration
- [ ] Install agent-browser
- [ ] Create `lib/browser_automation.py`
- [ ] Build `skills/linkedin-browser-scrape/`
- [ ] Add fallback logic to `fetch_linkedin_posts.py`
- [ ] Evaluate Kernel provider for stealth mode

### Week 7-8: Web UI Foundation
- [ ] Initialize Next.js app with shadcn/ui
- [ ] Build task list/dashboard component
- [ ] Implement SSE progress streaming
- [ ] Add Firebase Firestore mirroring

### Week 9-10: Content Management UI
- [ ] Build content library
- [ ] Implement approval workflow
- [ ] Add client selector
- [ ] Create basic analytics

---

## Key Metrics to Track

### After Implementation
| Metric | Current | Target |
|--------|---------|--------|
| Skill discoverability | Manual lookup | Natural language |
| API failure recovery | None | Browser fallback |
| Task visibility for marketers | 0% | 100% |
| Content approval time | Email-based | In-app workflow |
| Public skill installs | 0 | 10K+ (6 months) |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Format migration breaks skills | Low | Medium | Thorough testing, rollback plan |
| Browser automation gets blocked | Medium | Low | Use APIs as primary, Kernel stealth |
| UI increases maintenance burden | Medium | Medium | Start minimal, iterate |
| Open-source skills leak IP | Low | High | Clear proprietary/open boundaries |

---

## Conclusion

MH1 is already **ahead of Vercel's offerings** in marketing-specific capabilities. This integration strategy:

1. **Adopts industry standards** (skill format) for compatibility
2. **Fills gaps** (browser automation) for edge cases  
3. **Establishes authority** (ecosystem publishing) in marketing
4. **Improves UX** (web UI) for non-technical users

The result: MH1 becomes the **definitive marketing intelligence platform** that works with any AI agent while maintaining our competitive advantage in quality, reliability, and domain expertise.

---

## Detailed Reports

For full analysis of each repository:
- `delivery/vercel-skills-analysis-report.md` - agent-skills format analysis
- `knowledge/sources/agent-browser-analysis.md` - browser automation integration
- `docs/vercel-skills-cli-integration-report.md` - skills CLI strategy
- `knowledge/sources/vercel-coding-agent-analysis.md` - UI/task patterns

---

*Prepared by MH1 Analysis System*
