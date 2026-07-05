"""Tests for configuration settings."""

from videomarker.config.settings import VideoMarkerSettings


class TestVideoMarkerSettings:
    def test_default_settings(self):
        settings = VideoMarkerSettings()
        assert settings.llm_provider == "openai"
        assert settings.base_url == "https://api.openai.com/v1"
        assert settings.frame_extraction_fps == 1.0
        assert settings.scene_detect_threshold == 30.0
        assert settings.ocr_engine == "paddle"

    def test_is_local_mode(self):
        settings = VideoMarkerSettings(llm_provider="ollama")
        assert settings.is_local_mode() is True

        settings = VideoMarkerSettings(llm_provider="openai")
        assert settings.is_local_mode() is False

    def test_enabled_processors_default(self):
        settings = VideoMarkerSettings()
        assert "transcript" in settings.enabled_processors
        assert "ocr" in settings.enabled_processors
        assert "vision" in settings.enabled_processors
