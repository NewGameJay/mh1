#!/usr/bin/env python3
"""
Research Company Skill - Deep Company Research for Onboarding (v1.0.0)

Performs comprehensive company research by scraping and analyzing the company
website to extract company profile, market positioning, products/services,
and brand voice patterns.

Features:
- Website scraping via Firecrawl MCP
- LLM-powered content analysis
- Structured profile extraction
- Brand voice detection
- Research document generation

Usage:
    # Basic run
    ./mh1 run skill research-company --client_id <id> --company_name <name> --website_url <url>
    
    # Deep research
    ./mh1 run skill research-company --client_id <id> --company_name <name> --website_url <url> --depth deep
    
    # Programmatic
    from skills.research_company.run import run_research_company
    result = run_research_company({
        "client_id": "abc123",
        "company_name": "Acme Corp",
        "website_url": "https://acme.com"
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

# Import lib modules (these would be implemented in the actual system)
try:
    from runner import (
        WorkflowRunner,
        SkillRunner,
        RunStatus,
        ContextManager,
        ContextConfig,
        estimate_tokens,
        get_model_for_subtask,
        should_offload_context
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
    
    def estimate_tokens(text):
        return len(str(text)) // 4
    
    def get_model_for_subtask(task_type):
        return {"model": "claude-sonnet-4"}
    
    def should_offload_context(data):
        tokens = estimate_tokens(json.dumps(data))
        return tokens > 8000, "chunked" if tokens > 8000 else "inline"
    
    def evaluate_output(output, schema=None, requirements=None):
        return {"score": 0.85, "pass": True, "breakdown": {}}
    
    def determine_release_action(standard_eval=None, is_external_facing=False):
        return ReleaseAction()
    
    def get_release_action_message(action):
        return "Auto-delivered"
    
    class BudgetManager:
        def check_run_cost(self, tenant_id, cost):
            return True, "OK"
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
                'end_time': None,
                'steps': []
            })()
        
        def run_step(self, name, func, inputs):
            result = func(inputs)
            class StepResult:
                status = "success"
                output = result.get("output", {})
                error = None
            return StepResult()
        
        def complete(self, status, evaluation=None):
            return {}
        
        def route_to_human(self, reason, context):
            pass
    
    def log_run(**kwargs):
        pass


# Constants
SKILL_NAME = "research-company"
SKILL_VERSION = "v1.0.0"

# Depth configurations
DEPTH_CONFIG = {
    "quick": {"max_pages": 5, "timeout": 60},
    "standard": {"max_pages": 20, "timeout": 120},
    "deep": {"max_pages": 50, "timeout": 180}
}

# Cost estimates
COST_PER_1K_INPUT = 0.003
COST_PER_1K_OUTPUT = 0.015


class ResearchCompanySkill:
    """
    Deep company research skill for client onboarding.
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
        
        # Initialize budget manager
        self.budget = BudgetManager()
        
        # Telemetry tracking
        self.tokens_input = 0
        self.tokens_output = 0
        self.pages_scraped = 0
        self.sub_calls: List[Dict] = []
    
    def _estimate_cost(self, depth: str) -> float:
        """Estimate run cost based on depth."""
        config = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["standard"])
        pages = config["max_pages"]
        
        # Estimate tokens per page
        tokens_per_page = 2000
        analysis_tokens = 5000
        
        estimated_input = (pages * tokens_per_page) + analysis_tokens
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
    
    def _scrape_website(self, url: str, max_pages: int) -> Dict:
        """
        Scrape website using Firecrawl MCP.
        
        In production, this would call the Firecrawl MCP server.
        """
        # Placeholder for MCP call
        # In production: result = mcp.call("firecrawl", "crawl", {"url": url, "limit": max_pages})
        
        return {
            "pages": [],
            "total_scraped": 0,
            "source": "firecrawl",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _extract_company_profile(self, content: str, company_name: str) -> Dict:
        """Extract structured company profile from content."""
        # In production, this would use LLM for extraction
        return {
            "name": company_name,
            "description": "",
            "founded": None,
            "headquarters": None,
            "size": None,
            "mission": None,
            "vision": None
        }
    
    def _analyze_market_positioning(self, content: str) -> Dict:
        """Analyze market positioning from content."""
        return {
            "target_audience": "",
            "icp": {},
            "value_proposition": "",
            "differentiators": [],
            "competitive_advantages": []
        }
    
    def _extract_products_services(self, content: str) -> List[Dict]:
        """Extract products and services."""
        return []
    
    def _detect_brand_voice(self, content: str) -> Dict:
        """Detect brand voice patterns."""
        return {
            "tone": [],
            "personality": "",
            "formality_level": "",
            "key_terms": [],
            "messaging_themes": []
        }
    
    def _generate_research_document(self, data: Dict) -> str:
        """Generate markdown research document."""
        doc = f"""# Company Research: {data.get('company_name', 'Unknown')}

**Generated:** {datetime.now().strftime('%Y-%m-%d')}
**Client ID:** {self.client_id}
**Research Depth:** {data.get('depth', 'standard')}

---

## Company Overview

{data.get('company_profile', {}).get('description', 'Not available')}

### Key Facts

- **Founded:** {data.get('company_profile', {}).get('founded', 'Unknown')}
- **Headquarters:** {data.get('company_profile', {}).get('headquarters', 'Unknown')}
- **Company Size:** {data.get('company_profile', {}).get('size', 'Unknown')}

### Mission & Vision

**Mission:** {data.get('company_profile', {}).get('mission', 'Not available')}

**Vision:** {data.get('company_profile', {}).get('vision', 'Not available')}

---

## Market Positioning

### Target Audience

{data.get('market_positioning', {}).get('target_audience', 'Not available')}

### Value Proposition

{data.get('market_positioning', {}).get('value_proposition', 'Not available')}

### Key Differentiators

{chr(10).join(['- ' + d for d in data.get('market_positioning', {}).get('differentiators', [])])}

---

## Products & Services

{chr(10).join([f"### {p.get('name', 'Product')}{chr(10)}{p.get('description', '')}{chr(10)}" for p in data.get('products_services', [])])}

---

## Brand Voice

### Tone

{', '.join(data.get('brand_voice', {}).get('tone', []))}

### Personality

{data.get('brand_voice', {}).get('personality', 'Not available')}

### Key Terms & Phrases

{', '.join(data.get('brand_voice', {}).get('key_terms', []))}

---

## Sources

- Primary website: {data.get('website_url', 'N/A')}
- Pages analyzed: {data.get('pages_scraped', 0)}

---

*This research document was generated automatically. Please verify key facts during client interview.*
"""
        return doc
    
    def _save_outputs(self, data: Dict, research_doc: str) -> Dict:
        """Save outputs to client directory."""
        client_dir = SYSTEM_ROOT / "clients" / self.client_id / "research"
        client_dir.mkdir(parents=True, exist_ok=True)
        
        # Save markdown document
        doc_path = client_dir / "company-research.md"
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(research_doc)
        
        # Save structured JSON
        json_path = client_dir / "company-research.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        return {
            "doc_path": str(doc_path),
            "json_path": str(json_path)
        }
    
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
            "pages_scraped": self.pages_scraped,
            "tokens": {
                "input": self.tokens_input,
                "output": self.tokens_output,
                "total": self.tokens_input + self.tokens_output
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def run(self, inputs: Dict) -> Dict:
        """
        Main execution method for company research.
        
        Args:
            inputs: Dictionary with:
                - company_name: Company name (required)
                - website_url: Primary website URL (required)
                - additional_urls: Additional URLs to analyze (optional)
                - industry: Industry vertical (optional)
                - depth: Research depth - quick/standard/deep (default: standard)
        
        Returns:
            Complete research result with outputs and metadata
        """
        # Extract parameters
        company_name = inputs.get("company_name")
        website_url = inputs.get("website_url")
        additional_urls = inputs.get("additional_urls", [])
        industry = inputs.get("industry")
        depth = inputs.get("depth", "standard")
        
        if not company_name or not website_url:
            return {
                "status": "failed",
                "error": "company_name and website_url are required",
                "_meta": self._build_meta(0, 0, "blocked")
            }
        
        # Initialize workflow runner
        runner = WorkflowRunner(
            workflow_name=SKILL_NAME,
            version=SKILL_VERSION,
            client=self.client_id,
            tenant_id=self.tenant_id
        )
        
        try:
            # Step 0: Budget check
            estimated_cost = self._estimate_cost(depth)
            budget_check = self._check_budget(estimated_cost)
            
            if not budget_check["allowed"]:
                return {
                    "status": "budget_exceeded",
                    "message": budget_check["message"],
                    "_meta": self._build_meta(
                        runtime=time.time() - self.start_time,
                        cost=0,
                        release_action="blocked"
                    )
                }
            
            # Step 1: Scrape website
            def scrape_step(step_inputs):
                config = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["standard"])
                
                all_urls = [website_url] + additional_urls
                all_content = []
                
                for url in all_urls:
                    scrape_result = self._scrape_website(url, config["max_pages"])
                    all_content.extend(scrape_result.get("pages", []))
                    self.pages_scraped += scrape_result.get("total_scraped", 0)
                
                return {
                    "output": {
                        "content": all_content,
                        "pages_scraped": self.pages_scraped,
                        "urls_processed": all_urls
                    },
                    "tokens_input": 0,
                    "tokens_output": 0
                }
            
            scrape_result = runner.run_step("scrape_website", scrape_step, {"url": website_url})
            if scrape_result.status != "success":
                raise Exception(f"Scraping failed: {scrape_result.error}")
            
            # Combine all content
            all_content = "\n".join([
                page.get("content", "") 
                for page in scrape_result.output.get("content", [])
            ])
            
            # Step 2: Extract company profile
            def extract_profile_step(step_inputs):
                content = step_inputs.get("content", "")
                profile = self._extract_company_profile(content, company_name)
                
                self.tokens_input += estimate_tokens(content)
                self.tokens_output += estimate_tokens(json.dumps(profile))
                
                return {"output": profile}
            
            profile_result = runner.run_step(
                "extract_profile", 
                extract_profile_step, 
                {"content": all_content}
            )
            
            # Step 3: Analyze positioning
            def analyze_positioning_step(step_inputs):
                positioning = self._analyze_market_positioning(step_inputs.get("content", ""))
                return {"output": positioning}
            
            positioning_result = runner.run_step(
                "analyze_positioning",
                analyze_positioning_step,
                {"content": all_content}
            )
            
            # Step 4: Extract products/services
            def extract_products_step(step_inputs):
                products = self._extract_products_services(step_inputs.get("content", ""))
                return {"output": products}
            
            products_result = runner.run_step(
                "extract_products",
                extract_products_step,
                {"content": all_content}
            )
            
            # Step 5: Detect brand voice
            def detect_voice_step(step_inputs):
                voice = self._detect_brand_voice(step_inputs.get("content", ""))
                return {"output": voice}
            
            voice_result = runner.run_step(
                "detect_voice",
                detect_voice_step,
                {"content": all_content}
            )
            
            # Build final output
            final_data = {
                "company_name": company_name,
                "website_url": website_url,
                "industry": industry,
                "depth": depth,
                "company_profile": profile_result.output,
                "market_positioning": positioning_result.output,
                "products_services": products_result.output,
                "brand_voice": voice_result.output,
                "pages_scraped": self.pages_scraped
            }
            
            # Generate research document
            research_doc = self._generate_research_document(final_data)
            
            # Save outputs
            saved_paths = self._save_outputs(final_data, research_doc)
            
            final_output = {
                **final_data,
                "research_doc": research_doc,
                "research_doc_path": saved_paths["doc_path"],
                "research_json_path": saved_paths["json_path"]
            }
            
            # Evaluation
            eval_schema = {
                "required": ["company_profile", "market_positioning", "products_services"],
                "properties": {
                    "company_profile": {"type": "object"},
                    "market_positioning": {"type": "object"},
                    "products_services": {"type": "array"},
                    "brand_voice": {"type": "object"}
                }
            }
            
            evaluation = evaluate_output(
                final_output,
                schema=eval_schema,
                requirements={"required_sections": ["company_profile", "market_positioning"]}
            )
            
            # Determine release action
            release_action = determine_release_action(
                standard_eval=evaluation,
                is_external_facing=False
            )
            
            # Calculate runtime and cost
            runtime = time.time() - self.start_time
            actual_cost = self._calculate_actual_cost()
            
            # Complete workflow
            release_value = release_action.value if hasattr(release_action, 'value') else str(release_action)
            
            if release_value == "auto_deliver":
                runner.complete(RunStatus.SUCCESS, evaluation=evaluation)
                status = "success"
            elif release_value == "human_review":
                runner.route_to_human(
                    reason=f"Evaluation score: {evaluation.get('score', 0):.0%}",
                    context={"output": final_output, "evaluation": evaluation}
                )
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
                "release_message": get_release_action_message(release_action),
                "run_id": runner.run_id,
                "_meta": self._build_meta(runtime, actual_cost, release_value)
            }
            
        except Exception as e:
            runner.complete(RunStatus.FAILED)
            runtime = time.time() - self.start_time
            
            return {
                "status": "failed",
                "error": str(e),
                "error_type": type(e).__name__,
                "run_id": runner.run_id,
                "_meta": self._build_meta(runtime, 0, "blocked")
            }


