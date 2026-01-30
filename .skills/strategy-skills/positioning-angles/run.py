#!/usr/bin/env python3
"""
Positioning & Angles Skill - Execution Script (v1.0.0)

Find the angle that makes something sell. Generates 3-5 distinct positioning
options with headline directions for products, offers, or campaigns.

Features:
- Multiple angle generation using proven frameworks
- Market sophistication assessment
- Headline direction for each angle
- Recommendation for best starting point

Usage:
    # Basic run
    python skills/positioning-angles/run.py --product "AI Marketing Skills Pack"

    # With context
    python skills/positioning-angles/run.py --product "SaaS Tool" --audience "startup founders" --problem "manual marketing"

    # With client context
    python skills/positioning-angles/run.py --client_id abc123 --product "Product Name"

    # Programmatic
    from skills.positioning_angles.run import run_positioning_angles
    result = run_positioning_angles({
        "product": "AI Marketing Skills Pack",
        "audience": "Claude Code users",
        "problem": "generic AI output"
    })
"""

import argparse
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add lib to path
SKILL_ROOT = Path(__file__).parent
SYSTEM_ROOT = SKILL_ROOT.parent.parent
sys.path.insert(0, str(SYSTEM_ROOT / "lib"))

# Import lib modules with fallback
try:
    from runner import WorkflowRunner, RunStatus, estimate_tokens
    from evaluator import evaluate_output
    from telemetry import log_run
except ImportError:
    class RunStatus:
        SUCCESS = "success"
        FAILED = "failed"

    def estimate_tokens(text): return len(str(text)) // 4
    def evaluate_output(output, schema=None, requirements=None):
        return {"score": 0.85, "pass": True}

    class WorkflowRunner:
        def __init__(self, **kwargs):
            self.run_id = str(uuid.uuid4())[:8]
        def run_step(self, name, func, inputs):
            result = func(inputs)
            class StepResult:
                status = "success"
                output = result.get("output", {})
            return StepResult()
        def complete(self, status, evaluation=None): return {}

    def log_run(**kwargs): pass


# Constants
SKILL_NAME = "positioning-angles"
SKILL_VERSION = "v1.0.0"

# Angle frameworks
ANGLE_FRAMEWORKS = [
    {
        "name": "Contrarian",
        "description": "Challenge a common assumption in the market",
        "template": "Everything you've been told about {topic} is wrong. Here's what actually works.",
        "works_when": "Market is frustrated with conventional approaches. Audience sees themselves as independent thinkers."
    },
    {
        "name": "Unique Mechanism",
        "description": "Lead with the HOW, not just the WHAT",
        "template": "The {method_name} that {specific_result}",
        "works_when": "Market is sophisticated (Stage 3+). Similar promises exist. Need to differentiate."
    },
    {
        "name": "Transformation",
        "description": "Before and after. The gap between current and desired state",
        "template": "From {painful_current_state} to {desired_outcome}",
        "works_when": "The transformation is dramatic and specific. Market is problem-aware."
    },
    {
        "name": "Enemy",
        "description": "Position against a common enemy (problem, mindset, obstacle)",
        "template": "Stop letting {enemy} steal your {valuable_thing}",
        "works_when": "Audience has shared frustrations. There's a clear villain to rally against."
    },
    {
        "name": "Speed/Ease",
        "description": "Compress the time or reduce the effort",
        "template": "{outcome} in {surprisingly_short_time} without {expected_sacrifice}",
        "works_when": "Alternatives require significant time or effort. Speed/ease is genuinely differentiated."
    },
    {
        "name": "Specificity",
        "description": "Get hyper-specific about who it's for or what it delivers",
        "template": "For {very_specific_avatar} who want {very_specific_outcome}",
        "works_when": "Competing with generic offerings. Want to signal 'this is built for YOU'."
    },
    {
        "name": "Social Proof",
        "description": "Lead with evidence, not claims",
        "template": "{specific_result} for {number} {type_of_people}",
        "works_when": "Have strong proof. Market is skeptical. Trust is the primary barrier."
    },
    {
        "name": "Risk Reversal",
        "description": "Make the guarantee the headline",
        "template": "{outcome} or {dramatic_consequence_for_seller}",
        "works_when": "Risk is the primary objection. Confidence in delivery is high."
    }
]

