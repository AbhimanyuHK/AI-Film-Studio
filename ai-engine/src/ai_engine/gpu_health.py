from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GPUHealth:
    available: bool
    device_count: int
    devices: tuple[dict, ...]


def inspect_gpu() -> GPUHealth:
    try:
        import torch  # type: ignore
    except ImportError:
        return GPUHealth(False, 0, ())

    if not torch.cuda.is_available():
        return GPUHealth(False, 0, ())

    devices = tuple(
        {
            "index": index,
            "name": torch.cuda.get_device_name(index),
            "total_memory_bytes": torch.cuda.get_device_properties(index).total_memory,
        }
        for index in range(torch.cuda.device_count())
    )
    return GPUHealth(True, len(devices), devices)
