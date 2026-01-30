#!/bin/bash
# MH1 Skill Orchestrator - Quick Start
#
# Usage:
#   ./scripts/start-skill-dev.sh                    # Analyze all MRDs, execute & create
#   ./scripts/start-skill-dev.sh flowcode           # Target specific MRD
#   ./scripts/start-skill-dev.sh --execute-only     # Only execute existing skills
#   ./scripts/start-skill-dev.sh --create-only      # Only create new skills (no execution)
#   ./scripts/start-skill-dev.sh --review           # List skills awaiting review

set -e

WORKSPACE_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MRD_DIR="$WORKSPACE_ROOT/.cursor/modules/MRDs"
STAGING_DIR="$WORKSPACE_ROOT/skills-staging"
SKILLS_DIR="$WORKSPACE_ROOT/skills"
PROMPT_FILE="$WORKSPACE_ROOT/prompts/skill-development-from-mrd.md"

# Ensure staging directory exists
mkdir -p "$STAGING_DIR"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              MH1 Skill Orchestrator                          ║"
echo "║   Execute existing skills • Create new skills in staging     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Handle --review flag
if [ "$1" == "--review" ]; then
    echo "📋 Skills Awaiting Review in skills-staging/:"
    echo ""
    if [ -d "$STAGING_DIR" ] && [ "$(ls -A $STAGING_DIR 2>/dev/null)" ]; then
        for skill_dir in "$STAGING_DIR"/*/; do
            if [ -d "$skill_dir" ]; then
                skill_name=$(basename "$skill_dir")
                echo "┌─ $skill_name"
                
                # Check for REVIEW.md
                if [ -f "$skill_dir/REVIEW.md" ]; then
                    approved=$(grep -c "\[x\] Approved for production" "$skill_dir/REVIEW.md" 2>/dev/null || echo "0")
                    if [ "$approved" -gt 0 ]; then
                        echo "│  Status: ✅ Approved - Ready to promote"
                    else
                        echo "│  Status: ⏳ Pending review"
                    fi
                else
                    echo "│  Status: ⚠️  Missing REVIEW.md"
                fi
                
                # Check for tests
                if [ -d "$skill_dir/tests" ]; then
                    echo "│  Tests: $(ls "$skill_dir/tests"/*.py 2>/dev/null | wc -l | tr -d ' ') test file(s)"
                fi
                
                echo "│"
                echo "│  To promote: mv skills-staging/$skill_name skills/$skill_name"
                echo "└─"
                echo ""
            fi
        done
    else
        echo "   (none)"
    fi
    echo ""
    exit 0
fi

# Show MRDs
if [ -d "$MRD_DIR" ]; then
    echo "📋 Available MRDs:"
    ls -1 "$MRD_DIR"/*.html 2>/dev/null | while read f; do
        basename "$f" | sed 's/^/   - /'
    done
    echo ""
else
    echo "⚠️  No MRDs found in $MRD_DIR"
fi

# Show skill counts
PROD_COUNT=$(ls -1 "$SKILLS_DIR" 2>/dev/null | grep -v "^_" | wc -l | tr -d ' ')
STAGING_COUNT=$(ls -1 "$STAGING_DIR" 2>/dev/null | wc -l | tr -d ' ')

echo "📦 Skills:"
echo "   Production: $PROD_COUNT skills in skills/"
echo "   Staging:    $STAGING_COUNT skills in skills-staging/"
echo ""

# Show some existing skills for reference
echo "🔧 Key Existing Skills (can be executed):"
for skill in lifecycle-audit at-risk-detection pipeline-analysis crm-discovery data-quality-audit; do
    if [ -d "$SKILLS_DIR/$skill" ]; then
        desc=$(grep -A1 "^description:" "$SKILLS_DIR/$skill/SKILL.md" 2>/dev/null | tail -1 | sed 's/^[ ]*//' | head -c 60)
        echo "   - $skill: $desc..."
    fi
done
echo ""

# Build the prompt based on arguments
MODE_MODIFIER=""
if [ "$1" == "--execute-only" ]; then
    MODE_MODIFIER="
