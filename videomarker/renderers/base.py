"""Base renderer interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

from videomarker.models.document import VideoDocument


class BaseRenderer(ABC):
    """All renderers inherit from this."""

    format_name: str = ""

    @abstractmethod
    def render(self, doc: VideoDocument, output_dir: Path) -> Path:
        """Render a VideoDocument to the given output directory.

        Args:
            doc: The document to render.
            output_dir: Directory to write output files.

        Returns:
            Path to the rendered output.
        """
        ...
