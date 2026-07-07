"""Scene detection stage."""

from __future__ import annotations

import logging
from typing import List

from scenedetect import ContentDetector, open_video, SceneManager

from vdoc.models.document import Scene
from vdoc.pipeline.base import PipelineContext, PipelineStage

logger = logging.getLogger(__name__)


class SceneDetectionStage(PipelineStage):
    """Detect scene changes using PySceneDetect."""

    stage_name = "scene"

    async def execute(self, ctx: PipelineContext) -> PipelineContext:
        threshold = ctx.config.get("scene_threshold", 30.0)
        video_path = ctx.video_path

        video = open_video(video_path)
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector(threshold=threshold))
        scene_manager.detect_scenes(video)
        scene_list = scene_manager.get_scene_list()

        scenes: List[Scene] = []
        for i, (start, end) in enumerate(scene_list):
            scenes.append(Scene(
                id=f"scene_{i+1:03d}",
                number=i + 1,
                start_time=start.get_seconds(),
                end_time=end.get_seconds(),
                confidence=0.9,
            ))

        if not scenes:
            scenes.append(Scene(
                id="scene_001",
                number=1,
                start_time=0.0,
                end_time=ctx.video_metadata.get("duration", 0),
                confidence=1.0,
            ))

        ctx.scenes = scenes
        logger.info("Detected %d scenes", len(scenes))
        return ctx

    async def validate(self, ctx: PipelineContext) -> bool:
        return bool(ctx.video_path)
