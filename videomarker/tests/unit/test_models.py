"""Tests for data models."""

from pathlib import Path

from vdoc.models.document import (
    Asset, Caption, Chapter, Concept, Embedding, Entity, Frame, OCR, OCRBlock,
    Relationship, Scene, Timeline, Transcript, TranscriptSegment, VideoDocument, Word,
)


class TestVideoDocument:
    def test_defaults(self):
        doc = VideoDocument()
        assert doc.title == ""
        assert doc.duration == 0.0
        assert doc.scene_count == 0
        assert doc.chapter_count == 0

    def test_with_scenes(self):
        doc = VideoDocument(
            title="Test Video",
            duration=120.0,
            fps=30.0,
            resolution=(1920, 1080),
            timeline=Timeline(scenes=[
                Scene(id="s1", number=1, start_time=0.0, end_time=10.0),
                Scene(id="s2", number=2, start_time=10.0, end_time=20.0),
            ]),
        )
        assert doc.scene_count == 2
        assert doc.get_scene(1).id == "s1"


class TestSceneModel:
    def test_scene_creation(self):
        scene = Scene(
            id="scene_001",
            number=1,
            start_time=0.0,
            end_time=10.5,
            description="Introduction",
        )
        assert scene.id == "scene_001"
        assert scene.duration == 10.5
        assert scene.number == 1

    def test_scene_duration(self):
        scene = Scene(id="s1", number=1, start_time=5.0, end_time=15.0)
        assert scene.duration == 10.0


class TestTranscriptModel:
    def test_transcript_creation(self):
        t = Transcript(text="Hello world", language="en")
        assert t.text == "Hello world"
        assert t.word_count == 2

    def test_segments_typed(self):
        t = Transcript(text="Hello world", segments=[
            TranscriptSegment(start=0.0, end=1.5, text="Hello world"),
        ])
        assert len(t.segments) == 1
        assert t.segments[0].start == 0.0
        assert t.segments[0].end == 1.5


class TestTranscriptSegmentModel:
    def test_segment_creation(self):
        seg = TranscriptSegment(
            start=0.0,
            end=5.5,
            text="Welcome to the lecture",
            confidence=0.95,
            words=[
                Word(word="Welcome", start=0.0, end=0.8, probability=0.99),
                Word(word="to", start=0.8, end=1.0, probability=0.98),
            ],
        )
        assert seg.start == 0.0
        assert seg.end == 5.5
        assert len(seg.words) == 2
        assert seg.words[0].word == "Welcome"


class TestOCRModel:
    def test_ocr_creation(self):
        ocr = OCR(text="Hello World", language="en", blocks=[
            OCRBlock(text="Hello", confidence=0.95, bbox=[0, 0, 100, 0, 100, 50, 0, 50]),
            OCRBlock(text="World", confidence=0.90),
        ])
        assert ocr.text == "Hello World"
        assert len(ocr.blocks) == 2
        assert ocr.blocks[0].confidence == 0.95


class TestChapterModel:
    def test_chapter_creation(self):
        ch = Chapter(title="Intro", start_time=0.0, end_time=120.0, scene_ids=["s1", "s2"])
        assert ch.title == "Intro"
        assert len(ch.scene_ids) == 2


class TestEntityModel:
    def test_entity_creation(self):
        e = Entity(name="Python", type="language", confidence=0.95)
        assert e.name == "Python"
        assert e.type == "language"


class TestConceptModel:
    def test_concept_creation(self):
        c = Concept(name="Machine Learning", description="ML concepts", importance=0.9)
        assert c.name == "Machine Learning"


class TestEmbeddingModel:
    def test_embedding_creation(self):
        emb = Embedding(id="e1", vector=[0.1, 0.2, 0.3], text="test")
        assert len(emb.vector) == 3
        assert emb.text == "test"


class TestTimelineModel:
    def test_timeline_with_chapters(self):
        tl = Timeline(
            scenes=[Scene(id="s1", number=1, start_time=0.0, end_time=10.0)],
            chapters=[Chapter(title="Intro", start_time=0.0, end_time=10.0)],
        )
        assert len(tl.scenes) == 1
        assert len(tl.chapters) == 1


class TestFrameModel:
    def test_frame_creation(self):
        f = Frame(id="f1", number=1, timestamp=5.0)
        assert f.id == "f1"
        assert f.number == 1


class TestRelationshipModel:
    def test_relationship_creation(self):
        r = Relationship(subject="Python", predicate="is_a", obj="Language")
        assert r.subject == "Python"
        assert r.obj == "Language"


class TestAssetModel:
    def test_asset_creation(self):
        a = Asset(path=Path("/tmp/keyframe.jpg"), type="image")
        assert a.type == "image"

