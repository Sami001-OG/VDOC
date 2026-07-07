"""Tests for configuration validation and management."""

from vdoc.config.manager import ConfigManager
from vdoc.config.validator import validate_config


class TestConfigValidation:
    def test_valid_config(self):
        cfg = {
            "llm_provider": "openai",
            "llm_api_key": "sk-xxx",
            "device": "cpu",
            "frame_fps": 1.0,
            "scene_threshold": 30.0,
            "max_frames": 100,
            "parallel_workers": 2,
            "log_level": "INFO",
            "temperature": 0.1,
            "max_tokens": 4096,
            "export_formats": ["markdown"],
        }
        errors = validate_config(cfg)
        assert errors == []

    def test_invalid_provider(self):
        errors = validate_config({"llm_provider": "invalid"})
        assert any("llm_provider" in e for e in errors)

    def test_invalid_device(self):
        errors = validate_config({"device": "invalid"})
        assert any("device" in e for e in errors)

    def test_invalid_log_level(self):
        errors = validate_config({"log_level": "TRACE"})
        assert any("log_level" in e for e in errors)

    def test_missing_api_key(self):
        errors = validate_config({"llm_provider": "openai", "llm_api_key": ""})
        assert any("llm_api_key" in e for e in errors)

    def test_invalid_export_format(self):
        errors = validate_config({"export_formats": ["exe"]})
        assert any("export" in e for e in errors)

    def test_negative_temperature(self):
        errors = validate_config({"temperature": -1})
        assert any("temperature" in e for e in errors)


class TestConfigProfiles:
    def test_default_profile(self):
        cm = ConfigManager()
        cfg = cm.resolve()
        assert cfg.profile == "default"
        assert cfg.frame_fps == 1.0

    def test_fast_profile(self):
        cm = ConfigManager()
        cm.load_cli(profile="fast")
        cfg = cm.resolve()
        assert cfg.frame_fps == 0.5
        assert cfg.max_frames == 1000

    def test_full_profile(self):
        cm = ConfigManager()
        cm.load_cli(profile="full")
        cfg = cm.resolve()
        assert cfg.frame_fps == 2.0
        assert cfg.max_frames == 10000
