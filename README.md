# MH1 — Your CMO Co-Pilot

**Version 0.6.0** | **Status: Production** | **Last Updated: January 30, 2026**

MH1 is an AI-powered marketing operations CLI. It acts as your CMO co-pilot — executing skills, managing clients, and delivering results without the technical complexity.

```
███╗   ███╗██╗  ██╗  ██╗
████╗ ████║██║  ██║  ███║
██╔████╔██║███████║  ╚██║
██║╚██╔╝██║██╔══██║   ██║
██║ ╚═╝ ██║██║  ██║   ██║
╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝
```

---

## Install

### One-liner (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/NewGameJay/mh1/main/install.sh | bash
```

This installs to `~/.mh1` and adds `mh1` to your PATH. Then just:

```bash
mh1
```

### pip Install (Alternative)

```bash
pip install mh1-copilot
mh1
```

On first run, it downloads the full system to `~/.mh1`.

### Manual Install

```bash
git clone https://github.com/NewGameJay/mh1.git ~/.mh1
cd ~/.mh1
./install.sh
```

### First Run

On first run, MH1 will ask for your Anthropic API key:

```
ANTHROPIC_API_KEY not found.
Enter your API key: sk-ant-...
```

Or set it beforehand:

```bash
echo "ANTHROPIC_API_KEY=sk-ant-your-key" >> ~/.mh1/.env
```

That's it. Run `mh1` and it will guide you from there.

---

## What Can MH1 Do?

### 70+ Marketing Skills

| Category | Examples |
|----------|----------|
| **Analysis** | Lifecycle audit, churn prediction, cohort retention, pipeline analysis |
| **Research** | Competitor research, company research, founder research |
| **Content** | Email copy, newsletters, ghostwriting, SEO content |
| **Strategy** | Positioning angles, email sequences, GTM engineering |
| **Operations** | Client onboarding, data quality audit, account 360 |

### Intelligent Workflows

MH1 automatically detects what you need:

| You Say | MH1 Does |
|---------|----------|
| "Run a lifecycle audit" | Executes single skill |
| "Acme Corp" | Starts client onboarding |
| "Comprehensive retention strategy" | Creates module with multiple skills |
| "Connect HubSpot" | Guides platform configuration |
| "What skills help with churn?" | Answers directly |

---

## How It Works

### Client-Centric

Everything is organized by client:

```
clients/
└── acme-corp/
    ├── config/        # Platform connections, thresholds
    ├── data/          # Raw data files
    └── reports/       # Skill outputs (markdown)
```

### Skill Execution

1. **You request** → "run lifecycle audit"
2. **MH1 checks** → Do we have required inputs? Platform access?
3. **MH1 asks** → Collects anything missing
4. **You confirm** → Review inputs before execution
5. **MH1 executes** → Streams progress in real-time
6. **Output saved** → `clients/{name}/reports/lifecycle-audit-{timestamp}.md`

### Module Workflow (Complex Tasks)

For tasks needing 3+ skills:

1. **Module created** → `modules/{name}-{date}/`
2. **MRD generated** → Requirements document
3. **Plan created** → Skill sequence with dependencies
4. **You approve** → Review before execution
5. **Skills execute** → Sequential with checkpoints
6. **Outputs compiled** → All deliverables in one place

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `./mh1` | Start interactive mode |
| `./mh1 --client "Name"` | Start with a client |
| `1` | List all skills |
| `2` | List all agents |
| `3` | Switch or create client |
| `?` | Show help |
| `q` | Quit |

### Example Sessions

**Single Skill:**
```
> run lifecycle audit

To run lifecycle-audit, I need:
- HubSpot access for contact data
- (Optional) Snowflake for usage enrichment

Do you have HubSpot connected? What contact limit?

> Yes, limit to 100 contacts

Running lifecycle-audit with:
- Platform: HubSpot (connected)
- Limit: 100 contacts

Proceed? [Y/n]
```

**New Client:**
```
> Acme Corp

Detected new client: Acme Corp

Starting onboarding...

Company name: Acme Corp
Industry: SaaS
Website: https://acme.com
Your role: Head of Marketing

What CRM do you use?
1. HubSpot
2. Salesforce
...
```

---

## Configuration

### Environment Variables (`.env`)

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional - Platform connections
HUBSPOT_API_KEY=...
SNOWFLAKE_ACCOUNT=...
SNOWFLAKE_USER=...
SNOWFLAKE_PASSWORD=...
```

### Client Config (`clients/{name}/config/`)

Platform connections and thresholds are stored per-client:

```yaml
# datasources.yaml
warehouse:
  type: snowflake
  database: "CLIENT_DB"
crm:
  type: hubspot
thresholds:
  high_value_min: 10000
  dormant_days: 30
```

---

## Project Structure

