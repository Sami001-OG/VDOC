"""Tests for the timeline builder."""

from videomarker.core.builder import TimelineBuilder
from videomarker.models.segment import Scene, SegmentType


class TestTimelineBuilder:
    def test_build_with_scenes(self):
        builder = TimelineBuilder()
        scenes = [
            Scene(
                id=f"scene_{i:03d}",
                segment_type=SegmentType.SCENE,
                scene_number=0,
                start_time=i * 10.0,
                end_time=(i + 1) * 10.0,
            )
            for i in range(5)
        ]
        timeline = builder.build(scenes)
        assert len(timeline.scenes) == 5
        assert len(timeline.chapters) >= 1
        assert timeline.scenes[0].scene_number == 1

    def test_auto_chapterize(self):
        builder = TimelineBuilder()
        scenes = [
            Scene(
                id=f"scene_{i:03d}",
                segment_type=SegmentType.SCENE,
                scene_number=0,
                start_time=i * 10.0,
                end_time=(i + 1) * 10.0,
            )
            for i in range(20)
        ]
        timeline = builder.build(scenes)
        assert len(timeline.chapters) >= 2

    def test_empty_scenes(self):
        builder = TimelineBuilder()
        timeline = builder.build([])
        assert len(timeline.scenes) == 0
        assert len(timeline.chapters) == 0
