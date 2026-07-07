"""Whisper speech-to-text provider via faster-whisper."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from videomarker.providers.base import ProviderConfig, ProviderStatus
from videomarker.providers.speech.base import SpeechProvider

logger = logging.getLogger(__name__)


class WhisperSpeechProvider(SpeechProvider):
    """Speech recognition using faster-whisper."""

    def __init__(self, config: Optional[ProviderConfig] = None) -> None:
        super().__init__(config)
        self._model = None

    async def initialize(self) -> None:
        try:
            from faster_whisper import WhisperModel

            model_size = self.config.model or "base"
            device = self.config.device
            compute_type = "float16" if device == "cuda" else "int8"

            self._model = WhisperModel(model_size, device=device, compute_type=compute_type)
            self.status = ProviderStatus.READY
            logger.info("Whisper model loaded: %s (%s)", model_size, device)
        except ImportError:
            logger.warning("faster-whisper not installed. Install: pip install videomarker[audio]")
            raise

    async def transcribe(
        self, audio_path: Path, language: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self._model:
            raise RuntimeError("Provider not initialized")

        segments, info = self._model.transcribe(
            str(audio_path),
            language=language,
            beam_size=5,
            word_timestamps=True,
            vad_filter=True,
        )

        result = {
            "language": info.language,
            "duration": info.duration,
            "segments": [],
            "text": "",
        }

        text_parts = []
        for seg in segments:
            seg_dict = {
                "start": seg.start,
                "end": seg.end,
                "text": seg.text.strip(),
                "confidence": getattr(seg, "avg_logprob", 0),
                "words": [],
            }
            if seg.words:
                seg_dict["words"] = [
                    {"word": w.word, "start": w.start, "end": w.end, "probability": getattr(w, "probability", 0)}
                    for w in seg.words
                ]
            result["segments"].append(seg_dict)
            text_parts.append(seg.text.strip())

        result["text"] = " ".join(text_parts)
        return result

    async def transcribe_segment(
        self, audio_path: Path, start: float, end: float
    ) -> str:
        if not self._model:
            raise RuntimeError("Provider not initialized")

        segments, _ = self._model.transcribe(
            str(audio_path),
            vad_filter=True,
            offset_t=start,
            duration_t=end - start,
        )
        return " ".join(seg.text.strip() for seg in segments)
