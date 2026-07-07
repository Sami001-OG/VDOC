"""LLM analysis stage — semantic understanding, chapters, summaries."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict

from videomarker.pipeline.base import PipelineContext, PipelineStage
from videomarker.providers.registry import ProviderRegistry

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

        prompt = (
            "Analyze this video transcript. Extract:\n"
            "1. Overall summary (2-3 sentences)\n"
            "2. Chapter titles with timestamps\n"
            "3. Key concepts and definitions\n"
            "4. Important technical terms\n\n"
            f"Transcript:\n{transcript_text[:12000]}\n\n"
            "Return JSON with keys: summary, chapters (list of {title, start_time, end_time}), "
            "concepts (list of {name, description}), technical_terms (object)"
        )

        result = await provider.complete(prompt, system="You are a video analysis assistant. Return only valid JSON.")
        try:
            parsed = json.loads(result)
            ctx.llm_output = parsed
            # Derive chapters from scenes + LLM
            if parsed.get("chapters") and ctx.scenes:
                await self._assign_chapters(ctx, parsed["chapters"])
        except json.JSONDecodeError:
            ctx.llm_output = {"summary": result}

        logger.info("LLM analysis complete")
        return ctx

    async def _assign_chapters(self, ctx: PipelineContext, chapters: list) -> None:
        """Assign chapters to scenes."""
        for ch in chapters:
            ch["scene_ids"] = []
            for scene in ctx.scenes:
                if scene["start_time"] >= ch.get("start_time", 0) and scene["end_time"] <= ch.get("end_time", float("inf")):
                    ch["scene_ids"].append(scene["id"])

    async def validate(self, ctx: PipelineContext) -> bool:
        return ctx.config.get("llm_provider", "openai") != "none"
