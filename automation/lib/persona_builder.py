"""
MH1 Persona Builder
Builds rich agent personas from client research data.

Features:
- Load company context from research
- Extract founder voice patterns
- Build target audience profiles
- Generate system prompts for copilot

Usage:
    from lib.persona_builder import PersonaBuilder, get_persona_builder

    builder = get_persona_builder()
    persona = builder.build("client-id")

    # Use persona in copilot
    system_prompt = persona.to_system_prompt()
"""

import json
import re
import threading
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import logging

from .firebase_client import get_firebase_client, FirebaseError

logger = logging.getLogger(__name__)

SYSTEM_ROOT = Path(__file__).parent.parent
CLIENTS_DIR = SYSTEM_ROOT / "clients"


@dataclass
class VoiceContract:
    """
    Voice contract extracted from founder content.

    Contains patterns for tone, style, and communication preferences.
    """
    founder_name: str
    role: str = ""

    # Tone and style
    tone_words: List[str] = field(default_factory=list)  # e.g., ["direct", "friendly", "technical"]
    writing_style: str = ""  # e.g., "conversational with industry expertise"

    # Structural patterns
    avg_sentence_length: int = 15
    uses_emojis: bool = False
    uses_hashtags: bool = True
    paragraph_style: str = "short"  # short, medium, long

    # Content patterns
    opening_patterns: List[str] = field(default_factory=list)  # Common ways they start posts
    closing_patterns: List[str] = field(default_factory=list)  # Common endings/CTAs
    favorite_phrases: List[str] = field(default_factory=list)  # Signature phrases

    # Topics and expertise
    expertise_areas: List[str] = field(default_factory=list)
    avoided_topics: List[str] = field(default_factory=list)

    # Engagement style
    engagement_style: str = ""  # e.g., "asks questions", "shares stories"
    cta_style: str = ""  # e.g., "soft ask", "direct call to action"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "founder_name": self.founder_name,
            "role": self.role,
            "tone_words": self.tone_words,
            "writing_style": self.writing_style,
            "avg_sentence_length": self.avg_sentence_length,
            "uses_emojis": self.uses_emojis,
            "uses_hashtags": self.uses_hashtags,
            "paragraph_style": self.paragraph_style,
            "opening_patterns": self.opening_patterns,
            "closing_patterns": self.closing_patterns,
            "favorite_phrases": self.favorite_phrases,
            "expertise_areas": self.expertise_areas,
            "avoided_topics": self.avoided_topics,
            "engagement_style": self.engagement_style,
            "cta_style": self.cta_style,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VoiceContract":
        return cls(
            founder_name=data.get("founder_name", ""),
            role=data.get("role", ""),
            tone_words=data.get("tone_words", []),
            writing_style=data.get("writing_style", ""),
            avg_sentence_length=data.get("avg_sentence_length", 15),
            uses_emojis=data.get("uses_emojis", False),
            uses_hashtags=data.get("uses_hashtags", True),
            paragraph_style=data.get("paragraph_style", "short"),
            opening_patterns=data.get("opening_patterns", []),
            closing_patterns=data.get("closing_patterns", []),
            favorite_phrases=data.get("favorite_phrases", []),
            expertise_areas=data.get("expertise_areas", []),
            avoided_topics=data.get("avoided_topics", []),
            engagement_style=data.get("engagement_style", ""),
            cta_style=data.get("cta_style", ""),
        )

    def to_prompt_section(self) -> str:
        """Convert voice contract to prompt section."""
        lines = [f"### Voice: {self.founder_name}"]

        if self.role:
            lines.append(f"Role: {self.role}")

        if self.writing_style:
            lines.append(f"Style: {self.writing_style}")

        if self.tone_words:
            lines.append(f"Tone: {', '.join(self.tone_words)}")

        if self.expertise_areas:
            lines.append(f"Expertise: {', '.join(self.expertise_areas)}")

        if self.engagement_style:
            lines.append(f"Engagement: {self.engagement_style}")

        if self.favorite_phrases:
            lines.append(f"Signature phrases: {', '.join(self.favorite_phrases[:3])}")

        # Structural notes
        notes = []
        if self.uses_emojis:
            notes.append("uses emojis")
        if not self.uses_hashtags:
            notes.append("minimal hashtags")
        if self.paragraph_style == "short":
            notes.append("short paragraphs")
        if notes:
            lines.append(f"Notes: {', '.join(notes)}")

        return "\n".join(lines)


