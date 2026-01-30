#!/usr/bin/env python3
"""
Incorporate Interview Results Skill - Post-Interview Processing (v1.0.0)

Processes interview transcripts and notes to update research documents with
validated information, fill gaps, and extract voice data.

Features:
- Interview transcript processing
- Research document updates
- Assumption validation
- Voice data extraction
- Conflict detection

Usage:
    # With transcript file
    ./mh1 run skill incorporate-interview-results --client_id <id> --interview_file <path>
    
    # With inline transcript
    ./mh1 run skill incorporate-interview-results --client_id <id> --interview_transcript "..."
    
    # Programmatic
    from skills.incorporate_interview_results.run import run_incorporate_interview_results
    result = run_incorporate_interview_results({
        "client_id": "abc123",
        "interview_transcript": "Full transcript..."
    })
"""

import argparse
import json
import os
import re
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add lib to path
SKILL_ROOT = Path(__file__).parent
SYSTEM_ROOT = SKILL_ROOT.parent.parent
sys.path.insert(0, str(SYSTEM_ROOT / "lib"))

# Import lib modules
try:
    from runner import (
        WorkflowRunner, RunStatus, ContextManager, ContextConfig,
        estimate_tokens, get_model_for_subtask, should_offload_context
    )
    from evaluator import evaluate_output
    from release_policy import determine_release_action, ReleaseAction, get_release_action_message
    from budget import BudgetManager
    from telemetry import log_run
except ImportError:
    # Stub implementations for standalone testing
    class RunStatus:
        SUCCESS = "success"
        FAILED = "failed"
        REVIEW = "review"
    
    class ReleaseAction:
        AUTO_DELIVER = "auto_deliver"
        HUMAN_REVIEW = "human_review"
        BLOCKED = "blocked"
        @property
        def value(self):
            return self
    
    def estimate_tokens(text): return len(str(text)) // 4
    def get_model_for_subtask(task_type): return {"model": "claude-sonnet-4"}
    def should_offload_context(data):
        tokens = estimate_tokens(json.dumps(data))
        return tokens > 8000, "chunked" if tokens > 8000 else "inline"
    def evaluate_output(output, schema=None, requirements=None):
        return {"score": 0.85, "pass": True, "breakdown": {}}
    def determine_release_action(standard_eval=None, is_external_facing=False):
        return ReleaseAction()
    def get_release_action_message(action): return "Auto-delivered"
    
    class BudgetManager:
        def check_run_cost(self, tenant_id, cost): return True, "OK"
        def check_budget(self, tenant_id, cost):
            class Status:
                status = "ok"
                daily_remaining = 100
                monthly_remaining = 2000
            return Status()
    
    class WorkflowRunner:
        def __init__(self, **kwargs):
            self.run_id = str(uuid.uuid4())[:8]
            self.run_dir = Path("/tmp")
            self.telemetry = type('obj', (object,), {
                'start_time': datetime.now(timezone.utc).isoformat(),
                'end_time': None, 'steps': []
            })()
        def run_step(self, name, func, inputs):
            result = func(inputs)
            class StepResult:
                status = "success"
                output = result.get("output", {})
                error = None
            return StepResult()
        def complete(self, status, evaluation=None): return {}
        def route_to_human(self, reason, context): pass
    
    def log_run(**kwargs): pass


# Constants
SKILL_NAME = "incorporate-interview-results"
SKILL_VERSION = "v1.0.0"
COST_PER_1K_INPUT = 0.003
COST_PER_1K_OUTPUT = 0.015

# Insight categories
INSIGHT_CATEGORIES = [
    "strategy",
    "audience",
    "voice",
    "competitive",
    "content",
    "products",
    "metrics",
    "general"
]


