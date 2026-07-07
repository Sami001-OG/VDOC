# `vdoc.cli.main`

VDOC CLI — thin presentation layer. All business logic in vdoc.services.

## Classes

### `ConfigManager()`

Layered configuration manager.

Usage:
    config = ConfigManager()
    config.load_cli(video="input.mp4", output="./out")
    config.load_yaml("config.yaml")
    config.load_env()
    settings = config.resolve()

**Methods:**

- `load_cli(kwargs: Any)` &mdash; Load configuration from CLI arguments.
- `load_defaults(defaults: Dict[str, Any])` &mdash; Load default configuration values.
- `load_env(path: Optional[Path] = None)` &mdash; Load configuration from .env file (optional, uses python-dotenv).
- `load_yaml(path: Optional[Path] = None)` &mdash; Load configuration from YAML file.
- `resolve()` &mdash; Resolve configuration with profile support (#81).
- `save_yaml(path: Path)` &mdash; Save current config to YAML.
- `to_dict()` &mdash; Export resolved config as dictionary.

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

## Functions

### `benchmark(video: Path = <typer.models.ArgumentInfo object at 0x00000206873407D0>)`

Run performance benchmarks.

### `callback(ctx: typer.Context)`

### `completion(shell: str = <typer.models.ArgumentInfo object at 0x0000020687340B90>)`

Generate shell completion scripts.

### `config(show: bool = <typer.models.OptionInfo object at 0x0000020687340410>, path: Optional[Path] = <typer.models.OptionInfo object at 0x0000020687340550>, validate: bool = <typer.models.OptionInfo object at 0x0000020687340690>)`

View and manage configuration.

### `doctor()`

Check system dependencies.

### `export(input_dir: Path = <typer.models.ArgumentInfo object at 0x00000206872C7ED0>, format: str = <typer.models.OptionInfo object at 0x0000020687340050>, output: Optional[Path] = <typer.models.OptionInfo object at 0x0000020687340190>)`

Export processed video to a different format.

### `plugin(list_plugins: bool = <typer.models.OptionInfo object at 0x00000206873402D0>)`

List and manage plugins.

### `process(video: Path = <typer.models.ArgumentInfo object at 0x00000206872F0980>, output: Optional[Path] = <typer.models.OptionInfo object at 0x00000206872C6350>, config: Optional[Path] = <typer.models.OptionInfo object at 0x00000206872C6490>, resume: bool = <typer.models.OptionInfo object at 0x00000206872C65D0>, no_transcript: bool = <typer.models.OptionInfo object at 0x00000206872C6710>, no_ocr: bool = <typer.models.OptionInfo object at 0x00000206872C6850>, no_vision: bool = <typer.models.OptionInfo object at 0x00000206872C6990>, no_llm: bool = <typer.models.OptionInfo object at 0x00000206872C6AD0>, overwrite: bool = <typer.models.OptionInfo object at 0x00000206872C6C10>)`

Process a video into a structured MarkDirectory.

### `run(stages: List[str] = <typer.models.ArgumentInfo object at 0x00000206872C7750>, video: Path = <typer.models.ArgumentInfo object at 0x00000206872C7890>, output: Optional[Path] = <typer.models.OptionInfo object at 0x00000206872C79D0>)`

Run specific pipeline stage(s) on a video.

### `search(query: str = <typer.models.ArgumentInfo object at 0x00000206872C7B10>, index: Path = <typer.models.OptionInfo object at 0x00000206872C7C50>, top_k: int = <typer.models.OptionInfo object at 0x00000206872C7D90>)`

Semantic search across processed videos.

### `summarize(video: Path = <typer.models.ArgumentInfo object at 0x00000206872C6D50>, output: Optional[Path] = <typer.models.OptionInfo object at 0x00000206872C6E90>, config: Optional[Path] = <typer.models.OptionInfo object at 0x00000206872C6FD0>)`

Generate summary only (video → scene → speech → llm).

### `transcript(video: Path = <typer.models.ArgumentInfo object at 0x00000206872C7250>, output: Optional[Path] = <typer.models.OptionInfo object at 0x00000206872C7390>, config: Optional[Path] = <typer.models.OptionInfo object at 0x00000206872C74D0>)`

Generate transcript only (video → speech).

### `validate(video: Path = <typer.models.ArgumentInfo object at 0x0000020687340910>, config: Optional[Path] = <typer.models.OptionInfo object at 0x0000020687340A50>)`

Validate that a video can be processed with current config.
