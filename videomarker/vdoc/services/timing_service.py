"""TimingService — time formatting and code timing utilities."""

from __future__ import annotations

import time
from typing import Optional


def format_timestamp(seconds: float, fmt: str = "hh:mm:ss.mmm") -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    if fmt == "hh:mm:ss":
        return f"{hours:02d}:{minutes:02d}:{int(secs):02d}"
    elif fmt == "mm:ss.mmm":
        return f"{minutes:02d}:{secs:06.3f}"
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"


def parse_timestamp(timestamp: str) -> float:
    parts = timestamp.strip().split(":")
    if len(parts) == 3:
        return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    elif len(parts) == 2:
        return float(parts[0]) * 60 + float(parts[1])
    return float(parts[0])


class Timer:
    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name or "Timer"
        self.start_time: float = 0.0
        self.elapsed: float = 0.0

    def __enter__(self) -> Timer:
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args: object) -> None:
        self.elapsed = time.perf_counter() - self.start_time

    def get_elapsed(self) -> float:
        if self.start_time:
            return time.perf_counter() - self.start_time
        return self.elapsed
