"""RendererRegistry — single point of registration for output format renderers."""

from __future__ import annotations

import logging
from typing import Dict, Optional, Type

from vdoc.renderers.base import BaseRenderer

logger = logging.getLogger(__name__)


class RendererRegistry:
    """Central registry for output format renderers.

    Plugins can register new renderers without modifying core code.
    """

    _renderers: Dict[str, Type[BaseRenderer]] = {}

    @classmethod
    def register(cls, name: str, renderer_cls: Type[BaseRenderer]) -> None:
        cls._renderers[name] = renderer_cls
        logger.debug("Renderer registered: %s → %s", name, renderer_cls.__name__)

    @classmethod
    def get(cls, name: str) -> Optional[BaseRenderer]:
        cls_cls = cls._renderers.get(name)
        return cls_cls() if cls_cls else None

    @classmethod
    def list_formats(cls) -> Dict[str, str]:
        return {name: cls_cls.__doc__ or "" for name, cls_cls in cls._renderers.items()}
