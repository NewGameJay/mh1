#!/usr/bin/env python3
"""
GTM Engineering Skill - Execution Script (v1.0.0)

Executes Crustdata APIs for TAM mapping, decision maker discovery, and watcher configuration.
This is a data retrieval skill for GTM data collection.

Usage:
    python skills/gtm-engineering/run.py --query_type tam --industry "SaaS" --company_size "50-500"

    from skills.gtm_engineering.run import run_gtm_engineering
    result = run_gtm_engineering({"query_type": "tam", "industry": "SaaS"})
"""

import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

SKILL_ROOT = Path(__file__).parent
SYSTEM_ROOT = SKILL_ROOT.parent.parent
sys.path.insert(0, str(SYSTEM_ROOT / "lib"))

try:
    from runner import WorkflowRunner, RunStatus
except ImportError:
    class RunStatus:
        SUCCESS = "success"
        FAILED = "failed"
    class WorkflowRunner:
        def __init__(self, **kwargs): self.run_id = str(uuid.uuid4())[:8]
        def complete(self, status, evaluation=None): return {}

SKILL_NAME = "gtm-engineering"
SKILL_VERSION = "v1.0.0"

# Crustdata API endpoints
CRUSTDATA_COMPANY_URL = "https://api.crustdata.com/screener/companydb/search"
CRUSTDATA_PEOPLE_URL = "https://api.crustdata.com/screener/person/search"

# Standard company size mappings
COMPANY_SIZE_FILTERS = {
    "startup": {"min_employees": 1, "max_employees": 50},
    "small": {"min_employees": 11, "max_employees": 50},
    "mid-market": {"min_employees": 51, "max_employees": 500},
    "enterprise": {"min_employees": 501, "max_employees": 10000},
    "50-500": {"min_employees": 50, "max_employees": 500},
    "100-1000": {"min_employees": 100, "max_employees": 1000},
    "500+": {"min_employees": 500, "max_employees": None}
}

# Seniority levels for decision maker mapping
SENIORITY_LEVELS = ["c_suite", "vp", "director", "manager"]


