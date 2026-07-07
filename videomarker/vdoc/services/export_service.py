"""ExportService — export processed videos between formats."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from vdoc.renderers.html_renderer import HTMLRenderer
from vdoc.renderers.json_renderer import JSONRenderer
from vdoc.renderers.markdown import MarkdownRenderer


class ExportService:
    """Service for exporting processed videos between output formats."""

    RENDERERS = {
        "markdown": MarkdownRenderer,
        "json": JSONRenderer,
        "html": HTMLRenderer,
    }

    @staticmethod
    def export(input_dir: str, fmt: str, output_path: Optional[str] = None) -> str:
        """Export a MarkDirectory or processed output to another format."""
        from vdoc.models.document import VideoDocument

        renderer_cls = ExportService.RENDERERS.get(fmt)
        if not renderer_cls:
            raise ValueError(f"Unknown format: {fmt}. Available: {list(ExportService.RENDERERS)}")

        doc = VideoDocument.load(Path(input_dir))
        out = Path(output_path or f"{input_dir}.{fmt}")
        renderer_cls().render(doc, out.parent, filename=out.name)
        return str(out)
