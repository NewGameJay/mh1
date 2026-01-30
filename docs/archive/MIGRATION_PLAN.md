# Migration Plan: Repository Convergence

**Date:** January 27, 2026  
**Source:** Council Decision (COUNCIL_DECISION.md)  
**Status:** APPROVED  
**Revision:** 3.0 - Hybrid Approach, Complete MCP/Credentials/Runtime

---

## Overview

This document outlines the step-by-step implementation path to merge `mh1-hq` (System Architecture) and `MH-1-Platform` (Client Delivery) into a unified system using the **hybrid merge approach**.

**Merge Direction:** MH-1-Platform remains operational base; mh1-hq governance modules integrated INTO it.

**Total Estimated Duration:** 10 weeks (5 sprints)  
**Total Components:** 294+ (see COMPONENT_MAP.md)  
**Total MCP Servers:** 12 (8 from mh1-hq + 4 unique from MH-1-Platform)  
**Critical Fixes:** 15+ hardcoded values, 4 missing MCP scripts, 1 broken import (FIXED)  
**Deferred Items:** None - all components are immediate priorities

---

## Phase 0: Preparation (Week 0)

### 0.1 Environment Setup (Dual Runtime)

```bash
# Create unified development environment
cd /Users/jflo7006/Downloads/Marketerhire/mh1-hq

# Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Update requirements.txt
cat >> requirements.txt << 'EOF'
# Added for integration
firebase-admin>=6.0.0
requests>=2.28.0
EOF

pip install -r requirements.txt

# Node.js environment (for Firebase skills)
npm install  # Uses root package.json
```

### 0.2 Backup & Branching

```bash
# Create migration branch
git checkout -b feature/repo-convergence

# Tag current state for rollback
git tag pre-convergence-$(date +%Y%m%d)

# Document current MH-1-Platform state
cp -r MH-1-Platform MH-1-Platform.backup
```

### 0.3 Credentials Migration (CRITICAL)

**DO NOT port credentials directly. Follow this secure handling process:**

```bash
# 1. Create credentials directory
mkdir -p credentials
echo "credentials/" >> .gitignore

# 2. Move Firebase service account (DO NOT commit)
cp MH-1-Platform/moe-platform-479917-firebase-adminsdk-*.json credentials/firebase-service-account.json

# 3. Create .env file for API keys (DO NOT commit)
cat > .env << 'EOF'
# Firebase
GOOGLE_APPLICATION_CREDENTIALS=./credentials/firebase-service-account.json
FIREBASE_PROJECT_ID=moe-platform-479917
FIREBASE_STORAGE_BUCKET=moe-platform-479917.firebasestorage.app

# Firecrawl (extract from MH-1-Platform/.mcp.json)
FIRECRAWL_API_KEY=<REDACTED_MOVE_FROM_MCP_JSON>

# Parallel (extract from MH-1-Platform/.mcp.json)
PARALLEL_AUTH_TOKEN=<REDACTED_MOVE_FROM_MCP_JSON>

# HubSpot (existing)
HUBSPOT_ACCESS_TOKEN=<existing>

# Snowflake (existing)
SNOWFLAKE_ACCOUNT=<existing>
SNOWFLAKE_USER=<existing>
SNOWFLAKE_PASSWORD=<existing>

# Airtable (existing)
AIRTABLE_API_KEY=<existing>
EOF

echo ".env" >> .gitignore
```

### 0.4 Path Normalization

**MH-1-Platform has Windows paths that need normalization:**

```bash
# Find and replace Windows paths in .mcp.json
# FROM: "C:\\Workspaces\\MH-1-Platform\\..."
# TO: "./credentials/..." or "${ENV_VAR}"

# Update .mcp.json to use environment variables
sed -i '' 's|C:\\\\Workspaces\\\\MH-1-Platform\\\\|./|g' MH-1-Platform/.mcp.json
```

### 0.5 Fix mh1-hq Issues

**These issues exist in the current mh1-hq codebase and must be fixed:**

```bash
# 1. CLAUDE.md paths already fixed (paths corrected from .mh1-system/ to root)
# Verify: grep -r ".mh1-system" CLAUDE.md  # Should return nothing

# 2. lib/release_policy.py - get_release_reason already added
# Verify: grep "def get_release_reason" lib/release_policy.py

# 3. Add __init__.py to directories that need to be Python packages
touch scripts/__init__.py
touch agents/__init__.py
touch workflows/__init__.py
```

### 0.6 Fix MH-1-Platform Hardcoded Values

**Fix these files before porting:**

