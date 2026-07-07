"""BenchmarkService — performance benchmarks for pipeline stages."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

from vdoc.pipeline.orchestrator import PipelineOrchestrator
from vdoc.pipeline.stages import (
    VideoStage,
    SceneDetectionStage,
    SpeechStage,
    OCRStage,
    VisionStage,
    LLMStage,
    EmbeddingStage,
    SearchIndexStage,
    RenderStage,
)
from vdoc.services.pipeline_service import PipelineService
from vdoc.providers.registry import ProviderRegistry


class BenchmarkService:
    """Run timing benchmarks for individual pipeline stages."""

    STAGES = {
        "video": VideoStage,
        "scene": SceneDetectionStage,
        "speech": SpeechStage,
        "ocr": OCRStage,
        "vision": VisionStage,
        "llm": LLMStage,
        "embedding": EmbeddingStage,
        "search": SearchIndexStage,
        "render": RenderStage,
    }

    @staticmethod
    def run(video_path: str) -> List[Tuple[str, float]]:
        """Run benchmarks on each stage and return (name, duration_seconds) pairs."""
        results: List[Tuple[str, float]] = []
        video = Path(video_path)
        output_dir = str(video.parent / f"{video.stem}_benchmark")

        ProviderRegistry.register_defaults()

        for name, stage_cls in BenchmarkService.STAGES.items():
            pipeline = PipelineOrchestrator()
            pipeline.register_stage(stage_cls())
            ctx = PipelineService.create_context(video_path, output_dir, {})
            start = time.monotonic()
            try:
                PipelineService.run_sync(pipeline, ctx)
            except Exception:
                pass
            elapsed = time.monotonic() - start
            results.append((name, elapsed))

        return results
