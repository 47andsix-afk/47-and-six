try:
    from core.config import is_mock_enabled
except Exception:
    def is_mock_enabled():
        return False

from agents.chef_knowledge_client import query_chef_knowledge_context


def run_recipe(user_message: str) -> str:
    if is_mock_enabled():
        return f"[MOCK] Recipe agent mock reply for: {user_message}"

    context, _ = query_chef_knowledge_context(user_message)
    prompt = f"""
Recipe Agent

Context:
{context}

User Request:
{user_message}
"""
    return prompt