```bash
# 1. Fix score_posts.py - replace hardcoded CLIENT_ID
# FROM: CLIENT_ID = "ui1do9cjAQiqnkmuPOgx"
# TO: Read from inputs/active_client.md or CLI argument

# 2. Fix upload_to_firestore.py - same issue

# 3. Fix get-client.js - use GOOGLE_APPLICATION_CREDENTIALS
# FROM: require('../../../moe-platform-479917-firebase-adminsdk-*.json')
# TO: require(process.env.GOOGLE_APPLICATION_CREDENTIALS || './credentials/firebase-service-account.json')

# 4. Fix firebase-init.js - same issue

# 5. Fix fetch-full-client.cjs - same issue
```

### 0.7 Create Missing MCP Server Scripts

**These scripts are referenced in `config/mcp-servers.json` but don't exist:**

```bash
# Create placeholder scripts that will be implemented in Sprint 1
mkdir -p scripts
touch scripts/mcp_server_hubspot.py
touch scripts/mcp_server_snowflake.py
touch scripts/mcp_server_perplexity.py
touch scripts/mcp_server_n8n.py

# Each script should follow the MCP server protocol
# See: https://modelcontextprotocol.io/docs/server/python
```

### 0.8 Test Infrastructure

- [ ] Ensure pytest is configured
- [ ] Create `tests/integration/` directory
- [ ] Set up test fixtures for Firebase (mock or sandbox project)
- [ ] Verify Node.js skills work (`npm test` in skill directories)
- [ ] Test that `lib/__init__.py` imports work: `python -c "from lib import get_release_reason"`

**Deliverable:** Development environment ready, credentials secured, paths normalized, mh1-hq issues fixed, backups in place.

---

## Phase 1: Foundation Consolidation (Week 1-2)

### 1.1 MCP Configuration Merge (ALL 12 SERVERS)

**Goal:** Unified MCP config with all servers from both repos

**Current State:**
- `mh1-hq/config/mcp-servers.json`: 8 servers (hubspot, snowflake, airtable, notion, perplexity, browser, filesystem, n8n)
- `MH-1-Platform/.mcp.json`: 5 servers (firebase-mcp, firecrawl, Parallel-Search-MCP, Parallel-Task-MCP, Notion)
- **Overlap:** Notion (use mh1-hq version)
- **Total Unique:** 12 servers

**Merged Configuration:**

```json
{
  "mcpServers": {
    // From mh1-hq
    "hubspot": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@anthropic/hubspot-mcp"],
      "env": {
        "HUBSPOT_ACCESS_TOKEN": "${HUBSPOT_ACCESS_TOKEN}"
      }
    },
    "snowflake": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@anthropic/snowflake-mcp"],
      "env": {
        "SNOWFLAKE_ACCOUNT": "${SNOWFLAKE_ACCOUNT}",
        "SNOWFLAKE_USER": "${SNOWFLAKE_USER}",
        "SNOWFLAKE_PASSWORD": "${SNOWFLAKE_PASSWORD}"
      }
    },
    "airtable": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@anthropic/airtable-mcp"],
      "env": {
        "AIRTABLE_API_KEY": "${AIRTABLE_API_KEY}"
      }
    },
    
    // From MH-1-Platform
    "firebase-mcp": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@gannonh/firebase-mcp"],
      "env": {
        "FIREBASE_PROJECT_ID": "${FIREBASE_PROJECT_ID}",
        "SERVICE_ACCOUNT_KEY_PATH": "${GOOGLE_APPLICATION_CREDENTIALS}",
        "FIREBASE_STORAGE_BUCKET": "${FIREBASE_STORAGE_BUCKET}"
      }
    },
    "mcp-server-firecrawl": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY}"
      }
    },
    "Parallel-Search-MCP": {
      "type": "http",
      "url": "https://search-mcp.parallel.ai/mcp",
      "headers": {
        "Authorization": "Bearer ${PARALLEL_AUTH_TOKEN}"
      }
    },
    "Parallel-Task-MCP": {
      "type": "http",
      "url": "https://task-mcp.parallel.ai/mcp",
      "headers": {
        "Authorization": "Bearer ${PARALLEL_AUTH_TOKEN}"
      }
    },
    "Notion": {
      "type": "http",
      "url": "https://mcp.notion.com/mcp"
    }
  }
}
```

**Validation:**
- [ ] All 8 MCP servers connect successfully
- [ ] Firebase reads work
- [ ] Firecrawl scraping works
- [ ] Parallel Search/Task work
- [ ] Notion access works

### 1.2 Runtime Coordination Setup

**Goal:** Python and Node.js work together seamlessly

**Python calling Node.js pattern:**

