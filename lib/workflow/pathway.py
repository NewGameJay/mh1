"""
Pathway Detection for MH1

Determines which workflow to follow based on user input and context.
"""

from enum import Enum
from typing import Optional
import re


class Pathway(Enum):
    """Available workflow pathways."""
    ONBOARDING = "onboarding"
    MODULE = "module"
    MODULE_WITH_MRD = "module_with_mrd"
    MODULE_WITH_PLAN = "module_with_plan"
    SKILL = "skill"
    CONFIG = "config"
    FLEX = "flex"


# Keywords that suggest each pathway
ONBOARDING_KEYWORDS = [
    "onboard", "new client", "add company", "setup client", "new company",
    "add client", "create client", "start fresh", "new account"
]

MODULE_KEYWORDS = [
    "audit", "campaign", "launch", "project", "initiative", "comprehensive",
    "full", "complete", "end-to-end", "module", "plan out", "strategy for",
    "build a", "create a plan", "run a full", "do a complete"
]

CONFIG_KEYWORDS = [
    "connect", "setup mcp", "add integration", "configure", "link my",
    "connect to", "setup api", "add api", "credentials", "oauth",
    "authenticate", "login to"
]

SKILL_PATTERNS = [
    r"run (?:a |the )?(\w+[\-\w]*)",
    r"execute (?:the )?(\w+[\-\w]*)",
    r"do (?:a |an )?(\w+[\-\w]*) (?:analysis|audit|check)",
    r"generate (?:a |an )?(\w+[\-\w]*)",
    r"create (?:a |an )?(\w+[\-\w]*) (?:report|analysis)",
]

# Skills that typically work alone (don't need modules)
SINGLE_SKILLS = [
    "research-company", "competitive-intel", "social-listening",
    "ghostwrite-content", "email-copy-generator", "find-skills",
    "cohort-retention", "churn-prediction", "at-risk-detection"
]


def detect_pathway(
    user_input: str,
    client_id: Optional[str] = None,
    has_uploaded_file: bool = False,
    uploaded_file_type: Optional[str] = None,
    available_skills: Optional[list] = None,
    existing_clients: Optional[list] = None
) -> tuple[Pathway, dict]:
    """
    Detect which workflow pathway to follow.

    Args:
        user_input: The user's message
        client_id: Current client ID (None if no client selected)
        has_uploaded_file: Whether user uploaded a file
        uploaded_file_type: Type of uploaded file (mrd, plan, etc.)
        available_skills: List of available skill names
        existing_clients: List of existing client IDs

    Returns:
        Tuple of (Pathway, metadata dict with details)
    """
    input_lower = user_input.lower().strip()
    metadata = {"raw_input": user_input}

    # No client = needs onboarding (unless explicitly asking something else)
    if not client_id:
        # Check if they're asking a general question
        if _is_general_question(input_lower):
            return Pathway.FLEX, {"reason": "general_question_no_client"}
        # Otherwise, prompt for onboarding
        return Pathway.ONBOARDING, {"reason": "no_client", "trigger": "missing_context"}

    # Check for explicit onboarding request
    if any(kw in input_lower for kw in ONBOARDING_KEYWORDS):
        return Pathway.ONBOARDING, {"reason": "explicit_request"}

    # Check if input looks like a new client name
    new_client = _detect_new_client_name(user_input, existing_clients)
    if new_client:
        return Pathway.ONBOARDING, {"reason": "new_client_name", "client_name": new_client}

    # Check for uploaded files
    if has_uploaded_file:
        if uploaded_file_type == "mrd":
            return Pathway.MODULE_WITH_MRD, {"reason": "uploaded_mrd"}
        if uploaded_file_type == "plan":
            return Pathway.MODULE_WITH_PLAN, {"reason": "uploaded_plan"}

    # Check for config/setup requests
    if any(kw in input_lower for kw in CONFIG_KEYWORDS):
        platform = _extract_platform(input_lower)
        return Pathway.CONFIG, {"reason": "config_request", "platform": platform}

    # Check for explicit module keywords
    if any(kw in input_lower for kw in MODULE_KEYWORDS):
        estimated_skills = _estimate_skills_needed(input_lower, available_skills)
        if estimated_skills >= 3:
            return Pathway.MODULE, {
                "reason": "complex_task",
                "estimated_skills": estimated_skills
            }

    # Check for skill-specific requests
    matched_skill = _match_skill(input_lower, available_skills)
    if matched_skill:
        # Check if this skill typically needs a module
        if matched_skill in SINGLE_SKILLS:
            return Pathway.SKILL, {"reason": "matched_skill", "skill": matched_skill}
        # Estimate complexity
        estimated_skills = _estimate_skills_needed(input_lower, available_skills)
        if estimated_skills >= 3:
            return Pathway.MODULE, {
                "reason": "complex_skill_request",
                "primary_skill": matched_skill,
                "estimated_skills": estimated_skills
            }
        return Pathway.SKILL, {"reason": "matched_skill", "skill": matched_skill}

    # Default to flex conversation
    return Pathway.FLEX, {"reason": "conversation"}


def _is_general_question(text: str) -> bool:
    """Check if input is a general question."""
    question_starters = [
        "what is", "what are", "how do", "how does", "can you",
        "tell me about", "explain", "why", "when", "who", "which",
        "what skills", "what agents", "help me understand"
    ]
    return any(text.startswith(q) for q in question_starters)


