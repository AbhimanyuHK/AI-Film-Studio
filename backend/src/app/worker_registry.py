from collections.abc import Awaitable, Callable
from typing import Any

from app.provider_registry import AIProvider, ProviderConfig, ProviderRegistry


class WorkerRegistry:
    def __init__(self) -> None:
        self.providers = ProviderRegistry()

    def register_provider(self, name: str, job_types: tuple[str, ...], provider: AIProvider) -> None:
        self.providers.register(ProviderConfig(name=name, job_types=job_types), provider)

    def resolve(self, job_type: str) -> AIProvider:
        return self.providers.resolve(job_type)
