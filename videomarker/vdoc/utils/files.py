"""File system utility functions."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Generator, List


def ensure_dir(path: Path) -> Path:
    """Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure exists.

    Returns:
        The path to the directory.
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_filename(name: str) -> str:
    """Convert a string to a safe filename.

    Args:
        name: Raw filename string.

    Returns:
        Sanitized filename safe for all operating systems.
    """
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    name = re.sub(r'\s+', "_", name)
    name = name.strip("._")
    return name


def iter_video_files(
    directory: Path,
    recursive: bool = True,
) -> Generator[Path, None, None]:
    """Iterate over video files in a directory.

    Args:
        directory: Directory to search.
        recursive: Whether to search subdirectories.

    Yields:
        Paths to video files.
    """
    extensions = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".m4v", ".mpeg", ".ogv"}
    pattern = "**/*" if recursive else "*"
    for f in Path(directory).glob(pattern):
        if f.is_file() and f.suffix.lower() in extensions:
            yield f


def get_directory_size(path: Path) -> int:
    """Calculate the total size of a directory in bytes.

    Args:
        path: Directory path.

    Returns:
        Total size in bytes.
    """
    return sum(f.stat().st_size for f in Path(path).rglob("*") if f.is_file())
