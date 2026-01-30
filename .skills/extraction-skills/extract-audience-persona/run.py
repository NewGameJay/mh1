#!/usr/bin/env python3
"""
Extract Audience Persona Skill - Execution Script (v1.0.0)

Parses audience persona markdown into structured JSON with ICP, buyer personas, and messaging.

Usage:
    python skills/extract-audience-persona/run.py --input context/audience-persona.md

    from skills.extract_audience_persona.run import run_extract_audience_persona
    result = run_extract_audience_persona({"client_id": "abc123"})
"""

import argparse
import json
import re
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

SKILL_NAME = "extract-audience-persona"
SKILL_VERSION = "v1.0.0"


class ExtractAudiencePersonaSkill:
    """Extract structured persona data from markdown documents."""

    def __init__(self, client_id: str = None, client_name: str = None):
        self.client_id = client_id or "standalone"
        self.client_name = client_name
        self.run_id = str(uuid.uuid4())[:8]
        self.start_time = time.time()

        if client_id:
            self.client_dir = SYSTEM_ROOT / "clients" / client_id
        else:
            self.client_dir = None

    def _find_persona_file(self, input_path: str = None) -> Optional[Path]:
        """Find the audience persona file."""
        if input_path:
            path = Path(input_path)
            if path.exists():
                return path

        # Check standard locations
        candidates = [
            self.client_dir / "context" / "audience-persona.md" if self.client_dir else None,
            SYSTEM_ROOT / "inputs" / "audience-persona.md",
            SYSTEM_ROOT / "context" / "audience-persona.md"
        ]

        for path in candidates:
            if path and path.exists():
                return path

        return None

    def _parse_section(self, content: str, section_name: str) -> str:
        """Extract content from a markdown section."""
        pattern = rf"#+\s*{re.escape(section_name)}.*?\n(.*?)(?=\n#+\s|\Z)"
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    def _parse_table(self, content: str) -> List[Dict]:
        """Parse markdown table into list of dicts."""
        lines = content.strip().split('\n')
        rows = []

        # Find header row
        header_line = None
        data_lines = []

        for line in lines:
            if '|' in line:
                if header_line is None:
                    header_line = line
                elif '---' in line:
                    continue
                else:
                    data_lines.append(line)

        if not header_line:
            return []

        # Parse header
        headers = [h.strip() for h in header_line.split('|')[1:-1]]

        # Parse rows
        for line in data_lines:
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if len(cells) == len(headers):
                row = {headers[i]: cells[i] for i in range(len(headers))}
                rows.append(row)

        return rows

    def _parse_bullet_list(self, content: str) -> List[str]:
        """Parse bullet list items."""
        items = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                items.append(line[2:].strip())
            elif line.startswith('• '):
                items.append(line[2:].strip())
        return items

    def _extract_icp(self, content: str) -> Dict:
        """Extract Ideal Customer Profile data."""
        icp_section = self._parse_section(content, "Ideal Customer Profile") or \
                     self._parse_section(content, "ICP")

        if not icp_section:
            return {}

        # Try to parse as table first
        table_data = self._parse_table(icp_section)
        if table_data:
            return {
                "company_characteristics": table_data,
                "raw_content": icp_section
            }

        # Fall back to bullet list
        bullets = self._parse_bullet_list(icp_section)
        return {
            "characteristics": bullets,
            "raw_content": icp_section
        }

    def _extract_personas(self, content: str) -> List[Dict]:
        """Extract buyer persona data."""
        personas = []

        # Look for persona sections
        persona_pattern = r"#+\s*(?:Persona|Buyer Persona|Decision Maker)[\s:]*([^\n]+).*?\n(.*?)(?=\n#+\s*(?:Persona|Buyer|Decision)|## |\Z)"
        matches = re.finditer(persona_pattern, content, re.IGNORECASE | re.DOTALL)

        for match in matches:
            name = match.group(1).strip()
            section_content = match.group(2).strip()

            persona = {
                "name": name,
                "title": "",
                "goals": [],
                "pains": [],
                "objections": [],
                "triggers": [],
                "raw_content": section_content
            }

            # Extract subsections
            goals = self._parse_section(section_content, "Goals") or \
                   self._parse_section(section_content, "Objectives")
            if goals:
                persona["goals"] = self._parse_bullet_list(goals)

            pains = self._parse_section(section_content, "Pain") or \
                   self._parse_section(section_content, "Challenges") or \
                   self._parse_section(section_content, "Problems")
            if pains:
                persona["pains"] = self._parse_bullet_list(pains)

            objections = self._parse_section(section_content, "Objection")
            if objections:
                persona["objections"] = self._parse_bullet_list(objections)

            triggers = self._parse_section(section_content, "Trigger") or \
                      self._parse_section(section_content, "Buying Signal")
            if triggers:
                persona["triggers"] = self._parse_bullet_list(triggers)

            personas.append(persona)

        return personas

    def _extract_messaging(self, content: str) -> Dict:
        """Extract messaging and positioning data."""
        messaging = {}

        # Value proposition
        value_prop = self._parse_section(content, "Value Proposition") or \
                    self._parse_section(content, "Positioning")
        if value_prop:
            messaging["value_proposition"] = value_prop[:500]

        # Key messages
        messages = self._parse_section(content, "Key Message") or \
                  self._parse_section(content, "Messaging")
        if messages:
            messaging["key_messages"] = self._parse_bullet_list(messages)

        # Differentiators
        diff = self._parse_section(content, "Differentiator") or \
              self._parse_section(content, "Competitive Advantage")
        if diff:
            messaging["differentiators"] = self._parse_bullet_list(diff)

        return messaging

    def _extract_buying_committee(self, content: str) -> List[Dict]:
        """Extract buying committee/stakeholder data."""
        committee_section = self._parse_section(content, "Buying Committee") or \
                          self._parse_section(content, "Stakeholder")

        if not committee_section:
            return []

        table_data = self._parse_table(committee_section)
        if table_data:
            return table_data

        return self._parse_bullet_list(committee_section)

    def run(self, inputs: Dict) -> Dict:
        """Main execution method."""
        input_path = inputs.get("input")

        print(f"\n{'='*60}")
        print(f"EXTRACT AUDIENCE PERSONA")
        print(f"{'='*60}")
        print(f"Client: {self.client_id}")
        print(f"{'='*60}\n")

        runner = WorkflowRunner(
            workflow_name=SKILL_NAME,
            version=SKILL_VERSION,
            client=self.client_id
        )

        try:
            # Find persona file
            persona_file = self._find_persona_file(input_path)

            if not persona_file:
                return {
                    "status": "failed",
                    "error": "Could not find audience-persona.md file",
                    "searched_paths": [
                        str(self.client_dir / "context" / "audience-persona.md") if self.client_dir else None,
                        str(SYSTEM_ROOT / "inputs" / "audience-persona.md"),
                        str(SYSTEM_ROOT / "context" / "audience-persona.md")
                    ]
                }

            print(f"[Reading file: {persona_file}]")
            content = persona_file.read_text()

            # Extract structured data
            print("[Extracting ICP...]")
            icp = self._extract_icp(content)

            print("[Extracting Personas...]")
            personas = self._extract_personas(content)

            print("[Extracting Messaging...]")
            messaging = self._extract_messaging(content)

            print("[Extracting Buying Committee...]")
            buying_committee = self._extract_buying_committee(content)

            # Build output structure
            structured_data = {
                "source_file": str(persona_file),
                "extracted_at": datetime.now(timezone.utc).isoformat(),
                "icp": icp,
                "personas": personas,
                "messaging": messaging,
                "buying_committee": buying_committee,
                "metadata": {
                    "persona_count": len(personas),
                    "has_icp": bool(icp),
                    "has_messaging": bool(messaging),
                    "has_buying_committee": bool(buying_committee)
                }
            }

            # Save output
            if self.client_dir:
                output_path = self.client_dir / "context" / "audience-persona.json"
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(json.dumps(structured_data, indent=2))
                print(f"\n  Saved to: {output_path}")

            runtime = time.time() - self.start_time

            result = {
                "status": "success",
                "data": structured_data,
                "summary": {
                    "personas_found": len(personas),
                    "has_icp": bool(icp),
                    "has_messaging": bool(messaging),
                    "has_buying_committee": bool(buying_committee)
                },
                "run_id": runner.run_id,
                "runtime_seconds": round(runtime, 2)
            }

            print(f"\n{'='*60}")
            print(f"EXTRACTION COMPLETE")
            print(f"  Personas: {len(personas)}")
            print(f"  ICP: {'✓' if icp else '✗'}")
            print(f"  Messaging: {'✓' if messaging else '✗'}")
            print(f"{'='*60}\n")

            runner.complete(RunStatus.SUCCESS)
            return result

        except Exception as e:
            runner.complete(RunStatus.FAILED)
            return {"status": "failed", "error": str(e), "run_id": runner.run_id}


def run_extract_audience_persona(inputs: Dict) -> Dict:
    """Main entry point for extract audience persona skill."""
    skill = ExtractAudiencePersonaSkill(
        client_id=inputs.get("client_id"),
        client_name=inputs.get("client_name")
    )
    return skill.run(inputs)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Extract audience persona to structured JSON")
    parser.add_argument("--input", type=str, help="Path to audience-persona.md file")
    parser.add_argument("--client_id", type=str, help="Client identifier")
    parser.add_argument("--output", type=str, help="Output file path (JSON)")

    args = parser.parse_args()

    inputs = {}
    if args.input: inputs["input"] = args.input
    if args.client_id: inputs["client_id"] = args.client_id

    result = run_extract_audience_persona(inputs)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Output saved to {args.output}")
    else:
        print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result.get("status") == "success" else 1)


if __name__ == "__main__":
    main()
