from __future__ import annotations

from typing import Any


class HunyuanVideoPipelineAdapter:
    """Lazy HunyuanVideo Diffusers adapter for dedicated GPU workers.

    The exact checkpoint and pipeline implementation are configurable because
    HunyuanVideo variants have different hardware and scheduler requirements.
    """

    def __init__(self, model_id: str = "hunyuanvideo-community/HunyuanVideo", device: str = "cuda") -> None:
        self.model_id = model_id
        self.device = device
        self._pipeline: Any | None = None

    def load(self) -> None:
        if self._pipeline is not None:
            return
        try:
            import torch  # type: ignore
            from diffusers import HunyuanVideoPipeline  # type: ignore
        except ImportError as exc:
            raise RuntimeError("HunyuanVideo worker requires torch and diffusers") from exc
        dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
        self._pipeline = HunyuanVideoPipeline.from_pretrained(self.model_id, torch_dtype=dtype)
        if self.device.startswith("cuda") and torch.cuda.is_available():
            self._pipeline = self._pipeline.to(self.device)

    def generate(self, image: Any, prompt: str, **kwargs: Any) -> Any:
        self.load()
        assert self._pipeline is not None
        seed = kwargs.pop("seed", None)
        generator = None
        if seed is not None:
            import torch  # type: ignore
            generator = torch.Generator(device=self.device).manual_seed(int(seed))
        result = self._pipeline(prompt=prompt, image=image, generator=generator, **kwargs)
        return result.frames[0] if hasattr(result, "frames") else result

    def unload(self) -> None:
        self._pipeline = None
        try:
            import torch  # type: ignore
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
