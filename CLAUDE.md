# MH1 Agent System — Global Context

This file is automatically loaded into every Claude Code session. Keep it concise and actively tuned.

**For marketers:** See `MH1.md` for the simple command reference.
**For developers:** Continue reading below.

**IMPORTANT**: Prefer retrieval-led reasoning over pre-training-led reasoning. When working with MH1 code, skills, or client data, always read the actual files rather than relying on assumptions. See `AGENTS.md` for codebase-specific learnings.

---

## THE MARKETER WORKFLOW (CRITICAL)

When a marketer asks you to do something, you MUST follow this workflow:

**Read:** `prompts/system/mh1-cmo-copilot.md` for the full CMO co-pilot instructions.
**Reference:** `docs/TRUE_USER_FLOW.md` for the complete marketer journey.

**Quick summary:**
1. **Understand** - Parse request, confirm understanding (y/n)
2. **Plan** - Create module folder, generate MRD.md and .plan.md
3. **Approve** - Show plan summary, get approval before executing
4. **Execute** - Run skills per plan, track progress
5. **Deliver** - Compile outputs, present results

**NEVER skip the confirmation step.** Always confirm understanding before planning, and get approval before executing.

---

## Who we are

MH1 builds AI-powered marketing operations for clients. We specialize in:
- Lifecycle marketing audits and automation
- Content production systems (email, social, ads, webinars)
- CRM intelligence (any major platform)
- Agentic marketing workflows

**Platform-Agnostic**: Skills work with any CRM (HubSpot, Salesforce, Pipedrive, Zoho, Dynamics), any data warehouse (Snowflake, BigQuery, Redshift, Databricks, PostgreSQL), and any marketing platform.

**Self-Evolving**: New platforms can be added via `skill-builder` without code changes.

---

## System architecture

- **Claude Code** is our orchestration layer for multi-step workflows.
- **Skills** are versioned, reusable modules in `skills/` (AgentSkills.io YAML frontmatter format).
- **Agents** are defined in `agents/` (orchestrators, workers, evaluators).
- **MCP** connects us to HubSpot, Snowflake, Firebase, Firecrawl, and other tools (12 servers total).
- **Cursor** is used for codebase work and UI; Claude Code for workflows.
- **Web UI** at `ui/` provides task visibility and content management for marketers.
- **Clients** are isolated in `clients/{clientId}/` with local files for voice contracts and campaigns.
- **Governance** is enforced via `lib/budget.py`, `lib/evaluator.py`, and `lib/release_policy.py`.
- **Browser Automation** via `lib/browser_automation.py` provides fallback when APIs fail.

---

## Conventions

### File naming
- Skills: `skills/[skill-name]/SKILL.md`
- Agents: `agents/[type]/[agent-name].md`
- Workflows: `workflows/templates/[workflow-name].md`
- Prompts: `prompts/[prompt-name].md`

### Output formats
- Structured data: JSON with schema validation
- Reports: Markdown with clear sections
- Client deliverables: follow templates in `delivery/client-templates/`

### Quality gates
Every client-facing output must pass:
1. Schema validation (if structured)
2. Factuality check (claims linked to sources)
3. Brand voice check (tone, style)
4. Completeness check (all required sections present)

If any check fails, rerun with stricter constraints or route to human review.

---

## Model routing

| Task type              | Model           | Why                          |
|------------------------|-----------------|------------------------------|
| Strategy, synthesis    | claude-sonnet-4 | Best reasoning               |
| Extraction, cleanup    | claude-haiku    | Fast, cheap, reliable        |
| Long-form writing      | claude-sonnet-4 | Style coherence              |
| Code generation        | claude-sonnet-4 | Accuracy                     |
| Content generation     | claude-sonnet-4 | Voice authenticity           |
| Topic curation         | claude-haiku    | Fast classification          |
| QA review              | claude-haiku    | Checklist evaluation         |
| Voice analysis         | claude-sonnet-4 | Pattern extraction           |

See `config/model-routing.yaml` for full rules.

