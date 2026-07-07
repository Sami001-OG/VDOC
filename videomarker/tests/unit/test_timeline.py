"""Tests for the timeline model."""

from vdoc.models.document import Chapter, Scene, Timeline


class TestTimeline:
    def test_build_with_scenes(self):
        scenes = [
            Scene(
                id=f"s{i:03d}",
                number=i + 1,
                start_time=i * 10.0,
                end_time=(i + 1) * 10.0,
            )
            for i in range(5)
        ]
        tl = Timeline(scenes=scenes)
        assert len(tl.scenes) == 5
        assert tl.scenes[0].number == 1

    def test_with_chapters(self):
        tl = Timeline(
            scenes=[Scene(id="s1", number=1, start_time=0.0, end_time=60.0)],
            chapters=[Chapter(title="Full Video", start_time=0.0, end_time=60.0)],
        )
        assert len(tl.chapters) == 1
        assert tl.chapters[0].title == "Full Video"

    def test_empty_timeline(self):
        tl = Timeline()
        assert len(tl.scenes) == 0
        assert len(tl.chapters) == 0

