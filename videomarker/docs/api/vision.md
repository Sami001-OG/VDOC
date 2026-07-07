# `vdoc.pipeline.stages.vision`

Vision analysis stage.

## Classes

### `PipelineContext(video_path: str = '', output_dir: str = '', config: Dict[str, Any] = <factory>, video_metadata: Dict[str, Any] = <factory>, scenes: List[Dict[str, Any]] = <factory>, transcript: Dict[str, Any] = <factory>, ocr_results: Dict[str, Any] = <factory>, vision_results: Dict[str, Any] = <factory>, llm_output: Dict[str, Any] = <factory>, embeddings: List[Dict[str, Any]] = <factory>, search_index: Dict[str, Any] = <factory>, knowledge_graph: Dict[str, Any] = <factory>, completed_stages: List[str] = <factory>, errors: Dict[str, str] = <factory>, cancelled: bool = False, stage_timing: Dict[str, float] = <factory>)`

Shared context that flows through all pipeline stages.

Each stage reads its inputs from and writes its outputs to this context.

### `PipelineStage()`

A single stage in the processing pipeline.

Each stage is self-contained and restartable.

**Methods:**

- `execute(ctx: PipelineContext)` &mdash; Execute this stage.
- `get_progress()` &mdash; Return progress of this stage as 0.0-1.0.
- `run_standalone(video_path: str = '', output_dir: str = '', config: Optional[Dict[str, Any]] = None, prereqs: Optional[Dict[str, Any]] = None)` &mdash; Execute this stage standalone with minimal setup.
- `validate(ctx: PipelineContext)` &mdash; Check if this stage can execute given the current context.

### `ProviderRegistry()`

Central registry that manages provider lifecycle.

Supports:
    - Multiple providers of the same type (#30)
    - Provider lookup by capability (#22)
    - Automatic fallback chains (#29)

### `VisionStage()`

Analyze scene keyframes with vision provider.

**Methods:**

- `execute(ctx: PipelineContext)` &mdash; Execute this stage.
- `get_progress()` &mdash; Return progress of this stage as 0.0-1.0.
- `run_standalone(video_path: str = '', output_dir: str = '', config: Optional[Dict[str, Any]] = None, prereqs: Optional[Dict[str, Any]] = None)` &mdash; Execute this stage standalone with minimal setup.
- `validate(ctx: PipelineContext)` &mdash; Check if this stage can execute given the current context.
