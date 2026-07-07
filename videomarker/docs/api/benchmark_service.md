# `vdoc.services.benchmark_service`

BenchmarkService — performance benchmarks for pipeline stages.

## Classes

### `BenchmarkService()`

Run timing benchmarks for individual pipeline stages.

**Methods:**

- `run(video_path: str)` &mdash; Run benchmarks on each stage and return (name, duration_seconds) pairs.

### `EmbeddingStage()`

Generate embeddings for transcript segments, scene descriptions, and OCR text.

**Methods:**

- `execute(ctx: PipelineContext)` &mdash; Execute this stage.
- `get_progress()` &mdash; Return progress of this stage as 0.0-1.0.
- `run_standalone(video_path: str = '', output_dir: str = '', config: Optional[Dict[str, Any]] = None, prereqs: Optional[Dict[str, Any]] = None)` &mdash; Execute this stage standalone with minimal setup.
- `validate(ctx: PipelineContext)` &mdash; Check if this stage can execute given the current context.

### `LLMStage()`

Generate semantic understanding using LLM provider.

**Methods:**

- `execute(ctx: PipelineContext)` &mdash; Execute this stage.
- `get_progress()` &mdash; Return progress of this stage as 0.0-1.0.
- `run_standalone(video_path: str = '', output_dir: str = '', config: Optional[Dict[str, Any]] = None, prereqs: Optional[Dict[str, Any]] = None)` &mdash; Execute this stage standalone with minimal setup.
- `validate(ctx: PipelineContext)` &mdash; Check if this stage can execute given the current context.

### `OCRStage()`

Extract text from keyframes using OCR provider.

**Methods:**

- `execute(ctx: PipelineContext)` &mdash; Execute this stage.
- `get_progress()` &mdash; Return progress of this stage as 0.0-1.0.
- `run_standalone(video_path: str = '', output_dir: str = '', config: Optional[Dict[str, Any]] = None, prereqs: Optional[Dict[str, Any]] = None)` &mdash; Execute this stage standalone with minimal setup.
- `validate(ctx: PipelineContext)` &mdash; Check if this stage can execute given the current context.

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

### `PipelineService()`

Service for building and running video processing pipelines.

**Methods:**

- `build_partial_pipeline(stage_names: List[str])` &mdash; Build a pipeline with a subset of stages.
- `build_pipeline(config: Dict[str, Any])` &mdash; Build and return the processing pipeline.
- `create_context(video_path: str, output_dir: str, config: Dict[str, Any], completed_stages: Optional[List[str]] = None)` &mdash; Create a pipeline context with the given parameters.
- `load_config(video: Path, output: Optional[Path], config_file: Optional[Path] = None, cli_overrides: Any)` &mdash; Load and resolve configuration.
- `process_batch(video_paths: List[str], output_base: str, config: Dict[str, Any])` &mdash; Process multiple videos sequentially (#38 batch processing).
- `run_pipeline(pipeline: PipelineOrchestrator, ctx: PipelineContext, resume: bool = False)` &mdash; Execute the pipeline with provider setup.
- `run_sync(pipeline: PipelineOrchestrator, ctx: PipelineContext)` &mdash; Run pipeline synchronously (wraps async).

### `ProviderService()`

Business logic for provider registration and lifecycle.

**Methods:**

- `close_all()` &mdash; 
- `is_registered(name: str)` &mdash; 
- `list_available()` &mdash; 
- `register_defaults(config: Optional[Dict[str, Any]] = None)` &mdash; Register all default providers based on configuration.

### `RenderStage(output_formats: List[str] | None = None)`

Produce final output in configured formats.

**Methods:**

- `execute(ctx: PipelineContext)` &mdash; Execute this stage.
- `get_progress()` &mdash; Return progress of this stage as 0.0-1.0.
- `run_standalone(video_path: str = '', output_dir: str = '', config: Optional[Dict[str, Any]] = None, prereqs: Optional[Dict[str, Any]] = None)` &mdash; Execute this stage standalone with minimal setup.
- `validate(ctx: PipelineContext)` &mdash; Check if this stage can execute given the current context.

### `SceneDetectionStage()`

Detect scene changes using PySceneDetect.

**Methods:**

- `execute(ctx: PipelineContext)` &mdash; Execute this stage.
- `get_progress()` &mdash; Return progress of this stage as 0.0-1.0.
- `run_standalone(video_path: str = '', output_dir: str = '', config: Optional[Dict[str, Any]] = None, prereqs: Optional[Dict[str, Any]] = None)` &mdash; Execute this stage standalone with minimal setup.
- `validate(ctx: PipelineContext)` &mdash; Check if this stage can execute given the current context.

### `SearchIndexStage()`

Build a search index from generated embeddings for semantic search.

**Methods:**

- `execute(ctx: PipelineContext)` &mdash; Execute this stage.
- `get_progress()` &mdash; Return progress of this stage as 0.0-1.0.
- `run_standalone(video_path: str = '', output_dir: str = '', config: Optional[Dict[str, Any]] = None, prereqs: Optional[Dict[str, Any]] = None)` &mdash; Execute this stage standalone with minimal setup.
- `validate(ctx: PipelineContext)` &mdash; Check if this stage can execute given the current context.

### `SpeechStage()`

Transcribe audio using the speech provider.

**Methods:**

- `execute(ctx: PipelineContext)` &mdash; Execute this stage.
- `get_progress()` &mdash; Return progress of this stage as 0.0-1.0.
- `run_standalone(video_path: str = '', output_dir: str = '', config: Optional[Dict[str, Any]] = None, prereqs: Optional[Dict[str, Any]] = None)` &mdash; Execute this stage standalone with minimal setup.
- `validate(ctx: PipelineContext)` &mdash; Check if this stage can execute given the current context.

### `VideoStage()`

Load video file and extract metadata.

**Methods:**

- `execute(ctx: PipelineContext)` &mdash; Execute this stage.
- `get_progress()` &mdash; Return progress of this stage as 0.0-1.0.
- `run_standalone(video_path: str = '', output_dir: str = '', config: Optional[Dict[str, Any]] = None, prereqs: Optional[Dict[str, Any]] = None)` &mdash; Execute this stage standalone with minimal setup.
- `validate(ctx: PipelineContext)` &mdash; Check if this stage can execute given the current context.

### `VisionStage()`

Analyze scene keyframes with vision provider.

**Methods:**

- `execute(ctx: PipelineContext)` &mdash; Execute this stage.
- `get_progress()` &mdash; Return progress of this stage as 0.0-1.0.
- `run_standalone(video_path: str = '', output_dir: str = '', config: Optional[Dict[str, Any]] = None, prereqs: Optional[Dict[str, Any]] = None)` &mdash; Execute this stage standalone with minimal setup.
- `validate(ctx: PipelineContext)` &mdash; Check if this stage can execute given the current context.
