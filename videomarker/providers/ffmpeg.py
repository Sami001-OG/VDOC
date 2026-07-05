"""FFmpeg-based video provider implementation."""

from __future__ import annotations

import hashlib
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from videomarker.core.provider import VideoProvider
from videomarker.models.video import VideoFormat, VideoInfo, VideoMetadata

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS: List[str] = [
    ".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".m4v", ".mpeg", ".ogv"
]


class FFmpegVideoProvider(VideoProvider):
    """Video provider using FFprobe for metadata extraction."""

    def load(self, path: Path) -> VideoInfo:
        """Load a video file and extract its metadata using FFprobe."""
        path = Path(path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Video file not found: {path}")
        if not self.supports(path):
            raise UnsupportedFormatError(f"Unsupported video format: {path.suffix}")

        metadata = self.get_metadata(path)
        video_info = VideoInfo(
            id=self._generate_id(path),
            metadata=VideoMetadata(**metadata),
            total_frames=self._calculate_total_frames(metadata),
            output_dir=path.parent / f"{path.stem}.markdir",
        )
        return video_info

    def supports(self, path: Path) -> bool:
        return path.suffix.lower() in SUPPORTED_EXTENSIONS

    def get_metadata(self, path: Path) -> dict:
        """Extract detailed metadata using FFprobe."""
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(path),
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFprobe failed: {e.stderr}") from e
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse FFprobe output: {e}") from e

        return self._parse_ffprobe_output(data, path)

    def _parse_ffprobe_output(self, data: dict, path: Path) -> dict:
        """Parse FFprobe JSON output into a metadata dictionary."""
        format_info = data.get("format", {})
        streams = data.get("streams", [])

        video_stream = None
        audio_stream = None
        for stream in streams:
            codec_type = stream.get("codec_type")
            if codec_type == "video" and video_stream is None:
                video_stream = stream
            elif codec_type == "audio" and audio_stream is None:
                audio_stream = stream

        duration = float(format_info.get("duration", 0))
        if video_stream:
            fps = self._parse_fps(video_stream)
            width = int(video_stream.get("width", 0))
            height = int(video_stream.get("height", 0))
            codec = video_stream.get("codec_name", "unknown")
            rotation = int(video_stream.get("rotation", 0))
        else:
            fps = 0.0
            width = 0
            height = 0
            codec = "unknown"
            rotation = 0

        metadata = {
            "file_path": str(path),
            "file_size": int(format_info.get("size", 0)),
            "duration": duration,
            "fps": fps,
            "width": width,
            "height": height,
            "codec": codec,
            "audio_codec": audio_stream.get("codec_name") if audio_stream else None,
            "audio_channels": int(audio_stream.get("channels", 0)) if audio_stream else None,
            "audio_sample_rate": int(audio_stream.get("sample_rate", 0)) if audio_stream else None,
            "bit_rate": int(format_info.get("bit_rate", 0)),
            "rotation": rotation,
            "format_name": format_info.get("format_name", "unknown"),
            "has_video": video_stream is not None,
            "has_audio": audio_stream is not None,
            "title": format_info.get("tags", {}).get("title"),
            "creation_time": format_info.get("tags", {}).get("creation_time"),
        }
        return metadata

    def _parse_fps(self, stream: dict) -> float:
        """Parse FPS from stream metadata."""
        r_frame_rate = stream.get("r_frame_rate", "0/1")
        parts = r_frame_rate.split("/")
        try:
            if len(parts) == 2 and float(parts[1]) != 0:
                return float(parts[0]) / float(parts[1])
        except (ValueError, ZeroDivisionError):
            pass
        avg_frame_rate = stream.get("avg_frame_rate", "0/1")
        parts = avg_frame_rate.split("/")
        try:
            if len(parts) == 2 and float(parts[1]) != 0:
                return float(parts[0]) / float(parts[1])
        except (ValueError, ZeroDivisionError):
            pass
        return 0.0

    def _calculate_total_frames(self, metadata: dict) -> int:
        """Calculate total number of frames."""
        duration = metadata.get("duration", 0)
        fps = metadata.get("fps", 0)
        if duration > 0 and fps > 0:
            return int(duration * fps)
        return 0

    def _generate_id(self, path: Path) -> str:
        """Generate a unique ID for the video job."""
        stat = path.stat()
        unique = f"{path.name}{stat.st_size}{stat.st_mtime}"
        return hashlib.md5(unique.encode()).hexdigest()[:12]


class UnsupportedFormatError(Exception):
    """Raised when a video format is not supported."""
    pass
