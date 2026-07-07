"""Decorators and utilities for plugin development."""

from __future__ import annotations

import logging
from functools import wraps
from typing import Any, Callable, Optional, TypeVar

from vdoc.events.bus import EventBus, get_bus

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def vdoc_event(event_name: str):
    """Decorator that emits a VDOC event before and after a function call.

    Example:
        @vdoc_event("my_plugin.process")
        async def process(self, ctx):
            ...
    """
    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            bus = get_bus()
            bus.emit(PipelineEvent(name=f"{event_name}.started"))
            try:
                result = await func(*args, **kwargs)
                bus.emit(PipelineEvent(name=f"{event_name}.completed"))
                return result
            except Exception as e:
                bus.emit(PipelineEvent(name=f"{event_name}.failed", data={"error": str(e)}))
                raise
        return wrapper  # type: ignore
    return decorator


def benchmark(prefix: str = "plugin"):
    """Decorator that logs execution time of a function."""
    import time

    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.monotonic()
            result = await func(*args, **kwargs)
            elapsed = time.monotonic() - start
            logger.info("[%s] %s took %.3fs", prefix, func.__name__, elapsed)
            return result
        return wrapper  # type: ignore
    return decorator
