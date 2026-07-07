# Plugin Tutorial

Plugins extend VDOC with custom processing stages, renderers, or providers.

## Creating a Plugin

Create a new Python file in `plugins/community/` or `plugins/local/`:

```python
"""Example VDOC plugin."""

from vdoc.plugins.loader import PluginInterface


class MyPlugin(PluginInterface):
    plugin_name = "my-plugin"
    plugin_version = "1.0.0"
    plugin_description = "Custom analysis plugin"
    plugin_dependencies = []

    @classmethod
    def initialize(cls) -> None:
        print(f"Plugin {cls.plugin_name} initialized")

    @classmethod
    def on_load(cls) -> None:
        print(f"Plugin {cls.plugin_name} loaded")

    @classmethod
    def on_pipeline_start(cls, config: dict) -> None:
        print(f"Pipeline starting with config: {config}")

    @classmethod
    def on_pipeline_end(cls, config: dict) -> None:
        print("Pipeline completed")
```

## Testing Plugins

```python
from vdoc.plugins.loader import PluginLoader

PluginLoader.reset()
PluginLoader.add_path(Path("plugins/local"))
plugins = PluginLoader.discover(force=True)
assert "my-plugin" in plugins
```

## Lifecycle Hooks

| Hook | When Called |
|------|-------------|
| `initialize()` | When plugin is first loaded |
| `on_load()` | After plugin is registered |
| `on_unload()` | Before plugin is removed |
| `on_pipeline_start(config)` | When pipeline execution begins |
| `on_pipeline_end(config)` | When pipeline execution completes |