@dataclass
class AgentPersona:
    """
    Complete agent persona for a client.

    Injected into all copilot interactions to provide
    client-specific expertise and context.
    """
    client_id: str
    company_name: str = ""
    company_context: str = ""        # From research-company
    industry_expertise: str = ""     # From competitor analysis
    founder_voices: List[VoiceContract] = field(default_factory=list)
    target_audience: str = ""        # From extract-audience-persona
    pov_statements: List[str] = field(default_factory=list)  # From extract-pov
    communication_style: str = ""    # Derived from voice contracts
    domain_vocabulary: List[str] = field(default_factory=list)  # Industry terms

    # Additional context
    products: List[str] = field(default_factory=list)
    competitors: List[str] = field(default_factory=list)
    differentiators: List[str] = field(default_factory=list)

    # Metadata
    built_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    data_sources: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "client_id": self.client_id,
            "company_name": self.company_name,
            "company_context": self.company_context,
            "industry_expertise": self.industry_expertise,
            "founder_voices": [v.to_dict() for v in self.founder_voices],
            "target_audience": self.target_audience,
            "pov_statements": self.pov_statements,
            "communication_style": self.communication_style,
            "domain_vocabulary": self.domain_vocabulary,
            "products": self.products,
            "competitors": self.competitors,
            "differentiators": self.differentiators,
            "built_at": self.built_at,
            "data_sources": self.data_sources,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentPersona":
        voices = [VoiceContract.from_dict(v) for v in data.get("founder_voices", [])]

        return cls(
            client_id=data.get("client_id", ""),
            company_name=data.get("company_name", ""),
            company_context=data.get("company_context", ""),
            industry_expertise=data.get("industry_expertise", ""),
            founder_voices=voices,
            target_audience=data.get("target_audience", ""),
            pov_statements=data.get("pov_statements", []),
            communication_style=data.get("communication_style", ""),
            domain_vocabulary=data.get("domain_vocabulary", []),
            products=data.get("products", []),
            competitors=data.get("competitors", []),
            differentiators=data.get("differentiators", []),
            built_at=data.get("built_at", datetime.now(timezone.utc).isoformat()),
            data_sources=data.get("data_sources", []),
        )

    def to_system_prompt(self) -> str:
        """Generate system prompt for copilot interactions."""
        sections = []

        # Header
        sections.append(f"You are the MH1 Copilot for {self.company_name}.")

        # Company context
        if self.company_context:
            sections.append("\n## Company Context")
            sections.append(self.company_context)

        if self.industry_expertise:
            sections.append(f"\nIndustry: {self.industry_expertise}")

        # Target audience
        if self.target_audience:
            sections.append("\n## Target Audience")
            sections.append(self.target_audience)

        # POV and differentiators
        if self.pov_statements:
            sections.append("\n## Point of View")
            for pov in self.pov_statements:
                sections.append(f"- {pov}")

        if self.differentiators:
            sections.append("\n## Key Differentiators")
            for diff in self.differentiators:
                sections.append(f"- {diff}")

        # Communication style
        if self.founder_voices:
            sections.append("\n## Voice & Communication")
            for voice in self.founder_voices:
                sections.append(voice.to_prompt_section())

        # Domain vocabulary
        if self.domain_vocabulary:
            sections.append("\n## Domain Terms")
            sections.append(f"Use these terms naturally: {', '.join(self.domain_vocabulary[:10])}")

        # Behavioral instructions
        sections.append("\n## Behavior")
        sections.append("""
- When creating a plan, show expected outcomes before execution
- Ask for approval before running skills
- Match the founder's voice in all content
- Connect content to current industry conversations
- Prioritize quality over quantity
""")

        return "\n".join(sections)

    @property
    def primary_voice(self) -> Optional[VoiceContract]:
        """Get the primary (first) voice contract."""
        return self.founder_voices[0] if self.founder_voices else None

    @property
    def is_complete(self) -> bool:
        """Check if persona has minimum required data."""
        return bool(
            self.company_name and
            (self.company_context or self.founder_voices)
        )


