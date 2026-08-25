from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SubtitleCue:
    index: int
    start_seconds: float
    end_seconds: float
    text: str

    def __post_init__(self) -> None:
        if self.index < 1 or self.start_seconds < 0 or self.end_seconds <= self.start_seconds:
            raise ValueError("invalid subtitle cue timing")


def _timestamp(seconds: float) -> str:
    milliseconds = int(round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds_part, millis = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{seconds_part:02},{millis:03}"


def to_srt(cues: tuple[SubtitleCue, ...]) -> str:
    return "\n\n".join(
        f"{cue.index}\n{_timestamp(cue.start_seconds)} --> {_timestamp(cue.end_seconds)}\n{cue.text}"
        for cue in cues
    ) + ("\n" if cues else "")
