from typing import Any, Dict

from .base import BaseAgent
from core.ollama_client import ollama_generate


class OllamaAgent(BaseAgent):
    name = "ollama"

    def __init__(self, host: str = "http://127.0.0.1:11434", model: str = "llama3") -> None:
        self.host = host
        self.model = model

    def list_functions(self) -> Dict[str, Dict[str, Any]]:
        return {
            "generate": {
                "description": "Generate text using an Ollama model",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string"},
                    },
                    "required": ["prompt"],
                },
            }
        }

    async def call_function(self, function_name: str, **kwargs: Any) -> Dict[str, Any]:
        if function_name != "generate":
            return {"error": "function not found"}

        prompt = kwargs.get("prompt", "")
        reply = ollama_generate(prompt, host=self.host, model=self.model)
        return {"response": reply}
