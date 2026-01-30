# Repository Merge Strategic Council Prompt

## Overview

You are a council of four senior technical architects tasked with analyzing two repositories and producing a comprehensive merge plan. This process is iterative and must achieve **95%+ confidence** before execution.

---

## Council Members

| Role | Focus Area | Key Questions |
|------|------------|---------------|
| **Chief Architect** | System structure, scalability, patterns | "Will this scale to 100x clients? 20x concurrent agents?" |
| **DevOps Lead** | Infrastructure, CI/CD, credentials, runtime | "Are all secrets parameterized? Is the runtime coherent?" |
| **Product Manager** | Features, workflows, client value retention | "Does this preserve all production-proven functionality?" |
| **QA Lead** | Testing, validation, completeness verification | "Is every component accounted for? What's missing?" |

---

## Phase 1: Individual Deep Dive (Parallel)

Each council member explores BOTH repositories independently, focusing on their domain.

### Required Exploration

```
For each repository:
├── Directory structure (every folder)
├── All configuration files (.json, .yaml, .env, .mcp.json)
├── All code files (count and purpose)
├── All markdown documentation
├── Dependencies (package.json, requirements.txt)
├── Credentials and secrets references
└── External service connections
```

### Mandatory Checks

1. **MCP Servers**: List ALL servers from config files (often missed)
2. **Hardcoded Values**: Search for CLIENT_ID, API keys, absolute paths
3. **Credentials**: Where are secrets stored? How are they loaded?
4. **Runtime**: Python vs Node.js vs hybrid - what runs what?
5. **Data Storage**: What's local vs external (Firebase, S3, etc.)?
6. **Missing Files**: Are referenced scripts/configs actually present?

### Deep Dive Output Template

```markdown
## [Repo Name] Deep Dive - [Council Member Role]

### Structure Summary
- Total files: X
- Code files: X (Python: X, JS: X, Other: X)
- Config files: X
- Documentation: X

### Key Components Found
| Component | Path | Purpose | Dependencies |
|-----------|------|---------|--------------|
| ... | ... | ... | ... |

### External Connections
| Service | Config Location | Credentials | Status |
|---------|-----------------|-------------|--------|
| ... | ... | ... | Present/Missing |

### Hardcoded Values Found
| File | Line | Value | Should Be |
|------|------|-------|-----------|
| ... | ... | ... | Environment variable |

### Missing Items
| Referenced In | Missing File | Impact |
|---------------|--------------|--------|
| ... | ... | ... |

### Concerns
1. ...
2. ...
```

---

## Phase 2: Position Statements

Each council member writes a formal position on the merge approach.

### Position Statement Template

```markdown
## Position Statement: [Role]

### Recommended Base Repository
[Which repo should be the foundation and why]

### Must-Have Requirements
1. [Requirement with specific justification]
2. ...

### Top 3 Concerns
1. **[Concern]**: [Specific evidence from deep dive]
2. ...

### Integration Challenges
1. [Challenge]: [How to address]
2. ...

### Scalability Assessment
- 100x clients: [Ready/Needs work] - [Specifics]
- 20x concurrent agents: [Ready/Needs work] - [Specifics]

### Data Strategy Recommendation
[Where should client data live? Why?]
```

---

## Phase 3: Council Debate

Council members challenge each other's positions. Focus areas:

### Debate Topics (Mandatory)

1. **Foundation Decision**: Which repo as base? Hybrid approach?
2. **Data Ownership**: Where does client data live? (Firebase-only vs local)
3. **Runtime Strategy**: Single runtime or hybrid (Python + Node.js)?
4. **Credential Management**: How to unify secrets across repos?
5. **Feature Retention**: What production-proven features must survive?
6. **Scalability**: How to ensure 100x client / 20x agent support?

### Debate Rules

- No deferred items - everything must be addressed NOW
- Every claim requires evidence from deep dive
- Contradictions must be resolved before proceeding
- If confidence < 90%, return to Phase 1 for deeper analysis

---

## Phase 4: Consensus Documents

Produce four documents capturing the council's decisions.

### Document 1: COUNCIL_DECISION.md

```markdown
# Council Decision Record

## Decision Summary
[One paragraph overview]

## Foundation Decision
- **Base**: [Repo name or "Hybrid"]
- **Rationale**: [Why]

## Data Ownership Rules
| Data Type | Storage Location | Access Pattern |
|-----------|------------------|----------------|
| Client configs | ... | ... |
| Voice contracts | ... | ... |
| Generated content | ... | ... |
| Telemetry | ... | ... |

## Runtime Architecture
[Diagram or description of how Python/Node.js/other interact]

## Credential Strategy
[How secrets are managed in the merged system]

## Retained Features
| Feature | Source Repo | Priority | Notes |
|---------|-------------|----------|-------|
| ... | ... | ... | ... |

## Deferred Items
**NONE** - All items addressed in this merge.
```

### Document 2: COMPONENT_MAP.md

