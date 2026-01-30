# MH1 Implementation Plan - Make Fully Functional NOW

**Date:** January 28, 2026
**Goal:** Fix critical issues, complete partial implementations, validate core workflows
**Strategy:** Retain all existing functionality, fix blockers first, optimize later

---

## Executive Summary

The codebase is at **91% production readiness**. To reach 100% functional:

| Priority | Category | Items | Effort |
|----------|----------|-------|--------|
| P0 | Critical Fixes | 2 bugs in firebase_client.py | 30 min |
| P1 | Skill Completion | 9 partial skills need schemas | 1 hour |
| P2 | Validation | Test context sync + core workflows | 30 min |
| P3 | Tests | Add minimal integration tests | 30 min |

**Total estimated effort: 2.5 hours**

---

## GAPS IDENTIFIED

### Codebase Review Findings

1. **Critical Bug**: `lib/firebase_client.py:74-76` - `ConnectionError` shadows Python builtin
2. **Critical Bug**: `lib/firebase_client.py:762-767` - Transaction API uses wrong pattern
3. **9 Partial Skills**: Missing schemas/configs (documented but scripts work)
4. **Context Sync**: Implemented but untested with real workflows
5. **Web UI**: Using mock data, not connected to Firebase

### Session Summary Gaps

The session summary accurately captures the state. No major discrepancies, but:
- Firebase credential path is redacted (blank in doc) - verify `.env` has correct path
- "40 complete skills" but glob shows 49 total - 9 are partial (matches)

---

## PHASE 1: Critical Firebase Fixes (P0)

### Task 1.1: Fix ConnectionError Shadow

**File:** `lib/firebase_client.py`
**Lines:** 74-76
**Issue:** `ConnectionError` class shadows Python's builtin `ConnectionError`

**Current Code:**
```python
class ConnectionError(FirebaseError):
    """Raised when connection to Firebase fails."""
    pass
```

**Fix:**
```python
class FirebaseConnectionError(FirebaseError):
    """Raised when connection to Firebase fails."""
    pass
```

**Also update all references** in the file (search for `ConnectionError`).

---

### Task 1.2: Fix Transaction API

**File:** `lib/firebase_client.py`
**Lines:** 762-767
**Issue:** Uses `@client.transaction` decorator which doesn't exist

**Current Code:**
```python
def transaction(self, callback: Callable) -> Any:
    with self._get_client() as client:
        @client.transaction
        def run_transaction(transaction):
            return callback(transaction, client)
        return run_transaction()
```

**Fix:**
```python
def transaction(self, callback: Callable) -> Any:
    """Execute operations in a transaction."""
    firebase_admin, firestore = _ensure_firebase()

    with self._get_client() as client:
        @firestore.transactional
        def run_transaction(transaction):
            return callback(transaction, client)

        transaction_ref = client.transaction()
        return run_transaction(transaction_ref)
```

---

## PHASE 2: Complete Partial Skills (P1)

### Skills Needing Completion

| Skill | Status | Missing |
|-------|--------|---------|
| `linkedin-keyword-search` | Scripts work | config/, templates/schema |
| `twitter-keyword-search` | Scripts work | config/, templates/schema |
| `reddit-keyword-search` | Scripts work | config/, templates/schema |
| `firebase-bulk-upload` | Scripts work | config/ |
| `upload-posts-to-notion` | Documented | config/, templates/schema |
| `call-analytics` | Documented | Implementation details |
| `sales-rep-performance` | Documented | Implementation details |
| `pipeline-analysis` | Documented | Implementation details |
| `icp-historical-analysis` | Documented | Implementation details |

### Task 2.1: Add Social Signal Output Schema

Create shared schema for all keyword search skills:

