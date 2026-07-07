"""PipelineOrchestrator — restartable, stage-based pipeline executor with parallel support."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

from vdoc.events.bus import EventBus, PipelineEvent, get_bus
from vdoc.pipeline.base import PipelineContext, PipelineStage

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Orchestrates the video processing pipeline.

    Supports:
        - Restarting from any failed/interrupted stage
        - Progress callbacks via EventBus
        - Parallel stage execution (stages with same parallel_group)
        - Graceful cancellation
        - Per-stage timing metrics
    """

    def __init__(self, event_bus: Optional[EventBus] = None) -> None:
        self._bus = event_bus or get_bus()
        self._stages: Dict[str, PipelineStage] = {}
        self._stage_order: List[str] = []
        self._progress_callbacks: List[Callable[[str, float], None]] = []
        self._checkpoint_dir: Optional[Path] = None

    def register_stage(self, stage: PipelineStage) -> PipelineOrchestrator:
        """Register a pipeline stage."""
        if not stage.stage_name:
            raise ValueError("PipelineStage must have stage_name set")
        self._stages[stage.stage_name] = stage
        self._stage_order.append(stage.stage_name)
        return self

    def set_checkpoint_dir(self, path: Path) -> PipelineOrchestrator:
        """Set directory for checkpoint files (supports resume)."""
        self._checkpoint_dir = path
        path.mkdir(parents=True, exist_ok=True)
        return self

    def on_progress(self, callback: Callable[[str, float], None]) -> PipelineOrchestrator:
        """Register a progress callback."""
        self._progress_callbacks.append(callback)
        return self

    async def run(
        self,
        ctx: Optional[PipelineContext] = None,
        resume_from: Optional[str] = None,
    ) -> PipelineContext:
        """Execute the pipeline from start or resume from a specific stage.

        Args:
            ctx: Initial pipeline context. Created fresh if None.
            resume_from: Stage name to resume from. If None, resumes from
                         the last incomplete stage (if checkpoints exist)
                         or starts from the beginning.

        Returns:
            Completed pipeline context.
        """
        ctx = ctx or PipelineContext()

        # Check for existing checkpoint to resume from
        if resume_from is None and self._checkpoint_dir:
            ctx = self._load_checkpoint(ctx)

        # Determine starting stage
        start_idx = 0
        if resume_from:
            if resume_from not in self._stage_order:
                raise ValueError(f"Unknown stage: {resume_from}")
            start_idx = self._stage_order.index(resume_from)
        elif ctx.completed_stages:
            last = ctx.last_completed
            if last and last in self._stage_order:
                start_idx = self._stage_order.index(last) + 1

        # Execute stages in order, running parallel groups concurrently
        i = start_idx
        while i < len(self._stage_order):
            if ctx.cancelled:
                logger.warning("Pipeline cancelled")
                break

            # Collect stages in the same parallel group
            parallel_group = self._stage_order[i]
            batch: List[str] = []
            while i < len(self._stage_order):
                si = self._stages[self._stage_order[i]]
                if not batch or si.parallel_group == parallel_group:
                    batch.append(self._stage_order[i])
                    i += 1
                else:
                    break

            if len(batch) == 1:
                ctx = await self._execute_single(batch[0], ctx)
            else:
                ctx = await self._execute_parallel(batch, ctx)

        return ctx

    async def _execute_single(self, stage_name: str, ctx: PipelineContext) -> PipelineContext:
        stage = self._stages[stage_name]
        self._bus.emit(PipelineEvent(name="stage.started", stage=stage_name))
        if not await stage.validate(ctx):
            logger.warning("Stage %s prerequisites not met, skipping", stage_name)
            ctx.completed_stages.append(stage_name)
            self._bus.emit(PipelineEvent(name="stage.skipped", stage=stage_name))
            return ctx
        return await self._run_and_record(stage_name, stage, ctx)

    async def _execute_parallel(self, batch: List[str], ctx: PipelineContext) -> PipelineContext:
        for name in batch:
            self._bus.emit(PipelineEvent(name="stage.started", stage=name))
        tasks = []
        for name in batch:
            stage = self._stages[name]
            tasks.append(self._run_and_record(name, stage, ctx))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for name, result in zip(batch, results):
            if isinstance(result, Exception):
                ctx.errors[name] = str(result)
                logger.error("Stage %s failed: %s", name, result)
                self._bus.emit(PipelineEvent(name="stage.failed", stage=name, data={"error": str(result)}))
        return ctx

    async def _run_and_record(self, name: str, stage: PipelineStage, ctx: PipelineContext) -> PipelineContext:
        start = time.monotonic()
        try:
            ctx = await stage.execute(ctx)
            elapsed = time.monotonic() - start
            ctx.stage_timing[name] = elapsed
            if name not in ctx.completed_stages:
                ctx.completed_stages.append(name)
            self._notify_progress(name, 1.0)
            self._save_checkpoint(ctx)
            self._bus.emit(PipelineEvent(name="stage.completed", stage=name, data={"timing": elapsed}))
        except Exception as e:
            ctx.stage_timing[name] = time.monotonic() - start
            raise
        return ctx

        return ctx

    def _notify_progress(self, stage: str, progress: float) -> None:
        for cb in self._progress_callbacks:
            try:
                cb(stage, progress)
            except Exception as e:
                logger.warning("Progress callback error: %s", e)

    def _checkpoint_path(self) -> Path:
        if not self._checkpoint_dir:
            raise RuntimeError("Checkpoint directory not set")
        return self._checkpoint_dir / "pipeline_checkpoint.json"

    def _save_checkpoint(self, ctx: PipelineContext) -> None:
        if not self._checkpoint_dir:
            return
        try:
            data = {
                "completed_stages": ctx.completed_stages,
                "errors": ctx.errors,
                "video_path": ctx.video_path,
                "output_dir": ctx.output_dir,
                "config": ctx.config,
                "video_metadata": ctx.video_metadata,
                "scenes": ctx.scenes,
                "transcript": ctx._serialize(ctx.transcript),
                "ocr_results": ctx._serialize(ctx.ocr_results),
                "vision_results": ctx._serialize(ctx.vision_results),
                "llm_output": ctx._serialize(ctx.llm_output),
                "embeddings": ctx._serialize(ctx.embeddings),
                "knowledge_graph": ctx._serialize(ctx.knowledge_graph),
                "search_index": ctx._serialize(ctx.search_index),
            }
            self._checkpoint_path().write_text(json.dumps(data, indent=2, default=str))
        except Exception as e:
            logger.warning("Failed to save checkpoint: %s", e)

    def _load_checkpoint(self, ctx: PipelineContext) -> PipelineContext:
        if not self._checkpoint_dir:
            return ctx
        cp = self._checkpoint_path()
        if not cp.exists():
            return ctx
        try:
            data = json.loads(cp.read_text())
            ctx.completed_stages = data.get("completed_stages", [])
            ctx.errors = data.get("errors", {})
            ctx.video_path = data.get("video_path", ctx.video_path)
            ctx.output_dir = data.get("output_dir", ctx.output_dir)
            ctx.config = data.get("config", ctx.config)
            ctx.video_metadata = data.get("video_metadata", ctx.video_metadata)
            ctx.scenes = data.get("scenes", ctx.scenes)
            ctx.transcript = data.get("transcript", ctx.transcript)
            ctx.ocr_results = data.get("ocr_results", ctx.ocr_results)
            ctx.vision_results = data.get("vision_results", ctx.vision_results)
            ctx.llm_output = data.get("llm_output", ctx.llm_output)
            ctx.embeddings = data.get("embeddings", ctx.embeddings)
            ctx.knowledge_graph = data.get("knowledge_graph", ctx.knowledge_graph)
            ctx.search_index = data.get("search_index", ctx.search_index)
            logger.info("Resumed from checkpoint: %d stages completed", len(ctx.completed_stages))
        except Exception as e:
            logger.warning("Failed to load checkpoint: %s", e)
        return ctx

    def clear_checkpoint(self) -> None:
        if self._checkpoint_dir:
            cp = self._checkpoint_path()
            if cp.exists():
                cp.unlink()

    @staticmethod
    def _make_context() -> PipelineContext:
        return PipelineContext()
