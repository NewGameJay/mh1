#!/usr/bin/env python3
"""
Brand Voice Skill - Execution Script (v1.0.0)

Define or extract a consistent brand voice profile that other skills can use.
Supports two modes: Extract (analyze existing content) or Build (construct strategically).

Features:
- Extract mode: Analyze existing content to codify voice patterns
- Build mode: Strategic questions to construct voice from scratch
- Voice profile generation with comprehensive attributes
- Integration with content generation skills

Usage:
    # Extract mode - analyze existing content
    python skills/brand-voice/run.py --mode extract --content_paths "path/to/content1.md,path/to/content2.md"

    # Build mode - strategic construction
    python skills/brand-voice/run.py --mode build --answers_file "path/to/answers.json"

    # With explicit client
    python skills/brand-voice/run.py --client_id abc123 --mode extract

    # Programmatic
    from skills.brand_voice.run import run_brand_voice
    result = run_brand_voice({
        "mode": "extract",
        "content_paths": ["path/to/content1.md"]
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
    from release_policy import determine_release_action, ReleaseAction, get_release_action_message
    from telemetry import log_run
except ImportError:
    class RunStatus:
        SUCCESS = "success"
        FAILED = "failed"
        REVIEW = "review"

    class ReleaseAction:
        AUTO_DELIVER = "auto_deliver"
        @property
        def value(self):
            return str(self)

    def estimate_tokens(text): return len(str(text)) // 4
    def evaluate_output(output, schema=None, requirements=None):
        return {"score": 0.85, "pass": True}
    def determine_release_action(standard_eval=None, is_external_facing=False):
        return ReleaseAction()
    def get_release_action_message(action): return "Auto-delivered"

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

    def log_run(**kwargs): pass


# Constants
SKILL_NAME = "brand-voice"
SKILL_VERSION = "v1.0.0"

# Voice profile template structure
VOICE_PROFILE_TEMPLATE = {
    "voice_summary": "",
    "personality_traits": [],
    "tone_spectrum": {
        "formal_casual": {"position": "", "notes": ""},
        "serious_playful": {"position": "", "notes": ""},
        "reserved_bold": {"position": "", "notes": ""},
        "simple_sophisticated": {"position": "", "notes": ""},
        "warm_direct": {"position": "", "notes": ""}
    },
    "vocabulary": {
        "words_to_use": [],
        "words_to_avoid": [],
        "jargon_level": "",
        "profanity": ""
    },
    "rhythm_structure": {
        "sentences": "",
        "paragraphs": "",
        "openings": "",
        "formatting": ""
    },
    "pov_address": {
        "first_person": "",
        "reader_address": "",
        "relationship_stance": ""
    },
    "example_phrases": {
        "on_brand": [],
        "off_brand": []
    },
    "dos_and_donts": {
        "do": [],
        "dont": []
    }
}

# Strategic questions for Build mode
BUILD_QUESTIONS = {
    "identity": [
        "What are 3-5 words that describe your personality?",
        "What do you stand for? What's your core belief about your industry/topic?",
        "What's your background? What shaped how you see things?",
        "What makes you genuinely different from others in your space?"
    ],
    "audience": [
        "Who are you talking to? (Be specific)",
        "What tone resonates with them? (What do they respond to?)",
        "What would make them trust you? What would turn them off?"
    ],
    "positioning": [
        "Are you the expert, the peer, the rebel, the guide, the insider?",
        "Where do you sit on accessible to exclusive?",
        "Where do you sit on approachable to authoritative?"
    ],
    "aspiration": [
        "Name 2-3 brands or people whose voice you admire. What specifically do you like about how they communicate?",
        "What do you explicitly NOT want to sound like?"
    ],
    "practical": [
        "Any words or phrases that are signature to you?",
        "Any words or phrases you hate or want to avoid?",
        "How do you feel about humor? Profanity? Hot takes?"
    ]
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


class BrandVoiceSkill:
    """
    Brand Voice skill for defining or extracting voice profiles.
    """

    def __init__(
        self,
        client_id: str,
        client_name: str = None
    ):
        self.client_id = client_id
        self.client_name = client_name or client_id
        self.run_id = str(uuid.uuid4())[:8]
        self.start_time = time.time()

        # Build paths
        self.client_dir = SYSTEM_ROOT / "clients" / self.client_id
        self.context_dir = self.client_dir / "context"
        self.output_dir = self.client_dir / "voice-profiles"

        # Ensure directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_content_files(self, content_paths: List[str]) -> List[Dict]:
        """Load content from specified file paths."""
        content_items = []

        for path in content_paths:
            full_path = Path(path) if Path(path).is_absolute() else SYSTEM_ROOT / path
            if full_path.exists():
                content_items.append({
                    "path": str(full_path),
                    "content": full_path.read_text(),
                    "type": full_path.suffix.lstrip('.')
                })
            else:
                content_items.append({
                    "path": str(full_path),
                    "content": None,
                    "error": "File not found"
                })

        return content_items

    def _analyze_content_patterns(self, content_items: List[Dict]) -> Dict:
        """Analyze content for voice patterns."""
        # In production, this would use LLM to analyze patterns
        # For now, return structured analysis placeholder

        all_content = "\n\n".join([
            c.get("content", "") for c in content_items if c.get("content")
        ])

        # Basic heuristic analysis
        words = all_content.split()
        sentences = all_content.split('.')
        paragraphs = all_content.split('\n\n')

        return {
            "content_analyzed": len([c for c in content_items if c.get("content")]),
            "total_words": len(words),
            "avg_sentence_length": len(words) / max(len(sentences), 1),
            "avg_paragraph_length": len(sentences) / max(len(paragraphs), 1),
            "uses_contractions": "n't" in all_content or "'re" in all_content,
            "uses_first_person": " I " in all_content or "I'm" in all_content,
            "uses_questions": "?" in all_content,
            "formality_indicators": {
                "contractions": all_content.count("'"),
                "exclamations": all_content.count("!"),
                "questions": all_content.count("?")
            }
        }

    def _extract_voice_profile(self, analysis: Dict, content_items: List[Dict]) -> Dict:
        """Generate voice profile from content analysis."""
        profile = VOICE_PROFILE_TEMPLATE.copy()

        # Determine tone based on analysis
        profile["voice_summary"] = (
            "Voice profile extracted from provided content. "
            "Adjust and refine based on specific brand needs."
        )

        # Set tone spectrum based on analysis
        profile["tone_spectrum"] = {
            "formal_casual": {
                "position": "Casual" if analysis.get("uses_contractions") else "Formal",
                "notes": "Based on contraction usage in content"
            },
            "serious_playful": {
                "position": "Mixed",
                "notes": f"Exclamation count: {analysis.get('formality_indicators', {}).get('exclamations', 0)}"
            },
            "reserved_bold": {
                "position": "Moderate",
                "notes": "Requires manual assessment"
            },
            "simple_sophisticated": {
                "position": "Simple" if analysis.get("avg_sentence_length", 15) < 15 else "Sophisticated",
                "notes": f"Average sentence length: {analysis.get('avg_sentence_length', 0):.1f} words"
            },
            "warm_direct": {
                "position": "Direct" if analysis.get("uses_first_person") else "Warm",
                "notes": "Based on first-person usage"
            }
        }

        # Set rhythm patterns
        profile["rhythm_structure"] = {
            "sentences": f"Average {analysis.get('avg_sentence_length', 0):.1f} words per sentence",
            "paragraphs": f"Average {analysis.get('avg_paragraph_length', 0):.1f} sentences per paragraph",
            "openings": "Extracted from content patterns",
            "formatting": "Review content for header/list usage patterns"
        }

        # Set POV
        profile["pov_address"] = {
            "first_person": "I" if analysis.get("uses_first_person") else "We",
            "reader_address": "You (direct)",
            "relationship_stance": "Peer"
        }

        # Default guidance
        profile["dos_and_donts"] = {
            "do": [
                "Maintain consistent tone across content",
                "Use active voice",
                "Keep paragraphs short"
            ],
            "dont": [
                "Use corporate jargon",
                "Write long, complex sentences",
                "Be impersonal"
            ]
        }

        return profile

    def _build_voice_profile(self, answers: Dict) -> Dict:
        """Build voice profile from strategic question answers."""
        profile = VOICE_PROFILE_TEMPLATE.copy()

        # Map answers to profile structure
        identity = answers.get("identity", {})
        audience = answers.get("audience", {})
        positioning = answers.get("positioning", {})
        aspiration = answers.get("aspiration", {})
        practical = answers.get("practical", {})

        # Build voice summary
        personality_words = identity.get("personality_words", [])
        core_belief = identity.get("core_belief", "")

        profile["voice_summary"] = (
            f"A voice characterized by being {', '.join(personality_words[:3])}. "
            f"{core_belief}"
        )

        # Set personality traits
        profile["personality_traits"] = [
            {"trait": word, "meaning": "Defined by user"}
            for word in personality_words
        ]

        # Set tone based on positioning
        profile["tone_spectrum"] = {
            "formal_casual": {
                "position": positioning.get("accessible_exclusive", "Accessible"),
                "notes": ""
            },
            "serious_playful": {
                "position": positioning.get("serious_playful", "Balanced"),
                "notes": ""
            },
            "reserved_bold": {
                "position": "Bold" if positioning.get("stance") == "rebel" else "Moderate",
                "notes": f"Stance: {positioning.get('stance', 'peer')}"
            },
            "simple_sophisticated": {
                "position": positioning.get("approachable_authoritative", "Approachable"),
                "notes": ""
            },
            "warm_direct": {
                "position": "Direct with warmth",
                "notes": ""
            }
        }

        # Set vocabulary
        profile["vocabulary"] = {
            "words_to_use": practical.get("signature_phrases", []),
            "words_to_avoid": practical.get("words_to_avoid", []),
            "jargon_level": "Light",
            "profanity": practical.get("profanity_stance", "Never")
        }

        # Set dos and donts
        not_like = aspiration.get("not_like", [])
        profile["dos_and_donts"] = {
            "do": [
                f"Sound like: {', '.join(aspiration.get('admired_voices', [])[:2])}",
                "Stay true to core personality",
                "Connect with target audience"
            ],
            "dont": [
                f"Sound like: {', '.join(not_like[:2])}" if not_like else "Generic marketing speak",
                "Use words from avoid list",
                "Abandon voice for trends"
            ]
        }

        return profile

    def _generate_markdown_profile(self, profile: Dict, name: str) -> str:
        """Generate markdown-formatted voice profile document."""
        md = f"""# {name} Voice Profile

