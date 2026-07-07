# `vdoc.services.asset_manager`

AssetManager — centralized file handling for pipeline assets.

## Classes

### `AssetManager(output_dir: Optional[Path] = None)`

Centralizes all file I/O for pipeline artifacts.

Responsibilities:
  - Track every file the pipeline creates (keyframes, checkpoints, exports)
  - Provide deterministic paths organized by output directory
  - Auto-cleanup temporary files on request or context exit

**Methods:**

- `allocate_path(name: str, subdir: str = '')` &mdash; Return a deterministic path under the output directory, creating parent dirs.
- `allocate_temp(suffix: str = '', prefix: str = 'vdoc_')` &mdash; Return a path to a temporary file that will be cleaned up.
- `allocate_temp_dir(prefix: str = 'vdoc_')` &mdash; Return a path to a temporary directory that will be cleaned up.
- `cleanup_temp()` &mdash; Remove all tracked temp files and dirs. Returns count removed.
- `get(key: str)` &mdash; 
- `get_disk_usage()` &mdash; 
- `get_output_dir()` &mdash; 
- `list_assets(subdir: str = '')` &mdash; 
- `list_by_type(ext: str)` &mdash; 
- `set_output_dir(path: Path)` &mdash; 
- `track(key: str, path: Path)` &mdash; 
