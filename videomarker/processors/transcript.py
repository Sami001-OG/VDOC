"""Transcript processor — converts audio to text with speaker diarization."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from videomarker.core.processor import Processor
from videomarker.core.plugin import processor
from videomarker.models.transcript import (
    Speaker,
    Transcript,
    TranscriptSegment,
    WordTimestamp,
)

logger = logging.getLogger(__name__)


@processor("transcript", dependencies=["audio_extract"], priority=10)
class TranscriptProcessor(Processor):
    """Generate transcription from extracted audio using Whisper."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._model = None

    def process(self, context: Any) -> None:
        """Run transcription on the extracted audio."""
        audio_path = context.data.get("audio_path")
        if not audio_path or not Path(audio_path).exists():
            logger.warning("No audio file found, skipping transcription")
            return

        logger.info("Starting transcription: %s", audio_path)
        transcript = self._transcribe(Path(audio_path))
        context.data["transcript"] = transcript
        logger.info(
            "Transcription complete: %d segments, language=%s",
            len(transcript.segments),
            transcript.language,
        )

    def _transcribe(self, audio_path: Path) -> Transcript:
        """Transcribe audio using faster-whisper if available, else placeholder."""
        transcript = Transcript()

        try:
            from faster_whisper import WhisperModel

            model_size = self.settings.whisper_model if self.settings else "base"
            device = self.settings.whisper_device if self.settings else "cpu"
            compute_type = self.settings.whisper_compute_type if self.settings else "float16"

            self._model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type,
            )

            segments, info = self._model.transcribe(
                str(audio_path),
                language=self.settings.language if self.settings else None,
                beam_size=5,
                word_timestamps=True,
                vad_filter=True,
            )

            transcript.language = info.language
            for seg in segments:
                words = []
                if seg.words:
                    for w in seg.words:
                        words.append(
                            WordTimestamp(
                                word=w.word,
                                start=w.start,
                                end=w.end,
                                confidence=w.probability if hasattr(w, 'probability') else 0.0,
                            )
                        )

                segment = TranscriptSegment(
                    start=seg.start,
                    end=seg.end,
                    text=seg.text.strip(),
                    confidence=seg.avg_logprob if hasattr(seg, 'avg_logprob') else 0.0,
                    words=words,
                    language=info.language,
                )
                transcript.segments.append(segment)

            transcript.full_text = " ".join(s.text for s in transcript.segments)

        except ImportError:
            logger.warning(
                "faster-whisper not installed. Install with: pip install videomarker[audio]"
            )
            transcript = self._fallback_transcript(audio_path)

        return transcript

    def _fallback_transcript(self, audio_path: Path) -> Transcript:
        """Create a minimal transcript when faster-whisper is unavailable."""
        transcript = Transcript()
        transcript.language = "unknown"
        # Try using FFmpeg/ffprobe to get audio duration
        try:
            import subprocess
            import json as j
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                str(audio_path),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = j.loads(result.stdout)
            duration = float(data.get("format", {}).get("duration", 0))
        except Exception:
            duration = 0

        transcript.segments.append(
            TranscriptSegment(
                start=0.0,
                end=duration,
                text="[Transcription requires faster-whisper]",
                confidence=0.0,
            )
        )
        return transcript


@processor("diarize", dependencies=["transcript"], priority=15)
class DiarizationProcessor(Processor):
    """Perform speaker diarization on the transcript."""

    def process(self, context: Any) -> None:
        transcript: Optional[Transcript] = context.data.get("transcript")
        if not transcript:
            return

        # Simple diarization: group segments by time gaps and assign speaker IDs
        speakers: Dict[str, Speaker] = {}
        speaker_counter = 0
        current_speaker: Optional[str] = None
        gap_threshold = 1.5

        for seg in transcript.segments:
            if current_speaker is None:
                speaker_counter += 1
                current_speaker = f"SPEAKER_{speaker_counter:02d}"
            elif (seg.start - transcript.segments[transcript.segments.index(seg) - 1].end) > gap_threshold:
                speaker_counter += 1
                current_speaker = f"SPEAKER_{speaker_counter:02d}"

            seg.speaker_id = current_speaker
            if current_speaker not in speakers:
                speakers[current_speaker] = Speaker(speaker_id=current_speaker)
            speakers[current_speaker].segments.append(seg.text)

        transcript.speakers = list(speakers.values())
        context.data["transcript"] = transcript
        logger.info("Diarization complete: %d speakers detected", len(speakers))
