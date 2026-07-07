"""Configuration manager — layered config with CLI > YAML > .env > defaults."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field


CONFIG_PROFILES = {
    "default": {},
    "fast": {"frame_fps": 0.5, "scene_threshold": 50.0, "max_frames": 1000, "max_tokens": 1024},
    "full": {"frame_fps": 2.0, "scene_threshold": 20.0, "max_frames": 10000, "max_tokens": 8192},
    "minimal": {"frame_fps": 0.25, "max_frames": 100, "parallel_workers": 1},
}


class ConfigSchema(BaseModel):
    """Unified configuration schema.

    Priority (highest to lowest):
        CLI overrides
        config.yaml
        .env
        defaults
    """

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

    # Profile
    profile: str = "default"

    # Pipeline
    video_path: str = ""
    frame_fps: float = 1.0
    scene_threshold: float = 30.0
    max_frames: int = 5000
    parallel_workers: int = 4
    device: str = "cpu"
    gpu_enabled: bool = False

    # Output
    output_dir: str = ""
    output_format: str = "markdirectory"
    export_formats: List[str] = ["markdirectory", "markdown", "json"]
    overwrite: bool = False

    # Search
    build_search_index: bool = True
    search_top_k: int = 10

    # Misc
    log_level: str = "INFO"
    temperature: float = 0.1
    max_tokens: int = 4096
    resume: bool = False

    model_config = {"extra": "ignore"}


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
        """Load configuration from .env file (optional, uses python-dotenv)."""
        if path and path.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(path)
            except ImportError:
                pass
        return self

    def load_cli(self, **kwargs: Any) -> ConfigManager:
        """Load configuration from CLI arguments."""
        self._cli_config = {k: v for k, v in kwargs.items() if v is not None}
        return self

    def load_defaults(self, defaults: Dict[str, Any]) -> ConfigManager:
        """Load default configuration values."""
        self._overrides.update(defaults)
        return self

    def resolve(self) -> ConfigSchema:
        """Resolve configuration with profile support (#81).

        Priority: CLI > YAML > .env > profile > defaults
        """
        config = ConfigSchema()

        # Determine effective profile (CLI > YAML > defaults)
        profile = self._cli_config.get("profile") or self._yaml_config.get("profile") or config.profile

        # Apply profile defaults
        if profile in CONFIG_PROFILES:
            for k, v in CONFIG_PROFILES[profile].items():
                setattr(config, k, v)

        # Apply manual overrides
        for key, value in self._overrides.items():
            if hasattr(config, key):
                setattr(config, key, value)

        # Apply YAML overrides (overrides profile defaults)
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
