# `vdoc.services.cache_manager`

CacheManager — disk-backed caching abstraction.

Higher-level than the in-memory ResponseCache used inside providers.
Supports TTL, namespace isolation, and cache size limits.

## Classes

### `CacheEntry(value: Any, ttl: float = 0)`

**Methods:**

- `to_dict()` &mdash; 

### `CacheManager(cache_dir: Optional[Path] = None, default_ttl: float = 300, max_size_mb: int = 500)`

Multi-backend cache with TTL, namespaces, and optional persistence.

**Methods:**

- `clear()` &mdash; 
- `get(key: str, namespace: str = 'default')` &mdash; 
- `get_or_compute(key: str, factory, namespace: str = 'default', ttl: Optional[float] = None)` &mdash; 
- `invalidate(key: str, namespace: str = 'default')` &mdash; 
- `invalidate_namespace(namespace: str)` &mdash; 
- `set(key: str, value: Any, namespace: str = 'default', ttl: Optional[float] = None)` &mdash; 
- `stats()` &mdash; 
