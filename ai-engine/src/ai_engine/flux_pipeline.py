from __future__ import annotations

from typing import Any


class FluxPipelineAdapter:
    """Lazy FLUX.1 image pipeline adapter for GPU workers."""

    def __init__(self, model_id: str = "black-forest-labs/FLUX.1-dev", device: str = "cuda") -> None:
        self.model_id = model_id
        self.device = device
        self._pipeline: Any | None = None

    def load(self) -> None:
        if self._pipeline is not None:
            return
        try:
            import torch  # type: ignore
            from diffusers import FluxPipeline  # type: ignore
        except ImportError as exc:
            raise RuntimeError("FLUX worker requires torch and diffusers") from exc
        dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
        self._pipeline = FluxPipeline.from_pretrained(self.model_id, torch_dtype=dtype)
        if self.device.startswith("cuda") and torch.cuda.is_available():
            self._pipeline = self._pipeline.to(self.device)

    def generate(self, prompt: str, **kwargs: Any) -> Any:
        self.load()
        assert self._pipeline is not None
        references = kwargs.pop("references", ())
        if references:
            raise NotImplementedError("reference-image conditioning requires a compatible FLUX adapter")
        kwargs.pop("film_id", None)
        kwargs.pop("shot_id", None)
        generator = kwargs.pop("generator", None)
        if generator is None and kwargs.get("seed") is not None:
            generator = self._make_generator(int(kwargs.pop("seed")))
        else:
            kwargs.pop("seed", None)
        result = self._pipeline(prompt=prompt, generator=generator, **kwargs)
        return result.images[0]

    def _make_generator(self, seed: int) -> Any:
        import torch  # type: ignore
        return torch.Generator(device=self.device).manual_seed(seed)

    def unload(self) -> None:
        self._pipeline = None
        try:
            import torch  # type: ignore
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
