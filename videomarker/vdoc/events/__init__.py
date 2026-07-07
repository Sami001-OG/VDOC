"""Event system — decouples pipeline stages via pub/sub."""

from vdoc.events.bus import EventBus, PipelineEvent

__all__ = ["EventBus", "PipelineEvent"]
