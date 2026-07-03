import asyncio
import json

try:
    from core.config import is_mock_enabled
except Exception:
    def is_mock_enabled():
        return False

class OpsAgent:
    def __init__(self, generate_func):
        self.generate = generate_func

    async def run(self, inquiry: str, local_context: str) -> dict:
        if is_mock_enabled():
            return {
                "feasibility": "mock",
                "menu_classes": ["mock_item"],
                "scaling_notes": "Mock ops response (development mode)",
            }
        prompt = f"""
RONIN-01 // Culinary Operations

You are RONIN-01, an expert in menu engineering, scaling, and kitchen production.
Apply local operational rules and return a STRICT JSON object with these keys:
- feasibility
- menu_classes
- scaling_notes

Local Operational Rule: {local_context}
User Inquiry: {inquiry}
"""
        try:
            raw = await asyncio.wait_for(self.generate(prompt), timeout=4.0)
        except asyncio.TimeoutError:
            return {
                "feasibility": "timeout",
                "menu_classes": "",
                "scaling_notes": "RONIN ops timeout — fallback engaged.",
                "parse_error": "timeout",
            }
        return self._parse(raw)

    def _parse(self, raw: str) -> dict:
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass
        return {
            "feasibility": raw,
            "menu_classes": "",
            "scaling_notes": "",
            "parse_error": "parse_error",
        }
