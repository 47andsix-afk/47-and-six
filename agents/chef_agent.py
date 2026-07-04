from typing import Any, Dict, List

from .base import BaseAgent


class ChefAgent(BaseAgent):
    name = "chef_agent"

    def list_functions(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "analyze_recipe",
                "description": "Analyze a recipe and its ingredients.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "recipe": {"type": "string"},
                        "ingredients": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["recipe"],
                },
            },
            {
                "name": "convert_units",
                "description": "Convert ingredient units.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ingredient": {"type": "string"},
                        "quantity": {"type": "number"},
                        "from_unit": {"type": "string"},
                        "to_unit": {"type": "string"},
                    },
                    "required": ["ingredient", "quantity", "from_unit", "to_unit"],
                },
            },
            {
                "name": "suggest_improvements",
                "description": "Suggest improvements for a recipe.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "recipe": {"type": "string"},
                    },
                    "required": ["recipe"],
                },
            },
            {
                "name": "pairings",
                "description": "Suggest flavor pairings for a dish.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dish": {"type": "string"},
                    },
                    "required": ["dish"],
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
