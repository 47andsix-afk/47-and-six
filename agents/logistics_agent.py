import asyncio
import json

try:
    from core.config import is_mock_enabled
except Exception:
    def is_mock_enabled():
        return False

class LogisticsAgent:
    def __init__(self, generate_func):
        self.generate = generate_func

    async def run(self, inquiry: str, local_context: str) -> dict:
        if is_mock_enabled():
            return {
                "radius_ok": "mock",
                "staffing": ["mock_staff"],
                "equipment": ["mock_equipment"],
                "travel_cost": "0.00",
            }
        prompt = f"""
RONIN-03 // Logistics & Deployment

You are RONIN-03, responsible for routing, staffing deployment, and equipment logistics.
Return STRICT JSON with keys:
- radius_ok
- staffing
- equipment
- travel_cost

Local Operational Rule: {local_context}
User Inquiry: {inquiry}
"""
        try:
            raw = await asyncio.wait_for(self.generate(prompt), timeout=4.0)
        except asyncio.TimeoutError:
            return {
                "radius_ok": "unknown",
                "staffing": "",
                "equipment": "",
                "travel_cost": "timeout",
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
            "radius_ok": raw,
            "staffing": "",
            "equipment": "",
            "travel_cost": "",
            "parse_error": "parse_error",
        }
