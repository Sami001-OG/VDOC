"""Search and embedding models."""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Embedding(BaseModel):
    """A vector embedding with associated metadata."""

    id: str
    vector: List[float]
    text: str
    source_type: str = Field(..., description="e.g., scene, chapter, transcript, ocr")
    timestamp: float = 0.0
    metadata: Dict[str, object] = Field(default_factory=dict)


class SearchResult(BaseModel):
    """A single search result."""

    id: str
    text: str
    score: float = Field(..., ge=0.0, le=1.0)
    source_type: str
    timestamp: float = 0.0
    scene_number: Optional[int] = None
    chapter_title: Optional[str] = None
    preview: Optional[str] = None


class SearchIndex(BaseModel):
    """Search index metadata."""

    version: int = 1
    model_name: str = "BAAI/bge-large-en-v1.5"
    dimension: int = 1024
    num_embeddings: int = 0
    index_path: Optional[str] = None
