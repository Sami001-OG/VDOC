"""Tests for data models."""

from videomarker.models.segment import Scene, SegmentType, Timeline, Chapter
from videomarker.models.video import VideoMetadata, VideoInfo, VideoFormat
from videomarker.models.transcript import Transcript, TranscriptSegment, WordTimestamp
from videomarker.models.markdirectory import Manifest


class TestSceneModel:
    def test_scene_creation(self):
        scene = Scene(
            id="scene_001",
            segment_type=SegmentType.SCENE,
            scene_number=1,
            start_time=0.0,
            end_time=10.5,
        )
        assert scene.id == "scene_001"
        assert scene.duration == 10.5
        assert scene.start_timestamp == "00:00:00.000"
        assert scene.end_timestamp == "00:00:10.500"

    def test_timeline_add_scene(self):
        timeline = Timeline()
        scene = Scene(
            id="scene_001",
            segment_type=SegmentType.SCENE,
            scene_number=1,
            start_time=0.0,
            end_time=10.0,
        )
        timeline.add_scene(scene)
        assert len(timeline.scenes) == 1
        assert timeline.scenes[0] == scene


class TestTranscriptModel:
    def test_transcript_creation(self):
        seg = TranscriptSegment(
            start=0.0,
            end=5.0,
            text="Hello world",
            speaker_id="SPEAKER_01",
            confidence=0.95,
        )
        assert seg.text == "Hello world"
        assert seg.speaker_id == "SPEAKER_01"

    def test_word_timestamp(self):
        word = WordTimestamp(word="hello", start=0.0, end=0.5, confidence=0.99)
        assert word.word == "hello"


class TestVideoModel:
    def test_video_metadata(self):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".mp4") as f:
            meta = VideoMetadata(
                file_path=f.name,
                file_size=1000,
                duration=120.0,
                fps=30.0,
                width=1920,
                height=1080,
                codec="h264",
                format_name="mp4",
            )
            assert meta.duration == 120.0
            assert meta.width == 1920

    def test_video_format_enum(self):
        assert VideoFormat.MP4.value == "mp4"
        assert VideoFormat.MKV.value == "mkv"


class TestManifest:
    def test_manifest_defaults(self):
        manifest = Manifest(video_file="test.mp4")
        assert manifest.videomarker_version == "0.1.0"
        assert manifest.video_file == "test.mp4"
        assert manifest.num_scenes == 0
