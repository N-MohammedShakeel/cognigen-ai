# graphs/content_gen.py
from typing import TypedDict, List, Dict
import ollama
from datetime import datetime
from langgraph.graph import StateGraph, END
from utils.common import extract_json, enforce_content_template


class ContentState(TypedDict, total=False):
    topic_id: str
    topic_name: str
    course_name: str
    experience_level: str
    submodules: List[Dict]

    current_index: int
    generated_contents: List[Dict]
    topic_content: List[Dict]


def is_content_valid(raw: Dict) -> bool:
    """Ensure JSON has MINIMAL required fields."""
    if not isinstance(raw, dict):
        return False

    required = [
        "title", "summary", "explanation",
        "code_examples", "real_world_examples",
        "step_by_step", "mini_quiz",
        "project_suggestion"
    ]

    for k in required:
        if k not in raw:
            return False

    # Title or explanation being empty = invalid
    if len(raw.get("explanation", "")) < 50:
        return False

    return True


def input_node(state: ContentState):
    state["generated_contents"] = []
    state["current_index"] = 0
    return state


def loop_decision_node(state: ContentState):
    idx = state["current_index"]
    if idx >= len(state["submodules"]):
        return {"next": "output"}
    return {"next": "content_gen"}


def content_gen_node(state: ContentState):
    idx = state["current_index"]
    sub = state["submodules"][idx]

    system = """
Return ONLY valid JSON:
{
  "title": "string",
  "summary": "string",
  "explanation": "string (min 120 words)",
  "code_examples": [
    { "title":"string", "code":"string", "explanation":"string" }
  ],
  "real_world_examples": ["string"],
  "step_by_step": ["string"],
  "mini_quiz": [
    { "question":"string", "options":["A","B","C","D"], "answer":"A" }
  ],
  "project_suggestion": "string"
}
NO markdown. NO comments. JSON only.
"""

    user = f"""
Generate detailed educational content for:
Submodule: {sub['title']}
Topic: {state['topic_name']}
Course: {state['course_name']}
Experience Level: {state['experience_level']}

JSON STRUCTURE MUST BE EXACT.
"""

    # --------------------------
    # MULTI-PASS GENERATION
    # --------------------------
    attempts = 0
    parsed = {}

    while attempts < 3:
        raw = ollama.generate(model="gemma3:1b", prompt=system + user)["response"]

        try:
            parsed = extract_json(raw)
        except:
            attempts += 1
            continue

        if is_content_valid(parsed):
            break

        attempts += 1

    # Last attempt fallback
    cleaned = enforce_content_template(parsed, sub)

    state["generated_contents"].append(cleaned)
    state["current_index"] += 1

    return state


def output_node(state: ContentState):
    state["topic_content"] = state["generated_contents"]
    return state


# -------------------------------------------------------
# BUILD GRAPH
# -------------------------------------------------------
builder = StateGraph(ContentState)

builder.add_node("input", input_node)
builder.add_node("loop_decision", loop_decision_node)
builder.add_node("content_gen", content_gen_node)
builder.add_node("output", output_node)

builder.set_entry_point("input")

builder.add_edge("input", "loop_decision")

builder.add_conditional_edges(
    "loop_decision",
    lambda s: s["next"],
    {"content_gen": "content_gen", "output": "output"}
)

builder.add_edge("content_gen", "loop_decision")
builder.add_edge("output", END)

content_graph = builder.compile()
