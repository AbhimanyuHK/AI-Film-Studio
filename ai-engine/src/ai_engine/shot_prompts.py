from __future__ import annotations

from .storyboard import Shot


def build_shot_prompt(shot: Shot) -> str:
    parts = [
        shot.visual_prompt,
        f"Shot type: {shot.shot_type}",
        f"Camera: {shot.camera}",
        f"Lens: {shot.lens}",
        f"Movement: {shot.movement}",
        f"Action: {shot.action}",
    ]
    if shot.dialogue:
        parts.append(f"Dialogue: {shot.dialogue}")
    if shot.continuity_anchors:
        parts.append("Continuity anchors: " + "; ".join(shot.continuity_anchors))
    return ". ".join(part for part in parts if part)
