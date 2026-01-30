#!/usr/bin/env python3
"""
Email Sequences Skill - Execution Script (v1.0.0)

Builds email sequences that convert subscribers into customers.
Supports welcome, nurture, conversion, launch, and re-engagement sequences.

Usage:
    python skills/email-sequences/run.py --lead_magnet "Ultimate Guide" --offer "Course" --sequence_type welcome

    from skills.email_sequences.run import run_email_sequences
    result = run_email_sequences({"lead_magnet": "Guide", "offer": "Course"})
"""

import argparse
import json
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
    from runner import WorkflowRunner, RunStatus, estimate_tokens
    from evaluator import evaluate_output
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
        def complete(self, status, evaluation=None): return {}

SKILL_NAME = "email-sequences"
SKILL_VERSION = "v1.0.0"

SEQUENCE_TEMPLATES = {
    "welcome": {
        "description": "Deliver value, build relationship",
        "email_count": 5,
        "cadence": [0, 1, 2, 4, 7],  # Days after opt-in
        "templates": [
            {"purpose": "Deliver lead magnet + introduce yourself", "cta": "Download/access"},
            {"purpose": "Quick win from lead magnet", "cta": "Implement one thing"},
            {"purpose": "Your story/why you do this", "cta": "Connect on social"},
            {"purpose": "Deep value email (best content)", "cta": "Apply concept"},
            {"purpose": "Soft intro to paid offer", "cta": "Learn more"}
        ]
    },
    "nurture": {
        "description": "Provide value, build trust",
        "email_count": 4,
        "cadence": [0, 3, 7, 10],
        "templates": [
            {"purpose": "Case study or result", "cta": "Read full story"},
            {"purpose": "Common mistake + fix", "cta": "Audit yourself"},
            {"purpose": "Framework or method", "cta": "Try the framework"},
            {"purpose": "Objection handling", "cta": "Ask questions"}
        ]
    },
    "conversion": {
        "description": "Sell the product",
        "email_count": 5,
        "cadence": [0, 1, 2, 4, 7],
        "templates": [
            {"purpose": "Introduce the offer", "cta": "Learn more"},
            {"purpose": "Why now (urgency)", "cta": "Check availability"},
            {"purpose": "Social proof", "cta": "See results"},
            {"purpose": "FAQ / objections", "cta": "Ask questions"},
            {"purpose": "Last call", "cta": "Get started"}
        ]
    },
    "launch": {
        "description": "Time-bound campaign",
        "email_count": 7,
        "cadence": [-3, -1, 0, 1, 2, 4, 7],  # Days relative to launch
        "templates": [
            {"purpose": "Announce what's coming", "cta": "Get notified"},
            {"purpose": "Behind the scenes", "cta": "Early access"},
            {"purpose": "Doors open!", "cta": "Enroll now"},
            {"purpose": "Bonus reveal", "cta": "Claim bonus"},
            {"purpose": "Case study / results", "cta": "Join them"},
            {"purpose": "FAQ + objections", "cta": "Ask questions"},
            {"purpose": "Final hours", "cta": "Don't miss out"}
        ]
    },
    "re-engagement": {
        "description": "Win back cold subscribers",
        "email_count": 3,
        "cadence": [0, 3, 7],
        "templates": [
            {"purpose": "We miss you + gift", "cta": "Get the gift"},
            {"purpose": "Best content recap", "cta": "Catch up"},
            {"purpose": "Stay or go (clean list)", "cta": "Click to stay"}
        ]
    }
}


