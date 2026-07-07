# `vdoc.pipeline.stages.llm`

LLM analysis stage — semantic understanding, chapters, summaries.

## Classes

### `Chapter(title: str = '', start_time: float = 0.0, end_time: float = 0.0, scene_ids: List[str] = <factory>, uuid: str = <factory>)`

A chapter/ section in the video.

### `LLMStage()`

Generate semantic understanding using LLM provider.

**Methods:**

- `execute(ctx: PipelineContext)` &mdash; Execute this stage.
- `get_progress()` &mdash; Return progress of this stage as 0.0-1.0.
- `run_standalone(video_path: str = '', output_dir: str = '', config: Optional[Dict[str, Any]] = None, prereqs: Optional[Dict[str, Any]] = None)` &mdash; Execute this stage standalone with minimal setup.
- `validate(ctx: PipelineContext)` &mdash; Check if this stage can execute given the current context.

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

## Functions

### `render_prompt(template_name: str, kwargs: Any)`

Load and render a prompt template by name.

Args:
    template_name: Relative path under prompts/ (e.g. "llm/transcript_analysis.j2")
    **kwargs: Variables to substitute into the template.

Returns:
    Rendered prompt string.

Raises:
    FileNotFoundError: If the template does not exist.
