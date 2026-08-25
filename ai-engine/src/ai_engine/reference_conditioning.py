from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class ReferenceConditioningInput:
    reference_id: str
    image: Any
    character_name: str


class ReferenceConditioningAdapter(Protocol):
    """Model-specific interface for identity/reference conditioning."""

    def condition(self, prompt: str, references: tuple[ReferenceConditioningInput, ...]) -> dict[str, Any]: ...


class UnsupportedReferenceConditioning:
    """Safe fallback: never silently discards references."""

    def condition(self, prompt: str, references: tuple[ReferenceConditioningInput, ...]) -> dict[str, Any]:
        if references:
            raise NotImplementedError("selected image model does not support reference conditioning")
        return {"prompt": prompt}


@dataclass(frozen=True)
class ConditionedPrompt:
    prompt: str
    reference_ids: tuple[str, ...]


def build_conditioned_input(
    prompt: str,
    references: tuple[ReferenceConditioningInput, ...],
    adapter: ReferenceConditioningAdapter,
) -> ConditionedPrompt:
    if any(not r.reference_id for r in references):
        raise ValueError("reference_id is required for every conditioning reference")
    payload = adapter.condition(prompt, references)
    return ConditionedPrompt(
        prompt=str(payload.get("prompt", prompt)),
        reference_ids=tuple(r.reference_id for r in references),
    )