```
mh1-hq/
├── mh1                     # CLI entry point (run this)
├── install.sh              # One-liner installer
├── .env                    # Your API keys (auto-created on first run)
├── requirements.txt        # Python dependencies
│
├── clients/                # Client data & outputs
│   └── {client-name}/
│       ├── config/         # Platform configs
│       ├── data/           # Raw data
│       └── reports/        # Skill outputs (markdown)
│
├── modules/                # Complex project folders
│   └── {module-name}/
│       ├── MRD.md          # Requirements document
│       ├── .plan.md        # Execution plan
│       ├── state.json      # Progress tracking
│       └── outputs/        # Deliverables
│
├── .skills/                # 70+ marketing skills
│   ├── analysis-skills/
│   ├── generation-skills/
│   ├── strategy-skills/
│   └── ...
│
├── agents/                 # AI agent definitions
│   ├── orchestrators/
│   ├── workers/
│   └── evaluators/
│
├── lib/                    # Core library
│   ├── workflow/           # CLI workflow components
│   ├── evaluator.py        # Quality evaluation
│   ├── budget.py           # Cost tracking
│   └── ...
│
├── config/                 # System configuration
│   ├── model-routing.yaml
│   ├── input_schemas.yaml
│   └── quotas.yaml
│
└── prompts/                # System prompts
    └── system/
        └── mh1-cmo-copilot.md
```

---

## For Developers

### Adding Skills

Skills live in `.skills/{category}-skills/{skill-name}/`:

```
.skills/analysis-skills/my-skill/
├── SKILL.md          # Definition (YAML frontmatter + markdown)
├── schemas/
│   ├── input.json    # Input validation
│   └── output.json   # Output validation
└── examples/
```

### Skill Definition (`SKILL.md`)

```yaml
---
name: my-skill
description: What this skill does
inputs:
  - name: param1
    type: string
    required: true
outputs:
  result: object
---

# Skill: My Skill

## When to Use
...

## Process
1. Step one
2. Step two
...
```

### Workflow Components (`lib/workflow/`)

| Module | Purpose |
|--------|---------|
| `pathway.py` | Detects which workflow to use |
| `inputs.py` | Structured input collection |
| `markers.py` | Parses `[[SKILL:name]]` markers |
| `module_manager.py` | Creates/manages module folders |
| `skill_executor.py` | Executes skills via Claude |

---

## Quality & Cost

### Quality Gates

Every skill output is evaluated:
- Schema validation
- Factuality check
- Completeness check
- Brand voice match

Score ≥ 80% → Auto-deliver
Score < 80% → Refinement or review

### Cost Optimization

MH1 uses intelligent model routing:

| Task | Model | Cost |
|------|-------|------|
| Extraction | Claude Haiku | $ |
| Analysis | Claude Haiku | $ |
| Synthesis | Claude Sonnet | $$$ |
| Strategy | Claude Sonnet | $$$ |

**Result:** 60-70% savings vs using premium models for everything.

### Budget Tracking

Per-client cost limits in `config/quotas.yaml`:

```yaml
defaults:
  daily_limit_usd: 100
  monthly_limit_usd: 2000
```

---

## Troubleshooting

### "ANTHROPIC_API_KEY not set"

Make sure `.env` exists and contains your key:
```bash
cat .env
# Should show: ANTHROPIC_API_KEY=sk-ant-...
```

### "Skill not found"

Check available skills:
```bash
./mh1
# Then press 1 to list skills
```

### "Missing required inputs"

MH1 now validates inputs before execution. Provide the required inputs when asked.

### "MCP connection failed"

Check platform credentials in `.env` or `clients/{name}/config/`.

---

## Changelog

### v0.6.0 (January 30, 2026)

**CMO Co-Pilot CLI:**
- New interactive CLI with CMO co-pilot persona
- Client-centric workflow (everything under `clients/{name}/`)
- Automatic pathway detection (onboarding, module, skill, config, flex)
- New client name detection triggers onboarding
- Pre-flight input validation before skill execution
- Platform credential collection during onboarding
- Skill outputs saved as human-readable Markdown
- Client context loading (Claude sees existing data)
- One-liner install: `curl ... | bash`

### v0.5.0 (January 26, 2026)

**Production Foundation:**
- Release policy (auto_deliver, auto_refine, human_review, blocked)
- Per-tenant budget tracking
- Skill templates with full contracts
- Execution modes (suggest/preview/execute)

### v0.4.0 (January 25, 2026)

**Research-Based Enhancements:**
- SRAC evaluation framework
- TATS forecasting
- AI washing detection
- Multi-agent pipelines
- 70+ skills

---

## License

Proprietary — MarketerHire Internal Use

---

## Support

- Read this README
- Check `CLAUDE.md` for AI context
- Ask MH1 directly — it's designed to help