class GTMEngineeringSkill:
    """GTM Engineering skill for TAM mapping and decision maker discovery."""

    def __init__(self, client_id: str = None, client_name: str = None):
        self.client_id = client_id or "standalone"
        self.client_name = client_name
        self.run_id = str(uuid.uuid4())[:8]
        self.start_time = time.time()
        self.api_key = os.getenv("CRUSTDATA_API_KEY")
        self.credits_used = 0

        if client_id:
            self.output_dir = SYSTEM_ROOT / "clients" / client_id / "gtm"
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def _call_crustdata_api(self, endpoint: str, payload: Dict) -> Dict:
        """Call Crustdata API with given payload."""
        if not self.api_key:
            return self._generate_sample_response(endpoint, payload)

        try:
            result = subprocess.run(
                [
                    "curl", "-s", "-X", "POST",
                    endpoint,
                    "-H", f"Authorization: Bearer {self.api_key}",
                    "-H", "Content-Type: application/json",
                    "-d", json.dumps(payload)
                ],
                capture_output=True,
                text=True,
                timeout=60
            )

            self.credits_used += 1

            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {"error": result.stderr}

        except Exception as e:
            return {"error": str(e)}

    def _generate_sample_response(self, endpoint: str, payload: Dict) -> Dict:
        """Generate sample response for development/testing."""
        if "company" in endpoint.lower():
            return {
                "total_count": 2500,
                "companies": [
                    {"name": "Sample Company 1", "employees": 150, "industry": payload.get("industry", "Technology")},
                    {"name": "Sample Company 2", "employees": 300, "industry": payload.get("industry", "Technology")}
                ],
                "source": "sample_data"
            }
        else:
            return {
                "total_count": 500,
                "people": [
                    {"name": "John Doe", "title": "VP Marketing", "company": "Sample Corp"},
                    {"name": "Jane Smith", "title": "CMO", "company": "Tech Inc"}
                ],
                "source": "sample_data"
            }

    def _build_company_filters(self, inputs: Dict) -> Dict:
        """Build Crustdata company search filters."""
        filters = {}

        # Industry filter
        if inputs.get("industry"):
            filters["industry"] = {"contains": [inputs["industry"]]}

        # Company size filter
        size = inputs.get("company_size", "")
        if size in COMPANY_SIZE_FILTERS:
            size_config = COMPANY_SIZE_FILTERS[size]
            if size_config.get("min_employees"):
                filters["employees_min"] = size_config["min_employees"]
            if size_config.get("max_employees"):
                filters["employees_max"] = size_config["max_employees"]

        # Geography filter
        if inputs.get("geography"):
            filters["headquarters_location"] = {"contains": [inputs["geography"]]}

        # Revenue filter
        if inputs.get("min_revenue"):
            filters["annual_revenue_min"] = inputs["min_revenue"]

        # Technology filter
        if inputs.get("technologies"):
            filters["technologies_used"] = {"contains": inputs["technologies"]}

        return filters

    def _build_people_filters(self, inputs: Dict) -> Dict:
        """Build Crustdata people search filters."""
        filters = {}

        # Title filter
        if inputs.get("titles"):
            filters["title"] = {"contains": inputs["titles"]}

        # Seniority filter
        if inputs.get("seniority"):
            filters["seniority"] = {"in": inputs["seniority"]}

        # Department filter
        if inputs.get("department"):
            filters["department"] = {"contains": [inputs["department"]]}

        return filters

    def _run_tam_mapping(self, inputs: Dict) -> Dict:
        """Run TAM (Total Addressable Market) mapping."""
        filters = self._build_company_filters(inputs)

        # First, get total count with limit=1 (1 credit)
        payload = {
            "filters": filters,
            "limit": 1
        }

        print("  [Querying company count...]")
        result = self._call_crustdata_api(CRUSTDATA_COMPANY_URL, payload)

        total_count = result.get("total_count", 0)

        # Calculate TAM
        avg_deal_size = inputs.get("avg_deal_size", 50000)
        tam_value = total_count * avg_deal_size

        return {
            "query_type": "tam",
            "filters_applied": filters,
            "total_companies": total_count,
            "avg_deal_size": avg_deal_size,
            "tam_value": tam_value,
            "tam_formatted": f"${tam_value:,.0f}",
            "sample_companies": result.get("companies", []),
            "credits_used": self.credits_used,
            "source": result.get("source", "api")
        }

    def _run_decision_maker_discovery(self, inputs: Dict) -> Dict:
        """Run decision maker discovery."""
        company_filters = self._build_company_filters(inputs)
        people_filters = self._build_people_filters(inputs)

        results_by_seniority = {}
        total_decision_makers = 0

        # Query each seniority level
        for seniority in SENIORITY_LEVELS:
            print(f"  [Querying {seniority} level...]")

            payload = {
                "filters": {
                    **company_filters,
                    "seniority": {"in": [seniority]},
                    **people_filters
                },
                "limit": 1
            }

            result = self._call_crustdata_api(CRUSTDATA_PEOPLE_URL, payload)
            count = result.get("total_count", 0)

            results_by_seniority[seniority] = {
                "count": count,
                "sample": result.get("people", [])[:2]
            }
            total_decision_makers += count

        return {
            "query_type": "decision_makers",
            "company_filters": company_filters,
            "people_filters": people_filters,
            "total_decision_makers": total_decision_makers,
            "by_seniority": results_by_seniority,
            "credits_used": self.credits_used,
            "source": "api" if self.api_key else "sample_data"
        }

    def _format_output_markdown(self, result: Dict) -> str:
        """Format GTM results as markdown."""
        query_type = result.get("query_type", "unknown")

        md = f"""# GTM Engineering Report

**Query Type:** {query_type.upper()}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Credits Used:** {result.get('credits_used', 0)}

---

"""
        if query_type == "tam":
            md += f"""## TAM Analysis

**Total Addressable Market:** {result.get('tam_formatted', 'N/A')}

| Metric | Value |
|--------|-------|
| Total Companies | {result.get('total_companies', 0):,} |
| Avg Deal Size | ${result.get('avg_deal_size', 0):,} |
| TAM Value | {result.get('tam_formatted', 'N/A')} |

### Filters Applied

```json
{json.dumps(result.get('filters_applied', {}), indent=2)}
```

### Sample Companies

"""
            for company in result.get('sample_companies', [])[:5]:
                md += f"- **{company.get('name', 'N/A')}** - {company.get('employees', 0)} employees\n"

        elif query_type == "decision_makers":
            md += f"""## Decision Maker Analysis

**Total Decision Makers:** {result.get('total_decision_makers', 0):,}

### By Seniority Level

| Level | Count |
|-------|-------|
"""
            for level, data in result.get('by_seniority', {}).items():
                md += f"| {level} | {data.get('count', 0):,} |\n"

            md += """
### Sample Decision Makers

"""
            for level, data in result.get('by_seniority', {}).items():
                for person in data.get('sample', []):
                    md += f"- **{person.get('name', 'N/A')}** - {person.get('title', 'N/A')} at {person.get('company', 'N/A')}\n"

        md += f"""
---

## Next Steps

1. **Refine Filters** - Adjust industry/size/geography for more precision
2. **Export Data** - Use full API calls to get complete company lists
3. **Configure Watchers** - Set up alerts for new companies matching criteria
4. **Prioritize Outreach** - Start with highest-fit segments

---

*Generated by gtm-engineering skill on {datetime.now().strftime('%Y-%m-%d')}*
"""
        return md

    def run(self, inputs: Dict) -> Dict:
        """Main execution method."""
        query_type = inputs.get("query_type", "tam")

        print(f"\n{'='*60}")
        print(f"GTM ENGINEERING")
        print(f"{'='*60}")
        print(f"Query Type: {query_type}")
        print(f"Industry: {inputs.get('industry', 'All')}")
        print(f"Company Size: {inputs.get('company_size', 'All')}")
        print(f"API Key: {'✓ Set' if self.api_key else '✗ Not set (using sample data)'}")
        print(f"{'='*60}\n")

        runner = WorkflowRunner(
            workflow_name=SKILL_NAME,
            version=SKILL_VERSION,
            client=self.client_id
        )

        try:
            # Run appropriate query
            if query_type == "tam":
                print("[Running TAM Mapping...]")
                result = self._run_tam_mapping(inputs)
            elif query_type == "decision_makers":
                print("[Running Decision Maker Discovery...]")
                result = self._run_decision_maker_discovery(inputs)
            else:
                print("[Running Both TAM + Decision Makers...]")
                tam_result = self._run_tam_mapping(inputs)
                dm_result = self._run_decision_maker_discovery(inputs)
                result = {
                    "query_type": "combined",
                    "tam": tam_result,
                    "decision_makers": dm_result,
                    "credits_used": self.credits_used
                }

            # Format output
            markdown = self._format_output_markdown(result)
            result["markdown"] = markdown

            # Save output
            if hasattr(self, 'output_dir'):
                md_path = self.output_dir / f"gtm-{query_type}-{self.run_id}.md"
                md_path.write_text(markdown)

                json_path = self.output_dir / f"gtm-{query_type}-{self.run_id}.json"
                json_path.write_text(json.dumps(result, indent=2, default=str))

                print(f"\n  Saved to: {self.output_dir}")

            runtime = time.time() - self.start_time

            final_result = {
                "status": "success",
                "data": result,
                "credits_used": self.credits_used,
                "run_id": runner.run_id,
                "runtime_seconds": round(runtime, 2)
            }

            print(f"\n{'='*60}")
            print(f"GTM ANALYSIS COMPLETE")
            print(f"  Credits Used: {self.credits_used}")
            print(f"{'='*60}\n")

            runner.complete(RunStatus.SUCCESS)
            return final_result

        except Exception as e:
            runner.complete(RunStatus.FAILED)
            return {"status": "failed", "error": str(e), "run_id": runner.run_id}


