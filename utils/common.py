
import json
import re
import uuid
from typing import List, Dict
from datetime import datetime


# ---------------------------------------------------------
# SAFE JSON EXTRACTION (Production Stable)
# ---------------------------------------------------------
def extract_json(text: str):
    """
    Extract JSON safely from LLM output.

    Handles:
    - Markdown fences
    - Embedded ```python blocks
    - Noise before/after JSON
    - Trailing commas
    - Array wrapping
    """

    raw_text = text.strip()

    # Remove markdown fences only (do NOT remove backticks inside content)
    cleaned = raw_text.replace("```json", "").replace("```", "").strip()

    # -------------------------------
    # 1️⃣ Direct JSON parse (fast path)
    # -------------------------------
    try:
        parsed = json.loads(cleaned)
        return parsed
    except:
        pass

    # -------------------------------
    # 2️⃣ Extract biggest JSON block
    # -------------------------------
    blocks = re.findall(r"\{[\s\S]*\}|\[[\s\S]*\]", cleaned)

    if blocks:
        largest = max(blocks, key=len)

        # Remove trailing commas
        largest = re.sub(r",(\s*[}\]])", r"\1", largest)

        try:
            parsed = json.loads(largest)
            return parsed
        except:
            pass

    # -------------------------------
    # 3️⃣ Final fallback
    # -------------------------------
    raise ValueError(
        f"❌ JSON extraction failed.\nRAW OUTPUT:\n{raw_text}"
    )


# ---------------------------------------------------------
# LLM SAFE PARSER (USE THIS EVERYWHERE)
# ---------------------------------------------------------
def safe_parse_llm_json(raw: str):
    """
    Production-safe LLM JSON parser.
    Tries direct json.loads first.
    Falls back to extract_json.
    """

    try:
        return json.loads(raw)
    except:
        return extract_json(raw)


# ---------------------------------------------------------
# TOPIC NORMALIZATION (old workflow – unchanged)
# ---------------------------------------------------------
def normalize_topic_fields(topics: List[Dict], exp_level: str) -> List[Dict]:
    diff_map = {
        "beginner": ("easy", 2),
        "intermediate": ("medium", 3),
        "advanced": ("hard", 4)
    }

    diff, base_hours = diff_map.get(exp_level.lower(), ("easy", 2))

    for t in topics:
        t["difficulty"] = diff
        t["estimated_time_hours"] = base_hours + (t.get("order", 1) // 5)
        t["completed"] = False
        t["lastGeneratedAt"] = datetime.utcnow().isoformat()

    return topics


# ---------------------------------------------------------
# LIMIT TOPICS
# ---------------------------------------------------------
def limit_topics_by_difficulty(topics: List[Dict], exp_level: str) -> List[Dict]:
    priority_map = {
        "beginner": {"easy": 1, "medium": 2, "hard": 3},
        "intermediate": {"medium": 1, "hard": 2, "easy": 3},
        "advanced": {"hard": 1, "medium": 2, "easy": 3}
    }

    prio = priority_map.get(exp_level.lower(), priority_map["beginner"])

    sorted_topics = sorted(
        topics,
        key=lambda t: (prio.get(t["difficulty"], 3), t["order"])
    )[:10]

    for i, t in enumerate(sorted_topics, start=1):
        t["order"] = i

    return sorted_topics


# ---------------------------------------------------------
# OLD TEMPLATE NORMALIZER (keep for backward compatibility)
# ---------------------------------------------------------
def enforce_content_template(raw: dict, submodule: dict) -> dict:
    """
    Older version content format — retained for backward compatibility.
    New system uses "cells" so this is rarely used now.
    """

    if isinstance(raw, list):
        raw = raw[0] if raw and isinstance(raw[0], dict) else {}
    if not isinstance(raw, dict):
        raw = {}

    code_examples = raw.get("code_examples", [])
    if isinstance(code_examples, list):
        for ex in code_examples:
            if "explanation" not in ex:
                ex["explanation"] = "Explanation unavailable."

    return {
        "submodule_id": submodule.get("id", str(uuid.uuid4())),
        "title": raw.get("title", submodule["title"]),
        "summary": raw.get("summary", submodule.get("summary", "")),

        "content": {
            "explanation": raw.get("explanation", "No explanation provided."),
            "code_examples": code_examples,
            "real_world_examples": raw.get("real_world_examples", []),
            "step_by_step": raw.get("step_by_step", []),
            "mini_quiz": raw.get("mini_quiz", []),
            "project_suggestion": raw.get("project_suggestion", "No project suggested.")
        },

        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": datetime.utcnow().isoformat(),
        "lastGeneratedAt": datetime.utcnow().isoformat(),
    }