def _detect_new_client_name(text: str, existing_clients: Optional[list]) -> Optional[str]:
    """
    Detect if input looks like a new client/company name.

    Returns the client name if detected, None otherwise.
    """
    text = text.strip()
    text_lower = text.lower()

    # Skip if it's clearly a question or command
    skip_starters = [
        "what", "how", "why", "when", "where", "who", "which", "can", "could",
        "would", "should", "is", "are", "do", "does", "run", "execute", "create",
        "help", "show", "list", "find", "search", "tell", "explain", "hi", "hello",
        "hey", "thanks", "thank", "yes", "no", "ok", "okay", "sure", "quit", "exit"
    ]
    first_word = text_lower.split()[0] if text_lower.split() else ""
    if first_word in skip_starters:
        return None

    # Skip if it contains common action verbs mid-sentence
    action_phrases = [
        "audit", "analyze", "research", "generate", "build", "create a",
        "run a", "do a", "make a", "start a", "launch", "plan", "strategy"
    ]
    if any(phrase in text_lower for phrase in action_phrases):
        return None

    # Skip single common words
    common_words = [
        "start", "begin", "continue", "stop", "cancel", "help", "skills",
        "agents", "clients", "history", "status", "settings", "config"
    ]
    if text_lower in common_words:
        return None

    # Looks like a company name if:
    # 1. Short (1-5 words)
    # 2. Contains capital letters or is Title Case
    # 3. Not an existing client

    words = text.split()
    if len(words) > 5:
        return None

    # Check if it's already an existing client
    if existing_clients:
        text_slug = text_lower.replace(" ", "-")
        for client in existing_clients:
            client_lower = client.lower()
            if text_slug == client_lower or text_lower == client_lower.replace("-", " "):
                return None  # Already exists, not a new client

    # Check for company name patterns:
    # - Title Case (e.g., "Acme Corp")
    # - Contains common business suffixes
    # - Short phrase with capitals

    business_suffixes = [
        "inc", "llc", "corp", "co", "ltd", "company", "technologies",
        "tech", "labs", "studio", "studios", "media", "group", "ai",
        "io", "app", "software", "solutions", "services", "consulting"
    ]

    # Has a business suffix
    if any(text_lower.endswith(suffix) or f" {suffix}" in text_lower for suffix in business_suffixes):
        return text

    # Is Title Case and 1-3 words (likely a company name)
    if len(words) <= 3:
        # Check if it looks like Title Case or has mixed case (brand names)
        has_capitals = any(c.isupper() for c in text)
        if has_capitals and not text.isupper():  # Not all caps (like "HELP")
            # Additional check: first letter of each word is capital
            is_title_case = all(word[0].isupper() for word in words if word)
            if is_title_case:
                return text

    return None


def _extract_platform(text: str) -> Optional[str]:
    """Extract platform name from config request."""
    platforms = [
        "hubspot", "salesforce", "pipedrive", "zoho", "snowflake",
        "bigquery", "redshift", "postgres", "firebase", "notion",
        "airtable", "slack", "zapier", "segment", "amplitude"
    ]
    for platform in platforms:
        if platform in text:
            return platform
    return None


def _match_skill(text: str, available_skills: Optional[list]) -> Optional[str]:
    """Match input to a specific skill."""
    if not available_skills:
        return None

    # Direct name match
    for skill in available_skills:
        if skill.replace("-", " ") in text or skill in text:
            return skill

    # Pattern matching
    for pattern in SKILL_PATTERNS:
        match = re.search(pattern, text)
        if match:
            potential_skill = match.group(1).lower()
            # Find closest skill
            for skill in available_skills:
                if potential_skill in skill or skill in potential_skill:
                    return skill

    # Semantic matching for common phrases
    phrase_to_skill = {
        "lifecycle": "lifecycle-audit",
        "retention": "cohort-retention",
        "churn": "churn-prediction",
        "at risk": "at-risk-detection",
        "competitor": "competitive-intel",
        "email sequence": "email-sequences",
        "email copy": "email-copy-generator",
        "newsletter": "newsletter-builder",
        "ghost": "ghostwrite-content",
        "linkedin post": "ghostwrite-content",
        "social listen": "social-listening",
        "research": "research-company",
        "onboard": "client-onboarding",
        "persona": "persona-development",
        "journey": "customer-journey-mapping",
        "gtm": "gtm-plan",
        "go to market": "gtm-plan",
    }

    for phrase, skill in phrase_to_skill.items():
        if phrase in text and skill in available_skills:
            return skill

    return None


def _estimate_skills_needed(text: str, available_skills: Optional[list]) -> int:
    """Estimate how many skills a request might need."""
    if not available_skills:
        return 1

    # Count how many skill-related concepts are mentioned
    skill_concepts = 0
    concept_keywords = [
        "audit", "analysis", "report", "emails", "sequences", "content",
        "research", "competitors", "personas", "journey", "funnel",
        "retention", "churn", "activation", "engagement", "automation",
        "campaign", "strategy", "plan"
    ]

    for keyword in concept_keywords:
        if keyword in text.lower():
            skill_concepts += 1

    # Complexity indicators
    complexity_words = ["comprehensive", "full", "complete", "end-to-end", "detailed", "thorough"]
    if any(word in text.lower() for word in complexity_words):
        skill_concepts += 2

    # "and" typically means multiple things
    skill_concepts += text.lower().count(" and ")

    return max(1, skill_concepts)


def pathway_description(pathway: Pathway) -> str:
    """Get human-readable description of a pathway."""
    descriptions = {
        Pathway.ONBOARDING: "New client setup and discovery",
        Pathway.MODULE: "Complex project with multiple skills",
        Pathway.MODULE_WITH_MRD: "Project with uploaded requirements",
        Pathway.MODULE_WITH_PLAN: "Project with uploaded plan",
        Pathway.SKILL: "Single skill execution",
        Pathway.CONFIG: "Platform configuration and setup",
        Pathway.FLEX: "General conversation and questions",
    }
    return descriptions.get(pathway, "Unknown pathway")
