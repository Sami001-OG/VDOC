# `vdoc.events.bus`

EventBus — lightweight pub/sub for decoupled pipeline communication.

## Classes

### `EventBus()`

Simple pub/sub event bus for decoupling pipeline stages.

Stages emit events instead of calling each other directly.
Handlers subscribe to specific event names.

**Methods:**

- `clear()` &mdash; Remove all handlers.
- `emit(event: PipelineEvent)` &mdash; Emit an event to all subscribed handlers.
- `subscribe(event_name: str, handler: EventHandler)` &mdash; Subscribe a handler to a specific event name.
- `subscribe_all(handler: EventHandler)` &mdash; Subscribe a handler to all events.
- `unsubscribe(event_name: str, handler: EventHandler)` &mdash; Remove a handler from an event.

### `PipelineEvent(name: str, stage: str = '', data: Dict[str, Any] = <factory>, timestamp: float = 0.0)`

An event emitted during pipeline execution.

## Functions

### `emit(event_name: str, stage: str = '', data: Optional[Dict[str, Any]] = None)`

Convenience: emit an event on the default bus.

### `get_bus()`

Get the default global event bus instance.
