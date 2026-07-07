"""Document model — the single source of truth for all video analysis data.

Everything operates on these objects. Renderers convert them to output.
"""

from videomarker.models.document.document import (
    VideoDocument,
    Timeline,
    Scene,
    Transcript,
    Caption,
    OCR,
    Concept,
    Entity,
    Asset,
    Embedding,
)

__all__ = [
    "VideoDocument",
    "Timeline",
    "Scene",
    "Transcript",
    "Caption",
    "OCR",
    "Concept",
    "Entity",
    "Asset",
    "Embedding",
]
