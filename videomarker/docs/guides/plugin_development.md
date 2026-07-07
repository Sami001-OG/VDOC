# Plugin Development Guide

## Overview

VDOC uses a plugin architecture for extending functionality. The `PluginLoader` auto-discovers plugins from several directories. Plugins can provide custom processors, providers, or renderers.

## Directory Structure

```
project/
├── plugins/
│   ├── my_plugin/
│   │   ├── __init__.py
│   │   └── processor.py
├── plugins/community/
│   └── ...
└── plugins/local/
    └── ...
```

## Creating a Processor Plugin

### 1. Create the plugin structure

```
plugins/my_sentiment_plugin/
├── __init__.py
└── processor.py
```

### 2. Define the processor function

```python
"""plugins/my_sentiment_plugin/processor.py"""

from vdoc.plugins import processor


@processor(
    name="sentiment_analyzer",
    description="Analyze transcript sentiment per scene",
    dependencies=["transcript"],
)
def analyze_sentiment(context):
    """Analyze sentiment for each transcribed scene."""
    transcript = context.get("transcript", {})
    segments = transcript.get("segments", [])

    results = []
    for seg in segments:
        text = seg.get("text", "")
        # Custom sentiment logic
        score = 0.5  # placeholder
        results.append({
            "start": seg.get("start", 0),
            "end": seg.get("end", 0),
            "sentiment": "positive" if score > 0.5 else "negative",
            "score": score,
        })

    context["sentiment"] = results
    return results
```

## Creating a Provider Plugin

Providers wrap external services. Implement `BaseProvider` and register via `ProviderRegistry`:

```python
"""plugins/my_tts_provider/provider.py"""

from vdoc.providers.base import BaseProvider, ProviderConfig


class MyTTSProvider(BaseProvider):
    """Custom text-to-speech provider."""

    async def initialize(self) -> None:
        # Set up connections
        pass

    async def process(self, data: dict) -> dict:
        text = data.get("text", "")
        voice = data.get("voice", "default")
        # Generate speech...
        return {"audio_path": "/path/to/output.wav"}

    async def close(self) -> None:
        # Clean up
        pass
```

Register it:

```python
from vdoc.providers.registry import ProviderRegistry
from my_tts_provider.provider import MyTTSProvider

ProviderRegistry.register("tts", MyTTSProvider)
```

## Creating a Renderer Plugin

Implement `BaseRenderer`:

```python
"""plugins/my_renderer/renderer.py"""

from pathlib import Path
from vdoc.renderers.base import BaseRenderer
from vdoc.models.document import VideoDocument


class MyCustomRenderer(BaseRenderer):
    """Custom renderer that produces a CSV report."""

    format_name = "csv"

    def render(self, doc: VideoDocument, output_dir: Path) -> Path:
        path = output_dir / "report.csv"
        with open(path, "w") as f:
            f.write("scene,start,end,transcript\n")
            for scene in doc.timeline.scenes:
                text = scene.transcript.text if scene.transcript else ""
                f.write(f"{scene.number},{scene.start_time},{scene.end_time},\"{text}\"\n")
        return path
```

## Plugin Lifecycle

1. **Discovery**: `PluginLoader` scans plugin directories on startup
2. **Registration**: Processors are registered with their dependencies
3. **Execution**: The pipeline runs processors in dependency order
4. **Cleanup**: Each processor's cleanup is called after execution

## Testing Plugins

```python
def test_sentiment_analyzer():
    context = {
        "transcript": {
            "segments": [
                {"start": 0.0, "end": 5.0, "text": "This is great!"},
            ]
        }
    }
    result = analyze_sentiment(context)
    assert "sentiment" in context
    assert len(context["sentiment"]) == 1
```
