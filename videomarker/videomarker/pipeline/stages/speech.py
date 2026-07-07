"""Speech transcription stage."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from videomarker.pipeline.base import PipelineContext, PipelineStage
from videomarker.providers.registry import ProviderRegistry

logger = logging.getLogger(__name__)


class SpeechStage(PipelineStage):
    """Transcribe audio using the speech provider."""

    stage_name = "speech"

    async def execute(self, ctx: PipelineContext) -> PipelineContext:
        audio_path = Path(ctx.video_path).with_suffix(".wav")
        if not audio_path.exists():
            # Extract audio first
            video_provider = await ProviderRegistry.get("video")
            await video_provider.extract_audio(audio_path)

        provider = await ProviderRegistry.get("speech")
        language = ctx.config.get("language")
        result = await provider.transcribe(audio_path, language=language)
        ctx.transcript = result
        logger.info("Transcribed %d segments, language=%s", len(result.get("segments", [])), result.get("language"))
        return ctx

    async def validate(self, ctx: PipelineContext) -> bool:
        return ctx.config.get("speech_provider", "whisper") != "none"
