from __future__ import annotations

from dataclasses import dataclass

from .character_bible import CharacterBible, EnvironmentBible


@dataclass(frozen=True)
class VisualPrompt:
    subject: str
    environment: str
    continuity: str
    prompt: str


def character_prompt(character: CharacterBible) -> VisualPrompt:
    prompt = (
        f"{character.visual_anchor}. {character.appearance}. "
        f"Wardrobe: {character.wardrobe}. Personality: {character.personality}. "
        "Cinematic live-action film still, consistent facial identity, natural anatomy, "
        "physically plausible lighting, high detail."
    )
    return VisualPrompt(character.name, "", character.visual_anchor, prompt)


def environment_prompt(environment: EnvironmentBible) -> VisualPrompt:
    continuity = "; ".join(environment.continuity_anchors)
    prompt = (
        f"{environment.name}. {environment.description}. Architecture: {environment.architecture}. "
        f"Lighting: {environment.lighting}. Palette: {environment.palette}. "
        f"Continuity anchors: {continuity}. Cinematic production design, realistic materials, "
        "physically plausible lighting, high detail."
    )
    return VisualPrompt(environment.name, environment.name, continuity, prompt)
