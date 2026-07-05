"""Video metadata and information models."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class VideoFormat(str, Enum):
    """Supported video format identifiers."""

    MP4 = "mp4"
    MKV = "mkv"
    MOV = "mov"
    AVI = "avi"
    WEBM = "webm"
    FLV = "flv"
    M4V = "m4v"
    MPEG = "mpeg"
    OGG = "ogg"


class VideoMetadata(BaseModel):
    """Raw metadata extracted from the video file."""

    file_path: Path
    file_size: int = Field(..., description="File size in bytes")
    duration: float = Field(..., description="Duration in seconds")
    fps: float = Field(..., description="Frames per second")
    width: int = Field(..., description="Frame width in pixels")
    height: int = Field(..., description="Frame height in pixels")
    codec: str = Field(..., description="Video codec name")
    audio_codec: Optional[str] = Field(None, description="Audio codec name")
    audio_channels: Optional[int] = Field(None, description="Number of audio channels")
    audio_sample_rate: Optional[int] = Field(None, description="Audio sample rate in Hz")
    bit_rate: Optional[int] = Field(None, description="Video bit rate in bps")
    rotation: int = Field(0, description="Rotation in degrees")
    format_name: str = Field(..., description="Container format name")
    has_video: bool = True
    has_audio: bool = False
    title: Optional[str] = None
    creation_time: Optional[str] = None


class VideoInfo(BaseModel):
    """High-level video information after processing setup."""

    id: str = Field(..., description="Unique identifier for this video job")
    metadata: VideoMetadata
    total_frames: int = Field(..., description="Total number of frames")
    output_dir: Path = Field(..., description="Output markdirectory path")
    processed: bool = False
