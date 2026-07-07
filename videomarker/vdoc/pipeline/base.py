"""Base class for all pipeline stages."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class PipelineContext:
    """Shared context that flows through all pipeline stages.

    Each stage reads its inputs from and writes its outputs to this context.
    """

    video_path: str = ""
    output_dir: str = ""
    config: Dict[str, Any] = field(default_factory=dict)

    # Stage outputs
    video_metadata: Dict[str, Any] = field(default_factory=dict)
    scenes: List[Dict[str, Any]] = field(default_factory=list)
    transcript: Dict[str, Any] = field(default_factory=dict)
    ocr_results: Dict[str, Any] = field(default_factory=dict)
    vision_results: Dict[str, Any] = field(default_factory=dict)
    llm_output: Dict[str, Any] = field(default_factory=dict)
    embeddings: List[Dict[str, Any]] = field(default_factory=list)
    search_index: Dict[str, Any] = field(default_factory=dict)
    knowledge_graph: Dict[str, Any] = field(default_factory=dict)

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
