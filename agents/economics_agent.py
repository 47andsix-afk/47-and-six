import asyncio
import json

try:
    from core.config import is_mock_enabled
except Exception:
    def is_mock_enabled():
        return False

class EconomicsAgent:
    def __init__(self, generate_func):
        self.generate = generate_func

    async def run(self, inquiry: str, local_context: str) -> dict:
        if is_mock_enabled():
            return {
                "cost_summary": "mock",
                "surcharge_band": "mock",
                "yield_notes": "Mock economics response (development)",
                "risk_flags": "low",
            }
        prompt = f"""
RONIN-02 // Economics Engine

You are RONIN-02, responsible for cost control, purchasing logic, and 6-minute cycle math.
Return STRICT JSON with keys:
- cost_summary
- surcharge_band
- yield_notes
- risk_flags

Local Operational Rule: {local_context}
User Inquiry: {inquiry}
"""
        try:
            raw = await asyncio.wait_for(self.generate(prompt), timeout=4.0)
        except asyncio.TimeoutError:
            return {
                "cost_summary": "timeout",
                "surcharge_band": "",
                "yield_notes": "",
                "risk_flags": "timeout",
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
            "cost_summary": raw,
            "surcharge_band": "",
            "yield_notes": "",
            "risk_flags": "parse_error",
        }
