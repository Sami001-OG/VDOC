"""Abstract base class for all processors in the plugin system."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from videomarker.config.settings import VideoMarkerSettings


class Processor(ABC):
    """Base class for all video processors.

    All processors must inherit from this class and implement
    the process method. Processors are discovered automatically
    via the plugin system.
    """

    def __init__(self, settings: Optional[VideoMarkerSettings] = None, **kwargs: Any) -> None:
        self.settings = settings

    @abstractmethod
    def process(self, context: Any) -> None:
        """Execute the processor on the given pipeline context.

        The context contains all data produced by previous pipeline
        stages: video info, frames, audio, scenes, timeline, etc.

        Args:
            context: PipelineContext with all pipeline data.
        """
        ...

    @property
    def name(self) -> str:
        """Return the processor name (set via decorator or class attribute)."""
        return getattr(self, "__processor_name__", self.__class__.__name__)
