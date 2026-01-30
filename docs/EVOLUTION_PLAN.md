# MH1 Evolution Plan: MOE Pattern Integration

This plan merges the best practices from MOE (moe-main) into MH1 while preserving MH1's copilot architecture advantages.

---

## Executive Summary

| Component | Current State | Target State | Priority |
|-----------|---------------|--------------|----------|
| Local Context Storage | Firebase-only | Firebase + local files | P0 |
| Skill Folder Structure | Flat SKILL.md files | config/ scripts/ stages/ templates/ | P0 |
| Agent Training | Basic MD files | Training/ with approaches & references | P1 |
| Intelligence Data Flow | Firebase read/write | Firebase → local cache → working memory | P1 |
| Voice Contracts | Basic schema | MOE's 81-template system | P2 |
| Upload Scripts | None | lib/upload_*.py utilities | P2 |

---

## Phase 1: Local Context Storage (P0)

### Problem
MH1 stores all context in Firebase but doesn't maintain local copies. MOE stores context locally in `outputs/{client}/` which enables:
- Offline access to client context
- Faster reads (no network latency)
- Version control of context files
- Easy debugging and inspection

### Solution

#### 1.1 Create Local Context Directory Structure

```
clients/{client_id}/
├── config/
│   └── datasources.yaml        # Platform connections
├── context/                     # NEW: Local context cache
│   ├── company-research.md     # From research-company
│   ├── founder-research/       # From research-founder
│   │   ├── jane-doe.md
│   │   └── john-smith.md
│   ├── voice-contract.json     # Voice rules
│   ├── audience-personas.json  # Target audiences
│   ├── pov.md                  # Positioning/POV
│   └── competitors/            # Competitor research
│       ├── competitor-1.md
│       └── competitor-2.md
├── signals/                     # NEW: Collected signals
│   ├── linkedin/
│   ├── reddit/
│   └── twitter/
├── content/                     # NEW: Generated content
│   ├── drafts/
│   ├── approved/
│   └── published/
└── campaigns/                   # Existing
    └── active/
```

#### 1.2 Update lib/firebase_client.py

Add local file sync on every Firebase read/write:

```python
# lib/firebase_client.py additions

class FirebaseClient:
    def __init__(self, local_cache_enabled: bool = True):
        self.local_cache_enabled = local_cache_enabled
        self.local_cache_dir = Path("clients")

    def get_document(self, path: str) -> dict:
        """Get document from Firebase, cache locally."""
        doc = self.db.document(path).get().to_dict()

        if self.local_cache_enabled and doc:
            self._cache_locally(path, doc)

        return doc

    def set_document(self, path: str, data: dict) -> None:
        """Write to Firebase AND local cache."""
        self.db.document(path).set(data)

        if self.local_cache_enabled:
            self._cache_locally(path, data)

    def _cache_locally(self, path: str, data: dict) -> None:
        """Cache document to local filesystem."""
        # Convert Firebase path to local path
        # clients/{id}/context/voice-contract → clients/{id}/context/voice-contract.json
        local_path = self.local_cache_dir / f"{path}.json"
        local_path.parent.mkdir(parents=True, exist_ok=True)

        with open(local_path, 'w') as f:
            json.dump(data, f, indent=2)

    def get_cached_or_fetch(self, path: str, max_age_hours: int = 24) -> dict:
        """Get from local cache if fresh, otherwise fetch from Firebase."""
        local_path = self.local_cache_dir / f"{path}.json"

        if local_path.exists():
            age = time.time() - local_path.stat().st_mtime
            if age < max_age_hours * 3600:
                with open(local_path) as f:
                    return json.load(f)

        return self.get_document(path)
```

#### 1.3 Create lib/context_sync.py

New module for bi-directional context synchronization:

