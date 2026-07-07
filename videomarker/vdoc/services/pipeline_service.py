"""PipelineService — business logic for pipeline execution."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional

from vdoc.config.manager import ConfigManager
from vdoc.pipeline.base import PipelineContext
from vdoc.pipeline.orchestrator import PipelineOrchestrator
from vdoc.pipeline.registry import StageRegistry


class PipelineService:
    """Service for building and running video processing pipelines."""

    @staticmethod
    def get_stage_map() -> Dict[str, Any]:
        return StageRegistry.list_stages()

    @staticmethod
    def build_pipeline(config: Dict[str, Any]) -> PipelineOrchestrator:
        """Build and return the processing pipeline."""
        pipeline = PipelineOrchestrator()
        default_order = ["video", "scene", "speech", "ocr", "vision", "llm", "embedding", "search_index", "render"]
        for name in default_order:
            cls = StageRegistry.get(name)
            if cls:
                pipeline.register_stage(cls())

        if config.get("output_dir"):
            pipeline.set_checkpoint_dir(Path(config["output_dir"]) / ".checkpoints")

        return pipeline

    @staticmethod
    def list_stages() -> List[str]:
        return list(StageRegistry.list_stages())

    @staticmethod
    def build_partial_pipeline(stage_names: List[str]) -> PipelineOrchestrator:
        """Build a pipeline with a subset of stages."""
        pipeline = PipelineOrchestrator()
        for name in stage_names:
            cls = StageRegistry.get(name)
            if cls:
                pipeline.register_stage(cls())
        return pipeline

    @staticmethod
    def create_context(
        video_path: str,
        output_dir: str,
        config: Dict[str, Any],
        completed_stages: Optional[List[str]] = None,
    ) -> PipelineContext:
        """Create a pipeline context with the given parameters."""
        ctx = PipelineContext()
        ctx.video_path = video_path
        ctx.output_dir = output_dir
        ctx.config = config
        if completed_stages:
            ctx.completed_stages = completed_stages
        return ctx

    @staticmethod
    def load_config(
        video: Path,
        output: Optional[Path],
        config_file: Optional[Path] = None,
        **cli_overrides: Any,
    ) -> Dict[str, Any]:
        """Load and resolve configuration."""
        cm = ConfigManager()
        if config_file:
            cm.load_yaml(config_file)
        filtered = {k: v for k, v in cli_overrides.items() if v is not None}
        cm.load_cli(
            video_path=str(video),
            output_dir=str(output or video.parent / f"{video.stem}.markdir"),
            **filtered,
        )
        return cm.resolve().model_dump()

    @staticmethod
    async def run_pipeline(
        pipeline: PipelineOrchestrator,
        ctx: PipelineContext,
        resume: bool = False,
    ) -> PipelineContext:
        """Execute the pipeline with provider setup."""
        ProviderRegistry.register_defaults()
        try:
            result = await pipeline.run(ctx, resume_from="video" if resume else None)
            return result
        finally:
            await ProviderRegistry.close_all()

    @staticmethod
    def run_sync(pipeline: PipelineOrchestrator, ctx: PipelineContext) -> PipelineContext:
        """Run pipeline synchronously (wraps async)."""
        return asyncio.run(PipelineService.run_pipeline(pipeline, ctx))

    @staticmethod
    def process_batch(video_paths: List[str], output_base: str, config: Dict[str, Any]) -> List[PipelineContext]:
        """Process multiple videos sequentially (#38 batch processing)."""
        results = []
        for v in video_paths:
            pipeline = PipelineService.build_pipeline(config)
            out_dir = str(Path(output_base) / Path(v).stem)
            ctx = PipelineService.create_context(v, out_dir, config)
            result = PipelineService.run_sync(pipeline, ctx)
            results.append(result)
        return results
