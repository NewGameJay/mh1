#!/usr/bin/env python3
"""
Newsletter Builder Skill - Execution Script (v1.0.0)

Creates best-in-class newsletters with proven formats from top creators.
Supports deep-dive, news briefing, curated links, personal essay styles.

Usage:
    python skills/newsletter-builder/run.py --topic "AI Marketing" --format deep_dive

    from skills.newsletter_builder.run import run_newsletter_builder
    result = run_newsletter_builder({"topic": "AI Tools", "format": "curated"})
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
    from runner import WorkflowRunner, RunStatus
except ImportError:
    class RunStatus:
        SUCCESS = "success"
        FAILED = "failed"
    class WorkflowRunner:
        def __init__(self, **kwargs): self.run_id = str(uuid.uuid4())[:8]
        def complete(self, status, evaluation=None): return {}

SKILL_NAME = "newsletter-builder"
SKILL_VERSION = "v1.0.0"

NEWSLETTER_FORMATS = {
    "deep_dive": {
        "name": "Deep-Dive / Framework",
        "example": "Lenny Rachitsky style",
        "word_count": "1,500-3,000",
        "frequency": "Weekly",
        "structure": [
            {"section": "Hook", "description": "Provocative opening that creates curiosity"},
            {"section": "Context", "description": "Why this matters now"},
            {"section": "Framework", "description": "The main mental model or framework"},
            {"section": "Examples", "description": "3-5 real examples showing the framework"},
            {"section": "How to Apply", "description": "Step-by-step implementation"},
            {"section": "Templates", "description": "Downloads, checklists, or tools"},
            {"section": "Further Reading", "description": "Related resources"}
        ]
    },
    "news_briefing": {
        "name": "News Briefing",
        "example": "Morning Brew / Finimize style",
        "word_count": "500-1,000",
        "frequency": "Daily or 3x/week",
        "structure": [
            {"section": "Top Story", "description": "Most important news with analysis"},
            {"section": "Quick Hits", "description": "3-5 bullet point news items"},
            {"section": "Chart of the Day", "description": "Visual data point"},
            {"section": "What to Watch", "description": "Upcoming events or trends"},
            {"section": "One More Thing", "description": "Fun fact or lighter content"}
        ]
    },
    "curated": {
        "name": "Curated Links + Commentary",
        "example": "Ben's Bites / TLDR style",
        "word_count": "500-800",
        "frequency": "Daily or weekly",
        "structure": [
            {"section": "Intro", "description": "Personal note or quick thought"},
            {"section": "Headlines", "description": "Top 3-5 stories with commentary"},
            {"section": "Tools & Resources", "description": "Useful finds"},
            {"section": "Deep Dive Pick", "description": "One article worth reading fully"},
            {"section": "Community", "description": "Reader submissions or discussions"}
        ]
    },
    "personal_essay": {
        "name": "Personal Essay / Story",
        "example": "Paul Graham / Sahil Bloom style",
        "word_count": "1,000-2,000",
        "frequency": "Weekly",
        "structure": [
            {"section": "Story Hook", "description": "Personal anecdote that draws in"},
            {"section": "The Lesson", "description": "What you learned"},
            {"section": "Universal Truth", "description": "How this applies to everyone"},
            {"section": "Call to Reflection", "description": "Question for the reader"},
            {"section": "Next Steps", "description": "What to do with this insight"}
        ]
    },
    "roundup": {
        "name": "Weekly Roundup",
        "example": "Product Hunt / Hacker News digest style",
        "word_count": "800-1,500",
        "frequency": "Weekly",
        "structure": [
            {"section": "Editor's Pick", "description": "Your top recommendation"},
            {"section": "This Week's Best", "description": "Categorized list of highlights"},
            {"section": "Trending", "description": "What's getting attention"},
            {"section": "Upcoming", "description": "What to watch next week"},
            {"section": "Reader Spotlight", "description": "Community contribution"}
        ]
    }
}


class NewsletterBuilderSkill:
    """Newsletter Builder skill for creating publication-ready newsletters."""

    def __init__(self, client_id: str = None, client_name: str = None):
        self.client_id = client_id or "standalone"
        self.client_name = client_name
        self.run_id = str(uuid.uuid4())[:8]
        self.start_time = time.time()

        if client_id:
            self.output_dir = SYSTEM_ROOT / "clients" / client_id / "newsletters"
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def _generate_subject_lines(self, topic: str, format_type: str) -> List[str]:
        """Generate subject line options."""
        subjects = []

        if format_type == "deep_dive":
            subjects = [
                f"The complete guide to {topic}",
                f"How top performers approach {topic}",
                f"A framework for {topic} (with templates)"
            ]
        elif format_type == "news_briefing":
            subjects = [
                f"Today in {topic}: The 5-minute brief",
                f"What you missed in {topic} this week",
                f"[Daily Brief] {topic} news you need"
            ]
        elif format_type == "curated":
            subjects = [
                f"Best of {topic} this week",
                f"10 {topic} links worth your time",
                f"The {topic} roundup: What I'm reading"
            ]
        elif format_type == "personal_essay":
            subjects = [
                f"What I learned about {topic}",
                f"A story about {topic}",
                f"The {topic} lesson I wish I knew earlier"
            ]
        else:
            subjects = [
                f"This week in {topic}",
                f"Your weekly {topic} digest",
                f"The {topic} roundup"
            ]

        return subjects

    def _generate_outline(self, topic: str, format_type: str, content_inputs: List[str] = None) -> List[Dict]:
        """Generate newsletter outline based on format."""
        format_info = NEWSLETTER_FORMATS.get(format_type, NEWSLETTER_FORMATS["curated"])
        outline = []

        for section in format_info["structure"]:
            outline_section = {
                "section": section["section"],
                "guidance": section["description"],
                "content_placeholder": f"[Write {section['section'].lower()} about {topic} here]",
                "word_count_target": self._estimate_section_words(section["section"], format_info["word_count"])
            }
            outline.append(outline_section)

        return outline

    def _estimate_section_words(self, section_name: str, total_range: str) -> str:
        """Estimate word count for a section."""
        try:
            low, high = total_range.replace(",", "").split("-")
            avg = (int(low) + int(high)) // 2
        except:
            avg = 1000

        # Distribute based on section importance
        weights = {
            "Hook": 0.1, "Intro": 0.1, "Story Hook": 0.15,
            "Context": 0.1, "Top Story": 0.25,
            "Framework": 0.25, "The Lesson": 0.2,
            "Examples": 0.2, "Headlines": 0.3,
            "How to Apply": 0.15, "Universal Truth": 0.2,
            "Quick Hits": 0.15, "Tools & Resources": 0.1,
            "Templates": 0.05, "Further Reading": 0.05,
            "One More Thing": 0.05
        }

        weight = weights.get(section_name, 0.1)
        return f"~{int(avg * weight)} words"

    def _format_output_markdown(self, topic: str, format_type: str, outline: List[Dict], subjects: List[str]) -> str:
        """Format newsletter template as markdown."""
        format_info = NEWSLETTER_FORMATS.get(format_type, NEWSLETTER_FORMATS["curated"])

        md = f"""# Newsletter: {topic}

