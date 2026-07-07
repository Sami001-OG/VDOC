"""Base class for all pipeline stages."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


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

    @property
    def last_completed(self) -> Optional[str]:
        return self.completed_stages[-1] if self.completed_stages else None


class PipelineStage(ABC):
    """A single stage in the processing pipeline.

    Each stage is self-contained and restartable.
    """

    stage_name: str = ""

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
