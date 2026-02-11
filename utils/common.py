# cognigen-ai-service/utils/common.py
import json
import re
import uuid
from typing import List, Dict
from datetime import datetime


def extract_json(text: str) -> dict:
    """
    Safely extract JSON from LLM output.
    Handles:
    - Markdown fences (```json)
    - Noise before/after JSON
    - Large JSON blocks
    - Lists containing a single dict
    - Dangling commas
    """

    raw_text = text

    cleaned = (
        text.replace("```json", "")
            .replace("```", "")
            .replace("`", "")
            .strip()
    )

    # 1) Try loading entire cleaned content
    try:
        result = json.loads(cleaned)

        if isinstance(result, list) and len(result) == 1 and isinstance(result[0], dict):
            return result[0]

        return result

    except Exception:
        pass

    # 2) Extract JSON blocks using regex, largest first
    blocks = re.findall(r"\{[\s\S]*?\}|\[[\s\S]*?\]", cleaned)
    blocks = sorted(blocks, key=len, reverse=True)

    for block in blocks:
        try:
            result = json.loads(block)

            if isinstance(result, list) and len(result) == 1 and isinstance(result[0], dict):
                return result[0]

            return result

        except Exception:
            continue

    # 3) Fix trailing commas
    cleaned2 = re.sub(r",(\s*[}\]])", r"\1", cleaned)
    try:
        result = json.loads(cleaned2)

        if isinstance(result, list) and len(result) == 1 and isinstance(result[0], dict):
            return result[0]

        return result

    except Exception:
        raise ValueError(f"❌ JSON extraction failed.\nRAW OUTPUT:\n{raw_text}")


# ---------------------------------------------------------
# TOPIC NORMALIZATION
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
# LIMIT TOPICS BASED ON DIFFICULTY PRIORITY
# ---------------------------------------------------------
def limit_topics_by_difficulty(topics: List[Dict], exp_level: str) -> List[Dict]:
    priority_map = {
        "beginner": {"easy": 1, "medium": 2, "hard": 3},
        "intermediate": {"medium": 1, "hard": 2, "easy": 3},
        "advanced": {"hard": 1, "medium": 2, "easy": 3}
    }

    prio = priority_map.get(exp_level.lower(), priority_map["beginner"])

    topics = sorted(
        topics,
        key=lambda t: (prio.get(t["difficulty"], 3), t["order"])
    )

    topics = topics[:10]

    for i, t in enumerate(topics, start=1):
        t["order"] = i

    return topics


# ---------------------------------------------------------
# CLEAN CONTENT TEMPLATE (FULLY SAFE VERSION)
# ---------------------------------------------------------
def enforce_content_template(raw: dict, submodule: dict) -> dict:
    """
    Ensures all required fields exist, fixes missing keys,
    and handles cases when raw is list or malformed.
    """

    # If raw is a list → use first dict
    if isinstance(raw, list):
        raw = raw[0] if raw and isinstance(raw[0], dict) else {}

    # If still not dict → reset to empty dict
    if not isinstance(raw, dict):
        raw = {}

    # Ensure LLM output has a valid array
    code_examples = raw.get("code_examples", [])
    if isinstance(code_examples, list):
        for ex in code_examples:
            if "explanation" not in ex:
                ex["explanation"] = "Explanation unavailable."

    # Final normalized output
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