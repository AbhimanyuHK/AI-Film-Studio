from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RuntimeOutput:
    assets: tuple[bytes, ...]
    metadata: dict[str, Any]


class HuggingFaceRuntime:
    """Lazy Hugging Face image/video runtime owned by GPU workers."""

    def __init__(self, device: str = "cuda") -> None:
        self.device = device
        self._models: dict[tuple[str, str], Any] = {}

    def _image_pipeline(self, model: str) -> Any:
        key = ("image", model)
        if key not in self._models:
            from diffusers import AutoPipelineForText2Image  # type: ignore
            import torch  # type: ignore
            dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
            pipe = AutoPipelineForText2Image.from_pretrained(model, torch_dtype=dtype)
            if self.device.startswith("cuda") and torch.cuda.is_available():
                pipe = pipe.to(self.device)
            self._models[key] = pipe
        return self._models[key]

    def _video_pipeline(self, model: str) -> Any:
        key = ("video", model)
        if key not in self._models:
            from diffusers import DiffusionPipeline  # type: ignore
            import torch  # type: ignore
            dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
            pipe = DiffusionPipeline.from_pretrained(model, torch_dtype=dtype)
            if self.device.startswith("cuda") and torch.cuda.is_available():
                pipe = pipe.to(self.device)
            self._models[key] = pipe
        return self._models[key]

    def generate_image(self, model: str, prompt: str, parameters: dict[str, Any] | None = None) -> RuntimeOutput:
        result = self._image_pipeline(model)(prompt=prompt, **(parameters or {}))
        image = result.images[0]
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return RuntimeOutput((buffer.getvalue(),), {"model": model, "format": "png"})

    def generate_video(self, model: str, prompt: str, parameters: dict[str, Any] | None = None) -> RuntimeOutput:
        result = self._video_pipeline(model)(prompt=prompt, **(parameters or {}))
        frames = getattr(result, "frames", None)
        if frames is None:
            raise RuntimeError("video pipeline returned no frames")
        return RuntimeOutput((self._frames_to_mp4(frames),), {"model": model, "format": "mp4"})

    @staticmethod
    def _frames_to_mp4(frames: Any, fps: int = 24) -> bytes:
        import imageio.v3 as iio  # type: ignore
        import numpy as np  # type: ignore
        import tempfile
        from pathlib import Path
        sequence = frames[0] if isinstance(frames, (list, tuple)) and frames and isinstance(frames[0], (list, tuple)) else frames
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "output.mp4"
            iio.imwrite(path, np.asarray(sequence), fps=fps, codec="libx264")
            return path.read_bytes()

    def unload(self) -> None:
        self._models.clear()
        try:
            import torch  # type: ignore
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
