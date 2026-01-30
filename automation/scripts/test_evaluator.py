#!/usr/bin/env python3
"""
Test script for lib/evaluator.py and lib/release_policy.py

Tests:
1. Evaluator 6-dimension framework
2. Release policy determination
3. Threshold behavior
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from lib.evaluator import Evaluator, evaluate_output, SRACScore, SRACEvaluator
from lib.release_policy import (
    ReleaseAction,
    determine_release_action,
    get_release_action_message,
    get_release_reason
)


class TestResults:
    def __init__(self):
        self.tests = []
        self.evaluator_dimensions = []
        self.release_policies = []

    def add_test(self, name: str, passed: bool, details: str = ""):
        self.tests.append({
            "name": name,
            "passed": passed,
            "details": details
        })

    def to_dict(self):
        passed = sum(1 for t in self.tests if t["passed"])
        failed = len(self.tests) - passed
        return {
            "timestamp": datetime.now().isoformat(),
            "evaluator_dimensions_found": self.evaluator_dimensions,
            "release_policies_found": self.release_policies,
            "tests_run": self.tests,
            "summary": {
                "total": len(self.tests),
                "passed": passed,
                "failed": failed
            },
            "production_ready": failed == 0
        }


def test_evaluator_dimensions(results: TestResults):
    """Test that all 6 dimensions are present with correct weights."""
    print("\n=== Testing Evaluator Dimensions ===")

    expected_dimensions = {
        "schema_validity": 0.18,
        "factuality": 0.23,
        "completeness": 0.18,
        "brand_voice": 0.13,
        "risk_flags": 0.18,
        "context_efficiency": 0.10
    }

    evaluator = Evaluator()

    # Check all dimensions exist
    for dim, expected_weight in expected_dimensions.items():
        actual_weight = evaluator.WEIGHTS.get(dim)
        if actual_weight is None:
            results.add_test(
                f"dimension_{dim}_exists",
                False,
                f"Dimension {dim} not found in evaluator"
            )
            print(f"  FAIL: Dimension {dim} not found")
        elif abs(actual_weight - expected_weight) > 0.001:
            results.add_test(
                f"dimension_{dim}_weight",
                False,
                f"Weight mismatch: expected {expected_weight}, got {actual_weight}"
            )
            print(f"  FAIL: {dim} weight mismatch: expected {expected_weight}, got {actual_weight}")
        else:
            results.add_test(
                f"dimension_{dim}",
                True,
                f"Weight: {actual_weight}"
            )
            print(f"  PASS: {dim} = {actual_weight}")
            results.evaluator_dimensions.append(dim)

    # Verify weights sum to 1.0
    total_weight = sum(evaluator.WEIGHTS.values())
    if abs(total_weight - 1.0) < 0.001:
        results.add_test("weights_sum_to_1", True, f"Total: {total_weight}")
        print(f"  PASS: Weights sum to {total_weight}")
    else:
        results.add_test("weights_sum_to_1", False, f"Total: {total_weight}")
        print(f"  FAIL: Weights sum to {total_weight}, expected 1.0")


def test_release_policies(results: TestResults):
    """Test that all 4 release policies exist."""
    print("\n=== Testing Release Policies ===")

    expected_policies = ["auto_deliver", "auto_refine", "human_review", "blocked"]

    for policy_name in expected_policies:
        try:
            policy = ReleaseAction(policy_name)
            results.add_test(
                f"policy_{policy_name}_exists",
                True,
                f"Value: {policy.value}"
            )
            results.release_policies.append(policy_name)
            print(f"  PASS: {policy_name} exists")
        except ValueError:
            results.add_test(
                f"policy_{policy_name}_exists",
                False,
                f"Policy {policy_name} not found"
            )
            print(f"  FAIL: {policy_name} not found")

    # Test message functions
    for action in ReleaseAction:
        msg = get_release_action_message(action)
        if msg and msg != "Unknown action":
            results.add_test(
                f"policy_{action.value}_has_message",
                True,
                msg[:50]
            )
            print(f"  PASS: {action.value} message: {msg[:50]}...")
        else:
            results.add_test(
                f"policy_{action.value}_has_message",
                False,
                "No message defined"
            )
            print(f"  FAIL: {action.value} has no message")


def test_evaluation_scoring(results: TestResults):
    """Test evaluation with sample outputs."""
    print("\n=== Testing Evaluation Scoring ===")

    # Test 1: High-quality output (should pass)
    good_output = {
        "summary": "Email performance improved 15% this quarter according to HubSpot data.",
        "recommendations": [
            "Increase send frequency to 2x per week",
            "Test subject lines with A/B testing"
        ],
        "metrics": {
            "open_rate": 0.42,
            "click_rate": 0.08
        }
    }

    good_schema = {
        "required": ["summary", "recommendations"],
        "properties": {
            "summary": {"type": "string"},
            "recommendations": {"type": "array"},
            "metrics": {"type": "object"}
        }
    }

    result = evaluate_output(good_output, schema=good_schema)
    passed = result.get("pass", False)
    score = result.get("score", 0)

    results.add_test(
        "good_output_passes",
        passed,
        f"Score: {score}"
    )
    print(f"  {'PASS' if passed else 'FAIL'}: Good output - score {score}, passed={passed}")

    # Test 2: Output with placeholders (should fail completeness)
    placeholder_output = {
        "summary": "Revenue improved [INSERT PERCENTAGE HERE]",
        "recommendations": ["TODO: Add recommendations"]
    }

    result = evaluate_output(placeholder_output, schema=good_schema)
    has_completeness_issues = any(
        issue.get("dimension") == "completeness"
        for issue in result.get("issues", [])
    )

    results.add_test(
        "placeholder_detected",
        has_completeness_issues,
        f"Issues: {len(result.get('issues', []))}"
    )
    print(f"  {'PASS' if has_completeness_issues else 'FAIL'}: Placeholder detection - issues found={has_completeness_issues}")

    # Test 3: Output missing required fields (should fail schema)
    missing_fields_output = {
        "summary": "Only has summary, missing recommendations"
    }

    result = evaluate_output(missing_fields_output, schema=good_schema)
    has_schema_issues = any(
        issue.get("dimension") == "schema_validity"
        for issue in result.get("issues", [])
    )

    results.add_test(
        "missing_fields_detected",
        has_schema_issues,
        f"Schema issues: {has_schema_issues}"
    )
    print(f"  {'PASS' if has_schema_issues else 'FAIL'}: Missing fields detection - schema issues={has_schema_issues}")

    # Test 4: Output with unsourced claims (should lower factuality)
    unsourced_output = {
        "summary": "Revenue increased by 45% and conversion improved 23%. Click rates grew 15%.",
        "recommendations": ["Increase budget by $50,000"]
    }

    result = evaluate_output(unsourced_output, schema=good_schema)
    factuality_score = result.get("breakdown", {}).get("factuality", 1.0)

    factuality_lowered = factuality_score < 1.0
    results.add_test(
        "unsourced_claims_detected",
        factuality_lowered,
        f"Factuality score: {factuality_score}"
    )
    print(f"  {'PASS' if factuality_lowered else 'FAIL'}: Unsourced claims - factuality={factuality_score}")

    # Test 5: Context efficiency with large inline input
    large_input_telemetry = {
        "context_handling": {
            "input_size_tokens": 50000,
            "strategy": "inline",  # Should be chunked for large inputs
            "sub_calls": []
        }
    }

    result = evaluate_output(good_output, telemetry=large_input_telemetry)
    context_efficiency = result.get("breakdown", {}).get("context_efficiency", 1.0)

    efficiency_penalized = context_efficiency < 1.0
    results.add_test(
        "large_inline_penalized",
        efficiency_penalized,
        f"Context efficiency: {context_efficiency}"
    )
    print(f"  {'PASS' if efficiency_penalized else 'FAIL'}: Large inline context - efficiency={context_efficiency}")


def test_release_policy_determination(results: TestResults):
    """Test release policy determination based on scores."""
    print("\n=== Testing Release Policy Determination ===")

    # Test 1: High score -> AUTO_DELIVER
    high_score_eval = {
        "score": 0.92,
        "pass": True,
        "issues": [],
        "suggestions": []
    }

    action = determine_release_action(high_score_eval)
    is_auto_deliver = action == ReleaseAction.AUTO_DELIVER

    results.add_test(
        "high_score_auto_deliver",
        is_auto_deliver,
        f"Action: {action.value}"
    )
    print(f"  {'PASS' if is_auto_deliver else 'FAIL'}: High score (0.92) -> {action.value}")

    # Test 2: Low score -> HUMAN_REVIEW
    low_score_eval = {
        "score": 0.65,
        "pass": False,
        "issues": [{"severity": "medium", "description": "Issues found"}],
        "suggestions": ["Fix issues"]
    }

    action = determine_release_action(low_score_eval)
    is_human_review = action == ReleaseAction.HUMAN_REVIEW

    results.add_test(
        "low_score_human_review",
        is_human_review,
        f"Action: {action.value}"
    )
    print(f"  {'PASS' if is_human_review else 'FAIL'}: Low score (0.65) -> {action.value}")

    # Test 3: Medium score with suggestions -> AUTO_REFINE
    medium_score_eval = {
        "score": 0.75,
        "pass": False,
        "issues": [{"severity": "medium", "description": "Minor issues"}],
        "suggestions": ["Add more sources", "Improve clarity"]
    }

    action = determine_release_action(medium_score_eval)
    is_auto_refine = action == ReleaseAction.AUTO_REFINE

    results.add_test(
        "medium_score_auto_refine",
        is_auto_refine,
        f"Action: {action.value}"
    )
    print(f"  {'PASS' if is_auto_refine else 'FAIL'}: Medium score (0.75) with suggestions -> {action.value}")

    # Test 4: Critical issues -> BLOCKED
    critical_eval = {
        "score": 0.85,
        "pass": False,
        "issues": [{"severity": "critical", "description": "Sensitive data exposed"}],
        "suggestions": []
    }

    action = determine_release_action(critical_eval)
    is_blocked = action == ReleaseAction.BLOCKED

    results.add_test(
        "critical_issues_blocked",
        is_blocked,
        f"Action: {action.value}"
    )
    print(f"  {'PASS' if is_blocked else 'FAIL'}: Critical issues -> {action.value}")

    # Test 5: AI washing high severity -> BLOCKED
    with_ai_washing = {
        "score": 0.90,
        "pass": True,
        "issues": [],
        "suggestions": []
    }
    ai_washing_eval = {
        "overall": {
            "highest_severity": "high",
            "warning_count": 3
        }
    }

    action = determine_release_action(with_ai_washing, ai_washing_eval=ai_washing_eval)
    is_blocked = action == ReleaseAction.BLOCKED

    results.add_test(
        "ai_washing_high_blocked",
        is_blocked,
        f"Action: {action.value}"
    )
    print(f"  {'PASS' if is_blocked else 'FAIL'}: High AI washing -> {action.value}")


def test_threshold_behavior(results: TestResults):
    """Test threshold boundary conditions."""
    print("\n=== Testing Threshold Behavior ===")

    evaluator = Evaluator()

    # Test PASS_THRESHOLD (0.8)
    results.add_test(
        "pass_threshold_is_0.8",
        evaluator.PASS_THRESHOLD == 0.8,
        f"Value: {evaluator.PASS_THRESHOLD}"
    )
    print(f"  {'PASS' if evaluator.PASS_THRESHOLD == 0.8 else 'FAIL'}: PASS_THRESHOLD = {evaluator.PASS_THRESHOLD}")

    # Test MIN_PER_DIMENSION (0.6)
    results.add_test(
        "min_per_dimension_is_0.6",
        evaluator.MIN_PER_DIMENSION == 0.6,
        f"Value: {evaluator.MIN_PER_DIMENSION}"
    )
    print(f"  {'PASS' if evaluator.MIN_PER_DIMENSION == 0.6 else 'FAIL'}: MIN_PER_DIMENSION = {evaluator.MIN_PER_DIMENSION}")

    # Test INLINE_THRESHOLD (8000)
    results.add_test(
        "inline_threshold_is_8000",
        evaluator.INLINE_THRESHOLD == 8000,
        f"Value: {evaluator.INLINE_THRESHOLD}"
    )
    print(f"  {'PASS' if evaluator.INLINE_THRESHOLD == 8000 else 'FAIL'}: INLINE_THRESHOLD = {evaluator.INLINE_THRESHOLD}")

    # Test score exactly at 0.7 threshold
    at_threshold_eval = {
        "score": 0.70,
        "pass": False,
        "issues": [],
        "suggestions": ["Some suggestion"]
    }

    action = determine_release_action(at_threshold_eval)
    # At 0.70 exactly, should be AUTO_REFINE (>= 0.7 passes the low score check)
    is_auto_refine = action == ReleaseAction.AUTO_REFINE

    results.add_test(
        "score_at_0.7_not_human_review",
        is_auto_refine,
        f"Score 0.70 -> {action.value}"
    )
    print(f"  {'PASS' if is_auto_refine else 'FAIL'}: Score exactly 0.70 -> {action.value}")

    # Test score just below 0.7 threshold
    below_threshold_eval = {
        "score": 0.69,
        "pass": False,
        "issues": [],
        "suggestions": []
    }

    action = determine_release_action(below_threshold_eval)
    is_human_review = action == ReleaseAction.HUMAN_REVIEW

    results.add_test(
        "score_below_0.7_human_review",
        is_human_review,
        f"Score 0.69 -> {action.value}"
    )
    print(f"  {'PASS' if is_human_review else 'FAIL'}: Score 0.69 -> {action.value}")


def test_srac_framework(results: TestResults):
    """Test SRAC evaluation framework exists."""
    print("\n=== Testing SRAC Framework ===")

    # Test SRACScore dataclass
    try:
        score = SRACScore(
            specificity=4.0,
            relevance=4.5,
            actionability=4.2,
            concision=3.8
        )

        # Test weighted score calculation
        expected = (4.0 * 0.25) + (4.5 * 0.25) + (4.2 * 0.30) + (3.8 * 0.20)
        actual = score.weighted_score

        score_correct = abs(actual - expected) < 0.001
        results.add_test(
            "srac_weighted_score",
            score_correct,
            f"Expected: {expected:.3f}, Actual: {actual:.3f}"
        )
        print(f"  {'PASS' if score_correct else 'FAIL'}: SRAC weighted score = {actual:.3f}")

        # Test pass threshold (3.5)
        passes = score.passed
        should_pass = actual >= 3.5

        results.add_test(
            "srac_pass_threshold",
            passes == should_pass,
            f"Score: {actual:.3f}, Passes: {passes}"
        )
        print(f"  {'PASS' if passes == should_pass else 'FAIL'}: SRAC pass threshold (3.5) - passes={passes}")

    except Exception as e:
        results.add_test("srac_framework_exists", False, str(e))
        print(f"  FAIL: SRAC framework error: {e}")


def test_get_release_reason(results: TestResults):
    """Test get_release_reason function."""
    print("\n=== Testing Release Reason Messages ===")

    # Test BLOCKED reason
    blocked_eval = {
        "score": 0.5,
        "issues": [{"severity": "critical", "message": "Data breach detected"}]
    }
    reason = get_release_reason(ReleaseAction.BLOCKED, blocked_eval)
    has_reason = len(reason) > 0

    results.add_test(
        "blocked_has_reason",
        has_reason,
        reason[:50] if reason else "No reason"
    )
    print(f"  {'PASS' if has_reason else 'FAIL'}: BLOCKED reason: {reason[:50]}...")

    # Test AUTO_DELIVER reason
    good_eval = {
        "score": 0.92,
        "issues": []
    }
    reason = get_release_reason(ReleaseAction.AUTO_DELIVER, good_eval)
    includes_score = "0.92" in reason

    results.add_test(
        "auto_deliver_includes_score",
        includes_score,
        reason
    )
    print(f"  {'PASS' if includes_score else 'FAIL'}: AUTO_DELIVER reason: {reason}")


def main():
    print("=" * 60)
    print("MH1 Evaluator & Release Policy Test Suite")
    print("=" * 60)

    results = TestResults()

    # Run all tests
    test_evaluator_dimensions(results)
    test_release_policies(results)
    test_evaluation_scoring(results)
    test_release_policy_determination(results)
    test_threshold_behavior(results)
    test_srac_framework(results)
    test_get_release_reason(results)

    # Generate output
    output = results.to_dict()

    # Write to telemetry
    telemetry_path = PROJECT_ROOT / "telemetry" / "evaluator_test.json"
    with open(telemetry_path, "w") as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests: {output['summary']['total']}")
    print(f"Passed: {output['summary']['passed']}")
    print(f"Failed: {output['summary']['failed']}")
    print(f"Production ready: {output['production_ready']}")
    print(f"\nResults written to: {telemetry_path}")

    # Return exit code based on results
    return 0 if output["production_ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
