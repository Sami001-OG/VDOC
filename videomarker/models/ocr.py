"""OCR result models."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class OCRWord(BaseModel):
    """A single word from OCR."""

    text: str
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    x0: float
    y0: float
    x1: float
    y1: float


class OCRLine(BaseModel):
    """A line of text from OCR."""

    text: str
    words: List[OCRWord] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    x0: float
    y0: float
    x1: float
    y1: float


class OCRBlock(BaseModel):
    """A block of text from OCR."""

    text: str
    lines: List[OCRLine] = Field(default_factory=list)
    block_type: str = "text"
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    x0: float
    y0: float
    x1: float
    y1: float


class OCRResult(BaseModel):
    """OCR results from a single frame or scene keyframe."""

    blocks: List[OCRBlock] = Field(default_factory=list)
    text: Optional[str] = None
    image_path: Optional[str] = None
    timestamp: float = 0.0

    @property
    def full_text(self) -> str:
        """Get the full concatenated text."""
        if self.text:
            return self.text
        return "\n".join(block.text for block in self.blocks)
