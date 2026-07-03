try:
    from core.config import is_mock_enabled
except Exception:
    def is_mock_enabled():
        return False

from agents.chef_knowledge_client import query_chef_knowledge_context


def run_menu_costing(user_message: str) -> str:
    if is_mock_enabled():
        return f"[MOCK] Menu costing response for: {user_message}"

    context, _ = query_chef_knowledge_context(user_message)
    prompt = f"""
Menu Costing Agent

Context:
{context}

User Message:
{user_message}
"""
    # For now, return the composed prompt (replace with Gemini call later)
    return prompt
