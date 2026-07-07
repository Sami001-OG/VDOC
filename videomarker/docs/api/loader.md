# `vdoc.plugins.loader`

Plugin loader — auto-discovers plugins from multiple search paths.

## Classes

### `PluginInterface()`

Base class that all plugins should inherit from (#91-95).

### `PluginLoader()`

Discovers and loads plugins from multiple search paths.

Searches in order:
    1. vdoc/plugins/ (built-in)
    2. plugins/community/ (community contributed)
    3. plugins/local/ (user local)
    4. Any additional registered paths
