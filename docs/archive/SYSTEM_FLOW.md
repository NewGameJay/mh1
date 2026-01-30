# MH1 System Flow

> **The standardized self-operating system for MH1 client operations.**

This document defines the end-to-end workflow from client onboarding to content delivery.

---

## Quick Reference

| Phase | Trigger | Input | Output Location |
|-------|---------|-------|-----------------|
| 1. Onboard | `/onboard-client` | MRD or company info | Firebase: `clients/{clientId}/` |
| 2. Discover | `/discovery` | Client ID | Firebase: `clients/{clientId}/context/` |
| 3. Configure | `/configure-signals` | Discovery results | Firebase: `clients/{clientId}/modules/` |
| 4. Collect | `/collect-signals` | Signal sources | Firebase: `clients/{clientId}/signals/` |
| 5. Curate | `/curate-briefs` | Signals | Firebase: `clients/{clientId}/modules/linkedin-ghostwriter/assignment-briefs/` |
| 6. Create | `/ghostwrite` | Briefs | Firebase: `clients/{clientId}/modules/linkedin-ghostwriter/posts/` |
| 7. Deliver | `/sync-notion` | Posts | Notion + Firebase (status update) |

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MH1 SYSTEM FLOW                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐              │
│   │   MRD   │────▶│ ONBOARD │────▶│DISCOVER │────▶│CONFIGURE│              │
│   │ (input) │     │         │     │         │     │         │              │
│   └─────────┘     └────┬────┘     └────┬────┘     └────┬────┘              │
│                        │               │               │                    │
│                        ▼               ▼               ▼                    │
│                   ┌─────────────────────────────────────────┐               │
│                   │              FIREBASE                    │               │
│                   │   clients/{clientId}/                    │               │
│                   │   ├── metadata/                          │               │
│                   │   ├── context/     ◀─── Discovery        │               │
│                   │   ├── founders/                          │               │
│                   │   ├── signals/     ◀─── Collection       │               │
│                   │   └── modules/                           │               │
│                   │       └── linkedin-ghostwriter/          │               │
│                   │           ├── assignment-briefs/ ◀─ Curation            │
│                   │           └── posts/            ◀─ Creation             │
│                   └─────────────────────────────────────────┘               │
│                        │               │               │                    │
│                        ▼               ▼               ▼                    │
│   ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐              │
│   │ COLLECT │────▶│ CURATE  │────▶│ CREATE  │────▶│ DELIVER │              │
│   │ signals │     │ briefs  │     │ posts   │     │ notion  │              │
│   └─────────┘     └─────────┘     └─────────┘     └─────────┘              │
│                                                        │                    │
│                                                        ▼                    │
│                                                   ┌─────────┐               │
│                                                   │ NOTION  │               │
│                                                   │Dashboard│               │
│                                                   └─────────┘               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Memory Model

### What Goes INTO Firebase (Write)

| Data Type | Path | When Written | By What |
|-----------|------|--------------|---------|
| Client metadata | `clients/{id}/metadata` | Onboarding | `onboard-client` |
| Company profile | `clients/{id}/context/company-profile` | Discovery | `research-company` skill |
| Founder profiles | `clients/{id}/founders/{founderId}` | Discovery | `research-founder` skill |
| Voice contracts | `clients/{id}/founders/{id}/voiceContract` | Post-interview | `incorporate-interview` skill |
| Competitors | `clients/{id}/competitors/` | Discovery | `research-competitors` skill |
| Signals | `clients/{id}/signals/` | Collection | Signal collection skills |
| Briefs | `clients/{id}/modules/.../assignment-briefs/` | Curation | `create-assignment-brief` skill |
| Posts | `clients/{id}/modules/.../posts/` | Creation | `ghostwrite-content` skill |
| Evaluations | `clients/{id}/evaluations/` | QA | Evaluation pipeline |

### What Gets PULLED from Firebase (Read)

| Data Type | Path | When Read | By What |
|-----------|------|-----------|---------|
| Active client context | `clients/{id}/*` | Every operation | Client selector |
| Voice contract | `clients/{id}/founders/{id}/voiceContract` | Content creation | Ghostwriter |
| Unused signals | `clients/{id}/signals/` (status=unused) | Brief curation | Brief creator |
| Ready briefs | `clients/{id}/.../assignment-briefs/` (status=ready) | Content creation | Ghostwriter |
| Approved posts | `clients/{id}/.../posts/` (status=approved) | Notion sync | Sync tool |

