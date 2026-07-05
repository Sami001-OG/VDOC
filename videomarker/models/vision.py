"""Vision understanding models."""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ObjectDetected(BaseModel):
    """An object detected in a frame or scene."""

    label: str
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    x0: float
    y0: float
    x1: float
    y1: float


class SceneDescription(BaseModel):
    """Visual description of a scene."""

    summary: str = Field(..., description="Brief description of what's happening")
    detailed: str = Field(..., description="Detailed visual description")
    objects: List[ObjectDetected] = Field(default_factory=list)
    activities: List[str] = Field(default_factory=list)
    ui_components: List[str] = Field(default_factory=list)
    people_count: int = 0
    is_slide: bool = False
    is_code: bool = False
    is_diagram: bool = False
    is_screen_capture: bool = False
    tags: List[str] = Field(default_factory=list)


class VisionUnderstanding(BaseModel):
    """Complete vision understanding for a scene or frame."""

    description: SceneDescription
    timestamp: float = 0.0
    image_path: Optional[str] = None