# Market sophistication levels
MARKET_STAGES = {
    1: {
        "name": "New category",
        "description": "Market hasn't seen this before",
        "angle_type": "Simple announcement",
        "example": "Now you can {do_thing}"
    },
    2: {
        "name": "Growing awareness",
        "description": "Competition exists, market warming",
        "angle_type": "Claim superiority",
        "example": "The fastest/easiest/most complete way to {outcome}"
    },
    3: {
        "name": "Crowded",
        "description": "Many players, similar claims, skepticism rising",
        "angle_type": "Explain mechanism",
        "example": "Here's WHY this works when others don't"
    },
    4: {
        "name": "Jaded",
        "description": "Market has seen everything, needs new frame",
        "angle_type": "Identity and belonging",
        "example": "For people who {identity_marker}"
    },
    5: {
        "name": "Iconic",
        "description": "Established leaders, brand loyalty matters",
        "angle_type": "Exclusive access",
        "example": "Join the {tribe/movement}"
    }
}


def get_client_from_active_file() -> Dict[str, str]:
    """Read client configuration from inputs/active_client.md."""
    active_client_path = SYSTEM_ROOT / "inputs" / "active_client.md"
    if not active_client_path.exists():
        return {}

    content = active_client_path.read_text()
    result = {}

    for line in content.split('\n'):
        line = line.strip()
        if 'Firestore Client ID:' in line:
            result['client_id'] = line.split(':', 1)[1].strip()
        elif 'Client Name:' in line:
            result['client_name'] = line.split(':', 1)[1].strip()

    return result