## Mode: Execute Only
Do NOT create any new skills. Only execute existing skills.
Report any gaps that require new skill development.
"
    echo "🎯 Mode: Execute Only (no new skill creation)"
    shift
elif [ "$1" == "--create-only" ]; then
    MODE_MODIFIER="
## Mode: Create Only  
Do NOT execute any skills. Only analyze and create new skills in skills-staging/.
"
    echo "🎯 Mode: Create Only (no skill execution)"
    shift
else
    echo "🎯 Mode: Full Orchestration (execute existing + create new in staging)"
fi
echo ""

# Target MRD or all
if [ -n "$1" ]; then
    MRD_PATTERN="$1"
    MATCHING_MRD=$(ls "$MRD_DIR"/*.html 2>/dev/null | grep -i "$MRD_PATTERN" | head -1)
    if [ -n "$MATCHING_MRD" ]; then
        MRD_TARGET="MRD File: \`.cursor/modules/MRDs/$(basename "$MATCHING_MRD")\`"
        echo "📄 Target: $(basename "$MATCHING_MRD")"
    else
        echo "❌ No MRD found matching '$MRD_PATTERN'"
        exit 1
    fi
else
    MRD_TARGET="MRD Location: \`.cursor/modules/MRDs/\` (all MRDs)"
    echo "📄 Target: All MRDs"
fi

echo ""
echo "Copy this prompt into Claude Code:"
echo "════════════════════════════════════════════════════════════════"
cat << EOF

# MH1 Skill Orchestrator

You are an MH1 skill orchestrator. Your job is to fulfill client requirements by:
1. **EXECUTING existing skills** when they match the need
2. **CREATING new skills** in \`skills-staging/\` only when no existing skill fits

**Key Principle: Execute first, create only if necessary.**
$MODE_MODIFIER
## Input

$MRD_TARGET

## Context Files (Read First)

1. \`CLAUDE.md\` - System conventions
2. \`skills/lifecycle-audit/SKILL.md\` - Reference implementation
3. \`prompts/skill-development-from-mrd.md\` - Full orchestration guide

## Process

### Phase 1: Analyze & Match
1. Parse MRD requirements (client, problem, integrations, deliverables)
2. Search existing skills: \`ls skills/*/SKILL.md\`
3. Match each requirement to existing skills (score 0-1)
4. Decision per requirement:
   - Match ≥80% → **EXECUTE** the skill
   - Match 50-80% → **EXECUTE + NOTE** gaps
   - Match <50% → **CREATE** new skill in staging

### Phase 2: Execute Existing Skills
For each "execute" decision:
1. Read skill's SKILL.md for inputs
2. Prepare input JSON from MRD data
3. Run: \`python skills/{name}/run.py --input '{...}'\`
4. Capture results and report

### Phase 3: Create New Skills (in staging)
For each "create" decision:
1. Create in \`skills-staging/{skill-name}/\`
2. Include: SKILL.md, run.py, schemas/, tests/, **REVIEW.md**
3. Run tests: \`python -m pytest skills-staging/{name}/tests/ -v\`
4. All tests must pass

### Phase 4: Summary Report
Output:
- Requirements fulfilled (executed vs created)
- Skills executed with results
- Skills created in staging (pending review)
- Gaps remaining
- Next steps

## Important Rules

1. **Execute existing skills first** - Don't reinvent
2. **New skills go to \`skills-staging/\`** - Never directly to \`skills/\`
3. **Every staged skill needs REVIEW.md** - For manual approval
4. **All tests must pass** - Before completing
5. **Report gaps honestly** - Note what couldn't be fulfilled

## Start

Begin with Phase 1: Read the MRDs and match requirements to existing skills.

EOF

echo "════════════════════════════════════════════════════════════════"
echo ""
echo "💡 Tips:"
echo "   • Full guide: prompts/skill-development-from-mrd.md"
echo "   • Review staging: ./scripts/start-skill-dev.sh --review"
echo "   • Promote skill: mv skills-staging/{name} skills/{name}"
echo ""
