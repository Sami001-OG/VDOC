"""OCR stage — extracts text from scene keyframes."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict

from vdoc.models.document import OCR, OCRBlock
from vdoc.pipeline.base import PipelineContext, PipelineStage
from vdoc.providers.registry import ProviderRegistry

logger = logging.getLogger(__name__)


class OCRStage(PipelineStage):
    """Extract text from keyframes using OCR provider."""

    stage_name = "ocr"

    async def execute(self, ctx: PipelineContext) -> PipelineContext:
        provider = await ProviderRegistry.get("ocr")
        frames_dir = Path(ctx.output_dir) / "frames"

        ocr_results: Dict[str, OCR] = {}
        if frames_dir.exists():
            keyframes = sorted(frames_dir.glob("*.jpg"))[:10]
            for kf in keyframes:
                raw = await provider.extract_text(kf)
                if isinstance(raw, dict):
                    blocks = [OCRBlock(**b) if isinstance(b, dict) else b for b in raw.get("blocks", [])]
                    ocr_results[kf.stem] = OCR(text=raw.get("text", ""), blocks=blocks, language=raw.get("language", "en"))
                elif isinstance(raw, OCR):
                    ocr_results[kf.stem] = raw

        ctx.ocr_results = ocr_results
        logger.info("OCR complete: %d frames processed", len(ocr_results))
        return ctx

    async def validate(self, ctx: PipelineContext) -> bool:
        return ctx.config.get("ocr_provider", "paddle") != "none"