```python
# lib/context_sync.py

@dataclass
class SyncStatus:
    local_path: Path
    firebase_path: str
    local_modified: datetime
    firebase_modified: datetime
    status: Literal["synced", "local_newer", "firebase_newer", "conflict"]

class ContextSync:
    """Bi-directional sync between local files and Firebase."""

    def __init__(self, client_id: str):
        self.client_id = client_id
        self.local_root = Path(f"clients/{client_id}/context")
        self.firebase_root = f"clients/{client_id}/context"

    def sync_to_local(self) -> List[SyncStatus]:
        """Pull all context from Firebase to local files."""
        pass

    def sync_to_firebase(self) -> List[SyncStatus]:
        """Push local changes to Firebase."""
        pass

    def check_status(self) -> List[SyncStatus]:
        """Check sync status without making changes."""
        pass

    def resolve_conflict(self, path: str, prefer: Literal["local", "firebase"]) -> None:
        """Resolve a sync conflict."""
        pass
```

#### 1.4 CLI Integration

Add sync commands to mh1 CLI:

```bash
mh1 sync              # Sync current client context
mh1 sync --pull       # Pull from Firebase only
mh1 sync --push       # Push to Firebase only
mh1 sync --status     # Show sync status
```

---

## Phase 2: Standardized Skill Folder Structure (P0)

### Problem
MH1 skills are flat SKILL.md files. MOE uses a rich folder structure with stages, configs, templates, and references that enables:
- Modular skill composition
- Stage-based execution with checkpoints
- Reusable templates and configs
- Self-contained reference materials

### Solution

#### 2.1 New Skill Folder Structure

```
skills/{skill-name}/
├── SKILL.md                    # Main skill definition (frontmatter + instructions)
├── config/
│   ├── defaults.yaml           # Default parameters
│   ├── thresholds.yaml         # Quality thresholds
│   └── model-routing.yaml      # Model selection rules
├── scripts/
│   ├── preprocess.py           # Data preparation
│   ├── postprocess.py          # Output formatting
│   └── validate.py             # Output validation
├── stages/
│   ├── 00-setup.md             # Stage 0: Setup and validation
│   ├── 01-extract.md           # Stage 1: Data extraction
│   ├── 02-transform.md         # Stage 2: Processing
│   └── 03-output.md            # Stage 3: Final output
├── templates/
│   ├── output-schema.json      # Output JSON schema
│   ├── report-template.md      # Report template
│   └── prompts/                # Prompt templates
│       ├── system.md
│       └── user.md
└── references/                  # NEW: Reference materials
    ├── platform-docs.md        # Platform-specific docs
    ├── examples/               # Example inputs/outputs
    │   ├── input-example.json
    │   └── output-example.json
    └── best-practices.md       # Domain best practices
```

#### 2.2 SKILL.md Frontmatter Updates

```yaml
---
name: skill-name
version: 1.0.0
description: What this skill does
category: research|content|analysis|automation

# Stage configuration
stages:
  - id: "00-setup"
    name: "Setup"
    required: true
  - id: "01-extract"
    name: "Extract Data"
    checkpoint: true  # Can resume from here
  - id: "02-transform"
    name: "Transform"
    model: claude-haiku  # Override model for this stage
  - id: "03-output"
    name: "Generate Output"
    model: claude-sonnet-4

# Input/output
inputs:
  - name: client_id
    type: string
    required: true
  - name: options
    type: object
    schema: config/input-schema.json

outputs:
  - name: result
    type: object
    schema: templates/output-schema.json

# Dependencies
requires_skills: []
requires_context:
  - voice-contract
  - company-research

# Execution
timeout_minutes: 30
max_retries: 2
---
```

#### 2.3 Migration Script

Create a script to migrate existing skills:

```python
# scripts/migrate_skills.py

def migrate_skill(skill_path: Path) -> None:
    """Migrate flat SKILL.md to folder structure."""

    # 1. Create folder structure
    skill_dir = skill_path.parent
    (skill_dir / "config").mkdir(exist_ok=True)
    (skill_dir / "scripts").mkdir(exist_ok=True)
    (skill_dir / "stages").mkdir(exist_ok=True)
    (skill_dir / "templates").mkdir(exist_ok=True)
    (skill_dir / "references").mkdir(exist_ok=True)

    # 2. Parse existing SKILL.md
    content = skill_path.read_text()
    frontmatter, body = parse_frontmatter(content)

    # 3. Extract stages from body (if any)
    stages = extract_stages(body)
    for i, stage in enumerate(stages):
        stage_file = skill_dir / "stages" / f"{i:02d}-{stage['id']}.md"
        stage_file.write_text(stage['content'])

    # 4. Create default configs
    create_default_configs(skill_dir, frontmatter)

    # 5. Update SKILL.md frontmatter
    update_frontmatter(skill_path, frontmatter, stages)
```

