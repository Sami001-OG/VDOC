"""AssetManager — centralized file handling for pipeline assets."""

from __future__ import annotations

import logging
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class AssetManager:
    """Centralizes all file I/O for pipeline artifacts.

    Responsibilities:
      - Track every file the pipeline creates (keyframes, checkpoints, exports)
      - Provide deterministic paths organized by output directory
      - Auto-cleanup temporary files on request or context exit
    """

    def __init__(self, output_dir: Optional[Path] = None) -> None:
        self._output_dir = Path(output_dir) if output_dir else Path(tempfile.mkdtemp())
        self._tracked: Dict[str, Path] = {}
        self._temp_dirs: Set[Path] = set()

    # -- Public API --

    def set_output_dir(self, path: Path) -> None:
        self._output_dir = Path(path)

    def get_output_dir(self) -> Path:
        return self._output_dir

    def allocate_path(self, name: str, subdir: str = "") -> Path:
        """Return a deterministic path under the output directory, creating parent dirs."""
        base = self._output_dir / subdir if subdir else self._output_dir
        base.mkdir(parents=True, exist_ok=True)
        path = base / name
        self._tracked[name] = path
        return path

    def allocate_temp(self, suffix: str = "", prefix: str = "vdoc_") -> Path:
        """Return a path to a temporary file that will be cleaned up."""
        fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
        import os
        os.close(fd)
        p = Path(path)
        self._tracked[prefix] = p
        return p

    def allocate_temp_dir(self, prefix: str = "vdoc_") -> Path:
        """Return a path to a temporary directory that will be cleaned up."""
        path = Path(tempfile.mkdtemp(prefix=prefix))
        self._temp_dirs.add(path)
        return path

    def track(self, key: str, path: Path) -> None:
        self._tracked[key] = path

    def get(self, key: str) -> Optional[Path]:
        return self._tracked.get(key)

    def list_assets(self, subdir: str = "") -> List[Path]:
        base = self._output_dir / subdir if subdir else self._output_dir
        if not base.exists():
            return []
        return sorted(p for p in base.rglob("*") if p.is_file())

    def list_by_type(self, ext: str) -> List[Path]:
        return [p for p in self._tracked.values() if p.suffix == ext]

    def cleanup_temp(self) -> int:
        """Remove all tracked temp files and dirs. Returns count removed."""
        count = 0
        for key, path in list(self._tracked.items()):
            if path.exists():
                try:
                    path.unlink()
                    count += 1
                except OSError as e:
                    logger.warning("Could not remove %s: %s", path, e)
        for d in self._temp_dirs:
            if d.exists():
                try:
                    shutil.rmtree(d)
                    count += 1
                except OSError as e:
                    logger.warning("Could not remove temp dir %s: %s", d, e)
        self._tracked.clear()
        self._temp_dirs.clear()
        return count

    def get_disk_usage(self) -> int:
        total = 0
        for p in self._tracked.values():
            if p.exists() and p.is_file():
                total += p.stat().st_size
        return total
