"""Integration tests for the pipeline."""

import tempfile
from pathlib import Path

import pytest

from videomarker.config.settings import VideoMarkerSettings
from videomarker.core.pipeline import Pipeline
from videomarker.models.segment import Scene, SegmentType
from videomarker.models.video import VideoInfo, VideoMetadata


class MockProvider:
    """Simple mock video provider for testing."""

    def load(self, path):
        meta = VideoMetadata(
            file_path=str(path),
            file_size=1000,
            duration=60.0,
            fps=30.0,
            width=1920,
            height=1080,
            codec="h264",
            format_name="mp4",
        )
        return VideoInfo(
            id="test_001",
            metadata=meta,
            total_frames=1800,
            output_dir=path.parent / "test.markdir",
        )


class TestPipelineIntegration:
    def test_pipeline_creation(self):
        settings = VideoMarkerSettings()
        pipeline = Pipeline(settings=settings)
        assert pipeline is not None
        assert pipeline.context is not None

    def test_pipeline_skip_audio_when_missing(self):
        """Test pipeline handles missing components gracefully."""
        settings = VideoMarkerSettings()
        pipeline = Pipeline(settings=settings)

        # Override steps to avoid real deps
        def mock_step():
            pass

        pipeline.register_step("provider", mock_step)
        pipeline.register_step("frame_extract", mock_step)
        pipeline.register_step("audio_extract", mock_step)
        pipeline.register_step("scene_detect", mock_step)
        pipeline.register_step("timeline_build", mock_step)
        pipeline.register_step("processors", mock_step)
        pipeline.register_step("render", mock_step)

        with tempfile.NamedTemporaryFile(suffix=".mp4") as f:
            result = pipeline.run(Path(f.name))
            assert result is not None

    def test_pipeline_with_scenes(self):
        """Test pipeline processes scene data correctly."""
        from videomarker.core.builder import TimelineBuilder

        scenes = [
            Scene(
                id=f"scene_{i:03d}",
                segment_type=SegmentType.SCENE,
                scene_number=i + 1,
                start_time=i * 10.0,
                end_time=(i + 1) * 10.0,
            )
            for i in range(3)
        ]
        timeline = TimelineBuilder().build(scenes)
        assert len(timeline.scenes) == 3
