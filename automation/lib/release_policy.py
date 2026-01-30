"""
Release Policy - Deterministic release decisions for all skills.

This is the SINGLE source of truth for release decisions.
All skills use this. No exceptions.
"""

from typing import Optional
from enum import Enum

class ReleaseAction(Enum):
    AUTO_DELIVER = "auto_deliver"
    AUTO_REFINE = "auto_refine"
    HUMAN_REVIEW = "human_review"
    BLOCKED = "blocked"

def determine_release_action(
    standard_eval: dict,
    srac_eval: Optional[dict] = None,
    ai_washing_eval: Optional[dict] = None,
    is_external_facing: bool = False
) -> ReleaseAction:
    """
    Determine release action based on evaluation results.
    
    Rules (in order of precedence):
    1. BLOCKED: Critical issues OR high AI washing severity
    2. HUMAN_REVIEW: Score < 0.7 OR AI washing warnings (if external)
    3. AUTO_REFINE: Score < 0.8 with fixable suggestions
    4. AUTO_DELIVER: Score >= 0.8 and passes all checks
    
    Args:
        standard_eval: Standard 6-dimension evaluation result
        srac_eval: Optional SRAC evaluation (for content)
        ai_washing_eval: Optional AI washing check (for external content)
        is_external_facing: If True, AI washing check is mandatory
    
    Returns:
        ReleaseAction enum value
    """
    # Rule 1: BLOCKED - Critical issues
    issues = standard_eval.get("issues", [])
    if any(issue.get("severity") == "critical" for issue in issues):
        return ReleaseAction.BLOCKED
    
    # Rule 1b: BLOCKED - High AI washing (if provided)
    if ai_washing_eval:
        if ai_washing_eval.get("overall", {}).get("highest_severity") == "high":
            return ReleaseAction.BLOCKED
    
    # Rule 2: HUMAN_REVIEW - Low confidence
    score = standard_eval.get("score", 0)
    if score < 0.7:
        return ReleaseAction.HUMAN_REVIEW
    
    # Rule 2b: HUMAN_REVIEW - AI washing warnings on external content
    if is_external_facing and ai_washing_eval:
        warning_count = ai_washing_eval.get("overall", {}).get("warning_count", 0)
        if warning_count > 0:
            return ReleaseAction.HUMAN_REVIEW
    
    # Rule 3: AUTO_REFINE - Fixable issues
    if not standard_eval.get("pass", False):
        suggestions = standard_eval.get("suggestions", [])
        if len(suggestions) > 0:
            return ReleaseAction.AUTO_REFINE
    
    # Rule 3b: AUTO_REFINE - SRAC below threshold
    if srac_eval and not srac_eval.get("pass", True):
        return ReleaseAction.AUTO_REFINE
    
    # Rule 4: AUTO_DELIVER - All good
    return ReleaseAction.AUTO_DELIVER


def get_release_action_message(action: ReleaseAction) -> str:
    """Human-readable message for each action."""
    messages = {
        ReleaseAction.AUTO_DELIVER: "Output passed all quality gates. Ready for delivery.",
        ReleaseAction.AUTO_REFINE: "Output needs improvement. Applying suggestions and retrying.",
        ReleaseAction.HUMAN_REVIEW: "Output requires human review before delivery.",
        ReleaseAction.BLOCKED: "Output blocked due to critical issues. Cannot proceed.",
    }
    return messages.get(action, "Unknown action")


def get_release_reason(
    action: ReleaseAction,
    standard_eval: dict,
    srac_eval: Optional[dict] = None,
    ai_washing_eval: Optional[dict] = None
) -> str:
    """
    Get the specific reason why a release action was determined.
    
    Args:
        action: The determined ReleaseAction
        standard_eval: Standard evaluation result
        srac_eval: Optional SRAC evaluation
        ai_washing_eval: Optional AI washing check
    
    Returns:
        Human-readable reason for the action
    """
    issues = standard_eval.get("issues", [])
    score = standard_eval.get("score", 0)
    
    if action == ReleaseAction.BLOCKED:
        critical_issues = [i for i in issues if i.get("severity") == "critical"]
        if critical_issues:
            return f"Critical issue: {critical_issues[0].get('message', 'Unknown')}"
        if ai_washing_eval and ai_washing_eval.get("overall", {}).get("highest_severity") == "high":
            return "High AI washing severity detected"
        return "Blocked due to critical quality issues"
    
    elif action == ReleaseAction.HUMAN_REVIEW:
        if score < 0.7:
            return f"Score {score:.2f} below 0.7 threshold"
        if ai_washing_eval:
            warning_count = ai_washing_eval.get("overall", {}).get("warning_count", 0)
            if warning_count > 0:
                return f"{warning_count} AI washing warning(s) on external content"
        return "Requires human verification"
    
    elif action == ReleaseAction.AUTO_REFINE:
        suggestions = standard_eval.get("suggestions", [])
        if suggestions:
            return f"{len(suggestions)} fixable suggestion(s): {suggestions[0]}"
        if srac_eval and not srac_eval.get("pass", True):
            return "SRAC check below threshold"
        return "Minor improvements needed"
    
    else:  # AUTO_DELIVER
        return f"Score {score:.2f} passed all quality gates"
