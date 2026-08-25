from __future__ import annotations

import json
import os
import urllib.request
from typing import Any


class OllamaRuntime:
    """Open-source local LLM runtime using Ollama's HTTP API."""

    def __init__(self, endpoint: str | None = None, model: str | None = None) -> None:
        self.endpoint = (endpoint or os.getenv("OLLAMA_ENDPOINT", "http://127.0.0.1:11434")).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

    def generate(self, prompt: str, parameters: dict[str, Any] | None = None) -> str:
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        if parameters:
            payload["options"] = parameters
        request = urllib.request.Request(f"{self.endpoint}/api/generate", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(request, timeout=300) as response:
            result = json.loads(response.read().decode())
        text = result.get("response")
        if not text:
            raise RuntimeError("Ollama returned no response text")
        return str(text)
