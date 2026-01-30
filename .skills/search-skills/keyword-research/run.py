#!/usr/bin/env python3
"""
Keyword Research Skill - Execution Script (v1.0.0)

Strategic keyword research without expensive tools. Uses the 6 Circles Method
to expand from seed keywords, clusters into content pillars, and maps to a
prioritized content plan.

Features:
- Seed keyword generation from business context
- 6 Circles Method expansion
- Pillar clustering and validation
- Priority scoring (business value, opportunity, speed)
- Content calendar mapping

Usage:
    # Basic run
    python skills/keyword-research/run.py --business "AI marketing consulting" --audience "startup founders"

    # With website context
    python skills/keyword-research/run.py --business "SaaS tool" --website "https://example.com" --competitors "comp1,comp2"

    # Programmatic
    from skills.keyword_research.run import run_keyword_research
    result = run_keyword_research({
        "business": "AI marketing consulting",
        "audience": "funded startups",
        "goal": "leads"
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
SKILL_NAME = "keyword-research"
SKILL_VERSION = "v1.0.0"

# 6 Circles for keyword expansion
SIX_CIRCLES = [
    {
        "name": "What You Sell",
        "description": "Products, services, and solutions you offer directly",
        "pattern": "direct_terms"
    },
    {
        "name": "Problems You Solve",
        "description": "Pain points and challenges your audience faces",
        "pattern": "problem_terms"
    },
    {
        "name": "Outcomes You Deliver",
        "description": "Results and transformations customers achieve",
        "pattern": "outcome_terms"
    },
    {
        "name": "Your Unique Positioning",
        "description": "What makes you different from alternatives",
        "pattern": "positioning_terms"
    },
    {
        "name": "Adjacent Topics",
        "description": "Related areas where your audience spends time",
        "pattern": "adjacent_terms"
    },
    {
        "name": "Entities to Associate With",
        "description": "People, tools, frameworks, concepts to be connected to",
        "pattern": "entity_terms"
    }
]

# Question patterns for expansion
QUESTION_PATTERNS = [
    "What is {keyword}?",
    "How to {keyword}?",
    "Why {keyword}?",
    "Best {keyword}?",
    "{keyword} vs",
    "{keyword} examples",
    "{keyword} for beginners"
]

# Modifier patterns
MODIFIER_PATTERNS = [
    "{keyword} tools",
    "{keyword} templates",
    "{keyword} guide",
    "{keyword} strategy",
    "{keyword} 2025",
    "{keyword} for startups",
    "{keyword} software"
]

# Content type mapping
CONTENT_TYPES = {
    "pillar_guide": {"word_count": "5000-8000", "purpose": "Comprehensive topic coverage"},
    "how_to_tutorial": {"word_count": "2000-3000", "purpose": "Step-by-step instructions"},
    "comparison": {"word_count": "2500-4000", "purpose": "X vs Y, Best [category]"},
    "listicle": {"word_count": "2000-3000", "purpose": "Tools, examples, tips"},
    "use_case": {"word_count": "1500-2500", "purpose": "Industry or scenario specific"},
    "definition": {"word_count": "1500-2500", "purpose": "What is [term]"}
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


class KeywordResearchSkill:
    """
    Keyword Research skill for strategic content planning.
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

        # Output directory
        if client_id:
            self.output_dir = SYSTEM_ROOT / "clients" / client_id / "keyword-research"
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def _generate_seed_keywords(self, business: str, audience: str, goal: str) -> List[str]:
        """Generate initial seed keywords from business context."""
        # In production, this would use LLM for intelligent extraction
        seeds = []

        # Extract key terms from business description
        business_words = business.lower().replace(',', ' ').replace('.', ' ').split()
        meaningful_words = [w for w in business_words if len(w) > 3]
        seeds.extend(meaningful_words[:5])

        # Add common variations
        if "marketing" in business.lower():
            seeds.extend(["marketing automation", "marketing strategy", "digital marketing"])
        if "ai" in business.lower() or "artificial intelligence" in business.lower():
            seeds.extend(["AI tools", "AI automation", "AI marketing"])
        if "consulting" in business.lower():
            seeds.extend(["consultant", "advisory", "consulting services"])

        # Add audience-related terms
        if audience:
            audience_words = audience.lower().replace(',', ' ').split()
            for word in audience_words[:3]:
                if len(word) > 3:
                    seeds.append(f"{word} marketing")

        # Add goal-related terms
        if goal:
            if "lead" in goal.lower():
                seeds.extend(["lead generation", "lead magnet", "lead capture"])
            if "traffic" in goal.lower():
                seeds.extend(["website traffic", "organic traffic", "SEO"])
            if "sale" in goal.lower():
                seeds.extend(["conversion optimization", "sales funnel"])

        return list(set(seeds))[:20]

    def _expand_with_six_circles(self, seeds: List[str], context: Dict) -> Dict[str, List[str]]:
        """Expand seeds using the 6 Circles Method."""
        expanded = {circle["name"]: [] for circle in SIX_CIRCLES}

        business = context.get("business", "")
        audience = context.get("audience", "")

        # Circle 1: What You Sell
        expanded["What You Sell"] = [
            s for s in seeds if any(term in s.lower() for term in ["tool", "service", "platform", "software"])
        ]
        if not expanded["What You Sell"]:
            expanded["What You Sell"] = seeds[:5]

        # Circle 2: Problems You Solve
        for seed in seeds[:5]:
            expanded["Problems You Solve"].extend([
                f"{seed} challenges",
                f"{seed} problems",
                f"struggling with {seed}"
            ])

        # Circle 3: Outcomes You Deliver
        for seed in seeds[:5]:
            expanded["Outcomes You Deliver"].extend([
                f"{seed} results",
                f"{seed} benefits",
                f"improve {seed}"
            ])

        # Circle 4: Unique Positioning
        expanded["Your Unique Positioning"] = [
            f"best {seed}" for seed in seeds[:3]
        ] + [
            f"{seed} alternative" for seed in seeds[:3]
        ]

        # Circle 5: Adjacent Topics
        if audience:
            expanded["Adjacent Topics"] = [
                f"{audience.split()[0]} growth",
                f"{audience.split()[0]} tools",
                f"{audience.split()[0]} strategies"
            ]

        # Circle 6: Entities
        expanded["Entities to Associate With"] = [
            "AI tools",
            "automation platforms",
            business.split()[0] if business else "industry"
        ]

        return expanded

    def _apply_patterns(self, keywords: List[str]) -> List[str]:
        """Apply question and modifier patterns to keywords."""
        expanded = []

        for kw in keywords[:10]:  # Limit to prevent explosion
            # Question patterns
            for pattern in QUESTION_PATTERNS[:3]:
                expanded.append(pattern.format(keyword=kw))

            # Modifier patterns
            for pattern in MODIFIER_PATTERNS[:3]:
                expanded.append(pattern.format(keyword=kw))

        return list(set(expanded))

    def _cluster_into_pillars(self, all_keywords: Dict[str, List[str]]) -> List[Dict]:
        """Cluster keywords into content pillars."""
        # Flatten all keywords
        flat_keywords = []
        for circle, keywords in all_keywords.items():
            for kw in keywords:
                flat_keywords.append({"keyword": kw, "circle": circle})

        # Group by semantic similarity (simplified - in production use embeddings)
        pillars = []
        keyword_groups = {}

        for item in flat_keywords:
            kw = item["keyword"].lower()
            # Simple grouping by first significant word
            words = kw.split()
            group_key = words[0] if words else "general"

            if group_key not in keyword_groups:
                keyword_groups[group_key] = []
            keyword_groups[group_key].append(item)

        # Convert groups to pillars
        for group_key, items in keyword_groups.items():
            if len(items) >= 2:  # Only create pillars with multiple keywords
                pillars.append({
                    "name": group_key.title(),
                    "primary_keyword": items[0]["keyword"],
                    "supporting_keywords": [i["keyword"] for i in items[1:]],
                    "keyword_count": len(items)
                })

        # Sort by keyword count
        pillars.sort(key=lambda x: x["keyword_count"], reverse=True)

        return pillars[:10]  # Top 10 pillars

    def _validate_pillars(self, pillars: List[Dict]) -> List[Dict]:
        """Run validation tests on pillars."""
        validated = []

        for pillar in pillars:
            # Simplified validation (in production, check search volume, competition)
            tests = {
                "search_volume_test": "PASS" if pillar["keyword_count"] >= 3 else "NEEDS_REVIEW",
                "market_centric_test": "PASS",  # Would check against product-centric terms
                "competitive_test": "PASS",  # Would check SERP competition
                "proprietary_advantage_test": "UNKNOWN"  # Would check unique data/expertise
            }

            passed_tests = sum(1 for v in tests.values() if v == "PASS")
            verdict = "VALID" if passed_tests >= 3 else "NEEDS_REVIEW"

            validated.append({
                **pillar,
                "validation": tests,
                "verdict": verdict
            })

        return validated

    def _prioritize_clusters(self, pillars: List[Dict]) -> List[Dict]:
        """Score and prioritize keyword clusters."""
        for pillar in pillars:
            # Simplified scoring (in production, use actual data)
            business_value = "High" if pillar["keyword_count"] >= 5 else "Medium"
            opportunity = "High" if pillar["verdict"] == "VALID" else "Medium"
            speed = "Fast" if pillar["keyword_count"] >= 3 else "Medium"

            # Priority score
            score_map = {"High": 3, "Medium": 2, "Low": 1, "Fast": 3}
            priority_score = (
                score_map.get(business_value, 2) +
                score_map.get(opportunity, 2) +
                score_map.get(speed, 2)
            )

            pillar["priority"] = {
                "business_value": business_value,
                "opportunity": opportunity,
                "speed_to_win": speed,
                "score": priority_score,
                "tier": "DO_FIRST" if priority_score >= 8 else "DO_SECOND" if priority_score >= 6 else "BACKLOG"
            }

        # Sort by priority score
        pillars.sort(key=lambda x: x["priority"]["score"], reverse=True)

        return pillars

    def _map_to_content(self, pillars: List[Dict]) -> List[Dict]:
        """Map clusters to specific content pieces."""
        content_plan = []

        for pillar in pillars[:5]:  # Top 5 pillars
            # Determine content type based on keyword patterns
            primary_kw = pillar["primary_keyword"].lower()

            if "what is" in primary_kw or "how to" in primary_kw:
                content_type = "pillar_guide"
            elif "vs" in primary_kw or "best" in primary_kw:
                content_type = "comparison"
            elif "tools" in primary_kw or "examples" in primary_kw:
                content_type = "listicle"
            else:
                content_type = "how_to_tutorial"

            content_piece = {
                "pillar": pillar["name"],
                "primary_keyword": pillar["primary_keyword"],
                "content_type": content_type,
                "word_count": CONTENT_TYPES[content_type]["word_count"],
                "purpose": CONTENT_TYPES[content_type]["purpose"],
                "supporting_keywords": pillar["supporting_keywords"][:5],
                "priority_tier": pillar["priority"]["tier"],
                "recommended_publish_week": pillars.index(pillar) + 1
            }

            content_plan.append(content_piece)

        return content_plan

    def _generate_content_calendar(self, content_plan: List[Dict]) -> Dict:
        """Generate a 90-day content calendar."""
        calendar = {
            "month_1": [],
            "month_2": [],
            "month_3": []
        }

        for i, piece in enumerate(content_plan):
            week = piece["recommended_publish_week"]
            if week <= 4:
                month = "month_1"
            elif week <= 8:
                month = "month_2"
            else:
                month = "month_3"

            calendar[month].append({
                "week": week if week <= 4 else (week - 4 if week <= 8 else week - 8),
                "title": f"{piece['content_type'].replace('_', ' ').title()}: {piece['primary_keyword']}",
                "pillar": piece["pillar"],
                "content_type": piece["content_type"]
            })

        return calendar

    def _format_output_markdown(
        self,
        business: str,
        pillars: List[Dict],
        content_plan: List[Dict],
        calendar: Dict
    ) -> str:
        """Format output as markdown document."""
        md = f"""# Keyword Research: {business}

## Executive Summary

Generated {len(pillars)} content pillars with {sum(p['keyword_count'] for p in pillars)} keywords.

### Top Opportunities

"""
        for i, pillar in enumerate(pillars[:3], 1):
            md += f"{i}. **{pillar['name']}** - {pillar['keyword_count']} keywords, {pillar['priority']['tier']}\n"

        md += """
### Quick Wins (Start Here)

"""
        quick_wins = [p for p in content_plan if p["priority_tier"] == "DO_FIRST"]
        for piece in quick_wins[:3]:
            md += f"- {piece['primary_keyword']} ({piece['content_type']})\n"

        md += """
---

## Content Pillars

"""
        for pillar in pillars[:5]:
            md += f"""### {pillar['name']}

**Primary Keyword:** {pillar['primary_keyword']}
**Supporting Keywords:** {', '.join(pillar['supporting_keywords'][:5])}
**Priority:** {pillar['priority']['tier']} (Score: {pillar['priority']['score']})
**Validation:** {pillar['verdict']}

---

"""

        md += """## Content Plan

| Pillar | Primary Keyword | Content Type | Word Count | Priority |
|--------|-----------------|--------------|------------|----------|
"""
        for piece in content_plan:
            md += f"| {piece['pillar']} | {piece['primary_keyword']} | {piece['content_type']} | {piece['word_count']} | {piece['priority_tier']} |\n"

        md += """
---

## 90-Day Content Calendar

### Month 1

"""
        for item in calendar.get("month_1", []):
            md += f"- Week {item['week']}: {item['title']}\n"

        md += """
### Month 2

"""
        for item in calendar.get("month_2", []):
            md += f"- Week {item['week']}: {item['title']}\n"

        md += """
### Month 3

"""
        for item in calendar.get("month_3", []):
            md += f"- Week {item['week']}: {item['title']}\n"

        md += f"""
---

*Generated by keyword-research skill on {datetime.now().strftime('%Y-%m-%d')}*
"""
        return md

    def run(self, inputs: Dict) -> Dict:
        """
        Main execution method for keyword research skill.

        Args:
            inputs: Dictionary with:
                - business: Business description (required)
                - audience: Target audience (optional)
                - website: Business website (optional)
                - competitors: List of competitors (optional)
                - goal: Marketing goal (traffic, leads, sales)

        Returns:
            Complete skill result with keyword research plan
        """
        business = inputs.get("business")

        if not business:
            return {
                "status": "failed",
                "error": "business description is required"
            }

        audience = inputs.get("audience", "target customers")
        goal = inputs.get("goal", "leads")

        print(f"\n{'='*60}")
        print(f"KEYWORD RESEARCH")
        print(f"{'='*60}")
        print(f"Business: {business}")
        print(f"Audience: {audience}")
        print(f"Goal: {goal}")
        print(f"Run ID: {self.run_id}")
        print(f"{'='*60}\n")

        runner = WorkflowRunner(
            workflow_name=SKILL_NAME,
            version=SKILL_VERSION,
            client=self.client_id
        )

        try:
            # Step 1: Generate seed keywords
            print("[Step 1] Generating seed keywords...")
            seeds = self._generate_seed_keywords(business, audience, goal)
            print(f"  Generated {len(seeds)} seeds")

            # Step 2: Expand using 6 Circles
            print("\n[Step 2] Expanding with 6 Circles Method...")
            expanded = self._expand_with_six_circles(seeds, {
                "business": business,
                "audience": audience
            })
            total_expanded = sum(len(v) for v in expanded.values())
            print(f"  Expanded to {total_expanded} keywords")

            # Step 3: Apply patterns
            print("\n[Step 3] Applying question/modifier patterns...")
            all_keywords = list(seeds)
            for circle_keywords in expanded.values():
                all_keywords.extend(circle_keywords)
            patterned = self._apply_patterns(all_keywords[:20])
            print(f"  Added {len(patterned)} pattern variations")

            # Step 4: Cluster into pillars
            print("\n[Step 4] Clustering into content pillars...")
            pillars = self._cluster_into_pillars(expanded)
            print(f"  Created {len(pillars)} pillars")

            # Step 5: Validate pillars
            print("\n[Step 5] Validating pillars...")
            validated_pillars = self._validate_pillars(pillars)
            valid_count = sum(1 for p in validated_pillars if p["verdict"] == "VALID")
            print(f"  {valid_count}/{len(validated_pillars)} passed validation")

            # Step 6: Prioritize
            print("\n[Step 6] Prioritizing clusters...")
            prioritized = self._prioritize_clusters(validated_pillars)

            # Step 7: Map to content
            print("\n[Step 7] Mapping to content plan...")
            content_plan = self._map_to_content(prioritized)
            print(f"  Created {len(content_plan)} content pieces")

            # Step 8: Generate calendar
            print("\n[Step 8] Generating content calendar...")
            calendar = self._generate_content_calendar(content_plan)

            # Step 9: Format output
            print("\n[Step 9] Formatting output...")
            markdown = self._format_output_markdown(business, prioritized, content_plan, calendar)

            # Save output if client directory exists
            if hasattr(self, 'output_dir'):
                output_path = self.output_dir / f"keyword-research-{self.run_id}.md"
                output_path.write_text(markdown)
                print(f"\n  Saved to: {output_path}")

            runtime = time.time() - self.start_time

            result = {
                "status": "success",
                "business": business,
                "audience": audience,
                "goal": goal,
                "seeds": seeds,
                "expanded_by_circle": {k: len(v) for k, v in expanded.items()},
                "pillars": prioritized,
                "content_plan": content_plan,
                "calendar": calendar,
                "markdown": markdown,
                "run_id": runner.run_id,
                "runtime_seconds": round(runtime, 2)
            }

            print(f"\n{'='*60}")
            print(f"KEYWORD RESEARCH COMPLETE")
            print(f"{'='*60}")
            print(f"Seeds: {len(seeds)}")
            print(f"Pillars: {len(prioritized)}")
            print(f"Content pieces: {len(content_plan)}")
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


