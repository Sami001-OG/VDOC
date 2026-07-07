"""Speech transcription stage."""

from __future__ import annotations

import logging
from pathlib import Path

from vdoc.models.document import Transcript, TranscriptSegment, Word
from vdoc.pipeline.base import PipelineContext, PipelineStage
from vdoc.providers.registry import ProviderRegistry

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
        raw = await provider.transcribe(audio_path, language=language)
        if isinstance(raw, dict):
            segments = [
                TranscriptSegment(
                    start=s.get("start", 0),
                    end=s.get("end", 0),
                    text=s.get("text", ""),
                    confidence=s.get("confidence", 0),
                    words=[Word(**w) if isinstance(w, dict) else w for w in s.get("words", [])],
                )
                for s in raw.get("segments", [])
            ]
            ctx.transcript = Transcript(
                text=raw.get("text", ""),
                segments=segments,
                language=raw.get("language"),
            )
        else:
            ctx.transcript = raw
        logger.info("Transcribed %d segments, language=%s", len(ctx.transcript.segments) if ctx.transcript else 0,
                     ctx.transcript.language if ctx.transcript else None)
        return ctx

    async def validate(self, ctx: PipelineContext) -> bool:
        return ctx.config.get("speech_provider", "whisper") != "none"
