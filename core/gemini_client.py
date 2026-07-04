import json
from typing import Any, Dict, List


class GeminiClient:
    """Thin wrapper with optional runtime dependency on google-generativeai."""

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self._model: Any = None

        if not api_key:
            return

        try:
            import google.generativeai as genai  # type: ignore[import-not-found]
        except Exception:
            return

        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model_name=model_name)

    async def call_functions(self, functions: List[Dict[str, Any]], user_input: str) -> Dict[str, Any]:
        if self._model is None:
            return {"function_calls": []}

        response = self._model.generate_content(
            user_input,
            generation_config={"response_mime_type": "application/json"},
            tools=[{"function_declarations": functions}],
        )

        text = getattr(response, "text", None)
        if not text:
            return {"function_calls": []}
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return {"function_calls": []}

        if isinstance(parsed, dict):
            return parsed
        return {"function_calls": []}