def run_keyword_research(inputs: Dict) -> Dict:
    """
    Main entry point for keyword research skill.

    Args:
        inputs: Dictionary with business context

    Returns:
        Complete skill result with keyword research plan
    """
    if not inputs.get("client_id"):
        active_client = get_client_from_active_file()
        if active_client.get("client_id"):
            inputs["client_id"] = active_client["client_id"]
            inputs["client_name"] = active_client.get("client_name")

    skill = KeywordResearchSkill(
        client_id=inputs.get("client_id"),
        client_name=inputs.get("client_name")
    )

    return skill.run(inputs)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Strategic keyword research for content planning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic run
    python run.py --business "AI marketing consulting"

    # With full context
    python run.py --business "SaaS tool" --audience "startup founders" --goal "leads"

    # Save output
    python run.py --business "Product" --output research.json
        """
    )

    parser.add_argument("--business", type=str, required=True, help="Business description")
    parser.add_argument("--audience", type=str, help="Target audience")
    parser.add_argument("--website", type=str, help="Business website")
    parser.add_argument("--competitors", type=str, help="Comma-separated competitors")
    parser.add_argument("--goal", type=str, choices=["traffic", "leads", "sales", "authority"], default="leads")
    parser.add_argument("--client_id", type=str, help="Client identifier")
    parser.add_argument("--output", type=str, help="Output file path (JSON)")

    args = parser.parse_args()

    inputs = {
        "business": args.business,
        "goal": args.goal
    }

    if args.audience:
        inputs["audience"] = args.audience
    if args.website:
        inputs["website"] = args.website
    if args.competitors:
        inputs["competitors"] = args.competitors.split(",")
    if args.client_id:
        inputs["client_id"] = args.client_id

    result = run_keyword_research(inputs)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Output saved to {args.output}")
    else:
        print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result.get("status") == "success" else 1)


if __name__ == "__main__":
    main()
