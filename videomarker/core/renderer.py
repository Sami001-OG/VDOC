"""Abstract base class for renderers that produce the final output."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

from videomarker.config.settings import VideoMarkerSettings


class Renderer(ABC):
    """Interface for rendering pipeline output to the MarkDirectory format."""

    def __init__(self, settings: Optional[VideoMarkerSettings] = None) -> None:
        self.settings = settings

    @abstractmethod
    def render(self, context: Any) -> Path:
        """Render pipeline context to the final output.

        Args:
            context: PipelineContext with all pipeline data.

        Returns:
            Path to the root of the rendered MarkDirectory.
        """
        ...

    @abstractmethod
    def render_scene(self, scene: Any, context: Any) -> Path:
        """Render a single scene directory.

        Args:
            scene: Scene object to render.
            context: PipelineContext with scene data.

        Returns:
            Path to the scene directory.
        """
        ...