#### 2.4 Skills to Migrate (Priority Order)

| Skill | Complexity | Notes |
|-------|------------|-------|
| research-company | High | Has multiple extraction phases |
| research-founder | High | Voice extraction + content analysis |
| social-listening-collect | High | 7-agent pipeline in MOE |
| ghostwrite-content | High | Port MOE's 81-template system |
| create-assignment-brief | Medium | Template-based |
| extract-founder-voice | Medium | Schema-based output |
| hubspot-lifecycle-audit | Medium | Multi-stage analysis |
| skill-builder | High | Meta-skill, needs careful migration |

---

## Phase 3: Enhanced Agent Training (P1)

### Problem
MH1 agent MDs are basic instruction files. MOE agents have rich training materials with:
- Detailed approaches and methodologies
- Platform-specific reference docs
- Example interactions
- Common pitfalls and solutions

### Solution

#### 3.1 New Agent Folder Structure

```
agents/{type}/{agent-name}/
├── AGENT.md                    # Main agent definition
├── Training/
│   ├── approaches/
│   │   ├── approach-1.md       # Method 1 with examples
│   │   ├── approach-2.md       # Method 2 with examples
│   │   └── decision-tree.md    # When to use which approach
│   ├── references/
│   │   ├── platform-docs/      # Platform-specific documentation
│   │   │   ├── hubspot-api.md
│   │   │   ├── linkedin-api.md
│   │   │   └── salesforce-api.md
│   │   ├── industry-guides/    # Domain knowledge
│   │   │   ├── b2b-saas.md
│   │   │   └── ecommerce.md
│   │   └── templates/          # Response templates
│   │       ├── analysis-template.md
│   │       └── recommendation-template.md
│   └── examples/
│       ├── successful/         # Good interaction examples
│       │   ├── example-1.md
│       │   └── example-2.md
│       └── failures/           # What to avoid
│           ├── failure-1.md
│           └── failure-2.md
└── Evaluation/                  # NEW: Self-evaluation criteria
    ├── rubric.yaml             # Scoring rubric
    └── test-cases/             # Test inputs/expected outputs
```

#### 3.2 AGENT.md Template Update

```markdown
---
name: agent-name
type: orchestrator|worker|evaluator
version: 1.0.0
description: What this agent does

# Capabilities
capabilities:
  - capability-1
  - capability-2

# Training materials
training:
  approaches:
    - approaches/approach-1.md
    - approaches/approach-2.md
  references:
    - references/platform-docs/hubspot-api.md
  examples:
    - examples/successful/example-1.md

# Evaluation
evaluation:
  rubric: Evaluation/rubric.yaml
  min_score: 0.8
---

# Agent Instructions

## Role
[Clear role definition]

## Process
[Step-by-step process]

## Quality Criteria
[What makes a good output]

## Common Pitfalls
[What to avoid - loaded from Training/examples/failures/]
```

#### 3.3 Agents to Enhance (Priority Order)

| Agent | Type | Training Needs |
|-------|------|----------------|
| lifecycle-auditor | orchestrator | HubSpot/Salesforce docs, audit methodologies |
| content-strategist | orchestrator | Voice matching, content frameworks |
| social-listener | worker | Platform APIs, signal classification |
| ghostwriter | worker | 81 templates, voice contracts, tone guides |
| crm-analyst | worker | Platform docs, query patterns |
| evaluator | evaluator | Rubrics, quality criteria |

---

## Phase 4: Intelligence System Data Flow (P1)

### Problem
The intelligence system reads from Firebase but doesn't properly flow data to local working memory and back. Need clear data flow:

