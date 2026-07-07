"""Abstract vision provider."""

from __future__ import annotations

from abc import abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from vdoc.providers.base import BaseProvider


class VisionProvider(BaseProvider):
    """Image and video understanding."""

    @abstractmethod
    async def describe(self, image_path: Path, prompt: Optional[str] = None) -> Dict[str, Any]:
        """Describe the contents of an image.

        Returns dict with keys: summary, detailed, tags, objects, activities.
        """
        ...

    @abstractmethod
    async def analyze_batch(
        self, image_paths: List[Path], prompt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Analyze multiple images."""
        ...
