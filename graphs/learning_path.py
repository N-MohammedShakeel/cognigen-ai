# graphs/learning_path.py

from typing import TypedDict, List, Dict
import uuid
import ollama
from datetime import datetime
from langgraph.graph import StateGraph, END

from utils.common import (
    extract_json,
    normalize_topic_fields,
    limit_topics_by_difficulty
)


# -------------------------------------------------------
# STATE
# -------------------------------------------------------
class LPState(TypedDict, total=False):
    user_id: str
    course_name: str
    experience_level: str
    custom_topics: List[str]
    goal: str
    preferred_learning_style: str
    time_availability: dict

    student_profile: dict
    auto_topics: list
    llm_topics: dict
    learning_path: dict


# -------------------------------------------------------
def input_node(state: LPState):
    return state


def profile_node(state: LPState):
    state["student_profile"] = {
        "user_id": state.get("user_id"),
        "course_name": state.get("course_name"),
        "experience_level": state.get("experience_level"),
        "custom_topics": state.get("custom_topics", []),
        "goal": state.get("goal"),
        "preferred_learning_style": state.get("preferred_learning_style"),
        "time_availability": state.get("time_availability"),
    }
    return state


# -------------------------------------------------------
def auto_topic_gen_node(state: LPState):
    sp = state["student_profile"]

    # If user provides custom topics, skip auto generation
    if sp["custom_topics"]:
        return state

    system = """
Return only JSON:
{
  "topics": [
    { "id": "string", "name": "string", "order": number, "submodules": [] }
  ]
}
"""

    user = f"""
Generate foundational topics for course: {sp['course_name']}
Experience: {sp['experience_level']}
Goal: {sp['goal']}
"""

    raw = ollama.generate(model="gemma3:1b", prompt=system + user)["response"]

    parsed = extract_json(raw)
    state["auto_topics"] = parsed.get("topics", [])
    return state


# -------------------------------------------------------
def topic_generation_node(state: LPState):
    sp = state["student_profile"]

    # If user provided custom topics, enforce EXACTLY those topics
    if sp["custom_topics"]:
        topics = []
        for i, name in enumerate(sp["custom_topics"], start=1):
            topics.append({
                "id": str(i),
                "name": name,
                "order": i,
                "submodules": [],
            })

        # Normalize + difficulty + time
        topics = normalize_topic_fields(topics, sp["experience_level"])
        topics = limit_topics_by_difficulty(topics, sp["experience_level"])

        state["llm_topics"] = {
            "title": f"{sp['course_name']} - Custom Learning Path",
            "description": "Learning path generated only from user-provided custom topics.",
            "topics": topics,
        }
        return state

    # (Otherwise) GENERATE NORMAL TOPICS USING LLM
    base_topics = [t["name"] for t in state.get("auto_topics", [])]

    system = """
Return only JSON:
{
  "title": "string",
  "description": "string",
  "topics": [
    { "id": "string", "name": "string", "order": number, "submodules": [] }
  ]
}
"""

    user = f"""
Generate a structured learning path for course: {sp['course_name']}
Experience level: {sp['experience_level']}
Core topics: {base_topics}
"""

    raw = ollama.generate(model="gemma3:1b", prompt=system + user)["response"]
    parsed = extract_json(raw)

    topics = normalize_topic_fields(parsed.get("topics", []), sp["experience_level"])
    topics = limit_topics_by_difficulty(topics, sp["experience_level"])

    state["llm_topics"] = {
        "title": parsed.get("title", f"{sp['course_name']} Learning Path"),
        "description": parsed.get("description", ""),
        "topics": topics,
    }

    return state



# -------------------------------------------------------
def submodule_gen_node(state: LPState):
    sp = state["student_profile"]
    topics = state["llm_topics"]["topics"]

    for topic in topics:
        system = """
Return only JSON:
{
  "submodules": [
    { "title": "string", "summary": "string" }
  ]
}
"""
        user = f"""
Generate up to 4 high-quality submodules for topic: {topic['name']}
Course: {sp['course_name']}
Experience level: {sp['experience_level']}
"""

        raw = ollama.generate(model="gemma3:1b", prompt=system + user)["response"]
        parsed = extract_json(raw)

        submods = parsed.get("submodules", [])[:2]

        if not submods:
            submods = [{"title": topic["name"], "summary": ""}]

        enriched = []
        for i, sm in enumerate(submods, start=1):
            enriched.append({
                "id": str(uuid.uuid4()),
                "title": sm["title"],
                "summary": sm.get("summary", ""),
                "order": i,
                "createdAt": datetime.utcnow().isoformat(),
                "updatedAt": datetime.utcnow().isoformat(),
                "completed": False,
                "content": {}
            })

        topic["submodules"] = enriched

    return state


# -------------------------------------------------------
def learning_path_builder_node(state: LPState):
    sp = state["student_profile"]
    llm = state["llm_topics"]

    topics = llm["topics"]
    total_submods = sum(len(t["submodules"]) for t in topics)

    state["learning_path"] = {
        "id": str(uuid.uuid4()),
        "title": llm["title"],
        "description": llm["description"],
        "course_name": sp["course_name"],
        "goal": sp["goal"],
        "student_profile": sp,
        "topics": topics,
        "status": "draft",
        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": datetime.utcnow().isoformat(),
        "progress": {
            "topics_completed": 0,
            "total_topics": len(topics),
            "submodules_completed": 0,
            "total_submodules": total_submods,
            "percentage": 0,
        }
    }
    return state


# -------------------------------------------------------
# BUILD GRAPH
# -------------------------------------------------------
builder = StateGraph(LPState)

builder.add_node("input", input_node)
builder.add_node("profile", profile_node)
builder.add_node("auto_topics", auto_topic_gen_node)
builder.add_node("topic_gen", topic_generation_node)
builder.add_node("submodule_gen", submodule_gen_node)
builder.add_node("builder", learning_path_builder_node)

builder.set_entry_point("input")

builder.add_edge("input", "profile")
builder.add_edge("profile", "auto_topics")
builder.add_edge("auto_topics", "topic_gen")
builder.add_edge("topic_gen", "submodule_gen")
builder.add_edge("submodule_gen", "builder")
builder.add_edge("builder", END)

learning_path_graph = builder.compile()