class PersonaBuilder:
    """
    Builds agent personas from client research data.

    Loads data from:
    - Firebase: clients/{id}/context/, clients/{id}/founders/
    - Local: clients/{id}/research/, clients/{id}/context/
    """

    def __init__(self, clients_dir: Path = None):
        """
        Initialize the persona builder.

        Args:
            clients_dir: Directory containing client folders
        """
        self.clients_dir = clients_dir or CLIENTS_DIR
        self._lock = threading.RLock()
        self._cache: Dict[str, AgentPersona] = {}

    def build(self, client_id: str, force_refresh: bool = False) -> AgentPersona:
        """
        Build or retrieve persona for a client.

        Args:
            client_id: Client identifier
            force_refresh: If True, rebuild even if cached

        Returns:
            AgentPersona for the client
        """
        with self._lock:
            # Check cache
            if not force_refresh and client_id in self._cache:
                return self._cache[client_id]

            logger.info(f"Building persona for client: {client_id}")

            persona = AgentPersona(client_id=client_id)
            data_sources = []

            # Try Firebase first
            try:
                fb_data = self._load_from_firebase(client_id)
                if fb_data:
                    persona = self._merge_data(persona, fb_data)
                    data_sources.append("firebase")
            except Exception as e:
                logger.warning(f"Could not load from Firebase: {e}")

            # Try local files
            try:
                local_data = self._load_from_local(client_id)
                if local_data:
                    persona = self._merge_data(persona, local_data)
                    data_sources.append("local")
            except Exception as e:
                logger.warning(f"Could not load from local: {e}")

            # Derive communication style from voice contracts
            if persona.founder_voices:
                persona.communication_style = self._derive_communication_style(
                    persona.founder_voices
                )

            persona.data_sources = data_sources

            # Cache the result
            self._cache[client_id] = persona

            return persona

    def _load_from_firebase(self, client_id: str) -> Dict[str, Any]:
        """Load persona data from Firebase."""
        fb = get_firebase_client()
        data = {}

        # Load client metadata
        client_doc = fb.get_document("clients", client_id)
        if client_doc:
            data["company_name"] = client_doc.get("displayName", client_doc.get("name", ""))
            data["products"] = client_doc.get("products", [])

        # Load context
        context_doc = fb.get_document("clients", client_id, subcollection="context", subdoc_id="company")
        if context_doc:
            data["company_context"] = context_doc.get("summary", context_doc.get("description", ""))
            data["industry_expertise"] = context_doc.get("industry", "")
            data["competitors"] = context_doc.get("competitors", [])

        # Load POV
        pov_doc = fb.get_document("clients", client_id, subcollection="context", subdoc_id="pov")
        if pov_doc:
            data["pov_statements"] = pov_doc.get("statements", [])
            data["differentiators"] = pov_doc.get("differentiators", [])

        # Load audience
        audience_doc = fb.get_document("clients", client_id, subcollection="context", subdoc_id="audience")
        if audience_doc:
            data["target_audience"] = audience_doc.get("description", "")

        # Load voice contracts
        voice_doc = fb.get_document("clients", client_id, subcollection="context", subdoc_id="voice-contract")
        if voice_doc:
            data["voice_contract"] = voice_doc

        # Load founders
        founders = fb.get_collection(
            "founders",
            parent_collection="clients",
            parent_doc=client_id
        )
        if founders:
            data["founders"] = founders

        return data

    def _load_from_local(self, client_id: str) -> Dict[str, Any]:
        """Load persona data from local files."""
        client_dir = self.clients_dir / client_id
        if not client_dir.exists():
            return {}

        data = {}

        # Load research files
        research_dir = client_dir / "research"
        if research_dir.exists():
            # Company research
            company_file = research_dir / "company-research.md"
            if company_file.exists():
                data["company_context"] = self._extract_summary(company_file.read_text())

            # Competitor research
            competitor_file = research_dir / "competitor-research.md"
            if competitor_file.exists():
                competitors = self._extract_list(competitor_file.read_text(), "competitors")
                data["competitors"] = competitors

            # Founder research files
            for founder_file in research_dir.glob("founder-*.md"):
                founder_name = founder_file.stem.replace("founder-", "").replace("-", " ").title()
                content = founder_file.read_text()

                if "founders" not in data:
                    data["founders"] = []

                data["founders"].append({
                    "name": founder_name,
                    "content": content,
                })

        # Load context files
        context_dir = client_dir / "context"
        if context_dir.exists():
            # Voice contract
            voice_file = context_dir / "voice-contract.json"
            if voice_file.exists():
                try:
                    data["voice_contract"] = json.loads(voice_file.read_text())
                except json.JSONDecodeError:
                    pass

            # POV
            pov_file = context_dir / "pov.md"
            if pov_file.exists():
                data["pov_statements"] = self._extract_list(pov_file.read_text(), "pov")

            # Audience personas
            audience_file = context_dir / "audience-personas.json"
            if audience_file.exists():
                try:
                    audience_data = json.loads(audience_file.read_text())
                    if isinstance(audience_data, list) and audience_data:
                        data["target_audience"] = audience_data[0].get("description", "")
                except json.JSONDecodeError:
                    pass

        return data

    def _merge_data(self, persona: AgentPersona, data: Dict[str, Any]) -> AgentPersona:
        """Merge loaded data into persona."""
        if "company_name" in data and data["company_name"]:
            persona.company_name = data["company_name"]

        if "company_context" in data and data["company_context"]:
            persona.company_context = data["company_context"]

        if "industry_expertise" in data and data["industry_expertise"]:
            persona.industry_expertise = data["industry_expertise"]

        if "target_audience" in data and data["target_audience"]:
            persona.target_audience = data["target_audience"]

        if "pov_statements" in data and data["pov_statements"]:
            persona.pov_statements = data["pov_statements"]

        if "products" in data and data["products"]:
            persona.products = data["products"]

        if "competitors" in data and data["competitors"]:
            persona.competitors = data["competitors"]

        if "differentiators" in data and data["differentiators"]:
            persona.differentiators = data["differentiators"]

        # Build voice contracts from various sources
        if "voice_contract" in data:
            vc_data = data["voice_contract"]
            if isinstance(vc_data, dict):
                voice = VoiceContract(
                    founder_name=vc_data.get("founder_name", vc_data.get("name", "Founder")),
                    role=vc_data.get("role", ""),
                    tone_words=vc_data.get("tone_words", vc_data.get("tone", [])),
                    writing_style=vc_data.get("writing_style", vc_data.get("style", "")),
                    expertise_areas=vc_data.get("expertise_areas", vc_data.get("expertise", [])),
                    favorite_phrases=vc_data.get("favorite_phrases", vc_data.get("phrases", [])),
                    uses_emojis=vc_data.get("uses_emojis", False),
                    uses_hashtags=vc_data.get("uses_hashtags", True),
                    engagement_style=vc_data.get("engagement_style", ""),
                )
                persona.founder_voices.append(voice)

        # Build from founder research
        if "founders" in data:
            for founder_data in data["founders"]:
                if isinstance(founder_data, dict):
                    # Check if it's from Firebase (has detailed fields) or local (has content)
                    if "voice_contract" in founder_data:
                        voice = VoiceContract.from_dict(founder_data["voice_contract"])
                        voice.founder_name = founder_data.get("name", voice.founder_name)
                        voice.role = founder_data.get("role", voice.role)
                    else:
                        voice = VoiceContract(
                            founder_name=founder_data.get("name", "Founder"),
                            role=founder_data.get("role", ""),
                        )

                    # Only add if not duplicate
                    if not any(v.founder_name == voice.founder_name for v in persona.founder_voices):
                        persona.founder_voices.append(voice)

        return persona

    def _extract_summary(self, content: str) -> str:
        """Extract summary from markdown content."""
        # Look for ## Summary or first paragraph
        lines = content.split("\n")

        # Try to find summary section
        in_summary = False
        summary_lines = []

        for line in lines:
            if re.match(r"^##?\s*(summary|overview|about)", line.lower()):
                in_summary = True
                continue
            elif in_summary:
                if line.startswith("#"):
                    break
                if line.strip():
                    summary_lines.append(line.strip())

        if summary_lines:
            return " ".join(summary_lines[:5])  # First 5 lines

        # Fall back to first paragraph
        paragraphs = content.split("\n\n")
        for para in paragraphs:
            para = para.strip()
            if para and not para.startswith("#"):
                return para[:500]  # First 500 chars

        return ""

    def _extract_list(self, content: str, section_name: str) -> List[str]:
        """Extract a list from markdown content."""
        items = []
        lines = content.split("\n")

        in_section = False
        for line in lines:
            if section_name.lower() in line.lower() and "#" in line:
                in_section = True
                continue
            elif in_section:
                if line.startswith("#"):
                    break
                if line.strip().startswith(("-", "*", "1.")):
                    item = re.sub(r"^[-*\d.]+\s*", "", line.strip())
                    if item:
                        items.append(item)

        return items

    def _derive_communication_style(self, voices: List[VoiceContract]) -> str:
        """Derive overall communication style from voice contracts."""
        if not voices:
            return ""

        # Aggregate tone words
        all_tones = []
        for voice in voices:
            all_tones.extend(voice.tone_words)

        # Count most common
        tone_counts = {}
        for tone in all_tones:
            tone_counts[tone] = tone_counts.get(tone, 0) + 1

        top_tones = sorted(tone_counts.keys(), key=lambda x: tone_counts[x], reverse=True)[:3]

        if top_tones:
            return f"{', '.join(top_tones)} communication style"

        return voices[0].writing_style or "professional communication style"

    def clear_cache(self, client_id: str = None):
        """Clear cached personas."""
        with self._lock:
            if client_id:
                self._cache.pop(client_id, None)
            else:
                self._cache.clear()


