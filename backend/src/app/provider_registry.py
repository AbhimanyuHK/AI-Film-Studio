from dataclasses import dataclass
from typing import Any, Protocol


class AIProvider(Protocol):
    async def execute(self, payload: dict[str, Any]) -> dict[str, Any]: ...


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    job_types: tuple[str, ...]
    enabled: bool = True


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, AIProvider] = {}
        self._configs: dict[str, ProviderConfig] = {}

    def register(self, config: ProviderConfig, provider: AIProvider) -> None:
        self._configs[config.name] = config
        self._providers[config.name] = provider

    def resolve(self, job_type: str) -> AIProvider:
        for name, config in self._configs.items():
            if config.enabled and job_type in config.job_types:
                return self._providers[name]
        raise LookupError(f"No enabled AI provider for {job_type}")
