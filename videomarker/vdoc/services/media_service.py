"""MediaService — video/media utility operations."""

from __future__ import annotations

from math import gcd
from pathlib import Path
from typing import Optional, Tuple


def is_video_file(path: Path) -> bool:
    video_extensions = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".m4v", ".mpeg", ".ogv"}
    return path.suffix.lower() in video_extensions


def get_video_dimensions(path: Path) -> Optional[Tuple[int, int]]:
    try:
        import cv2
        cap = cv2.VideoCapture(str(path))
        if not cap.isOpened():
            return None
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        return (width, height)
    except ImportError:
        return None


def get_aspect_ratio(width: int, height: int) -> str:
    g = gcd(width, height)
    return f"{width // g}:{height // g}"
