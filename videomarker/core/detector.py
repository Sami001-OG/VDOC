"""Abstract base class for scene detectors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from videomarker.models.segment import Scene
from videomarker.models.video import VideoInfo


class SceneDetector(ABC):
    """Interface for detecting scene changes in a video."""

    @abstractmethod
    def detect(
        self,
        video_info: VideoInfo,
        frames_dir: Optional[Path] = None,
        video_path: Optional[Path] = None,
    ) -> List[Scene]:
        """Detect scenes in the video.

        Args:
            video_info: Video information from the provider.
            frames_dir: Optional directory with extracted frames.
            video_path: Optional path to the original video file.

        Returns:
            List of detected Scene objects.
        """
        ...

    @abstractmethod
    def detect_hard_cuts(
        self,
        video_info: VideoInfo,
        threshold: float = 30.0,
    ) -> List[Scene]:
        """Detect hard cut transitions.

        Args:
            video_info: Video information from the provider.
            threshold: Detection threshold.

        Returns:
            List of scenes detected via hard cuts.
        """
        ...
