# -------------------------------------------------------
# quiz_gen.py — FINAL STABLE VERSION (QWEN OPTIMIZED)
# -------------------------------------------------------

from typing import TypedDict, List, Dict
from datetime import datetime
import ollama

from langgraph.graph import StateGraph, END
from utils.common import extract_json


# -------------------------------------------------------
# STATE
# -------------------------------------------------------
class QuizState(TypedDict, total=False):
    submodule_id: str
    submodule_title: str
    cells: List[Dict]
    extracted_text: str
    quiz: List[Dict]


# -------------------------------------------------------
# HELPERS
# -------------------------------------------------------
def extract_learning_text(cells: List[Dict]) -> str:
    chunks = []
    for c in cells:
        if c.get("type") == "markdown":
            chunks.append(c.get("content", ""))
        elif c.get("type") == "code":
            chunks.append("# Code Example\n" + c.get("content", ""))
    return "\n\n".join(chunks)


def enforce_quality(questions: List[Dict]) -> List[Dict]:
    labels = ["A.", "B.", "C.", "D."]
    cleaned = []

    for q in questions[:5]:

        opts = q.get("options", [])
        new_opts = []

        for i, o in enumerate(opts[:4]):
            if not isinstance(o, str):
                continue
            text = o.split(". ", 1)[-1] if ". " in o[:4] else o
            new_opts.append(f"{labels[i]} {text}")

        ans = str(q.get("answer", "A")).strip().upper()
        if ans not in ["A", "B", "C", "D"]:
            ans = "A"

        cleaned.append({
            "question": q.get("question", "").strip(),
            "options": new_opts,
            "answer": ans,
            "difficulty": q.get("difficulty", "easy")
        })

    return cleaned


# -------------------------------------------------------
# QUIZ GENERATION
# -------------------------------------------------------
def generate_quiz(text: str):

    system = """
Return ONLY valid JSON.
No markdown.
No explanations.
No extra text.

FORMAT:

{
  "quiz": [
    { "question": "...", "options": ["A. ...","B. ...","C. ...","D. ..."], "answer": "A", "difficulty": "easy" }
  ]
}

Rules:
- EXACTLY 5 questions.
- 2 easy, 2 medium, 1 hard.
- Exactly 4 options.
- Answer must be A/B/C/D.
"""

    user = f"""
Generate quiz based only on this text:

{text}
"""

    raw = ollama.generate(
        model="qwen2.5:3b",
        prompt=system + "\n" + user,
        options={"temperature": 0.2}
    )["response"]

    parsed = extract_json(raw)
    return parsed.get("quiz", [])


# -------------------------------------------------------
# NODES
# -------------------------------------------------------
def input_node(state: QuizState):
    return state


def extract_text_node(state: QuizState):
    state["extracted_text"] = extract_learning_text(state["cells"])
    return state


def quiz_gen_node(state: QuizState):

    questions = generate_quiz(state["extracted_text"])
    state["quiz"] = enforce_quality(questions)

    return state


def finalize_node(state: QuizState):
    return {
        "submodule_id": state["submodule_id"],
        "quiz": state["quiz"],
        "generatedAt": datetime.utcnow().isoformat()
    }


# -------------------------------------------------------
# GRAPH
# -------------------------------------------------------
builder = StateGraph(QuizState)

builder.add_node("input", input_node)
builder.add_node("extract", extract_text_node)
builder.add_node("quiz", quiz_gen_node)
builder.add_node("final", finalize_node)

builder.set_entry_point("input")
builder.add_edge("input", "extract")
builder.add_edge("extract", "quiz")
builder.add_edge("quiz", "final")
builder.add_edge("final", END)

quiz_graph = builder.compile()
