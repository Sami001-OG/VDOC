"""Render stage — converts pipeline context to VideoDocument and renders output."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from videomarker.models.document import (
    Asset,
    Caption,
    Concept,
    Embedding,
    Entity,
    OCR,
    Scene,
    Timeline,
    Transcript,
    VideoDocument,
)
from videomarker.pipeline.base import PipelineContext, PipelineStage
from videomarker.renderers.html_renderer import HTMLRenderer
from videomarker.renderers.json_renderer import JSONRenderer
from videomarker.renderers.markdown import MarkdownRenderer
from videomarker.renderers.markdirectory import MarkDirectoryRenderer

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

        scenes = []
        for s in ctx.scenes:
            scene = Scene(
                id=s.get("id", ""),
                number=s.get("number", 0),
                start_time=s.get("start_time", 0.0),
                end_time=s.get("end_time", 0.0),
                description=s.get("description", ""),
                transcript=Transcript(
                    text=s.get("transcript", {}).get("text", ""),
                    segments=s.get("transcript", {}).get("segments", []),
                ) if s.get("transcript") else None,
                ocr=OCR(text=s.get("ocr", {}).get("text", "")) if s.get("ocr") else None,
                caption=Caption(
                    summary=s.get("caption", {}).get("summary", ""),
                    detailed=s.get("caption", {}).get("detailed", ""),
                    tags=s.get("caption", {}).get("tags", []),
                ) if s.get("caption") else None,
                embedding=Embedding(
                    vector=s["embedding"]["vector"],
                    model=s["embedding"].get("model", ""),
                ) if s.get("embedding") else None,
                keyframe_path=Path(s["keyframe_path"]) if s.get("keyframe_path") else None,
            )
            scenes.append(scene)

        transcript = Transcript(
            text=ctx.transcript.get("text", ""),
            segments=ctx.transcript.get("segments", []),
        ) if ctx.transcript else Transcript(text="", segments=[])

        doc = VideoDocument(
            title=meta.get("title", ""),
            source_path=Path(ctx.video_path),
            duration=meta.get("duration", 0.0),
            fps=meta.get("fps", 0.0),
            resolution=(meta.get("width", 0), meta.get("height", 0)),
            codec=meta.get("codec", ""),
            file_size=meta.get("file_size", 0),
            scene_count=len(scenes),
            chapter_count=len(ctx.timeline.get("chapters", [])),
            created_at=datetime.now(),
            summary=ctx.llm_output.get("summary", ""),
            keywords=ctx.llm_output.get("keywords", []),
            concepts=[
                Concept(name=c["name"], description=c.get("description", ""), importance=c.get("importance", 0.0))
                for c in ctx.llm_output.get("concepts", [])
            ],
            entities=[
                Entity(name=e["name"], type=e.get("type", ""), confidence=e.get("confidence", 0.0))
                for e in ctx.llm_output.get("entities", [])
            ],
            timeline=Timeline(
                scenes=scenes,
                chapters=meta.get("chapters", []),
            ),
            transcript=transcript,
            embeddings=ctx.embeddings,
            assets=[],
        )
        return doc

    def _get_renderer(self, fmt: str):
        renderers = {
            "markdirectory": MarkDirectoryRenderer(),
            "json": JSONRenderer(),
            "markdown": MarkdownRenderer(),
            "html": HTMLRenderer(),
        }
        return renderers.get(fmt)