---

## Key commands

```bash
# Run a skill
claude /run-skill [skill-name] --input [input-file]

# Run an evaluation
claude /eval [output-file] --schema [schema-file]

# Log a run
claude /log-run --workflow [name] --status [pass|fail] --tokens [count]

# Search knowledge base
claude /search-knowledge "[query]"

# Ingest content into knowledge base
/ingest --source "path/to/file.md"
/ingest --source "this conversation" --client "{clientId}"

# Check knowledge graph health
/graph-health
/graph-health --fix --verbose
```

---

## Important paths

- Skills: `skills/`
- Agents: `agents/`
- Schemas: `schemas/`
- Telemetry: `telemetry/`
- Client delivery: `delivery/`
- Core library: `lib/`
- Configuration: `config/`
- Platform registry: `config/platform_registry.yaml` (supported platforms)
- Clients: `clients/{clientId}/`
- Knowledge: `knowledge/`
- Knowledge base: `knowledge/knowledge_base/` (atomic concepts)
- Templates: `templates/`
- Prompts: `prompts/`
- SQL templates: `sql/` (platform-agnostic queries)
- Semantic layer: `config/semantic_layer/` (event/lifecycle mappings)
- Commands: `commands/`
- Web UI: `ui/` (Next.js 15 dashboard)
- Public skills: `public-skills/` (MIT-licensed for ecosystem)

---

## Do NOT

- Hallucinate facts without sources
- Skip quality gates on client deliverables
- Use deprecated skills (check `deprecated` flag in SKILL.md)
- Commit API keys or secrets
- Pass 50K+ tokens directly to any prompt without context offloading
- Use Sonnet for simple extraction tasks (use Haiku)
- Skip context size checks on variable inputs

---

## Context handling guidelines

### When to offload context

| Input size | Action | Model routing |
|------------|--------|---------------|
| < 8,000 tokens | Process inline | As per task type |
| 8,000 - 50,000 tokens | Use chunked processing | Haiku for chunks, Sonnet for synthesis |
| > 50,000 tokens | Require explicit ContextManager | Haiku for chunks, Sonnet for synthesis |

### Chunked processing pattern

1. **Peek first**: Always preview data structure before full processing
2. **Filter with code**: Use predicates/regex to reduce data before LLM sees it
3. **Chunk appropriately**: 500-1000 records per chunk
4. **Use cheaper models**: Haiku for chunk processing, Sonnet for synthesis
5. **Track sub-calls**: Log every sub-LM call for cost analysis

### Using ContextManager

```python
from lib.runner import ContextManager, ContextConfig

ctx = ContextManager(large_data, ContextConfig(max_inline_tokens=8000))

if ctx.should_offload():
    # Process with chunked pattern
    for chunk in ctx.chunk(size=500):
        result = process_with_haiku(chunk)
        ctx.aggregate_buffer("results", result)
    
    final = synthesize_with_sonnet(ctx.get_aggregated("results"))
else:
    # Process directly
    final = process_directly(large_data)
```

### Sub-call model tiering

| Sub-task type | Model | Why |
|---------------|-------|-----|
| chunk_processing | claude-haiku | Fast, cheap extraction |
| filtering | claude-haiku | Simple classification |
| extraction | claude-haiku | Structured data pull |
| verification | claude-haiku | Quick validation |
| aggregation | claude-sonnet-4 | Needs coherence |
| synthesis | claude-sonnet-4 | Complex reasoning |

---

## Knowledge base

### Structure

The atomic knowledge base lives at `knowledge/knowledge_base/`:

```
knowledge/knowledge_base/
├── companies/       # Company profiles (one file per company)
├── founders/        # Founder profiles (one file per founder)
├── competitors/     # Competitor profiles
├── concepts/        # Marketing concepts (content-strategy, etc.)
├── industries/      # Industry profiles
└── emergent/        # New unvalidated concepts (confidence < 0.5)
```

### Node format

All knowledge nodes use `templates/knowledge-node.md` format with frontmatter:

