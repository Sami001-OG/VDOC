"""Pipeline stage implementations."""

from vdoc.pipeline.registry import StageRegistry
from vdoc.pipeline.stages.embedding import EmbeddingStage
from vdoc.pipeline.stages.llm import LLMStage
from vdoc.pipeline.stages.ocr import OCRStage
from vdoc.pipeline.stages.render import RenderStage
from vdoc.pipeline.stages.scene import SceneDetectionStage
from vdoc.pipeline.stages.search_index import SearchIndexStage
from vdoc.pipeline.stages.speech import SpeechStage
from vdoc.pipeline.stages.video import VideoStage
from vdoc.pipeline.stages.vision import VisionStage

# Register built-in stages
StageRegistry.register("video", VideoStage)
StageRegistry.register("scene", SceneDetectionStage)
StageRegistry.register("speech", SpeechStage)
StageRegistry.register("ocr", OCRStage)
StageRegistry.register("vision", VisionStage)
StageRegistry.register("llm", LLMStage)
StageRegistry.register("embedding", EmbeddingStage)
StageRegistry.register("search_index", SearchIndexStage)
StageRegistry.register("render", RenderStage)

__all__ = [
    "EmbeddingStage",
    "LLMStage",
    "OCRStage",
    "RenderStage",
    "SceneDetectionStage",
    "SearchIndexStage",
    "SpeechStage",
    "VideoStage",
    "VisionStage",
]
