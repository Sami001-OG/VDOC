"""Abstract speech recognition provider."""

from __future__ import annotations

from abc import abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from vdoc.providers.base import BaseProvider


class SpeechProvider(BaseProvider):
    """Speech-to-text transcription."""

    @abstractmethod
    async def transcribe(
        self, audio_path: Path, language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Transcribe audio file to text with timestamps.

        Returns dict with keys: segments, text, language, segments[].{start,end,text,words[]}
        """
        ...

    @abstractmethod
    async def transcribe_segment(
        self, audio_path: Path, start: float, end: float
    ) -> str:
        """Transcribe a specific time segment."""
        ...
