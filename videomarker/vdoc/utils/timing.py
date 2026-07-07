"""Timing utility functions."""

from __future__ import annotations

import time
from typing import Optional


def format_timestamp(seconds: float, format: str = "hh:mm:ss.mmm") -> str:
    """Format seconds to a human-readable timestamp.

    Args:
        seconds: Time value in seconds.
        format: Output format (hh:mm:ss.mmm, hh:mm:ss, mm:ss.mmm).

    Returns:
        Formatted timestamp string.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60

    if format == "hh:mm:ss":
        return f"{hours:02d}:{minutes:02d}:{int(secs):02d}"
    elif format == "mm:ss.mmm":
        return f"{minutes:02d}:{secs:06.3f}"
    else:
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"


def parse_timestamp(timestamp: str) -> float:
    """Parse a timestamp string to seconds.

    Args:
        timestamp: Timestamp in format HH:MM:SS.mmm or MM:SS.mmm.

    Returns:
        Time value in seconds.
    """
    parts = timestamp.strip().split(":")
    if len(parts) == 3:
        hours = float(parts[0])
        minutes = float(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds
    elif len(parts) == 2:
        minutes = float(parts[0])
        seconds = float(parts[1])
        return minutes * 60 + seconds
    else:
        return float(parts[0])


class Timer:
    """Simple context manager for timing code blocks."""

    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name or "Timer"
        self.start_time: float = 0.0
        self.elapsed: float = 0.0

    def __enter__(self) -> Timer:
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args: object) -> None:
        self.elapsed = time.perf_counter() - self.start_time
        if self.name:
            print(f"{self.name}: {self.elapsed:.3f}s")

    def get_elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time:
            return time.perf_counter() - self.start_time
        return self.elapsed
