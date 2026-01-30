"""
Context Orchestrator - Progressive context loading system.

Loads context in 3 levels:
- Level 1: Client profile, voice contract (always loaded)
- Level 2: Skill metadata, agent expertise (loaded on intent match)
- Level 3: Full skill content, historical patterns (loaded on execution)

This implements efficient context management to minimize token usage while
ensuring all necessary context is available for execution.

Usage:
    from lib.context_orchestrator import ContextOrchestrator, ContextBudget

    orchestrator = ContextOrchestrator()

    # Planning phase - load levels 1 & 2
    context = orchestrator.load_for_planning(client_id="abc123", intent={"type": "lifecycle"})

    # Execution phase - load level 3
    context = orchestrator.load_for_execution(client_id="abc123", skill_name="lifecycle-audit")
"""

import json
import logging
import re
import threading
import yaml
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timezone

# Configure logging
logger = logging.getLogger(__name__)

# Base paths
SYSTEM_ROOT = Path(__file__).parent.parent
SKILLS_DIR = SYSTEM_ROOT / "skills"
AGENTS_DIR = SYSTEM_ROOT / "agents"
CLIENTS_DIR = SYSTEM_ROOT / "clients"
CONFIG_DIR = SYSTEM_ROOT / "config"


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class ContextBudget:
    """
    Track context token usage across loading levels.

    Manages token budget to prevent context overflow.
    Default budget is 100K tokens with reserves for output and system.
    """
    max_tokens: int = 100000
    reserved_for_output: int = 4000
    reserved_for_system: int = 2000
    level_1_used: int = 0
    level_2_used: int = 0
    level_3_used: int = 0

    @property
    def available(self) -> int:
        """Total available tokens after reserves."""
        return self.max_tokens - self.reserved_for_output - self.reserved_for_system

    @property
    def total_used(self) -> int:
        """Total tokens used across all levels."""
        return self.level_1_used + self.level_2_used + self.level_3_used

    def remaining(self) -> int:
        """Remaining tokens available for loading."""
        return self.available - self.total_used

    def can_load(self, estimated_tokens: int) -> bool:
        """Check if we have budget to load additional content."""
        return self.remaining() >= estimated_tokens

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "max_tokens": self.max_tokens,
            "reserved_for_output": self.reserved_for_output,
            "reserved_for_system": self.reserved_for_system,
            "level_1_used": self.level_1_used,
            "level_2_used": self.level_2_used,
            "level_3_used": self.level_3_used,
            "available": self.available,
            "total_used": self.total_used,
            "remaining": self.remaining()
        }


@dataclass
class LoadedContext:
    """
    Context loaded for execution.

    Contains all context data loaded across the three levels:
    - Level 1: client, voice_contract
    - Level 2: skills (metadata), agents (metadata), platform_config
    - Level 3: full_skill, patterns
    """
    # Level 1: Core client context
    client: Dict = field(default_factory=dict)
    voice_contract: Dict = field(default_factory=dict)

    # Level 2: Skill and agent metadata
    skills: List[Dict] = field(default_factory=list)
    agents: List[Dict] = field(default_factory=list)
    platform_config: Dict = field(default_factory=dict)

    # Level 3: Full execution context
    full_skill: Dict = field(default_factory=dict)
    patterns: List[Dict] = field(default_factory=list)
    skill_specific_data: Dict = field(default_factory=dict)

    # Budget tracking
    budget: ContextBudget = field(default_factory=ContextBudget)

    # Metadata
    client_id: str = ""
    loaded_at: str = ""
    levels_loaded: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "client": self.client,
            "voice_contract": self.voice_contract,
            "skills": self.skills,
            "agents": self.agents,
            "platform_config": self.platform_config,
            "full_skill": self.full_skill,
            "patterns": self.patterns,
            "skill_specific_data": self.skill_specific_data,
            "budget": self.budget.to_dict(),
            "client_id": self.client_id,
            "loaded_at": self.loaded_at,
            "levels_loaded": self.levels_loaded
        }

    def has_level(self, level: int) -> bool:
        """Check if a specific level has been loaded."""
        return level in self.levels_loaded

    def get_skill_names(self) -> List[str]:
        """Get names of all loaded skills."""
        return [s.get("name", "") for s in self.skills if s.get("name")]

    def get_agent_names(self) -> List[str]:
        """Get names of all loaded agents."""
        return [a.get("name", "") for a in self.agents if a.get("name")]


# ============================================================
# MAIN ORCHESTRATOR CLASS
# ============================================================

