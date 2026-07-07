"""Abstract OCR provider."""

from __future__ import annotations

from abc import abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from vdoc.providers.base import BaseProvider


class OCRProvider(BaseProvider):
    """Optical character recognition."""

    @abstractmethod
    async def extract_text(self, image_path: Path) -> Dict[str, Any]:
        """Extract text from an image.

        Returns dict with keys: text, blocks[{text, bbox, confidence}], language.
        """
        ...

    @abstractmethod
    async def extract_batch(self, image_paths: List[Path]) -> List[Dict[str, Any]]:
        """Extract text from multiple images."""
        ...
