from __future__ import annotations

import json
import os
import urllib.request
from typing import Any

from .huggingface_runtime import HuggingFaceRuntime, RuntimeOutput
from .ollama_runtime import OllamaRuntime


class ConfiguredRuntime:
    """Routes AI stages to local open-source runtimes or configured workers."""

    def __init__(self, device: str = "cuda") -> None:
        self.huggingface = HuggingFaceRuntime(device)
        self.ollama = OllamaRuntime()

    def execute(self, stage: str, model: str, prompt: str, parameters: dict[str, Any] | None = None) -> RuntimeOutput:
        parameters = parameters or {}
        if stage in {"script_analysis", "storyboard", "translation"}:
            text = self.ollama.generate(prompt, parameters)
            return RuntimeOutput((text.encode("utf-8"),), {"model": self.ollama.model, "format": "text"})
        if stage in {"character_generation", "environment_generation", "storyboard_image"}:
            return self.huggingface.generate_image(model, prompt, parameters)
        if stage in {"shot_generation", "video_generation"}:
            return self.huggingface.generate_video(model, prompt, parameters)
        endpoint = os.getenv("AI_AUDIO_ENDPOINT")
        if not endpoint:
            raise RuntimeError(f"no runtime configured for stage: {stage}; set AI_AUDIO_ENDPOINT")
        payload = json.dumps({"model": model, "stage": stage, "prompt": prompt, "parameters": parameters}).encode()
        request = urllib.request.Request(endpoint, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(request, timeout=600) as response:
            body = response.read()
            content_type = response.headers.get("Content-Type", "application/octet-stream")
        return RuntimeOutput((body,), {"model": model, "stage": stage, "content_type": content_type})

    def unload(self) -> None:
        self.huggingface.unload()