def run_gtm_engineering(inputs: Dict) -> Dict:
    """Main entry point for GTM engineering skill."""
    skill = GTMEngineeringSkill(
        client_id=inputs.get("client_id"),
        client_name=inputs.get("client_name")
    )
    return skill.run(inputs)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="GTM data collection via Crustdata API")
    parser.add_argument("--query_type", type=str, default="tam",
                       choices=["tam", "decision_makers", "both"], help="Type of query")
    parser.add_argument("--industry", type=str, help="Industry filter")
    parser.add_argument("--company_size", type=str, help="Company size filter")
    parser.add_argument("--geography", type=str, help="Geography filter")
    parser.add_argument("--titles", type=str, help="Comma-separated job titles")
    parser.add_argument("--avg_deal_size", type=int, default=50000, help="Average deal size for TAM")
    parser.add_argument("--client_id", type=str, help="Client identifier")
    parser.add_argument("--output", type=str, help="Output file path (JSON)")

    args = parser.parse_args()

    inputs = {
        "query_type": args.query_type,
        "avg_deal_size": args.avg_deal_size
    }

    if args.industry: inputs["industry"] = args.industry
    if args.company_size: inputs["company_size"] = args.company_size
    if args.geography: inputs["geography"] = args.geography
    if args.titles: inputs["titles"] = args.titles.split(",")
    if args.client_id: inputs["client_id"] = args.client_id

    result = run_gtm_engineering(inputs)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2, default=str)
    else:
        print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result.get("status") == "success" else 1)


if __name__ == "__main__":
    main()
