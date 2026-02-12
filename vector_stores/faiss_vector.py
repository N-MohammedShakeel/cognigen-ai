import faiss
import numpy as np
import json
import os

# Paths to index + metadata
INDEX_PATH = "vector_stores/python.index"
META_PATH = "vector_stores/python_metadata.json"

# Load index
if os.path.exists(INDEX_PATH):
    index = faiss.read_index(INDEX_PATH)
else:
    index = None

# Load metadata that stores titles, urls, descriptions
if os.path.exists(META_PATH):
    with open(META_PATH, "r") as f:
        metadata = json.load(f)
else:
    metadata = []


def embed(text: str) -> np.ndarray:
    """TEMP: dummy embedding (replace with your mxbai embedding code)."""
    # TODO: integrate mxbai-embed-large-v1
    vec = np.random.rand(1024).astype("float32")
    return vec / np.linalg.norm(vec)


def vector_search(query: str, k: int = 5):
    """Search in FAISS index and return top resources."""
    if index is None or len(metadata) == 0:
        return []

    q_vec = embed(query)
    q_vec = np.expand_dims(q_vec, axis=0)

    scores, indices = index.search(q_vec, k)
    results = []

    for i in indices[0]:
        if i < 0 or i >= len(metadata):
            continue
        item = metadata[i]
        results.append({
            "title": item["title"],
            "url": item["url"],
            "description": item["description"]
        })

    return results
