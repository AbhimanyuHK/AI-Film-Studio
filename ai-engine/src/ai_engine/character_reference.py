from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class ReferenceImagePipeline(Protocol):
    def generate(self, prompt: str, **kwargs: Any) -> Any: ...


@dataclass(frozen=True)
class CharacterReference:
    film_id: str
    character_name: str
    reference_id: str
    image: Any
    visual_anchor: str


class CharacterReferenceGenerator:
    """Creates a canonical character reference image for one film."""

    def __init__(self, pipeline: ReferenceImagePipeline) -> None:
        self.pipeline = pipeline

    def generate(self, film_id: str, character_name: str, visual_anchor: str, *, seed: int | None = None) -> CharacterReference:
        if not film_id or not character_name:
            raise ValueError("film_id and character_name are required")
        prompt = (
            f"Character reference sheet for {character_name}. {visual_anchor}. "
            "Neutral pose, front three-quarter view, full body and portrait-ready facial detail, "
            "consistent wardrobe, realistic cinematic production photography, clean background."
        )
        kwargs: dict[str, Any] = {"width": 1024, "height": 1024, "num_inference_steps": 30}
        if seed is not None:
            kwargs["seed"] = seed
        image = self.pipeline.generate(prompt, **kwargs)
        reference_id = f"{film_id}:character:{character_name}"
        return CharacterReference(film_id, character_name, reference_id, image, visual_anchor)
