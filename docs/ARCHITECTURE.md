# MH1 System Architecture

> Complete technical reference for the MH1 marketing operations system.

---

## Overview

MH1 is a self-operating system for AI-powered marketing operations. It handles:
- Client onboarding and research
- Social signal collection and curation
- Content creation with voice matching
- Quality assurance and delivery

All client data lives in **Firebase** - nothing stored locally except skills and configuration.

---

## 7-Phase Workflow

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

## Phase Reference

| Phase | Command | Input | Output Location |
|-------|---------|-------|-----------------|
| 1. Onboard | `/onboard` | Company info or MRD | `clients/{clientId}/` |
| 2. Discover | `/discover` | Client ID | `clients/{clientId}/context/` |
| 3. Configure | (automatic) | Discovery results | `clients/{clientId}/modules/` |
| 4. Collect | `/signals` | Signal sources | `clients/{clientId}/signals/` |
| 5. Curate | `/briefs` | Signals | `clients/{clientId}/modules/linkedin-ghostwriter/assignment-briefs/` |
| 6. Create | `/write` | Briefs | `clients/{clientId}/modules/linkedin-ghostwriter/posts/` |
| 7. Deliver | `/sync` | Posts | Notion + Firebase status update |

---

## Phase Details

### Phase 1: Onboard

**Trigger:** `/onboard [company name]`

**Steps:**
1. Parse input (company info or MRD)
2. Create client in Firebase at `clients/{clientId}/`
3. Initialize module placeholders
4. Set as active client

**Output:**
```
Firebase: clients/{clientId}/
├── metadata (name, website, status, createdAt)
└── modules/
    ├── linkedin-ghostwriter/
    ├── leads-database/
    └── signals/
```

---

### Phase 2: Discover

**Trigger:** `/discover [client]`

**Steps:**
1. Research company (website, products, market)
2. Research competitors (3-5)
3. Research founders (background, style)
4. Generate interview questions

**Skills Executed:**
- `research-company`
- `research-competitors`
- `research-founder`
- `generate-interview-questions`

**Output:**
```
Firebase: clients/{clientId}/
├── context/
│   ├── company-profile
│   └── audience-personas
├── competitors/{competitorId}/
├── founders/{founderId}/
└── outputs/interview-questions
```

---

### Phase 3: Configure

**Trigger:** Automatic after discovery

**Steps:**
1. Extract keywords from discovery research
2. Identify thought leaders to monitor
3. Configure RSS feeds
4. Set up Notion dashboards

**Output:**
```
Firebase: clients/{clientId}/modules/
├── signals/settings (keywords, thought leaders, RSS)
├── linkedin-ghostwriter/notionDatabaseId
└── leads-database/notionDatabaseId
```

---

### Phase 4: Collect Signals

**Trigger:** `/signals [client]`

**Steps:**
1. Fetch from sources (Twitter, LinkedIn, Reddit, RSS)
2. Score signals (relevance, freshness, engagement)
3. Store qualified signals (score >= 60)
4. Dedupe by URL

**Skills Executed:**
- `twitter-keyword-search`
- `linkedin-keyword-search`
- `reddit-keyword-search`
- `social-listening-collect`

**Output:**
```
Firebase: clients/{clientId}/signals/{signalId}/
├── url
├── content
├── author
├── score
├── status: "unused"
└── collectedAt
```

---

### Phase 5: Curate Briefs

**Trigger:** `/briefs [client]`

**Steps:**
1. Fetch unused signals (status = "unused")
2. Group related signals (max 3 per brief)
3. Create brief with POV, target persona, pillar
4. Update signal status to "used_in_brief"

**Skills Executed:**
- `create-assignment-brief`

**Output:**
```
Firebase: clients/{clientId}/modules/linkedin-ghostwriter/assignment-briefs/{briefId}/
├── signals: [{signalId}, ...]
├── targetPersona
├── pov
├── contentPillar
├── funnelStage
├── status: "ready"
└── createdAt
```

---

### Phase 6: Create Content

**Trigger:** `/write [client]`

**Steps:**
1. Select briefs by funnel distribution
2. Load context (voice contract, company, audience)
3. Select template based on brief type
4. Generate post using ghostwriter agent
5. QA review and scoring
6. Revise if needed (max 2 iterations)

**Skills Executed:**
- `ghostwrite-content`
- Evaluation pipeline

**Output:**
```
Firebase: clients/{clientId}/modules/linkedin-ghostwriter/posts/{postId}/
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

### Phase 7: Deliver

**Trigger:** `/sync [client]`

**Steps:**
1. Fetch approved posts (status = "approved")
2. Transform to Notion format
3. Upload to Notion database
4. Update Firebase status to "synced"

**Skills Executed:**
- `upload-posts-to-notion`

**Output:**
```
Notion: Posts Database
└── {page}/
    ├── Name: {post title}
    ├── Content: {post content}
    ├── Status: Ready for Review
    └── Founder: {founder name}
