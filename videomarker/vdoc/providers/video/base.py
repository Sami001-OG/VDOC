"""Abstract video provider."""

from __future__ import annotations

from abc import abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from vdoc.providers.base import BaseProvider, ProviderConfig


class VideoProvider(BaseProvider):
    """Reads video files, extracts metadata, frames, and audio."""

    @abstractmethod
    async def load(self, path: Path) -> Dict[str, Any]:
        """Load video and return metadata."""
        ...

    @abstractmethod
    async def extract_frames(
        self, timestamps: List[float], output_dir: Path
    ) -> List[Path]:
        """Extract frames at specific timestamps."""
        ...

    @abstractmethod
    async def extract_audio(
        self, output_path: Path, sample_rate: int = 16000
    ) -> Path:
        """Extract audio track."""
        ...

    @abstractmethod
    async def get_metadata(self) -> Dict[str, Any]:
        """Return video metadata."""
        ...
