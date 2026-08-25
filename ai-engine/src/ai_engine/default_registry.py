from .adapters import AudioGenerationAdapter, ImageGenerationAdapter, ModelAdapter, ScriptAnalysisAdapter, VideoGenerationAdapter


def default_adapters() -> tuple[ModelAdapter, ...]:
    return (
        ScriptAnalysisAdapter(),
        ImageGenerationAdapter(),
        VideoGenerationAdapter(),
        AudioGenerationAdapter(),
    )


def adapter_for_stage(stage: str) -> ModelAdapter:
    for adapter in default_adapters():
        if stage in adapter.stages:
            return adapter
    raise KeyError(f"No AI adapter registered for stage: {stage}")