```
Firebase (source of truth)
    ↓ sync
Local Cache (clients/{id}/context/)
    ↓ load
Working Memory (lib/working_memory.py)
    ↓ use
Skill Execution
    ↓ output
Local Cache + Firebase (dual write)
```

### Solution

#### 4.1 Update lib/intelligence/learner.py

```python
class Learner:
    def __init__(self, firebase: FirebaseClient, local_cache: Path):
        self.firebase = firebase
        self.local_cache = local_cache

    def load_client_context(self, client_id: str) -> ClientContext:
        """Load context from local cache (with Firebase fallback)."""
        local_path = self.local_cache / client_id / "context"

        if local_path.exists():
            # Load from local
            context = self._load_local_context(local_path)
        else:
            # Fetch from Firebase and cache
            context = self.firebase.get_document(f"clients/{client_id}/context")
            self._cache_context(local_path, context)

        return context

    def save_learning(self, client_id: str, learning: Learning) -> None:
        """Save learning to both local and Firebase."""
        # Local first (fast)
        local_path = self.local_cache / client_id / "learnings" / f"{learning.id}.json"
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_text(learning.to_json())

        # Firebase (durable)
        self.firebase.set_document(
            f"clients/{client_id}/learnings/{learning.id}",
            learning.to_dict()
        )
```

#### 4.2 Update lib/working_memory.py

```python
class WorkingMemory:
    def __init__(self, context_sync: ContextSync):
        self.context_sync = context_sync
        self._memory: Dict[str, Any] = {}

    def load_client_context(self, client_id: str) -> None:
        """Load all client context into working memory."""
        # Sync from Firebase if needed
        self.context_sync.sync_to_local()

        # Load local files into memory
        context_dir = Path(f"clients/{client_id}/context")
        for file in context_dir.glob("**/*"):
            if file.is_file():
                key = str(file.relative_to(context_dir))
                self._memory[key] = self._load_file(file)

    def save_and_sync(self, key: str, value: Any) -> None:
        """Save to working memory, local file, and Firebase."""
        self._memory[key] = value

        # Write to local file
        local_path = Path(f"clients/{self.client_id}/context/{key}")
        self._write_file(local_path, value)

        # Sync to Firebase
        self.context_sync.sync_to_firebase()
```

---

## Phase 5: Port MOE Assets (P2)

### 5.1 Voice Contract System

Port MOE's voice contract schema and 81 LinkedIn templates:

```
templates/
├── voice-contracts/
│   └── schema.json             # Voice contract JSON schema
└── linkedin-posts/
    ├── tofu/                   # Top of funnel (32 templates)
    │   ├── problem-agitate.md
    │   ├── contrarian-take.md
    │   └── ...
    ├── mofu/                   # Middle of funnel (27 templates)
    │   ├── case-study.md
    │   ├── how-to.md
    │   └── ...
    └── bofu/                   # Bottom of funnel (22 templates)
        ├── testimonial.md
        ├── product-launch.md
        └── ...
```

### 5.2 Upload Scripts

Port MOE's upload utilities to lib/:

```python
# lib/upload_context.py
def upload_voice_contract(client_id: str, contract: dict) -> None:
    """Upload voice contract to Firebase and local cache."""
    pass

# lib/upload_signals.py
def upload_signals(client_id: str, signals: List[dict]) -> None:
    """Upload collected signals with deduplication."""
    pass

# lib/upload_content.py
def upload_content(client_id: str, content: List[dict]) -> None:
    """Upload generated content."""
    pass
```

### 5.3 Deduplication System

Port MOE's signal deduplication:

```python
# lib/deduplication.py

def generate_signal_id(signal: dict) -> str:
    """Generate unique ID from immutable fields."""
    # SHA256 of postUrl, truncated to 12 chars
    immutable = signal.get("postUrl", "")
    return hashlib.sha256(immutable.encode()).hexdigest()[:12]

def deduplicate_signals(
    new_signals: List[dict],
    existing_ids: Set[str]
) -> List[dict]:
    """Filter out duplicate signals."""
    unique = []
    for signal in new_signals:
        signal_id = generate_signal_id(signal)
        if signal_id not in existing_ids:
            unique.append({**signal, "id": signal_id})
    return unique
```

