"""
Pre-flight Checker for MH1 Skills

Checks that all requirements are met before executing a skill:
- Platform connections (MCPs, APIs)
- Client data (files in clients/{id}/)
- User inputs

Returns what's missing with setup guides.
"""

import os
import yaml
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Platform setup guides
PLATFORM_GUIDES = {
    "hubspot": {
        "name": "HubSpot CRM",
        "type": "crm",
        "setup_steps": [
            "1. Go to HubSpot Settings > Integrations > Private Apps",
            "2. Create a new private app with these scopes: crm.objects.contacts.read, crm.objects.deals.read",
            "3. Copy the access token",
            "4. Add to .env: HUBSPOT_API_KEY=your-token",
            "5. Or add to clients/{client_id}/config/datasources.yaml under 'crm.api_key'"
        ],
        "docs_url": "https://developers.hubspot.com/docs/api/private-apps",
        "env_var": "HUBSPOT_API_KEY",
        "config_path": "datasources.yaml > crm.api_key"
    },
    "salesforce": {
        "name": "Salesforce CRM",
        "type": "crm",
        "setup_steps": [
            "1. Go to Salesforce Setup > Apps > App Manager",
            "2. Create a new Connected App with OAuth enabled",
            "3. Note the Consumer Key and Consumer Secret",
            "4. Add to .env: SALESFORCE_CLIENT_ID, SALESFORCE_CLIENT_SECRET, SALESFORCE_USERNAME, SALESFORCE_PASSWORD",
            "5. Or add to clients/{client_id}/config/datasources.yaml under 'crm'"
        ],
        "docs_url": "https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_oauth_and_connected_apps.htm",
        "env_var": "SALESFORCE_CLIENT_ID",
        "config_path": "datasources.yaml > crm"
    },
    "snowflake": {
        "name": "Snowflake Data Warehouse",
        "type": "warehouse",
        "setup_steps": [
            "1. Get your Snowflake account identifier (e.g., abc123.us-east-1)",
            "2. Create a user with appropriate permissions or use existing credentials",
            "3. Add to .env:",
            "   SNOWFLAKE_ACCOUNT=your-account",
            "   SNOWFLAKE_USER=your-user",
            "   SNOWFLAKE_PASSWORD=your-password",
            "   SNOWFLAKE_DATABASE=your-database",
            "   SNOWFLAKE_SCHEMA=your-schema",
            "4. Or add to clients/{client_id}/config/datasources.yaml under 'warehouse'"
        ],
        "docs_url": "https://docs.snowflake.com/en/user-guide/admin-account-identifier",
        "env_var": "SNOWFLAKE_ACCOUNT",
        "config_path": "datasources.yaml > warehouse"
    },
    "bigquery": {
        "name": "Google BigQuery",
        "type": "warehouse",
        "setup_steps": [
            "1. Go to Google Cloud Console > IAM & Admin > Service Accounts",
            "2. Create a service account with BigQuery User role",
            "3. Download the JSON key file",
            "4. Add to .env: GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json",
            "5. Or add to clients/{client_id}/config/datasources.yaml under 'warehouse'"
        ],
        "docs_url": "https://cloud.google.com/bigquery/docs/authentication",
        "env_var": "GOOGLE_APPLICATION_CREDENTIALS",
        "config_path": "datasources.yaml > warehouse"
    },
    "firecrawl": {
        "name": "Firecrawl Web Scraper",
        "type": "mcp",
        "setup_steps": [
            "1. Sign up at https://firecrawl.dev",
            "2. Get your API key from the dashboard",
            "3. Add to .env: FIRECRAWL_API_KEY=your-key",
            "4. Firecrawl MCP should auto-connect when key is present"
        ],
        "docs_url": "https://firecrawl.dev/docs",
        "env_var": "FIRECRAWL_API_KEY",
        "config_path": ".env > FIRECRAWL_API_KEY"
    },
    "firebase": {
        "name": "Firebase/Firestore",
        "type": "database",
        "setup_steps": [
            "1. Go to Firebase Console > Project Settings > Service Accounts",
            "2. Generate new private key (downloads JSON file)",
            "3. Add to .env: GOOGLE_APPLICATION_CREDENTIALS=/path/to/firebase-key.json",
            "4. Or set FIREBASE_SERVICE_ACCOUNT_KEY with the JSON content"
        ],
        "docs_url": "https://firebase.google.com/docs/admin/setup",
        "env_var": "GOOGLE_APPLICATION_CREDENTIALS",
        "config_path": ".env > GOOGLE_APPLICATION_CREDENTIALS"
    },
    "perplexity": {
        "name": "Perplexity AI Search",
        "type": "mcp",
        "setup_steps": [
            "1. Sign up at https://perplexity.ai",
            "2. Go to API settings and generate a key",
            "3. Add to .env: PERPLEXITY_API_KEY=your-key"
        ],
        "docs_url": "https://docs.perplexity.ai",
        "env_var": "PERPLEXITY_API_KEY",
        "config_path": ".env > PERPLEXITY_API_KEY"
    }
}