```python
# lib/firebase_bridge.py
import subprocess
import json

def call_firestore_nav(path: str, options: dict = None) -> dict:
    """Call Node.js firestore-nav from Python."""
    cmd = ["node", ".claude/skills/firestore-nav/firestore-nav.js", path]
    if options:
        for key, value in options.items():
            cmd.extend([f"--{key}", str(value)])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

def call_get_client(client_id: str) -> dict:
    """Call Node.js get-client from Python."""
    cmd = ["node", ".claude/skills/get-client/get-client.js", client_id]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)
```

**Node.js package.json at root:**

```json
{
  "name": "mh1-system",
  "version": "1.0.0",
  "dependencies": {
    "firebase-admin": "^13.6.0"
  },
  "scripts": {
    "firestore-nav": "node .claude/skills/firestore-nav/firestore-nav.js",
    "get-client": "node .claude/skills/get-client/get-client.js"
  }
}
```

### 1.3 FIRESTORE_DATAMAP.md Integration

**Goal:** Establish FIRESTORE_DATAMAP.md as the authoritative schema reference

**Action:**

```bash
# Copy to root level for easy access
cp MH-1-Platform/FIRESTORE_DATAMAP.md ./FIRESTORE_DATAMAP.md

# Update paths in the document for multi-tenant structure
# (manual review required)
```

**This document defines:**
- All Firebase collection schemas
- Query patterns for common operations
- Agent usage guidelines
- Data quality standards
- Firestore vs Local file ownership rules

**All developers must read this before working with Firebase.**

### 1.4 MCP Client Extension

**Goal:** Add Firebase and Firecrawl to `lib/mcp_client.py`

**Action:**

```json
{
  "mcpServers": {
    "hubspot": { /* existing from mh1-hq */ },
    "snowflake": { /* existing from mh1-hq */ },
    "airtable": { /* existing from mh1-hq */ },
    "firebase": {
      "command": "npx",
      "args": ["-y", "firebase-mcp"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "./credentials/firebase-service-account.json"
      }
    },
    "firecrawl": {
      "command": "npx", 
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY}"
      }
    }
  }
}
```

**Validation:**
- [ ] All MCP servers connect successfully
- [ ] Firebase reads work
- [ ] Firecrawl scraping works

### 1.2 MCP Client Extension

**Goal:** Add Firebase and Firecrawl to `lib/mcp_client.py`

**Action:** Extend the existing client pattern:

```python
# lib/mcp_client.py additions

class FirebaseClient(MCPClient):
    """Firebase/Firestore operations via MCP."""
    
    def __init__(self, project_id: str):
        super().__init__("firebase")
        self.project_id = project_id
    
    def get_document(self, collection: str, doc_id: str) -> dict:
        return self._call("firestore_get_document", {
            "collection": collection,
            "document_id": doc_id
        })
    
    def set_document(self, collection: str, doc_id: str, data: dict) -> None:
        return self._call("firestore_set_document", {
            "collection": collection,
            "document_id": doc_id,
            "data": data
        })
    
    def query_collection(self, collection: str, filters: list = None) -> list:
        return self._call("firestore_query", {
            "collection": collection,
            "filters": filters or []
        })


class FirecrawlClient(MCPClient):
    """Web scraping via Firecrawl MCP."""
    
    def scrape_url(self, url: str) -> dict:
        return self._call("scrape", {"url": url})
    
    def scrape_batch(self, urls: list[str]) -> list[dict]:
        return [self.scrape_url(url) for url in urls]
```

**Validation:**
- [ ] `FirebaseClient` unit tests pass
- [ ] `FirecrawlClient` unit tests pass
- [ ] Integration test: read existing MH-1 voice contract from Firestore

### 1.3 Create Core Client Libraries (FIXES BUG-001, BUG-003)

**Goal:** Create `lib/client.py` and `lib/firebase_client.py` for client data management.

**CRITICAL:** No local client folders. All client data lives in Firebase.

**Action:**

```python
# lib/firebase_client.py
import firebase_admin
from firebase_admin import credentials, firestore
import os

class FirebaseClient:
    _instance = None
    
    def __init__(self):
        if not firebase_admin._apps:
            cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", 
                                       "./credentials/firebase-service-account.json")
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def get_document(self, path: str) -> dict:
        doc = self.db.document(path).get()
        return doc.to_dict() if doc.exists else None
    
    def get_collection(self, path: str) -> list:
        return [{"id": doc.id, **doc.to_dict()} for doc in self.db.collection(path).stream()]
    
    def set_document(self, path: str, data: dict) -> None:
        self.db.document(path).set(data)
    
    def add_document(self, collection_path: str, data: dict) -> str:
        return self.db.collection(collection_path).add(data)[1].id
```

