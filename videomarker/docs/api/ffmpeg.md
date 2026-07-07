# `vdoc.providers.video.ffmpeg`

FFmpeg-based video provider — extracts metadata, frames, and audio.

## Classes

### `FFmpegVideoProvider()`

Video provider using FFprobe for metadata and FFmpeg for frame/audio extraction.

**Methods:**

- `close()` &mdash; 
- `extract_audio(output_path: Path, sample_rate: int = 16000)` &mdash; Extract audio track.
- `extract_frames(timestamps: List[float], output_dir: Path)` &mdash; Extract frames at specific timestamps.
- `get_metadata(video_path: Optional[Path] = None)` &mdash; Return video metadata.
- `health_check()` &mdash; 
- `initialize()` &mdash; 
- `list_capabilities()` &mdash; 
- `load(path: Path)` &mdash; Load video and return metadata.
- `process(data: Any)` &mdash; 
- `set_fallbacks(providers: List[BaseProvider])` &mdash; 
- `stream(kwargs: Any)` &mdash; 
- `supports(capability: ProviderCapability)` &mdash; 

### `VideoProvider(config: Optional[ProviderConfig] = None)`

Reads video files, extracts metadata, frames, and audio.

**Methods:**

- `close()` &mdash; 
- `extract_audio(output_path: Path, sample_rate: int = 16000)` &mdash; Extract audio track.
- `extract_frames(timestamps: List[float], output_dir: Path)` &mdash; Extract frames at specific timestamps.
- `get_metadata()` &mdash; Return video metadata.
- `health_check()` &mdash; 
- `initialize()` &mdash; 
- `list_capabilities()` &mdash; 
- `load(path: Path)` &mdash; Load video and return metadata.
- `set_fallbacks(providers: List[BaseProvider])` &mdash; 
- `stream(kwargs: Any)` &mdash; 
- `supports(capability: ProviderCapability)` &mdash; 
