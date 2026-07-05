"""OCR stage — extracts text from scene keyframes."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from videomarker.pipeline.base import PipelineContext, PipelineStage
from videomarker.providers.registry import ProviderRegistry

logger = logging.getLogger(__name__)


class OCRStage(PipelineStage):
    """Extract text from keyframes using OCR provider."""

    stage_name = "ocr"

    async def execute(self, ctx: PipelineContext) -> PipelineContext:
        provider = await ProviderRegistry.get("ocr")
        frames_dir = Path(ctx.output_dir) / "frames"

        ocr_results = {}
        if frames_dir.exists():
            keyframes = sorted(frames_dir.glob("*.jpg"))[:10]
            for kf in keyframes:
                result = await provider.extract_text(kf)
                if result.get("text", "").strip():
                    ocr_results[kf.stem] = result

        ctx.ocr_results = ocr_results
        logger.info("OCR complete: %d frames processed", len(ocr_results))
        return ctx

    async def validate(self, ctx: PipelineContext) -> bool:
        return ctx.config.get("ocr_provider", "paddle") != "none"
