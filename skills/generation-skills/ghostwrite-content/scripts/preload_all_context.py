#!/usr/bin/env python3
"""
Preload all context for ghostwriting in a single script.
Multi-client marketing platform - mh1-hq structure.

This script consolidates ALL context loading into one place.

**Context Loading Priority**:
1. LOCAL FIRST: Attempts to load from clients/{clientId}/context/*.md
2. FIREBASE FALLBACK: Falls back to Firebase if local files don't exist

**Data that ALWAYS comes from Firebase** (not available locally):
- Signals (signals collection)
- Thought leader posts (thoughtLeaders/*/posts)
- Parallel events (parallelEvents)
- Founder posts (founders/*/posts)

Outputs:
- context_bundle.json: All context for all stages (~22KB)
- voice_contract.json: Compact founder voice rules (~2KB)

Usage:
    python preload_all_context.py <client_id> <founder_id> [options]

Arguments:
    client_id: Firebase Client ID (or read from active_client.md)
    founder_id: Firebase founder document ID
    --client-name: Client display name (default: derived from folder)
    --folder-name: Local folder name for context files (default: client_name)
    --output-dir: Directory for output files (default: current directory)
    --founder-posts-limit: Max founder posts to include (default: 50)
    --canonical-examples: Number of canonical post examples (default: 3)
    --firebase-only: Skip local file check, always use Firebase
"""

import json
import sys
import os
import argparse
import re
from datetime import datetime, timezone
from collections import Counter
from pathlib import Path

# Force UTF-8 encoding on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add lib to path for client utilities
SKILL_ROOT = Path(__file__).parent.parent
SYSTEM_ROOT = SKILL_ROOT.parent.parent
sys.path.insert(0, str(SYSTEM_ROOT / "lib"))

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    print("Installing firebase-admin...", file=sys.stderr)
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "firebase-admin", "-q"])
    import firebase_admin
    from firebase_admin import credentials, firestore


