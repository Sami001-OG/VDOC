"""Time segments, scenes, chapters, and timeline models."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SegmentType(str, Enum):
    """Types of time segments detected."""

    SCENE = "scene"
    CHAPTER = "chapter"
    SHOT = "shot"
    PAUSE = "pause"
    SLIDE_CHANGE = "slide_change"
    CAMERA_SWITCH = "camera_switch"
    TRANSITION = "transition"


class TimeSegment(BaseModel):
    """A generic time segment with start and end times."""

    id: str = Field(..., description="Unique segment identifier")
    segment_type: SegmentType
    start_time: float = Field(..., description="Start time in seconds")
    end_time: float = Field(..., description="End time in seconds")
    confidence: float = Field(0.0, ge=0.0, le=1.0)

    @property
    def duration(self) -> float:
        """Duration of the segment in seconds."""
        return self.end_time - self.start_time

    @property
    def start_timestamp(self) -> str:
        """Human-readable start timestamp (HH:MM:SS.mmm)."""
        return _format_timestamp(self.start_time)

    @property
    def end_timestamp(self) -> str:
        """Human-readable end timestamp (HH:MM:SS.mmm)."""
        return _format_timestamp(self.end_time)


class Scene(TimeSegment):
    """A detected scene with additional metadata."""

    scene_number: int = Field(..., description="Sequential scene number")
    keyframe_path: Optional[Path] = Field(None, description="Path to representative keyframe")
    description: Optional[str] = Field(None, description="Scene description from vision model")
    transcript_path: Optional[Path] = None
    summary_path: Optional[Path] = None
    ocr_path: Optional[Path] = None
    embedding_path: Optional[Path] = None
    metadata: Dict[str, object] = Field(default_factory=dict)


class Chapter(TimeSegment):
    """A chapter grouping multiple scenes."""

    chapter_number: int = Field(..., description="Sequential chapter number")
    title: str = Field(..., description="Chapter title")
    summary: Optional[str] = None
    scene_ids: List[str] = Field(default_factory=list, description="Scene IDs in this chapter")


class Timeline(BaseModel):
    """Complete timeline of the video."""

    scenes: List[Scene] = Field(default_factory=list)
    chapters: List[Chapter] = Field(default_factory=list)
    duration: float = 0.0

    def add_scene(self, scene: Scene) -> None:
        self.scenes.append(scene)

    def add_chapter(self, chapter: Chapter) -> None:
        self.chapters.append(chapter)


def _format_timestamp(seconds: float) -> str:
    """Format seconds to HH:MM:SS.mmm."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