class PositioningAnglesSkill:
    """
    Positioning & Angles skill for finding compelling market positions.
    """

    def __init__(
        self,
        client_id: str = None,
        client_name: str = None
    ):
        self.client_id = client_id or "standalone"
        self.client_name = client_name or client_id
        self.run_id = str(uuid.uuid4())[:8]
        self.start_time = time.time()

    def _identify_transformation(self, product: str, problem: str, audience: str) -> Dict:
        """Identify the core transformation the product delivers."""
        # In production, this would use LLM for deeper analysis
        return {
            "before": problem or "struggling with the problem",
            "after": f"achieving results with {product}",
            "pain_removed": problem,
            "capability_gained": f"ability to use {product} effectively"
        }

    def _assess_market_stage(self, inputs: Dict) -> int:
        """Assess market sophistication level."""
        # In production, this would analyze competitor landscape
        # Default to Stage 3 (crowded) as most common scenario
        competitors = inputs.get("competitors", [])
        is_new_category = inputs.get("is_new_category", False)

        if is_new_category:
            return 1
        elif len(competitors) == 0:
            return 2
        elif len(competitors) < 5:
            return 3
        else:
            return 4

    def _generate_angle(
        self,
        framework: Dict,
        product: str,
        audience: str,
        problem: str,
        transformation: Dict
    ) -> Dict:
        """Generate a specific angle using a framework."""
        name = framework["name"]

        # Generate context-specific angle based on framework
        if name == "Contrarian":
            angle = f"Challenge the assumption that {problem} requires traditional approaches"
            headline = f"Stop doing {problem.split()[0] if problem else 'it'} the hard way. Here's what actually works."

        elif name == "Unique Mechanism":
            angle = f"Lead with the specific methodology that makes {product} different"
            headline = f"The {product} Method that delivers results others can't match"

        elif name == "Transformation":
            angle = f"Show the dramatic before/after: {transformation['before']} to {transformation['after']}"
            headline = f"From {transformation['before'][:30]}... to {transformation['after'][:30]}..."

        elif name == "Enemy":
            enemy = problem.split()[0] if problem else "inefficiency"
            angle = f"Position against {enemy} as the common enemy holding people back"
            headline = f"Stop letting {enemy} steal your potential. There's a better way."

        elif name == "Speed/Ease":
            angle = f"Emphasize how {product} compresses time and reduces effort"
            headline = f"Get results in half the time without the usual struggle"

        elif name == "Specificity":
            angle = f"Hyper-focus on {audience} and their exact needs"
            headline = f"Built specifically for {audience} who need {transformation['capability_gained']}"

        elif name == "Social Proof":
            angle = f"Lead with evidence and results from real users"
            headline = f"See why [X] {audience} already use {product} for results"

        elif name == "Risk Reversal":
            angle = f"Make trying {product} completely risk-free"
            headline = f"Get results or get your money back. That's how confident we are."

        else:
            angle = f"Position {product} for {audience}"
            headline = f"{product}: The solution for {audience}"

        return {
            "framework": name,
            "angle": angle,
            "why_it_works": framework["description"],
            "headline_direction": headline,
            "when_to_use": framework["works_when"]
        }

    def _select_best_angles(self, all_angles: List[Dict], market_stage: int) -> List[Dict]:
        """Select the best 3-5 angles based on market context."""
        # Score angles based on market stage fit
        stage_preferences = {
            1: ["Unique Mechanism", "Transformation", "Specificity"],
            2: ["Speed/Ease", "Transformation", "Unique Mechanism"],
            3: ["Unique Mechanism", "Contrarian", "Specificity"],
            4: ["Contrarian", "Enemy", "Specificity"],
            5: ["Social Proof", "Specificity", "Risk Reversal"]
        }

        preferred = stage_preferences.get(market_stage, stage_preferences[3])

        # Sort by preference, then take top 5
        def score_angle(angle):
            framework = angle["framework"]
            if framework in preferred:
                return preferred.index(framework)
            return 10

        sorted_angles = sorted(all_angles, key=score_angle)
        return sorted_angles[:5]

    def _generate_recommendation(self, angles: List[Dict], audience: str) -> str:
        """Generate recommendation for starting point."""
        if not angles:
            return "No angles generated."

        top_angle = angles[0]
        return (
            f"Recommended starting point: **{top_angle['framework']}** angle. "
            f"This works best for {audience} because {top_angle['why_it_works'].lower()}. "
            f"Test with: \"{top_angle['headline_direction']}\""
        )

    def _format_output_markdown(
        self,
        product: str,
        angles: List[Dict],
        market_stage: int,
        recommendation: str
    ) -> str:
        """Format output as markdown document."""
        stage_info = MARKET_STAGES.get(market_stage, MARKET_STAGES[3])

        md = f"""# Positioning Angles for {product}

## Market Assessment

**Stage:** {market_stage} - {stage_info['name']}
**Description:** {stage_info['description']}
**Recommended angle type:** {stage_info['angle_type']}

---

## Angle Options

"""
        for i, angle in enumerate(angles, 1):
            md += f"""### Angle {i}: {angle['framework']}

**The angle:** {angle['angle']}

**Why it works:** {angle['why_it_works']}

**Headline direction:** "{angle['headline_direction']}"

**When to use:** {angle['when_to_use']}

---

"""

        md += f"""## Recommendation

{recommendation}

---

*Generated by positioning-angles skill on {datetime.now().strftime('%Y-%m-%d')}*
"""
        return md

    def run(self, inputs: Dict) -> Dict:
        """
        Main execution method for positioning angles skill.

        Args:
            inputs: Dictionary with:
                - product: Name/description of product or offer (required)
                - audience: Target audience (optional)
                - problem: Problem being solved (optional)
                - competitors: Known competitors (optional)
                - is_new_category: Whether this is a new category (optional)

        Returns:
            Complete skill result with angle options
        """
        product = inputs.get("product")

        if not product:
            return {
                "status": "failed",
                "error": "product is required"
            }

        audience = inputs.get("audience", "target customers")
        problem = inputs.get("problem", "current challenges")

        print(f"\n{'='*60}")
        print(f"POSITIONING & ANGLES")
        print(f"{'='*60}")
        print(f"Product: {product}")
        print(f"Audience: {audience}")
        print(f"Problem: {problem}")
        print(f"Run ID: {self.run_id}")
        print(f"{'='*60}\n")

        runner = WorkflowRunner(
            workflow_name=SKILL_NAME,
            version=SKILL_VERSION,
            client=self.client_id
        )

        try:
            # Step 1: Identify transformation
            print("[Step 1] Identifying core transformation...")
            transformation = self._identify_transformation(product, problem, audience)

            # Step 2: Assess market stage
            print("\n[Step 2] Assessing market sophistication...")
            market_stage = self._assess_market_stage(inputs)
            print(f"  Market stage: {market_stage} ({MARKET_STAGES[market_stage]['name']})")

            # Step 3: Generate angles from all frameworks
            print("\n[Step 3] Generating angles from frameworks...")
            all_angles = []
            for framework in ANGLE_FRAMEWORKS:
                angle = self._generate_angle(
                    framework, product, audience, problem, transformation
                )
                all_angles.append(angle)
                print(f"  - {framework['name']}")

            # Step 4: Select best angles
            print("\n[Step 4] Selecting best angles for context...")
            best_angles = self._select_best_angles(all_angles, market_stage)
            print(f"  Selected {len(best_angles)} angles")

            # Step 5: Generate recommendation
            print("\n[Step 5] Generating recommendation...")
            recommendation = self._generate_recommendation(best_angles, audience)

            # Step 6: Format output
            print("\n[Step 6] Formatting output...")
            markdown = self._format_output_markdown(
                product, best_angles, market_stage, recommendation
            )

            runtime = time.time() - self.start_time

            result = {
                "status": "success",
                "product": product,
                "audience": audience,
                "problem": problem,
                "market_stage": {
                    "level": market_stage,
                    "name": MARKET_STAGES[market_stage]["name"],
                    "description": MARKET_STAGES[market_stage]["description"]
                },
                "angles": best_angles,
                "recommendation": recommendation,
                "markdown": markdown,
                "run_id": runner.run_id,
                "runtime_seconds": round(runtime, 2)
            }

            print(f"\n{'='*60}")
            print(f"ANGLES GENERATED")
            print(f"{'='*60}")
            print(f"Product: {product}")
            print(f"Angles: {len(best_angles)}")
            print(f"Top angle: {best_angles[0]['framework'] if best_angles else 'None'}")
            print(f"Runtime: {runtime:.1f}s")
            print(f"{'='*60}\n")

            runner.complete(RunStatus.SUCCESS)
            return result

        except Exception as e:
            runner.complete(RunStatus.FAILED)
            return {
                "status": "failed",
                "error": str(e),
                "error_type": type(e).__name__,
                "run_id": runner.run_id
            }