class EmailSequencesSkill:
    """Email Sequences skill for creating high-converting email sequences."""

    def __init__(self, client_id: str = None, client_name: str = None):
        self.client_id = client_id or "standalone"
        self.client_name = client_name
        self.run_id = str(uuid.uuid4())[:8]
        self.start_time = time.time()

        if client_id:
            self.output_dir = SYSTEM_ROOT / "clients" / client_id / "email-sequences"
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def _generate_subject_lines(self, email_purpose: str, context: Dict) -> List[str]:
        """Generate subject line variations for an email."""
        lead_magnet = context.get("lead_magnet", "resource")
        offer = context.get("offer", "product")

        base_subjects = {
            "Deliver lead magnet": [
                f"Your {lead_magnet} is ready",
                f"[Download] {lead_magnet}",
                f"Here's your {lead_magnet}"
            ],
            "Quick win": [
                "Try this today (takes 5 min)",
                f"The first thing to do with your {lead_magnet}",
                "Quick win from yesterday's download"
            ],
            "Your story": [
                "Why I created this...",
                "The story behind what you downloaded",
                "Can I share something personal?"
            ],
            "Deep value": [
                "My best advice (no fluff)",
                "What actually works",
                f"The framework behind {lead_magnet}"
            ],
            "Soft intro": [
                "When you're ready for the next level...",
                f"Beyond the {lead_magnet}",
                "For when you want more"
            ],
            "Introduce the offer": [
                f"Introducing: {offer}",
                "Something new for you",
                "You asked, we built it"
            ],
            "Urgency": [
                "Time-sensitive opportunity",
                "This won't last",
                "Doors closing soon"
            ],
            "Social proof": [
                "See what [Name] achieved",
                "Results that speak for themselves",
                "Their story might be yours"
            ],
            "FAQ": [
                "Your questions answered",
                "The truth about [topic]",
                "Let me address the elephant..."
            ],
            "Last call": [
                "Final reminder",
                "Last chance",
                "Closing at midnight"
            ]
        }

        for key, subjects in base_subjects.items():
            if key.lower() in email_purpose.lower():
                return subjects

        return [f"Important: {email_purpose}", email_purpose, f"Re: {lead_magnet}"]

    def _generate_email_body(self, template: Dict, context: Dict, email_num: int) -> str:
        """Generate email body copy."""
        lead_magnet = context.get("lead_magnet", "your download")
        offer = context.get("offer", "our product")
        price = context.get("price", "")
        voice = context.get("voice", "friendly and professional")

        purpose = template["purpose"]
        cta = template["cta"]

        body = f"""Hey {{{{first_name}}}},

[Opening hook related to: {purpose}]

[Main content - 2-3 paragraphs that:
- Deliver on the purpose above
- Connect to their situation
- Provide clear value]

[Bridge to CTA]

**{cta}**: [Link or button]

[Sign-off matching brand voice: {voice}]

P.S. [Post-script that reinforces value or adds urgency]

---
Email {email_num} | Purpose: {purpose}
Tone: {voice}
"""
        return body

    def _build_sequence(self, sequence_type: str, context: Dict) -> List[Dict]:
        """Build a complete email sequence."""
        template = SEQUENCE_TEMPLATES.get(sequence_type)
        if not template:
            return []

        emails = []
        for i, email_template in enumerate(template["templates"]):
            email = {
                "email_number": i + 1,
                "send_day": template["cadence"][i],
                "purpose": email_template["purpose"],
                "subject_lines": self._generate_subject_lines(email_template["purpose"], context),
                "cta": email_template["cta"],
                "body": self._generate_email_body(email_template, context, i + 1)
            }
            emails.append(email)

        return emails

    def _format_output_markdown(self, sequence_type: str, emails: List[Dict], context: Dict) -> str:
        """Format the sequence as markdown."""
        template = SEQUENCE_TEMPLATES.get(sequence_type, {})

        md = f"""# {sequence_type.title()} Email Sequence

**Lead Magnet:** {context.get('lead_magnet', 'N/A')}
**Offer:** {context.get('offer', 'N/A')}
**Sequence Type:** {template.get('description', sequence_type)}
**Total Emails:** {len(emails)}

---

## Sequence Overview

| Email | Day | Purpose | CTA |
|-------|-----|---------|-----|
"""
        for email in emails:
            md += f"| {email['email_number']} | {email['send_day']} | {email['purpose']} | {email['cta']} |\n"

        md += "\n---\n\n## Full Email Copy\n\n"

        for email in emails:
            md += f"""### Email {email['email_number']}: {email['purpose']}

**Send:** Day {email['send_day']}
**Subject Lines:**
- {email['subject_lines'][0]}
- {email['subject_lines'][1]}
- {email['subject_lines'][2]}

**Body:**

{email['body']}

---

"""

        md += f"""
## Implementation Notes

1. **A/B Test Subject Lines** - Test at least 2 subject lines per email
2. **Personalization** - Replace {{first_name}} with actual merge tags for your ESP
3. **Links** - Add actual URLs before sending
4. **Timing** - Adjust send days based on your audience behavior
5. **Voice** - Review and adjust copy to match brand voice

---

*Generated by email-sequences skill on {datetime.now().strftime('%Y-%m-%d')}*
"""
        return md

    def run(self, inputs: Dict) -> Dict:
        """Main execution method."""
        lead_magnet = inputs.get("lead_magnet")
        offer = inputs.get("offer")
        sequence_type = inputs.get("sequence_type", "welcome")

        if not lead_magnet:
            return {"status": "failed", "error": "lead_magnet is required"}

        if sequence_type not in SEQUENCE_TEMPLATES:
            return {"status": "failed", "error": f"Invalid sequence_type. Choose from: {list(SEQUENCE_TEMPLATES.keys())}"}

        context = {
            "lead_magnet": lead_magnet,
            "offer": offer or "your solution",
            "price": inputs.get("price", ""),
            "voice": inputs.get("voice", "friendly and professional"),
            "objections": inputs.get("objections", [])
        }

        print(f"\n{'='*60}")
        print(f"EMAIL SEQUENCES")
        print(f"{'='*60}")
        print(f"Lead Magnet: {lead_magnet}")
        print(f"Offer: {offer}")
        print(f"Sequence Type: {sequence_type}")
        print(f"{'='*60}\n")

        runner = WorkflowRunner(
            workflow_name=SKILL_NAME,
            version=SKILL_VERSION,
            client=self.client_id
        )

        try:
            # Build the sequence
            print(f"[Building {sequence_type} sequence...]")
            emails = self._build_sequence(sequence_type, context)
            print(f"  Created {len(emails)} emails")

            # Format output
            markdown = self._format_output_markdown(sequence_type, emails, context)

            # Save if client directory exists
            if hasattr(self, 'output_dir'):
                output_path = self.output_dir / f"{sequence_type}-sequence-{self.run_id}.md"
                output_path.write_text(markdown)
                print(f"\n  Saved to: {output_path}")

            runtime = time.time() - self.start_time

            result = {
                "status": "success",
                "sequence_type": sequence_type,
                "email_count": len(emails),
                "emails": emails,
                "markdown": markdown,
                "run_id": runner.run_id,
                "runtime_seconds": round(runtime, 2)
            }

            print(f"\n{'='*60}")
            print(f"SEQUENCE COMPLETE - {len(emails)} emails created")
            print(f"{'='*60}\n")

            runner.complete(RunStatus.SUCCESS)
            return result

        except Exception as e:
            runner.complete(RunStatus.FAILED)
            return {"status": "failed", "error": str(e), "run_id": runner.run_id}