@dataclass
class Requirement:
    """A single requirement for a skill."""
    name: str
    type: str  # 'platform', 'data', 'input'
    required: bool
    description: str
    setup_guide: list = field(default_factory=list)
    docs_url: str = ""
    status: str = "unknown"  # 'met', 'missing', 'unknown'


@dataclass
class PreflightResult:
    """Result of a pre-flight check."""
    skill_name: str
    can_execute: bool
    missing_requirements: list  # List of Requirement
    met_requirements: list  # List of Requirement
    user_actions_needed: list  # Human-readable actions
    setup_guides: dict  # platform -> guide


class PreflightChecker:
    """Checks requirements before skill execution."""

    def __init__(self, client_id: str = None):
        self.client_id = client_id
        self.client_dir = PROJECT_ROOT / "clients" / client_id if client_id else None
        self.skills_cache = {}
        self._load_skills()

    def _load_skills(self):
        """Load skill definitions."""
        for dirname in [".skills", "skills"]:
            skills_dir = PROJECT_ROOT / dirname
            if not skills_dir.exists():
                continue
            for category_dir in skills_dir.iterdir():
                if not category_dir.is_dir() or category_dir.name.startswith("_"):
                    continue
                for skill_dir in category_dir.iterdir():
                    if not skill_dir.is_dir() or "TEMPLATE" in skill_dir.name:
                        continue
                    skill_md = skill_dir / "SKILL.md"
                    if skill_md.exists():
                        self._parse_skill(skill_md)

    def _parse_skill(self, skill_path: Path):
        """Parse a skill definition."""
        try:
            content = skill_path.read_text()
            if not content.startswith("---"):
                return

            parts = content.split("---", 2)
            if len(parts) < 3:
                return

            frontmatter = yaml.safe_load(parts[1])
            name = frontmatter.get("name", skill_path.parent.name)
            self.skills_cache[name] = {
                "name": name,
                "path": skill_path,
                "frontmatter": frontmatter,
                "body": parts[2].strip(),
            }
        except Exception:
            pass

    def get_skill_requirements(self, skill_name: str) -> list:
        """Extract requirements from a skill definition."""
        skill = self.skills_cache.get(skill_name)
        if not skill:
            return []

        fm = skill["frontmatter"]
        requirements = []

        # Check requires_mcp (platform connections)
        for mcp in fm.get("requires_mcp", []):
            mcp_lower = mcp.lower()
            guide = PLATFORM_GUIDES.get(mcp_lower, {})
            requirements.append(Requirement(
                name=mcp,
                type="platform",
                required=True,
                description=f"MCP connection to {guide.get('name', mcp)}",
                setup_guide=guide.get("setup_steps", [f"Configure {mcp} MCP"]),
                docs_url=guide.get("docs_url", ""),
            ))

        # Check compatibility (optional platforms)
        for compat in fm.get("compatibility", []):
            compat_lower = compat.lower().replace(" mcp", "").replace(" ", "_")
            guide = PLATFORM_GUIDES.get(compat_lower, {})
            if compat_lower not in [r.name.lower() for r in requirements]:
                requirements.append(Requirement(
                    name=compat,
                    type="platform",
                    required=False,
                    description=f"Compatible with {guide.get('name', compat)}",
                    setup_guide=guide.get("setup_steps", []),
                    docs_url=guide.get("docs_url", ""),
                ))

        # Check inputs (user-provided data)
        for inp in fm.get("inputs", []):
            if isinstance(inp, dict):
                requirements.append(Requirement(
                    name=inp.get("name", "unknown"),
                    type="input",
                    required=inp.get("required", False),
                    description=inp.get("description", ""),
                ))

        # Check data requirements from body (look for ## Requirements section)
        body = skill.get("body", "")
        if "## Requirements" in body or "## Data Requirements" in body:
            # Parse requirements section if it exists
            pass  # Could extract more structured requirements here

        return requirements

    def check_platform_connection(self, platform: str) -> bool:
        """Check if a platform connection is configured."""
        platform_lower = platform.lower().replace(" mcp", "").replace(" ", "_")
        guide = PLATFORM_GUIDES.get(platform_lower, {})

        # Check environment variable
        env_var = guide.get("env_var")
        if env_var and os.environ.get(env_var):
            return True

        # Check client config
        if self.client_dir:
            datasources_path = self.client_dir / "config" / "datasources.yaml"
            if datasources_path.exists():
                try:
                    with open(datasources_path) as f:
                        config = yaml.safe_load(f)

                    # Check based on platform type
                    ptype = guide.get("type", "")
                    if ptype == "crm" and config.get("crm"):
                        return True
                    if ptype == "warehouse" and config.get("warehouse"):
                        return True
                    if platform_lower in str(config).lower():
                        return True
                except Exception:
                    pass

        return False

    def check_client_data(self, data_type: str) -> bool:
        """Check if client has specific data configured."""
        if not self.client_dir:
            return False

        # Check for common data files
        data_files = {
            "contacts": ["contacts.json", "contacts.csv", "crm_export.json"],
            "deals": ["deals.json", "pipeline.json"],
            "company_profile": ["profile.yaml", "company.yaml"],
            "voice_contract": ["voice_contract.md", "voice.yaml"],
        }

        files_to_check = data_files.get(data_type, [data_type])
        data_dir = self.client_dir / "data"
        config_dir = self.client_dir / "config"

        for filename in files_to_check:
            if (data_dir / filename).exists() or (config_dir / filename).exists():
                return True

        return False

    def check(self, skill_name: str, provided_inputs: dict = None) -> PreflightResult:
        """
        Run pre-flight check for a skill.

        Returns what's needed before execution can proceed.
        """
        provided_inputs = provided_inputs or {}
        requirements = self.get_skill_requirements(skill_name)

        met = []
        missing = []
        user_actions = []
        guides = {}

        for req in requirements:
            if req.type == "platform":
                if self.check_platform_connection(req.name):
                    req.status = "met"
                    met.append(req)
                elif req.required:
                    req.status = "missing"
                    missing.append(req)
                    user_actions.append(f"Configure {req.name}: {req.description}")
                    guides[req.name] = {
                        "steps": req.setup_guide,
                        "docs": req.docs_url
                    }

            elif req.type == "input":
                if req.name in provided_inputs:
                    req.status = "met"
                    met.append(req)
                elif req.required:
                    req.status = "missing"
                    missing.append(req)
                    user_actions.append(f"Provide input '{req.name}': {req.description}")

            elif req.type == "data":
                if self.check_client_data(req.name):
                    req.status = "met"
                    met.append(req)
                elif req.required:
                    req.status = "missing"
                    missing.append(req)
                    user_actions.append(f"Upload/configure '{req.name}' data")

        can_execute = len([r for r in missing if r.required]) == 0

        return PreflightResult(
            skill_name=skill_name,
            can_execute=can_execute,
            missing_requirements=missing,
            met_requirements=met,
            user_actions_needed=user_actions,
            setup_guides=guides
        )

    def format_missing_for_user(self, result: PreflightResult) -> str:
        """Format missing requirements as user-friendly message."""
        if result.can_execute:
            return ""

        lines = [
            f"## Cannot execute {result.skill_name}",
            "",
            "The following requirements are missing:",
            ""
        ]

        # Group by type
        platforms = [r for r in result.missing_requirements if r.type == "platform"]
        inputs = [r for r in result.missing_requirements if r.type == "input"]
        data = [r for r in result.missing_requirements if r.type == "data"]

        if platforms:
            lines.append("### Platform Connections Needed")
            for req in platforms:
                lines.append(f"\n**{req.name}** - {req.description}")
                if req.setup_guide:
                    lines.append("\nSetup:")
                    for step in req.setup_guide:
                        lines.append(f"  {step}")
                if req.docs_url:
                    lines.append(f"\nDocs: {req.docs_url}")
                lines.append("")

        if inputs:
            lines.append("### User Inputs Needed")
            for req in inputs:
                lines.append(f"- **{req.name}**: {req.description}")
            lines.append("")

        if data:
            lines.append("### Client Data Needed")
            for req in data:
                lines.append(f"- **{req.name}**: {req.description}")
            lines.append("")

        return "\n".join(lines)


def check_skill_requirements(skill_name: str, client_id: str = None, inputs: dict = None) -> PreflightResult:
    """Convenience function to check skill requirements."""
    checker = PreflightChecker(client_id)
    return checker.check(skill_name, inputs)
