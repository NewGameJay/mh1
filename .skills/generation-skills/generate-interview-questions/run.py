#!/usr/bin/env python3
"""
Generate Interview Questions Skill - Interview Prep for Onboarding (v1.0.0)

Generates targeted interview questions based on research gaps identified during
company, competitor, and founder research.

Features:
- Research gap analysis
- Assumption validation
- Categorized question generation
- Interview guide document generation

Usage:
    # Basic run (after research)
    ./mh1 run skill generate-interview-questions --client_id <id>
    
    # With options
    ./mh1 run skill generate-interview-questions --client_id <id> --question_count 30
    
    # Programmatic
    from skills.generate_interview_questions.run import run_generate_interview_questions
    result = run_generate_interview_questions({"client_id": "abc123"})
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
SKILL_NAME = "generate-interview-questions"
SKILL_VERSION = "v1.0.0"
COST_PER_1K_INPUT = 0.003
COST_PER_1K_OUTPUT = 0.015

# Question categories
CATEGORIES = [
    "strategy",
    "audience",
    "voice",
    "competitive",
    "content",
    "founder",
    "metrics"
]

# Default questions when no research is available
DEFAULT_QUESTIONS = [
    {
        "category": "strategy",
        "question": "What are your top 3 business priorities for the next 6 months?",
        "purpose": "Understand strategic focus for content alignment"
    },
    {
        "category": "strategy",
        "question": "What's the biggest challenge you're currently facing in reaching your target customers?",
        "purpose": "Identify pain points to address in content"
    },
    {
        "category": "audience",
        "question": "Describe your ideal customer - what does their day-to-day look like?",
        "purpose": "Build detailed ICP understanding"
    },
    {
        "category": "audience",
        "question": "What objections do you most commonly hear from prospects?",
        "purpose": "Understand barriers to conversion"
    },
    {
        "category": "voice",
        "question": "If your brand had a personality, how would you describe it in 3 words?",
        "purpose": "Define brand voice characteristics"
    },
    {
        "category": "voice",
        "question": "Are there any topics or tones you want to specifically avoid in content?",
        "purpose": "Identify content guardrails"
    },
    {
        "category": "voice",
        "question": "Share an example of content (yours or others) that you feel represents your ideal voice.",
        "purpose": "Get concrete voice examples"
    },
    {
        "category": "competitive",
        "question": "What do customers tell you sets you apart from alternatives?",
        "purpose": "Understand differentiation from customer perspective"
    },
    {
        "category": "competitive",
        "question": "Which competitors do you most frequently lose deals to, and why?",
        "purpose": "Identify competitive weaknesses to address"
    },
    {
        "category": "content",
        "question": "What content topics have performed best for you in the past?",
        "purpose": "Build on proven content themes"
    },
    {
        "category": "content",
        "question": "What topics do you want to be known for as a thought leader?",
        "purpose": "Define thought leadership direction"
    },
    {
        "category": "content",
        "question": "What content format resonates most with your audience (long-form, short tips, stories)?",
        "purpose": "Understand format preferences"
    },
    {
        "category": "founder",
        "question": "What's a contrarian or unique perspective you hold about your industry?",
        "purpose": "Identify distinctive POV for content"
    },
    {
        "category": "founder",
        "question": "What question do you wish more people asked you?",
        "purpose": "Surface unexplored expertise areas"
    },
    {
        "category": "metrics",
        "question": "How will you measure the success of our content efforts?",
        "purpose": "Align on success metrics"
    },
    {
        "category": "metrics",
        "question": "What would a home run look like in the first 90 days?",
        "purpose": "Set clear expectations"
    }
]


class GenerateInterviewQuestionsSkill:
    """
    Interview question generation skill for client onboarding.
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
        self.research_docs_loaded = 0
    
    def _estimate_cost(self) -> float:
        """Estimate run cost."""
        estimated_input = 20000  # Research docs + prompt
        estimated_output = 3000
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
    
    def _load_research_docs(self, founder_names: List[str] = None) -> Dict:
        """Load all available research documents for the client."""
        research_dir = SYSTEM_ROOT / "clients" / self.client_id / "research"
        docs = {}
        
        if not research_dir.exists():
            return docs
        
        # Load company research
        company_path = research_dir / "company-research.json"
        if company_path.exists():
            with open(company_path, 'r') as f:
                docs["company"] = json.load(f)
                self.research_docs_loaded += 1
        
        # Load competitor research
        competitor_path = research_dir / "competitor-research.json"
        if competitor_path.exists():
            with open(competitor_path, 'r') as f:
                docs["competitors"] = json.load(f)
                self.research_docs_loaded += 1
        
        # Load founder research
        docs["founders"] = []
        for file in research_dir.glob("founder-*.json"):
            if founder_names:
                # Check if this founder is in the list
                founder_data = json.load(open(file, 'r'))
                name = founder_data.get("founder_profile", {}).get("name", "")
                if not any(fn.lower() in name.lower() for fn in founder_names):
                    continue
            with open(file, 'r') as f:
                docs["founders"].append(json.load(f))
                self.research_docs_loaded += 1
        
        return docs
    
    def _identify_research_gaps(self, docs: Dict) -> List[Dict]:
        """Identify gaps in the research that need to be filled."""
        gaps = []
        
        # Company research gaps
        company = docs.get("company", {})
        if not company:
            gaps.append({"area": "company", "description": "No company research available"})
        else:
            profile = company.get("company_profile", {})
            if not profile.get("mission"):
                gaps.append({"area": "mission", "description": "Company mission not documented"})
            
            positioning = company.get("market_positioning", {})
            if not positioning.get("target_audience"):
                gaps.append({"area": "audience", "description": "Target audience not clearly defined"})
            if not positioning.get("differentiators"):
                gaps.append({"area": "differentiators", "description": "Key differentiators not identified"})
            
            products = company.get("products_services", [])
            if not products:
                gaps.append({"area": "products", "description": "Products/services not documented"})
        
        # Competitor research gaps
        competitors = docs.get("competitors", {})
        if not competitors:
            gaps.append({"area": "competitors", "description": "No competitor research available"})
        else:
            if not competitors.get("market_gaps"):
                gaps.append({"area": "market_gaps", "description": "Market gaps not identified"})
        
        # Founder research gaps
        founders = docs.get("founders", [])
        if not founders:
            gaps.append({"area": "founders", "description": "No founder research available"})
        else:
            for founder in founders:
                voice = founder.get("voice_patterns", {})
                if voice.get("confidence", 0) < 0.5:
                    name = founder.get("founder_profile", {}).get("name", "Founder")
                    gaps.append({
                        "area": "voice",
                        "description": f"Low confidence in voice patterns for {name}"
                    })
        
        return gaps
    
    def _identify_assumptions(self, docs: Dict) -> List[Dict]:
        """Identify assumptions that need validation."""
        assumptions = []
        
        # Company assumptions
        company = docs.get("company", {})
        if company:
            positioning = company.get("market_positioning", {})
            if positioning.get("target_audience"):
                assumptions.append({
                    "assumption": f"Primary audience is: {positioning.get('target_audience')[:100]}",
                    "source": "company-research"
                })
            
            voice = company.get("brand_voice", {})
            if voice.get("tone"):
                assumptions.append({
                    "assumption": f"Brand tone is: {', '.join(voice.get('tone', []))}",
                    "source": "company-research"
                })
        
        # Competitor assumptions
        competitors = docs.get("competitors", {})
        if competitors.get("competitors"):
            comp_names = [c.get("name") for c in competitors.get("competitors", [])[:3]]
            assumptions.append({
                "assumption": f"Primary competitors are: {', '.join(comp_names)}",
                "source": "competitor-research"
            })
        
        return assumptions
    
    def _generate_questions(
        self,
        gaps: List[Dict],
        assumptions: List[Dict],
        docs: Dict,
        focus_areas: List[str],
        question_count: int,
        include_voice: bool
    ) -> List[Dict]:
        """Generate interview questions based on gaps and assumptions."""
        questions = []
        question_id = 1
        
        # Start with default questions as base
        for q in DEFAULT_QUESTIONS:
            if focus_areas and q["category"] not in focus_areas:
                continue
            if q["category"] == "voice" and not include_voice:
                continue
            
            questions.append({
                "id": question_id,
                "category": q["category"],
                "question": q["question"],
                "purpose": q["purpose"],
                "gap_addressed": None,
                "priority": "medium"
            })
            question_id += 1
        
        # Add gap-specific questions
        for gap in gaps:
            if len(questions) >= question_count:
                break
            
            gap_questions = self._questions_for_gap(gap)
            for q in gap_questions:
                if len(questions) >= question_count:
                    break
                questions.append({
                    "id": question_id,
                    "category": q.get("category", "general"),
                    "question": q["question"],
                    "purpose": q.get("purpose", "Fill research gap"),
                    "gap_addressed": gap["description"],
                    "priority": "high"
                })
                question_id += 1
        
        # Add assumption validation questions
        for assumption in assumptions:
            if len(questions) >= question_count:
                break
            
            questions.append({
                "id": question_id,
                "category": "validation",
                "question": f"We found that {assumption['assumption']}. Is this accurate? Any nuances we should know?",
                "purpose": "Validate research assumption",
                "gap_addressed": None,
                "assumption_validated": assumption["assumption"],
                "priority": "medium"
            })
            question_id += 1
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        questions.sort(key=lambda x: priority_order.get(x.get("priority", "medium"), 1))
        
        return questions[:question_count]
    
    def _questions_for_gap(self, gap: Dict) -> List[Dict]:
        """Generate questions to address a specific gap."""
        area = gap.get("area", "")
        
        gap_question_map = {
            "mission": [
                {"category": "strategy", "question": "What's the core mission that drives your company?", "purpose": "Understand company purpose"}
            ],
            "audience": [
                {"category": "audience", "question": "Walk us through your ideal customer's typical day and challenges.", "purpose": "Build detailed ICP"},
                {"category": "audience", "question": "Who are the key decision-makers you need to reach?", "purpose": "Understand buying process"}
            ],
            "differentiators": [
                {"category": "competitive", "question": "When you win deals, what do customers say was the deciding factor?", "purpose": "Identify true differentiators"},
                {"category": "competitive", "question": "What do you do that no one else in your space does?", "purpose": "Find unique value"}
            ],
            "products": [
                {"category": "strategy", "question": "Walk us through your product/service offerings and who each is for.", "purpose": "Understand product portfolio"}
            ],
            "competitors": [
                {"category": "competitive", "question": "Who do you see as your main competitors and why?", "purpose": "Identify competitive landscape"}
            ],
            "market_gaps": [
                {"category": "competitive", "question": "Where do you see unmet needs in your market?", "purpose": "Identify market opportunities"}
            ],
            "founders": [
                {"category": "founder", "question": "What's your background and what led you to start this company?", "purpose": "Understand founder story"}
            ],
            "voice": [
                {"category": "voice", "question": "Show us 2-3 pieces of content that capture the voice you want to have.", "purpose": "Get concrete voice examples"},
                {"category": "voice", "question": "What tone feels most natural to you - formal, conversational, provocative?", "purpose": "Define voice preferences"}
            ]
        }
        
        return gap_question_map.get(area, [])
    
    def _generate_interview_guide(self, questions: List[Dict], gaps: List[Dict], assumptions: List[Dict]) -> str:
        """Generate markdown interview guide document."""
        doc = f"""# Client Onboarding Interview Guide

**Client ID:** {self.client_id}
**Generated:** {datetime.now().strftime('%Y-%m-%d')}
**Total Questions:** {len(questions)}

---

## Pre-Interview Summary

### Research Gaps to Address

{chr(10).join(['- ' + g['description'] for g in gaps]) if gaps else '- No significant gaps identified'}

### Assumptions to Validate

{chr(10).join(['- ' + a['assumption'] + ' (from ' + a['source'] + ')' for a in assumptions]) if assumptions else '- No assumptions to validate'}

---

## Interview Questions

"""
        # Group by category
        categories_seen = []
        for q in questions:
            cat = q.get("category", "general")
            if cat not in categories_seen:
                categories_seen.append(cat)
                doc += f"\n### {cat.title()}\n\n"
            
            priority_badge = "🔴" if q.get("priority") == "high" else "🟡" if q.get("priority") == "medium" else "🟢"
            doc += f"{priority_badge} **Q{q['id']}:** {q['question']}\n"
            doc += f"   - *Purpose:* {q.get('purpose', 'N/A')}\n"
            if q.get("gap_addressed"):
                doc += f"   - *Addresses:* {q['gap_addressed']}\n"
            doc += "\n"
        
        doc += """---

## Interview Tips

1. **Start with rapport** - Begin with easier questions about their background
2. **Go deep on voice** - Voice questions are critical for content quality
3. **Capture exact phrases** - Note specific words/phrases they use
4. **Validate assumptions** - Don't assume research findings are correct
5. **Ask for examples** - Concrete examples are more useful than abstract descriptions

---

## Post-Interview

After the interview, run the `incorporate-interview-results` skill to update research documents with new information.

---

*This interview guide was generated automatically based on research analysis.*
"""
        return doc
    
    def _save_outputs(self, data: Dict, interview_guide: str) -> Dict:
        """Save outputs to client directory."""
        client_dir = SYSTEM_ROOT / "clients" / self.client_id / "research"
        client_dir.mkdir(parents=True, exist_ok=True)
        
        doc_path = client_dir / "interview-questions.md"
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(interview_guide)
        
        json_path = client_dir / "interview-questions.json"
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
            "research_docs_loaded": self.research_docs_loaded,
            "tokens": {
                "input": self.tokens_input,
                "output": self.tokens_output,
                "total": self.tokens_input + self.tokens_output
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def run(self, inputs: Dict) -> Dict:
        """
        Main execution method for interview question generation.
        """
        founder_names = inputs.get("founder_names", [])
        focus_areas = inputs.get("focus_areas", [])
        question_count = min(inputs.get("question_count", 20), 50)
        include_voice = inputs.get("include_voice_questions", True)
        
        runner = WorkflowRunner(
            workflow_name=SKILL_NAME,
            version=SKILL_VERSION,
            client=self.client_id,
            tenant_id=self.tenant_id
        )
        
        try:
            # Budget check
            estimated_cost = self._estimate_cost()
            budget_check = self._check_budget(estimated_cost)
            
            if not budget_check["allowed"]:
                return {
                    "status": "budget_exceeded",
                    "message": budget_check["message"],
                    "_meta": self._build_meta(time.time() - self.start_time, 0, "blocked")
                }
            
            # Load research documents
            def load_research_step(step_inputs):
                docs = self._load_research_docs(founder_names)
                return {"output": docs}
            
            research_result = runner.run_step("load_research", load_research_step, {})
            research_docs = research_result.output
            
            # Identify gaps
            def identify_gaps_step(step_inputs):
                gaps = self._identify_research_gaps(step_inputs.get("docs", {}))
                return {"output": gaps}
            
            gaps_result = runner.run_step("identify_gaps", identify_gaps_step, {"docs": research_docs})
            research_gaps = gaps_result.output
            
            # Identify assumptions
            def identify_assumptions_step(step_inputs):
                assumptions = self._identify_assumptions(step_inputs.get("docs", {}))
                return {"output": assumptions}
            
            assumptions_result = runner.run_step("identify_assumptions", identify_assumptions_step, {"docs": research_docs})
            assumptions = assumptions_result.output
            
            # Generate questions
            def generate_questions_step(step_inputs):
                questions = self._generate_questions(
                    gaps=step_inputs.get("gaps", []),
                    assumptions=step_inputs.get("assumptions", []),
                    docs=step_inputs.get("docs", {}),
                    focus_areas=focus_areas,
                    question_count=question_count,
                    include_voice=include_voice
                )
                return {"output": questions}
            
            questions_result = runner.run_step("generate_questions", generate_questions_step, {
                "gaps": research_gaps,
                "assumptions": assumptions,
                "docs": research_docs
            })
            questions = questions_result.output
            
            # Build final data
            final_data = {
                "questions": questions,
                "research_gaps": research_gaps,
                "assumptions_to_validate": assumptions
            }
            
            # Generate interview guide
            interview_guide = self._generate_interview_guide(questions, research_gaps, assumptions)
            
            # Save outputs
            saved_paths = self._save_outputs(final_data, interview_guide)
            
            final_output = {
                **final_data,
                "interview_guide": interview_guide,
                "interview_guide_path": saved_paths["doc_path"]
            }
            
            # Evaluation
            evaluation = evaluate_output(
                final_output,
                schema={"required": ["questions"]},
                requirements={"min_questions": 10}
            )
            
            release_action = determine_release_action(
                standard_eval=evaluation,
                is_external_facing=False
            )
            
            runtime = time.time() - self.start_time
            actual_cost = self._calculate_actual_cost()
            release_value = release_action.value if hasattr(release_action, 'value') else str(release_action)
            
            if release_value == "auto_deliver":
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


def run_generate_interview_questions(inputs: Dict) -> Dict:
    """Main entry point for interview question generation skill."""
    client_id = inputs.get("client_id")
    if not client_id:
        return {"status": "failed", "error": "client_id is required"}
    
    skill = GenerateInterviewQuestionsSkill(
        client_id=client_id,
        tenant_id=inputs.get("tenant_id", client_id),
        execution_mode=inputs.get("execution_mode", "suggest")
    )
    return skill.run(inputs)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Generate interview questions")
    parser.add_argument("--client_id", type=str, required=True)
    parser.add_argument("--founder_names", type=str, help="Comma-separated founder names")
    parser.add_argument("--focus_areas", type=str, help="Comma-separated focus areas")
    parser.add_argument("--question_count", type=int, default=20)
    parser.add_argument("--include_voice_questions", action="store_true", default=True)
    parser.add_argument("--tenant_id", type=str)
    parser.add_argument("--execution_mode", type=str, choices=["suggest", "preview", "execute"], default="suggest")
    parser.add_argument("--output", type=str)
    
    args = parser.parse_args()
    
    inputs = {
        "client_id": args.client_id,
        "question_count": args.question_count,
        "include_voice_questions": args.include_voice_questions,
        "execution_mode": args.execution_mode
    }
    
    if args.founder_names:
        inputs["founder_names"] = args.founder_names.split(",")
    if args.focus_areas:
        inputs["focus_areas"] = args.focus_areas.split(",")
    if args.tenant_id:
        inputs["tenant_id"] = args.tenant_id
    
    result = run_generate_interview_questions(inputs)
    
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Output saved to {args.output}")
    else:
        print(json.dumps(result, indent=2, default=str))
    
    sys.exit(0 if result["status"] in ["success", "review"] else 1)


if __name__ == "__main__":
    main()
