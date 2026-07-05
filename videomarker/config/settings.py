"""Configuration management for VideoMarker.

All settings can be configured via environment variables or a .env file.
Changing providers requires only changing the .env file.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class VideoMarkerSettings(BaseSettings):
    """Global settings for VideoMarker.

    All configuration is loaded from environment variables or .env file.
    Changing providers requires only updating the .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- LLM Provider ---
    llm_provider: str = Field("openai", description="LLM provider name")
    base_url: str = Field("https://api.openai.com/v1", description="API base URL")
    api_key: str = Field("", description="API key for the LLM provider")
    model: str = Field("gpt-4o", description="Primary model for text processing")
    vision_model: str = Field("gpt-4o", description="Model for vision understanding")
    embedding_model: str = Field(
        "BAAI/bge-large-en-v1.5", description="Model for generating embeddings"
    )
    max_tokens: int = Field(4096, description="Maximum tokens for LLM responses")
    temperature: float = Field(0.1, description="Temperature for LLM sampling")
    llm_request_timeout: int = Field(120, description="Timeout for LLM requests in seconds")

    # --- Processing ---
    frame_extraction_fps: float = Field(1.0, description="Frames to extract per second")
    max_frames: int = Field(5000, description="Maximum frames to extract")
    scene_detect_threshold: float = Field(30.0, description="Scene detection threshold")
    keyframe_method: str = Field(
        "scene_middle", description="Method for selecting keyframes"
    )
    max_scenes: int = Field(200, description="Maximum number of scenes to process")
    parallel_workers: int = Field(4, description="Number of parallel worker threads")
    batch_size: int = Field(16, description="Batch size for processor inference")
    gpu_enabled: bool = Field(False, description="Use GPU acceleration")
    device: str = Field("cpu", description="Device for inference (cpu/cuda/mps)")
    fp16: bool = Field(False, description="Use FP16 precision")

    # --- Audio ---
    whisper_model: str = Field("base", description="Whisper model size (tiny/base/small/medium/large)")
    whisper_device: str = Field("cpu", description="Device for Whisper")
    whisper_compute_type: str = Field("float16", description="Compute type for Whisper")
    language: Optional[str] = Field(None, description="Language code (auto-detect if None)")
    diarize: bool = Field(False, description="Enable speaker diarization")
    num_speakers: int = Field(0, description="Number of speakers (0 = auto)")

    # --- OCR ---
    ocr_engine: str = Field("paddle", description="OCR engine (paddle/surya)")
    ocr_languages: List[str] = Field(["en"], description="OCR languages")
    ocr_confidence_threshold: float = Field(0.5, description="OCR confidence threshold")

    # --- Vision ---
    vision_engine: str = Field("qwen-vl", description="Vision model engine")
    vision_confidence_threshold: float = Field(0.5, description="Vision detection threshold")
    scene_description_prompt: str = Field(
        "Describe what is happening in this video scene in detail.",
        description="Prompt for scene description",
    )

    # --- Semantic ---
    semantic_engine: str = Field("llm", description="Semantic understanding engine")
    extract_keywords: bool = Field(True, description="Extract keywords")
    extract_entities: bool = Field(True, description="Extract named entities")
    build_knowledge_graph: bool = Field(True, description="Build knowledge graph")
    generate_summary: bool = Field(True, description="Generate summary")
    chapter_title_prompt: str = Field(
        "Generate a concise, descriptive title for this chapter.",
        description="Prompt for chapter title generation",
    )

    # --- Search ---
    build_search_index: bool = Field(True, description="Build search index")
    search_index_type: str = Field("faiss", description="Search index type (faiss/flat)")
    embedding_dimension: int = Field(1024, description="Embedding vector dimension")

    # --- Output ---
    output_format: str = Field("markdirectory", description="Output format")
    export_formats: List[str] = Field(
        ["markdown", "json"], description="Export formats"
    )
    include_keyframes: bool = Field(True, description="Include keyframe images")
    include_thumbnails: bool = Field(True, description="Include thumbnail images")
    include_embeddings: bool = Field(True, description="Include embedding files")
    overwrite: bool = Field(False, description="Overwrite existing output")

    # --- Pipeline ---
    enabled_processors: List[str] = Field(
        default_factory=lambda: [
            "transcript",
            "ocr",
            "vision",
            "semantic",
            "keywords",
            "entities",
        ],
        description="List of enabled processor names",
    )
    skip_steps: List[str] = Field(
        default_factory=list, description="Pipeline steps to skip"
    )
    resume: bool = Field(False, description="Resume interrupted processing")

    # --- Logging ---
    log_level: str = Field("INFO", description="Logging level")
    log_file: Optional[str] = Field(None, description="Log file path")
    verbose: bool = Field(False, description="Enable verbose logging")

    # --- File paths ---
    temp_dir: Optional[str] = Field(None, description="Temporary directory")
    cache_dir: Optional[str] = Field(None, description="Cache directory")

    def get_openai_client_kwargs(self) -> Dict[str, Any]:
        """Get kwargs for OpenAI-compatible client initialization."""
        kwargs: Dict[str, Any] = {
            "base_url": self.base_url,
        }
        if self.api_key:
            kwargs["api_key"] = self.api_key
        return kwargs

    def is_local_mode(self) -> bool:
        """Check if running in fully local mode (no cloud APIs)."""
        return self.llm_provider.lower() in ("ollama", "lm_studio", "local")


def load_settings(path: Optional[str] = None) -> VideoMarkerSettings:
    """Load settings from a custom path or environment.

    Args:
        path: Optional path to a .env file.

    Returns:
        Loaded VideoMarkerSettings instance.
    """
    if path:
        return VideoMarkerSettings(_env_file=path)
    return VideoMarkerSettings()
