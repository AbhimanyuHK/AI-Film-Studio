from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Protocol

from .script_analysis import Character, Location


@dataclass(frozen=True)
class CharacterBible:
    name: str
    identity: str
    age_range: str
    appearance: str
    wardrobe: str
    personality: str
    visual_anchor: str


@dataclass(frozen=True)
class EnvironmentBible:
    name: str
    description: str
    architecture: str
    lighting: str
    palette: str
    continuity_anchors: tuple[str, ...]


@dataclass(frozen=True)
class ProductionBible:
    characters: tuple[CharacterBible, ...]
    environments: tuple[EnvironmentBible, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class StructuredLLM(Protocol):
    async def generate_json(self, *, system_prompt: str, user_prompt: str) -> dict[str, Any]: ...


CHARACTER_PROMPT = """Create a production character bible from the supplied screenplay character. Preserve supplied facts and do not invent plot facts. Return only JSON: {identity:string,age_range:string,appearance:string,wardrobe:string,personality:string,visual_anchor:string}. The visual_anchor must be concise and stable so downstream image/video prompts can preserve identity."""

ENVIRONMENT_PROMPT = """Create a production environment bible from the supplied screenplay location. Preserve supplied facts and do not invent story facts. Return only JSON: {description:string,architecture:string,lighting:string,palette:string,continuity_anchors:[string]}."""


class ProductionBibleBuilder:
    def __init__(self, llm: StructuredLLM) -> None:
        self.llm = llm

    async def character(self, character: Character) -> CharacterBible:
        payload = await self.llm.generate_json(
            system_prompt=CHARACTER_PROMPT,
            user_prompt=f"Name: {character.name}\nDescription: {character.description}",
        )
        return CharacterBible(
            name=character.name,
            identity=str(payload.get("identity", character.description)),
            age_range=str(payload.get("age_range", "unspecified")),
            appearance=str(payload.get("appearance", "")),
            wardrobe=str(payload.get("wardrobe", "")),
            personality=str(payload.get("personality", "")),
            visual_anchor=str(payload.get("visual_anchor", character.name)),
        )

    async def environment(self, location: Location) -> EnvironmentBible:
        payload = await self.llm.generate_json(
            system_prompt=ENVIRONMENT_PROMPT,
            user_prompt=f"Location: {location.name}\nDescription: {location.description}",
        )
        return EnvironmentBible(
            name=location.name,
            description=str(payload.get("description", location.description)),
            architecture=str(payload.get("architecture", "")),
            lighting=str(payload.get("lighting", "")),
            palette=str(payload.get("palette", "")),
            continuity_anchors=tuple(map(str, payload.get("continuity_anchors", []))),
        )

    async def build(self, characters: tuple[Character, ...], locations: tuple[Location, ...]) -> ProductionBible:
        character_bibles = tuple([await self.character(c) for c in characters])
        environment_bibles = tuple([await self.environment(l) for l in locations])
        return ProductionBible(character_bibles, environment_bibles)
