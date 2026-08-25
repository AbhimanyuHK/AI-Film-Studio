from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    model: str
    endpoint: str | None = None
    api_key_env: str | None = None

    def api_key(self) -> str | None:
        return os.getenv(self.api_key_env) if self.api_key_env else None


class ProviderRegistry:
    """Lightweight runtime registry; heavy ML libraries remain worker-only."""

    def __init__(self) -> None:
        self._factories: dict[str, Callable[[ProviderConfig], Any]] = {}
        self._configs: dict[str, ProviderConfig] = {}
        self._instances: dict[str, Any] = {}

    def register(self, stage: str, config: ProviderConfig, factory: Callable[[ProviderConfig], Any]) -> None:
        if not stage or stage in self._factories:
            raise ValueError("stage must be non-empty and registered only once")
        self._configs[stage] = config
        self._factories[stage] = factory

    def get(self, stage: str) -> Any:
        if stage not in self._factories:
            raise KeyError(f"no provider registered for stage: {stage}")
        if stage not in self._instances:
            self._instances[stage] = self._factories[stage](self._configs[stage])
        return self._instances[stage]

    def config(self, stage: str) -> ProviderConfig:
        return self._configs[stage]

    def unload(self, stage: str) -> None:
        instance = self._instances.pop(stage, None)
        if instance is not None and hasattr(instance, "unload"):
            instance.unload()

    def clear(self) -> None:
        for stage in tuple(self._instances):
            self.unload(stage)
