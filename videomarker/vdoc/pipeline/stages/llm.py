"""LLM analysis stage — semantic understanding, chapters, summaries."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

from vdoc.models.document import Chapter
from vdoc.pipeline.base import PipelineContext, PipelineStage
from vdoc.prompts import render as render_prompt
from vdoc.providers.registry import ProviderRegistry

logger = logging.getLogger(__name__)


class LLMStage(PipelineStage):
    """Generate semantic understanding using LLM provider."""

    stage_name = "llm"

    async def execute(self, ctx: PipelineContext) -> PipelineContext:
        provider = await ProviderRegistry.get("llm")
        transcript_text = ctx.transcript.get("text", "")

        if not transcript_text:
            logger.warning("No transcript text for LLM analysis")
            return ctx

        prompt = render_prompt("llm/transcript_analysis.j2", transcript_text=transcript_text[:12000])
        system = render_prompt("llm/transcript_analysis_system.j2")

        result = await provider.complete(prompt, system=system)
        try:
            parsed = json.loads(result)
            ctx.llm_output = parsed
            # Derive chapters from scenes + LLM
            if parsed.get("chapters") and ctx.scenes:
                chapters = [Chapter(**ch) for ch in parsed["chapters"]]
                await self._assign_scenes_to_chapters(ctx, chapters)
                ctx.llm_output["chapters"] = [
                    {"title": ch.title, "start_time": ch.start_time, "end_time": ch.end_time, "scene_ids": ch.scene_ids}
                    for ch in chapters
                ]
        except json.JSONDecodeError:
            ctx.llm_output = {"summary": result}

        logger.info("LLM analysis complete")
        return ctx

    async def _assign_scenes_to_chapters(self, ctx: PipelineContext, chapters: List[Chapter]) -> None:
        """Assign scene IDs to chapters based on timestamps."""
        for ch in chapters:
            for scene in ctx.scenes:
                if scene["start_time"] >= ch.start_time and scene["end_time"] <= ch.end_time:
                    ch.scene_ids.append(scene["id"])

    async def validate(self, ctx: PipelineContext) -> bool:
        return ctx.config.get("llm_provider", "openai") != "none"
