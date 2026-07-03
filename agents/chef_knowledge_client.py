from chef_knowledge.indexer import query_chef_knowledge

DB_QUERY_COUNT = 5

def query_chef_knowledge_context(prompt: str, n_results: int = DB_QUERY_COUNT):
    """Return flattened context string and raw results for a prompt."""
    try:
        results = query_chef_knowledge(prompt, n_results=n_results)
        docs = results.get("documents", [[]])[0]
        context = "\n\n".join(d for d in docs if d)
        return context, results
    except Exception:
        return "", {"documents": []}
