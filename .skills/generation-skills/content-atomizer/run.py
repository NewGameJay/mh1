#!/usr/bin/env python3
"""
Content Atomizer Skill - Execution Script (v1.0.0)

Transform one piece of content into platform-optimized assets across
LinkedIn, Twitter/X, Instagram, TikTok, and YouTube.

Features:
- Source content extraction and analysis
- Platform-specific content generation
- Hook formulas and algorithm alignment
- Multi-format output (text, carousel outlines, video scripts)

Usage:
    # Atomize a blog post
    python skills/content-atomizer/run.py --source_file "blog-post.md" --platforms "linkedin,twitter"

    # Atomize from URL (requires content to be fetched separately)
    python skills/content-atomizer/run.py --source_text "..." --platforms "all"

    # Programmatic
    from skills.content_atomizer.run import run_content_atomizer
    result = run_content_atomizer({
        "source_file": "path/to/content.md",
        "platforms": ["linkedin", "twitter", "instagram"]
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
SKILL_NAME = "content-atomizer"
SKILL_VERSION = "v1.0.0"

# Platform specifications
PLATFORM_SPECS = {
    "linkedin": {
        "name": "LinkedIn",
        "formats": ["text_post", "carousel"],
        "max_chars": 3000,
        "hook_chars": 140,
        "optimal_length": "1200-1500 chars",
        "top_signal": "Dwell time + topic authority",
        "algorithm_notes": "Post 2-3x/week max, not daily. Native content preferred."
    },
    "twitter": {
        "name": "Twitter/X",
        "formats": ["single_tweet", "thread"],
        "max_chars": 280,
        "hook_chars": 100,
        "optimal_length": "<100 chars for singles, 8-15 tweets for threads",
        "top_signal": "Replies + early engagement",
        "algorithm_notes": "Grok AI ranks For You feed. Media boosts visibility."
    },
    "instagram": {
        "name": "Instagram",
        "formats": ["carousel", "reel_script", "caption"],
        "max_chars": 2200,
        "hook_chars": 125,
        "optimal_length": "6-10 slides for carousels",
        "top_signal": "DM shares (sends per reach)",
        "algorithm_notes": "Carousels expanded to 20 slides. Photos getting more support."
    },
    "tiktok": {
        "name": "TikTok",
        "formats": ["video_script"],
        "max_duration": "30-60 seconds",
        "hook_seconds": 3,
        "optimal_length": "15-30 seconds for virality, 30-60 with strong retention",
        "top_signal": "Completion rate + niche alignment",
        "algorithm_notes": "Longer content favored if retention is high."
    },
    "youtube": {
        "name": "YouTube",
        "formats": ["short_script", "video_outline"],
        "max_duration": "60 seconds for Shorts",
        "hook_seconds": 2,
        "optimal_length": "10-35 seconds for Shorts, 8-12 minutes for long-form",
        "top_signal": "CTR + satisfaction + session time",
        "algorithm_notes": "Topical authority matters. Evergreen content gets revived."
    }
}

# Hook formulas by platform
HOOK_FORMULAS = {
    "linkedin": [
        "contrarian_statement",
        "story_hook",
        "list_preview",
        "credibility_insight",
        "question_hook",
        "bold_claim"
    ],
    "twitter": [
        "bold_opener",
        "numbers_outcome",
        "controversial_take",
        "curiosity_gap",
        "specific_proof"
    ],
    "instagram": [
        "bold_statement",
        "problem_setup",
        "transformation_tease"
    ],
    "tiktok": [
        "pattern_interrupt",
        "identity_callout",
        "proof_first",
        "controversy_spark",
        "tutorial_promise"
    ],
    "youtube": [
        "immediate_value",
        "challenge_belief",
        "quick_lesson"
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


class ContentAtomizerSkill:
    """
    Content Atomizer skill for multi-platform content transformation.
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
            self.output_dir = SYSTEM_ROOT / "clients" / client_id / "atomized-content"
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_source_content(self, source_file: str = None, source_text: str = None) -> Dict:
        """Load source content from file or text."""
        if source_file:
            path = Path(source_file) if Path(source_file).is_absolute() else SYSTEM_ROOT / source_file
            if path.exists():
                return {
                    "content": path.read_text(),
                    "source": str(path),
                    "type": path.suffix.lstrip('.')
                }
            else:
                return {"error": f"File not found: {path}"}

        if source_text:
            return {
                "content": source_text,
                "source": "text_input",
                "type": "text"
            }

        return {"error": "No source content provided"}

    def _extract_key_elements(self, content: str) -> Dict:
        """Extract key elements from source content for atomization."""
        # Split into sentences and paragraphs
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        paragraphs = content.split('\n\n')

        # Extract elements
        elements = {
            "core_insight": "",
            "supporting_points": [],
            "stories_examples": [],
            "data_points": [],
            "contrarian_takes": [],
            "quotable_lines": [],
            "actionable_steps": []
        }

        # Find core insight (typically in first paragraph)
        if paragraphs:
            elements["core_insight"] = paragraphs[0][:200] if len(paragraphs[0]) > 200 else paragraphs[0]

        # Find supporting points (headers or numbered items)
        for line in content.split('\n'):
            if line.startswith('#') or line.startswith('-') or re.match(r'^\d+\.', line):
                cleaned = re.sub(r'^[#\-\d\.]+\s*', '', line).strip()
                if cleaned and len(cleaned) > 10:
                    elements["supporting_points"].append(cleaned)

        # Find data points (numbers, percentages, statistics)
        data_pattern = r'\d+%|\$\d+|\d+x|\d+ (percent|million|billion|thousand)'
        for sentence in sentences:
            if re.search(data_pattern, sentence, re.IGNORECASE):
                elements["data_points"].append(sentence.strip())

        # Find quotable lines (short, punchy sentences)
        for sentence in sentences:
            if 5 <= len(sentence.split()) <= 15 and not sentence.startswith('('):
                elements["quotable_lines"].append(sentence.strip())

        # Limit each category
        elements["supporting_points"] = elements["supporting_points"][:7]
        elements["data_points"] = elements["data_points"][:5]
        elements["quotable_lines"] = elements["quotable_lines"][:5]

        return elements

    def _generate_linkedin_text_post(self, elements: Dict) -> Dict:
        """Generate LinkedIn text post."""
        core = elements.get("core_insight", "")
        points = elements.get("supporting_points", [])[:5]
        quotables = elements.get("quotable_lines", [])

        # Build post
        hook = quotables[0] if quotables else core[:140]

        post = f"""{hook}

"""
        if points:
            post += "Here's what I learned:\n\n"
            for i, point in enumerate(points, 1):
                post += f"{i}. {point}\n\n"

        post += f"""---

What's your experience with this? Drop a comment below.

#ContentStrategy #LinkedIn #Marketing"""

        return {
            "platform": "linkedin",
            "format": "text_post",
            "content": post,
            "hook": hook,
            "char_count": len(post),
            "optimal": len(post) <= 1500
        }

    def _generate_linkedin_carousel_outline(self, elements: Dict) -> Dict:
        """Generate LinkedIn carousel slide outline."""
        points = elements.get("supporting_points", [])[:6]
        core = elements.get("core_insight", "")

        slides = [
            {
                "slide": 1,
                "type": "hook",
                "content": core[:100] if core else "Hook slide content",
                "notes": "Bold statement or question. Swipe to learn more."
            }
        ]

        for i, point in enumerate(points, 2):
            slides.append({
                "slide": i,
                "type": "content",
                "content": point[:150],
                "notes": "2-3 sentences of explanation"
            })

        slides.append({
            "slide": len(slides) + 1,
            "type": "summary",
            "content": "Quick recap:\n" + "\n".join([f"- {p[:30]}..." for p in points[:5]]),
            "notes": "Bullet summary of key points"
        })

        slides.append({
            "slide": len(slides) + 1,
            "type": "cta",
            "content": "Found this useful?\n\n-> Follow for more\n-> Repost to help others\n-> Save for later",
            "notes": "Clear call to action"
        })

        return {
            "platform": "linkedin",
            "format": "carousel",
            "slides": slides,
            "slide_count": len(slides),
            "optimal": 5 <= len(slides) <= 10
        }

    def _generate_twitter_thread(self, elements: Dict) -> Dict:
        """Generate Twitter thread."""
        core = elements.get("core_insight", "")
        points = elements.get("supporting_points", [])[:7]
        quotables = elements.get("quotable_lines", [])

        tweets = []

        # Hook tweet
        hook = quotables[0][:200] if quotables else core[:200]
        tweets.append({
            "tweet_number": 1,
            "content": f"{hook}\n\nThread:",
            "type": "hook"
        })

        # Content tweets
        for i, point in enumerate(points, 2):
            tweets.append({
                "tweet_number": i,
                "content": f"{i-1}. {point[:250]}",
                "type": "content"
            })

        # Wrap tweet
        wrap_content = "TL;DR:\n\n" + "\n".join([f"- {p[:40]}..." for p in points[:5]])
        wrap_content += "\n\nIf useful, RT tweet 1. Follow for more."
        tweets.append({
            "tweet_number": len(tweets) + 1,
            "content": wrap_content,
            "type": "wrap"
        })

        return {
            "platform": "twitter",
            "format": "thread",
            "tweets": tweets,
            "tweet_count": len(tweets),
            "optimal": 8 <= len(tweets) <= 15
        }

    def _generate_twitter_single(self, elements: Dict) -> Dict:
        """Generate single tweet."""
        quotables = elements.get("quotable_lines", [])
        core = elements.get("core_insight", "")

        # Pick best quotable or condense core insight
        if quotables:
            best = min(quotables, key=lambda x: abs(len(x) - 200))
            content = best[:280]
        else:
            content = core[:280]

        return {
            "platform": "twitter",
            "format": "single_tweet",
            "content": content,
            "char_count": len(content),
            "optimal": len(content) <= 100
        }

    def _generate_instagram_carousel_outline(self, elements: Dict) -> Dict:
        """Generate Instagram carousel outline."""
        points = elements.get("supporting_points", [])[:8]
        core = elements.get("core_insight", "")

        slides = [
            {
                "slide": 1,
                "type": "cover",
                "content": core[:60] if core else "Hook Text",
                "visual_notes": "Bold text, high contrast, minimal design"
            }
        ]

        for i, point in enumerate(points, 2):
            slides.append({
                "slide": i,
                "type": "content",
                "content": point[:80],
                "visual_notes": "One point per slide, large text"
            })

        slides.append({
            "slide": len(slides) + 1,
            "type": "cta",
            "content": "Save this\nFollow @handle\nShare with a friend",
            "visual_notes": "Clear CTAs with icons"
        })

        return {
            "platform": "instagram",
            "format": "carousel",
            "slides": slides,
            "slide_count": len(slides),
            "optimal": 6 <= len(slides) <= 10
        }

    def _generate_instagram_caption(self, elements: Dict) -> Dict:
        """Generate Instagram caption."""
        core = elements.get("core_insight", "")
        points = elements.get("supporting_points", [])[:3]

        caption = f"""{core[:125]}

.
.
.

"""
        for point in points:
            caption += f"- {point[:100]}\n\n"

        caption += """---

Save this for later
Share with a friend who needs it
Drop a comment if this resonated

#ContentStrategy #SocialMedia #Marketing"""

        return {
            "platform": "instagram",
            "format": "caption",
            "content": caption,
            "char_count": len(caption),
            "optimal": len(caption) <= 2200
        }

    def _generate_tiktok_script(self, elements: Dict) -> Dict:
        """Generate TikTok video script."""
        core = elements.get("core_insight", "")
        points = elements.get("supporting_points", [])[:3]
        quotables = elements.get("quotable_lines", [])

        hook = quotables[0][:50] if quotables else "Stop scrolling if you..."

        script = {
            "platform": "tiktok",
            "format": "video_script",
            "duration": "30 seconds",
            "sections": [
                {
                    "timing": "0-3 seconds",
                    "type": "hook",
                    "content": hook,
                    "visual": "Face to camera, pattern interrupt"
                },
                {
                    "timing": "3-25 seconds",
                    "type": "body",
                    "content": f"Here's the thing:\n\n" + "\n".join([f"- {p[:50]}" for p in points]),
                    "visual": "Fast delivery, movement"
                },
                {
                    "timing": "25-30 seconds",
                    "type": "cta",
                    "content": "Follow for more. Save this.",
                    "visual": "Point to follow button"
                }
            ]
        }

        return script

    def _generate_youtube_short_script(self, elements: Dict) -> Dict:
        """Generate YouTube Short script."""
        core = elements.get("core_insight", "")
        points = elements.get("supporting_points", [])[:3]

        script = {
            "platform": "youtube",
            "format": "short_script",
            "duration": "45 seconds",
            "sections": [
                {
                    "timing": "0-2 seconds",
                    "type": "hook",
                    "content": f"Here's why {core[:30]}... is wrong",
                    "visual": "Immediate pattern interrupt"
                },
                {
                    "timing": "2-40 seconds",
                    "type": "body",
                    "content": "\n".join([f"Point {i+1}: {p[:60]}" for i, p in enumerate(points)]),
                    "visual": "Fast-paced delivery with visual movement"
                },
                {
                    "timing": "40-45 seconds",
                    "type": "cta",
                    "content": "Subscribe for more",
                    "visual": "Point to subscribe, or end abruptly for rewatch"
                }
            ]
        }

        return script

    def _atomize_for_platform(self, platform: str, elements: Dict) -> List[Dict]:
        """Generate all content pieces for a platform."""
        pieces = []

        if platform == "linkedin":
            pieces.append(self._generate_linkedin_text_post(elements))
            pieces.append(self._generate_linkedin_carousel_outline(elements))

        elif platform == "twitter":
            pieces.append(self._generate_twitter_thread(elements))
            pieces.append(self._generate_twitter_single(elements))

        elif platform == "instagram":
            pieces.append(self._generate_instagram_carousel_outline(elements))
            pieces.append(self._generate_instagram_caption(elements))

        elif platform == "tiktok":
            pieces.append(self._generate_tiktok_script(elements))

        elif platform == "youtube":
            pieces.append(self._generate_youtube_short_script(elements))

        return pieces

    def _generate_posting_sequence(self, all_pieces: Dict) -> List[Dict]:
        """Generate recommended posting sequence."""
        sequence = []
        day = 1

        # LinkedIn first (longest shelf life)
        if "linkedin" in all_pieces:
            for piece in all_pieces["linkedin"]:
                sequence.append({
                    "day": day,
                    "platform": "LinkedIn",
                    "format": piece["format"],
                    "notes": "Post early morning (8-10am)"
                })
                day += 1

        # Twitter next
        if "twitter" in all_pieces:
            for piece in all_pieces["twitter"]:
                sequence.append({
                    "day": day,
                    "platform": "Twitter/X",
                    "format": piece["format"],
                    "notes": "Good for discussion and engagement"
                })
            day += 1

        # Instagram
        if "instagram" in all_pieces:
            sequence.append({
                "day": day,
                "platform": "Instagram",
                "format": "carousel + caption",
                "notes": "Repurpose LinkedIn design elements"
            })
            day += 1

        # Video platforms last (need production)
        if "tiktok" in all_pieces:
            sequence.append({
                "day": day,
                "platform": "TikTok",
                "format": "video",
                "notes": "Record and edit video"
            })
            day += 1

        if "youtube" in all_pieces:
            sequence.append({
                "day": day,
                "platform": "YouTube Shorts",
                "format": "video",
                "notes": "Can repurpose TikTok with adjustments"
            })

        return sequence

    def run(self, inputs: Dict) -> Dict:
        """
        Main execution method for content atomizer skill.

        Args:
            inputs: Dictionary with:
                - source_file: Path to source content file
                - source_text: Source content as text
                - platforms: List of target platforms (default: all)

        Returns:
            Complete skill result with atomized content
        """
        source_file = inputs.get("source_file")
        source_text = inputs.get("source_text")
        platforms = inputs.get("platforms", list(PLATFORM_SPECS.keys()))

        if isinstance(platforms, str):
            if platforms.lower() == "all":
                platforms = list(PLATFORM_SPECS.keys())
            else:
                platforms = [p.strip() for p in platforms.split(",")]

        print(f"\n{'='*60}")
        print(f"CONTENT ATOMIZER")
        print(f"{'='*60}")
        print(f"Platforms: {', '.join(platforms)}")
        print(f"Run ID: {self.run_id}")
        print(f"{'='*60}\n")

        runner = WorkflowRunner(
            workflow_name=SKILL_NAME,
            version=SKILL_VERSION,
            client=self.client_id
        )

        try:
            # Step 1: Load source content
            print("[Step 1] Loading source content...")
            source = self._load_source_content(source_file, source_text)

            if source.get("error"):
                return {
                    "status": "failed",
                    "error": source["error"]
                }

            content = source["content"]
            print(f"  Loaded {len(content)} characters from {source['source']}")

            # Step 2: Extract key elements
            print("\n[Step 2] Extracting key elements...")
            elements = self._extract_key_elements(content)
            print(f"  Core insight: {len(elements['core_insight'])} chars")
            print(f"  Supporting points: {len(elements['supporting_points'])}")
            print(f"  Quotable lines: {len(elements['quotable_lines'])}")
            print(f"  Data points: {len(elements['data_points'])}")

            # Step 3: Generate content for each platform
            print("\n[Step 3] Atomizing for platforms...")
            all_pieces = {}
            total_pieces = 0

            for platform in platforms:
                if platform not in PLATFORM_SPECS:
                    print(f"  Skipping unknown platform: {platform}")
                    continue

                print(f"  - {PLATFORM_SPECS[platform]['name']}...")
                pieces = self._atomize_for_platform(platform, elements)
                all_pieces[platform] = pieces
                total_pieces += len(pieces)
                print(f"    Generated {len(pieces)} piece(s)")

            # Step 4: Generate posting sequence
            print("\n[Step 4] Generating posting sequence...")
            sequence = self._generate_posting_sequence(all_pieces)

            # Step 5: Save outputs
            if hasattr(self, 'output_dir'):
                output_path = self.output_dir / f"atomized-{self.run_id}.json"
                with open(output_path, 'w') as f:
                    json.dump({
                        "source": source["source"],
                        "elements": elements,
                        "pieces": all_pieces,
                        "sequence": sequence
                    }, f, indent=2)
                print(f"\n  Saved to: {output_path}")

            runtime = time.time() - self.start_time

            result = {
                "status": "success",
                "source": source["source"],
                "elements_extracted": {
                    "core_insight_length": len(elements["core_insight"]),
                    "supporting_points": len(elements["supporting_points"]),
                    "quotable_lines": len(elements["quotable_lines"]),
                    "data_points": len(elements["data_points"])
                },
                "pieces": all_pieces,
                "total_pieces": total_pieces,
                "posting_sequence": sequence,
                "platforms_processed": list(all_pieces.keys()),
                "run_id": runner.run_id,
                "runtime_seconds": round(runtime, 2)
            }

            print(f"\n{'='*60}")
            print(f"ATOMIZATION COMPLETE")
            print(f"{'='*60}")
            print(f"Platforms: {len(all_pieces)}")
            print(f"Total pieces: {total_pieces}")
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


