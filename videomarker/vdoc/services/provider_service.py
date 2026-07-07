"""ProviderService — manages provider lifecycle for CLI and API."""

from __future__ import annotations

from typing import Any, Dict, Optional

from vdoc.providers.registry import ProviderRegistry


class ProviderService:
    """Business logic for provider registration and lifecycle."""

    @staticmethod
    def register_defaults(config: Optional[Dict[str, Any]] = None) -> None:
        """Register all default providers based on configuration."""
        if not ProviderRegistry.is_registered("video"):
            from vdoc.providers.video.ffmpeg import FFmpegVideoProvider
            ProviderRegistry.register("video", FFmpegVideoProvider)

        if not ProviderRegistry.is_registered("llm"):
            from vdoc.providers.llm.openai_compatible import OpenAICompatibleProvider
            ProviderRegistry.register("llm", OpenAICompatibleProvider)

        if not ProviderRegistry.is_registered("speech"):
            from vdoc.providers.speech.whisper import WhisperSpeechProvider
            ProviderRegistry.register("speech", WhisperSpeechProvider)

        if not ProviderRegistry.is_registered("vision"):
            from vdoc.providers.vision.openai_vision import OpenAIVisionProvider
            ProviderRegistry.register("vision", OpenAIVisionProvider)

        if not ProviderRegistry.is_registered("ocr"):
            from vdoc.providers.ocr.paddle import PaddleOCRProvider
            ProviderRegistry.register("ocr", PaddleOCRProvider)

        if not ProviderRegistry.is_registered("embedding"):
            from vdoc.providers.embedding.sentence import SentenceEmbeddingProvider
            ProviderRegistry.register("embedding", SentenceEmbeddingProvider)

    @staticmethod
    async def close_all() -> None:
        await ProviderRegistry.close_all()

    @staticmethod
    def is_registered(name: str) -> bool:
        return ProviderRegistry.is_registered(name)

    @staticmethod
    def list_available() -> Dict[str, str]:
        return ProviderRegistry.list_available()
