# `vdoc.utils.media`

Media utility functions.

## Functions

### `get_aspect_ratio(width: int, height: int)`

Get the aspect ratio string for given dimensions.

Args:
    width: Frame width in pixels.
    height: Frame height in pixels.

Returns:
    Aspect ratio string (e.g., "16:9").

### `get_video_dimensions(path: Path)`

Get video dimensions (width, height) using OpenCV.

Args:
    path: Path to the video file.

Returns:
    Tuple of (width, height) or None if unavailable.

### `is_video_file(path: Path)`

Check if a file is a supported video format.

Args:
    path: Path to check.

Returns:
    True if the file is a supported video format.
