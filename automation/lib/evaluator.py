"""
MH1 Evaluation Agent
Runs quality checks on outputs before delivery.
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pathlib import Path

from lib.release_policy import determine_release_action, get_release_action_message, ReleaseAction

SYSTEM_ROOT = Path(__file__).parent.parent


@dataclass
class EvaluationResult:
    score: float
    passed: bool
    breakdown: dict
    issues: list
    suggestions: list

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "pass": self.passed,
            "breakdown": self.breakdown,
            "issues": self.issues,
            "suggestions": self.suggestions
        }


class Evaluator:
    """
    Evaluates outputs against quality criteria.
    
    Dimensions:
    - schema_validity (18%): Output matches expected schema
    - factuality (23%): Claims have sources
    - completeness (18%): All required sections present
    - brand_voice (13%): Tone and style appropriate
    - risk_flags (18%): No hallucinations or sensitive content
    - context_efficiency (10%): Large inputs handled efficiently (RLM pattern)
    """

    WEIGHTS = {
        "schema_validity": 0.18,
        "factuality": 0.23,
        "completeness": 0.18,
        "brand_voice": 0.13,
        "risk_flags": 0.18,
        "context_efficiency": 0.10
    }
    
    PASS_THRESHOLD = 0.8
    MIN_PER_DIMENSION = 0.6
    
    # Context handling thresholds
    INLINE_THRESHOLD = 8000  # tokens
    SONNET_SUB_CALL_WARNING_THRESHOLD = 5

    def __init__(self, schema: dict = None, requirements: dict = None, telemetry: dict = None):
        self.schema = schema
        self.requirements = requirements or {}
        self.telemetry = telemetry or {}  # Run telemetry for context efficiency check

    def evaluate(self, output: Any, context: dict = None) -> EvaluationResult:
        """
        Run full evaluation on output.
        
        Args:
            output: The output to evaluate (dict, string, or markdown)
            context: Original task context for reference
            
        Returns:
            EvaluationResult with scores, issues, and suggestions
        """
        issues = []
        suggestions = []
        
        # Run each evaluation dimension
        schema_score = self._check_schema(output, issues, suggestions)
        factuality_score = self._check_factuality(output, issues, suggestions)
        completeness_score = self._check_completeness(output, issues, suggestions)
        brand_voice_score = self._check_brand_voice(output, issues, suggestions)
        risk_score = self._check_risk_flags(output, issues, suggestions)
        context_efficiency_score = self._check_context_efficiency(issues, suggestions)
        
        breakdown = {
            "schema_validity": schema_score,
            "factuality": factuality_score,
            "completeness": completeness_score,
            "brand_voice": brand_voice_score,
            "risk_flags": risk_score,
            "context_efficiency": context_efficiency_score
        }
        
        # Calculate weighted score
        total_score = sum(
            score * self.WEIGHTS[dimension]
            for dimension, score in breakdown.items()
        )
        
        # Determine pass/fail
        passed = (
            total_score >= self.PASS_THRESHOLD and
            all(score >= self.MIN_PER_DIMENSION for score in breakdown.values()) and
            not any(issue["severity"] == "critical" for issue in issues)
        )
        
        return EvaluationResult(
            score=round(total_score, 2),
            passed=passed,
            breakdown=breakdown,
            issues=issues,
            suggestions=suggestions
        )

    def _check_schema(self, output: Any, issues: list, suggestions: list) -> float:
        """Check if output matches expected schema."""
        if not self.schema:
            return 1.0  # No schema to validate against
        
        score = 1.0
        
        if isinstance(output, dict):
            # Check required fields
            required = self.schema.get("required", [])
            for field in required:
                if field not in output:
                    issues.append({
                        "dimension": "schema_validity",
                        "severity": "high",
                        "description": f"Missing required field: {field}",
                        "location": "root"
                    })
                    score -= 0.2
            
            # Check for unexpected fields
            properties = self.schema.get("properties", {})
            if self.schema.get("additionalProperties") is False:
                for field in output:
                    if field not in properties:
                        issues.append({
                            "dimension": "schema_validity",
                            "severity": "low",
                            "description": f"Unexpected field: {field}",
                            "location": "root"
                        })
                        score -= 0.05
        
        return max(0, score)

    def _check_factuality(self, output: Any, issues: list, suggestions: list) -> float:
        """Check if factual claims have sources."""
        score = 1.0
        text = self._extract_text(output)
        
        # Patterns that suggest factual claims
        claim_patterns = [
            r'\d+%',  # Percentages
            r'\$[\d,]+',  # Dollar amounts
            r'increased by',
            r'decreased by',
            r'grew \d+',
            r'according to',
            r'studies show',
            r'research indicates',
        ]
        
        claims_found = 0
        claims_sourced = 0
        
        for pattern in claim_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            claims_found += len(matches)
        
        # Check for source indicators near claims
        source_patterns = [
            r'\[source\]',
            r'\(source:',
            r'source:',
            r'according to \w+',
            r'per \w+ data',
            r'from hubspot',
            r'from snowflake',
        ]
        
        for pattern in source_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            claims_sourced += len(matches)
        
        if claims_found > 0:
            source_ratio = min(1.0, claims_sourced / claims_found)
            if source_ratio < 0.5:
                issues.append({
                    "dimension": "factuality",
                    "severity": "high",
                    "description": f"Found {claims_found} factual claims but only {claims_sourced} have sources",
                    "location": "various"
                })
                suggestions.append("Add source references for factual claims (e.g., '[source: HubSpot data]')")
                score = source_ratio
            elif source_ratio < 0.8:
                issues.append({
                    "dimension": "factuality",
                    "severity": "medium",
                    "description": "Some factual claims lack source attribution",
                    "location": "various"
                })
                score = 0.7 + (source_ratio * 0.3)
        
        return max(0, score)

    def _check_completeness(self, output: Any, issues: list, suggestions: list) -> float:
        """Check if all required sections are present."""
        score = 1.0
        text = self._extract_text(output)
        
        # Check for placeholder text
        placeholder_patterns = [
            r'\[.*?\]',  # [placeholder]
            r'TODO',
            r'TBD',
            r'PLACEHOLDER',
            r'INSERT.*HERE',
            r'XXX',
        ]
        
        for pattern in placeholder_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            # Filter out legitimate brackets (like [source])
            real_placeholders = [m for m in matches if 'source' not in m.lower()]
            if real_placeholders:
                issues.append({
                    "dimension": "completeness",
                    "severity": "high",
                    "description": f"Found placeholder text: {real_placeholders[:3]}",
                    "location": "various"
                })
                suggestions.append("Replace placeholder text with actual content")
                score -= 0.2 * len(real_placeholders)
        
        # Check required sections if specified
        required_sections = self.requirements.get("required_sections", [])
        for section in required_sections:
            if section.lower() not in text.lower():
                issues.append({
                    "dimension": "completeness",
                    "severity": "medium",
                    "description": f"Missing required section: {section}",
                    "location": "root"
                })
                score -= 0.15
        
        # Check minimum length if specified
        min_length = self.requirements.get("min_length", 0)
        if len(text) < min_length:
            issues.append({
                "dimension": "completeness",
                "severity": "medium",
                "description": f"Output too short ({len(text)} chars, minimum {min_length})",
                "location": "root"
            })
            score -= 0.2
        
        return max(0, score)

    def _check_brand_voice(self, output: Any, issues: list, suggestions: list) -> float:
        """Check tone and style consistency."""
        score = 1.0
        text = self._extract_text(output)
        
        # Check for overly casual language (in professional context)
        casual_patterns = [
            r'\bsuper\b',
            r'\bawesome\b',
            r'\bcool\b',
            r'\bstuff\b',
            r'\bguys\b',
            r'\btotally\b',
            r'\bkinda\b',
            r'\bwanna\b',
            r'\bgonna\b',
        ]
        
        casual_count = 0
        for pattern in casual_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            casual_count += len(matches)
        
        if casual_count > 3:
            issues.append({
                "dimension": "brand_voice",
                "severity": "medium",
                "description": f"Found {casual_count} instances of overly casual language",
                "location": "various"
            })
            suggestions.append("Use more professional language for client deliverables")
            score -= 0.1 * min(casual_count, 5)
        
        # Check for inconsistent capitalization in headers (if markdown)
        if "##" in text:
            headers = re.findall(r'^#{1,3}\s+(.+)$', text, re.MULTILINE)
            if headers:
                # Check if all headers follow same capitalization style
                title_case = sum(1 for h in headers if h.istitle() or h[0].isupper())
                lower_case = len(headers) - title_case
                if title_case > 0 and lower_case > 0:
                    issues.append({
                        "dimension": "brand_voice",
                        "severity": "low",
                        "description": "Inconsistent header capitalization",
                        "location": "headers"
                    })
                    score -= 0.1
        
        return max(0, score)

    def _check_risk_flags(self, output: Any, issues: list, suggestions: list) -> float:
        """Check for hallucinations, bias, or sensitive content."""
        score = 1.0
        text = self._extract_text(output)
        
        # Check for absolute claims without hedging
        absolute_patterns = [
            r'\balways\b',
            r'\bnever\b',
            r'\ball companies\b',
            r'\beveryone\b',
            r'\bno one\b',
            r'\bguaranteed\b',
            r'\bdefinitely will\b',
        ]
        
        absolute_count = 0
        for pattern in absolute_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            absolute_count += len(matches)
        
        if absolute_count > 2:
            issues.append({
                "dimension": "risk_flags",
                "severity": "medium",
                "description": f"Found {absolute_count} absolute claims that may be overstated",
                "location": "various"
            })
            suggestions.append("Consider hedging absolute claims (e.g., 'often' instead of 'always')")
            score -= 0.1 * min(absolute_count, 3)
        
        # Check for potentially sensitive topics
        sensitive_patterns = [
            r'\bconfidential\b',
            r'\bproprietary\b',
            r'\bcompetitor\b.*\bweak',
            r'\bfailing\b',
            r'\bbankrupt',
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append({
                    "dimension": "risk_flags",
                    "severity": "high",
                    "description": "Contains potentially sensitive content - requires human review",
                    "location": "various"
                })
                score -= 0.3
                break
        
        # Check for signs of hallucination (very specific numbers without context)
        suspicious_numbers = re.findall(r'\b\d{5,}\b', text)  # 5+ digit numbers
        if suspicious_numbers:
            issues.append({
                "dimension": "risk_flags",
                "severity": "medium",
                "description": f"Found very specific numbers that should be verified: {suspicious_numbers[:3]}",
                "location": "various"
            })
            suggestions.append("Verify large specific numbers against source data")
            score -= 0.1
        
        return max(0, score)

    def _check_context_efficiency(self, issues: list, suggestions: list) -> float:
        """
        Check if context was handled efficiently (RLM pattern).
        
        Evaluates:
        - Large context processed inline (inefficient)
        - Excessive Sonnet usage for sub-calls (expensive)
        - Sub-call count within reasonable limits
        """
        score = 1.0
        
        # If no telemetry provided, assume efficient (can't evaluate)
        if not self.telemetry:
            return 1.0
        
        context_handling = self.telemetry.get("context_handling", {})
        input_size = context_handling.get("input_size_tokens", 0)
        strategy = context_handling.get("strategy", "inline")
        sub_calls = context_handling.get("sub_calls", [])
        
        # Check 1: Large context processed inline (inefficient)
        if input_size > self.INLINE_THRESHOLD and strategy == "inline":
            issues.append({
                "dimension": "context_efficiency",
                "severity": "medium",
                "description": f"Large input ({input_size:,} tokens) processed inline. Consider chunked approach.",
                "location": "context_handling"
            })
            suggestions.append(
                f"Use ContextManager for inputs > {self.INLINE_THRESHOLD:,} tokens. "
                "This enables chunked processing with cheaper models."
            )
            score -= 0.3
        
        # Check 2: Excessive Sonnet usage in sub-calls
        if sub_calls:
            sonnet_sub_calls = [
                c for c in sub_calls 
                if "sonnet" in c.get("model", "").lower()
                and c.get("task_type") not in ["synthesis", "aggregation"]
            ]
            
            if len(sonnet_sub_calls) > self.SONNET_SUB_CALL_WARNING_THRESHOLD:
                issues.append({
                    "dimension": "context_efficiency",
                    "severity": "low",
                    "description": f"{len(sonnet_sub_calls)} non-synthesis sub-calls used Sonnet. Consider Haiku for extraction tasks.",
                    "location": "sub_calls"
                })
                suggestions.append(
                    "Use claude-haiku for extraction, filtering, and chunk_processing sub-tasks. "
                    "Reserve claude-sonnet-4 for synthesis and aggregation."
                )
                score -= 0.15
        
        # Check 3: Excessive sub-calls (potential infinite loop or poor chunking)
        if len(sub_calls) > 50:
            issues.append({
                "dimension": "context_efficiency",
                "severity": "medium",
                "description": f"High sub-call count ({len(sub_calls)}). May indicate poor chunking strategy.",
                "location": "sub_calls"
            })
            suggestions.append(
                "Review chunk size. Consider larger chunks to reduce sub-call overhead."
            )
            score -= 0.2
        
        # Check 4: Good practice - using chunked strategy for large context (bonus)
        if input_size > self.INLINE_THRESHOLD and strategy in ["chunked", "offloaded"]:
            # Context was handled correctly, no penalty
            pass
        
        return max(0, score)

    def _extract_text(self, output: Any) -> str:
        """Extract text content from various output formats."""
        if isinstance(output, str):
            return output
        elif isinstance(output, dict):
            # Recursively extract all string values
            texts = []
            def extract(obj):
                if isinstance(obj, str):
                    texts.append(obj)
                elif isinstance(obj, dict):
                    for v in obj.values():
                        extract(v)
                elif isinstance(obj, list):
                    for item in obj:
                        extract(item)
            extract(output)
            return " ".join(texts)
        else:
            return str(output)


def evaluate_output(
    output: Any, 
    schema: dict = None, 
    requirements: dict = None,
    telemetry: dict = None
) -> dict:
    """
    Convenience function to evaluate an output.
    
    Args:
        output: The output to evaluate
        schema: Optional JSON schema for validation
        requirements: Optional dict with required_sections, min_length, etc.
        telemetry: Optional run telemetry for context efficiency evaluation
        
    Returns:
        Evaluation result as dict
    
    Example:
        # Basic evaluation
        result = evaluate_output(my_output, schema=my_schema)
        
        # With context efficiency check
        result = evaluate_output(
            my_output, 
            schema=my_schema,
            telemetry={"context_handling": {"strategy": "chunked", "input_size_tokens": 50000}}
        )
    """
    evaluator = Evaluator(schema=schema, requirements=requirements, telemetry=telemetry)
    result = evaluator.evaluate(output)
    result_dict = result.to_dict()
    
    # Add release policy decision
    action = determine_release_action(result_dict)
    result_dict["release_action"] = action.value
    result_dict["release_message"] = get_release_action_message(action)
    
    return result_dict


if __name__ == "__main__":
    # Test evaluation
    test_output = {
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
    
    test_schema = {
        "required": ["summary", "recommendations"],
        "properties": {
            "summary": {"type": "string"},
            "recommendations": {"type": "array"},
            "metrics": {"type": "object"}
        }
    }
    
    result = evaluate_output(test_output, schema=test_schema)
    print(json.dumps(result, indent=2))


# === P1 ADDITIONS: SRAC Framework ===
# Source: r12.pdf "A Multi-Agent System for Generating Actionable Business Advice"
# Evidence: 92-95/100 composite quality scores achieved
# Improvement: 18-22% quality improvement over single-pass generation

class ToolErrorType(Enum):
    """12-category error taxonomy from r7.pdf research"""
    NOT_INITIALIZED = "init_fail"      # ~68% of failures
    ARGS_MISMATCH = "args_fail"        # ~20% of failures
    EXECUTION_ERROR = "exec_fail"      # ~8% of failures
    RESULT_MISMATCH = "result_fail"    # ~4% of failures


@dataclass
class SRACScore:
    """SRAC Quality Framework from r12.pdf - 92-95/100 quality scores achieved"""
    specificity: float  # 1-5: Does it address specific segment?
    relevance: float    # 1-5: Aligns with objectives?
    actionability: float  # 1-5: Drives clear next steps?
    concision: float    # 1-5: Appropriately brief?
    
    @property
    def weighted_score(self) -> float:
        """Weighted sum with research-validated weights"""
        return (
            self.specificity * 0.25 +
            self.relevance * 0.25 +
            self.actionability * 0.30 +
            self.concision * 0.20
        )
    
    @property
    def passed(self) -> bool:
        """Threshold: 3.5/5.0 from r12.pdf"""
        return self.weighted_score >= 3.5


class SRACEvaluator:
    """
    SRAC (Specificity-Relevance-Actionability-Concision) Evaluator
    
    Source: r12.pdf "A Multi-Agent System for Generating Actionable Business Advice"
    Evidence: 92-95/100 composite quality scores across automotive, restaurant, hospitality
    Improvement: 18-22% quality improvement over single-pass generation
    """
    
    DIMENSIONS = {
        "specificity": {
            "weight": 0.25,
            "description": "Does content address specific audience segment or use case?",
            "scale": {
                5: "Highly specific, tailored details",
                4: "Mostly specific with minor generalizations",
                3: "Moderately specific",
                2: "Somewhat generic",
                1: "Generic, one-size-fits-all"
            }
        },
        "relevance": {
            "weight": 0.25,
            "description": "Does content align with stated objectives?",
            "scale": {
                5: "Directly addresses all objectives",
                4: "Addresses most objectives",
                3: "Addresses some objectives",
                2: "Partially relevant",
                1: "Off-topic or tangential"
            }
        },
        "actionability": {
            "weight": 0.30,
            "description": "Does content drive clear next steps?",
            "scale": {
                5: "Explicit, implementable actions",
                4: "Clear actions with minor gaps",
                3: "Some actionable guidance",
                2: "Vague action suggestions",
                1: "Theoretical only, no actions"
            }
        },
        "concision": {
            "weight": 0.20,
            "description": "Is content appropriately brief for format?",
            "scale": {
                5: "Optimal length, no filler",
                4: "Mostly concise",
                3: "Some unnecessary content",
                2: "Noticeably bloated",
                1: "Repetitive or excessive"
            }
        }
    }
    
    PASS_THRESHOLD = 3.5
    
    def evaluate(self, content: str, context: Dict) -> SRACScore:
        """Evaluate content using SRAC framework"""
        # This would call LLM for actual evaluation
        # Returns structured SRACScore
        pass
    
    def get_feedback(self, score: SRACScore) -> str:
        """Generate textual feedback for refinement loop"""
        feedback = []
        if score.specificity < 4:
            feedback.append("Increase specificity: Add more tailored details for the target segment")
        if score.relevance < 4:
            feedback.append("Improve relevance: Better align with stated objectives")
        if score.actionability < 4:
            feedback.append("Enhance actionability: Provide more explicit, implementable steps")
        if score.concision < 4:
            feedback.append("Improve concision: Remove filler and redundant content")
        return "\n".join(feedback) if feedback else "Content meets quality threshold"


class ToolErrorTracker:
    """
    Tool Error Taxonomy from r7.pdf research
    
    Source: "When Agents Fail to Act: A Diagnostic Framework for Tool Invocation Reliability"
    Evidence: 1,980 test instances, 12-category error taxonomy
    Key Finding: Tool initialization failures (~68%) dominate over parameter errors (~32%)
    """
    
    def __init__(self):
        self.errors: List[Dict] = []
    
    def log_error(self, 
                  error_type: ToolErrorType, 
                  tool_name: str,
                  failure_mode: str,  # "omission" or "malformed"
                  step_count: int,
                  details: str = ""):
        """
        Log tool error with taxonomy classification
        
        Failure modes (from r7.pdf):
        - omission (~68%): Agent fails to recognize tool invocation is required
        - malformed (~32%): Incorrect tool names, invalid JSON, hallucinated parameters
        """
        self.errors.append({
            "error_type": error_type.value,
            "tool_name": tool_name,
            "failure_mode": failure_mode,
            "step_count": step_count,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_remediation(self, error_type: ToolErrorType, failure_mode: str) -> str:
        """Get remediation strategy based on error classification"""
        if failure_mode == "omission":
            return "Enhanced procedural reasoning training needed"
        elif failure_mode == "malformed":
            return "Schema-aware invocation + validation layers needed"
        return "Unknown failure mode"
    
    def get_statistics(self) -> Dict:
        """Get error statistics for monitoring"""
        total = len(self.errors)
        if total == 0:
            return {"total": 0}
        
        by_type = {}
        by_mode = {"omission": 0, "malformed": 0}
        
        for error in self.errors:
            by_type[error["error_type"]] = by_type.get(error["error_type"], 0) + 1
            by_mode[error["failure_mode"]] = by_mode.get(error["failure_mode"], 0) + 1
        
        return {
            "total": total,
            "by_type": by_type,
            "by_mode": by_mode,
            "omission_rate": by_mode["omission"] / total,
            "malformed_rate": by_mode["malformed"] / total
        }