```python
# lib/client.py
from pathlib import Path
from .firebase_client import FirebaseClient

class ClientManager:
    def __init__(self):
        self.firebase = FirebaseClient.get_instance()
        self._active_client = None
        self._indexed_context = None
    
    def get_active_client(self) -> dict:
        """Read inputs/active_client.md and return client info."""
        active_file = Path("inputs/active_client.md")
        if not active_file.exists():
            raise FileNotFoundError("inputs/active_client.md not found")
        
        content = active_file.read_text()
        client = {}
        for line in content.split("\n"):
            if "=" in line:
                key, value = line.split("=", 1)
                client[key.strip()] = value.strip()
        
        self._active_client = client
        return client
    
    def pull_client_context(self, client_id: str = None) -> dict:
        """Pull all client context from Firebase."""
        if client_id is None:
            client_id = self.get_active_client().get("CLIENT_ID")
        
        self._indexed_context = {
            "client_id": client_id,
            "voice_contracts": self.firebase.get_collection(f"clients/{client_id}/voiceContracts"),
            "context": self.firebase.get_collection(f"clients/{client_id}/context"),
            "founders": self.firebase.get_collection(f"clients/{client_id}/founders"),
        }
        return self._indexed_context
    
    def push_campaign_data(self, campaign_data: dict) -> str:
        """Push generated campaign to Firebase."""
        client_id = self._active_client.get("CLIENT_ID")
        campaign_id = self.firebase.add_document(
            f"clients/{client_id}/campaigns", 
            campaign_data["metadata"]
        )
        for post in campaign_data.get("posts", []):
            self.firebase.add_document(
                f"clients/{client_id}/campaigns/{campaign_id}/posts",
                post
            )
        return campaign_id
```

**Validation:**
- [ ] `from lib.client import ClientManager` imports successfully
- [ ] `ClientManager().get_active_client()` reads inputs/active_client.md
- [ ] `ClientManager().pull_client_context("ui1do9cjAQiqnkmuPOgx")` returns MH-1 data

### 1.4 Create inputs/ Directory (FIXES BUG-002)

**Goal:** Create inputs/ directory with active_client.md

**Action:**

```bash
mkdir -p inputs

cat > inputs/active_client.md << 'EOF'
# Active Client Configuration

CLIENT_ID = ui1do9cjAQiqnkmuPOgx
CLIENT_NAME = MH-1
DEFAULT_FOUNDER = Raaja Nemani
EOF
```

**Validation:**
- [ ] `inputs/active_client.md` exists
- [ ] ClientManager can parse it

### 1.5 Upload MH-1 Local Data to Firebase (FIXES BUG-006, BUG-007, BUG-008)

**Goal:** Upload local MH-1 data that's missing from Firebase.

**CRITICAL:** No local client folders. All data goes to Firebase.

**Action:**

```python
# scripts/migrate_mh1_to_firebase.py
from lib.firebase_client import FirebaseClient
import json
from pathlib import Path

CLIENT_ID = "ui1do9cjAQiqnkmuPOgx"
firebase = FirebaseClient.get_instance()

# 1. Upload voice contracts (FIXES BUG-006)
for vc_file in Path("MH-1-Platform/MH-1/context-data").glob("voice_contract_*.json"):
    with open(vc_file) as f:
        vc_data = json.load(f)
    vc_id = vc_file.stem  # voice_contract_raaja_nemani
    firebase.set_document(f"clients/{CLIENT_ID}/voiceContracts/{vc_id}", vc_data)
    print(f"Uploaded: {vc_id}")

# 2. Upload context documents (FIXES BUG-008)
for ctx_file in Path("MH-1-Platform/MH-1/context").glob("*.md"):
    content = ctx_file.read_text()
    doc_name = ctx_file.stem  # brand, strategy, audience, etc.
    firebase.set_document(f"clients/{CLIENT_ID}/context/{doc_name}", {
        "content": content,
        "updated_at": datetime.now().isoformat(),
        "format": "markdown"
    })
    print(f"Uploaded context: {doc_name}")

# 3. Upload brand-visual docs
for bv_file in Path("MH-1-Platform/MH-1/brand-visual").glob("*.md"):
    content = bv_file.read_text()
    doc_name = f"brand-visual-{bv_file.stem}"
    firebase.set_document(f"clients/{CLIENT_ID}/context/{doc_name}", {
        "content": content,
        "updated_at": datetime.now().isoformat(),
        "format": "markdown"
    })
    print(f"Uploaded brand-visual: {doc_name}")

# 4. Upload existing campaigns (FIXES BUG-007)
for campaign_dir in Path("MH-1-Platform/MH-1/campaigns").iterdir():
    if campaign_dir.is_dir():
        campaign_id = campaign_dir.name
        
        # Upload campaign metadata
        metadata = {
            "campaign_id": campaign_id,
            "created_at": datetime.now().isoformat(),
            "status": "completed"
        }
        firebase.set_document(f"clients/{CLIENT_ID}/campaigns/{campaign_id}", metadata)
        
        # Upload posts
        for posts_file in (campaign_dir / "posts").glob("*.json"):
            with open(posts_file) as f:
                posts = json.load(f)
            for post in posts:
                firebase.add_document(f"clients/{CLIENT_ID}/campaigns/{campaign_id}/posts", post)
        
        print(f"Uploaded campaign: {campaign_id}")

print("Migration complete!")
```

