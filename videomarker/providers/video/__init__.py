"""Video providers — extract metadata, frames, and audio."""

from videomarker.providers.video.base import VideoProvider
from videomarker.providers.video.ffmpeg import FFmpegVideoProvider

__all__ = ["VideoProvider", "FFmpegVideoProvider"]
