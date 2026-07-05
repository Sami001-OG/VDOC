"""Transcript and speech recognition models."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class WordTimestamp(BaseModel):
    """A single word with timing information."""

    word: str
    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")
    confidence: float = Field(0.0, ge=0.0, le=1.0)


class Speaker(BaseModel):
    """A detected speaker."""

    speaker_id: str
    name: Optional[str] = None
    segments: List[str] = Field(default_factory=list)


class TranscriptSegment(BaseModel):
    """A segment of the transcript with speaker and timing."""

    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")
    text: str
    speaker_id: Optional[str] = None
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    words: List[WordTimestamp] = Field(default_factory=list)
    language: Optional[str] = None


class Transcript(BaseModel):
    """Complete transcript of the video."""

    segments: List[TranscriptSegment] = Field(default_factory=list)
    speakers: List[Speaker] = Field(default_factory=list)
    language: Optional[str] = None
    full_text: Optional[str] = None