def run_content_atomizer(inputs: Dict) -> Dict:
    """
    Main entry point for content atomizer skill.

    Args:
        inputs: Dictionary with source content and platform options

    Returns:
        Complete skill result with atomized content
    """
    if not inputs.get("client_id"):
        active_client = get_client_from_active_file()
        if active_client.get("client_id"):
            inputs["client_id"] = active_client["client_id"]
            inputs["client_name"] = active_client.get("client_name")

    skill = ContentAtomizerSkill(
        client_id=inputs.get("client_id"),
        client_name=inputs.get("client_name")
    )

    return skill.run(inputs)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Transform content into platform-optimized assets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Atomize a file
    python run.py --source_file "blog-post.md" --platforms "linkedin,twitter"

    # Atomize text
    python run.py --source_text "Content here..." --platforms "all"

    # Save output
    python run.py --source_file "content.md" --output atomized.json
        """
    )

    parser.add_argument("--source_file", type=str, help="Path to source content file")
    parser.add_argument("--source_text", type=str, help="Source content as text")
    parser.add_argument("--platforms", type=str, default="all",
                       help="Comma-separated platforms or 'all'")
    parser.add_argument("--client_id", type=str, help="Client identifier")
    parser.add_argument("--output", type=str, help="Output file path (JSON)")

    args = parser.parse_args()

    if not args.source_file and not args.source_text:
        parser.error("Either --source_file or --source_text is required")

    inputs = {
        "platforms": args.platforms
    }

    if args.source_file:
        inputs["source_file"] = args.source_file
    if args.source_text:
        inputs["source_text"] = args.source_text
    if args.client_id:
        inputs["client_id"] = args.client_id

    result = run_content_atomizer(inputs)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Output saved to {args.output}")
    else:
        print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result.get("status") == "success" else 1)


if __name__ == "__main__":
    main()