```yaml
---
name: CONCEPT_NAME
type: company|founder|competitor|concept|industry
lifecycle: emergent|validated|canonical
confidence: 0.0-1.0
related_concepts: ["[[wiki-link-1]]", "[[wiki-link-2]]"]
---
```

### Wiki-links

Use `[[wiki-links]]` for relationships between concepts:
- `[[companies/acme-corp]]` - Link to company
- `[[founders/jane-doe]]` - Link to founder
- `[[concepts/content-strategy]]` - Link to concept

### Key commands

```bash
# Ingest content and extract knowledge nodes
/ingest --source "path/to/file.md"
/ingest --source "this conversation"

# Check knowledge graph health
/graph-health
/graph-health --fix --verbose
```

### Lifecycle progression

1. **emergent** - Newly extracted, confidence < 0.5 or unvalidated
2. **validated** - Reviewed and confirmed, confidence ≥ 0.5
3. **canonical** - Authoritative source, confidence ≥ 0.8

### Navigation tips

- Search by type: `find knowledge/knowledge_base/companies -name "*.md"`
- Search by tag: `grep -r "tags:.*linkedin" knowledge/knowledge_base/`
- Find orphans: `/graph-health --verbose`
- Recent changes: `find knowledge/knowledge_base -mtime -7 -name "*.md"`

---

## Platform support & client onboarding

### Supported platforms

See `config/platform_registry.yaml` for complete list. Key platforms:

| Category | Supported |
|----------|-----------|
| CRM | HubSpot, Salesforce, Pipedrive, Zoho, Dynamics |
| Warehouse | Snowflake, BigQuery, Redshift, Databricks, PostgreSQL |
| Email | HubSpot, Salesforce MC, Marketo, Klaviyo |
| Analytics | Segment, Amplitude, Mixpanel, GA4 |

### Adding new platform support

Use the meta-skills for self-evolution:

```bash
# Assess if we can support a new client
/run-skill needs-assessment --client {client_id}

# Onboard a new client (auto-configures everything)
/run-skill client-onboarding --client {client_id}

# Generate skill for unsupported platform
/run-skill skill-builder --platform {platform_name}
```

### Client configuration

Each client has isolated config at `clients/{client_id}/config/`:

```yaml
# datasources.yaml
warehouse:
  type: snowflake
  database: "CLIENT_DB"
  customer_table: "customers"
crm:
  type: hubspot
  pipelines:
    sales: "123456"
thresholds:
  high_value_min: 10000
```

---

## Browser automation

When APIs fail, use browser automation as fallback:

```python
from lib.browser_automation import MH1BrowserClient
from lib.browser_rate_limiter import get_rate_limiter

limiter = get_rate_limiter()
with MH1BrowserClient(session="linkedin-scrape") as browser:
    limiter.wait_for_slot("linkedin.com")
    browser.open("https://linkedin.com/in/username")
    snapshot = browser.snapshot(interactive_only=True)
    limiter.record_request("linkedin.com")
```

Rate limits: LinkedIn (10/min), Twitter (20/min), Reddit (30/min).

---

## Web UI

Start the marketer dashboard:

```bash
cd ui && npm install && npm run dev
# Open http://localhost:3000
```

Features: Task visibility, content approval, client management, settings.

---

## When in doubt

1. Check the skill template: `skills/_templates/SKILL_TEMPLATE/SKILL.md`
2. Check the agent template: `agents/orchestrators/ORCHESTRATOR_TEMPLATE.md`
3. Check the workflow template: `workflows/templates/WORKFLOW_TEMPLATE.md`
4. Check model routing: `config/model-routing.yaml`
5. Check platform support: `config/platform_registry.yaml`
6. Check knowledge base: `knowledge/knowledge_base/` for existing concepts
7. Check implementation docs: `docs/IMPLEMENTATION_COMPLETE.md`
8. Use `needs-assessment` skill for new client evaluation
9. Ask for human review if uncertain about client-facing claims
