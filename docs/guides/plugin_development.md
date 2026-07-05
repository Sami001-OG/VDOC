# Plugin Development Guide

## Overview

VideoMarker uses a plugin architecture for all content processors. The system automatically discovers processors via the `PluginRegistry` and executes them in dependency order.

## Creating a Processor

### 1. Create a new module

Place your processor in `videomarker/plugins/` or any directory added to the plugin search path.

### 2. Define your processor class

```python
"""my_custom_processor.py"""

from videomarker.core.processor import Processor
from videomarker.core.plugin import processor


@processor(
    "my_analyzer",              # Unique processor name
    dependencies=["transcript"],  # Processors that must run first
    priority=60,                 # Execution order (lower = earlier)
)
class MyAnalyzer(Processor):
    """Custom processor that analyzes transcript sentiment."""

    def process(self, context):
        """Execute this processor.

        Args:
            context: PipelineContext with all pipeline data.
                     Access data via context.data dict.
        """
        transcript = context.data.get("transcript")
        if not transcript:
            return

        # Your custom analysis logic
        result = self.analyze(transcript)

        # Store result for other processors and renderers
        context.data["my_analysis"] = result

    def analyze(self, transcript):
        # Implement your analysis here
        return {"sentiment": "positive", "score": 0.85}
```

### 3. Register the plugin search path

```python
from pathlib import Path
from videomarker.core.plugin import PluginRegistry

PluginRegistry.add_search_path(Path("/path/to/your/plugins"))
```

Or place the module in `videomarker/plugins/` for automatic discovery.

## Processor API

### Required Methods

- `process(self, context) -> None`: Main processing logic

### Optional Attributes

- `__processor_name__`: Set via `@processor("name")` decorator
- `__processor_dependencies__`: List of processor names this depends on
- `__processor_priority__`: Integer priority (lower = earlier execution)

### Context Data

Common context.data keys:

| Key | Type | Description |
|-----|------|-------------|
| `video_path` | Path | Input video path |
| `video_info` | VideoInfo | Video metadata |
| `frames_dir` | Path | Extracted frames directory |
| `audio_path` | Path | Extracted audio file |
| `scenes` | List[Scene] | Detected scenes |
| `timeline` | Timeline | Structured timeline |
| `transcript` | Transcript | Speech transcription |
| `ocr_results` | Dict[str, OCRResult] | OCR per scene |
| `vision_results` | Dict[str, VisionUnderstanding] | Vision per scene |
| `semantic` | SemanticUnderstanding | Semantic analysis |
| `keywords` | List[str] | Extracted keywords |
| `knowledge_graph` | KnowledgeGraph | Entity graph |

## Testing Processors

```python
from unittest.mock import Mock

def test_my_processor():
    context = Mock()
    context.data = {"transcript": Mock(full_text="Hello world")}

    processor = MyAnalyzer()
    processor.process(context)

    assert "my_analysis" in context.data
```
