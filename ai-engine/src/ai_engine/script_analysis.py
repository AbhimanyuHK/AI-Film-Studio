from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Any, Protocol


@dataclass(frozen=True)
class Character:
    name: str
    description: str


@dataclass(frozen=True)
class Location:
    name: str
    description: str


@dataclass(frozen=True)
class Scene:
    scene_id: str
    heading: str
    summary: str
    characters: tuple[str, ...] = ()
    location: str | None = None
    dialogue_required: bool = False


@dataclass(frozen=True)
class ScreenplayAnalysis:
    title: str
    logline: str
    characters: tuple[Character, ...]
    locations: tuple[Location, ...]
    scenes: tuple[Scene, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class StructuredLLM(Protocol):
    async def generate_json(self, *, system_prompt: str, user_prompt: str) -> dict[str, Any]: ...


SYSTEM_PROMPT = """You are a professional screenplay analyst. Analyze the supplied screenplay and return ONLY JSON matching this schema: {title:string, logline:string, characters:[{name:string,description:string}], locations:[{name:string,description:string}], scenes:[{scene_id:string,heading:string,summary:string,characters:[string],location:string|null,dialogue_required:boolean}]}. Preserve story facts. Do not invent characters or locations."""


def _parse(payload: dict[str, Any]) -> ScreenplayAnalysis:
    return ScreenplayAnalysis(
        title=str(payload.get("title", "Untitled")),
        logline=str(payload.get("logline", "")),
        characters=tuple(Character(str(x["name"]), str(x.get("description", ""))) for x in payload.get("characters", [])),
        locations=tuple(Location(str(x["name"]), str(x.get("description", ""))) for x in payload.get("locations", [])),
        scenes=tuple(
            Scene(
                scene_id=str(x["scene_id"]),
                heading=str(x.get("heading", "")),
                summary=str(x.get("summary", "")),
                characters=tuple(map(str, x.get("characters", []))),
                location=str(x["location"]) if x.get("location") is not None else None,
                dialogue_required=bool(x.get("dialogue_required", False)),
            )
            for x in payload.get("scenes", [])
        ),
    )


class ScriptAnalyzer:
    def __init__(self, llm: StructuredLLM) -> None:
        self.llm = llm

    async def analyze(self, screenplay: str) -> ScreenplayAnalysis:
        if not screenplay.strip():
            raise ValueError("screenplay cannot be empty")
        payload = await self.llm.generate_json(system_prompt=SYSTEM_PROMPT, user_prompt=screenplay)
        return _parse(payload)
