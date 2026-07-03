import asyncio

try:
    from core.config import is_mock_enabled
except Exception:
    def is_mock_enabled():
        return False

class MemoryAgent:
    def __init__(self, retrieve_func):
        self.retrieve_func = retrieve_func

    async def retrieve(self, inquiry: str) -> str:
        if is_mock_enabled():
            return "No specific local parameters found. [MOCK]"
        if asyncio.iscoroutinefunction(self.retrieve_func):
            try:
                return await asyncio.wait_for(self.retrieve_func(inquiry), timeout=3.0)
            except asyncio.TimeoutError:
                return "No specific local parameters found."
        # Sync retrieval fallback
        return await asyncio.to_thread(self.retrieve_func, inquiry)
