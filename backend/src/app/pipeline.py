from dataclasses import dataclass


@dataclass(frozen=True)
class PipelineStage:
    name: str
    depends_on: tuple[str, ...] = ()


# Stages without dependencies can run in parallel. Downstream stages wait
# until every declared dependency succeeds.
FILM_PIPELINE: tuple[PipelineStage, ...] = (
    PipelineStage("script_analysis"),
    PipelineStage("character_generation", ("script_analysis",)),
    PipelineStage("environment_generation", ("script_analysis",)),
    PipelineStage("storyboard", ("script_analysis", "character_generation", "environment_generation")),
    PipelineStage("shot_generation", ("storyboard",)),
    PipelineStage("video_generation", ("shot_generation",)),
    PipelineStage("voice_generation", ("script_analysis",)),
    PipelineStage("translation", ("script_analysis",)),
    PipelineStage("dubbing", ("voice_generation", "translation")),
    PipelineStage("music_generation", ("script_analysis",)),
    PipelineStage("sfx_generation", ("shot_generation",)),
    PipelineStage("editing", ("video_generation", "dubbing", "music_generation", "sfx_generation")),
    PipelineStage("upscaling", ("editing",)),
    PipelineStage("final_render", ("upscaling",)),
)


def validate_pipeline() -> None:
    names = {stage.name for stage in FILM_PIPELINE}
    if len(names) != len(FILM_PIPELINE):
        raise ValueError("Duplicate pipeline stage")
    for stage in FILM_PIPELINE:
        unknown = set(stage.depends_on) - names
        if unknown:
            raise ValueError(f"Unknown dependencies for {stage.name}: {sorted(unknown)}")


validate_pipeline()


def ready_stages(succeeded: set[str], active: set[str] | None = None) -> list[str]:
    active = active or set()
    return [
        stage.name
        for stage in FILM_PIPELINE
        if stage.name not in succeeded and stage.name not in active and set(stage.depends_on) <= succeeded
    ]