def run_email_sequences(inputs: Dict) -> Dict:
    """Main entry point for email sequences skill."""
    skill = EmailSequencesSkill(
        client_id=inputs.get("client_id"),
        client_name=inputs.get("client_name")
    )
    return skill.run(inputs)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Build email sequences that convert")
    parser.add_argument("--lead_magnet", type=str, required=True, help="What the lead magnet is")
    parser.add_argument("--offer", type=str, help="The paid product/service")
    parser.add_argument("--sequence_type", type=str, default="welcome",
                       choices=list(SEQUENCE_TEMPLATES.keys()), help="Type of sequence")
    parser.add_argument("--price", type=str, help="Price point of offer")
    parser.add_argument("--voice", type=str, help="Brand voice description")
    parser.add_argument("--client_id", type=str, help="Client identifier")
    parser.add_argument("--output", type=str, help="Output file path (JSON)")

    args = parser.parse_args()

    inputs = {
        "lead_magnet": args.lead_magnet,
        "sequence_type": args.sequence_type
    }

    if args.offer: inputs["offer"] = args.offer
    if args.price: inputs["price"] = args.price
    if args.voice: inputs["voice"] = args.voice
    if args.client_id: inputs["client_id"] = args.client_id

    result = run_email_sequences(inputs)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Output saved to {args.output}")
    else:
        print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result.get("status") == "success" else 1)


if __name__ == "__main__":
    main()
