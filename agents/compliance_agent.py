import asyncio
import json

try:
    from core.config import is_mock_enabled
except Exception:
    def is_mock_enabled():
        return False

class ComplianceAgent:
    def __init__(self, generate_func):
        self.generate = generate_func

    async def run(self, inquiry: str, local_context: str) -> dict:
        if is_mock_enabled():
            return {
                "dietary": "none",
                "safety": "none",
                "constraints": "none",
                "red_flags": "none",
            }
        prompt = f"""
RONIN-06 // Compliance & Constraints

You are RONIN-06, ensuring dietary, safety, and scheduling compliance.
Return STRICT JSON with keys:
- dietary
- safety
- constraints
- red_flags

Local Operational Rule: {local_context}
User Inquiry: {inquiry}
"""
        try:
            raw = await asyncio.wait_for(self.generate(prompt), timeout=4.0)
        except asyncio.TimeoutError:
            return {
                "dietary": "",
                "safety": "",
                "constraints": "",
                "red_flags": "timeout",
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
            "dietary": raw,
            "safety": "",
            "constraints": "",
            "red_flags": "parse_error",
            "parse_error": "parse_error",
        }
