"""Abstract base classes for frame and audio extraction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from videomarker.models.video import VideoInfo


class FrameExtractor(ABC):
    """Interface for extracting frames from video files."""

    @abstractmethod
    def extract(
        self,
        video_info: VideoInfo,
        output_dir: Path,
        fps: Optional[float] = None,
        max_frames: Optional[int] = None,
    ) -> List[Path]:
        """Extract frames from the video.

        Args:
            video_info: Video information from the provider.
            output_dir: Directory to write extracted frames.
            fps: Frames per second to extract. If None, uses video FPS.
            max_frames: Maximum number of frames to extract.

        Returns:
            List of paths to extracted frame images.
        """
        ...

    @abstractmethod
    def extract_at_timestamps(
        self,
        video_info: VideoInfo,
        timestamps: List[float],
        output_dir: Path,
    ) -> List[Path]:
        """Extract frames at specific timestamps.

        Args:
            video_info: Video information from the provider.
            timestamps: List of timestamps in seconds.
            output_dir: Directory to write extracted frames.

        Returns:
            List of paths to extracted frame images.
        """
        ...


class AudioExtractor(ABC):
    """Interface for extracting audio from video files."""

    @abstractmethod
    def extract(
        self,
        video_info: VideoInfo,
        output_path: Path,
        sample_rate: int = 16000,
    ) -> Path:
        """Extract audio from the video.

        Args:
            video_info: Video information from the provider.
            output_path: Path to write the audio file.
            sample_rate: Target sample rate in Hz.

        Returns:
            Path to the extracted audio file.
        """
        ...

    @abstractmethod
    def extract_segment(
        self,
        video_info: VideoInfo,
        start_time: float,
        end_time: float,
        output_path: Path,
    ) -> Path:
        """Extract a segment of audio from the video.

        Args:
            video_info: Video information from the provider.
            start_time: Start time in seconds.
            end_time: End time in seconds.
            output_path: Path to write the audio segment.

        Returns:
            Path to the extracted audio segment.
        """
        ...