## Voice Summary

{profile.get('voice_summary', 'No summary provided.')}

## Core Personality Traits

"""
        for trait in profile.get('personality_traits', []):
            if isinstance(trait, dict):
                md += f"- **{trait.get('trait', 'Unknown')}:** {trait.get('meaning', '')}\n"
            else:
                md += f"- **{trait}**\n"

        md += """
## Tone Spectrum

| Dimension | Position | Notes |
|-----------|----------|-------|
"""
        for dimension, values in profile.get('tone_spectrum', {}).items():
            dim_name = dimension.replace('_', ' ').title()
            position = values.get('position', 'Not set')
            notes = values.get('notes', '')
            md += f"| {dim_name} | {position} | {notes} |\n"

        vocab = profile.get('vocabulary', {})
        md += f"""
## Vocabulary

**Words/phrases to USE:**
"""
        for word in vocab.get('words_to_use', ['(none specified)']):
            md += f"- {word}\n"

        md += """
**Words/phrases to AVOID:**
"""
        for word in vocab.get('words_to_avoid', ['(none specified)']):
            md += f"- {word}\n"

        md += f"""
**Jargon level:** {vocab.get('jargon_level', 'Not specified')}

**Profanity:** {vocab.get('profanity', 'Not specified')}

## Rhythm & Structure

