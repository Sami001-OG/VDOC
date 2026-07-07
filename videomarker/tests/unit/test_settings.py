"""Tests for configuration settings."""

from vdoc.config.manager import ConfigManager, ConfigSchema


class TestConfigManager:
    def test_defaults(self):
        cm = ConfigManager()
        cfg = cm.resolve()
        assert isinstance(cfg, ConfigSchema)
        assert cfg.llm_provider == "openai"

    def test_cli_override(self):
        cm = ConfigManager()
        cm.load_cli(video_path="/tmp/test.mp4")
        cfg = cm.resolve()
        assert cfg.video_path == "/tmp/test.mp4"

    def test_layered_priority(self):
        cm = ConfigManager()
        cm.load_defaults({"llm_provider": "ollama", "temperature": 0.7})
        cm.load_cli(temperature=0.5)
        cfg = cm.resolve()
        # CLI should win over defaults
        assert cfg.temperature == 0.5
        assert cfg.llm_provider == "ollama"