**Validation:**
- [ ] Voice contracts appear in Firebase: `clients/{CLIENT_ID}/voiceContracts/`
- [ ] Context docs appear in Firebase: `clients/{CLIENT_ID}/context/`
- [ ] Campaigns appear in Firebase: `clients/{CLIENT_ID}/campaigns/`
- [ ] `ClientManager().pull_client_context()` returns uploaded data

### 1.6 Remove Local Client Data (Clean Up)

**Goal:** Remove local client data since it's now in Firebase.

**Action:**

```bash
# DO NOT DELETE YET - Keep as backup until Firebase verified
# mv MH-1-Platform/MH-1 MH-1-Platform/MH-1.backup

# After validation, the local clients/ folder is NOT needed
# All client data lives in Firebase
```

**Deliverable:** Core client libraries created, inputs/ directory created, MH-1 data uploaded to Firebase.

---

## Phase 2: Content Pipeline Port (Week 2-3)

### 2.1 Create Ghostwrite Skill Structure

**Goal:** Port ghostwriter functionality into mh1-hq skill format

**Action:**

```bash
# Create skill directory
mkdir -p skills/ghostwrite-content/{prompts,schemas,tests,templates}
```

Create files:
- `skills/ghostwrite-content/SKILL.md` (from template + MH-1-Platform docs)
- `skills/ghostwrite-content/run.py` (new implementation)
- `skills/ghostwrite-content/schemas/input.json`
- `skills/ghostwrite-content/schemas/output.json`

### 2.2 Port Agent Prompts

**Goal:** Convert MH-1-Platform agent markdown to skill prompts

**Source Files:**
- `MH-1-Platform/.claude/agents/linkedin-ghostwriter.md`
- `MH-1-Platform/.claude/agents/linkedin-topic-curator.md`
- `MH-1-Platform/.claude/agents/linkedin-template-selector.md`
- `MH-1-Platform/.claude/agents/linkedin-qa-reviewer.md`

**Action:**

```bash
# Copy and rename
cp MH-1-Platform/.claude/agents/linkedin-ghostwriter.md \
   skills/ghostwrite-content/prompts/ghostwriter.md

cp MH-1-Platform/.claude/agents/linkedin-topic-curator.md \
   skills/ghostwrite-content/prompts/topic-curator.md

cp MH-1-Platform/.claude/agents/linkedin-template-selector.md \
   skills/ghostwrite-content/prompts/template-selector.md

cp MH-1-Platform/.claude/agents/linkedin-qa-reviewer.md \
   skills/ghostwrite-content/prompts/qa-reviewer.md
```

**Modify each prompt to:**
1. Remove MH-1 hardcoded references
2. Add `{client_id}` placeholders
3. Add `{voice_contract}` injection point
4. Standardize output format

### 2.3 Port LinkedIn Templates

**Goal:** Make templates accessible to skill

**Action:**

```bash
# Copy templates
cp -r MH-1-Platform/MH-1/templates/* skills/ghostwrite-content/templates/

# Create template index
python scripts/index_templates.py skills/ghostwrite-content/templates/
```

### 2.4 Implement Skill Runner

**Goal:** Create `run.py` that orchestrates the 6-stage pipeline

**Pipeline Stages:**
1. Load client context + voice contract
2. Topic curation (Haiku)
3. Template selection (Haiku)
4. Draft generation (Sonnet)
5. Polish/refinement (Sonnet)
6. QA evaluation (Haiku checklist + Sonnet holistic)

**Implementation Pattern:**

