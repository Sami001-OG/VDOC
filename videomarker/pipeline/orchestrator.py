"""PipelineOrchestrator — restartable, stage-based pipeline executor."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from videomarker.pipeline.base import PipelineContext, PipelineStage

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Orchestrates the video processing pipeline.

    Supports:
        - Restarting from any failed/interrupted stage
        - Progress callbacks
        - Parallel stage execution
        - Graceful cancellation
    """

    def __init__(self) -> None:
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

        # Execute stages in order
        for i in range(start_idx, len(self._stage_order)):
            stage_name = self._stage_order[i]
            stage = self._stages[stage_name]

            if ctx.cancelled:
                logger.warning("Pipeline cancelled at stage: %s", stage_name)
                break

            logger.info("Pipeline stage: %s", stage_name)

            # Validate prerequisites
            if not await stage.validate(ctx):
                logger.warning("Stage %s prerequisites not met, skipping", stage_name)
                ctx.completed_stages.append(stage_name)
                continue

            try:
                ctx = await stage.execute(ctx)
                ctx.completed_stages.append(stage_name)
                self._notify_progress(stage_name, 1.0)
                self._save_checkpoint(ctx)
            except Exception as e:
                ctx.errors[stage_name] = str(e)
                logger.error("Stage %s failed: %s", stage_name, e)
                raise

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
            }
            self._checkpoint_path().write_text(json.dumps(data, indent=2))
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
