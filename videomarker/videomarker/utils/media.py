"""Media utility functions."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple


def is_video_file(path: Path) -> bool:
    """Check if a file is a supported video format.

    Args:
        path: Path to check.

    Returns:
        True if the file is a supported video format.
    """
    video_extensions = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".m4v", ".mpeg", ".ogv"}
    return path.suffix.lower() in video_extensions


def get_video_dimensions(path: Path) -> Optional[Tuple[int, int]]:
    """Get video dimensions (width, height) using OpenCV.

    Args:
        path: Path to the video file.

    Returns:
        Tuple of (width, height) or None if unavailable.
    """
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
    """Get the aspect ratio string for given dimensions.

    Args:
        width: Frame width in pixels.
        height: Frame height in pixels.

    Returns:
        Aspect ratio string (e.g., "16:9").
    """
    from math import gcd
    g = gcd(width, height)
    return f"{width // g}:{height // g}"
