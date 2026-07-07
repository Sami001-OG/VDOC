"""Video providers — extract metadata, frames, and audio."""

from vdoc.providers.video.base import VideoProvider
from vdoc.providers.video.ffmpeg import FFmpegVideoProvider

__all__ = ["VideoProvider", "FFmpegVideoProvider"]
