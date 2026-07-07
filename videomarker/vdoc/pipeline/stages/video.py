"""Video loading and metadata extraction stage."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from vdoc.pipeline.base import PipelineContext, PipelineStage
from vdoc.providers.registry import ProviderRegistry

logger = logging.getLogger(__name__)


class VideoStage(PipelineStage):
    """Load video file and extract metadata."""

    stage_name = "video"

    async def execute(self, ctx: PipelineContext) -> PipelineContext:
        video_path = Path(ctx.video_path)
        provider = await ProviderRegistry.get("video")
        metadata = await provider.load(video_path)
        ctx.video_metadata = metadata
        return ctx

    async def validate(self, ctx: PipelineContext) -> bool:
        return bool(ctx.video_path) and Path(ctx.video_path).exists()
