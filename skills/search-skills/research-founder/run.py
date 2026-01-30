#!/usr/bin/env python3
"""
Research Founder Skill - Per-Founder Research for Onboarding (v1.0.0)

Performs deep research on individual founders/executives to understand their
background, expertise, content style, and voice patterns.

Features:
- LinkedIn profile extraction
- Public content collection and analysis
- Voice pattern detection
- Expertise identification
- Interview preparation suggestions

Usage:
    # Basic run
    ./mh1 run skill research-founder --client_id <id> --founder_name <name> --linkedin_url <url>
    
    # Without LinkedIn URL (will search)
    ./mh1 run skill research-founder --client_id <id> --founder_name <name> --company_name <company>
    
    # Programmatic
    from skills.research_founder.run import run_research_founder
    result = run_research_founder({
        "client_id": "abc123",
        "founder_name": "John Smith",
        "linkedin_url": "https://linkedin.com/in/johnsmith"
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
SKILL_NAME = "research-founder"
SKILL_VERSION = "v1.0.0"
COST_PER_1K_INPUT = 0.003
COST_PER_1K_OUTPUT = 0.015


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


class ResearchFounderSkill:
    """
    Per-founder research skill for client onboarding.
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
        self.content_pieces_analyzed = 0
    
    def _estimate_cost(self) -> float:
        """Estimate run cost."""
        estimated_input = 15000  # Profile + content
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
            "status": status.status,
            "daily_remaining": status.daily_remaining,
            "monthly_remaining": status.monthly_remaining
        }
    
    def _find_linkedin_profile(self, name: str, title: str = None, company: str = None) -> Optional[str]:
        """Search for LinkedIn profile URL."""
        # In production: Use search API to find LinkedIn profile
        return None
    
    def _scrape_linkedin(self, url: str) -> Dict:
        """Scrape LinkedIn profile data."""
        # In production: Use LinkedIn scraper MCP
        return {
            "name": "",
            "headline": "",
            "location": "",
            "about": "",
            "experience": [],
            "education": [],
            "skills": [],
            "posts": []
        }
    
    def _collect_public_content(self, sources: Dict) -> List[Dict]:
        """Collect public content from various sources."""
        content = []
        # In production: Scrape content from provided URLs
        return content
    
    def _analyze_voice_patterns(self, content: List[Dict]) -> Dict:
        """Analyze voice and style patterns from content."""
        total_words = sum(len(c.get("text", "").split()) for c in content)
        confidence = min(0.9, total_words / 5000)  # Max confidence at 5000 words
        
        return {
            "confidence": round(confidence, 2),
            "tone": [],
            "vocabulary_level": "professional",
            "common_phrases": [],
            "sentence_structure": "varied",
            "formality": "professional",
            "total_words_analyzed": total_words
        }
    
    def _identify_expertise(self, profile: Dict, content: List[Dict]) -> List[Dict]:
        """Identify areas of expertise."""
        # In production: LLM analysis of content and profile
        return []
    
    def _generate_interview_prep(self, profile: Dict, voice: Dict, expertise: List[Dict]) -> Dict:
        """Generate interview preparation suggestions."""
        return {
            "recommended_topics": [],
            "questions_to_explore": [
                "What are your top 3 content themes you want to focus on?",
                "Who is your primary target audience?",
                "What differentiates your perspective in the industry?",
                "Are there any topics you want to avoid?",
                "What tone resonates best with your audience?"
            ],
            "gaps_to_fill": [
                "Content preferences not publicly available",
                "Internal voice guidelines",
                "Competitor content to avoid"
            ]
        }
    
    def _generate_research_document(self, data: Dict) -> str:
        """Generate markdown research document."""
        profile = data.get("founder_profile", {})
        voice = data.get("voice_patterns", {})
        expertise = data.get("topics_of_expertise", [])
        interview = data.get("interview_prep", {})
        
        doc = f"""# Founder Research: {profile.get('name', 'Unknown')}

**Generated:** {datetime.now().strftime('%Y-%m-%d')}
**Client ID:** {self.client_id}
**Voice Confidence:** {voice.get('confidence', 0):.0%}

---

## Profile Overview

**Name:** {profile.get('name', 'Unknown')}
**Title:** {profile.get('title', 'Unknown')}
**Company:** {profile.get('company', 'Unknown')}
**Location:** {profile.get('location', 'Unknown')}

### About

{profile.get('about', 'Not available')}

---

## Career History

"""
        for exp in profile.get('career_history', []):
            doc += f"""### {exp.get('title', 'Role')} at {exp.get('company', 'Company')}
*{exp.get('duration', '')}*

{exp.get('description', '')}

"""
        
        doc += """---

## Education

"""
        for edu in profile.get('education', []):
            doc += f"- **{edu.get('school', '')}** - {edu.get('degree', '')} ({edu.get('year', '')})\n"
        
        doc += f"""
---

## Voice Analysis

**Confidence Level:** {voice.get('confidence', 0):.0%}
**Words Analyzed:** {voice.get('total_words_analyzed', 0)}

### Detected Patterns

- **Tone:** {', '.join(voice.get('tone', ['Not enough data']))}
- **Vocabulary Level:** {voice.get('vocabulary_level', 'Unknown')}
- **Formality:** {voice.get('formality', 'Unknown')}
- **Sentence Structure:** {voice.get('sentence_structure', 'Unknown')}

### Common Phrases

{chr(10).join(['- "' + p + '"' for p in voice.get('common_phrases', [])])}

---

## Topics of Expertise

"""
        for topic in expertise:
            doc += f"- **{topic.get('topic', '')}** (confidence: {topic.get('confidence', 0):.0%})\n"
        
        doc += f"""
---

## Interview Preparation

### Recommended Topics to Explore

{chr(10).join(['- ' + t for t in interview.get('recommended_topics', [])])}

### Questions to Ask

{chr(10).join([str(i+1) + '. ' + q for i, q in enumerate(interview.get('questions_to_explore', []))])}

### Information Gaps to Fill

{chr(10).join(['- ' + g for g in interview.get('gaps_to_fill', [])])}

---

## Content Sources Analyzed

- LinkedIn profile
- {data.get('content_analysis', {}).get('total_pieces', 0)} content pieces

---

*This founder research was generated automatically. Voice analysis will be refined after the client interview.*
"""
        return doc
    
    def _save_outputs(self, data: Dict, research_doc: str, founder_name: str) -> Dict:
        """Save outputs to client directory."""
        client_dir = SYSTEM_ROOT / "clients" / self.client_id / "research"
        client_dir.mkdir(parents=True, exist_ok=True)
        
        slug = slugify(founder_name)
        
        doc_path = client_dir / f"founder-{slug}.md"
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(research_doc)
        
        json_path = client_dir / f"founder-{slug}.json"
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
    
    def _build_meta(self, runtime: float, cost: float, release_action: str, founder_name: str) -> Dict:
        """Build metadata object for output."""
        return {
            "client_id": self.client_id,
            "tenant_id": self.tenant_id,
            "founder_name": founder_name,
            "run_id": self.run_id,
            "execution_mode": self.execution_mode,
            "runtime_seconds": round(runtime, 2),
            "cost_usd": cost,
            "release_action": release_action,
            "skill_version": SKILL_VERSION,
            "content_pieces_analyzed": self.content_pieces_analyzed,
            "tokens": {
                "input": self.tokens_input,
                "output": self.tokens_output,
                "total": self.tokens_input + self.tokens_output
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def run(self, inputs: Dict) -> Dict:
        """
        Main execution method for founder research.
        """
        founder_name = inputs.get("founder_name")
        founder_title = inputs.get("founder_title")
        linkedin_url = inputs.get("linkedin_url")
        twitter_handle = inputs.get("twitter_handle")
        other_profiles = inputs.get("other_profiles", [])
        company_name = inputs.get("company_name")
        
        if not founder_name:
            return {
                "status": "failed",
                "error": "founder_name is required",
                "_meta": self._build_meta(0, 0, "blocked", "")
            }
        
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
                    "_meta": self._build_meta(time.time() - self.start_time, 0, "blocked", founder_name)
                }
            
            # Find LinkedIn if not provided
            def find_profile_step(step_inputs):
                url = linkedin_url
                if not url:
                    url = self._find_linkedin_profile(founder_name, founder_title, company_name)
                return {"output": {"linkedin_url": url}}
            
            profile_step = runner.run_step("find_profile", find_profile_step, {})
            final_linkedin_url = profile_step.output.get("linkedin_url")
            
            # Scrape LinkedIn
            def scrape_linkedin_step(step_inputs):
                url = step_inputs.get("linkedin_url")
                if url:
                    data = self._scrape_linkedin(url)
                    data["linkedin_url"] = url
                    return {"output": data}
                return {"output": {"posts": []}}
            
            linkedin_result = runner.run_step("scrape_linkedin", scrape_linkedin_step, {"linkedin_url": final_linkedin_url})
            linkedin_data = linkedin_result.output
            
            # Collect additional content
            def collect_content_step(step_inputs):
                sources = {
                    "twitter": twitter_handle,
                    "other": other_profiles
                }
                content = self._collect_public_content(sources)
                
                # Add LinkedIn posts
                content.extend([
                    {"source": "linkedin", "text": p.get("text", ""), "date": p.get("date")}
                    for p in linkedin_data.get("posts", [])
                ])
                
                self.content_pieces_analyzed = len(content)
                return {"output": content}
            
            content_result = runner.run_step("collect_content", collect_content_step, {})
            all_content = content_result.output
            
            # Analyze voice patterns
            def analyze_voice_step(step_inputs):
                voice = self._analyze_voice_patterns(step_inputs.get("content", []))
                return {"output": voice}
            
            voice_result = runner.run_step("analyze_voice", analyze_voice_step, {"content": all_content})
            voice_patterns = voice_result.output
            
            # Build founder profile
            founder_profile = {
                "name": founder_name,
                "title": founder_title or linkedin_data.get("headline", ""),
                "company": company_name or "",
                "location": linkedin_data.get("location", ""),
                "about": linkedin_data.get("about", ""),
                "career_history": linkedin_data.get("experience", []),
                "education": linkedin_data.get("education", []),
                "skills": linkedin_data.get("skills", []),
                "linkedin_url": final_linkedin_url,
                "twitter_handle": twitter_handle
            }
            
            # Identify expertise
            expertise = self._identify_expertise(founder_profile, all_content)
            
            # Generate interview prep
            interview_prep = self._generate_interview_prep(founder_profile, voice_patterns, expertise)
            
            # Build final data
            final_data = {
                "founder_profile": founder_profile,
                "content_analysis": {
                    "total_pieces": len(all_content),
                    "sources": list(set(c.get("source", "unknown") for c in all_content)),
                    "topics": []
                },
                "voice_patterns": voice_patterns,
                "topics_of_expertise": expertise,
                "interview_prep": interview_prep
            }
            
            # Generate research document
            research_doc = self._generate_research_document(final_data)
            
            # Save outputs
            saved_paths = self._save_outputs(final_data, research_doc, founder_name)
            
            final_output = {
                **final_data,
                "research_doc": research_doc,
                "research_doc_path": saved_paths["doc_path"]
            }
            
            # Evaluation
            evaluation = evaluate_output(
                final_output,
                schema={"required": ["founder_profile", "voice_patterns"]},
                requirements={"required_sections": ["founder_profile"]}
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
            elif release_value == "human_review":
                runner.route_to_human(reason=f"Eval: {evaluation.get('score', 0):.0%}", context={})
                runner.complete(RunStatus.REVIEW, evaluation=evaluation)
                status = "review"
            else:
                runner.complete(RunStatus.FAILED, evaluation=evaluation)
                status = "blocked"
            
            return {
                "status": status,
                "output": final_output,
                "evaluation": evaluation,
                "release_action": release_value,
                "run_id": runner.run_id,
                "_meta": self._build_meta(runtime, actual_cost, release_value, founder_name)
            }
            
        except Exception as e:
            runner.complete(RunStatus.FAILED)
            return {
                "status": "failed",
                "error": str(e),
                "error_type": type(e).__name__,
                "run_id": runner.run_id,
                "_meta": self._build_meta(time.time() - self.start_time, 0, "blocked", founder_name)
            }


def run_research_founder(inputs: Dict) -> Dict:
    """Main entry point for founder research skill."""
    client_id = inputs.get("client_id")
    if not client_id:
        return {"status": "failed", "error": "client_id is required"}
    
    skill = ResearchFounderSkill(
        client_id=client_id,
        tenant_id=inputs.get("tenant_id", client_id),
        execution_mode=inputs.get("execution_mode", "suggest")
    )
    return skill.run(inputs)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Run founder research skill")
    parser.add_argument("--client_id", type=str, required=True)
    parser.add_argument("--founder_name", type=str, required=True)
    parser.add_argument("--founder_title", type=str)
    parser.add_argument("--linkedin_url", type=str)
    parser.add_argument("--twitter_handle", type=str)
    parser.add_argument("--other_profiles", type=str, help="Comma-separated URLs")
    parser.add_argument("--company_name", type=str)
    parser.add_argument("--tenant_id", type=str)
    parser.add_argument("--execution_mode", type=str, choices=["suggest", "preview", "execute"], default="suggest")
    parser.add_argument("--output", type=str)
    
    args = parser.parse_args()
    
    inputs = {
        "client_id": args.client_id,
        "founder_name": args.founder_name,
        "execution_mode": args.execution_mode
    }
    
    if args.founder_title:
        inputs["founder_title"] = args.founder_title
    if args.linkedin_url:
        inputs["linkedin_url"] = args.linkedin_url
    if args.twitter_handle:
        inputs["twitter_handle"] = args.twitter_handle
    if args.other_profiles:
        inputs["other_profiles"] = args.other_profiles.split(",")
    if args.company_name:
        inputs["company_name"] = args.company_name
    if args.tenant_id:
        inputs["tenant_id"] = args.tenant_id
    
    result = run_research_founder(inputs)
    
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Output saved to {args.output}")
    else:
        print(json.dumps(result, indent=2, default=str))
    
    sys.exit(0 if result["status"] in ["success", "review"] else 1)


if __name__ == "__main__":
    main()
