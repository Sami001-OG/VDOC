"""Vision analysis stage."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

from vdoc.pipeline.base import PipelineContext, PipelineStage
from vdoc.providers.registry import ProviderRegistry

logger = logging.getLogger(__name__)


class VisionStage(PipelineStage):
    """Analyze scene keyframes with vision provider."""

    stage_name = "vision"

    async def execute(self, ctx: PipelineContext) -> PipelineContext:
        provider = await ProviderRegistry.get("vision")
        frames_dir = Path(ctx.output_dir) / "frames"

        vision_results: Dict[str, Any] = {}
        scenes_with_frames = self._get_keyframes(ctx, frames_dir)

        for scene_id, kf_path in scenes_with_frames:
            result = await provider.describe(kf_path)
            vision_results[scene_id] = result

        ctx.vision_results = vision_results
        logger.info("Vision analysis: %d scenes", len(vision_results))
        return ctx

    def _get_keyframes(self, ctx: PipelineContext, frames_dir: Path) -> list:
        """Match scenes to keyframe images."""
        pairs = []
        for scene in ctx.scenes:
            mid = (scene["start_time"] + scene["end_time"]) / 2
            frame_name = f"frame_{mid:.3f}s.jpg"
            kf = frames_dir / frame_name
            if kf.exists():
                pairs.append((scene["id"], kf))
        return pairs

    async def validate(self, ctx: PipelineContext) -> bool:
        return ctx.config.get("vision_provider", "openai") != "none"
