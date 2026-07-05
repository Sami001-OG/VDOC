# VideoMarker

**Convert videos into structured MarkDirectory — the Marker equivalent for video.**

VideoMarker is a production-grade open-source framework that transforms video files into a richly structured `MarkDirectory` containing Markdown, JSON, images, embeddings, and a complete knowledge graph. Instead of a single transcript dump, it produces a navigable, searchable representation of the video's structure, content, and semantics.

## Architecture

```
Provider (FFmpeg/FFprobe)
    ↓
FrameExtractor (OpenCV)
    ↓
AudioExtractor (FFmpeg)
    ↓
SceneDetector (PySceneDetect)
    ↓
TimelineBuilder
    ↓
Processors (Plugin System)
    ├── Transcript (faster-whisper)
    ├── OCR (PaddleOCR / Surya)
    ├── Vision (Qwen-VL / GPT-4o)
    ├── Semantic (LLM)
    ├── Keywords
    └── Entities / Knowledge Graph
    ↓
Renderer → MarkDirectory
```

## Quick Start

```bash
# Install
pip install videomarker

# Process a single video
videomarker lecture.mp4

# Process with custom output
videomarker lecture.mp4 -o ./output/

# Batch process all videos in a directory
videomarker ./videos/

# Process specific components
videomarker lecture.mp4 --transcript
videomarker lecture.mp4 --ocr
videomarker lecture.mp4 --summary
videomarker lecture.mp4 --chapters
```

## Output Structure

```
lecture.markdir/
├── metadata.json          # Video file metadata
├── transcript.md          # Full transcript with speaker labels
├── summary.md             # AI-generated summary
├── chapters.md            # Chapter breakdown
├── timeline.json          # Structured timeline data
├── keywords.md            # Extracted keywords
├── entities.json          # Knowledge graph entities
├── search_index.json      # Semantic search index
├── scenes/
│   ├── scene_001/
│   │   ├── transcript.md  # Scene-level transcript
│   │   ├── summary.md     # Scene summary
│   │   ├── caption.md     # Visual description
│   │   ├── ocr.md         # OCR-extracted text
│   │   ├── metadata.json  # Scene timestamps
│   │   ├── keyframe.jpg   # Representative frame
│   │   └── embedding.bin  # Scene embedding
│   ├── scene_002/
│   └── ...
├── frames/                # Extracted frames
├── assets/                # Additional assets
├── thumbnails/            # Preview thumbnails
├── subtitles/             # SRT subtitle files
├── embeddings/            # Vector embeddings
└── manifest.json          # Processing manifest
```

## Configuration

Copy `.env.example` to `.env` and customize:

```bash
# Supported providers: openai, openrouter, groq, ollama, lm_studio, vllm, sglang
LLM_PROVIDER=openrouter
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-v1-...
MODEL=qwen/qwen3-32b
VISION_MODEL=qwen/qwen2.5-vl-72b
```

## Local Mode

```bash
LLM_PROVIDER=ollama
BASE_URL=http://localhost:11434/v1
MODEL=qwen2.5:32b
GPU_ENABLED=true
DEVICE=cuda
```

## REST API

```bash
# Start the API server
videomarker serve

# Process a video
curl -X POST -F "file=@lecture.mp4" http://localhost:8080/process

# Check status
curl http://localhost:8080/status/{job_id}

# Search content
curl -X POST -d "job_id={job_id}&query=recursion&top_k=5" http://localhost:8080/search

# Download results
curl http://localhost:8080/download/{job_id} -o output.zip
```

## Plugin System

Create custom processors without modifying existing code:

```python
# my_plugin.py
from videomarker.core.processor import Processor
from videomarker.core.plugin import processor

@processor("my_analyzer", dependencies=["transcript"], priority=60)
class MyAnalyzer(Processor):
    def process(self, context):
        transcript = context.data.get("transcript")
        # Your custom analysis here
        context.data["my_result"] = result
```

## Docker

```bash
docker-compose up
docker-compose run --rm videomarker-cli lecture.mp4
```

## License

Apache 2.0
