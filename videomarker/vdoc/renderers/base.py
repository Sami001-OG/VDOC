"""Base renderer interface with versioning and validation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from vdoc.models.document import VideoDocument

RENDERER_VERSION = "1.0.0"


class BaseRenderer(ABC):
    """All renderers inherit from this.

    Features:
        - Format name and version (#54)
        - Input validation (#55)
        - Deterministic by default (#57)
    """

    format_name: str = ""
    format_version: str = RENDERER_VERSION

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

    def validate(self, doc: VideoDocument) -> List[str]:
        """Validate that a document can be rendered by this renderer.

        Returns a list of error messages (empty = valid).
        """
        errors: List[str] = []
        if not doc.title and self.format_name != "json":
            errors.append("Document has no title")
        return errors
