import operator
import json
from typing import TypedDict, List, Dict, Annotated
from datetime import datetime
import ollama

from langgraph.graph import StateGraph, END

from utils.common import safe_parse_llm_json
from vector_stores.faiss_vector import vector_search
from integrations.youtube_fetcher import fetch_youtube_videos
from integrations.duckduckgo_search import duckduckgo_search


# -------------------------------------------------------
# STATE
# -------------------------------------------------------
class ContentState(TypedDict):
    topic_id: str
    topic_name: str
    course_name: str
    experience_level: str

    topic_content: Annotated[List[Dict], operator.add]

    submodules: List[Dict]
    current_submodule: Dict
    vector_results: List[Dict]


# -------------------------------------------------------
# RESOURCE RESOLUTION (MULTI SOURCE)
# -------------------------------------------------------
def get_resource_url(title: str, vector_results: List[Dict], max_total: int = 5):

    resources = []
    seen_urls = set()

    def add_resource(title_val, url_val, source_val):
        if (
            isinstance(url_val, str)
            and url_val.startswith("http")
            and url_val not in seen_urls
            and len(resources) < max_total
        ):
            resources.append({
                "title": title_val,
                "url": url_val,
                "source": source_val
            })
            seen_urls.add(url_val)

    # 1️⃣ Local FAISS
    for r in vector_results:
        if len(resources) >= max_total - 2:
            break
        add_resource(
            r.get("title", title),
            r.get("url"),
            "local"
        )

    # 2️⃣ DuckDuckGo
    try:
        ddg = duckduckgo_search(f"{title} tutorial", max_results=3)
        for item in ddg:
            if len(resources) >= max_total:
                break
            add_resource(
                item.get("title"),
                item.get("href"),
                "web"
            )
    except:
        pass

    # 3️⃣ YouTube
    try:
        yt = fetch_youtube_videos(f"{title} explained", max_results=3)
        for item in yt:
            if len(resources) >= max_total:
                break
            add_resource(
                item.get("title"),
                item.get("url"),
                "youtube"
            )
    except:
        pass

    return resources


# -------------------------------------------------------
# GRAPH NODES
# -------------------------------------------------------

def input_node(state: ContentState):
    return {"topic_content": []}


def pick_submodule_node(state: ContentState):
    subs = state.get("submodules", [])
    if not subs:
        return {"current_submodule": None}
    return {"current_submodule": subs[0]}


def vector_search_node(state: ContentState):
    sm = state.get("current_submodule")
    if not sm:
        return {}

    query = f"{sm['title']} {sm.get('summary','')}"
    results = vector_search(query, k=3)

    return {"vector_results": results}


# -------------------------------------------------------
# CONTENT GENERATION NODE (JSON SAFE + RETRY)
# -------------------------------------------------------
def content_generation_node(state: ContentState):

    sm = state.get("current_submodule")
    if not sm:
        return {}

    system_prompt = """
You MUST return ONLY valid JSON.

STRICT FORMAT:
{
  "markdown": "Full learning content in markdown format."
}

Rules:
- Output must start with { and end with }
- No text before or after JSON
- No markdown fences outside JSON
- No null values
- No trailing commas
- Include Python example inside triple backticks
"""

    user_prompt = f"""
Generate structured learning content.

Title: {sm["title"]}
Summary: {sm.get("summary","")}
Course: {state["course_name"]}
Experience Level: {state["experience_level"]}

Requirements:
- Use headings
- Use bullet points
- Explain clearly
- Include at least one Python example
- Keep everything inside markdown
"""

    parsed = {}

    # 🔁 Retry mechanism (2 attempts max)
    for attempt in range(2):
        response = ollama.chat(
            model="qwen2.5:3b",
            format="json", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            options={"temperature": 0.1}
        )

        raw = response["message"]["content"]

        # Try strict JSON first
        try:
            parsed = json.loads(raw)
        except:
            try:
                parsed = safe_parse_llm_json(raw)
            except:
                parsed = {}

        if isinstance(parsed, dict) and parsed.get("markdown"):
            break  

    markdown = parsed.get("markdown", "")
    if not isinstance(markdown, str) or not markdown.strip():
        markdown = f"# {sm['title']}\n\nContent generation failed. Please regenerate."

    # -------------------------------------------------------
    # RESOURCES
    # -------------------------------------------------------
    urls = get_resource_url(
        sm["title"],
        state.get("vector_results", [])
    )

    # -------------------------------------------------------
    # BUILD CELLS
    # -------------------------------------------------------
    cells = [
        {
            "type": "markdown",
            "content": markdown
        }
    ]

    if urls:
        cells.append({
            "type": "resource",
            "content": urls
        })

    content_obj = {
        "id": sm.get("id"),
        "title": sm.get("title"),
        "summary": sm.get("summary", ""),
        "cells": cells,
        "miniQuiz": [],
        "contentVersion": 2,
        "generatedAt": datetime.utcnow().isoformat()
    }

    return {"topic_content": [content_obj]}


# -------------------------------------------------------
# POP SUBMODULE
# -------------------------------------------------------
def pop_submodule_node(state: ContentState):
    subs = state.get("submodules", [])
    return {"submodules": subs[1:]} if subs else {"submodules": []}


def should_continue(state: ContentState):
    if state.get("submodules"):
        return "pick_submodule"
    return END


# -------------------------------------------------------
# BUILD GRAPH
# -------------------------------------------------------
builder = StateGraph(ContentState)

builder.add_node("input", input_node)
builder.add_node("pick_submodule", pick_submodule_node)
builder.add_node("vector_search", vector_search_node)
builder.add_node("generate", content_generation_node)
builder.add_node("pop_submodule", pop_submodule_node)

builder.set_entry_point("input")

builder.add_edge("input", "pick_submodule")
builder.add_edge("pick_submodule", "vector_search")
builder.add_edge("vector_search", "generate")
builder.add_edge("generate", "pop_submodule")

builder.add_conditional_edges("pop_submodule", should_continue)

content_graph = builder.compile()
