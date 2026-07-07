"""Utility functions — re-exported from services for backward compatibility."""

from vdoc.services.file_service import ensure_dir, get_directory_size, iter_video_files, safe_filename
from vdoc.services.media_service import get_aspect_ratio, get_video_dimensions, is_video_file
from vdoc.services.timing_service import Timer, format_timestamp, parse_timestamp

__all__ = [
    "ensure_dir", "get_directory_size", "iter_video_files", "safe_filename",
    "get_aspect_ratio", "get_video_dimensions", "is_video_file",
    "Timer", "format_timestamp", "parse_timestamp",
]