```python
# skills/ghostwrite-content/run.py (skeleton)

from lib.runner import SkillRunner, ContextManager
from lib.mcp_client import FirebaseClient
from lib.budget import BudgetManager
from lib.evaluator import Evaluator
from lib.release_policy import determine_release_action

class GhostwriteContentSkill:
    def __init__(self, client_id: str, tenant_id: str):
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.firebase = FirebaseClient(project_id="moe-platform-479917")
        self.budget = BudgetManager(tenant_id)
        self.evaluator = Evaluator()
    
    def run(self, input_data: dict) -> dict:
        # Budget check
        if not self.budget.check_available(estimated_cost=2.0):
            return {"error": "budget_exceeded"}
        
        # Load voice contract
        voice_contract = self._load_voice_contract(input_data["founder_id"])
        
        # Stage 1: Topic curation
        topics = self._curate_topics(input_data, voice_contract)
        
        # Stage 2: Template selection
        templates = self._select_templates(topics)
        
        # Stage 3-4: Draft and polish
        drafts = self._generate_drafts(topics, templates, voice_contract)
        
        # Stage 5: QA evaluation
        evaluated = self._evaluate_drafts(drafts, voice_contract)
        
        # Determine release action
        for post in evaluated:
            post["release_action"] = determine_release_action(
                post["evaluation_score"]
            )
        
        # Record costs
        self.budget.record_cost(actual_cost)
        
        return {"posts": evaluated}
```

**Validation:**
- [ ] Skill loads client voice contract
- [ ] All 6 stages execute
- [ ] Budget tracking works
- [ ] Evaluation scores calculated
- [ ] Release actions assigned

### 2.5 Integration Test

**Goal:** Generate 5 posts for MH-1 using merged system

**Test Script:**

```python
# tests/integration/test_ghostwrite_mh1.py

def test_ghostwrite_full_pipeline():
    skill = GhostwriteContentSkill(client_id="mh1", tenant_id="mh1")
    
    result = skill.run({
        "founder_id": "raaja_nemani",
        "topic_count": 5,
        "campaign_id": "test-migration-001"
    })
    
    assert len(result["posts"]) == 5
    assert all(p["evaluation_score"] > 50 for p in result["posts"])
    assert any(p["release_action"] == "auto_deliver" for p in result["posts"])
```

**Deliverable:** `ghostwrite-content` skill functional, generating quality-gated content.

---

## Phase 3: Quality System Integration (Week 3-4)

### 3.1 Add Voice Authenticity Dimension

**Goal:** Extend evaluator with 7th dimension

**Action:** Modify `lib/evaluator.py`:

```python
# Add to EVALUATION_DIMENSIONS
EVALUATION_DIMENSIONS = {
    # ... existing 6 dimensions ...
    "voice_authenticity": {
        "weight": 0.20,
        "description": "Content matches founder's voice contract",
        "checks": [
            "sentence_structure_match",
            "vocabulary_alignment", 
            "rhetoric_pattern_match",
            "anti_pattern_avoidance",
            "length_profile_match"
        ]
    }
}

# Rebalance weights to sum to 1.0
# schema: 0.12, factuality: 0.12, completeness: 0.12, 
# brand: 0.12, risk: 0.10, context: 0.10, voice: 0.20
```

### 3.2 Configure Content Thresholds

**Goal:** Create quality config for content generation

**Action:** Create `config/quality-thresholds.yaml`:

```yaml
# Content-specific quality thresholds
content_generation:
  auto_deliver:
    min_score: 85
    required_dimensions:
      - voice_authenticity >= 80
      - risk_flags == 0
  
  auto_refine:
    min_score: 70
    max_refinement_attempts: 2
  
  human_review:
    min_score: 50
    escalation_reasons:
      - voice_authenticity < 70
      - risk_flags > 0
      - factuality < 70
  
  blocked:
    max_score: 50
    reasons:
      - plagiarism_detected
      - compliance_violation
      - voice_authenticity < 40
```

### 3.3 QA Reviewer Integration

**Goal:** Connect QA reviewer agent to evaluator system

**Action:** The QA reviewer prompt produces qualitative feedback. Create adapter:

```python
# lib/qa_adapter.py

def qa_feedback_to_dimensions(qa_output: dict, voice_contract: dict) -> dict:
    """Convert QA reviewer output to evaluation dimensions."""
    
    scores = {}
    
    # Voice authenticity from QA
    scores["voice_authenticity"] = _calculate_voice_score(
        qa_output.get("voice_match", {}),
        voice_contract
    )
    
    # Other dimensions from QA checklist
    scores["completeness"] = qa_output.get("structure_score", 70)
    scores["brand_voice"] = qa_output.get("tone_score", 70)
    scores["risk_flags"] = _count_risks(qa_output.get("issues", []))
    
    return scores
```

### 3.4 Feedback Loop Infrastructure

**Goal:** Track failures for prompt improvement

**Action:** Create `lib/feedback_tracker.py`:

