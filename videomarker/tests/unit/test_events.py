"""Tests for the EventBus."""

from vdoc.events.bus import EventBus, PipelineEvent


class TestEventBus:
    def test_subscribe_and_emit(self):
        bus = EventBus()
        received = []

        def handler(event):
            received.append(event.name)

        bus.subscribe("test.event", handler)
        bus.emit(PipelineEvent(name="test.event"))
        assert received == ["test.event"]

    def test_subscribe_all(self):
        bus = EventBus()
        received = []

        def handler(event):
            received.append(event.name)

        bus.subscribe_all(handler)
        bus.emit(PipelineEvent(name="a"))
        bus.emit(PipelineEvent(name="b"))
        assert received == ["a", "b"]

    def test_unsubscribe(self):
        bus = EventBus()
        received = []

        def handler(event):
            received.append(event.name)

        bus.subscribe("test", handler)
        bus.unsubscribe("test", handler)
        bus.emit(PipelineEvent(name="test"))
        assert received == []

    def test_clear(self):
        bus = EventBus()
        received = []

        def handler(event):
            received.append(1)

        bus.subscribe("test", handler)
        bus.clear()
        bus.emit(PipelineEvent(name="test"))
        assert received == []

    def test_stage_specific(self):
        bus = EventBus()
        received = []

        def handler(event):
            received.append(f"{event.stage}:{event.name}")

        bus.subscribe("video:completed", handler)
        bus.emit(PipelineEvent(name="completed", stage="video"))
        bus.emit(PipelineEvent(name="completed", stage="scene"))
        assert received == ["video:completed"]

    def test_data_passthrough(self):
        bus = EventBus()
        received = []

        def handler(event):
            received.append(event.data)

        bus.subscribe("test", handler)
        bus.emit(PipelineEvent(name="test", data={"key": "val"}))
        assert received == [{"key": "val"}]
