"""EventBus — lightweight pub/sub for decoupled pipeline communication."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class PipelineEvent:
    """An event emitted during pipeline execution."""

    name: str
    stage: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0

    def __post_init__(self) -> None:
        import time
        if not self.timestamp:
            self.timestamp = time.time()


EventHandler = Callable[[PipelineEvent], None]


class EventBus:
    """Simple pub/sub event bus for decoupling pipeline stages.

    Stages emit events instead of calling each other directly.
    Handlers subscribe to specific event names.
    """

    def __init__(self) -> None:
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._wildcard_handlers: List[EventHandler] = []

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        """Subscribe a handler to a specific event name."""
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        self._handlers[event_name].append(handler)
        logger.debug("Subscribed to '%s': %s", event_name, getattr(handler, "__name__", handler))

    def subscribe_all(self, handler: EventHandler) -> None:
        """Subscribe a handler to all events."""
        self._wildcard_handlers.append(handler)

    def unsubscribe(self, event_name: str, handler: EventHandler) -> None:
        """Remove a handler from an event."""
        handlers = self._handlers.get(event_name, [])
        if handler in handlers:
            handlers.remove(handler)

    def emit(self, event: PipelineEvent) -> None:
        """Emit an event to all subscribed handlers."""
        for handler in self._wildcard_handlers:
            self._safe_call(handler, event)
        for handler in self._handlers.get(event.name, []):
            self._safe_call(handler, event)
        for handler in self._handlers.get(f"{event.stage}:{event.name}", []):
            self._safe_call(handler, event)

    def clear(self) -> None:
        """Remove all handlers."""
        self._handlers.clear()
        self._wildcard_handlers.clear()

    @staticmethod
    def _safe_call(handler: EventHandler, event: PipelineEvent) -> None:
        try:
            handler(event)
        except Exception as e:
            logger.warning("Event handler %s failed: %s", getattr(handler, "__name__", handler), e)


_default_bus = EventBus()


def get_bus() -> EventBus:
    """Get the default global event bus instance."""
    return _default_bus


def emit(event_name: str, stage: str = "", data: Optional[Dict[str, Any]] = None) -> None:
    """Convenience: emit an event on the default bus."""
    _default_bus.emit(PipelineEvent(name=event_name, stage=stage, data=data or {}))
