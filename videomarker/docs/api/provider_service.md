# `vdoc.services.provider_service`

ProviderService — manages provider lifecycle for CLI and API.

## Classes

### `ProviderRegistry()`

Central registry that manages provider lifecycle.

Supports:
    - Multiple providers of the same type (#30)
    - Provider lookup by capability (#22)
    - Automatic fallback chains (#29)

### `ProviderService()`

Business logic for provider registration and lifecycle.

**Methods:**

- `close_all()` &mdash; 
- `is_registered(name: str)` &mdash; 
- `list_available()` &mdash; 
- `register_defaults(config: Optional[Dict[str, Any]] = None)` &mdash; Register all default providers based on configuration.
