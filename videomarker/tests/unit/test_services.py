"""Tests for the service layer."""

from pathlib import Path

from vdoc.services.file_service import ensure_dir, safe_filename, get_directory_size
from vdoc.services.media_service import get_aspect_ratio


class TestFileService:
    def test_safe_filename(self):
        assert safe_filename("hello world") == "hello_world"
        assert safe_filename("file:name") == "file_name"
        assert safe_filename("normal.py") == "normal.py"

    def test_safe_filename_strips(self):
        result = safe_filename(".test.")
        assert not result.startswith(".")
        assert not result.endswith(".")

    def test_safe_filename_special_chars(self):
        result = safe_filename('a<b>c:d"e/f\\g|h?i*j')
        assert "a" in result and "i" in result


class TestMediaService:
    def test_aspect_ratio_16_9(self):
        assert get_aspect_ratio(1920, 1080) == "16:9"

    def test_aspect_ratio_4_3(self):
        assert get_aspect_ratio(640, 480) == "4:3"

    def test_aspect_ratio_1_1(self):
        assert get_aspect_ratio(100, 100) == "1:1"


class TestPipelineServiceConfig:
    def test_stage_map_completeness(self):
        from vdoc.services.pipeline_service import PipelineService
        expected = {"video", "scene", "speech", "ocr", "vision", "llm", "embedding", "search", "render"}
        assert set(PipelineService.STAGE_MAP) == expected
