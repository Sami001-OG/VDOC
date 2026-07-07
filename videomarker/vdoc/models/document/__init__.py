"""Document model — the single source of truth for all video analysis data.

Everything operates on these objects. Renderers convert them to output.
"""

from vdoc.models.document.document import (
    Asset,
    Caption,
    Chapter,
    Concept,
    Embedding,
    Entity,
    Frame,
    OCR,
    OCRBlock,
    Relationship,
    Scene,
    Timeline,
    Transcript,
    TranscriptSegment,
    VideoDocument,
    Word,
)

__all__ = [
    "Asset",
    "Caption",
    "Chapter",
    "Concept",
    "Embedding",
    "Entity",
    "Frame",
    "OCR",
    "OCRBlock",
    "Relationship",
    "Scene",
    "Timeline",
    "Transcript",
    "TranscriptSegment",
    "VideoDocument",
    "Word",
]