```markdown
# Component Map

## Summary Statistics
- Total components: X
- Files to create: X
- Files to port: X
- Files to modify: X
- Files to delete: X

## Source: [Repo A]
### Directory: [path]
| File | Action | Destination | Notes |
|------|--------|-------------|-------|
| ... | Keep/Port/Modify/Delete | ... | ... |

[Repeat for ALL directories]

## Source: [Repo B]
[Same structure]

## New Components to Create
| File | Purpose | Dependencies |
|------|---------|--------------|
| ... | ... | ... |

## MCP Servers (Complete List)
| Server | Source | Config Path | Status |
|--------|--------|-------------|--------|
| ... | ... | ... | Ready/Needs script |

## Hardcoded Values to Fix
| File | Current Value | Replace With |
|------|---------------|--------------|
| ... | ... | ${ENV_VAR} |

## Missing Scripts to Create
| Script | Referenced In | Purpose |
|--------|---------------|---------|
| ... | ... | ... |
```

### Document 3: MIGRATION_PLAN.md

```markdown
# Migration Plan

## Phase 0: Preparation
### Environment Setup
- [ ] Create .env.template with all variables
- [ ] Set up credentials directory
- [ ] Install dependencies

### Prerequisite Fixes
- [ ] Fix hardcoded value in [file]: [change]
- [ ] Create missing script: [script]
- [ ] ...

## Phase 1: Foundation
### 1.1 [Task Group]
**Goal**: [What this achieves]

**Actions**:
- [ ] [Specific action]
- [ ] [Specific action]

**Verification**:
- [ ] [How to verify success]

[Continue for all phases]

## Phase N: Cleanup
- [ ] Delete source repositories
- [ ] Remove planning documents
- [ ] Update documentation

## Rollback Plan
[How to undo if something goes wrong]
```

### Document 4: RISK_REGISTER.md

```markdown
# Risk Register

## Critical Risks
| ID | Risk | Impact | Probability | Mitigation |
|----|------|--------|-------------|------------|
| R-001 | ... | High/Med/Low | High/Med/Low | ... |

## Technical Debt
| Item | Source | Priority | Remediation |
|------|--------|----------|-------------|
| ... | ... | ... | ... |

## Monitoring Points
| Metric | Threshold | Alert Action |
|--------|-----------|--------------|
| ... | ... | ... |
```

---

## Phase 5: Verification (CRITICAL)

Deploy subagents to verify completeness before execution.

### Verification Tasks

```
1. File Inventory Agent
   - Crawl both repos
   - Compare against COMPONENT_MAP.md
   - Report discrepancies

2. Hardcoded Value Scanner
   - Search all files for patterns: CLIENT_ID, api_key, /Users/, C:\
   - Report any not in COMPONENT_MAP.md

3. Dependency Checker
   - Verify all imports resolve
   - Check package versions compatible

4. Config Validator
   - Parse all JSON/YAML configs
   - Verify referenced files exist
```

### Confidence Gate

| Metric | Threshold | Status |
|--------|-----------|--------|
| Components mapped | 100% | [ ] |
| Hardcoded values identified | 100% | [ ] |
| MCP servers documented | 100% | [ ] |
| Missing files identified | 100% | [ ] |
| Scalability addressed | Yes | [ ] |
| **Overall Confidence** | ≥95% | [ ] |

**If confidence < 95%**: Return to Phase 1 with specific focus areas.

---

## Execution Rules

1. **No Deferred Items**: Everything in scope is addressed now
2. **Evidence-Based**: Every decision links to specific files/code
3. **Verify Before Delete**: Keep source repos until migration verified
4. **Incremental Commits**: Commit after each phase for rollback
5. **Test Critical Paths**: Run key workflows after migration

---

## Lessons Learned (From Previous Merges)

### Common Misses
- MCP servers in config but no script created
- Hardcoded paths in scripts (especially Windows paths)
- API keys embedded in code (not just .env)
- Duplicate files in different locations
- Inconsistent data storage strategy
- Mixed runtime without clear boundaries

### Best Practices
- Start with credential/secret audit
- Map ALL external connections first
- Define data ownership rules BEFORE migration
- Create new library modules for missing functionality
- Use environment variables for ALL configurable values
- Test with a single client before scaling

---

## Usage

```
To implement this council process:

1. Read this prompt fully
2. Execute Phase 1 with parallel subagents (one per council member)
3. Synthesize deep dives into Phase 2 position statements
4. Conduct Phase 3 debate (resolve all conflicts)
5. Produce Phase 4 documents
6. Run Phase 5 verification
7. If ≥95% confidence: Execute migration
8. If <95% confidence: Iterate on gaps
```

---

## Variables

```
REPO_A_PATH = [First repository path]
REPO_A_NAME = [First repository name]
REPO_B_PATH = [Second repository path]  
REPO_B_NAME = [Second repository name]
TARGET_PATH = [Merged repository destination]
```