```python
# Track evaluation failures for prompt engineering
class FeedbackTracker:
    def __init__(self, db_path: str = "data/feedback.db"):
        self.db = sqlite3.connect(db_path)
        self._init_schema()
    
    def record_failure(self, 
                       skill: str,
                       dimension: str, 
                       score: float,
                       content_sample: str,
                       expected_behavior: str):
        """Record a quality failure for analysis."""
        self.db.execute("""
            INSERT INTO failures (skill, dimension, score, sample, expected, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (skill, dimension, score, content_sample, expected_behavior, datetime.now()))
    
    def get_failure_patterns(self, skill: str, dimension: str) -> list:
        """Retrieve common failure patterns for prompt tuning."""
        return self.db.execute("""
            SELECT sample, expected, COUNT(*) as frequency
            FROM failures
            WHERE skill = ? AND dimension = ?
            GROUP BY sample, expected
            ORDER BY frequency DESC
            LIMIT 20
        """, (skill, dimension)).fetchall()
```

**Deliverable:** 7-dimension evaluation with voice authenticity, configurable thresholds, feedback tracking.

---

## Phase 4: Voice Contract Generator (Week 4-5)

### 4.1 Create Skill Structure

```bash
mkdir -p skills/voice-contract-generator/{prompts,schemas,tests}
```

### 4.2 Implement Scraping Pipeline

**Goal:** Automate voice contract creation from LinkedIn posts

**Pipeline:**
1. Input: 10+ LinkedIn post URLs
2. Scrape posts via Firecrawl
3. Analyze patterns with Claude
4. Generate draft voice_contract.json
5. Flag for human review

```python
# skills/voice-contract-generator/run.py

class VoiceContractGeneratorSkill:
    def run(self, input_data: dict) -> dict:
        urls = input_data["post_urls"]  # 10+ URLs required
        
        # Scrape posts
        posts = self.firecrawl.scrape_batch(urls)
        
        # Analyze patterns
        analysis = self._analyze_voice_patterns(posts)
        
        # Generate contract
        contract = self._generate_contract(analysis)
        
        # Always require human review for new contracts
        return {
            "voice_contract": contract,
            "release_action": "human_review",
            "analysis_summary": analysis["summary"],
            "confidence_score": analysis["confidence"]
        }
```

### 4.3 Analysis Prompt

Create `skills/voice-contract-generator/prompts/analyzer.md`:

```markdown
# Voice Pattern Analyzer

Analyze the following LinkedIn posts to extract the author's unique voice patterns.

## Posts to Analyze
{posts}

## Extract These Patterns

### 1. Sentence Structure
- Average sentence length
- Complexity (simple/compound/complex ratios)
- Opening patterns (question, statement, story, data)

### 2. Vocabulary
- Frequently used words/phrases
- Industry jargon level
- Formality level (1-10)
- Emoji usage patterns

### 3. Rhetoric
- Persuasion techniques used
- Call-to-action style
- Storytelling approach
- Use of data/statistics

### 4. Length Profile
- Typical post length (words)
- Paragraph structure
- Use of lists/bullets

### 5. Anti-Patterns
- Phrases they NEVER use
- Styles they avoid
- Topics they don't discuss

Output as JSON matching the voice_contract schema.
```

**Deliverable:** Semi-automated voice contract generation skill.

---

## Phase 5: Lifecycle Audit Beta (Week 5-6)

### 5.1 Review Existing Implementation

The `lifecycle-audit` skill already exists in mh1-hq. Review for:
- [ ] HubSpot MCP integration working
- [ ] Snowflake MCP integration working
- [ ] Budget tracking integrated
- [ ] Evaluation system connected

### 5.2 Mark as Beta

Update `skills/lifecycle-audit/SKILL.md`:

```markdown
## Status: BETA

### Prerequisites
- Client must have HubSpot connected
- Client must have Snowflake data warehouse
- Minimum 1000 contacts in CRM
- 6 months of historical data

### Beta Limitations
- Manual data validation required
- Limited to single-funnel analysis
- No automated recommendations execution
```

### 5.3 Integration Test

```python
# tests/integration/test_lifecycle_audit_beta.py

def test_lifecycle_audit_with_prerequisites():
    # Verify prerequisites check
    skill = LifecycleAuditSkill(client_id="test", tenant_id="test")
    
    # Should fail gracefully without data
    result = skill.run({"company_id": "no-data-company"})
    assert result["status"] == "prerequisites_not_met"
    assert "HubSpot" in result["missing_prerequisites"]
```

**Deliverable:** Lifecycle audit available as beta feature with clear prerequisites.

---

## Phase 6: Dashboard & Observability (Week 6-7)

### 6.1 Budget Dashboard Data

Create API endpoints for budget visibility:

