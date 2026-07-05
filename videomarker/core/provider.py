"""Abstract base class for video providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from videomarker.models.video import VideoInfo


class VideoProvider(ABC):
    """Interface for loading video files and extracting metadata."""

    @abstractmethod
    def load(self, path: Path) -> VideoInfo:
        """Load a video file and return its metadata and info.

        Args:
            path: Path to the video file.

        Returns:
            VideoInfo with parsed metadata.

        Raises:
            FileNotFoundError: If the video file does not exist.
            UnsupportedFormatError: If the format is not supported.
        """
        ...

    @abstractmethod
    def supports(self, path: Path) -> bool:
        """Check if this provider can handle the given video file.

        Args:
            path: Path to the video file.

        Returns:
            True if the provider can handle this file.
        """
        ...

    @abstractmethod
    def get_metadata(self, path: Path) -> dict:
        """Get raw metadata from the video file.

        Args:
            path: Path to the video file.

        Returns:
            Dictionary of raw metadata.
        """
        ...