---

## Implementation Timeline

### Week 1: Foundation (P0)
- [ ] Day 1-2: Implement local context storage (lib/context_sync.py)
- [ ] Day 2-3: Update lib/firebase_client.py with dual-write
- [ ] Day 3-4: Add sync commands to CLI
- [ ] Day 4-5: Create skill folder structure template

### Week 2: Skill Migration (P0)
- [ ] Day 1: Create migration script
- [ ] Day 2-3: Migrate research-company, research-founder
- [ ] Day 3-4: Migrate social-listening-collect with stages
- [ ] Day 4-5: Migrate ghostwrite-content with templates

### Week 3: Agent Enhancement (P1)
- [ ] Day 1-2: Create agent folder structure template
- [ ] Day 2-3: Enhance lifecycle-auditor with training materials
- [ ] Day 3-4: Enhance content-strategist and ghostwriter
- [ ] Day 4-5: Create evaluation rubrics

### Week 4: Intelligence & Assets (P1-P2)
- [ ] Day 1-2: Update intelligence system data flow
- [ ] Day 2-3: Port voice contract schema and templates
- [ ] Day 3-4: Port upload scripts and deduplication
- [ ] Day 4-5: Integration testing and documentation

---

## Success Criteria

1. **Local Context Storage**
   - [ ] All client context synced to local files
   - [ ] Changes persist across sessions
   - [ ] Offline access works

2. **Skill Structure**
   - [ ] All skills have consistent folder structure
   - [ ] Stages enable checkpoint/resume
   - [ ] Templates are reusable

3. **Agent Training**
   - [ ] Agents have training materials
   - [ ] Platform references loaded
   - [ ] Examples available

4. **Intelligence Flow**
   - [ ] Data flows: Firebase → Local → Memory → Output
   - [ ] Dual-write ensures durability
   - [ ] Cache improves performance

5. **MOE Assets**
   - [ ] 81 LinkedIn templates available
   - [ ] Voice contract schema implemented
   - [ ] Deduplication working

---

## Files to Create

| File | Purpose |
|------|---------|
| `lib/context_sync.py` | Bi-directional Firebase/local sync |
| `lib/deduplication.py` | Signal deduplication |
| `lib/upload_context.py` | Context upload utilities |
| `lib/upload_signals.py` | Signal upload utilities |
| `lib/upload_content.py` | Content upload utilities |
| `scripts/migrate_skills.py` | Skill folder migration |
| `scripts/migrate_agents.py` | Agent folder migration |
| `templates/skill-folder/` | Skill folder template |
| `templates/agent-folder/` | Agent folder template |
| `templates/voice-contracts/schema.json` | Voice contract schema |
| `templates/linkedin-posts/` | 81 post templates |

## Files to Modify

| File | Changes |
|------|---------|
| `lib/firebase_client.py` | Add local caching, dual-write |
| `lib/working_memory.py` | Load from local cache |
| `lib/intelligence/learner.py` | Use local cache |
| `mh1` | Add sync commands |
| All `skills/*/SKILL.md` | Update frontmatter for stages |
| All `agents/*/*.md` | Update for training structure |

---

## Appendix: MOE Patterns Reference

### A. Stage Naming Convention
```
00-setup.md       # Always first, validates inputs
01-extract.md     # Data extraction
01.75-enrich.md   # Optional enrichment (fractional for insertion)
02-transform.md   # Core processing
03-output.md      # Final output generation
```

### B. Voice Contract Schema (from MOE)
```json
{
  "founder_name": "string",
  "role": "string",
  "voice_characteristics": {
    "tone": ["string"],
    "vocabulary_level": "string",
    "sentence_structure": "string"
  },
  "signature_phrases": ["string"],
  "topics_of_expertise": ["string"],
  "anti_patterns": ["string"],
  "example_posts": [{"content": "string", "engagement": "number"}]
}
```

### C. Signal Deduplication Fields
- **Immutable** (used for ID): postUrl, authorId, platform
- **Mutable** (can update): engagement, comments, shares, lastChecked
