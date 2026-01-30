# Production Readiness Checklist: [SKILL_NAME]

**Last Validation:** [YYYY-MM-DD]  
**Validated By:** [Name/Agent]  
**Status:** NOT READY | READY | DEPRECATED

---

## 1. Environment Setup

| Check | Status | Notes |
|-------|--------|-------|
| Dependencies listed in requirements.txt | [ ] | |
| verify_setup.py runs without errors | [ ] | |
| API credentials documented | [ ] | |
| MCP servers configured | [ ] | |

---

## 2. Documentation

| Check | Status | Notes |
|-------|--------|-------|
| SKILL.md complete | [ ] | |
| README.md exists with quick start | [ ] | |
| quick_reference.md exists | [ ] | |
| Examples documented | [ ] | |
| Error messages are clear | [ ] | |

---

## 3. Testing

| Check | Status | Notes |
|-------|--------|-------|
| Golden tests exist in /tests/ | [ ] | |
| All tests pass | [ ] | |
| Edge cases tested | [ ] | |
| Error handling tested | [ ] | |
| Large input handling tested | [ ] | |

---

## 4. Real-World Validation

| Run | Date | Client | Result | Notes |
|-----|------|--------|--------|-------|
| 1 | | | [ ] Pass [ ] Fail | |
| 2 | | | [ ] Pass [ ] Fail | |
| 3 | | | [ ] Pass [ ] Fail | |

**Minimum:** 3 successful runs before marking READY

---

## 5. Performance

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Execution time | [SLA target] | | [ ] Pass [ ] Fail |
| Cost per run | [SLA target] | | [ ] Pass [ ] Fail |
| Success rate | > 95% | | [ ] Pass [ ] Fail |

---

## 6. Integration

| Check | Status | Notes |
|-------|--------|-------|
| Works with lib/runner.py | [ ] | |
| Budget tracking integrated | [ ] | |
| Telemetry logging works | [ ] | |
| Client isolation works | [ ] | |

---

## 7. Security

| Check | Status | Notes |
|-------|--------|-------|
| No hardcoded credentials | [ ] | |
| Sensitive data not logged | [ ] | |
| Output sanitized | [ ] | |

---

## Sign-Off

**Ready for Production:** [ ] YES [ ] NO

**Blockers (if NO):**
1. 
2. 

**Approved By:** _______________  
**Date:** _______________
