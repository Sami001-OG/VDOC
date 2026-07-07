# `vdoc.pipeline.orchestrator`

PipelineOrchestrator — restartable, stage-based pipeline executor with parallel support.

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

### `PipelineContext(video_path: str = '', output_dir: str = '', config: Dict[str, Any] = <factory>, video_metadata: Dict[str, Any] = <factory>, scenes: List[Dict[str, Any]] = <factory>, transcript: Dict[str, Any] = <factory>, ocr_results: Dict[str, Any] = <factory>, vision_results: Dict[str, Any] = <factory>, llm_output: Dict[str, Any] = <factory>, embeddings: List[Dict[str, Any]] = <factory>, search_index: Dict[str, Any] = <factory>, knowledge_graph: Dict[str, Any] = <factory>, completed_stages: List[str] = <factory>, errors: Dict[str, str] = <factory>, cancelled: bool = False, stage_timing: Dict[str, float] = <factory>)`

Shared context that flows through all pipeline stages.

Each stage reads its inputs from and writes its outputs to this context.

### `PipelineEvent(name: str, stage: str = '', data: Dict[str, Any] = <factory>, timestamp: float = 0.0)`

An event emitted during pipeline execution.

### `PipelineOrchestrator(event_bus: Optional[EventBus] = None)`

Orchestrates the video processing pipeline.

Supports:
    - Restarting from any failed/interrupted stage
    - Progress callbacks via EventBus
    - Parallel stage execution (stages with same parallel_group)
    - Graceful cancellation
    - Per-stage timing metrics

**Methods:**

- `clear_checkpoint()` &mdash; 
- `on_progress(callback: Callable[[str, float], None])` &mdash; Register a progress callback.
- `register_stage(stage: PipelineStage)` &mdash; Register a pipeline stage.
- `run(ctx: Optional[PipelineContext] = None, resume_from: Optional[str] = None)` &mdash; Execute the pipeline from start or resume from a specific stage.
- `set_checkpoint_dir(path: Path)` &mdash; Set directory for checkpoint files (supports resume).

### `PipelineStage()`

A single stage in the processing pipeline.

Each stage is self-contained and restartable.

**Methods:**

- `execute(ctx: PipelineContext)` &mdash; Execute this stage.
- `get_progress()` &mdash; Return progress of this stage as 0.0-1.0.
- `run_standalone(video_path: str = '', output_dir: str = '', config: Optional[Dict[str, Any]] = None, prereqs: Optional[Dict[str, Any]] = None)` &mdash; Execute this stage standalone with minimal setup.
- `validate(ctx: PipelineContext)` &mdash; Check if this stage can execute given the current context.

## Functions

### `get_bus()`

Get the default global event bus instance.