```python
# api/budget_endpoints.py

def get_tenant_budget_status(tenant_id: str) -> dict:
    manager = BudgetManager(tenant_id)
    return {
        "current_period": manager.get_current_usage(),
        "limits": manager.get_limits(),
        "history": manager.get_usage_history(days=30),
        "projections": manager.project_month_end()
    }
```

### 6.2 Quality Metrics Dashboard Data

```python
# api/quality_endpoints.py

def get_quality_metrics(tenant_id: str, skill: str = None) -> dict:
    return {
        "auto_deliver_rate": _calc_rate("auto_deliver"),
        "human_review_rate": _calc_rate("human_review"),
        "average_score": _calc_avg_score(),
        "dimension_breakdown": _get_dimension_averages(),
        "trend": _get_trend(days=30)
    }
```

### 6.3 Telemetry Consolidation

Ensure all runs logged:

```python
# Verify telemetry captures
assert telemetry.get_runs(tenant_id="mh1", limit=10)
assert all(run["cost_usd"] > 0 for run in runs)
assert all(run["duration_seconds"] > 0 for run in runs)
```

**Deliverable:** Data endpoints ready for dashboard integration.

---

## Phase 7: MVP Validation (Week 7-8)

### 7.1 End-to-End Test: New Client Onboarding

```bash
# Simulate new client onboarding
python scripts/create_client.py acme-corp "ACME Corporation"

# Generate voice contract (with test posts)
python -m skills.voice_contract_generator.run \
  --client acme-corp \
  --urls posts.txt

# Human reviews and approves voice contract
# (manual step)

# Generate first campaign
python -m skills.ghostwrite_content.run \
  --client acme-corp \
  --founder "john-doe" \
  --count 5
```

**Success Criteria:**
- [ ] Client created in < 5 minutes
- [ ] Voice contract generated in < 30 minutes
- [ ] First posts generated in < 1 hour
- [ ] At least 1 post achieves `auto_deliver`

### 7.2 Load Test

```python
# Simulate 3 concurrent clients
import concurrent.futures

clients = ["mh1", "acme-corp", "beta-client"]

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(run_campaign, client_id=c, posts=5)
        for c in clients
    ]
    
    results = [f.result() for f in futures]
    
    # Verify isolation
    assert all(r["tenant_costs_isolated"] for r in results)
```

### 7.3 Documentation Update

- [ ] Update README.md with merged architecture
- [ ] Update CLAUDE.md with new capabilities
- [ ] Create QUICKSTART.md for new client setup
- [ ] Archive MH-1-Platform docs (reference only)

**Deliverable:** MVP validated, documentation complete.

---

## Post-Sprint Enhancements

**Note:** With Revision 3.0, there are no deferred features. All 268+ components (including 12 MCP servers) are scheduled across 5 sprints.

### Future Enhancements (Post-Sprint 5)

| Enhancement | Priority | Notes |
|-------------|----------|-------|
| Client self-serve portal | P1 | UI for client access |
| Advanced telemetry dashboard | P1 | Real-time monitoring |
| Mobile app integration | P2 | Push notifications |
| White-label capabilities | P2 | Agency reselling |

### Technical Debt to Address (Continuous)

1. Full test coverage (>80%)
2. CI/CD pipeline setup
3. Secrets management (move from env vars)
4. RBAC implementation
5. Performance optimization

---

## Rollback Plan

If migration fails at any phase:

```bash
# Return to pre-convergence state
git checkout main
git checkout pre-convergence-$(date +%Y%m%d)

# Restore MH-1-Platform backup
rm -rf MH-1-Platform
mv MH-1-Platform.backup MH-1-Platform

# Continue operating MH-1-Platform independently
```

---

## Sign-Off (Revised 5-Sprint Plan)

| Sprint | Focus | Owner | Status |
|--------|-------|-------|--------|
| Sprint 0: Preparation | Environment, backups | CTO | ⬜ |
| Sprint 1: Foundation | MCP, multi-tenant structure, MH-1 migration | CTO | ⬜ |
| Sprint 2: Content Pipeline | ghostwrite-content skill (all 10 stages), agents | Tech Marketer | ⬜ |
| Sprint 3: Social Listening | social-listening-collect, keyword search skills, report agents | Tech Marketer | ⬜ |
| Sprint 4: Support Systems | firestore-nav, firebase-bulk-upload, get-client, voice-contract-generator | CTO | ⬜ |
| Sprint 5: Quality & Analysis | competitor-analysis, founder-content-collect, knowledge integration | All | ⬜ |
| Validation | Full system test, 3+ clients | All | ⬜ |

---

*This plan includes all 294+ components (including 12 MCP servers, 15+ hardcoded fixes, 4 missing scripts) with no deferrals. Review weekly and adjust based on implementation learnings.*
