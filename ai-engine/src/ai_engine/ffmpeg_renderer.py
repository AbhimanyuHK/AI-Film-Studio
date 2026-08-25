from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any


class FFmpegRenderer:
    """Minimal local FFmpeg renderer for an already prepared shot sequence."""

    def __init__(self, ffmpeg_binary: str = "ffmpeg") -> None:
        self.ffmpeg_binary = ffmpeg_binary
        if shutil.which(ffmpeg_binary) is None:
            raise RuntimeError("ffmpeg executable was not found")

    def render(self, shots: list[Any], audio: Any = None, subtitles: str | None = None, **kwargs: Any) -> Path:
        output = kwargs.pop("output_path", None)
        if output is None:
            raise ValueError("output_path is required for FFmpegRenderer")
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shot_paths = [Path(item) for item in shots]
        if not shot_paths or any(not item.exists() for item in shot_paths):
            raise FileNotFoundError("all shot files must exist")
        concat = output_path.with_suffix(".concat.txt")
        concat.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in shot_paths), encoding="utf-8")
        command = [self.ffmpeg_binary, "-y", "-f", "concat", "-safe", "0", "-i", str(concat)]
        if audio is not None:
            command += ["-i", str(audio), "-shortest"]
        command += ["-c:v", "libx264", "-pix_fmt", "yuv420p"]
        if audio is not None:
            command += ["-c:a", "aac"]
        command += [str(output_path)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        concat.unlink(missing_ok=True)
        return output_path
