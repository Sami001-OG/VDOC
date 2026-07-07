# `vdoc.config.manager`

Configuration manager — layered config with CLI > YAML > .env > defaults.

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

### `ConfigSchema(llm_provider: str = 'openai', llm_base_url: str = 'https://api.openai.com/v1', llm_api_key: str = '', llm_model: str = 'gpt-4o', vision_provider: str = 'openai', vision_model: str = 'gpt-4o', vision_base_url: str = '', speech_provider: str = 'whisper', speech_model: str = 'base', ocr_provider: str = 'paddle', ocr_model: str = '', embedding_provider: str = 'sentence-transformers', embedding_model: str = 'BAAI/bge-large-en-v1.5', video_provider: str = 'ffmpeg', profile: str = 'default', video_path: str = '', frame_fps: float = 1.0, scene_threshold: float = 30.0, max_frames: int = 5000, parallel_workers: int = 4, device: str = 'cpu', gpu_enabled: bool = False, output_dir: str = '', output_format: str = 'markdirectory', export_formats: List = ['markdirectory', 'markdown', 'json'], overwrite: bool = False, build_search_index: bool = True, search_top_k: int = 10, log_level: str = 'INFO', temperature: float = 0.1, max_tokens: int = 4096, resume: bool = False, model_config: dict = {'extra': 'ignore'})`

Unified configuration schema.

Priority (highest to lowest):
    CLI overrides
    config.yaml
    .env
    defaults

**Methods:**

- `copy(include: Union = None, exclude: Union = None, update: Union = None, deep: bool = False)` &mdash; Duplicate a model, optionally choose which fields to include, exclude and change.
- `dict(include: Union = None, exclude: Union = None, by_alias: bool = False, skip_defaults: Union = None, exclude_unset: bool = False, exclude_defaults: bool = False, exclude_none: bool = False)` &mdash; Generate a dictionary representation of the model, optionally specifying which fields to include or exclude.
- `json(include: Union = None, exclude: Union = None, by_alias: bool = False, skip_defaults: Union = None, exclude_unset: bool = False, exclude_defaults: bool = False, exclude_none: bool = False, encoder: Union = None, models_as_dict: bool = True, dumps_kwargs: Any)` &mdash; Generate a JSON representation of the model, `include` and `exclude` arguments as per `dict()`.
