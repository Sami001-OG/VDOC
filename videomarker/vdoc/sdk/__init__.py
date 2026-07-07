"""VDOC SDK — public API for plugin and extension developers.

Usage:
    from vdoc.sdk import (
        BaseProvider, PipelineStage, PipelineContext,
        BaseRenderer, PluginInterface, EventBus,
        AssetManager, CacheManager, MemoryMonitor,
        VideoDocument, Scene, Transcript, Caption, Embedding,
        vdoc_event, register_provider, get_provider,
    )
"""

from vdoc.events.bus import EventBus, PipelineEvent
from vdoc.sdk.exceptions import (
    CacheError,
    ConfigError,
    PipelineError,
    PluginError,
    ProviderError,
    RendererError,
    StageError,
    ValidationError,
    VdocError,
)
from vdoc.models.document.document import (
    Asset,
    Caption,
    Chapter,
    Concept,
    Embedding,
    Entity,
    Frame,
    OCR,
    OCRBlock,
    Provenance,
    Relationship,
    Scene,
    Timeline,
    Transcript,
    TranscriptSegment,
    VideoDocument,
    Word,
)
from vdoc.pipeline.base import PipelineContext, PipelineStage
from vdoc.plugins.loader import PluginInterface
from vdoc.providers.base.provider import BaseProvider, ProviderCapability, ProviderConfig
from vdoc.providers.registry import get_provider, register_provider
from vdoc.renderers.base import BaseRenderer
from vdoc.services.asset_manager import AssetManager
from vdoc.services.cache_manager import CacheManager
from vdoc.services.memory_monitor import MemoryMonitor

DOCUMENT_MODEL_VERSION = "1.0.0"

__all__ = [
    "Asset",
    "AssetManager",
    "BaseProvider",
    "BaseRenderer",
    "CacheError",
    "CacheManager",
    "Caption",
    "Chapter",
    "Concept",
    "ConfigError",
    "DOCUMENT_MODEL_VERSION",
    "Embedding",
    "Entity",
    "EventBus",
    "Frame",
    "MemoryMonitor",
    "OCR",
    "OCRBlock",
    "PipelineContext",
    "PipelineError",
    "PipelineEvent",
    "PipelineStage",
    "PluginError",
    "PluginInterface",
    "Provenance",
    "ProviderCapability",
    "ProviderConfig",
    "ProviderError",
    "Relationship",
    "RendererError",
    "Scene",
    "StageError",
    "Timeline",
    "Transcript",
    "TranscriptSegment",
    "ValidationError",
    "VdocError",
    "VideoDocument",
    "Word",
    "get_provider",
    "register_provider",
]