class ContextOrchestrator:
    """
    Manages progressive context loading for MH1 workflows.

    Implements a 3-level loading system:
    - Level 1 (Always): Client profile, voice contract
    - Level 2 (Planning): Skill metadata, agent expertise based on intent
    - Level 3 (Execution): Full skill content, historical patterns

    Features:
    - Caching to avoid redundant Firebase/file reads
    - Token budget management
    - Graceful handling of missing data
    - YAML frontmatter parsing for skills and agents
    """

    # Mapping of intent keywords to relevant skills
    SKILL_TRIGGERS = {
        # Lifecycle/CRM triggers
        "lifecycle": ["lifecycle-audit", "churn-prediction", "at-risk-detection", "reactivation-detection"],
        "churn": ["churn-prediction", "at-risk-detection", "lifecycle-audit"],
        "at-risk": ["at-risk-detection", "churn-prediction", "dormant-detection"],
        "dormant": ["dormant-detection", "reactivation-detection"],
        "upsell": ["upsell-candidates", "engagement-velocity"],
        "renewal": ["renewal-tracker", "at-risk-detection"],

        # HubSpot/CRM triggers
        "hubspot": ["crm-discovery", "pipeline-analysis", "deal-velocity", "lifecycle-audit"],
        "crm": ["crm-discovery", "pipeline-analysis", "deal-velocity"],
        "pipeline": ["pipeline-analysis", "deal-velocity", "conversion-funnel"],
        "deal": ["deal-velocity", "pipeline-analysis"],
        "account": ["account-360", "at-risk-detection", "upsell-candidates"],

        # Content triggers
        "content": ["ghostwrite-content", "email-copy-generator", "cohort-email-builder"],
        "ghostwrite": ["ghostwrite-content"],
        "email": ["email-copy-generator", "cohort-email-builder"],
        "linkedin": ["linkedin-keyword-search", "ghostwrite-content"],

        # Research triggers
        "research": ["research-company", "research-competitors", "research-founder"],
        "company": ["research-company", "extract-company-profile"],
        "competitor": ["research-competitors"],
        "founder": ["research-founder", "extract-founder-voice"],

        # Social listening triggers
        "social": ["social-listening-collect", "twitter-keyword-search", "reddit-keyword-search"],
        "twitter": ["twitter-keyword-search"],
        "reddit": ["reddit-keyword-search"],

        # Data triggers
        "warehouse": ["data-warehouse-discovery", "data-quality-audit"],
        "data": ["data-warehouse-discovery", "data-quality-audit", "identity-mapping"],
        "quality": ["data-quality-audit"],

        # Onboarding triggers
        "onboarding": ["client-onboarding", "needs-assessment", "research-company"],
        "assessment": ["needs-assessment"],

        # Voice/persona triggers
        "voice": ["extract-founder-voice", "extract-writing-guideline"],
        "persona": ["extract-audience-persona"],
        "pov": ["extract-pov"],
    }

    # Mapping of skills to relevant agents
    SKILL_AGENT_MAP = {
        "lifecycle-audit": ["lifecycle-auditor"],
        "ghostwrite-content": ["linkedin-ghostwriter", "linkedin-topic-curator", "linkedin-template-selector", "linkedin-qa-reviewer"],
        "research-company": ["deep-research-agent"],
        "research-competitors": ["competitive-intelligence-analyst"],
        "research-founder": ["thought-leader-analyst"],
    }

    def __init__(self, firebase_client=None, intelligence_bridge=None):
        """
        Initialize the Context Orchestrator.

        Args:
            firebase_client: Optional FirebaseClient instance for data loading
            intelligence_bridge: Optional IntelligenceBridge for pattern retrieval
        """
        self.firebase = firebase_client
        self.bridge = intelligence_bridge

        # Caching
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        self._cache_lock = threading.RLock()
        self._cache_ttl_seconds = 300  # 5 minute cache TTL

        # Track loaded state
        self._current_context: Optional[LoadedContext] = None

        logger.debug("ContextOrchestrator initialized")

    # ============================================================
    # TOKEN ESTIMATION
    # ============================================================

    def _estimate_tokens(self, content: Any) -> int:
        """
        Estimate token count for content.

        Uses rough approximation of 4 characters per token.

        Args:
            content: Content to estimate (str, dict, list, etc.)

        Returns:
            Estimated token count
        """
        if content is None:
            return 0

        if isinstance(content, str):
            text = content
        elif isinstance(content, (dict, list)):
            try:
                text = json.dumps(content, default=str)
            except (TypeError, ValueError):
                text = str(content)
        else:
            text = str(content)

        # Rough estimate: 4 characters per token
        return len(text) // 4

    # ============================================================
    # CACHING HELPERS
    # ============================================================

    def _get_cached(self, cache_key: str) -> Optional[Any]:
        """Get item from cache if not expired."""
        with self._cache_lock:
            if cache_key not in self._cache:
                return None

            timestamp = self._cache_timestamps.get(cache_key)
            if timestamp:
                age = (datetime.now(timezone.utc) - timestamp).total_seconds()
                if age > self._cache_ttl_seconds:
                    # Expired - remove and return None
                    del self._cache[cache_key]
                    del self._cache_timestamps[cache_key]
                    return None

            return self._cache[cache_key]

    def _set_cached(self, cache_key: str, value: Any):
        """Set item in cache with timestamp."""
        with self._cache_lock:
            self._cache[cache_key] = value
            self._cache_timestamps[cache_key] = datetime.now(timezone.utc)

    def clear_cache(self, cache_key: str = None):
        """Clear cache (specific key or all)."""
        with self._cache_lock:
            if cache_key:
                self._cache.pop(cache_key, None)
                self._cache_timestamps.pop(cache_key, None)
            else:
                self._cache.clear()
                self._cache_timestamps.clear()

    # ============================================================
    # YAML FRONTMATTER PARSING
    # ============================================================

    def _parse_yaml_frontmatter(self, content: str) -> Tuple[Dict, str]:
        """
        Parse YAML frontmatter from markdown content.

        Args:
            content: Markdown content with optional YAML frontmatter

        Returns:
            Tuple of (frontmatter_dict, body_content)
        """
        if not content or not content.startswith("---"):
            return {}, content

        # Find the closing ---
        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}, content

        try:
            frontmatter = yaml.safe_load(parts[1])
            if not isinstance(frontmatter, dict):
                frontmatter = {}
            body = parts[2].strip()
            return frontmatter, body
        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse YAML frontmatter: {e}")
            return {}, content

    # ============================================================
    # LEVEL 1 LOADERS: Client Profile & Voice Contract
    # ============================================================

    def _load_client_profile(self, client_id: str) -> Dict:
        """
        Load client profile from Firebase.

        Level 1 context - always loaded.

        Args:
            client_id: Client identifier

        Returns:
            Client profile dict (empty dict if not found)
        """
        cache_key = f"client_profile:{client_id}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        profile = {}

        # Try Firebase first
        if self.firebase:
            try:
                doc = self.firebase.get_document("clients", client_id)
                if doc:
                    profile = doc
                    logger.debug(f"Loaded client profile from Firebase: {client_id}")
            except Exception as e:
                logger.warning(f"Failed to load client profile from Firebase: {e}")

        # If no Firebase or not found, try local config
        if not profile:
            client_config_path = CONFIG_DIR / "clients" / f"{client_id}.yaml"
            if client_config_path.exists():
                try:
                    profile = yaml.safe_load(client_config_path.read_text())
                    logger.debug(f"Loaded client profile from local config: {client_id}")
                except Exception as e:
                    logger.warning(f"Failed to load client config: {e}")

        self._set_cached(cache_key, profile)
        return profile

    def _load_voice_contract(self, client_id: str) -> Dict:
        """
        Load voice contract for client's founders.

        Level 1 context - essential for content generation.

        Args:
            client_id: Client identifier

        Returns:
            Voice contract dict (empty dict if not found)
        """
        cache_key = f"voice_contract:{client_id}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        voice_contract = {}

        # Try Firebase - look for founder voice contracts
        if self.firebase:
            try:
                # Get founders for this client
                founders = self.firebase.get_collection(
                    "founders",
                    parent_collection="clients",
                    parent_doc=client_id,
                    limit=5
                )

                if founders:
                    # Get voice data from first founder (or aggregate)
                    for founder in founders:
                        founder_voice = founder.get("voiceContract") or founder.get("voice_contract")
                        if founder_voice:
                            voice_contract[founder.get("name", "default")] = founder_voice

                    if voice_contract:
                        logger.debug(f"Loaded voice contract from Firebase: {client_id}")
            except Exception as e:
                logger.warning(f"Failed to load voice contract from Firebase: {e}")

        # Try local fallback
        if not voice_contract:
            voice_path = CLIENTS_DIR / client_id / "voice-contract.yaml"
            if voice_path.exists():
                try:
                    voice_contract = yaml.safe_load(voice_path.read_text())
                    logger.debug(f"Loaded voice contract from local file: {client_id}")
                except Exception as e:
                    logger.warning(f"Failed to load local voice contract: {e}")

        self._set_cached(cache_key, voice_contract)
        return voice_contract

    # ============================================================
    # LEVEL 2 LOADERS: Skill & Agent Metadata
    # ============================================================

    def _match_skills_to_intent(self, intent: Dict) -> List[str]:
        """
        Match skills to user intent based on keywords and context.

        Args:
            intent: Intent dict with keys like "type", "keywords", "description"

        Returns:
            List of relevant skill names
        """
        matched_skills: Set[str] = set()

        # Extract searchable text from intent
        search_text = " ".join([
            str(intent.get("type", "")),
            str(intent.get("description", "")),
            " ".join(intent.get("keywords", [])),
            str(intent.get("query", ""))
        ]).lower()

        # Match against trigger keywords
        for trigger, skills in self.SKILL_TRIGGERS.items():
            if trigger in search_text:
                matched_skills.update(skills)

        # If explicit skill requested, add it
        if intent.get("skill"):
            matched_skills.add(intent["skill"])

        # If no matches found, return empty list (let caller handle)
        if not matched_skills:
            logger.debug(f"No skills matched for intent: {intent}")

        return list(matched_skills)

    def _load_skill_metadata(self, skill_name: str) -> Dict:
        """
        Load skill metadata from SKILL.md frontmatter.

        Level 2 context - loaded for planning.

        Args:
            skill_name: Name of the skill

        Returns:
            Skill metadata dict (empty dict if not found)
        """
        cache_key = f"skill_metadata:{skill_name}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        metadata = {}
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"

        if skill_path.exists():
            try:
                content = skill_path.read_text()
                frontmatter, body = self._parse_yaml_frontmatter(content)

                # Extract key metadata fields
                metadata = {
                    "name": frontmatter.get("name", skill_name),
                    "version": frontmatter.get("version") or frontmatter.get("metadata", {}).get("version", "1.0.0"),
                    "description": frontmatter.get("description", ""),
                    "category": frontmatter.get("category", ""),
                    "status": frontmatter.get("metadata", {}).get("status", "active"),
                    "tags": frontmatter.get("metadata", {}).get("tags", []),
                    "inputs": frontmatter.get("inputs", []),
                    "outputs": frontmatter.get("outputs", []),
                    "stages": frontmatter.get("stages", []),
                    "requires_mcp": frontmatter.get("requires_mcp", []),
                    "requires_skills": frontmatter.get("requires_skills", []),
                    "requires_agents": frontmatter.get("requires_agents", []),
                    "quality_gates": frontmatter.get("quality_gates", []),
                    "compatibility": frontmatter.get("compatibility", []),
                    "estimated_runtime": frontmatter.get("metadata", {}).get("estimated_runtime", ""),
                    "max_cost": frontmatter.get("metadata", {}).get("max_cost", ""),
                    "client_facing": frontmatter.get("metadata", {}).get("client_facing", False),
                    "path": str(skill_path.parent),
                    "_frontmatter": frontmatter  # Keep raw frontmatter for reference
                }

                logger.debug(f"Loaded skill metadata: {skill_name}")
            except Exception as e:
                logger.warning(f"Failed to load skill metadata for {skill_name}: {e}")
        else:
            logger.debug(f"Skill not found: {skill_name}")

        self._set_cached(cache_key, metadata)
        return metadata

    def _match_agents_to_skills(self, skill_names: List[str]) -> List[Dict]:
        """
        Find agents relevant to the matched skills.

        Args:
            skill_names: List of skill names

        Returns:
            List of agent metadata dicts
        """
        agent_names: Set[str] = set()

        # Get agents from skill-agent mapping
        for skill_name in skill_names:
            if skill_name in self.SKILL_AGENT_MAP:
                agent_names.update(self.SKILL_AGENT_MAP[skill_name])

            # Also check skill metadata for required agents
            metadata = self._load_skill_metadata(skill_name)
            if metadata.get("requires_agents"):
                agent_names.update(metadata["requires_agents"])

        # Load metadata for each agent
        agents = []
        for agent_name in agent_names:
            agent_meta = self._load_agent_metadata(agent_name)
            if agent_meta:
                agents.append(agent_meta)

        return agents

    def _load_agent_metadata(self, agent_name: str) -> Dict:
        """
        Load agent metadata from AGENT.md or agent markdown files.

        Args:
            agent_name: Name of the agent

        Returns:
            Agent metadata dict (empty dict if not found)
        """
        cache_key = f"agent_metadata:{agent_name}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        metadata = {}

        # Search for agent in various locations
        search_paths = [
            AGENTS_DIR / "workers" / agent_name / "AGENT.md",
            AGENTS_DIR / "workers" / f"{agent_name}.md",
            AGENTS_DIR / "orchestrators" / f"{agent_name}.md",
            AGENTS_DIR / "evaluators" / f"{agent_name}.md",
        ]

        for agent_path in search_paths:
            if agent_path.exists():
                try:
                    content = agent_path.read_text()
                    frontmatter, body = self._parse_yaml_frontmatter(content)

                    metadata = {
                        "name": frontmatter.get("name", agent_name),
                        "type": frontmatter.get("type", "worker"),
                        "version": frontmatter.get("version", "1.0.0"),
                        "description": frontmatter.get("description", ""),
                        "capabilities": frontmatter.get("capabilities", []),
                        "skills": frontmatter.get("skills", []),
                        "model": frontmatter.get("model", {}),
                        "training": frontmatter.get("training", {}),
                        "path": str(agent_path.parent),
                        "_frontmatter": frontmatter
                    }

                    logger.debug(f"Loaded agent metadata: {agent_name}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to load agent metadata for {agent_name}: {e}")

        self._set_cached(cache_key, metadata)
        return metadata

    def _load_platform_config(self, client_id: str, platform: str) -> Dict:
        """
        Load platform-specific configuration for client.

        Args:
            client_id: Client identifier
            platform: Platform name (e.g., "hubspot", "snowflake")

        Returns:
            Platform config dict (empty dict if not found)
        """
        cache_key = f"platform_config:{client_id}:{platform}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        config = {}

        # Try Firebase client config
        if self.firebase:
            try:
                client_doc = self.firebase.get_document("clients", client_id)
                if client_doc:
                    # Check for platform config in settings
                    settings = client_doc.get("settings", {})
                    platform_settings = settings.get("platforms", {}).get(platform, {})
                    if platform_settings:
                        config = platform_settings
            except Exception as e:
                logger.warning(f"Failed to load platform config from Firebase: {e}")

        # Try local datasources.yaml
        if not config:
            datasources_path = CLIENTS_DIR / client_id / "config" / "datasources.yaml"
            if datasources_path.exists():
                try:
                    datasources = yaml.safe_load(datasources_path.read_text())
                    if platform in datasources:
                        config = datasources[platform]
                except Exception as e:
                    logger.warning(f"Failed to load local datasources config: {e}")

        # Load global platform registry info
        registry = self._load_platform_registry()
        platform_info = self._find_platform_in_registry(registry, platform)
        if platform_info:
            config["_registry_info"] = platform_info

        self._set_cached(cache_key, config)
        return config

    def _load_platform_registry(self) -> Dict:
        """Load the platform registry configuration."""
        cache_key = "platform_registry"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        registry = {}
        registry_path = CONFIG_DIR / "platform_registry.yaml"

        if registry_path.exists():
            try:
                # Use safe_load_all for multi-document YAML files
                # and merge all documents into a single dict
                content = registry_path.read_text()
                for doc in yaml.safe_load_all(content):
                    if isinstance(doc, dict):
                        registry.update(doc)
            except Exception as e:
                logger.warning(f"Failed to load platform registry: {e}")

        self._set_cached(cache_key, registry)
        return registry

    def _find_platform_in_registry(self, registry: Dict, platform: str) -> Optional[Dict]:
        """Find platform info in registry."""
        platform_lower = platform.lower()

        for category in ["crm", "data_warehouse", "analytics", "email_marketing"]:
            supported = registry.get(category, {}).get("supported", [])
            for p in supported:
                if p.get("name", "").lower() == platform_lower:
                    return {"category": category, **p}

        return None

    # ============================================================
    # LEVEL 3 LOADERS: Full Content & Patterns
    # ============================================================

    def _load_full_skill(self, skill_name: str) -> Dict:
        """
        Load full skill content including SKILL.md body and related files.

        Level 3 context - loaded for execution.

        Args:
            skill_name: Name of the skill

        Returns:
            Full skill dict with content
        """
        cache_key = f"full_skill:{skill_name}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        # Start with metadata
        skill = dict(self._load_skill_metadata(skill_name))
        skill_dir = SKILLS_DIR / skill_name

        if not skill_dir.exists():
            return skill

        # Load full SKILL.md content
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            try:
                content = skill_md.read_text()
                _, body = self._parse_yaml_frontmatter(content)
                skill["full_content"] = body
            except Exception as e:
                logger.warning(f"Failed to load full skill content: {e}")

        # Load schemas if present
        schemas_dir = skill_dir / "schemas"
        if schemas_dir.exists():
            skill["schemas"] = {}
            for schema_file in schemas_dir.glob("*.json"):
                try:
                    skill["schemas"][schema_file.stem] = json.loads(schema_file.read_text())
                except Exception as e:
                    logger.warning(f"Failed to load schema {schema_file}: {e}")

        # Load stage files if present
        stages_dir = skill_dir / "stages"
        if stages_dir.exists():
            skill["stage_files"] = {}
            for stage_file in stages_dir.glob("*.md"):
                try:
                    skill["stage_files"][stage_file.stem] = stage_file.read_text()
                except Exception as e:
                    logger.warning(f"Failed to load stage file {stage_file}: {e}")

        # Load config if present
        config_file = skill_dir / "config" / "defaults.yaml"
        if config_file.exists():
            try:
                skill["config"] = yaml.safe_load(config_file.read_text())
            except Exception as e:
                logger.warning(f"Failed to load skill config: {e}")

        self._set_cached(cache_key, skill)
        return skill

    def _load_historical_patterns(self, skill_name: str, client_id: str) -> List[Dict]:
        """
        Load historical execution patterns for skill + client combination.

        Args:
            skill_name: Name of the skill
            client_id: Client identifier

        Returns:
            List of pattern dicts
        """
        cache_key = f"patterns:{skill_name}:{client_id}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        patterns = []

        # Try intelligence bridge if available
        if self.bridge:
            try:
                patterns = self.bridge.get_patterns(skill_name, client_id)
            except Exception as e:
                logger.warning(f"Failed to load patterns from intelligence bridge: {e}")

        # Try Firebase telemetry
        if not patterns and self.firebase:
            try:
                # Query recent successful runs
                runs = self.firebase.query(
                    "telemetry_runs",
                    filters=[
                        ("name", "==", skill_name),
                        ("tenant_id", "==", client_id),
                        ("status", "==", "success")
                    ],
                    limit=10,
                    order_by="start_time",
                    order_direction="DESCENDING"
                )

                # Extract pattern data from runs
                for run in runs:
                    pattern = {
                        "run_id": run.get("run_id"),
                        "duration": run.get("duration_seconds"),
                        "tokens": run.get("tokens", {}),
                        "evaluation": run.get("evaluation", {}),
                        "timestamp": run.get("start_time")
                    }
                    patterns.append(pattern)
            except Exception as e:
                logger.warning(f"Failed to load patterns from Firebase: {e}")

        self._set_cached(cache_key, patterns)
        return patterns

    def _load_skill_specific_client_data(self, skill_name: str, client_id: str) -> Dict:
        """
        Load client data specific to a skill's requirements.

        Args:
            skill_name: Name of the skill
            client_id: Client identifier

        Returns:
            Skill-specific client data dict
        """
        cache_key = f"skill_client_data:{skill_name}:{client_id}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        data = {}

        # Get skill metadata to understand requirements
        metadata = self._load_skill_metadata(skill_name)
        requires_context = metadata.get("_frontmatter", {}).get("requires_context", [])

        # Load required context items from Firebase
        if self.firebase and requires_context:
            try:
                for context_item in requires_context:
                    doc = self.firebase.get_document(
                        "context",
                        context_item,
                        subcollection=None,
                        subdoc_id=None
                    )
                    if not doc:
                        # Try as subcollection of client
                        doc = self.firebase.get_document(
                            "clients",
                            client_id,
                            subcollection="context",
                            subdoc_id=context_item
                        )
                    if doc:
                        data[context_item] = doc
            except Exception as e:
                logger.warning(f"Failed to load skill-specific client data: {e}")

        # Try local context files
        context_dir = CLIENTS_DIR / client_id / "context"
        if context_dir.exists():
            for context_item in requires_context:
                if context_item not in data:
                    context_file = context_dir / f"{context_item}.md"
                    if context_file.exists():
                        try:
                            content = context_file.read_text()
                            frontmatter, body = self._parse_yaml_frontmatter(content)
                            data[context_item] = {
                                "content": body,
                                "metadata": frontmatter
                            }
                        except Exception as e:
                            logger.warning(f"Failed to load local context {context_item}: {e}")

        self._set_cached(cache_key, data)
        return data

    # ============================================================
    # MAIN INTERFACES
    # ============================================================

    def load_level_1(self, client_id: str) -> Dict:
        """
        Load Level 1 context: client profile and voice contract.

        This is always loaded regardless of intent or skill.

        Args:
            client_id: Client identifier

        Returns:
            Dict with "client" and "voice_contract" keys
        """
        client = self._load_client_profile(client_id)
        voice_contract = self._load_voice_contract(client_id)

        return {
            "client": client,
            "voice_contract": voice_contract
        }

    def load_level_2(self, client_id: str, intent: Dict) -> Dict:
        """
        Load Level 2 context: skill metadata, agent expertise based on intent.

        Args:
            client_id: Client identifier
            intent: Intent dict with type, keywords, description, etc.

        Returns:
            Dict with "skills", "agents", "platform_config" keys
        """
        # Match skills to intent
        skill_names = self._match_skills_to_intent(intent)

        # Load skill metadata
        skills = []
        for skill_name in skill_names:
            metadata = self._load_skill_metadata(skill_name)
            if metadata:
                skills.append(metadata)

        # Match and load agents
        agents = self._match_agents_to_skills(skill_names)

        # Determine platforms needed
        platforms_needed: Set[str] = set()
        for skill in skills:
            compatibility = skill.get("compatibility", [])
            requires_mcp = skill.get("requires_mcp", [])
            platforms_needed.update(compatibility)
            platforms_needed.update(requires_mcp)

        # Load platform configs
        platform_config = {}
        for platform in platforms_needed:
            config = self._load_platform_config(client_id, platform)
            if config:
                platform_config[platform] = config

        return {
            "skills": skills,
            "agents": agents,
            "platform_config": platform_config,
            "matched_skill_names": skill_names
        }

    def load_level_3(self, client_id: str, skill_name: str) -> Dict:
        """
        Load Level 3 context: full skill content and historical patterns.

        Args:
            client_id: Client identifier
            skill_name: Specific skill to load fully

        Returns:
            Dict with "full_skill", "patterns", "skill_specific_data" keys
        """
        full_skill = self._load_full_skill(skill_name)
        patterns = self._load_historical_patterns(skill_name, client_id)
        skill_specific_data = self._load_skill_specific_client_data(skill_name, client_id)

        return {
            "full_skill": full_skill,
            "patterns": patterns,
            "skill_specific_data": skill_specific_data
        }

    def load_for_planning(self, client_id: str, intent: Dict) -> LoadedContext:
        """
        Load context for the planning phase (Levels 1 & 2).

        Use this when determining which skills and agents to invoke.

        Args:
            client_id: Client identifier
            intent: Intent dict describing user request

        Returns:
            LoadedContext with levels 1 and 2 populated
        """
        budget = ContextBudget()

        # Level 1
        level_1 = self.load_level_1(client_id)
        budget.level_1_used = (
            self._estimate_tokens(level_1["client"]) +
            self._estimate_tokens(level_1["voice_contract"])
        )

        # Level 2
        level_2 = self.load_level_2(client_id, intent)
        budget.level_2_used = (
            self._estimate_tokens(level_2["skills"]) +
            self._estimate_tokens(level_2["agents"]) +
            self._estimate_tokens(level_2["platform_config"])
        )

        context = LoadedContext(
            client=level_1["client"],
            voice_contract=level_1["voice_contract"],
            skills=level_2["skills"],
            agents=level_2["agents"],
            platform_config=level_2["platform_config"],
            budget=budget,
            client_id=client_id,
            loaded_at=datetime.now(timezone.utc).isoformat(),
            levels_loaded=[1, 2]
        )

        self._current_context = context

        logger.info(
            f"Loaded planning context for {client_id}: "
            f"{len(context.skills)} skills, {len(context.agents)} agents, "
            f"budget used: {budget.total_used}/{budget.available} tokens"
        )

        return context

    def load_for_execution(self, client_id: str, skill_name: str) -> LoadedContext:
        """
        Load context for the execution phase (All 3 levels).

        Use this when ready to execute a specific skill.

        Args:
            client_id: Client identifier
            skill_name: Skill to execute

        Returns:
            LoadedContext with all levels populated
        """
        budget = ContextBudget()

        # Level 1
        level_1 = self.load_level_1(client_id)
        budget.level_1_used = (
            self._estimate_tokens(level_1["client"]) +
            self._estimate_tokens(level_1["voice_contract"])
        )

        # Level 2 (focused on single skill)
        skill_metadata = self._load_skill_metadata(skill_name)
        agents = self._match_agents_to_skills([skill_name])

        platforms_needed: Set[str] = set()
        platforms_needed.update(skill_metadata.get("compatibility", []))
        platforms_needed.update(skill_metadata.get("requires_mcp", []))

        platform_config = {}
        for platform in platforms_needed:
            config = self._load_platform_config(client_id, platform)
            if config:
                platform_config[platform] = config

        budget.level_2_used = (
            self._estimate_tokens(skill_metadata) +
            self._estimate_tokens(agents) +
            self._estimate_tokens(platform_config)
        )

        # Level 3
        level_3 = self.load_level_3(client_id, skill_name)
        budget.level_3_used = (
            self._estimate_tokens(level_3["full_skill"]) +
            self._estimate_tokens(level_3["patterns"]) +
            self._estimate_tokens(level_3["skill_specific_data"])
        )

        # Check budget
        if not budget.can_load(0):
            logger.warning(
                f"Context budget exceeded: {budget.total_used}/{budget.available}. "
                "Consider reducing context or using chunked processing."
            )

        context = LoadedContext(
            client=level_1["client"],
            voice_contract=level_1["voice_contract"],
            skills=[skill_metadata] if skill_metadata else [],
            agents=agents,
            platform_config=platform_config,
            full_skill=level_3["full_skill"],
            patterns=level_3["patterns"],
            skill_specific_data=level_3["skill_specific_data"],
            budget=budget,
            client_id=client_id,
            loaded_at=datetime.now(timezone.utc).isoformat(),
            levels_loaded=[1, 2, 3]
        )

        self._current_context = context

        logger.info(
            f"Loaded execution context for {client_id}/{skill_name}: "
            f"budget used: {budget.total_used}/{budget.available} tokens "
            f"(L1: {budget.level_1_used}, L2: {budget.level_2_used}, L3: {budget.level_3_used})"
        )

        return context

    def get_current_context(self) -> Optional[LoadedContext]:
        """Get the currently loaded context."""
        return self._current_context

    def get_available_skills(self) -> List[Dict]:
        """
        Get list of all available skills with basic metadata.

        Useful for discovery and planning.

        Returns:
            List of skill metadata dicts
        """
        skills = []

        if SKILLS_DIR.exists():
            for skill_dir in SKILLS_DIR.iterdir():
                if skill_dir.is_dir() and not skill_dir.name.startswith("_"):
                    metadata = self._load_skill_metadata(skill_dir.name)
                    if metadata:
                        skills.append({
                            "name": metadata.get("name"),
                            "description": metadata.get("description", ""),
                            "category": metadata.get("category", ""),
                            "status": metadata.get("status", "active"),
                            "tags": metadata.get("tags", [])
                        })

        return skills

    def find_skills_for_query(self, query: str) -> List[Dict]:
        """
        Find skills matching a natural language query.

        Args:
            query: Natural language query

        Returns:
            List of matching skill metadata dicts
        """
        intent = {
            "query": query,
            "description": query
        }

        skill_names = self._match_skills_to_intent(intent)

        skills = []
        for name in skill_names:
            metadata = self._load_skill_metadata(name)
            if metadata:
                skills.append(metadata)

        return skills