```

---

## Data Flow

### Firebase Structure

```
clients/{clientId}/
├── metadata/           # Name, website, status, timestamps
├── context/            # Company profile, personas
├── founders/           # Founder profiles and voice contracts
│   └── {founderId}/
│       └── voiceContract
├── competitors/        # Competitor profiles
├── signals/            # Collected social signals
├── modules/
│   ├── linkedin-ghostwriter/
│   │   ├── assignment-briefs/
│   │   └── posts/
│   ├── leads-database/
│   └── signals/settings
├── outputs/            # Generated outputs (interview questions, etc.)
└── evaluations/        # QA results
```

### What Gets Written

| Data Type | Path | When | By What |
|-----------|------|------|---------|
| Client metadata | `clients/{id}/metadata` | Onboarding | `/onboard` |
| Company profile | `clients/{id}/context/company-profile` | Discovery | `research-company` |
| Founder profiles | `clients/{id}/founders/{founderId}` | Discovery | `research-founder` |
| Voice contracts | `clients/{id}/founders/{id}/voiceContract` | Post-interview | `incorporate-interview` |
| Competitors | `clients/{id}/competitors/` | Discovery | `research-competitors` |
| Signals | `clients/{id}/signals/` | Collection | `/signals` |
| Briefs | `clients/{id}/modules/.../assignment-briefs/` | Curation | `/briefs` |
| Posts | `clients/{id}/modules/.../posts/` | Creation | `/write` |

### What Gets Read

| Data Type | Path | When | By What |
|-----------|------|------|---------|
| Active client | `clients/{id}/*` | Every operation | Client selector |
| Voice contract | `clients/{id}/founders/{id}/voiceContract` | Content creation | Ghostwriter |
| Unused signals | `clients/{id}/signals/` (status=unused) | Brief curation | `/briefs` |
| Ready briefs | `clients/{id}/.../assignment-briefs/` (status=ready) | Content creation | `/write` |
| Approved posts | `clients/{id}/.../posts/` (status=approved) | Notion sync | `/sync` |

---

## CLI Usage

### Interactive Mode

```bash
chmod +x mh1
./mh1
```

This presents a menu:
```
[1] Start New Project (from MRD)
[2] Select/Change Client
[3] Run Skill
[4] Run Agent
[5] Create Custom Skill
[6] System Status
[7] Help
[8] Exit
```

### Direct Commands

```bash
./mh1 status        # System status
./mh1 skills        # List all skills
./mh1 agents        # List all agents
./mh1 mrds          # List all MRDs
./mh1 run [skill]   # Run specific skill
./mh1 start         # Start MRD workflow
./mh1 help          # Show help
```

### Claude Code Integration

The CLI invokes Claude Code for AI operations:

```python
claude "{prompt}"
```

Or configure API mode in `.mh1/config/settings.yaml`:
```yaml
ai:
  provider: "claude"
  claude:
    api_key_env: "ANTHROPIC_API_KEY"
    model: "claude-sonnet-4-20250514"
```

---

## AI Entry Point

When Claude Code starts a session, it should:

```
1. READ active client
   └── inputs/active_client.md → Get {clientId}

2. DETERMINE phase
   └── Check what's needed based on MRD or user request

3. MATCH to existing skills
   └── ls skills/*/SKILL.md
   └── Score match (0-1) for each requirement

4. EXECUTE existing skills (if match >= 50%)
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

### Phase Detection

```
1. If no client set → Check for MRD in .cursor/modules/MRDs/ → Onboard
2. If client set but no discovery → Run discovery phase
3. If discovery done but no signals → Collect signals
4. If signals but no briefs → Curate briefs
5. If briefs but no posts → Create content
6. If posts ready → Sync to Notion
```

---

## File Structure

```
mh1-hq/
├── MH1.md                  # Marketer quick reference
├── CLAUDE.md               # AI conventions and rules
├── docs/
│   └── ARCHITECTURE.md     # This file
│
├── inputs/
│   └── active_client.md    # Current active client
│
├── skills/                 # Production skills (SKILL.md format)
├── skills-staging/         # New skills awaiting review
├── agents/                 # Agent definitions
├── commands/               # Command definitions
├── prompts/                # Reusable prompts
├── templates/              # Content templates
│
├── config/
│   ├── ontology.yaml       # Data relationships
│   ├── quotas.yaml         # Budget limits
│   └── model-routing.yaml  # AI model settings
│
├── lib/                    # Core Python library
├── ui/                     # Web UI (Next.js)
├── telemetry/              # Run history
│
├── .cursor/modules/MRDs/   # Market Requirements Documents
│
└── [Firebase]              # All client data (not in repo)
    └── clients/{clientId}/
```

---

## Configuration

### settings.yaml

```yaml
ai:
  provider: "claude"

workflow:
  auto_execute_threshold: 0.5   # Auto-execute if skill match >= 50%
  require_confirmation: true

staging:
  dir: "skills-staging"
  require_review_md: true
  run_tests: true
```

### Client Configuration

Located at `inputs/active_client.md`:
```markdown
# Active Client

clientId: example-company
```

---

## Important Rules

1. **NO local client data** - Everything in Firebase
2. **Execute before create** - Use existing skills first
3. **Staging for new skills** - Never directly to `skills/`
4. **Always set active client** - Before any operation
5. **Follow the phases** - Don't skip steps
6. **Report to Firebase** - All outputs stored there

---

## Troubleshooting

### "No active client set"
```bash
./mh1
# Select [2] Select/Change Client
# Enter client ID
```

### "Claude command not found"
Install Claude Code CLI or configure API mode in settings.yaml

### "Skill not found"
```bash
./mh1 skills  # See available skills
# Or create custom skill with option [5]
```

---

## Related Documentation

- `MH1.md` - Marketer quick reference
- `CLAUDE.md` - AI conventions and rules
- `config/ontology.yaml` - Data relationships
- `prompts/skill-development-from-mrd.md` - Skill orchestration guide
