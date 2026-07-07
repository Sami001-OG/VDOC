"""Pipeline stage implementations."""

from vdoc.pipeline.stages.video import VideoStage
from vdoc.pipeline.stages.scene import SceneDetectionStage
from vdoc.pipeline.stages.speech import SpeechStage
from vdoc.pipeline.stages.ocr import OCRStage
from vdoc.pipeline.stages.vision import VisionStage
from vdoc.pipeline.stages.llm import LLMStage
from vdoc.pipeline.stages.embedding import EmbeddingStage
from vdoc.pipeline.stages.search_index import SearchIndexStage
from vdoc.pipeline.stages.render import RenderStage

__all__ = [
    "VideoStage",
    "SceneDetectionStage",
    "SpeechStage",
    "OCRStage",
    "VisionStage",
    "LLMStage",
    "EmbeddingStage",
    "SearchIndexStage",
    "RenderStage",
]