# ============================================================
# MODULE-LEVEL ACCESSORS
# ============================================================

_orchestrator: Optional[ContextOrchestrator] = None
_orchestrator_lock = threading.Lock()


def get_context_orchestrator(
    firebase_client=None,
    intelligence_bridge=None
) -> ContextOrchestrator:
    """
    Get or create the context orchestrator.

    Args:
        firebase_client: Optional FirebaseClient instance
        intelligence_bridge: Optional IntelligenceBridge instance

    Returns:
        ContextOrchestrator instance
    """
    global _orchestrator

    with _orchestrator_lock:
        if _orchestrator is None:
            _orchestrator = ContextOrchestrator(
                firebase_client=firebase_client,
                intelligence_bridge=intelligence_bridge
            )
        return _orchestrator


def load_planning_context(client_id: str, intent: Dict) -> LoadedContext:
    """
    Convenience function to load planning context.

    Args:
        client_id: Client identifier
        intent: Intent dict

    Returns:
        LoadedContext with levels 1 and 2
    """
    return get_context_orchestrator().load_for_planning(client_id, intent)


def load_execution_context(client_id: str, skill_name: str) -> LoadedContext:
    """
    Convenience function to load execution context.

    Args:
        client_id: Client identifier
        skill_name: Skill to execute

    Returns:
        LoadedContext with all levels
    """
    return get_context_orchestrator().load_for_execution(client_id, skill_name)