**File:** `skills/_templates/social-signal-output-schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SocialSignalOutput",
  "type": "object",
  "required": ["posts", "metadata"],
  "properties": {
    "posts": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "platform", "content", "author", "timestamp"],
        "properties": {
          "id": { "type": "string" },
          "platform": { "type": "string", "enum": ["linkedin", "twitter", "reddit"] },
          "content": { "type": "string" },
          "author": { "type": "string" },
          "timestamp": { "type": "string", "format": "date-time" },
          "url": { "type": "string", "format": "uri" },
          "engagement": {
            "type": "object",
            "properties": {
              "likes": { "type": "integer", "minimum": 0 },
              "comments": { "type": "integer", "minimum": 0 },
              "shares": { "type": "integer", "minimum": 0 }
            }
          }
        }
      }
    },
    "metadata": {
      "type": "object",
      "required": ["query", "collected_at", "count"],
      "properties": {
        "query": { "type": "string" },
        "collected_at": { "type": "string", "format": "date-time" },
        "count": { "type": "integer", "minimum": 0 },
        "platform": { "type": "string" }
      }
    }
  }
}
```

### Task 2.2: Add Config Files to Keyword Search Skills

**File:** `skills/linkedin-keyword-search/config/defaults.yaml`
```yaml
# LinkedIn Keyword Search Defaults
api:
  provider: crustdata
  credits_per_post: 1
  max_results: 100

rate_limits:
  requests_per_minute: 10
  max_concurrent: 3

output:
  format: json
  include_engagement: true
  include_reactions: false

filters:
  date_range: "past_week"
  language: "en"
```

Same pattern for `twitter-keyword-search` and `reddit-keyword-search`.

### Task 2.3: Add Config to Firebase Bulk Upload

**File:** `skills/firebase-bulk-upload/config/defaults.yaml`
```yaml
# Firebase Bulk Upload Defaults
batch:
  max_size: 500
  retry_on_failure: true
  max_retries: 3

validation:
  require_client_id: true
  validate_schema: true

platforms:
  linkedin:
    collection: "signals"
    max_upload: 100
  twitter:
    collection: "signals"
    max_upload: 50
  reddit:
    collection: "signals"
    max_upload: 200
```

---

## PHASE 3: Validate Core Workflows (P2)

### Task 3.1: Verify Firebase Connection

```bash
cd /Users/jflo7006/Downloads/Marketerhire/mh1-hq
source .venv/bin/activate
set -a && source .env && set +a

# Test connection
python3 -c "
from lib.firebase_client import get_firebase_client
client = get_firebase_client()
print('Firebase connected:', client is not None)
"
```

### Task 3.2: Verify Client Selection

```bash
./mh1 status
```

Expected: Shows active client info or prompts for selection.

### Task 3.3: Test Context Sync

```bash
./mh1 sync --status
```

Expected: Shows sync status for current client without errors.

### Task 3.4: Test Skill Execution (Dry Run)

```bash
# Verify skill registry loads
python3 -c "
from lib.registry import discover_skills
skills = discover_skills()
print(f'Found {len(skills)} skills')
assert len(skills) >= 40, 'Expected 40+ skills'
"
```

---

## PHASE 4: Minimal Integration Tests (P3)

### Task 4.1: Create Core Tests

**File:** `tests/test_core_integration.py`

