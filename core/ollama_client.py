import requests
from typing import Any


def ollama_generate(prompt: str, host: str = "http://127.0.0.1:11434", model: str = "llama3", timeout: int = 60) -> str:
    url = f"{host.rstrip('/')}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
    }

    try:
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict):
            return str(data.get("response", ""))
        return str(data)
    except requests.RequestException as exc:
        return f"Ollama generation failed: {str(exc)}"
