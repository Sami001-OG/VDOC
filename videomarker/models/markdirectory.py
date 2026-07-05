"""MarkDirectory output structure models."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SceneDir(BaseModel):
    """Structure of a single scene directory."""

    scene_number: int
    path: Path
    transcript_md: Optional[Path] = None
    summary_md: Optional[Path] = None
    caption_md: Optional[Path] = None
    ocr_md: Optional[Path] = None
    metadata_json: Optional[Path] = None
    keyframe_jpg: Optional[Path] = None
    embedding_bin: Optional[Path] = None


class Manifest(BaseModel):
    """Manifest describing the entire MarkDirectory."""

    videomarker_version: str = "0.1.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    video_file: str
    video_hash: Optional[str] = None
    duration: float = 0.0
    num_scenes: int = 0
    num_chapters: int = 0
    total_frames: int = 0
    has_transcript: bool = False
    has_ocr: bool = False
    has_vision: bool = False
    has_embeddings: bool = False
    has_knowledge_graph: bool = False
    pipeline_steps: List[str] = Field(default_factory=list)
    config_snapshot: Dict[str, object] = Field(default_factory=dict)


class MarkDirectory(BaseModel):
    """Complete MarkDirectory structure."""

    root: Path
    metadata_json: Path
    transcript_md: Path
    summary_md: Path
    chapters_md: Path
    timeline_json: Path
    keywords_md: Path
    entities_json: Path
    search_index_json: Path
    scenes: List[SceneDir]
    frames_dir: Path
    assets_dir: Path
    thumbnails_dir: Path
    subtitles_dir: Path
    embeddings_dir: Path
    manifest_json: Path
