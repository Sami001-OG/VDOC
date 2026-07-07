"""FileService — file system operations."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Generator


def ensure_dir(path: Path) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_filename(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    name = re.sub(r'\s+', "_", name)
    name = name.strip("._")
    return name


def iter_video_files(directory: Path, recursive: bool = True) -> Generator[Path, None, None]:
    extensions = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".m4v", ".mpeg", ".ogv"}
    pattern = "**/*" if recursive else "*"
    for f in Path(directory).glob(pattern):
        if f.is_file() and f.suffix.lower() in extensions:
            yield f


def get_directory_size(path: Path) -> int:
    return sum(f.stat().st_size for f in Path(path).rglob("*") if f.is_file())