def run_positioning_angles(inputs: Dict) -> Dict:
    """
    Main entry point for positioning angles skill.

    Args:
        inputs: Dictionary with product, audience, problem, etc.

    Returns:
        Complete skill result with angle options
    """
    if not inputs.get("client_id"):
        active_client = get_client_from_active_file()
        if active_client.get("client_id"):
            inputs["client_id"] = active_client["client_id"]
            inputs["client_name"] = active_client.get("client_name")

    skill = PositioningAnglesSkill(
        client_id=inputs.get("client_id"),
        client_name=inputs.get("client_name")
    )

    return skill.run(inputs)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Find positioning angles for a product or offer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic run
    python run.py --product "AI Marketing Skills"

    # With full context
    python run.py --product "SaaS Tool" --audience "startup founders" --problem "manual workflows"

    # Save output
    python run.py --product "Product" --output angles.json
        """
    )

    parser.add_argument("--product", type=str, required=True, help="Product or offer name")
    parser.add_argument("--audience", type=str, help="Target audience")
    parser.add_argument("--problem", type=str, help="Problem being solved")
    parser.add_argument("--competitors", type=str, help="Comma-separated competitors")
    parser.add_argument("--is_new_category", action="store_true", help="Is this a new category?")
    parser.add_argument("--client_id", type=str, help="Client identifier")
    parser.add_argument("--output", type=str, help="Output file path (JSON)")

    args = parser.parse_args()

    inputs = {
        "product": args.product,
        "is_new_category": args.is_new_category
    }

    if args.audience:
        inputs["audience"] = args.audience
    if args.problem:
        inputs["problem"] = args.problem
    if args.competitors:
        inputs["competitors"] = args.competitors.split(",")
    if args.client_id:
        inputs["client_id"] = args.client_id

    result = run_positioning_angles(inputs)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Output saved to {args.output}")
    else:
        print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result.get("status") == "success" else 1)


if __name__ == "__main__":
    main()
