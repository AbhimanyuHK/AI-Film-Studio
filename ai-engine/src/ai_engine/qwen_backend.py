from __future__ import annotations

from typing import Any


class QwenStructuredBackend:
    """Adapter for a locally served Qwen model (for example through vLLM).

    The HTTP transport is injected so tests and workers do not require a live
    model server during import. Production wiring should provide a client
    implementing `generate_json`.
    """

    def __init__(self, client: Any, model: str = "qwen2.5-vl-72b") -> None:
        self.client = client
        self.model = model

    async def generate_json(self, *, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        result = await self.client.generate(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        if not isinstance(result, dict):
            raise TypeError("Qwen client must return a JSON object")
        return result
