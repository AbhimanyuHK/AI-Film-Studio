from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    name: str
    backend: str
    stages: tuple[str, ...]
    precision: str = "bf16"
    min_vram_gb: int = 0


# Production model names are configuration, not hard-coded execution dependencies.
# They can be replaced per deployment/film without changing the orchestration code.
DEFAULT_MODELS = (
    ModelSpec("qwen2.5-vl-72b", "huggingface", ("script_analysis", "storyboard"), min_vram_gb=80),
    ModelSpec("flux.1-dev", "huggingface", ("character_generation", "environment_generation"), min_vram_gb=24),
    ModelSpec("hunyuanvideo", "huggingface", ("video_generation", "shot_generation"), min_vram_gb=80),
    ModelSpec("whisper-large-v3", "huggingface", ("transcription",), min_vram_gb=8),
)


def models_for_stage(stage: str) -> tuple[ModelSpec, ...]:
    return tuple(model for model in DEFAULT_MODELS if stage in model.stages)
