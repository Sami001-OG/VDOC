# `vdoc.providers.speech.whisper`

Whisper speech-to-text provider via faster-whisper.

## Classes

### `ProviderConfig(name: str, model: str = '', device: str = 'cpu', max_retries: int = 3, timeout: int = 120, batch_size: int = 1, rate_limit: int = 0, cache_ttl: int = 0, fallbacks: List = None, extra: Dict = None)`

Base configuration for all providers.

**Methods:**

- `copy(include: Union = None, exclude: Union = None, update: Union = None, deep: bool = False)` &mdash; Duplicate a model, optionally choose which fields to include, exclude and change.
- `dict(include: Union = None, exclude: Union = None, by_alias: bool = False, skip_defaults: Union = None, exclude_unset: bool = False, exclude_defaults: bool = False, exclude_none: bool = False)` &mdash; Generate a dictionary representation of the model, optionally specifying which fields to include or exclude.
- `json(include: Union = None, exclude: Union = None, by_alias: bool = False, skip_defaults: Union = None, exclude_unset: bool = False, exclude_defaults: bool = False, exclude_none: bool = False, encoder: Union = None, models_as_dict: bool = True, dumps_kwargs: Any)` &mdash; Generate a JSON representation of the model, `include` and `exclude` arguments as per `dict()`.

### `ProviderStatus(values)`

str(object='') -> str
str(bytes_or_buffer[, encoding[, errors]]) -> str

Create a new string object from the given object. If encoding or
errors is specified, then the object must expose a data buffer
that will be decoded using the given encoding and error handler.
Otherwise, returns the result of object.__str__() (if defined)
or repr(object).
encoding defaults to 'utf-8'.
errors defaults to 'strict'.

### `SpeechProvider(config: Optional[ProviderConfig] = None)`

Speech-to-text transcription.

**Methods:**

- `close()` &mdash; 
- `get_metadata()` &mdash; 
- `health_check()` &mdash; 
- `initialize()` &mdash; 
- `list_capabilities()` &mdash; 
- `set_fallbacks(providers: List[BaseProvider])` &mdash; 
- `stream(kwargs: Any)` &mdash; 
- `supports(capability: ProviderCapability)` &mdash; 
- `transcribe(audio_path: Path, language: Optional[str] = None)` &mdash; Transcribe audio file to text with timestamps.
- `transcribe_segment(audio_path: Path, start: float, end: float)` &mdash; Transcribe a specific time segment.

### `WhisperSpeechProvider(config: Optional[ProviderConfig] = None)`

Speech recognition using faster-whisper.

**Methods:**

- `close()` &mdash; 
- `get_metadata()` &mdash; 
- `health_check()` &mdash; 
- `initialize()` &mdash; 
- `list_capabilities()` &mdash; 
- `set_fallbacks(providers: List[BaseProvider])` &mdash; 
- `stream(kwargs: Any)` &mdash; 
- `supports(capability: ProviderCapability)` &mdash; 
- `transcribe(audio_path: Path, language: Optional[str] = None)` &mdash; Transcribe audio file to text with timestamps.
- `transcribe_segment(audio_path: Path, start: float, end: float)` &mdash; Transcribe a specific time segment.