# Singleton accessor
_builder_instance: Optional[PersonaBuilder] = None
_builder_lock = threading.Lock()


def get_persona_builder() -> PersonaBuilder:
    """Get or create the global PersonaBuilder instance."""
    global _builder_instance

    with _builder_lock:
        if _builder_instance is None:
            _builder_instance = PersonaBuilder()
        return _builder_instance


if __name__ == "__main__":
    # Test basic functionality
    print("Persona Builder Module")
    print("=" * 50)

    builder = PersonaBuilder()

    # Test with mock data
    mock_persona = AgentPersona(
        client_id="test-client",
        company_name="Test Company",
        company_context="A B2B SaaS company specializing in marketing automation.",
        industry_expertise="Marketing Technology",
        target_audience="Marketing managers at mid-market companies",
        pov_statements=[
            "Marketing should be data-driven, not gut-driven",
            "Automation enables creativity, not replaces it",
        ],
        founder_voices=[
            VoiceContract(
                founder_name="Jane Smith",
                role="CEO",
                tone_words=["direct", "inspiring", "data-focused"],
                writing_style="conversational yet authoritative",
                expertise_areas=["marketing strategy", "B2B growth"],
                uses_emojis=False,
            )
        ],
    )

    print("\nGenerated System Prompt:")
    print("-" * 40)
    print(mock_persona.to_system_prompt())
