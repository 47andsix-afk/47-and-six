try:
    from core.config import is_mock_enabled
except Exception:
    def is_mock_enabled():
        return False

from agents.chef_knowledge_client import query_chef_knowledge_context


def run_client_intake(user_message: str) -> str:
    if is_mock_enabled():
        return f"[MOCK] Client intake mock reply for: {user_message}"

    context, _ = query_chef_knowledge_context(user_message)
    prompt = f"""
Client Intake Agent

Context:
{context}

Customer Message:
{user_message}
"""
    return prompt