"""
        rhythm = profile.get('rhythm_structure', {})
        md += f"**Sentences:** {rhythm.get('sentences', 'Not analyzed')}\n\n"
        md += f"**Paragraphs:** {rhythm.get('paragraphs', 'Not analyzed')}\n\n"
        md += f"**Openings:** {rhythm.get('openings', 'Not analyzed')}\n\n"
        md += f"**Formatting:** {rhythm.get('formatting', 'Not analyzed')}\n"

        pov = profile.get('pov_address', {})
        md += f"""
## POV & Address

**First person:** {pov.get('first_person', 'Not specified')}

**Reader address:** {pov.get('reader_address', 'Not specified')}

**Relationship stance:** {pov.get('relationship_stance', 'Not specified')}

## Example Phrases

**On-brand (sounds like us):**
"""
        for phrase in profile.get('example_phrases', {}).get('on_brand', ['(add examples)']):
            md += f'- "{phrase}"\n'

        md += """
**Off-brand (doesn't sound like us):**
"""
        for phrase in profile.get('example_phrases', {}).get('off_brand', ['(add examples)']):
            md += f'- "{phrase}"\n'

        dos_donts = profile.get('dos_and_donts', {})
        md += """
## Do's and Don'ts

**DO:**
"""
        for item in dos_donts.get('do', ['(add guidance)']):
            md += f"- {item}\n"

        md += """
**DON'T:**
"""
        for item in dos_donts.get('dont', ['(add guidance)']):
            md += f"- {item}\n"

        md += f"""
---

*Voice profile generated on {datetime.now().strftime('%Y-%m-%d')} by brand-voice skill*
"""
        return md

    def _save_profile(self, profile: Dict, markdown: str, profile_name: str) -> Dict:
        """Save voice profile to files."""
        # Save JSON
        json_path = self.output_dir / f"{profile_name}-voice-profile.json"
        with open(json_path, 'w') as f:
            json.dump(profile, f, indent=2)

        # Save Markdown
        md_path = self.output_dir / f"{profile_name}-voice-profile.md"
        md_path.write_text(markdown)

        # Also save to context directory for easy access
        context_json = self.context_dir / "voice-profile.json"
        context_md = self.context_dir / "voice-profile.md"

        self.context_dir.mkdir(parents=True, exist_ok=True)
        with open(context_json, 'w') as f:
            json.dump(profile, f, indent=2)
        context_md.write_text(markdown)

        return {
            "json_path": str(json_path),
            "markdown_path": str(md_path),
            "context_json": str(context_json),
            "context_markdown": str(context_md)
        }

    def run(self, inputs: Dict) -> Dict:
        """
        Main execution method for brand voice skill.

        Args:
            inputs: Dictionary with:
                - mode: "extract" or "build" (default: "extract")
                - content_paths: List of paths for extract mode
                - answers: Dict of answers for build mode
                - profile_name: Name for the profile (default: client_name)

        Returns:
            Complete skill result with voice profile
        """
        mode = inputs.get("mode", "extract")
        profile_name = inputs.get("profile_name", self.client_name)

        print(f"\n{'='*60}")
        print(f"BRAND VOICE - {mode.upper()} MODE")
        print(f"{'='*60}")
        print(f"Client: {self.client_name} ({self.client_id})")
        print(f"Profile Name: {profile_name}")
        print(f"Run ID: {self.run_id}")
        print(f"{'='*60}\n")

        runner = WorkflowRunner(
            workflow_name=SKILL_NAME,
            version=SKILL_VERSION,
            client=self.client_id
        )

        try:
            if mode == "extract":
                # Extract mode: analyze existing content
                content_paths = inputs.get("content_paths", [])

                if not content_paths:
                    return {
                        "status": "failed",
                        "error": "content_paths is required for extract mode"
                    }

                print(f"[Step 1] Loading {len(content_paths)} content file(s)...")
                content_items = self._load_content_files(content_paths)

                loaded_count = len([c for c in content_items if c.get("content")])
                if loaded_count == 0:
                    return {
                        "status": "failed",
                        "error": "No content files could be loaded",
                        "details": content_items
                    }

                print(f"  Loaded {loaded_count} file(s)")

                print("\n[Step 2] Analyzing content patterns...")
                analysis = self._analyze_content_patterns(content_items)
                print(f"  Analyzed {analysis.get('total_words', 0)} words")

                print("\n[Step 3] Generating voice profile...")
                profile = self._extract_voice_profile(analysis, content_items)

            else:  # Build mode
                answers = inputs.get("answers", {})

                if not answers:
                    # Return questions to answer
                    return {
                        "status": "questions_needed",
                        "questions": BUILD_QUESTIONS,
                        "message": "Please provide answers to build the voice profile",
                        "run_id": runner.run_id
                    }

                print("[Step 1] Processing strategic answers...")
                print(f"  Categories answered: {len(answers)}")

                print("\n[Step 2] Building voice profile...")
                profile = self._build_voice_profile(answers)

            # Generate markdown
            print("\n[Step 4] Generating markdown document...")
            markdown = self._generate_markdown_profile(profile, profile_name)

            # Save profile
            print("\n[Step 5] Saving voice profile...")
            saved = self._save_profile(profile, markdown, profile_name.lower().replace(' ', '-'))
            print(f"  JSON: {saved['json_path']}")
            print(f"  Markdown: {saved['markdown_path']}")

            runtime = time.time() - self.start_time

            result = {
                "status": "success",
                "mode": mode,
                "profile_name": profile_name,
                "profile": profile,
                "markdown": markdown,
                "files": saved,
                "run_id": runner.run_id,
                "runtime_seconds": round(runtime, 2)
            }

            print(f"\n{'='*60}")
            print(f"VOICE PROFILE CREATED")
            print(f"{'='*60}")
            print(f"Profile: {profile_name}")
            print(f"Mode: {mode}")
            print(f"Files saved to: {self.output_dir}")
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


def run_brand_voice(inputs: Dict) -> Dict:
    """
    Main entry point for brand voice skill.

    Args:
        inputs: Dictionary with configuration

    Returns:
        Complete skill result with voice profile
    """
    if not inputs.get("client_id"):
        active_client = get_client_from_active_file()
        if active_client.get("client_id"):
            inputs["client_id"] = active_client["client_id"]
            if not inputs.get("client_name"):
                inputs["client_name"] = active_client.get("client_name")
        else:
            return {
                "status": "failed",
                "error": "client_id is required"
            }

    skill = BrandVoiceSkill(
        client_id=inputs.get("client_id"),
        client_name=inputs.get("client_name")
    )

    return skill.run(inputs)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Define or extract brand voice profile",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Extract mode
    python run.py --mode extract --content_paths "content1.md,content2.md"

    # Build mode with answers file
    python run.py --mode build --answers_file answers.json

    # Get questions for build mode
    python run.py --mode build
        """
    )

    parser.add_argument("--client_id", type=str, help="Client identifier")
    parser.add_argument("--client_name", type=str, help="Client display name")
    parser.add_argument("--mode", type=str, choices=["extract", "build"], default="extract")
    parser.add_argument("--content_paths", type=str, help="Comma-separated content file paths")
    parser.add_argument("--answers_file", type=str, help="JSON file with build mode answers")
    parser.add_argument("--profile_name", type=str, help="Name for the voice profile")
    parser.add_argument("--output", type=str, help="Output file path (JSON)")

    args = parser.parse_args()

    inputs = {"mode": args.mode}

    if args.client_id:
        inputs["client_id"] = args.client_id
    if args.client_name:
        inputs["client_name"] = args.client_name
    if args.profile_name:
        inputs["profile_name"] = args.profile_name
    if args.content_paths:
        inputs["content_paths"] = args.content_paths.split(",")
    if args.answers_file:
        with open(args.answers_file, 'r') as f:
            inputs["answers"] = json.load(f)

    result = run_brand_voice(inputs)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Output saved to {args.output}")
    else:
        print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result.get("status") in ["success", "questions_needed"] else 1)


if __name__ == "__main__":
    main()