def get_client_from_active_file():
    """Read client configuration from inputs/active_client.md."""
    active_client_path = SYSTEM_ROOT / "inputs" / "active_client.md"
    if not active_client_path.exists():
        return None, None, None, None
    
    with open(active_client_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    client_id = None
    client_name = None
    folder_name = None
    default_founder = None
    
    for line in content.split('\n'):
        if 'Firestore Client ID:' in line:
            client_id = line.split(':', 1)[1].strip()
        elif 'Client Name:' in line:
            client_name = line.split(':', 1)[1].strip()
        elif 'Folder Name:' in line:
            folder_name = line.split(':', 1)[1].strip()
        elif 'Default Ghostwrite Founder:' in line:
            default_founder = line.split(':', 1)[1].strip()
    
    return client_id, client_name, folder_name, default_founder


def find_firebase_credentials():
    """Find Firebase credentials file in common locations."""
    search_paths = [
        os.getcwd(),
        os.path.dirname(os.getcwd()),
        str(SYSTEM_ROOT),
    ]

    for path in search_paths:
        try:
            for filename in os.listdir(path):
                if 'firebase' in filename.lower() and filename.endswith('.json'):
                    if 'adminsdk' in filename.lower():
                        return os.path.join(path, filename)
        except (OSError, PermissionError):
            continue

    if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
        return os.environ['GOOGLE_APPLICATION_CREDENTIALS']

    return None


# ============================================================================
# LOCAL MARKDOWN PARSING FUNCTIONS
# ============================================================================

def parse_markdown_table(lines, start_idx):
    """Parse a markdown table into a list of dicts."""
    rows = []
    headers = []
    i = start_idx

    while i < len(lines):
        line = lines[i].strip()
        if not line.startswith('|'):
            break

        cells = [c.strip() for c in line.split('|')[1:-1]]

        if not headers:
            headers = cells
        elif all(c.replace('-', '').replace(':', '') == '' for c in cells):
            pass
        else:
            if len(cells) == len(headers):
                row = {headers[j]: cells[j] for j in range(len(headers))}
                rows.append(row)
        i += 1

    return rows, i


def parse_markdown_list(lines, start_idx):
    """Parse a markdown list into a list of strings."""
    items = []
    i = start_idx

    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('- ') or line.startswith('* '):
            item = line[2:].strip()
            items.append(item)
            i += 1
        elif line.startswith('  - ') or line.startswith('  * '):
            if items:
                items[-1] += ' | ' + line.strip()[2:]
            i += 1
        elif line == '' or line.startswith('#'):
            break
        else:
            i += 1
            break

    return items, i


def parse_key_value_list(items):
    """Convert list items with **Key:** Value format to dict."""
    result = {}
    for item in items:
        if ':**' in item:
            match = re.match(r'\*\*([^*]+)\*\*:?\s*(.*)', item)
            if match:
                key = match.group(1).strip().lower().replace(' ', '_')
                value = match.group(2).strip()
                result[key] = value
        elif ':' in item and not item.startswith('http'):
            parts = item.split(':', 1)
            if len(parts) == 2:
                key = parts[0].strip().lower().replace(' ', '_')
                value = parts[1].strip()
                result[key] = value
    return result


def normalize_key(text):
    """Convert header text to camelCase key."""
    words = re.sub(r'[^a-zA-Z0-9\s]', '', text).strip().split()
    if not words:
        return text.lower()
    return words[0].lower() + ''.join(w.title() for w in words[1:])


def parse_markdown_section(lines, start_idx, current_level):
    """Recursively parse a markdown section."""
    result = {}
    content_lines = []
    i = start_idx

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith('#'):
            level = len(stripped) - len(stripped.lstrip('#'))
            header_text = stripped.lstrip('#').strip()

            if level <= current_level:
                break
            elif level == current_level + 1:
                key = normalize_key(header_text)
                child_result, i = parse_markdown_section(lines, i + 1, level)
                result[key] = child_result
                continue

        elif stripped.startswith('|') and i + 1 < len(lines) and lines[i + 1].strip().startswith('|'):
            table_data, i = parse_markdown_table(lines, i)
            if table_data:
                if not result:
                    return table_data, i
                else:
                    result['_table'] = table_data
            continue

        elif stripped.startswith('- ') or stripped.startswith('* '):
            list_items, i = parse_markdown_list(lines, i)
            if list_items:
                kv = parse_key_value_list(list_items)
                if kv:
                    result.update(kv)
                elif not result:
                    return list_items, i
                else:
                    result['_items'] = list_items
            continue

        elif stripped and not stripped.startswith('---'):
            content_lines.append(stripped)

        i += 1

    if content_lines and not result:
        return ' '.join(content_lines), i

    if content_lines:
        result['description'] = ' '.join(content_lines)

    return result if result else '', i


def load_context_from_local_markdown(doc_name, client_id):
    """Load a context document from local markdown file."""
    # Try clients/{clientId}/context/ path
    client_context_path = SYSTEM_ROOT / "clients" / client_id / "context" / f"{doc_name}.md"
    
    if not client_context_path.exists():
        return None, None

    try:
        with open(client_context_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        start_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('# '):
                start_idx = i + 1
                break

        result, _ = parse_markdown_section(lines, start_idx, 1)
        result = normalize_parsed_context(doc_name, result)

        return result, f"local:{client_context_path}"

    except Exception as e:
        print(f"  WARNING: Error parsing local file {client_context_path}: {e}", file=sys.stderr)
        return None, None


def normalize_parsed_context(doc_name, data):
    """Normalize parsed markdown data to match expected Firebase schema."""
    if not isinstance(data, dict):
        return data

    if doc_name == "brand":
        normalized = {}
        if 'companyProfile' in data:
            normalized['companyProfile'] = data['companyProfile']
        if 'brandVoice' in data:
            bv = data['brandVoice']
            normalized['brandVoice'] = {
                'tone': bv.get('tone', []) if isinstance(bv.get('tone'), list) else [],
                'personality': bv.get('personality', []) if isinstance(bv.get('personality'), list) else [],
                'guidelines': bv.get('guidelines', []) if isinstance(bv.get('guidelines'), list) else [],
                'examples': bv.get('examples', {})
            }
        if 'visualGuidelines' in data:
            normalized['visualGuidelines'] = data['visualGuidelines']
        normalized['dataQuality'] = 'Strong'
        normalized['source'] = 'Local File'
        return normalized if normalized else data

    elif doc_name == "messaging":
        normalized = {}
        if 'positioning' in data:
            normalized['positioning'] = data['positioning']
        if 'valuePropositions' in data:
            normalized['valuePropositions'] = data['valuePropositions']
        if 'keyMessages' in data:
            normalized['keyMessages'] = data['keyMessages']
        normalized['dataQuality'] = 'Strong'
        normalized['source'] = 'Local File'
        return normalized if normalized else data

    elif doc_name == "audience":
        normalized = {}
        if 'personas' in data:
            normalized['personas'] = data['personas']
        if 'icpTargets' in data:
            normalized['icpTargets'] = data['icpTargets']
        if 'segments' in data:
            normalized['segments'] = data['segments']
        normalized['dataQuality'] = 'Strong'
        normalized['source'] = 'Local File'
        return normalized if normalized else data

    data['dataQuality'] = data.get('dataQuality', 'Strong')
    data['source'] = data.get('source', 'Local File')
    return data


def load_context_document(db, doc_name, client_id, firebase_only=False):
    """Load a single context document, trying local first then Firebase."""
    if not firebase_only:
        local_data, source = load_context_from_local_markdown(doc_name, client_id)
        if local_data:
            return local_data, source

    try:
        doc_ref = db.collection("clients").document(client_id).collection("context").document(doc_name)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict(), f"firebase:clients/{client_id}/context/{doc_name}"
        else:
            print(f"  WARNING: context/{doc_name} does not exist in local or Firebase", file=sys.stderr)
            return None, None
    except Exception as e:
        print(f"  ERROR loading context/{doc_name}: {e}", file=sys.stderr)
        return None, None


def load_founder_profile(db, client_id, founder_id):
    """Load founder profile from Firebase."""
    try:
        doc_ref = db.collection("clients").document(client_id).collection("founders").document(founder_id)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            data["id"] = doc.id
            return data
        else:
            print(f"  WARNING: founders/{founder_id} does not exist", file=sys.stderr)
            return None
    except Exception as e:
        print(f"  ERROR loading founder profile: {e}", file=sys.stderr)
        return None


def load_founder_posts(db, client_id, founder_id, limit=50):
    """Load founder posts from Firebase."""
    try:
        posts_ref = db.collection("clients").document(client_id) \
            .collection("founders").document(founder_id).collection("posts")
        docs = posts_ref.stream()

        posts = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            posts.append(data)

        posts.sort(key=lambda p: p.get("postedAt", ""), reverse=True)
        return posts[:limit]
    except Exception as e:
        print(f"  ERROR loading founder posts: {e}", file=sys.stderr)
        return []


def analyze_sentence_structure(posts):
    """Analyze sentence structure patterns from posts."""
    if not posts:
        return {"averageLength": 12, "openingStyle": "Variable", "paragraphPattern": "2-3 sentences"}

    sentence_lengths = []
    first_sentences = []

    for post in posts:
        content = post.get("content", "")
        if not content:
            continue

        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]

        for sent in sentences:
            words = sent.split()
            sentence_lengths.append(len(words))

        if sentences:
            first_sentences.append(sentences[0])

    avg_length = round(sum(sentence_lengths) / len(sentence_lengths), 1) if sentence_lengths else 12

    short_openers = sum(1 for s in first_sentences if len(s.split()) < 12)
    opening_style = "Short punchy openers" if short_openers > len(first_sentences) * 0.6 else "Variable length openers"

    return {
        "averageLength": avg_length,
        "openingStyle": opening_style,
        "paragraphPattern": "2-3 sentences per paragraph"
    }


def analyze_vocabulary(posts, founder_profile):
    """Analyze vocabulary patterns from posts."""
    if not posts:
        return {
            "register": "casual-professional",
            "contractions": True,
            "avoidList": [],
            "signaturePhrases": []
        }

    all_text = " ".join(p.get("content", "") for p in posts)
    all_text_lower = all_text.lower()

    has_contractions = any(c in all_text_lower for c in ["don't", "won't", "can't", "it's", "i'm", "we're", "they're"])

    formal_indicators = ["leverage", "synergy", "facilitate", "optimize", "strategic"]
    casual_indicators = ["honestly", "literally", "basically", "actually", "totally"]

    formal_count = sum(1 for word in formal_indicators if word in all_text_lower)
    casual_count = sum(1 for word in casual_indicators if word in all_text_lower)

    if formal_count > casual_count:
        register = "professional"
    elif casual_count > formal_count:
        register = "casual"
    else:
        register = "casual-professional"

    words = all_text_lower.split()
    trigrams = [" ".join(words[i:i+3]) for i in range(len(words)-2)]
    trigram_counts = Counter(trigrams)

    generic_phrases = {"in the", "of the", "to the", "and the", "on the", "for the", "at the"}
    signature_phrases = [
        phrase.title() for phrase, count in trigram_counts.most_common(20)
        if count >= 2 and phrase not in generic_phrases and len(phrase) > 8
    ][:5]

    avoid_list = []
    corporate_phrases = ["leverage", "synergy", "game-changing", "revolutionary", "innovative",
                        "excited to announce", "thrilled to share", "humbled and honored"]
    for phrase in corporate_phrases:
        if phrase not in all_text_lower:
            avoid_list.append(phrase)

    return {
        "register": register,
        "contractions": has_contractions,
        "avoidList": avoid_list[:10],
        "signaturePhrases": signature_phrases
    }


def analyze_rhetoric(posts, founder_profile):
    """Analyze rhetorical patterns from posts."""
    if not posts:
        return {
            "rhetoricalQuestions": False,
            "hookPattern": "Variable",
            "ctaStyle": "Question + engagement prompt"
        }

    all_text = " ".join(p.get("content", "") for p in posts)

    question_count = all_text.count("?")
    rhetorical = question_count > len(posts) * 0.3

    hook_patterns = []
    for post in posts[:10]:
        content = post.get("content", "")
        first_line = content.split("\n")[0] if content else ""

        if first_line.endswith("?"):
            hook_patterns.append("question")
        elif any(word in first_line.lower() for word in ["most", "every", "never", "always"]):
            hook_patterns.append("contrarian")
        elif re.search(r'\d+%|\d+ out of|\d+x', first_line):
            hook_patterns.append("stat")
        else:
            hook_patterns.append("statement")

    pattern_counts = Counter(hook_patterns)
    dominant_hook = pattern_counts.most_common(1)[0][0] if pattern_counts else "statement"

    hook_descriptions = {
        "question": "Opening question to engage reader",
        "contrarian": "Contrarian or provocative statement",
        "stat": "Surprising statistic or number",
        "statement": "Direct declarative statement"
    }

    return {
        "rhetoricalQuestions": rhetorical,
        "hookPattern": hook_descriptions.get(dominant_hook, "Variable"),
        "ctaStyle": "Question + engagement prompt"
    }


def analyze_length_profile(posts):
    """Analyze post length patterns."""
    if not posts:
        return {
            "sweetSpot": {"min": 800, "max": 1500},
            "averageCharCount": 1150
        }

    lengths = [len(p.get("content", "")) for p in posts if p.get("content")]

    if not lengths:
        return {
            "sweetSpot": {"min": 800, "max": 1500},
            "averageCharCount": 1150
        }

    avg_length = int(sum(lengths) / len(lengths))
    min_length = min(lengths)
    max_length = max(lengths)

    sorted_lengths = sorted(lengths)
    lower_idx = int(len(sorted_lengths) * 0.2)
    upper_idx = int(len(sorted_lengths) * 0.8)

    sweet_min = sorted_lengths[lower_idx] if lower_idx < len(sorted_lengths) else min_length
    sweet_max = sorted_lengths[upper_idx] if upper_idx < len(sorted_lengths) else max_length

    return {
        "sweetSpot": {"min": sweet_min, "max": sweet_max},
        "averageCharCount": avg_length
    }


def analyze_post_type_distribution(posts):
    """Classify posts by type and calculate distribution."""
    if not posts:
        return {
            "distribution": {},
            "total": 0,
            "varietyGuidance": "No posts available for analysis"
        }

    types = {
        "short_take": [],
        "announcement": [],
        "deep_dive": [],
        "industry_comment": [],
        "hot_take": [],
        "educational": [],
        "promotional": []
    }

    announcement_keywords = ["excited to share", "announcing", "launching", "hiring",
                           "joining", "event", "live", "register", "save the date",
                           "something big", "we're"]
    hot_take_keywords = ["most people", "unpopular", "hot take", "prediction",
                        "wrong", "myth", "mistake", "actually", "here's the thing"]
    educational_keywords = ["framework", "checklist", "step 1", "step 2", "how to",
                           "here's how", "->", "tips", "guide"]
    industry_keywords = ["just announced", "acquired", "raised", "industry",
                        "market", "trend", "research shows"]

    for post in posts:
        content = post.get("content", "")
        content_lower = content.lower()
        length = len(content)
        post_id = post.get("id", "unknown")

        if length < 300:
            if any(kw in content_lower for kw in announcement_keywords):
                types["announcement"].append({"id": post_id, "length": length, "preview": content[:100]})
            else:
                types["short_take"].append({"id": post_id, "length": length, "preview": content[:100]})
        elif any(kw in content_lower for kw in announcement_keywords):
            types["announcement"].append({"id": post_id, "length": length, "preview": content[:100]})
        elif any(kw in content_lower for kw in hot_take_keywords):
            types["hot_take"].append({"id": post_id, "length": length, "preview": content[:100]})
        elif any(kw in content_lower for kw in educational_keywords):
            types["educational"].append({"id": post_id, "length": length, "preview": content[:100]})
        elif any(kw in content_lower for kw in industry_keywords):
            types["industry_comment"].append({"id": post_id, "length": length, "preview": content[:100]})
        elif length > 800:
            types["deep_dive"].append({"id": post_id, "length": length, "preview": content[:100]})
        else:
            types["promotional"].append({"id": post_id, "length": length, "preview": content[:100]})

    total = len(posts)
    distribution = {}
    for type_name, type_posts in types.items():
        count = len(type_posts)
        if count > 0:
            distribution[type_name] = {
                "count": count,
                "percentage": round(count / total * 100, 1),
                "examples": type_posts[:2]
            }

    guidance_parts = []
    if distribution.get("short_take", {}).get("count", 0) > 0:
        pct = distribution["short_take"]["percentage"]
        guidance_parts.append(f"{pct:.0f}% short takes (<300 chars)")
    if distribution.get("hot_take", {}).get("count", 0) > 0:
        pct = distribution["hot_take"]["percentage"]
        guidance_parts.append(f"{pct:.0f}% hot takes/opinions")
    if distribution.get("deep_dive", {}).get("count", 0) > 0:
        pct = distribution["deep_dive"]["percentage"]
        guidance_parts.append(f"{pct:.0f}% deep dives (>800 chars)")
    if distribution.get("announcement", {}).get("count", 0) > 0:
        pct = distribution["announcement"]["percentage"]
        guidance_parts.append(f"{pct:.0f}% announcements")

    variety_guidance = "Founder's post mix: " + ", ".join(guidance_parts) if guidance_parts else "Varied content types"

    return {
        "distribution": distribution,
        "total": total,
        "varietyGuidance": variety_guidance,
        "shortPostCount": len(types["short_take"]),
        "longPostCount": len(types["deep_dive"])
    }


def select_canonical_examples(posts, count=3):
    """Select canonical examples from posts."""
    if not posts:
        return []

    examples = []

    sorted_posts = sorted(
        posts,
        key=lambda p: (p.get("likes", 0) or 0) + (p.get("comments", 0) or 0) * 2 + (p.get("shares", 0) or 0) * 3,
        reverse=True
    )

    for i, post in enumerate(sorted_posts[:count]):
        content = post.get("content", "")
        first_line = content.split("\n")[0] if content else ""

        if i == 0:
            example_type = "hook"
            text = first_line
            why = "High engagement opener"
        elif i == 1:
            example_type = "full-post"
            text = content[:500] + "..." if len(content) > 500 else content
            why = "Representative post structure"
        else:
            example_type = "cta"
            lines = content.split("\n")
            cta_line = ""
            for line in reversed(lines):
                if line.strip() and (line.strip().endswith("?") or "comment" in line.lower() or "share" in line.lower()):
                    cta_line = line.strip()
                    break
            text = cta_line or lines[-1].strip() if lines else ""
            why = "Engagement-driving close"

        examples.append({
            "type": example_type,
            "text": text,
            "why": why,
            "sourcePostId": post.get("id"),
            "engagement": {
                "likes": post.get("likes", 0),
                "comments": post.get("comments", 0),
                "shares": post.get("shares", 0)
            }
        })

    return examples


def extract_voice_contract(founder_profile, founder_posts, canonical_count=3):
    """Transform founder data into compact voice contract."""

    existing_style = founder_profile.get("writingStyle", "") if founder_profile else ""
    existing_themes = founder_profile.get("topThemes", []) if founder_profile else []

    sentence_structure = analyze_sentence_structure(founder_posts)
    vocabulary = analyze_vocabulary(founder_posts, founder_profile)
    rhetoric = analyze_rhetoric(founder_posts, founder_profile)
    length_profile = analyze_length_profile(founder_posts)
    post_type_distribution = analyze_post_type_distribution(founder_posts)
    canonical_examples = select_canonical_examples(founder_posts, canonical_count)

    voice_contract = {
        "version": "1.1",
        "founderId": founder_profile.get("id") if founder_profile else None,
        "founderName": founder_profile.get("name") if founder_profile else None,
        "extractedAt": datetime.now(timezone.utc).isoformat(),

        "voiceRules": {
            "sentenceStructure": sentence_structure,
            "vocabulary": vocabulary,
            "rhetoric": rhetoric
        },

        "lengthProfile": length_profile,
        "postTypeDistribution": post_type_distribution,
        "canonicalExamples": canonical_examples,

        "antiPatterns": {
            "neverUse": [
                "em dashes (--)",
                "It's not X, it's Y",
                "structures of 3 unless natural",
                "Here's the thing:" if "Here's the thing" not in " ".join(vocabulary.get("signaturePhrases", [])) else None
            ]
        },

        "topThemes": existing_themes,

        "existingAnalysis": {
            "writingStyle": existing_style,
            "summaryReport": (founder_profile.get("summaryReport", "")[:500] + "...") if founder_profile and founder_profile.get("summaryReport") else None
        },

        "metadata": {
            "postsAnalyzed": len(founder_posts),
            "confidenceScore": min(0.5 + (len(founder_posts) / 20) * 0.5, 0.95) if founder_posts else 0.3
        }
    }

    voice_contract["antiPatterns"]["neverUse"] = [
        item for item in voice_contract["antiPatterns"]["neverUse"] if item is not None
    ]

    return voice_contract


def create_context_bundle(context_docs, founder_profile, founder_posts, voice_contract, client_id, client_name, folder_name):
    """Create the full context bundle with per-stage subsets."""

    brand = context_docs.get("brand", {}) or {}
    messaging = context_docs.get("messaging", {}) or {}
    audience = context_docs.get("audience", {}) or {}
    strategy = context_docs.get("strategy", {}) or {}
    competitive = context_docs.get("competitive", {}) or {}

    context_bundle = {
        "version": "1.0",
        "generatedAt": datetime.now(timezone.utc).isoformat(),

        "client": {
            "id": client_id,
            "name": client_name,
            "folderName": folder_name
        },

        "fullContext": {
            "brand": brand,
            "messaging": messaging,
            "audience": audience,
            "strategy": strategy,
            "competitive": competitive
        },

        "companyContext": {
            "companyProfile": brand.get("companyProfile", {}),
            "brandVoice": brand.get("brandVoice", {}),
            "positioning": messaging.get("positioning", {}),
            "valuePropositions": messaging.get("valuePropositions", []),
            "keyMessages": messaging.get("keyMessages", []),
            "icpTargets": audience.get("icpTargets", []),
            "personas": audience.get("personas", []),
            "differentiators": strategy.get("differentiators", []),
            "competitiveLandscape": competitive.get("competitiveLandscape", {})
        },

        "founderContext": {
            "profile": {
                "id": founder_profile.get("id") if founder_profile else None,
                "name": founder_profile.get("name") if founder_profile else None,
                "title": founder_profile.get("title") if founder_profile else None,
                "company": founder_profile.get("company") if founder_profile else None,
                "linkedinUrl": founder_profile.get("linkedinUrl") if founder_profile else None,
                "twitterHandle": founder_profile.get("twitterHandle") if founder_profile else None,
                "topThemes": founder_profile.get("topThemes", []) if founder_profile else [],
                "writingStyle": founder_profile.get("writingStyle") if founder_profile else None,
                "summaryReport": founder_profile.get("summaryReport") if founder_profile else None,
                "totalPostsCollected": founder_profile.get("totalPostsCollected", 0) if founder_profile else 0
            },
            "allPosts": [
                {
                    "id": p.get("id"),
                    "platform": p.get("platform"),
                    "content": p.get("content"),
                    "url": p.get("url"),
                    "postedAt": p.get("postedAt"),
                    "likes": p.get("likes", 0),
                    "comments": p.get("comments", 0),
                    "shares": p.get("shares", 0)
                }
                for p in founder_posts
            ],
            "postCount": len(founder_posts)
        },

        "voiceContract": voice_contract,

        "stageContexts": {
            "topicCurator": {
                "companyProfile": brand.get("companyProfile", {}),
                "positioning": messaging.get("positioning", {}),
                "icpTargets": audience.get("icpTargets", []),
                "founderTopThemes": founder_profile.get("topThemes", []) if founder_profile else []
            },
            "templateSelector": {
                "brandVoice": brand.get("brandVoice", {}),
                "personas": audience.get("personas", []),
                "positioning": messaging.get("positioning", {})
            },
            "ghostwriter": {
                "voiceContract": voice_contract,
                "companyContext": {
                    "companyProfile": brand.get("companyProfile", {}),
                    "brandVoice": brand.get("brandVoice", {}),
                    "positioning": messaging.get("positioning", {}),
                    "valuePropositions": messaging.get("valuePropositions", []),
                    "differentiators": strategy.get("differentiators", [])
                },
                "founderPosts": [
                    {
                        "content": p.get("content"),
                        "postedAt": p.get("postedAt"),
                        "likes": p.get("likes", 0),
                        "comments": p.get("comments", 0),
                        "shares": p.get("shares", 0)
                    }
                    for p in founder_posts
                ],
                "founderPostCount": len(founder_posts)
            }
        },

        "metadata": {
            "contextDocsLoaded": sum(1 for v in context_docs.values() if v),
            "founderPostsIncluded": len(founder_posts),
            "voiceContractConfidence": voice_contract.get("metadata", {}).get("confidenceScore", 0)
        }
    }

    return context_bundle


def main():
    parser = argparse.ArgumentParser(
        description='Preload all context for ghostwriting',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('client_id', nargs='?', help='Firebase Client ID (or omit to read from active_client.md)')
    parser.add_argument('founder_id', nargs='?', help='Firebase founder document ID')
    parser.add_argument('--client-name', default=None, help='Client display name')
    parser.add_argument('--folder-name', default=None, help='Local folder name for context files')
    parser.add_argument('--output-dir', default='.', help='Directory for output files')
    parser.add_argument('--founder-posts-limit', type=int, default=50, help='Max founder posts to load')
    parser.add_argument('--canonical-examples', type=int, default=3, help='Number of canonical examples')
    parser.add_argument('--firebase-only', action='store_true', help='Skip local file check')

    args = parser.parse_args()

    # Read from active_client.md if not provided
    if not args.client_id:
        active_client_id, active_name, active_folder, active_founder = get_client_from_active_file()
        if active_client_id:
            args.client_id = active_client_id
            args.client_name = args.client_name or active_name
            args.folder_name = args.folder_name or active_folder
            if not args.founder_id:
                args.founder_id = active_founder
        else:
            print("ERROR: No client_id provided and could not read from active_client.md", file=sys.stderr)
            sys.exit(1)

    if not args.founder_id:
        print("ERROR: founder_id is required", file=sys.stderr)
        sys.exit(1)

    CLIENT_ID = args.client_id
    CLIENT_NAME = args.client_name or args.folder_name or "Client"
    FOLDER_NAME = args.folder_name or args.client_name or args.client_id

    cred_path = find_firebase_credentials()
    if not cred_path:
        print("ERROR: Could not find Firebase credentials file.", file=sys.stderr)
        sys.exit(1)

    print(f"Using credentials: {cred_path}", file=sys.stderr)

    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

    db = firestore.client()

    print(f"\nLoading context for client", file=sys.stderr)
    print(f"Client ID: {CLIENT_ID}", file=sys.stderr)
    print(f"Client Name: {CLIENT_NAME}", file=sys.stderr)
    print(f"Founder ID: {args.founder_id}", file=sys.stderr)
    print("="*60, file=sys.stderr)

    # Load context documents
    print("\n1. Loading context documents...", file=sys.stderr)
    context_docs = {}
    context_sources = {}
    for doc_name in ["brand", "messaging", "audience", "strategy", "competitive"]:
        print(f"   - context/{doc_name}...", file=sys.stderr, end=" ")
        doc_data, source = load_context_document(
            db, doc_name,
            client_id=CLIENT_ID,
            firebase_only=args.firebase_only
        )
        context_docs[doc_name] = doc_data
        context_sources[doc_name] = source
        if doc_data:
            source_type = "LOCAL" if source and source.startswith("local:") else "FIREBASE"
            print(f"OK ({source_type})", file=sys.stderr)
        else:
            print("MISSING", file=sys.stderr)

    # Load founder profile
    print("\n2. Loading founder profile...", file=sys.stderr)
    founder_profile = load_founder_profile(db, CLIENT_ID, args.founder_id)
    if founder_profile:
        print(f"   - Name: {founder_profile.get('name')}", file=sys.stderr)
        print(f"   - Total posts: {founder_profile.get('totalPostsCollected', 0)}", file=sys.stderr)

    # Load founder posts
    print("\n3. Loading founder posts...", file=sys.stderr)
    founder_posts = load_founder_posts(db, CLIENT_ID, args.founder_id, args.founder_posts_limit)
    print(f"   - Loaded: {len(founder_posts)} posts", file=sys.stderr)

    # Extract voice contract
    print("\n4. Extracting voice contract...", file=sys.stderr)
    voice_contract = extract_voice_contract(founder_profile, founder_posts, args.canonical_examples)
    print(f"   - Confidence: {voice_contract['metadata']['confidenceScore']:.2f}", file=sys.stderr)

    # Create context bundle
    print("\n5. Creating context bundle...", file=sys.stderr)
    context_bundle = create_context_bundle(
        context_docs, founder_profile, founder_posts, voice_contract,
        client_id=CLIENT_ID, client_name=CLIENT_NAME, folder_name=FOLDER_NAME
    )

    # Write output files
    os.makedirs(args.output_dir, exist_ok=True)

    print("\n6. Writing output files...", file=sys.stderr)

    context_bundle_path = os.path.join(args.output_dir, "context_bundle.json")
    with open(context_bundle_path, 'w', encoding='utf-8') as f:
        json.dump(context_bundle, f, indent=2, ensure_ascii=False, default=str)
    bundle_size = os.path.getsize(context_bundle_path)
    print(f"   - {context_bundle_path} ({bundle_size / 1024:.1f} KB)", file=sys.stderr)

    voice_contract_path = os.path.join(args.output_dir, "voice_contract.json")
    with open(voice_contract_path, 'w', encoding='utf-8') as f:
        json.dump(voice_contract, f, indent=2, ensure_ascii=False, default=str)
    contract_size = os.path.getsize(voice_contract_path)
    print(f"   - {voice_contract_path} ({contract_size / 1024:.1f} KB)", file=sys.stderr)

    # Print summary
    local_count = sum(1 for s in context_sources.values() if s and s.startswith("local:"))
    firebase_context_count = sum(1 for s in context_sources.values() if s and s.startswith("firebase:"))

    print("\n" + "="*60, file=sys.stderr)
    print("PRELOAD COMPLETE", file=sys.stderr)
    print(f"  - Context docs from local: {local_count}", file=sys.stderr)
    print(f"  - Context docs from Firebase: {firebase_context_count}", file=sys.stderr)
    print(f"  - Founder posts analyzed: {len(founder_posts)}", file=sys.stderr)

    # Output JSON for integration
    print(json.dumps({
        "success": True,
        "client": {
            "id": CLIENT_ID,
            "name": CLIENT_NAME,
            "folderName": FOLDER_NAME
        },
        "outputs": {
            "contextBundle": context_bundle_path,
            "voiceContract": voice_contract_path
        },
        "metadata": {
            "localContextDocs": local_count,
            "firebaseContextDocs": firebase_context_count,
            "contextBundleSizeKB": round(bundle_size / 1024, 1),
            "voiceContractSizeKB": round(contract_size / 1024, 1),
            "founderPostsAnalyzed": len(founder_posts),
            "voiceConfidence": voice_contract['metadata']['confidenceScore']
        },
        "sources": context_sources
    }))


if __name__ == "__main__":
    main()
