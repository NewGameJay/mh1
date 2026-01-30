# Failure Analysis: [Brief Description]

## Context

**Client**: [Client name or anonymized]
**Date**: [When this occurred]
**Agent**: [Which agent handled this]
**Severity**: [Low/Medium/High]

## User Request

```
[Exact user request]
```

## What Went Wrong

### Failure Point
[At which stage did this fail?]

### Root Cause
[Why did it fail?]

### Impact
[What was the effect on the user/client?]

## The Interaction

### Agent's Initial Analysis
```
Intent: [What agent thought user wanted]
Confidence: [Score]
Selected approach: [What agent decided to do]
```

### What Actually Happened

1. **Step 1**: [What happened]
   - Expected: [What should have happened]
   - Actual: [What did happen]
   - Issue: [Where it went wrong]

2. **Step 2**: [If applicable]
   ...

### User's Response
```
[User feedback indicating failure]
```

## Analysis

### Contributing Factors

1. **[Factor 1]**
   - How it contributed: [Explanation]
   - Warning signs missed: [What could have indicated this]

2. **[Factor 2]**
   - How it contributed: [Explanation]
   - Warning signs missed: [What could have indicated this]

### Detection Opportunities

When should we have caught this?

| Checkpoint | Signal | Why Missed |
|------------|--------|------------|
| Intent parsing | [Signal] | [Reason] |
| Plan creation | [Signal] | [Reason] |
| Execution | [Signal] | [Reason] |
| Quality gates | [Signal] | [Reason] |

## Correct Approach

### What Should Have Happened

1. **Recognition**: [How to properly identify this type of request]
2. **Clarification**: [What questions should have been asked]
3. **Execution**: [Correct approach to use]
4. **Validation**: [How to verify correct output]

### Example Correct Output
```
[What the output should have looked like]
```

## Prevention Measures

### Immediate Fixes
- [ ] [Fix 1 - specific change to make]
- [ ] [Fix 2]

### Systemic Improvements
- [ ] [Improvement 1 - broader change]
- [ ] [Improvement 2]

### Added to Training
- [ ] Added to decision tree: [Where]
- [ ] Added to anti-patterns: [In which approach doc]
- [ ] Created test case: [Path to test]

## Related Failures

- [Similar failure 1](./similar-failure-1.md) - [Brief description]
- [Similar failure 2](./similar-failure-2.md) - [Brief description]

## Follow-up Actions

| Action | Owner | Status |
|--------|-------|--------|
| [Action 1] | [Who] | [ ] |
| [Action 2] | [Who] | [ ] |
