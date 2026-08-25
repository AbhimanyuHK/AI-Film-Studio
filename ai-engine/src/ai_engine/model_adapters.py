from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .provider_runtime import ProviderConfig, ProviderRegistry


class TextModel(Protocol):
    def generate(self, prompt: str, **kwargs: Any) -> Any: ...


class ImageModel(Protocol):
    def generate(self, prompt: str, **kwargs: Any) -> Any: ...


class VideoModel(Protocol):
    def generate(self, prompt: str, **kwargs: Any) -> Any: ...


class AudioModel(Protocol):
    def generate(self, text: str, **kwargs: Any) -> Any: ...


@dataclass(frozen=True)
class ModelRequest:
    stage: str
    prompt: str
    kwargs: dict[str, Any]


class RuntimeModelAdapter:
    """Thin adapter over ProviderRegistry; actual heavy model loading remains worker-owned."""

    def __init__(self, registry: ProviderRegistry) -> None:
        self.registry = registry

    def execute(self, request: ModelRequest) -> Any:
        model = self.registry.get(request.stage)
        if not hasattr(model, "generate"):
            raise TypeError(f"provider for {request.stage} does not expose generate()")
        return model.generate(request.prompt, **request.kwargs)

    def execute_text(self, request: ModelRequest) -> Any:
        return self.execute(request)

    def execute_image(self, request: ModelRequest) -> Any:
        return self.execute(request)

    def execute_video(self, request: ModelRequest) -> Any:
        return self.execute(request)

    def execute_audio(self, request: ModelRequest) -> Any:
        return self.execute(request)


def register_callable_provider(registry: ProviderRegistry, stage: str, model: str, factory: Any, endpoint: str | None = None, api_key_env: str | None = None) -> None:
    registry.register(stage, ProviderConfig(name=stage, model=model, endpoint=endpoint, api_key_env=api_key_env), factory)
