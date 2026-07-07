"""Integration tests for the pipeline."""

import tempfile
from pathlib import Path

import pytest

from vdoc.config.manager import ConfigManager
from vdoc.models.document import Scene, Timeline
from vdoc.pipeline.base import PipelineContext, PipelineStage


class MockStage(PipelineStage):
    """Simple mock stage for testing."""

    def __init__(self, name: str, ok: bool = True) -> None:
        super().__init__()
        self.stage_name = name
        self._ok = ok

    async def execute(self, ctx: PipelineContext) -> PipelineContext:
        return ctx

    async def validate(self, ctx: PipelineContext) -> bool:
        return self._ok


class TestPipelineIntegration:
    @pytest.mark.asyncio
    async def test_pipeline_creation(self):
        from vdoc.pipeline.orchestrator import PipelineOrchestrator

        pipeline = PipelineOrchestrator()
        pipeline.register_stage(MockStage("video"))
        pipeline.register_stage(MockStage("render"))

        ctx = PipelineContext(video_path="/tmp/test.mp4", output_dir="/tmp/out")
        result = await pipeline.run(ctx)
        assert result.completed_stages == ["video", "render"]

    @pytest.mark.asyncio
    async def test_pipeline_skip_invalid_stage(self):
        from vdoc.pipeline.orchestrator import PipelineOrchestrator

        pipeline = PipelineOrchestrator()
        pipeline.register_stage(MockStage("video", ok=True))
        pipeline.register_stage(MockStage("render", ok=False))

        ctx = PipelineContext(video_path="/tmp/test.mp4", output_dir="/tmp/out")
        result = await pipeline.run(ctx)
        assert "video" in result.completed_stages
        assert "render" in result.completed_stages  # skipped but still recorded

    @pytest.mark.asyncio
    async def test_pipeline_resume(self):
        from vdoc.pipeline.orchestrator import PipelineOrchestrator

        with tempfile.TemporaryDirectory() as tmp:
            pipeline = PipelineOrchestrator()
            pipeline.register_stage(MockStage("stage_a"))
            pipeline.register_stage(MockStage("stage_b"))
            pipeline.set_checkpoint_dir(Path(tmp))

            ctx = PipelineContext(video_path="/tmp/test.mp4", output_dir="/tmp/out")
            # Simulate first execution that saved checkpoint
            ctx.completed_stages = ["stage_a"]
            pipeline._save_checkpoint(ctx)

            # Resume execution
            old_len = len(ctx.completed_stages)
            result = await pipeline.run(ctx)
            assert len(result.completed_stages) > old_len

    def test_timeline_scenes(self):
        scenes = [
            Scene(id=f"s{i}", number=i + 1, start_time=i * 10.0, end_time=(i + 1) * 10.0)
            for i in range(3)
        ]
        tl = Timeline(scenes=scenes)
        assert len(tl.scenes) == 3
        assert tl.scenes[0].duration == 10.0

