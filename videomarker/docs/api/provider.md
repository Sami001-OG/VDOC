# `vdoc.providers.base.provider`

Abstract base class for all providers with retry, caching, rate-limiting.

## Classes

### `BaseProvider(config: Optional[ProviderConfig] = None)`

Every provider inherits from this.

Features:
    - Retry with exponential backoff (#24)
    - Rate limiting (#25)
    - Response caching (#28)
    - Capability detection (#22)
    - Health checks (#23)
    - Streaming support (#27)
    - Provider metadata (#21)

**Methods:**

- `close()` &mdash; 
- `get_metadata()` &mdash; 
- `health_check()` &mdash; 
- `initialize()` &mdash; 
- `list_capabilities()` &mdash; 
- `set_fallbacks(providers: List[BaseProvider])` &mdash; 
- `stream(kwargs: Any)` &mdash; 
- `supports(capability: ProviderCapability)` &mdash; 

### `ProviderCapability(values)`

str(object='') -> str
str(bytes_or_buffer[, encoding[, errors]]) -> str

Create a new string object from the given object. If encoding or
errors is specified, then the object must expose a data buffer
that will be decoded using the given encoding and error handler.
Otherwise, returns the result of object.__str__() (if defined)
or repr(object).
encoding defaults to 'utf-8'.
errors defaults to 'strict'.

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

### `RateLimiter(max_per_second: int = 0)`

Token-bucket rate limiter.

**Methods:**

- `acquire()` &mdash; 

### `ResponseCache(default_ttl: int = 300)`

Simple in-memory response cache with TTL.

**Methods:**

- `clear()` &mdash; 
- `get(key: str)` &mdash; 
- `invalidate(key: str)` &mdash; 
- `set(key: str, value: Any, ttl: Optional[int] = None)` &mdash; 

## Functions

### `retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0)`

Decorator: retry a function on failure with exponential backoff.
