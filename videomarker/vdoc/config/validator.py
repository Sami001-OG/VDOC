"""Configuration validation — ensures all config values are valid before pipeline starts."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List


def validate_config(cfg: Dict[str, Any]) -> List[str]:
    """Validate configuration dictionary. Returns list of error messages (empty if valid)."""
    errors: List[str] = []

    provider = cfg.get("llm_provider", "")
    if provider and provider not in ("openai", "ollama", "anthropic", "none"):
        errors.append(f"Invalid llm_provider: '{provider}'. Expected: openai, ollama, anthropic, or none")

    if provider == "openai":
        api_key = cfg.get("llm_api_key", "")
        if not api_key:
            errors.append("llm_api_key is required when llm_provider is 'openai'")
        base_url = cfg.get("llm_base_url", "")
        if base_url and not re.match(r"^https?://", base_url):
            errors.append(f"llm_base_url must start with http:// or https://, got: '{base_url}'")

    vision = cfg.get("vision_provider", "")
    if vision and vision not in ("openai", "none"):
        errors.append(f"Invalid vision_provider: '{vision}'. Expected: openai or none")

    speech = cfg.get("speech_provider", "")
    if speech and speech not in ("whisper", "none"):
        errors.append(f"Invalid speech_provider: '{speech}'. Expected: whisper or none")

    ocr = cfg.get("ocr_provider", "")
    if ocr and ocr not in ("paddle", "none"):
        errors.append(f"Invalid ocr_provider: '{ocr}'. Expected: paddle or none")

    embedding = cfg.get("embedding_provider", "")
    if embedding and embedding not in ("sentence-transformers", "none"):
        errors.append(f"Invalid embedding_provider: '{embedding}'. Expected: sentence-transformers or none")

    video_provider = cfg.get("video_provider", "")
    if video_provider and video_provider not in ("ffmpeg",):
        errors.append(f"Invalid video_provider: '{video_provider}'. Expected: ffmpeg")

    device = cfg.get("device", "")
    if device and device not in ("cpu", "cuda", "mps"):
        errors.append(f"Invalid device: '{device}'. Expected: cpu, cuda, or mps")

    fps = cfg.get("frame_fps", 1.0)
    if not isinstance(fps, (int, float)) or fps <= 0:
        errors.append(f"frame_fps must be positive, got: {fps}")

    threshold = cfg.get("scene_threshold", 30.0)
    if not isinstance(threshold, (int, float)) or threshold <= 0:
        errors.append(f"scene_threshold must be positive, got: {threshold}")

    max_frames = cfg.get("max_frames", 5000)
    if not isinstance(max_frames, int) or max_frames < 1:
        errors.append(f"max_frames must be a positive integer, got: {max_frames}")

    workers = cfg.get("parallel_workers", 4)
    if not isinstance(workers, int) or workers < 1:
        errors.append(f"parallel_workers must be a positive integer, got: {workers}")

    log_level = cfg.get("log_level", "INFO")
    if log_level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        errors.append(f"Invalid log_level: '{log_level}'. Expected: DEBUG, INFO, WARNING, ERROR, or CRITICAL")

    temperature = cfg.get("temperature", 0.1)
    if not isinstance(temperature, (int, float)) or not (0 <= temperature <= 2):
        errors.append(f"temperature must be between 0 and 2, got: {temperature}")

    max_tokens = cfg.get("max_tokens", 4096)
    if not isinstance(max_tokens, int) or max_tokens < 1:
        errors.append(f"max_tokens must be a positive integer, got: {max_tokens}")

    video_path = cfg.get("video_path", "")
    if video_path and not Path(video_path).exists():
        errors.append(f"video_path does not exist: '{video_path}'")

    export_formats = cfg.get("export_formats", [])
    valid_formats = {"markdirectory", "markdown", "json", "html"}
    if isinstance(export_formats, list):
        for fmt in export_formats:
            if fmt not in valid_formats:
                errors.append(f"Invalid export format: '{fmt}'. Valid: {', '.join(sorted(valid_formats))}")

    return errors
