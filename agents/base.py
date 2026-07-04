from typing import Any, Dict


class BaseAgent:
    name: str = "base"

    def list_functions(self) -> Dict[str, Dict[str, Any]]:
        """Return a mapping of function_name -> JSON schema (dummy for now)."""
        return {}

    async def call_function(self, function_name: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute a named function with kwargs (dummy implementation)."""
        return {
            "agent": self.name,
            "function": function_name,
            "args": kwargs,
            "result": "dummy-result",
        }
