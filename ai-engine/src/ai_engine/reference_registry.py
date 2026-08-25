from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReferenceBinding:
    film_id: str
    character_name: str
    reference_id: str


class FilmReferenceRegistry:
    """In-memory reference registry with explicit film-bound lookups."""

    def __init__(self) -> None:
        self._bindings: dict[tuple[str, str], ReferenceBinding] = {}

    def register(self, film_id: str, character_name: str, reference_id: str) -> ReferenceBinding:
        if not film_id or not character_name or not reference_id:
            raise ValueError("film_id, character_name and reference_id are required")
        binding = ReferenceBinding(film_id, character_name, reference_id)
        self._bindings[(film_id, character_name)] = binding
        return binding

    def get(self, film_id: str, character_name: str) -> ReferenceBinding | None:
        return self._bindings.get((film_id, character_name))

    def require(self, film_id: str, character_name: str) -> ReferenceBinding:
        binding = self.get(film_id, character_name)
        if binding is None:
            raise KeyError(f"no reference registered for film={film_id!r}, character={character_name!r}")
        return binding