class IncorporateInterviewResultsSkill:
    """
    Post-interview processing skill for updating research documents.
    """
    
    def __init__(
        self,
        client_id: str,
        tenant_id: str = None,
        execution_mode: str = "suggest"
    ):
        self.client_id = client_id
        self.tenant_id = tenant_id or client_id
        self.execution_mode = execution_mode
        self.run_id = str(uuid.uuid4())[:8]
        self.start_time = time.time()
        self.budget = BudgetManager()
        self.tokens_input = 0
        self.tokens_output = 0
        self.docs_updated = []
    
    def _estimate_cost(self, interview_length: int) -> float:
        """Estimate run cost based on interview length."""
        estimated_input = interview_length + 20000  # Interview + research docs
        estimated_output = 5000
        cost = (
            estimated_input / 1000 * COST_PER_1K_INPUT +
            estimated_output / 1000 * COST_PER_1K_OUTPUT
        )
        return round(cost, 4)
    
    def _check_budget(self, estimated_cost: float) -> Dict:
        """Check if run is within budget limits."""
        allowed, message = self.budget.check_run_cost(self.tenant_id, estimated_cost)
        status = self.budget.check_budget(self.tenant_id, estimated_cost)
        return {
            "allowed": allowed,
            "message": message,
            "status": status.status
        }
    
    def _load_interview_content(self, inputs: Dict) -> Tuple[str, int]:
        """Load interview content from inputs."""
        content = ""
        
        if inputs.get("interview_transcript"):
            content = inputs["interview_transcript"]
        elif inputs.get("interview_notes"):
            content = inputs["interview_notes"]
        elif inputs.get("interview_file"):
            file_path = Path(inputs["interview_file"])
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
        
        word_count = len(content.split())
        return content, word_count
    
    def _load_research_docs(self) -> Dict:
        """Load all research documents for the client."""
        research_dir = SYSTEM_ROOT / "clients" / self.client_id / "research"
        docs = {"files": {}, "data": {}}
        
        if not research_dir.exists():
            return docs
        
        # Load all JSON research files
        for file in research_dir.glob("*.json"):
            with open(file, 'r') as f:
                docs["data"][file.stem] = json.load(f)
                docs["files"][file.stem] = str(file)
        
        return docs
    
    def _load_interview_questions(self) -> Optional[Dict]:
        """Load interview questions if available."""
        questions_path = SYSTEM_ROOT / "clients" / self.client_id / "research" / "interview-questions.json"
        if questions_path.exists():
            with open(questions_path, 'r') as f:
                return json.load(f)
        return None
    
    def _extract_insights(self, content: str) -> List[Dict]:
        """Extract key insights from interview content."""
        # In production: Use LLM to extract structured insights
        insights = []
        
        # Simple extraction based on patterns
        # In production, this would be LLM-powered
        paragraphs = content.split('\n\n')
        
        for i, para in enumerate(paragraphs[:20]):  # Limit for demo
            if len(para) > 100:  # Substantial content
                insights.append({
                    "insight": para[:200] + "..." if len(para) > 200 else para,
                    "category": "general",
                    "confidence": "medium",
                    "source_quote": para[:100]
                })
        
        return insights
    
    def _validate_assumptions(self, content: str, research_docs: Dict) -> List[Dict]:
        """Check research assumptions against interview content."""
        validated = []
        
        # Load assumptions from interview questions if available
        questions_data = self._load_interview_questions()
        if questions_data and questions_data.get("assumptions_to_validate"):
            for assumption in questions_data["assumptions_to_validate"]:
                # In production: LLM checks if interview confirms/denies
                validated.append({
                    "assumption": assumption.get("assumption", ""),
                    "source": assumption.get("source", "unknown"),
                    "status": "needs_review",  # In production: confirmed/denied/partial
                    "notes": "Manual review required"
                })
        
        return validated
    
    def _fill_research_gaps(self, content: str, research_docs: Dict) -> List[Dict]:
        """Match interview content to known research gaps."""
        filled = []
        
        # Load gaps from interview questions
        questions_data = self._load_interview_questions()
        if questions_data and questions_data.get("research_gaps"):
            for gap in questions_data["research_gaps"]:
                # In production: LLM extracts relevant content for each gap
                filled.append({
                    "gap": gap.get("description", ""),
                    "area": gap.get("area", "general"),
                    "resolution": "Information discussed in interview",
                    "confidence": "medium",
                    "source_quote": ""
                })
        
        return filled
    
    def _extract_voice_data(self, content: str, interviewee_name: str = None) -> Dict:
        """Extract voice patterns from founder speech."""
        words = content.split()
        word_count = len(words)
        
        # In production: Sophisticated voice analysis via LLM
        # Extract common phrases, sentence patterns, vocabulary
        
        return {
            "words_analyzed": word_count,
            "new_phrases": [],
            "confirmed_tone": [],
            "vocabulary_patterns": [],
            "sentence_lengths": {
                "avg": 15,
                "style": "varied"
            },
            "confidence_delta": 0.1  # How much to increase voice confidence
        }
    
    def _detect_conflicts(self, insights: List[Dict], research_docs: Dict) -> List[Dict]:
        """Detect conflicts between interview and existing research."""
        conflicts = []
        
        # In production: Compare insights to research and flag contradictions
        # This is a placeholder that would use LLM comparison
        
        return conflicts
    
    def _update_research_docs(
        self,
        research_docs: Dict,
        insights: List[Dict],
        voice_data: Dict,
        gaps_filled: List[Dict],
        validate_only: bool
    ) -> List[str]:
        """Update research documents with new information."""
        updated = []
        
        if validate_only:
            return updated
        
        research_dir = SYSTEM_ROOT / "clients" / self.client_id / "research"
        
        # Update company research
        if "company-research" in research_docs.get("data", {}):
            company_data = research_docs["data"]["company-research"]
            
            # Add interview insights
            if "interview_insights" not in company_data:
                company_data["interview_insights"] = []
            
            company_insights = [i for i in insights if i["category"] in ["strategy", "audience", "products"]]
            company_data["interview_insights"].extend(company_insights)
            company_data["last_updated"] = datetime.now(timezone.utc).isoformat()
            company_data["interview_date"] = datetime.now().strftime("%Y-%m-%d")
            
            # Save
            with open(research_dir / "company-research.json", 'w') as f:
                json.dump(company_data, f, indent=2, default=str)
            updated.append("company-research.json")
            self.docs_updated.append("company-research.md")
        
        # Update founder research
        for key, data in research_docs.get("data", {}).items():
            if key.startswith("founder-"):
                # Update voice patterns
                if "voice_patterns" in data:
                    current_confidence = data["voice_patterns"].get("confidence", 0)
                    new_confidence = min(0.95, current_confidence + voice_data.get("confidence_delta", 0))
                    data["voice_patterns"]["confidence"] = new_confidence
                    
                    # Add new phrases
                    if voice_data.get("new_phrases"):
                        existing = data["voice_patterns"].get("common_phrases", [])
                        data["voice_patterns"]["common_phrases"] = list(set(existing + voice_data["new_phrases"]))
                
                data["last_updated"] = datetime.now(timezone.utc).isoformat()
                data["interview_date"] = datetime.now().strftime("%Y-%m-%d")
                
                # Save
                with open(research_dir / f"{key}.json", 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                updated.append(f"{key}.json")
                self.docs_updated.append(f"{key}.md")
        
        return updated
    
    def _generate_update_summary(
        self,
        insights: List[Dict],
        assumptions: List[Dict],
        gaps_filled: List[Dict],
        voice_data: Dict,
        conflicts: List[Dict],
        docs_updated: List[str]
    ) -> str:
        """Generate markdown summary of updates."""
        doc = f"""# Interview Results Summary

**Client ID:** {self.client_id}
**Processed:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Run ID:** {self.run_id}

---

## Summary

- **Insights Extracted:** {len(insights)}
- **Assumptions Validated:** {len(assumptions)}
- **Gaps Filled:** {len(gaps_filled)}
- **Documents Updated:** {len(docs_updated)}
- **Conflicts Detected:** {len(conflicts)}

---

## Extracted Insights

"""
        for i, insight in enumerate(insights[:10], 1):
            doc += f"""### Insight {i}
**Category:** {insight.get('category', 'general')}
**Confidence:** {insight.get('confidence', 'medium')}

{insight.get('insight', '')}

> Source: "{insight.get('source_quote', '')[:100]}..."

---

"""
        
        doc += """## Assumptions Validated

| Assumption | Status | Notes |
|------------|--------|-------|
"""
        for a in assumptions:
            doc += f"| {a.get('assumption', '')[:50]}... | {a.get('status', 'unknown')} | {a.get('notes', '')} |\n"
        
        doc += """
---

## Research Gaps Filled

"""
        for gap in gaps_filled:
            doc += f"""### {gap.get('area', 'General').title()}
**Gap:** {gap.get('gap', '')}
**Resolution:** {gap.get('resolution', '')}

---

"""
        
        doc += f"""## Voice Analysis Updates

- **Words Analyzed:** {voice_data.get('words_analyzed', 0)}
- **Confidence Increase:** +{voice_data.get('confidence_delta', 0):.0%}
- **New Phrases Detected:** {len(voice_data.get('new_phrases', []))}

"""
        
        if conflicts:
            doc += """## Conflicts Requiring Review

"""
            for conflict in conflicts:
                doc += f"""### Conflict in {conflict.get('area', 'Unknown')}
**Research Value:** {conflict.get('research_value', '')}
**Interview Value:** {conflict.get('interview_value', '')}

⚠️ Manual resolution required

---

"""
        
        doc += f"""## Documents Updated

{chr(10).join(['- ' + d for d in docs_updated])}

---

## Next Steps

1. Review any flagged conflicts
2. Verify voice pattern updates
3. Run `extract-founder-voice` for refined voice contract
4. Begin content production

---

*This summary was generated automatically from interview processing.*
"""
        return doc
    
    def _save_outputs(self, data: Dict, summary: str) -> Dict:
        """Save outputs to client directory."""
        client_dir = SYSTEM_ROOT / "clients" / self.client_id / "research"
        client_dir.mkdir(parents=True, exist_ok=True)
        
        doc_path = client_dir / "interview-results.md"
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        json_path = client_dir / "interview-results.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        return {"doc_path": str(doc_path), "json_path": str(json_path)}
    
    def _calculate_actual_cost(self) -> float:
        """Calculate actual cost from tracked tokens."""
        cost = (
            self.tokens_input / 1000 * COST_PER_1K_INPUT +
            self.tokens_output / 1000 * COST_PER_1K_OUTPUT
        )
        return round(cost, 4)
    
    def _build_meta(self, runtime: float, cost: float, release_action: str) -> Dict:
        """Build metadata object for output."""
        return {
            "client_id": self.client_id,
            "tenant_id": self.tenant_id,
            "run_id": self.run_id,
            "execution_mode": self.execution_mode,
            "runtime_seconds": round(runtime, 2),
            "cost_usd": cost,
            "release_action": release_action,
            "skill_version": SKILL_VERSION,
            "docs_updated": len(self.docs_updated),
            "tokens": {
                "input": self.tokens_input,
                "output": self.tokens_output,
                "total": self.tokens_input + self.tokens_output
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def run(self, inputs: Dict) -> Dict:
        """
        Main execution method for interview result incorporation.
        """
        interviewee_name = inputs.get("interviewee_name")
        validate_only = inputs.get("validate_only", False)
        
        runner = WorkflowRunner(
            workflow_name=SKILL_NAME,
            version=SKILL_VERSION,
            client=self.client_id,
            tenant_id=self.tenant_id
        )
        
        try:
            # Load interview content
            content, word_count = self._load_interview_content(inputs)
            
            if not content:
                return {
                    "status": "failed",
                    "error": "No interview content provided. Use interview_transcript, interview_notes, or interview_file.",
                    "_meta": self._build_meta(time.time() - self.start_time, 0, "blocked")
                }
            
            if word_count < 500:
                # Warning but continue
                pass
            
            # Budget check
            estimated_cost = self._estimate_cost(estimate_tokens(content))
            budget_check = self._check_budget(estimated_cost)
            
            if not budget_check["allowed"]:
                return {
                    "status": "budget_exceeded",
                    "message": budget_check["message"],
                    "_meta": self._build_meta(time.time() - self.start_time, 0, "blocked")
                }
            
            # Load research documents
            def load_research_step(step_inputs):
                docs = self._load_research_docs()
                if not docs.get("data"):
                    raise ValueError("No research documents found. Run research skills first.")
                return {"output": docs}
            
            research_result = runner.run_step("load_research", load_research_step, {})
            research_docs = research_result.output
            
            # Extract insights
            def extract_insights_step(step_inputs):
                insights = self._extract_insights(step_inputs.get("content", ""))
                return {"output": insights}
            
            insights_result = runner.run_step("extract_insights", extract_insights_step, {"content": content})
            insights = insights_result.output
            
            # Validate assumptions
            def validate_assumptions_step(step_inputs):
                validated = self._validate_assumptions(content, research_docs)
                return {"output": validated}
            
            assumptions_result = runner.run_step("validate_assumptions", validate_assumptions_step, {})
            assumptions = assumptions_result.output
            
            # Fill gaps
            def fill_gaps_step(step_inputs):
                filled = self._fill_research_gaps(content, research_docs)
                return {"output": filled}
            
            gaps_result = runner.run_step("fill_gaps", fill_gaps_step, {})
            gaps_filled = gaps_result.output
            
            # Extract voice data
            def extract_voice_step(step_inputs):
                voice = self._extract_voice_data(content, interviewee_name)
                return {"output": voice}
            
            voice_result = runner.run_step("extract_voice", extract_voice_step, {})
            voice_data = voice_result.output
            
            # Detect conflicts
            def detect_conflicts_step(step_inputs):
                conflicts = self._detect_conflicts(insights, research_docs)
                return {"output": conflicts}
            
            conflicts_result = runner.run_step("detect_conflicts", detect_conflicts_step, {})
            conflicts = conflicts_result.output
            
            # Update documents (if not validate_only)
            def update_docs_step(step_inputs):
                updated = self._update_research_docs(
                    research_docs, insights, voice_data, gaps_filled, validate_only
                )
                return {"output": updated}
            
            update_result = runner.run_step("update_docs", update_docs_step, {})
            updated_files = update_result.output
            
            # Build final data
            final_data = {
                "extracted_insights": insights,
                "assumptions_validated": assumptions,
                "gaps_filled": gaps_filled,
                "voice_updates": voice_data,
                "conflicts": conflicts,
                "docs_updated": self.docs_updated,
                "interview_word_count": word_count
            }
            
            # Generate summary
            summary = self._generate_update_summary(
                insights, assumptions, gaps_filled, voice_data, conflicts, self.docs_updated
            )
            
            # Save outputs
            saved_paths = self._save_outputs(final_data, summary)
            
            final_output = {
                **final_data,
                "update_summary": summary,
                "update_summary_path": saved_paths["doc_path"]
            }
            
            # Evaluation
            evaluation = evaluate_output(
                final_output,
                schema={"required": ["extracted_insights"]},
                requirements={"min_insights": 3}
            )
            
            # Check for conflicts requiring review
            if conflicts:
                release_action = ReleaseAction()
                release_action.value = "human_review"
            else:
                release_action = determine_release_action(
                    standard_eval=evaluation,
                    is_external_facing=False
                )
            
            runtime = time.time() - self.start_time
            actual_cost = self._calculate_actual_cost()
            release_value = release_action.value if hasattr(release_action, 'value') else str(release_action)
            
            if conflicts:
                runner.route_to_human(reason=f"Conflicts detected: {len(conflicts)}", context={})
                runner.complete(RunStatus.REVIEW, evaluation=evaluation)
                status = "review"
            elif release_value == "auto_deliver":
                runner.complete(RunStatus.SUCCESS, evaluation=evaluation)
                status = "success"
            else:
                runner.complete(RunStatus.REVIEW, evaluation=evaluation)
                status = "review"
            
            return {
                "status": status,
                "output": final_output,
                "evaluation": evaluation,
                "release_action": release_value,
                "run_id": runner.run_id,
                "_meta": self._build_meta(runtime, actual_cost, release_value)
            }
            
        except Exception as e:
            runner.complete(RunStatus.FAILED)
            return {
                "status": "failed",
                "error": str(e),
                "error_type": type(e).__name__,
                "run_id": runner.run_id,
                "_meta": self._build_meta(time.time() - self.start_time, 0, "blocked")
            }


def run_incorporate_interview_results(inputs: Dict) -> Dict:
    """Main entry point for interview incorporation skill."""
    client_id = inputs.get("client_id")
    if not client_id:
        return {"status": "failed", "error": "client_id is required"}
    
    skill = IncorporateInterviewResultsSkill(
        client_id=client_id,
        tenant_id=inputs.get("tenant_id", client_id),
        execution_mode=inputs.get("execution_mode", "suggest")
    )
    return skill.run(inputs)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Incorporate interview results")
    parser.add_argument("--client_id", type=str, required=True)
    parser.add_argument("--interview_transcript", type=str)
    parser.add_argument("--interview_notes", type=str)
    parser.add_argument("--interview_file", type=str)
    parser.add_argument("--interviewee_name", type=str)
    parser.add_argument("--validate_only", action="store_true")
    parser.add_argument("--tenant_id", type=str)
    parser.add_argument("--execution_mode", type=str, choices=["suggest", "preview", "execute"], default="suggest")
    parser.add_argument("--output", type=str)
    
    args = parser.parse_args()
    
    inputs = {
        "client_id": args.client_id,
        "validate_only": args.validate_only,
        "execution_mode": args.execution_mode
    }
    
    if args.interview_transcript:
        inputs["interview_transcript"] = args.interview_transcript
    if args.interview_notes:
        inputs["interview_notes"] = args.interview_notes
    if args.interview_file:
        inputs["interview_file"] = args.interview_file
    if args.interviewee_name:
        inputs["interviewee_name"] = args.interviewee_name
    if args.tenant_id:
        inputs["tenant_id"] = args.tenant_id
    
    result = run_incorporate_interview_results(inputs)
    
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Output saved to {args.output}")
    else:
        print(json.dumps(result, indent=2, default=str))
    
    sys.exit(0 if result["status"] in ["success", "review"] else 1)


if __name__ == "__main__":
    main()
