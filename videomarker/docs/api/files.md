# `vdoc.utils.files`

File system utility functions.

## Functions

### `ensure_dir(path: Path)`

Ensure a directory exists, creating it if necessary.

Args:
    path: Directory path to ensure exists.

Returns:
    The path to the directory.

### `get_directory_size(path: Path)`

Calculate the total size of a directory in bytes.

Args:
    path: Directory path.

Returns:
    Total size in bytes.

### `iter_video_files(directory: Path, recursive: bool = True)`

Iterate over video files in a directory.

Args:
    directory: Directory to search.
    recursive: Whether to search subdirectories.

Yields:
    Paths to video files.

### `safe_filename(name: str)`

Convert a string to a safe filename.

Args:
    name: Raw filename string.

Returns:
    Sanitized filename safe for all operating systems.
