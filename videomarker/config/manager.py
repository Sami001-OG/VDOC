"""Configuration manager — layered config with CLI > YAML > .env > defaults."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigSchema(BaseSettings):
    """Unified configuration schema.

    Priority (highest to lowest):
        CLI overrides
        config.yaml
        .env
        defaults
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Provider
    llm_provider: str = "openai"
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o"

    vision_provider: str = "openai"
    vision_model: str = "gpt-4o"
    vision_base_url: str = ""

    speech_provider: str = "whisper"
    speech_model: str = "base"

    ocr_provider: str = "paddle"
    ocr_model: str = ""

    embedding_provider: str = "sentence-transformers"
    embedding_model: str = "BAAI/bge-large-en-v1.5"

    video_provider: str = "ffmpeg"

    # Pipeline
    frame_fps: float = 1.0
    scene_threshold: float = 30.0
    max_frames: int = 5000
    parallel_workers: int = 4
    device: str = "cpu"
    gpu_enabled: bool = False

    # Output
    output_dir: str = ""
    output_format: str = "markdirectory"
    export_formats: List[str] = ["markdown", "json"]
    overwrite: bool = False

    # Search
    build_search_index: bool = True
    search_top_k: int = 10

    # Misc
    log_level: str = "INFO"
    temperature: float = 0.1
    max_tokens: int = 4096
    resume: bool = False


class ConfigManager:
    """Layered configuration manager.

    Usage:
        config = ConfigManager()
        config.load_cli(video="input.mp4", output="./out")
        config.load_yaml("config.yaml")
        config.load_env()
        settings = config.resolve()
    """

    def __init__(self) -> None:
        self._overrides: Dict[str, Any] = {}
        self._yaml_config: Dict[str, Any] = {}
        self._cli_config: Dict[str, Any] = {}

    def load_yaml(self, path: Optional[Path] = None) -> ConfigManager:
        """Load configuration from YAML file."""
        path = path or Path("config.yaml")
        if path.exists():
            with open(path) as f:
                self._yaml_config = yaml.safe_load(f) or {}
        return self

    def load_env(self, path: Optional[Path] = None) -> ConfigManager:
        """Load configuration from .env file."""
        if path:
            os.environ["VIDEOMARKER_CONFIG"] = str(path)
        return self

    def load_cli(self, **kwargs: Any) -> ConfigManager:
        """Load configuration from CLI arguments."""
        self._cli_config = {k: v for k, v in kwargs.items() if v is not None}
        return self

    def resolve(self) -> ConfigSchema:
        """Resolve configuration with proper priority.

        Priority: CLI > YAML > .env > defaults
        """
        # Start with defaults by constructing from env
        config = ConfigSchema()

        # Apply YAML overrides
        for key, value in self._yaml_config.items():
            if hasattr(config, key):
                setattr(config, key, value)

        # Apply CLI overrides (highest priority)
        for key, value in self._cli_config.items():
            if hasattr(config, key):
                setattr(config, key, value)

        return config

    def to_dict(self) -> Dict[str, Any]:
        """Export resolved config as dictionary."""
        return self.resolve().model_dump()

    def save_yaml(self, path: Path) -> None:
        """Save current config to YAML."""
        with open(path, "w") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)
