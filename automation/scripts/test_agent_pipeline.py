#!/usr/bin/env python3
"""
MH1 Agent Pipeline Test Suite

Tests the complete agent->skill->output pipeline:
1. Skill definition loading and parsing
2. Input validation against schema
3. Execution flow simulation
4. Output validation against schema
5. Evaluator quality gates
6. Release policy decisions

Outputs results to telemetry/agent_pipeline_test.json
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple

# Add lib to path
SYSTEM_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SYSTEM_ROOT))

from lib.runner import (
    SkillRunner,
    WorkflowRunner,
    ContextManager,
    ContextConfig,
    ContextStrategy,
    RunStatus,
    estimate_tokens,
    get_model_for_task,
    get_model_for_subtask,
    should_offload_context,
    ModelCapacityRouter,
    RetrievalStrategyRouter
)
from lib.evaluator import Evaluator, evaluate_output, SRACEvaluator, SRACScore
from lib.release_policy import determine_release_action, ReleaseAction, get_release_action_message


@dataclass
class TestResult:
    """Result of a single test."""
    test_name: str
    passed: bool
    duration_ms: float
    message: str
    details: Optional[Dict] = None
    error: Optional[str] = None


@dataclass
class TestSuiteResult:
    """Result of the entire test suite."""
    suite_name: str
    timestamp: str
    total_tests: int
    passed: int
    failed: int
    duration_seconds: float
    tests: List[Dict]
    summary: Dict


class AgentPipelineTester:
    """Tests the complete agent execution pipeline."""

    def __init__(self):
        self.results: List[TestResult] = []
        self.skills_dir = SYSTEM_ROOT / "skills"
        self.schemas_dir = SYSTEM_ROOT / "schemas"

    def run_all_tests(self) -> TestSuiteResult:
        """Run all pipeline tests."""
        start_time = time.time()

        # Test groups
        self._test_skill_loading()
        self._test_input_validation()
        self._test_execution_flow()
        self._test_output_validation()
        self._test_evaluator()
        self._test_release_policy()
        self._test_context_manager()
        self._test_model_routing()
        self._test_workflow_runner()

        duration = time.time() - start_time
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed

        return TestSuiteResult(
            suite_name="agent_pipeline",
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_tests=len(self.results),
            passed=passed,
            failed=failed,
            duration_seconds=round(duration, 2),
            tests=[asdict(r) for r in self.results],
            summary={
                "pass_rate": round(passed / len(self.results) * 100, 1) if self.results else 0,
                "skill_loading": self._get_group_summary("skill_loading"),
                "input_validation": self._get_group_summary("input_validation"),
                "execution_flow": self._get_group_summary("execution_flow"),
                "output_validation": self._get_group_summary("output_validation"),
                "evaluator": self._get_group_summary("evaluator"),
                "release_policy": self._get_group_summary("release_policy"),
                "context_manager": self._get_group_summary("context_manager"),
                "model_routing": self._get_group_summary("model_routing"),
                "workflow_runner": self._get_group_summary("workflow_runner")
            }
        )

    def _get_group_summary(self, prefix: str) -> Dict:
        """Get summary for a test group."""
        group_tests = [r for r in self.results if r.test_name.startswith(prefix)]
        if not group_tests:
            return {"total": 0, "passed": 0, "failed": 0}
        passed = sum(1 for r in group_tests if r.passed)
        return {
            "total": len(group_tests),
            "passed": passed,
            "failed": len(group_tests) - passed
        }

    def _add_result(self, name: str, passed: bool, message: str,
                    duration_ms: float, details: Dict = None, error: str = None):
        """Add a test result."""
        self.results.append(TestResult(
            test_name=name,
            passed=passed,
            duration_ms=round(duration_ms, 2),
            message=message,
            details=details,
            error=error
        ))

    # =========================================================================
    # Test Group: Skill Loading
    # =========================================================================

    def _test_skill_loading(self):
        """Test skill definition loading and parsing."""

        # Test 1: Load lifecycle-audit skill
        start = time.time()
        try:
            skill_path = self.skills_dir / "lifecycle-audit" / "SKILL.md"
            if skill_path.exists():
                content = skill_path.read_text()
                has_frontmatter = content.startswith("---")
                has_name = "name:" in content or "lifecycle-audit" in content
                passed = has_frontmatter and has_name
                self._add_result(
                    "skill_loading_lifecycle_audit",
                    passed,
                    "Loaded lifecycle-audit skill definition" if passed else "Missing frontmatter or name",
                    (time.time() - start) * 1000,
                    {"path": str(skill_path), "size_bytes": len(content)}
                )
            else:
                self._add_result(
                    "skill_loading_lifecycle_audit",
                    False,
                    "Skill file not found",
                    (time.time() - start) * 1000,
                    error=f"Path does not exist: {skill_path}"
                )
        except Exception as e:
            self._add_result(
                "skill_loading_lifecycle_audit",
                False,
                "Failed to load skill",
                (time.time() - start) * 1000,
                error=str(e)
            )

        # Test 2: Load at-risk-detection skill
        start = time.time()
        try:
            skill_path = self.skills_dir / "at-risk-detection" / "SKILL.md"
            if skill_path.exists():
                content = skill_path.read_text()
                has_version = 'version:' in content
                has_compatibility = 'compatibility:' in content
                passed = has_version and has_compatibility
                self._add_result(
                    "skill_loading_at_risk_detection",
                    passed,
                    "Loaded at-risk-detection with metadata" if passed else "Missing version or compatibility",
                    (time.time() - start) * 1000,
                    {"has_version": has_version, "has_compatibility": has_compatibility}
                )
            else:
                self._add_result(
                    "skill_loading_at_risk_detection",
                    False,
                    "Skill file not found",
                    (time.time() - start) * 1000
                )
        except Exception as e:
            self._add_result(
                "skill_loading_at_risk_detection",
                False,
                "Failed to load skill",
                (time.time() - start) * 1000,
                error=str(e)
            )

        # Test 3: Count available skills
        start = time.time()
        try:
            skill_count = 0
            for skill_dir in self.skills_dir.iterdir():
                if skill_dir.is_dir() and not skill_dir.name.startswith('_'):
                    skill_file = skill_dir / "SKILL.md"
                    if skill_file.exists():
                        skill_count += 1
            passed = skill_count > 10  # Expect at least 10 skills
            self._add_result(
                "skill_loading_count_skills",
                passed,
                f"Found {skill_count} skill definitions",
                (time.time() - start) * 1000,
                {"skill_count": skill_count}
            )
        except Exception as e:
            self._add_result(
                "skill_loading_count_skills",
                False,
                "Failed to count skills",
                (time.time() - start) * 1000,
                error=str(e)
            )

    # =========================================================================
    # Test Group: Input Validation
    # =========================================================================

    def _test_input_validation(self):
        """Test input validation against schema."""

        # Test 1: Valid input passes validation
        start = time.time()
        try:
            runner = SkillRunner("lifecycle-audit")
            schema = runner.load_schema("input")

            valid_input = {
                "tenant_id": "test-tenant",
                "limit": 50,
                "execution_mode": "suggest"
            }

            is_valid, errors = runner.validate(valid_input, schema)
            self._add_result(
                "input_validation_valid_passes",
                is_valid,
                "Valid input passed validation" if is_valid else f"Validation failed: {errors}",
                (time.time() - start) * 1000,
                {"input": valid_input, "errors": errors}
            )
        except Exception as e:
            self._add_result(
                "input_validation_valid_passes",
                False,
                "Exception during validation",
                (time.time() - start) * 1000,
                error=str(e)
            )

        # Test 2: Invalid input (wrong type) fails validation
        start = time.time()
        try:
            runner = SkillRunner("lifecycle-audit")
            schema = runner.load_schema("input")

            if schema:
                # Add a required field check if schema has required
                schema_copy = schema.copy()
                schema_copy["required"] = ["tenant_id"]

                invalid_input = {
                    "limit": "not_a_number"  # Should be integer, missing tenant_id
                }

                is_valid, errors = runner.validate(invalid_input, schema_copy)
                # We expect validation to fail
                passed = not is_valid or len(errors) > 0
                self._add_result(
                    "input_validation_invalid_fails",
                    passed,
                    "Invalid input correctly rejected" if passed else "Invalid input incorrectly accepted",
                    (time.time() - start) * 1000,
                    {"input": invalid_input, "errors": errors, "is_valid": is_valid}
                )
            else:
                self._add_result(
                    "input_validation_invalid_fails",
                    True,
                    "No schema to validate against (passes by default)",
                    (time.time() - start) * 1000
                )
        except Exception as e:
            self._add_result(
                "input_validation_invalid_fails",
                False,
                "Exception during validation",
                (time.time() - start) * 1000,
                error=str(e)
            )

        # Test 3: Schema loading for skill without schema
        start = time.time()
        try:
            runner = SkillRunner("brand-voice")
            schema = runner.load_schema("input")
            # Should return None if no schema exists
            passed = schema is None or isinstance(schema, dict)
            self._add_result(
                "input_validation_no_schema_handling",
                passed,
                "Skill without schema handled correctly",
                (time.time() - start) * 1000,
                {"schema": schema}
            )
        except Exception as e:
            self._add_result(
                "input_validation_no_schema_handling",
                False,
                "Exception handling missing schema",
                (time.time() - start) * 1000,
                error=str(e)
            )

    # =========================================================================
    # Test Group: Execution Flow
    # =========================================================================

    def _test_execution_flow(self):
        """Test skill execution flow simulation."""

        # Test 1: SkillRunner basic execution
        start = time.time()
        try:
            runner = SkillRunner("test-skill", version="v1.0.0", tenant_id="test-tenant")

            def mock_executor(inputs):
                return {
                    "output": {"result": "success", "data": [1, 2, 3]},
                    "tokens_input": 100,
                    "tokens_output": 50
                }

            result = runner.run({"test": "input"}, mock_executor)

            passed = (
                result.get("status") == "success" and
                result.get("output") is not None and
                result.get("tokens_input") == 100
            )
            self._add_result(
                "execution_flow_skill_runner_basic",
                passed,
                "SkillRunner executed successfully" if passed else "SkillRunner execution failed",
                (time.time() - start) * 1000,
                {"result_status": result.get("status"), "has_output": result.get("output") is not None}
            )
        except Exception as e:
            self._add_result(
                "execution_flow_skill_runner_basic",
                False,
                "Exception during execution",
                (time.time() - start) * 1000,
                error=str(e)
            )

        # Test 2: SkillRunner with validation failure
        start = time.time()
        try:
            runner = SkillRunner("lifecycle-audit", version="v2.0.0")

            # Force a schema that requires fields
            original_load = runner.load_schema
            def mock_schema(schema_type):
                if schema_type == "input":
                    return {
                        "required": ["mandatory_field"],
                        "properties": {"mandatory_field": {"type": "string"}}
                    }
                return original_load(schema_type)
            runner.load_schema = mock_schema

            def mock_executor(inputs):
                return {"output": {}, "tokens_input": 10, "tokens_output": 5}

            result = runner.run({}, mock_executor)  # Missing mandatory_field

            passed = result.get("status") == "failed" and "validation" in result.get("error", "").lower()
            self._add_result(
                "execution_flow_validation_failure",
                passed,
                "Validation failure handled correctly" if passed else "Validation failure not caught",
                (time.time() - start) * 1000,
                {"result_status": result.get("status"), "error": result.get("error")}
            )
        except Exception as e:
            self._add_result(
                "execution_flow_validation_failure",
                False,
                "Exception during validation failure test",
                (time.time() - start) * 1000,
                error=str(e)
            )

        # Test 3: SkillRunner executor exception handling
        start = time.time()
        try:
            runner = SkillRunner("test-skill", tenant_id="test-tenant")

            def failing_executor(inputs):
                raise ValueError("Simulated execution failure")

            result = runner.run({"test": "input"}, failing_executor)

            passed = result.get("status") == "failed" and "Simulated" in result.get("error", "")
            self._add_result(
                "execution_flow_exception_handling",
                passed,
                "Executor exception handled correctly" if passed else "Exception not caught properly",
                (time.time() - start) * 1000,
                {"result_status": result.get("status"), "error": result.get("error")}
            )
        except Exception as e:
            # Should not reach here - exception should be caught
            self._add_result(
                "execution_flow_exception_handling",
                False,
                "Uncaught exception propagated",
                (time.time() - start) * 1000,
                error=str(e)
            )

    # =========================================================================
    # Test Group: Output Validation
    # =========================================================================

    def _test_output_validation(self):
        """Test output validation against schema."""

        # Test 1: Valid lifecycle-audit output
        start = time.time()
        try:
            runner = SkillRunner("lifecycle-audit")
            schema = runner.load_schema("output")

            valid_output = {
                "summary": {
                    "total_accounts": 100,
                    "by_stage": {"lead": 50, "customer": 50},
                    "health_score": 0.75
                },
                "recommendations": [
                    {"priority": "high", "action": "Increase email frequency"}
                ],
                "_meta": {
                    "tenant_id": "test",
                    "run_id": "abc123",
                    "execution_mode": "suggest",
                    "runtime_seconds": 5.2,
                    "cost_usd": 0.05,
                    "release_action": "auto_deliver"
                }
            }

            is_valid, errors = runner.validate(valid_output, schema)
            self._add_result(
                "output_validation_valid_output",
                is_valid,
                "Valid output passed validation" if is_valid else f"Validation failed: {errors}",
                (time.time() - start) * 1000,
                {"errors": errors}
            )
        except Exception as e:
            self._add_result(
                "output_validation_valid_output",
                False,
                "Exception during output validation",
                (time.time() - start) * 1000,
                error=str(e)
            )

        # Test 2: Output missing required fields
        start = time.time()
        try:
            runner = SkillRunner("lifecycle-audit")
            schema = runner.load_schema("output")

            if schema and "required" in schema:
                incomplete_output = {
                    "summary": {"total_accounts": 10}
                    # Missing "recommendations" and "_meta"
                }

                is_valid, errors = runner.validate(incomplete_output, schema)
                passed = not is_valid or len(errors) > 0
                self._add_result(
                    "output_validation_missing_required",
                    passed,
                    "Incomplete output correctly rejected" if passed else "Missing fields not caught",
                    (time.time() - start) * 1000,
                    {"is_valid": is_valid, "errors": errors}
                )
            else:
                self._add_result(
                    "output_validation_missing_required",
                    True,
                    "No required fields in schema",
                    (time.time() - start) * 1000
                )
        except Exception as e:
            self._add_result(
                "output_validation_missing_required",
                False,
                "Exception during validation",
                (time.time() - start) * 1000,
                error=str(e)
            )

    # =========================================================================
    # Test Group: Evaluator
    # =========================================================================

    def _test_evaluator(self):
        """Test the evaluator quality gates."""

        # Test 1: High-quality output passes
        start = time.time()
        try:
            good_output = {
                "summary": "Email performance improved 15% according to HubSpot data.",
                "recommendations": [
                    "Increase send frequency to 2x per week",
                    "Test subject lines with A/B testing"
                ],
                "metrics": {
                    "open_rate": 0.42,
                    "click_rate": 0.08
                }
            }

            schema = {
                "required": ["summary", "recommendations"],
                "properties": {
                    "summary": {"type": "string"},
                    "recommendations": {"type": "array"}
                }
            }

            result = evaluate_output(good_output, schema=schema)

            passed = result.get("pass", False) and result.get("score", 0) >= 0.8
            self._add_result(
                "evaluator_high_quality_passes",
                passed,
                f"High-quality output scored {result.get('score', 0):.2f}" if passed else "High-quality output failed",
                (time.time() - start) * 1000,
                {"score": result.get("score"), "breakdown": result.get("breakdown")}
            )
        except Exception as e:
            self._add_result(
                "evaluator_high_quality_passes",
                False,
                "Exception during evaluation",
                (time.time() - start) * 1000,
                error=str(e)
            )

        # Test 2: Output with placeholders fails completeness
        start = time.time()
        try:
            placeholder_output = {
                "summary": "Results show [TODO: add metrics] improvement.",
                "recommendations": ["TBD - pending analysis"]
            }

            result = evaluate_output(placeholder_output)

            # Should have completeness issues
            completeness = result.get("breakdown", {}).get("completeness", 1.0)
            has_issues = any(
                i.get("dimension") == "completeness"
                for i in result.get("issues", [])
            )
            passed = completeness < 1.0 or has_issues
            self._add_result(
                "evaluator_placeholder_detected",
                passed,
                "Placeholder text detected" if passed else "Placeholders not caught",
                (time.time() - start) * 1000,
                {"completeness_score": completeness, "issues": result.get("issues")}
            )
        except Exception as e:
            self._add_result(
                "evaluator_placeholder_detected",
                False,
                "Exception during evaluation",
                (time.time() - start) * 1000,
                error=str(e)
            )

        # Test 3: Risk flags for absolute claims
        start = time.time()
        try:
            risky_output = {
                "summary": "This approach always works. Everyone should use it. It is guaranteed to succeed."
            }

            result = evaluate_output(risky_output)

            risk_score = result.get("breakdown", {}).get("risk_flags", 1.0)
            has_risk_issues = any(
                i.get("dimension") == "risk_flags"
                for i in result.get("issues", [])
            )
            passed = risk_score < 1.0 or has_risk_issues
            self._add_result(
                "evaluator_risk_flags_detected",
                passed,
                "Risk flags detected for absolute claims" if passed else "Absolute claims not flagged",
                (time.time() - start) * 1000,
                {"risk_score": risk_score, "issues": result.get("issues")}
            )
        except Exception as e:
            self._add_result(
                "evaluator_risk_flags_detected",
                False,
                "Exception during evaluation",
                (time.time() - start) * 1000,
                error=str(e)
            )

        # Test 4: Context efficiency evaluation
        start = time.time()
        try:
            output = {"summary": "Analysis complete."}

            # Simulate telemetry with large inline context (inefficient)
            telemetry = {
                "context_handling": {
                    "strategy": "inline",
                    "input_size_tokens": 50000,  # Large input processed inline = bad
                    "chunks_processed": 0,
                    "sub_calls": []
                }
            }

            result = evaluate_output(output, telemetry=telemetry)

            efficiency_score = result.get("breakdown", {}).get("context_efficiency", 1.0)
            passed = efficiency_score < 1.0  # Should be penalized
            self._add_result(
                "evaluator_context_efficiency",
                passed,
                "Large inline context penalized" if passed else "Inefficient context not detected",
                (time.time() - start) * 1000,
                {"efficiency_score": efficiency_score}
            )
        except Exception as e:
            self._add_result(
                "evaluator_context_efficiency",
                False,
                "Exception during evaluation",
                (time.time() - start) * 1000,
                error=str(e)
            )

    # =========================================================================
    # Test Group: Release Policy
    # =========================================================================

    def _test_release_policy(self):
        """Test release policy decisions."""

        # Test 1: Auto-deliver for high score
        start = time.time()
        try:
            eval_result = {
                "score": 0.92,
                "pass": True,
                "issues": [],
                "suggestions": []
            }

            action = determine_release_action(eval_result)
            passed = action == ReleaseAction.AUTO_DELIVER
            self._add_result(
                "release_policy_auto_deliver",
                passed,
                f"High score -> {action.value}" if passed else f"Expected AUTO_DELIVER, got {action.value}",
                (time.time() - start) * 1000,
                {"score": 0.92, "action": action.value}
            )
        except Exception as e:
            self._add_result(
                "release_policy_auto_deliver",
                False,
                "Exception in release policy",
                (time.time() - start) * 1000,
                error=str(e)
            )

        # Test 2: Human review for low score
        start = time.time()
        try:
            eval_result = {
                "score": 0.55,
                "pass": False,
                "issues": [{"severity": "high", "message": "Low quality"}],
                "suggestions": ["Improve content"]
            }

            action = determine_release_action(eval_result)
            passed = action == ReleaseAction.HUMAN_REVIEW
            self._add_result(
                "release_policy_human_review",
                passed,
                f"Low score -> {action.value}" if passed else f"Expected HUMAN_REVIEW, got {action.value}",
                (time.time() - start) * 1000,
                {"score": 0.55, "action": action.value}
            )
        except Exception as e:
            self._add_result(
                "release_policy_human_review",
                False,
                "Exception in release policy",
                (time.time() - start) * 1000,
                error=str(e)
            )

        # Test 3: Blocked for critical issues
        start = time.time()
        try:
            eval_result = {
                "score": 0.85,
                "pass": False,
                "issues": [{"severity": "critical", "message": "Security vulnerability"}],
                "suggestions": []
            }

            action = determine_release_action(eval_result)
            passed = action == ReleaseAction.BLOCKED
            self._add_result(
                "release_policy_blocked",
                passed,
                f"Critical issue -> {action.value}" if passed else f"Expected BLOCKED, got {action.value}",
                (time.time() - start) * 1000,
                {"action": action.value}
            )
        except Exception as e:
            self._add_result(
                "release_policy_blocked",
                False,
                "Exception in release policy",
                (time.time() - start) * 1000,
                error=str(e)
            )

        # Test 4: Auto-refine for fixable issues
        start = time.time()
        try:
            eval_result = {
                "score": 0.75,
                "pass": False,
                "issues": [{"severity": "medium", "message": "Minor issues"}],
                "suggestions": ["Fix formatting", "Add sources"]
            }

            action = determine_release_action(eval_result)
            passed = action == ReleaseAction.AUTO_REFINE
            self._add_result(
                "release_policy_auto_refine",
                passed,
                f"Fixable issues -> {action.value}" if passed else f"Expected AUTO_REFINE, got {action.value}",
                (time.time() - start) * 1000,
                {"score": 0.75, "action": action.value, "suggestions_count": 2}
            )
        except Exception as e:
            self._add_result(
                "release_policy_auto_refine",
                False,
                "Exception in release policy",
                (time.time() - start) * 1000,
                error=str(e)
            )

    # =========================================================================
    # Test Group: Context Manager
    # =========================================================================

    def _test_context_manager(self):
        """Test context manager for large input handling."""

        # Test 1: Small context is inline
        start = time.time()
        try:
            small_data = [{"id": i, "name": f"item_{i}"} for i in range(10)]
            ctx = ContextManager(small_data, ContextConfig(max_inline_tokens=8000))

            should_offload = ctx.should_offload()
            strategy = ctx.get_strategy()

            passed = not should_offload and strategy == ContextStrategy.INLINE
            self._add_result(
                "context_manager_small_inline",
                passed,
                f"Small context -> {strategy.value}" if passed else f"Expected INLINE, got {strategy.value}",
                (time.time() - start) * 1000,
                {"size_tokens": ctx.context_size, "strategy": strategy.value}
            )
        except Exception as e:
            self._add_result(
                "context_manager_small_inline",
                False,
                "Exception in context manager",
                (time.time() - start) * 1000,
                error=str(e)
            )

        # Test 2: Large context requires offload
        start = time.time()
        try:
            # Create large data (about 50K tokens worth)
            large_data = [{"id": i, "data": "x" * 500} for i in range(500)]
            ctx = ContextManager(large_data, ContextConfig(max_inline_tokens=8000))

            should_offload = ctx.should_offload()
            strategy = ctx.get_strategy()

            passed = should_offload and strategy in [ContextStrategy.CHUNKED, ContextStrategy.OFFLOADED]
            self._add_result(
                "context_manager_large_offload",
                passed,
                f"Large context -> {strategy.value}" if passed else f"Expected CHUNKED/OFFLOADED, got {strategy.value}",
                (time.time() - start) * 1000,
                {"size_tokens": ctx.context_size, "should_offload": should_offload}
            )
        except Exception as e:
            self._add_result(
                "context_manager_large_offload",
                False,
                "Exception in context manager",
                (time.time() - start) * 1000,
                error=str(e)
            )

        # Test 3: Chunking works correctly
        start = time.time()
        try:
            data = list(range(100))
            ctx = ContextManager(data, ContextConfig(chunk_size=25))

            chunks = list(ctx.chunk(size=25))

            passed = len(chunks) == 4 and all(len(c) == 25 for c in chunks)
            self._add_result(
                "context_manager_chunking",
                passed,
                f"Data chunked into {len(chunks)} chunks" if passed else f"Chunking failed: {len(chunks)} chunks",
                (time.time() - start) * 1000,
                {"chunk_count": len(chunks), "chunk_sizes": [len(c) for c in chunks]}
            )
        except Exception as e:
            self._add_result(
                "context_manager_chunking",
                False,
                "Exception during chunking",
                (time.time() - start) * 1000,
                error=str(e)
            )

        # Test 4: Buffer aggregation
        start = time.time()
        try:
            ctx = ContextManager([])

            ctx.aggregate_buffer("results", {"score": 0.8})
            ctx.aggregate_buffer("results", {"score": 0.9})
            ctx.aggregate_buffer("results", {"score": 0.85})

            aggregated = ctx.get_aggregated("results")

            passed = len(aggregated) == 3 and all("score" in r for r in aggregated)
            self._add_result(
                "context_manager_buffer_aggregation",
                passed,
                f"Aggregated {len(aggregated)} results" if passed else "Buffer aggregation failed",
                (time.time() - start) * 1000,
                {"buffer_size": len(aggregated)}
            )
        except Exception as e:
            self._add_result(
                "context_manager_buffer_aggregation",
                False,
                "Exception during aggregation",
                (time.time() - start) * 1000,
                error=str(e)
            )

    # =========================================================================
    # Test Group: Model Routing
    # =========================================================================

    def _test_model_routing(self):
        """Test model routing and capacity selection."""

        # Test 1: Client-facing uses maximum reliability
        start = time.time()
        try:
            router = ModelCapacityRouter()
            model = router.select_model("complex", 0.95, is_client_facing=True)

            passed = "sonnet" in model.lower() or "opus" in model.lower()
            self._add_result(
                "model_routing_client_facing",
                passed,
                f"Client-facing -> {model}" if passed else f"Expected high-reliability model, got {model}",
                (time.time() - start) * 1000,
                {"model": model}
            )
        except Exception as e:
            self._add_result(
                "model_routing_client_facing",
                False,
                "Exception in model routing",
                (time.time() - start) * 1000,
                error=str(e)
            )

        # Test 2: Subtask routing for extraction
        start = time.time()
        try:
            config = get_model_for_subtask("extraction")

            passed = "haiku" in config.get("model", "").lower()
            self._add_result(
                "model_routing_extraction_subtask",
                passed,
                f"Extraction -> {config.get('model')}" if passed else f"Expected Haiku, got {config}",
                (time.time() - start) * 1000,
                {"config": config}
            )
        except Exception as e:
            self._add_result(
                "model_routing_extraction_subtask",
                False,
                "Exception in subtask routing",
                (time.time() - start) * 1000,
                error=str(e)
            )

        # Test 3: Subtask routing for synthesis
        start = time.time()
        try:
            config = get_model_for_subtask("synthesis")

            passed = "sonnet" in config.get("model", "").lower()
            self._add_result(
                "model_routing_synthesis_subtask",
                passed,
                f"Synthesis -> {config.get('model')}" if passed else f"Expected Sonnet, got {config}",
                (time.time() - start) * 1000,
                {"config": config}
            )
        except Exception as e:
            self._add_result(
                "model_routing_synthesis_subtask",
                False,
                "Exception in subtask routing",
                (time.time() - start) * 1000,
                error=str(e)
            )

        # Test 4: Retrieval strategy selection
        start = time.time()
        try:
            router = RetrievalStrategyRouter()

            product_strategy = router.select_strategy("What is the price of SKU-12345?")
            concept_strategy = router.select_strategy("How does email marketing work?")

            passed = (
                product_strategy.get("strategy") == "direct_kb_mapping" and
                concept_strategy.get("strategy") == "semantic_embedding"
            )
            self._add_result(
                "model_routing_retrieval_strategy",
                passed,
                "Retrieval strategies correctly selected" if passed else "Retrieval strategy mismatch",
                (time.time() - start) * 1000,
                {"product": product_strategy, "concept": concept_strategy}
            )
        except Exception as e:
            self._add_result(
                "model_routing_retrieval_strategy",
                False,
                "Exception in retrieval routing",
                (time.time() - start) * 1000,
                error=str(e)
            )

    # =========================================================================
    # Test Group: Workflow Runner
    # =========================================================================

    def _test_workflow_runner(self):
        """Test WorkflowRunner multi-step execution."""

        # Test 1: Basic workflow execution
        start = time.time()
        try:
            runner = WorkflowRunner("test-workflow", version="v1.0.0", client="test", tenant_id="test")

            def step1(inputs):
                return {"output": {"step": 1}, "tokens_input": 50, "tokens_output": 25}

            def step2(inputs):
                return {"output": {"step": 2}, "tokens_input": 60, "tokens_output": 30}

            result1 = runner.run_step("step-1", step1, {"data": "input"})
            result2 = runner.run_step("step-2", step2, {"data": result1.output})

            telemetry = runner.complete(RunStatus.SUCCESS)

            passed = (
                result1.status == "success" and
                result2.status == "success" and
                telemetry.status == "success" and
                len(telemetry.steps) == 2
            )
            self._add_result(
                "workflow_runner_basic_execution",
                passed,
                "Workflow completed successfully" if passed else "Workflow execution failed",
                (time.time() - start) * 1000,
                {
                    "steps_count": len(telemetry.steps),
                    "total_tokens": telemetry.tokens.get("total", 0),
                    "status": telemetry.status
                }
            )
        except Exception as e:
            self._add_result(
                "workflow_runner_basic_execution",
                False,
                "Exception in workflow execution",
                (time.time() - start) * 1000,
                error=str(e)
            )

        # Test 2: Workflow with step failure and retry
        start = time.time()
        try:
            runner = WorkflowRunner("retry-test", tenant_id="test")

            attempt_count = [0]

            def flaky_step(inputs):
                attempt_count[0] += 1
                if attempt_count[0] < 2:
                    raise ValueError("Simulated transient failure")
                return {"output": {"success": True}, "tokens_input": 10, "tokens_output": 5}

            result = runner.run_step("flaky-step", flaky_step, {}, max_retries=2)

            passed = result.status == "success" and attempt_count[0] == 2
            self._add_result(
                "workflow_runner_retry_on_failure",
                passed,
                f"Step succeeded after {attempt_count[0]} attempts" if passed else "Retry logic failed",
                (time.time() - start) * 1000,
                {"attempts": attempt_count[0], "status": result.status}
            )
        except Exception as e:
            self._add_result(
                "workflow_runner_retry_on_failure",
                False,
                "Exception in retry test",
                (time.time() - start) * 1000,
                error=str(e)
            )

        # Test 3: Workflow state checkpointing
        start = time.time()
        try:
            runner = WorkflowRunner("checkpoint-test", tenant_id="test")

            def checkpoint_step(inputs):
                return {"output": {"checkpoint": "saved"}, "tokens_input": 20, "tokens_output": 10}

            runner.run_step("checkpoint-step", checkpoint_step, {})

            # Check that state file exists
            state_file = runner.run_dir / "state.json"
            passed = state_file.exists()

            if passed:
                with open(state_file) as f:
                    state = json.load(f)
                passed = "outputs" in state and "checkpoint-step" in state.get("outputs", {})

            self._add_result(
                "workflow_runner_checkpointing",
                passed,
                "State checkpointed successfully" if passed else "Checkpointing failed",
                (time.time() - start) * 1000,
                {"state_file_exists": state_file.exists()}
            )
        except Exception as e:
            self._add_result(
                "workflow_runner_checkpointing",
                False,
                "Exception in checkpointing test",
                (time.time() - start) * 1000,
                error=str(e)
            )


def main():
    """Run the test suite and save results."""
    print("=" * 60)
    print("MH1 Agent Pipeline Test Suite")
    print("=" * 60)
    print()

    tester = AgentPipelineTester()
    result = tester.run_all_tests()

    # Print summary
    print(f"\nTest Results: {result.passed}/{result.total_tests} passed ({result.summary['pass_rate']}%)")
    print(f"Duration: {result.duration_seconds}s")
    print()

    # Print group summaries
    for group, summary in result.summary.items():
        if isinstance(summary, dict) and "total" in summary:
            status = "PASS" if summary["failed"] == 0 else "FAIL"
            print(f"  [{status}] {group}: {summary['passed']}/{summary['total']}")

    print()

    # Print failed tests
    failed_tests = [t for t in result.tests if not t["passed"]]
    if failed_tests:
        print("Failed Tests:")
        for test in failed_tests:
            print(f"  - {test['test_name']}: {test['message']}")
            if test.get("error"):
                print(f"    Error: {test['error']}")

    # Save results
    output_path = SYSTEM_ROOT / "telemetry" / "agent_pipeline_test.json"
    with open(output_path, "w") as f:
        json.dump(asdict(result), f, indent=2)

    print(f"\nResults saved to: {output_path}")

    # Return exit code
    return 0 if result.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
