"""FFmpeg-based video provider — extracts metadata, frames, and audio."""

from __future__ import annotations

import hashlib
import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from vdoc.providers.video.base import VideoProvider

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS: List[str] = [
    ".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".m4v", ".mpeg", ".ogv",
]


class FFmpegVideoProvider(VideoProvider):
    """Video provider using FFprobe for metadata and FFmpeg for frame/audio extraction."""

    def __init__(self) -> None:
        super().__init__()
        self._current_path: Optional[Path] = None

    async def initialize(self) -> None:
        pass

    async def process(self, data: Any) -> Any:
        return await self.load(Path(data)) if isinstance(data, (str, Path)) else data

    async def close(self) -> None:
        pass

    async def load(self, path: Path) -> Dict[str, Any]:
        path = Path(path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Video file not found: {path}")
        if not self._supports(path):
            raise ValueError(f"Unsupported format: {path.suffix}")
        self._current_path = path
        return await self.get_metadata(path)

    async def extract_frames(self, timestamps: List[float], output_dir: Path) -> List[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        paths = []
        for i, ts in enumerate(timestamps):
            out = output_dir / f"frame_{i:06d}.jpg"
            cmd = [
                "ffmpeg", "-y",
                "-ss", str(ts),
                "-i", str(self._current_path),
                "-vframes", "1",
                "-q:v", "2",
                str(out),
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            paths.append(out)
        return paths

    async def extract_audio(self, output_path: Path, sample_rate: int = 16000) -> Path:
        cmd = [
            "ffmpeg", "-y",
            "-i", str(self._current_path),
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", str(sample_rate),
            "-ac", "1",
            str(output_path),
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return output_path

    async def get_metadata(self, video_path: Optional[Path] = None) -> Dict[str, Any]:
        path = video_path or self._current_path
        cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format", "-show_streams",
            str(path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return self._parse_ffprobe_output(data, Path(path))

    def _supports(self, path: Path) -> bool:
        return path.suffix.lower() in SUPPORTED_EXTENSIONS

    def _parse_ffprobe_output(self, data: dict, path: Path) -> dict:
        fmt = data.get("format", {})
        streams = data.get("streams", [])

        video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
        audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

        duration = float(fmt.get("duration", 0))
        fps = 0.0
        width, height = 0, 0
        codec = "unknown"
        if video_stream:
            fps = self._parse_fps(video_stream)
            width = int(video_stream.get("width", 0))
            height = int(video_stream.get("height", 0))
            codec = video_stream.get("codec_name", "unknown")

        return {
            "file_path": str(path),
            "file_size": int(fmt.get("size", 0)),
            "duration": duration,
            "fps": fps,
            "width": width,
            "height": height,
            "codec": codec,
            "audio_codec": audio_stream.get("codec_name") if audio_stream else None,
            "audio_channels": int(audio_stream.get("channels", 0)) if audio_stream else None,
            "audio_sample_rate": int(audio_stream.get("sample_rate", 0)) if audio_stream else None,
            "bit_rate": int(fmt.get("bit_rate", 0)),
            "format_name": fmt.get("format_name", "unknown"),
            "has_video": video_stream is not None,
            "has_audio": audio_stream is not None,
            "title": (fmt.get("tags") or {}).get("title"),
            "chapters": [],
        }

    def _parse_fps(self, stream: dict) -> float:
        for key in ("r_frame_rate", "avg_frame_rate"):
            val = stream.get(key, "0/1")
            parts = val.split("/")
            try:
                if len(parts) == 2 and float(parts[1]) != 0:
                    return float(parts[0]) / float(parts[1])
            except (ValueError, ZeroDivisionError):
                pass
        return 0.0