def run_research_company(inputs: Dict) -> Dict:
    """
    Main entry point for company research skill.
    
    Args:
        inputs: Dictionary with configuration:
            - client_id: Unique client identifier (required)
            - company_name: Company name (required)
            - website_url: Primary website URL (required)
            - additional_urls: Additional URLs to analyze (optional)
            - industry: Industry vertical (optional)
            - depth: Research depth - quick/standard/deep (default: standard)
            - tenant_id: Tenant identifier (default: client_id)
            - execution_mode: suggest/preview/execute (default: suggest)
    
    Returns:
        Complete research result with outputs and metadata
    """
    client_id = inputs.get("client_id")
    if not client_id:
        return {
            "status": "failed",
            "error": "client_id is required"
        }
    
    tenant_id = inputs.get("tenant_id", client_id)
    execution_mode = inputs.get("execution_mode", "suggest")
    
    skill = ResearchCompanySkill(
        client_id=client_id,
        tenant_id=tenant_id,
        execution_mode=execution_mode
    )
    
    return skill.run(inputs)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run company research skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic run
    python run.py --client_id abc123 --company_name "Acme Corp" --website_url "https://acme.com"
    
    # Deep research
    python run.py --client_id abc123 --company_name "Acme Corp" --website_url "https://acme.com" --depth deep
    
    # With additional URLs
    python run.py --client_id abc123 --company_name "Acme Corp" --website_url "https://acme.com" \\
        --additional_urls "https://blog.acme.com,https://docs.acme.com"
    
    # Save output to file
    python run.py --client_id abc123 --company_name "Acme Corp" --website_url "https://acme.com" --output results.json
        """
    )
    
    parser.add_argument("--client_id", type=str, required=True, help="Unique client identifier")
    parser.add_argument("--company_name", type=str, required=True, help="Company name")
    parser.add_argument("--website_url", type=str, required=True, help="Primary website URL")
    parser.add_argument("--additional_urls", type=str, help="Comma-separated additional URLs")
    parser.add_argument("--industry", type=str, help="Industry vertical")
    parser.add_argument("--depth", type=str, choices=["quick", "standard", "deep"], default="standard")
    parser.add_argument("--tenant_id", type=str, help="Tenant identifier")
    parser.add_argument("--execution_mode", type=str, choices=["suggest", "preview", "execute"], default="suggest")
    parser.add_argument("--output", type=str, help="Output file path (JSON)")
    
    args = parser.parse_args()
    
    # Build inputs
    inputs = {
        "client_id": args.client_id,
        "company_name": args.company_name,
        "website_url": args.website_url,
        "depth": args.depth,
        "execution_mode": args.execution_mode
    }
    
    if args.additional_urls:
        inputs["additional_urls"] = args.additional_urls.split(",")
    if args.industry:
        inputs["industry"] = args.industry
    if args.tenant_id:
        inputs["tenant_id"] = args.tenant_id
    
    # Run skill
    result = run_research_company(inputs)
    
    # Output
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Output saved to {args.output}")
    else:
        print(json.dumps(result, indent=2, default=str))
    
    # Exit with appropriate code
    sys.exit(0 if result["status"] in ["success", "review"] else 1)


if __name__ == "__main__":
    main()
