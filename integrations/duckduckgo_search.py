from duckduckgo_search import DDGS

def duckduckgo_search(query: str, max_results: int = 1):
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append(r)
    return results