### Local Files (NOT Client Data)

| Type | Location | Purpose |
|------|----------|---------|
| Skills | `skills/` | Skill definitions (production) |
| Skills (new) | `skills-staging/` | Awaiting review |
| Agents | `agents/` | Agent prompts |
| Commands | `commands/` | Command definitions |
| Templates | `templates/` | Content templates |
| Config | `config/` | System configuration |
| Prompts | `prompts/` | Reusable prompts |

---

## Phase 1: Onboarding

### Trigger
```
/onboard-client --displayName "Company Name" --website "https://example.com"
```

### Or from MRD
```
Read `prompts/skill-development-from-mrd.md` and execute onboarding workflow.
Target MRD: `.cursor/modules/MRDs/{mrd-file}.html`
```

### Steps

1. **Parse input** - Extract company info from MRD or arguments
2. **Create client** - `clients/{clientId}/` in Firebase
3. **Initialize modules** - Create module placeholders
4. **Set active client** - Write to `inputs/active_client.md`

### Skills Executed
- `client-onboarding` (orchestrator)

### Output
```
Firebase: clients/{clientId}/
├── metadata (name, website, status, createdAt)
└── modules/
    ├── linkedin-ghostwriter/
    ├── leads-database/
    └── signals/
```

---

## Phase 2: Discovery

### Trigger
```
/discovery {clientId}
```

### Steps

1. **Research company** - Website, products, market
2. **Research competitors** - 3-5 competitors
3. **Research founders** - Background, style
4. **Generate interview questions** - For kickoff call

### Skills Executed
- `research-company`
- `research-competitors`
- `research-founder` (per founder)
- `generate-interview-questions`

### Output
```
Firebase: clients/{clientId}/
├── context/
│   ├── company-profile
│   └── audience-personas
├── competitors/
│   └── {competitorId}/
├── founders/
│   └── {founderId}/
└── outputs/
    └── interview-questions
```

---

## Phase 3: Configure

### Trigger
```
/configure-signals {clientId}
```

### Steps

1. **Extract keywords** - From discovery research
2. **Identify thought leaders** - Industry experts to monitor
3. **Configure RSS feeds** - Industry publications
4. **Set up Notion** - Create dashboards, get DB IDs

### Skills Executed
- `extract-pov`
- `extract-audience-persona`

### Output
```
Firebase: clients/{clientId}/modules/
├── signals/
│   └── settings (keywords, thought leaders, RSS)
├── linkedin-ghostwriter/
│   └── notionDatabaseId
└── leads-database/
    └── notionDatabaseId
```

---

## Phase 4: Collect Signals

### Trigger
```
/collect-signals {clientId}
```

### Steps

1. **Fetch from sources** - Twitter, LinkedIn, Reddit, RSS
2. **Score signals** - Relevance, freshness, engagement
3. **Store qualified** - Score ≥ 60 to Firebase
4. **Dedupe** - By URL

### Skills Executed
- `twitter-keyword-search`
- `linkedin-keyword-search`
- `reddit-keyword-search`
- `social-listening-collect`

### Output
```
Firebase: clients/{clientId}/signals/
└── {signalId}/
    ├── url
    ├── content
    ├── author
    ├── score
    ├── status: "unused"
    └── collectedAt
```

---

## Phase 5: Curate Briefs

### Trigger
```
/curate-briefs {clientId}
```

### Steps

1. **Fetch unused signals** - Status = "unused"
2. **Group related** - Max 3 signals per brief
3. **Create brief** - With POV, target persona, pillar
4. **Update signal status** - "used_in_brief"

### Skills Executed
- `create-assignment-brief`

### Output
```
Firebase: clients/{clientId}/modules/linkedin-ghostwriter/assignment-briefs/
└── {briefId}/
    ├── signals: [{signalId}, ...]
    ├── targetPersona
    ├── pov
    ├── contentPillar
    ├── funnelStage
    ├── status: "ready"
    └── createdAt
```

---

## Phase 6: Create Content

### Trigger
```
/ghostwrite {clientId} --founder "{founderName}"
```

### Steps

