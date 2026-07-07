"""Base class for all pipeline stages."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from vdoc.models.document.document import Caption, Embedding, OCR, Scene, Transcript


class StageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


@dataclass
class StageResult:
    status: StageStatus = StageStatus.PENDING
    stage_name: str = ""
    error: Optional[str] = None
    timing: Optional[float] = None
    output: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineContext:
    """Shared context that flows through all pipeline stages.

    Each stage reads its inputs from and writes its outputs to this context.
    All fields use typed domain models — no raw dicts.
    """

    video_path: str = ""
    output_dir: str = ""
    config: Dict[str, Any] = field(default_factory=dict)

    # Stage outputs — typed domain models
    video_metadata: Dict[str, Any] = field(default_factory=dict)
    """FFmpeg-extracted metadata (duration, fps, codec, resolution, etc.)."""

    scenes: List[Scene] = field(default_factory=list)
    """Detected scenes, enriched by subsequent stages."""

    transcript: Optional[Transcript] = None
    """Speech-to-text result with segments and words."""

    ocr_results: Dict[str, OCR] = field(default_factory=dict)
    """OCR text per scene_id."""

    vision_results: Dict[str, Caption] = field(default_factory=dict)
    """Vision captions per scene_id."""

    llm_output: Dict[str, Any] = field(default_factory=dict)
    """LLM analysis results (summary, chapters, keywords, concepts, entities)."""

    embeddings: List[Embedding] = field(default_factory=list)
    """Vector embeddings for semantic search."""

    search_index: Dict[str, Any] = field(default_factory=dict)
    """Search index metadata (path, num_documents)."""

    knowledge_graph: Dict[str, Any] = field(default_factory=dict)
    """Knowledge graph data (reserved for future use)."""

    # Pipeline state
    completed_stages: List[str] = field(default_factory=list)
    errors: Dict[str, str] = field(default_factory=dict)
    cancelled: bool = False
    stage_timing: Dict[str, float] = field(default_factory=dict)

    @property
    def last_completed(self) -> Optional[str]:
        return self.completed_stages[-1] if self.completed_stages else None

    @staticmethod
    def _serialize(value: Any) -> Any:
        """Recursively convert dataclass objects to JSON-safe dicts."""
        if hasattr(value, "__dataclass_fields__"):
            return {
                f.name: PipelineContext._serialize(getattr(value, f.name))
                for f in value.__dataclass_fields__.values()
            }
        if isinstance(value, dict):
            return {k: PipelineContext._serialize(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [PipelineContext._serialize(v) for v in value]
        return value

    @staticmethod
    def _deserialize_scene(data: Dict[str, Any]) -> Scene:
        """Reconstruct a Scene from a serialized dict."""
        from vdoc.models.document.document import Caption, OCR, Transcript, Embedding, Scene
        fields = dict(data)
        if fields.get("transcript") and isinstance(fields["transcript"], dict):
            fields["transcript"] = Transcript(**fields["transcript"])
        if fields.get("ocr") and isinstance(fields["ocr"], dict):
            fields["ocr"] = OCR(**fields["ocr"])
        if fields.get("caption") and isinstance(fields["caption"], dict):
            fields["caption"] = Caption(**fields["caption"])
        if fields.get("embedding") and isinstance(fields["embedding"], dict):
            fields["embedding"] = Embedding(**fields["embedding"])
        return Scene(**fields)


class PipelineStage(ABC):
    """A single stage in the processing pipeline.

    Each stage is self-contained and restartable.
    """

    stage_name: str = ""
    parallel_group: str = ""

    @abstractmethod
    async def execute(self, ctx: PipelineContext) -> PipelineContext:
        """Execute this stage.

        Args:
            ctx: Current pipeline context with previous stage outputs.

        Returns:
            Updated pipeline context with this stage's outputs added.
        """
        ...

    @abstractmethod
    async def validate(self, ctx: PipelineContext) -> bool:
        """Check if this stage can execute given the current context.

        Returns True if all prerequisites are met.
        """
        ...

    def get_progress(self) -> float:
        """Return progress of this stage as 0.0-1.0."""
        return 0.0

    async def run_standalone(
        self,
        video_path: str = "",
        output_dir: str = "",
        config: Optional[Dict[str, Any]] = None,
        prereqs: Optional[Dict[str, Any]] = None,
    ) -> PipelineContext:
        """Execute this stage standalone with minimal setup.

        Args:
            video_path: Path to the video file.
            output_dir: Output directory.
            config: Configuration dictionary.
            prereqs: Pre-populated prerequisite data keyed by context field name.

        Returns:
            PipelineContext after stage execution.
        """
        ctx = PipelineContext(
            video_path=video_path,
            output_dir=output_dir,
            config=config or {},
        )
        if prereqs:
            for field, value in prereqs.items():
                if hasattr(ctx, field):
                    setattr(ctx, field, value)
        if not await self.validate(ctx):
            raise RuntimeError(f"Stage '{self.stage_name}' prerequisites not met")
        ctx = await self.execute(ctx)
        return ctx
