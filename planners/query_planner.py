import ollama
from utils.common import extract_json

def generate_search_queries(submodule_title: str, summary: str, course: str):
    system = """
Return only JSON array:
[
  { "site": "string", "query": "string" }
]
"""

    user = f"""
Generate 2-4 precise Google search queries to collect 
high-quality educational content (NO blogs, NO random low-quality sites).

Only allowed sites:
- w3schools.com
- geeksforgeeks.org
- tutorialspoint.com
- official docs

Submodule: {submodule_title}
Summary: {summary}
Course: {course}
"""

    raw = ollama.generate(
        model="gemma2:2b",
        prompt=system + user
    )["response"]

    return extract_json(raw)
