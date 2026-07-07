"""Render stage — converts pipeline context to VideoDocument and renders output."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from vdoc.models.document import Chapter, Concept, Entity, Timeline, VideoDocument
from vdoc.pipeline.base import PipelineContext, PipelineStage
from vdoc.renderers.base import BaseRenderer

logger = logging.getLogger(__name__)


class RenderStage(PipelineStage):
    """Produce final output in configured formats."""

    stage_name = "render"

    def __init__(self, output_formats: List[str] | None = None) -> None:
        super().__init__()
        self.output_formats = output_formats or ["markdirectory"]

    async def execute(self, ctx: PipelineContext) -> PipelineContext:
        output_dir = Path(ctx.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        doc = self._build_document(ctx)

        formats = ctx.config.get("export_formats", self.output_formats)
        for fmt in formats:
            renderer = self._get_renderer(fmt)
            if renderer:
                logger.info("Rendering format: %s", fmt)
                renderer.render(doc, output_dir)
            else:
                logger.warning("Unknown render format: %s", fmt)

        logger.info("Render complete: %s", output_dir)
        return ctx

    async def validate(self, ctx: PipelineContext) -> bool:
        return bool(ctx.output_dir)

    def _build_document(self, ctx: PipelineContext) -> VideoDocument:
        meta = ctx.video_metadata or {}

        chapters = ctx.llm_output.get("chapters", [])
        doc = VideoDocument(
            title=meta.get("title", ""),
            source_path=Path(ctx.video_path),
            duration=meta.get("duration", 0.0),
            fps=meta.get("fps", 0.0),
            resolution=(meta.get("width", 0), meta.get("height", 0)),
            codec=meta.get("codec", ""),
            file_size=meta.get("file_size", 0),
            created_at=datetime.now(),
            summary=ctx.llm_output.get("summary", ""),
            keywords=ctx.llm_output.get("keywords", []),
            concepts=[
                Concept(name=c["name"], description=c.get("description", ""), importance=c.get("importance", 0.0))
                for c in ctx.llm_output.get("concepts", [])
            ] if isinstance(ctx.llm_output.get("concepts"), list) else ctx.llm_output.get("concepts", []),
            entities=[
                Entity(name=e["name"], type=e.get("type", ""), confidence=e.get("confidence", 0.0))
                for e in ctx.llm_output.get("entities", [])
            ] if isinstance(ctx.llm_output.get("entities"), list) else ctx.llm_output.get("entities", []),
            timeline=Timeline(
                scenes=ctx.scenes,
                chapters=[Chapter(**ch) if isinstance(ch, dict) else ch for ch in (chapters or [])],
            ),
            transcript=ctx.transcript or Transcript(text="", segments=[]),
            embeddings=ctx.embeddings if isinstance(ctx.embeddings, list) else [],
            assets=[],
        )
        return doc

    def _get_renderer(self, fmt: str):
        from vdoc.renderers.registry import RendererRegistry
        return RendererRegistry.get(fmt)
