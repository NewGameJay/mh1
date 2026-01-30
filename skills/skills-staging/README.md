# Skills Staging

This folder contains **new skills awaiting manual review** before promotion to production.

## Why Staging?

New skills created by AI are placed here for human review to ensure:
- Quality standards are met
- No security issues exist
- Implementation is correct
- Tests are comprehensive

## Review Process

1. **Check REVIEW.md** in each skill folder
2. Run tests: `python -m pytest skills-staging/{skill}/tests/ -v`
3. Review code and documentation
4. Check off items in REVIEW.md
5. When approved, promote to production

## Promote to Production

```bash
# After review and approval:
mv skills-staging/{skill-name} skills/{skill-name}

# Update status in SKILL.md from 'staging' to 'active'
sed -i '' 's/status: staging/status: active/' skills/{skill-name}/SKILL.md
```

## Quick Commands

```bash
# List skills awaiting review
./scripts/start-skill-dev.sh --review

# Run tests for a staged skill
cd skills-staging/{skill-name}
python -m pytest tests/ -v
```

## Folder Structure

Each staged skill should contain:

```
skills-staging/{skill-name}/
├── SKILL.md        # Skill definition (required)
├── run.py          # Implementation (required)
├── REVIEW.md       # Review checklist (required)
├── schemas/
│   ├── input.json  # Input schema
│   └── output.json # Output schema
├── examples/
│   └── example-01.json
└── tests/
    └── test_{skill}.py
```

## Do NOT

- Move skills to production without review
- Delete REVIEW.md before approval
- Run staged skills against production data without testing
