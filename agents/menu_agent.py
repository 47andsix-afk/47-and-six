from typing import Any, Dict, List

from .base import BaseAgent


class MenuAgent(BaseAgent):
    name = "menu_agent"

    def list_functions(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "price_menu",
                "description": "Price menu dishes.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dishes": {
                            "type": "array",
                            "items": {"type": "object"},
                        },
                    },
                    "required": ["dishes"],
                },
            },
            {
                "name": "menu_engineering",
                "description": "Perform menu engineering analysis.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "menu": {
                            "type": "array",
                            "items": {"type": "object"},
                        },
                    },
                    "required": ["menu"],
                },
            },
            {
                "name": "profit_projection",
                "description": "Project menu profit.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "menu": {
                            "type": "array",
                            "items": {"type": "object"},
                        },
                        "costs": {"type": "object"},
                    },
                    "required": ["menu", "costs"],
                },
            },
        ]

    async def call_function(self, function_name: str, **kwargs: Any) -> Dict[str, Any]:
        return {
            "agent": self.name,
            "function": function_name,
            "args": kwargs,
            "result": f"dummy-{function_name}-result",
        }
