"""StageRegistry — single point of registration for pipeline stages."""

from __future__ import annotations

import logging
from typing import Dict, Optional, Type

from vdoc.pipeline.base import PipelineStage

logger = logging.getLogger(__name__)


class StageRegistry:
    """Central registry for pipeline stages.

    Plugins can register new stages without modifying core code.
    Discovery is separate from registration — plugins use this to participate.
    """

    _stages: Dict[str, Type[PipelineStage]] = {}

    @classmethod
    def register(cls, name: str, stage_cls: Type[PipelineStage]) -> None:
        cls._stages[name] = stage_cls
        logger.debug("Stage registered: %s → %s", name, stage_cls.__name__)

    @classmethod
    def get(cls, name: str) -> Optional[Type[PipelineStage]]:
        return cls._stages.get(name)

    @classmethod
    def list_stages(cls) -> Dict[str, str]:
        return {name: cls_cls.__doc__ or "" for name, cls_cls in cls._stages.items()}
