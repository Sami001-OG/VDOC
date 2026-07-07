# `vdoc.utils.timing`

Timing utility functions.

## Classes

### `Timer(name: Optional[str] = None)`

Simple context manager for timing code blocks.

**Methods:**

- `get_elapsed()` &mdash; Get elapsed time in seconds.

## Functions

### `format_timestamp(seconds: float, format: str = 'hh:mm:ss.mmm')`

Format seconds to a human-readable timestamp.

Args:
    seconds: Time value in seconds.
    format: Output format (hh:mm:ss.mmm, hh:mm:ss, mm:ss.mmm).

Returns:
    Formatted timestamp string.

### `parse_timestamp(timestamp: str)`

Parse a timestamp string to seconds.

Args:
    timestamp: Timestamp in format HH:MM:SS.mmm or MM:SS.mmm.

Returns:
    Time value in seconds.
