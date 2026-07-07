# `vdoc.services.memory_monitor`

MemoryMonitor — memory usage tracking and metrics collection.

## Classes

### `MemoryMonitor(interval: float = 5.0, max_samples: int = 1000)`

Periodically captures memory usage for profiling and alerting.

**Methods:**

- `collect_garbage()` &mdash; 
- `start()` &mdash; 
- `stop()` &mdash; 
- `summary()` &mdash; 
- `tick()` &mdash; 

### `MemorySnapshot(timestamp: float = 0.0, rss_mb: float = 0.0, vms_mb: float = 0.0, gc_objects: int = 0, gc_collections: int = 0)`

MemorySnapshot(timestamp: 'float' = 0.0, rss_mb: 'float' = 0.0, vms_mb: 'float' = 0.0, gc_objects: 'int' = 0, gc_collections: 'int' = 0)