```python
"""Core integration tests for MH1 system."""
import pytest
from pathlib import Path

class TestFirebaseClient:
    """Test Firebase client after fixes."""

    def test_no_builtin_shadowing(self):
        """Verify ConnectionError doesn't shadow Python builtin."""
        from lib.firebase_client import FirebaseConnectionError
        import builtins

        # Our error should have different name
        assert FirebaseConnectionError.__name__ == "FirebaseConnectionError"
        # Python's ConnectionError should still work
        assert builtins.ConnectionError is not FirebaseConnectionError

    def test_exception_hierarchy(self):
        """Test exception class hierarchy."""
        from lib.firebase_client import (
            FirebaseError,
            FirebaseConnectionError,
            DocumentNotFoundError,
            BatchWriteError
        )
        assert issubclass(FirebaseConnectionError, FirebaseError)
        assert issubclass(DocumentNotFoundError, FirebaseError)
        assert issubclass(BatchWriteError, FirebaseError)


class TestSkillRegistry:
    """Test skill discovery and validation."""

    def test_skill_count(self):
        """Verify expected number of skills."""
        from lib.registry import discover_skills
        skills = discover_skills()
        assert len(skills) >= 40

    def test_skill_frontmatter(self):
        """Verify all skills have valid frontmatter."""
        import yaml
        skills_dir = Path("skills")

        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith("_"):
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    content = skill_file.read_text()
                    # Extract YAML frontmatter
                    if content.startswith("---"):
                        end = content.find("---", 3)
                        if end > 0:
                            frontmatter = content[3:end]
                            data = yaml.safe_load(frontmatter)
                            assert "name" in data, f"{skill_dir.name} missing name"
                            assert "description" in data, f"{skill_dir.name} missing description"


class TestClientSelector:
    """Test client selection functionality."""

    def test_selector_loads(self):
        """Verify client selector can be instantiated."""
        from lib.client_selector import get_client_selector
        selector = get_client_selector()
        assert selector is not None


class TestContextSync:
    """Test context sync module."""

    def test_sync_instantiation(self):
        """Verify ContextSync can be created."""
        from lib.context_sync import ContextSync
        sync = ContextSync("test-client")
        assert sync.client_id == "test-client"

    def test_sync_paths_defined(self):
        """Verify sync paths are configured."""
        from lib.context_sync import ContextSync
        assert len(ContextSync.SYNC_PATHS) > 0


class TestEvaluator:
    """Test evaluation system."""

    def test_evaluator_weights(self):
        """Verify evaluator has correct weights."""
        from lib.evaluator import Evaluator
        weights = Evaluator.WEIGHTS
        total = sum(weights.values())
        assert abs(total - 1.0) < 0.01, f"Weights should sum to 1.0, got {total}"
```

---

## Implementation Checklist

### Phase 1: Critical Fixes (Do First)
- [ ] Rename `ConnectionError` to `FirebaseConnectionError` in `lib/firebase_client.py`
- [ ] Update all references to `ConnectionError` in the file
- [ ] Fix transaction API to use `@firestore.transactional` pattern
- [ ] Test: `python -c "from lib.firebase_client import FirebaseConnectionError; print('OK')"`

### Phase 2: Skill Completion
- [ ] Create `skills/_templates/social-signal-output-schema.json`
- [ ] Add `config/defaults.yaml` to `linkedin-keyword-search`
- [ ] Add `config/defaults.yaml` to `twitter-keyword-search`
- [ ] Add `config/defaults.yaml` to `reddit-keyword-search`
- [ ] Add `config/defaults.yaml` to `firebase-bulk-upload`
- [ ] Symlink or copy schema to each skill's `templates/`

### Phase 3: Validation
- [ ] Run `./mh1 status` - verify client selection works
- [ ] Run `./mh1 sync --status` - verify sync shows status
- [ ] Run skill registry check - verify 40+ skills found

### Phase 4: Tests
- [ ] Create `tests/test_core_integration.py`
- [ ] Run `pytest tests/test_core_integration.py -v`
- [ ] Verify all tests pass

---

## Success Criteria

After completing this plan:

```bash
# All these commands should work without errors:

# 1. Firebase client imports correctly
python -c "from lib.firebase_client import FirebaseConnectionError; print('OK')"

# 2. Client selection works
./mh1 status

# 3. Sync command works
./mh1 sync --status

# 4. Skills discovered
python -c "from lib.registry import discover_skills; print(f'{len(discover_skills())} skills')"

# 5. Tests pass
pytest tests/test_core_integration.py -v
```

---

## What We're NOT Doing (Optimize Later)

- Migrating all skills to folder structure (scripts exist, can run incrementally)
- Adding Training folders to all agents (templates exist)
- Connecting Web UI to Firebase (currently uses mock data)
- Performance optimization
- Additional MCP server integrations
- Comprehensive test coverage

---

## Files to Create/Modify

### Create
- `skills/_templates/social-signal-output-schema.json`
- `skills/linkedin-keyword-search/config/defaults.yaml`
- `skills/twitter-keyword-search/config/defaults.yaml`
- `skills/reddit-keyword-search/config/defaults.yaml`
- `skills/firebase-bulk-upload/config/defaults.yaml`
- `tests/test_core_integration.py`

### Modify
- `lib/firebase_client.py` (critical fixes)

---

## Next Action

Start with Phase 1 - the Firebase fixes are blocking production use and take ~30 minutes total.