# ============================================================
# UNIT TESTS
# ============================================================

if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("Context Orchestrator - Unit Tests")
    print("=" * 60)

    # Test 1: ContextBudget
    print("\n--- Test 1: ContextBudget ---")
    budget = ContextBudget()
    print(f"Available tokens: {budget.available}")
    print(f"Can load 50K: {budget.can_load(50000)}")
    budget.level_1_used = 5000
    budget.level_2_used = 10000
    print(f"After loading L1+L2, remaining: {budget.remaining()}")
    print(f"Budget dict: {budget.to_dict()}")
    assert budget.remaining() == budget.available - 15000
    print("PASSED")

    # Test 2: LoadedContext
    print("\n--- Test 2: LoadedContext ---")
    context = LoadedContext(
        client={"name": "Test Client"},
        skills=[{"name": "lifecycle-audit"}, {"name": "churn-prediction"}],
        client_id="test-123",
        levels_loaded=[1, 2]
    )
    print(f"Skill names: {context.get_skill_names()}")
    print(f"Has level 1: {context.has_level(1)}")
    print(f"Has level 3: {context.has_level(3)}")
    assert context.get_skill_names() == ["lifecycle-audit", "churn-prediction"]
    assert context.has_level(1) is True
    assert context.has_level(3) is False
    print("PASSED")

    # Test 3: Token estimation
    print("\n--- Test 3: Token Estimation ---")
    orchestrator = ContextOrchestrator()

    test_string = "Hello world" * 100
    tokens = orchestrator._estimate_tokens(test_string)
    print(f"String '{len(test_string)} chars' -> {tokens} tokens")
    assert tokens == len(test_string) // 4

    test_dict = {"key": "value" * 50, "nested": {"a": 1, "b": 2}}
    tokens = orchestrator._estimate_tokens(test_dict)
    print(f"Dict estimated at {tokens} tokens")

    tokens_none = orchestrator._estimate_tokens(None)
    assert tokens_none == 0
    print("PASSED")

    # Test 4: YAML frontmatter parsing
    print("\n--- Test 4: YAML Frontmatter Parsing ---")
    test_md = """---
name: test-skill
version: 1.0.0
description: A test skill
metadata:
  tags:
    - test
    - example
---

# Test Skill

This is the body content.
"""
    frontmatter, body = orchestrator._parse_yaml_frontmatter(test_md)
    print(f"Frontmatter keys: {list(frontmatter.keys())}")
    print(f"Body preview: {body[:50]}...")
    assert frontmatter["name"] == "test-skill"
    assert frontmatter["version"] == "1.0.0"
    assert "test" in frontmatter["metadata"]["tags"]
    assert "# Test Skill" in body
    print("PASSED")

    # Test 5: Skill trigger matching
    print("\n--- Test 5: Skill Trigger Matching ---")
    intent1 = {"type": "lifecycle", "description": "audit customer lifecycle"}
    matched = orchestrator._match_skills_to_intent(intent1)
    print(f"Intent 'lifecycle audit' matched: {matched}")
    assert "lifecycle-audit" in matched

    intent2 = {"query": "research company website"}
    matched = orchestrator._match_skills_to_intent(intent2)
    print(f"Intent 'research company' matched: {matched}")
    assert "research-company" in matched

    intent3 = {"type": "hubspot", "keywords": ["crm", "pipeline"]}
    matched = orchestrator._match_skills_to_intent(intent3)
    print(f"Intent 'hubspot crm pipeline' matched: {matched}")
    assert "pipeline-analysis" in matched or "crm-discovery" in matched
    print("PASSED")

    # Test 6: Caching
    print("\n--- Test 6: Caching ---")
    orchestrator._set_cached("test_key", {"data": "cached_value"})
    cached = orchestrator._get_cached("test_key")
    assert cached == {"data": "cached_value"}
    print("Cache set and get: PASSED")

    orchestrator.clear_cache("test_key")
    cached = orchestrator._get_cached("test_key")
    assert cached is None
    print("Cache clear single: PASSED")

    orchestrator._set_cached("key1", "value1")
    orchestrator._set_cached("key2", "value2")
    orchestrator.clear_cache()
    assert orchestrator._get_cached("key1") is None
    assert orchestrator._get_cached("key2") is None
    print("Cache clear all: PASSED")

    # Test 7: Skill metadata loading (if skills exist)
    print("\n--- Test 7: Skill Metadata Loading ---")
    if SKILLS_DIR.exists():
        # Find a skill to test with
        for skill_dir in SKILLS_DIR.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith("_"):
                skill_name = skill_dir.name
                metadata = orchestrator._load_skill_metadata(skill_name)
                print(f"Loaded '{skill_name}' metadata:")
                print(f"  - Name: {metadata.get('name')}")
                print(f"  - Version: {metadata.get('version')}")
                print(f"  - Status: {metadata.get('status')}")
                print(f"  - Tags: {metadata.get('tags')}")
                assert metadata.get("name") is not None
                print("PASSED")
                break
    else:
        print("Skills directory not found, skipping")

    # Test 8: Agent metadata loading (if agents exist)
    print("\n--- Test 8: Agent Metadata Loading ---")
    if AGENTS_DIR.exists():
        # Find an agent to test with
        found_agent = False
        for agent_type in ["workers", "orchestrators", "evaluators"]:
            agent_dir = AGENTS_DIR / agent_type
            if agent_dir.exists():
                for agent_file in agent_dir.glob("*.md"):
                    if not agent_file.name.endswith("_TEMPLATE.md"):
                        agent_name = agent_file.stem
                        metadata = orchestrator._load_agent_metadata(agent_name)
                        if metadata:
                            print(f"Loaded '{agent_name}' metadata:")
                            print(f"  - Type: {metadata.get('type')}")
                            print(f"  - Description preview: {str(metadata.get('description', ''))[:50]}...")
                            print("PASSED")
                            found_agent = True
                            break
            if found_agent:
                break
        if not found_agent:
            print("No agents found, skipping")
    else:
        print("Agents directory not found, skipping")

    # Test 9: Full planning context load (mock client)
    print("\n--- Test 9: Planning Context Load ---")
    context = orchestrator.load_for_planning(
        client_id="mock-client-123",
        intent={"type": "lifecycle", "description": "audit customer journey"}
    )
    print(f"Client ID: {context.client_id}")
    print(f"Levels loaded: {context.levels_loaded}")
    print(f"Skills found: {context.get_skill_names()}")
    print(f"Budget used: {context.budget.total_used} tokens")
    assert 1 in context.levels_loaded
    assert 2 in context.levels_loaded
    print("PASSED")

    # Test 10: Full execution context load (mock client)
    print("\n--- Test 10: Execution Context Load ---")
    # Find a real skill to load
    if SKILLS_DIR.exists():
        for skill_dir in SKILLS_DIR.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith("_"):
                skill_name = skill_dir.name
                context = orchestrator.load_for_execution(
                    client_id="mock-client-123",
                    skill_name=skill_name
                )
                print(f"Loaded execution context for '{skill_name}':")
                print(f"  - Levels loaded: {context.levels_loaded}")
                print(f"  - Full skill has content: {bool(context.full_skill.get('full_content'))}")
                print(f"  - Budget breakdown:")
                print(f"    - L1: {context.budget.level_1_used}")
                print(f"    - L2: {context.budget.level_2_used}")
                print(f"    - L3: {context.budget.level_3_used}")
                print(f"    - Total: {context.budget.total_used}")
                assert 3 in context.levels_loaded
                print("PASSED")
                break

    # Test 11: Available skills list
    print("\n--- Test 11: Available Skills List ---")
    available = orchestrator.get_available_skills()
    print(f"Found {len(available)} available skills")
    if available:
        print(f"Sample skill: {available[0]}")
    print("PASSED")

    # Test 12: Find skills for query
    print("\n--- Test 12: Find Skills for Query ---")
    skills = orchestrator.find_skills_for_query("help me identify at-risk customers")
    print(f"Query 'at-risk customers' found: {[s.get('name') for s in skills]}")

    skills = orchestrator.find_skills_for_query("create linkedin content for my founder")
    print(f"Query 'linkedin content' found: {[s.get('name') for s in skills]}")
    print("PASSED")

    # Summary
    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)
    print("\nUsage examples:")
    print("""
    from lib.context_orchestrator import (
        get_context_orchestrator,
        load_planning_context,
        load_execution_context
    )

    # Planning phase
    context = load_planning_context(
        client_id="my-client",
        intent={"type": "lifecycle", "description": "audit customer journey"}
    )
    print(f"Matched skills: {context.get_skill_names()}")

    # Execution phase
    context = load_execution_context(
        client_id="my-client",
        skill_name="lifecycle-audit"
    )
    print(f"Full skill loaded, budget: {context.budget.remaining()} tokens remaining")
    """)
