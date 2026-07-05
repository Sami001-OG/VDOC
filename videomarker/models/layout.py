"""Layout detection models."""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class LayoutType(str, Enum):
    """Types of layout elements that can be detected."""

    TITLE = "title"
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    LIST_ITEM = "list_item"
    TABLE = "table"
    TABLE_CELL = "table_cell"
    CODE_BLOCK = "code_block"
    CODE_LINE = "code_line"
    EQUATION = "equation"
    FIGURE = "figure"
    CAPTION = "caption"
    HEADER = "header"
    FOOTER = "footer"
    SIDEBAR = "sidebar"
    DIAGRAM = "diagram"
    CHART = "chart"
    TERMINAL = "terminal"
    SLIDE = "slide"
    SCREENSHOT = "screenshot"
    WINDOW = "window"
    UNKNOWN = "unknown"


class LayoutElement(BaseModel):
    """A single layout element detected in a frame."""

    layout_type: LayoutType
    text: str
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    x0: float
    y0: float
    x1: float
    y1: float
    children: List[LayoutElement] = Field(default_factory=list)

    def to_markdown(self, indent: int = 0) -> str:
        """Convert this layout element to Markdown."""
        prefix = "  " * indent
        if self.layout_type == LayoutType.TITLE:
            return f"{prefix}# {self.text}"
        elif self.layout_type == LayoutType.HEADING:
            return f"{prefix}## {self.text}"
        elif self.layout_type == LayoutType.CODE_BLOCK:
            return f"{prefix}```\n{self.text}\n```"
        elif self.layout_type == LayoutType.LIST_ITEM:
            return f"{prefix}- {self.text}"
        elif self.layout_type == LayoutType.EQUATION:
            return f"{prefix}$${self.text}$$"
        elif self.layout_type == LayoutType.TABLE:
            return self.text
        else:
            return f"{prefix}{self.text}"


class LayoutResult(BaseModel):
    """Complete layout detection result for a frame or scene."""

    elements: List[LayoutElement] = Field(default_factory=list)
    image_path: Optional[str] = None
    timestamp: float = 0.0

    def to_markdown(self) -> str:
        """Convert layout to Markdown."""
        lines = []
        for element in self.elements:
            lines.append(element.to_markdown())
        return "\n\n".join(lines)
