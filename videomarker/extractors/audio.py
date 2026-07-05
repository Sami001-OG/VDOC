"""FFmpeg-based audio extraction."""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Optional

from videomarker.core.extractor import AudioExtractor
from videomarker.models.video import VideoInfo

logger = logging.getLogger(__name__)


class FFmpegAudioExtractor(AudioExtractor):
    """Extract audio from video using FFmpeg."""

    def __init__(self, codec: str = "pcm_s16le") -> None:
        self.codec = codec

    def extract(
        self,
        video_info: VideoInfo,
        output_path: Path,
        sample_rate: int = 16000,
    ) -> Path:
        """Extract full audio track as WAV."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(video_info.metadata.file_path),
            "-vn",
            "-acodec", self.codec,
            "-ar", str(sample_rate),
            "-ac", "1",
            str(output_path),
        ]

        logger.info("Extracting audio: %s", " ".join(cmd))
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True
            )
            logger.info("Audio extracted to %s", output_path)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Audio extraction failed: {e.stderr}") from e

        return output_path

    def extract_segment(
        self,
        video_info: VideoInfo,
        start_time: float,
        end_time: float,
        output_path: Path,
    ) -> Path:
        """Extract a segment of audio."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        duration = end_time - start_time
        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(video_info.metadata.file_path),
            "-ss", str(start_time),
            "-t", str(duration),
            "-vn",
            "-acodec", self.codec,
            "-ar", "16000",
            "-ac", "1",
            str(output_path),
        ]

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(
                "Audio segment [%.2f-%.2f] extracted to %s",
                start_time, end_time, output_path,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Audio segment extraction failed: {e.stderr}") from e

        return output_path

    def has_audio(self, video_info: VideoInfo) -> bool:
        """Check if the video has an audio track."""
        return video_info.metadata.has_audio
