from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .character_bible import CharacterBible, EnvironmentBible
from .script_analysis import Scene


@dataclass(frozen=True)
class Shot:
    shot_id: str
    scene_id: str
    shot_type: str
    camera: str
    lens: str
    movement: str
    lighting: str
    action: str
    dialogue: str
    characters: tuple[str, ...]
    location: str | None
    visual_prompt: str
    continuity_anchors: tuple[str, ...]


@dataclass(frozen=True)
class Storyboard:
    scene_id: str
    shots: tuple[Shot, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class StoryboardBuilder:
    """Deterministic shot-plan builder from screenplay facts and production bibles."""

    def __init__(self, characters: tuple[CharacterBible, ...], environments: tuple[EnvironmentBible, ...]) -> None:
        self.characters = {c.name: c for c in characters}
        self.environments = {e.name: e for e in environments}

    def build_scene(self, scene: Scene) -> Storyboard:
        character_refs = [self.characters[name] for name in scene.characters if name in self.characters]
        environment = self.environments.get(scene.location or "")
        visual_parts = [scene.summary]
        visual_parts.extend(c.visual_anchor for c in character_refs)
        if environment:
            visual_parts.extend((environment.description, environment.lighting, environment.palette))
        prompt = ". ".join(x for x in visual_parts if x)
        anchors = tuple([c.visual_anchor for c in character_refs] + (list(environment.continuity_anchors) if environment else []))
        shot = Shot(
            shot_id=f"{scene.scene_id}-001",
            scene_id=scene.scene_id,
            shot_type="master",
            camera="eye-level",
            lens="35mm",
            movement="static",
            lighting=environment.lighting if environment else "natural cinematic lighting",
            action=scene.summary,
            dialogue="dialogue required" if scene.dialogue_required else "",
            characters=scene.characters,
            location=scene.location,
            visual_prompt=prompt,
            continuity_anchors=anchors,
        )
        return Storyboard(scene.scene_id, (shot,))

    def build(self, scenes: tuple[Scene, ...]) -> tuple[Storyboard, ...]:
        return tuple(self.build_scene(scene) for scene in scenes)