1. **Select briefs** - By funnel distribution
2. **Load context** - Voice contract, company, audience
3. **Select template** - Based on brief type
4. **Generate post** - Using ghostwriter agent
5. **QA review** - Score and evaluate
6. **Revise if needed** - Max 2 iterations

### Skills Executed
- `ghostwrite-content`
- Evaluation pipeline

### Output
```
Firebase: clients/{clientId}/modules/linkedin-ghostwriter/posts/
└── {postId}/
    ├── briefId
    ├── founderId
    ├── content
    ├── template
    ├── funnelStage
    ├── qaScore
    ├── status: "draft" | "approved" | "published"
    └── createdAt
```

---

## Phase 7: Deliver

### Trigger
```
/sync-notion {clientId}
```

### Steps

1. **Fetch approved posts** - Status = "approved"
2. **Transform to Notion** - Map fields to properties
3. **Upload** - Create pages in Notion database
4. **Update status** - Mark as "synced" in Firebase

### Skills Executed
- `upload-posts-to-notion`

### Output
```
Notion: Posts Database
└── {page}/
    ├── Name: {post title}
    ├── Content: {post content}
    ├── Status: Ready for Review
    ├── Founder: {founder name}
    └── ...

Firebase: Update post status to "synced"
```

---

## Skill Execution Flow

When Claude Code starts, it should:

```
1. READ active client
   └── inputs/active_client.md → Get {clientId}

2. DETERMINE phase
   └── Check what's needed based on MRD or user request

3. MATCH to existing skills
   └── ls skills/*/SKILL.md
   └── Score match (0-1) for each requirement

4. EXECUTE existing skills (if match ≥ 50%)
   └── Pull context from Firebase
   └── Run skill
   └── Push results to Firebase

5. CREATE new skills (if no match)
   └── Create in skills-staging/
   └── Include REVIEW.md
   └── Run tests

6. REPORT results
   └── What was executed
   └── What was created
   └── What's in Firebase
   └── Next steps
```

---

## Standard AI Entry Point

Copy this into Claude Code to start any client work:

```
# MH1 Skill Orchestrator

Read these files first:
1. `SYSTEM_FLOW.md` - This document (system architecture)
2. `CLAUDE.md` - Conventions and rules
3. `config/ontology.yaml` - Data relationships
4. `inputs/active_client.md` - Current client (if set)

Then determine what phase we're in and what needs to happen:

1. If no client set → Check for MRD in `.cursor/modules/MRDs/` → Onboard
2. If client set but no discovery → Run discovery phase
3. If discovery done but no signals → Collect signals
4. If signals but no briefs → Curate briefs
5. If briefs but no posts → Create content
6. If posts ready → Sync to Notion

For each phase:
- Execute existing skills when they match (≥50%)
- Create new skills in `skills-staging/` if no match
- Write all client data to Firebase
- Report results and next steps
```

---

## Commands Reference

| Command | Phase | Description |
|---------|-------|-------------|
| `/onboard-client` | 1 | Create new client from MRD |
| `/discovery` | 2 | Research company, competitors, founders |
| `/configure-signals` | 3 | Set up signal sources |
| `/collect-signals` | 4 | Gather social signals |
| `/curate-briefs` | 5 | Create assignment briefs |
| `/ghostwrite` | 6 | Generate content |
| `/sync-notion` | 7 | Deliver to Notion |
| `/status` | Any | Check client status and next steps |

---

## File Locations

```
mh1-hq/
├── SYSTEM_FLOW.md          # This file - system architecture
├── CLAUDE.md               # AI conventions and rules
├── START.md                # Quick start entry point
│
├── inputs/
│   └── active_client.md    # Current active client
│
├── skills/                 # Production skills
├── skills-staging/         # New skills awaiting review
├── agents/                 # Agent definitions
├── commands/               # Command definitions
├── prompts/                # Reusable prompts
├── config/
│   └── ontology.yaml       # Data relationships
│
├── .cursor/modules/MRDs/   # Market Requirements Documents
│
└── [Firebase]              # All client data (not in repo)
    └── clients/{clientId}/
```

---

## Important Rules

1. **NO local client data** - Everything in Firebase
2. **Execute before create** - Use existing skills first
3. **Staging for new skills** - Never directly to `skills/`
4. **Always set active client** - Before any operation
5. **Follow the phases** - Don't skip steps
6. **Report to Firebase** - All outputs stored there
