"""Document model — the single source of truth for all video analysis.

Everything operates on these typed objects instead of raw strings or dicts.
Renderers convert these objects into Markdown, JSON, HTML, etc.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Scene:
    """A detected scene or shot in the video."""

    id: str
    number: int
    start_time: float
    end_time: float
    confidence: float = 1.0

    # Per-scene analysis results
    transcript: Optional[Transcript] = None
    ocr: Optional[OCR] = None
    caption: Optional[Caption] = None

    # Assets
    keyframe_path: Optional[Path] = None
    embedding: Optional[Embedding] = None

    # Metadata
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time


@dataclass
class Transcript:
    """Speech transcription output."""

    segments: List[Dict[str, Any]] = field(default_factory=list)
    text: str = ""
    language: Optional[str] = None

    @property
    def word_count(self) -> int:
        return len(self.text.split())


@dataclass
class OCR:
    """OCR text extracted from frames."""

    blocks: List[Dict[str, Any]] = field(default_factory=list)
    text: str = ""
    language: str = "en"


@dataclass
class Caption:
    """Visual description from vision model."""

    summary: str = ""
    detailed: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class Concept:
    """A key concept extracted from the video."""

    name: str
    description: str = ""
    importance: float = 0.5
    related_concepts: List[str] = field(default_factory=list)


@dataclass
class Entity:
    """A named entity (person, library, framework, etc.)."""

    name: str
    type: str = "concept"
    description: Optional[str] = None
    confidence: float = 0.5


@dataclass
class Embedding:
    """Vector embedding for a piece of content."""

    id: str
    vector: List[float]
    text: str
    source_type: str = ""
    timestamp: float = 0.0


@dataclass
class Timeline:
    """Structured timeline with scenes and chapters."""

    scenes: List[Scene] = field(default_factory=list)
    chapters: List[Dict[str, Any]] = field(default_factory=list)
    duration: float = 0.0


@dataclass
class Asset:
    """A file asset (keyframe, thumbnail, subtitle, etc.)."""

    path: Path
    type: str = "image"
    description: str = ""


@dataclass
class VideoDocument:
    """Top-level document — the complete analysis result for one video.

    This is the single source of truth. All renderers consume this.
    """

    # Identity
    title: str = ""
    source_path: Path = Path("")
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Video metadata
    duration: float = 0.0
    fps: float = 0.0
    resolution: tuple = (0, 0)
    codec: str = ""
    file_size: int = 0

    # Analysis results
    timeline: Timeline = field(default_factory=Timeline)
    transcript: Transcript = field(default_factory=Transcript)
    summary: str = ""
    keywords: List[str] = field(default_factory=list)

    # Knowledge
    concepts: List[Concept] = field(default_factory=list)
    entities: List[Entity] = field(default_factory=list)
    relationships: List[Dict[str, str]] = field(default_factory=list)

    # Search
    embeddings: List[Embedding] = field(default_factory=list)

    # Assets
    assets: List[Asset] = field(default_factory=list)
    output_dir: Optional[Path] = None

    @property
    def scene_count(self) -> int:
        return len(self.timeline.scenes)

    @property
    def chapter_count(self) -> int:
        return len(self.timeline.chapters)

    def get_scene(self, number: int) -> Optional[Scene]:
        for s in self.timeline.scenes:
            if s.number == number:
                return s
        return None
