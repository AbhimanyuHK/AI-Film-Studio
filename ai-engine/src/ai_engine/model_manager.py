from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class LoadedModel:
    name: str
    device: str
    backend: str
    pipeline: Any


class ModelManager:
    """Lazy, per-worker model cache. Heavy ML dependencies are loaded only on GPU workers."""

    def __init__(self, device: str = "cuda") -> None:
        self.device = device
        self._models: dict[tuple[str, str], LoadedModel] = {}

    def get(self, name: str, backend: str) -> LoadedModel | None:
        return self._models.get((backend, name))

    def load(self, name: str, backend: str) -> LoadedModel:
        key = (backend, name)
        if key in self._models:
            return self._models[key]

        if backend == "huggingface":
            # Import only inside the worker process; API/test processes do not need torch/CUDA.
            try:
                import torch  # type: ignore
                from transformers import AutoModel  # type: ignore
            except ImportError as exc:
                raise RuntimeError("GPU worker requires torch and transformers") from exc
            dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
            pipeline = AutoModel.from_pretrained(name, torch_dtype=dtype)
            if self.device.startswith("cuda") and torch.cuda.is_available():
                pipeline = pipeline.to(self.device)
        else:
            raise ValueError(f"Unsupported model backend: {backend}")

        loaded = LoadedModel(name=name, device=self.device, backend=backend, pipeline=pipeline)
        self._models[key] = loaded
        return loaded

    def unload(self, name: str, backend: str) -> bool:
        model = self._models.pop((backend, name), None)
        if model is None:
            return False
        del model.pipeline
        try:
            import torch  # type: ignore
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
        return True
