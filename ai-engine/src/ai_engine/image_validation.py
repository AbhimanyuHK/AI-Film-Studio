from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ImageValidation:
    valid: bool
    width: int
    height: int
    errors: tuple[str, ...]


def validate_image(image: Any, *, min_width: int = 1024, min_height: int = 1024) -> ImageValidation:
    width = int(getattr(image, "width", 0))
    height = int(getattr(image, "height", 0))
    errors: list[str] = []
    if width < min_width:
        errors.append(f"width {width} is below minimum {min_width}")
    if height < min_height:
        errors.append(f"height {height} is below minimum {min_height}")
    return ImageValidation(not errors, width, height, tuple(errors))