**Format:** {format_info['name']} ({format_info['example']})
**Target Length:** {format_info['word_count']} words
**Recommended Frequency:** {format_info['frequency']}

---

## Subject Line Options

1. {subjects[0]}
2. {subjects[1]}
3. {subjects[2]}

---

## Newsletter Structure

"""
        for section in outline:
            md += f"""### {section['section']}

*{section['guidance']}*
*Target: {section['word_count_target']}*

{section['content_placeholder']}

---

"""

        md += f"""
## Writing Tips for {format_info['name']} Format

1. **Hook in the first line** - You have 3 seconds to earn their attention
2. **One idea per paragraph** - Make it scannable
3. **Use formatting** - Bold key points, use bullets for lists
4. **Include visuals** - Charts, images, or GIFs break up text
5. **End with value** - Give them something actionable or memorable

## Pre-Send Checklist

- [ ] Subject line A/B tested
- [ ] Preview text optimized
- [ ] Links all working
- [ ] Images have alt text
- [ ] Mobile preview checked
- [ ] Grammar/spell check done
- [ ] CTA is clear

---

*Template generated by newsletter-builder skill on {datetime.now().strftime('%Y-%m-%d')}*
"""
        return md

    def run(self, inputs: Dict) -> Dict:
        """Main execution method."""
        topic = inputs.get("topic")
        format_type = inputs.get("format", "curated")

        if not topic:
            return {"status": "failed", "error": "topic is required"}

        if format_type not in NEWSLETTER_FORMATS:
            return {"status": "failed", "error": f"Invalid format. Choose from: {list(NEWSLETTER_FORMATS.keys())}"}

        print(f"\n{'='*60}")
        print(f"NEWSLETTER BUILDER")
        print(f"{'='*60}")
        print(f"Topic: {topic}")
        print(f"Format: {format_type}")
        print(f"{'='*60}\n")

        runner = WorkflowRunner(
            workflow_name=SKILL_NAME,
            version=SKILL_VERSION,
            client=self.client_id
        )

        try:
            # Generate subject lines
            print("[Generating subject lines...]")
            subjects = self._generate_subject_lines(topic, format_type)

            # Generate outline
            print("[Building newsletter structure...]")
            outline = self._generate_outline(topic, format_type)

            # Format output
            markdown = self._format_output_markdown(topic, format_type, outline, subjects)

            # Save if client directory exists
            if hasattr(self, 'output_dir'):
                output_path = self.output_dir / f"newsletter-{self.run_id}.md"
                output_path.write_text(markdown)
                print(f"\n  Saved to: {output_path}")

            runtime = time.time() - self.start_time
            format_info = NEWSLETTER_FORMATS[format_type]

            result = {
                "status": "success",
                "topic": topic,
                "format": format_type,
                "format_name": format_info["name"],
                "word_count_target": format_info["word_count"],
                "subject_lines": subjects,
                "outline": outline,
                "markdown": markdown,
                "run_id": runner.run_id,
                "runtime_seconds": round(runtime, 2)
            }

            print(f"\n{'='*60}")
            print(f"NEWSLETTER TEMPLATE COMPLETE")
            print(f"{'='*60}\n")

            runner.complete(RunStatus.SUCCESS)
            return result

        except Exception as e:
            runner.complete(RunStatus.FAILED)
            return {"status": "failed", "error": str(e), "run_id": runner.run_id}


def run_newsletter_builder(inputs: Dict) -> Dict:
    """Main entry point for newsletter builder skill."""
    skill = NewsletterBuilderSkill(
        client_id=inputs.get("client_id"),
        client_name=inputs.get("client_name")
    )
    return skill.run(inputs)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Build newsletters people actually read")
    parser.add_argument("--topic", type=str, required=True, help="Newsletter topic")
    parser.add_argument("--format", type=str, default="curated",
                       choices=list(NEWSLETTER_FORMATS.keys()), help="Newsletter format style")
    parser.add_argument("--client_id", type=str, help="Client identifier")
    parser.add_argument("--output", type=str, help="Output file path (JSON)")

    args = parser.parse_args()

    inputs = {
        "topic": args.topic,
        "format": args.format
    }
    if args.client_id: inputs["client_id"] = args.client_id

    result = run_newsletter_builder(inputs)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2, default=str)
    else:
        print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result.get("status") == "success" else 1)


if __name__ == "__main__":
    main()
