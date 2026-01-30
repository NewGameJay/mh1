"""
MH1 Output Evaluator

Evaluates skill outputs against quality criteria.
Can invoke specialized evaluator agents for specific domains.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import anthropic

PROJECT_ROOT = Path(__file__).parent.parent.parent


@dataclass
class EvaluationResult:
    """Result of output evaluation."""
    score: float  # 0.0 - 1.0
    passed: bool
    dimensions: Dict[str, float]  # Individual dimension scores
    feedback: str
    issues: list
    release_decision: str  # auto_deliver, refine, human_review, blocked


class OutputEvaluator:
    """Evaluates skill outputs for quality."""

    # Quality thresholds
    AUTO_DELIVER_THRESHOLD = 0.8
    REFINE_THRESHOLD = 0.7
    REVIEW_THRESHOLD = 0.6

    # Evaluation dimensions
    DIMENSIONS = [
        "accuracy",      # Are facts correct and verifiable?
        "completeness",  # Are all required outputs present?
        "actionability", # Can the user act on this?
        "relevance",     # Is it relevant to the inputs?
        "clarity",       # Is it clear and well-structured?
        "brand_voice",   # Does it match expected tone?
    ]

    def __init__(self, client_id: str = None):
        self.client_id = client_id
        self.client = anthropic.Anthropic()

    def evaluate(
        self,
        skill_name: str,
        output: Dict[str, Any],
        inputs: Dict[str, Any] = None,
        quality_criteria: list = None,
        quick: bool = False,
    ) -> EvaluationResult:
        """
        Evaluate skill output quality.

        Args:
            skill_name: Name of the skill that produced the output
            output: The output to evaluate
            inputs: Original inputs for context
            quality_criteria: Custom criteria from SKILL.md
            quick: If True, use faster/cheaper evaluation

        Returns:
            EvaluationResult with scores and feedback
        """
        inputs = inputs or {}
        quality_criteria = quality_criteria or []

        # Build evaluation prompt
        prompt = self._build_eval_prompt(skill_name, output, inputs, quality_criteria)

        try:
            # Use Haiku for quick evals, Sonnet for thorough
            model = "claude-3-5-haiku-20241022" if quick else "claude-sonnet-4-20250514"

            response = self.client.messages.create(
                model=model,
                max_tokens=1024,
                system=self._get_evaluator_system_prompt(),
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse evaluation response
            return self._parse_evaluation(response.content[0].text)

        except Exception as e:
            # Return conservative result on error
            return EvaluationResult(
                score=0.5,
                passed=False,
                dimensions={d: 0.5 for d in self.DIMENSIONS},
                feedback=f"Evaluation failed: {e}",
                issues=["evaluation_error"],
                release_decision="human_review"
            )

    def _build_eval_prompt(
        self,
        skill_name: str,
        output: Dict[str, Any],
        inputs: Dict[str, Any],
        quality_criteria: list,
    ) -> str:
        """Build evaluation prompt."""
        output_str = json.dumps(output, indent=2)[:4000]  # Limit size
        inputs_str = json.dumps(inputs, indent=2)[:1000]
        criteria_str = "\n".join(f"- {c}" for c in quality_criteria) if quality_criteria else "Standard quality criteria"

        return f"""Evaluate this skill output for quality.

## Skill: {skill_name}

## Inputs Provided
{inputs_str}

## Output to Evaluate
{output_str}

## Quality Criteria
{criteria_str}

## Evaluation Dimensions
Score each from 0.0 to 1.0:
- accuracy: Are facts correct and verifiable?
- completeness: Are all required outputs present?
- actionability: Can the user act on this?
- relevance: Is it relevant to the inputs?
- clarity: Is it clear and well-structured?
- brand_voice: Is the tone professional and appropriate?

## Response Format (JSON)
```json
{{
  "overall_score": 0.85,
  "dimensions": {{
    "accuracy": 0.9,
    "completeness": 0.85,
    "actionability": 0.8,
    "relevance": 0.9,
    "clarity": 0.85,
    "brand_voice": 0.8
  }},
  "passed": true,
  "issues": ["minor issue 1"],
  "feedback": "Brief feedback on output quality"
}}
```

Respond with ONLY the JSON."""

    def _get_evaluator_system_prompt(self) -> str:
        """System prompt for evaluator."""
        return """You are an MH1 quality evaluator.

Your job:
1. Evaluate skill outputs against quality dimensions
2. Be consistent and objective
3. Provide actionable feedback
4. Score conservatively - don't inflate

Scoring guide:
- 0.9-1.0: Excellent, ready for delivery
- 0.8-0.9: Good, minor improvements possible
- 0.7-0.8: Acceptable, could use refinement
- 0.6-0.7: Below standard, needs work
- Below 0.6: Unacceptable, major issues

Respond with ONLY valid JSON."""

    def _parse_evaluation(self, response: str) -> EvaluationResult:
        """Parse evaluation response."""
        try:
            # Extract JSON
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end]
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                response = response[start:end]

            data = json.loads(response.strip())

            score = float(data.get("overall_score", 0.5))
            dimensions = data.get("dimensions", {d: 0.5 for d in self.DIMENSIONS})
            passed = data.get("passed", score >= self.REFINE_THRESHOLD)
            issues = data.get("issues", [])
            feedback = data.get("feedback", "")

            # Determine release decision
            if score >= self.AUTO_DELIVER_THRESHOLD:
                release_decision = "auto_deliver"
            elif score >= self.REFINE_THRESHOLD:
                release_decision = "refine"
            elif score >= self.REVIEW_THRESHOLD:
                release_decision = "human_review"
            else:
                release_decision = "blocked"

            return EvaluationResult(
                score=score,
                passed=passed,
                dimensions=dimensions,
                feedback=feedback,
                issues=issues,
                release_decision=release_decision
            )

        except Exception as e:
            return EvaluationResult(
                score=0.5,
                passed=False,
                dimensions={d: 0.5 for d in self.DIMENSIONS},
                feedback=f"Failed to parse evaluation: {e}",
                issues=["parse_error"],
                release_decision="human_review"
            )

    def get_specialized_evaluator(self, skill_name: str) -> Optional[str]:
        """Get specialized evaluator agent for a skill."""
        # Map skills to specialized evaluators
        skill_evaluators = {
            "ghostwrite-linkedin-post": "linkedin-qa-reviewer",
            "linkedin-content-creation": "linkedin-qa-reviewer",
        }
        return skill_evaluators.get(skill_name)


def evaluate_output(
    skill_name: str,
    output: Dict[str, Any],
    inputs: Dict[str, Any] = None,
    client_id: str = None,
    quick: bool = False,
) -> EvaluationResult:
    """
    Convenience function to evaluate skill output.

    Args:
        skill_name: Name of the skill
        output: Output to evaluate
        inputs: Original inputs
        client_id: Client ID for context
        quick: Use quick evaluation

    Returns:
        EvaluationResult
    """
    evaluator = OutputEvaluator(client_id)
    return evaluator.evaluate(skill_name, output, inputs, quick=quick)
