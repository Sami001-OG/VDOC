# Architecture Overview

## Design Philosophy

VideoMarker follows Marker's architectural philosophy:

**Provider → Builder → Processors → Renderer**

But instead of pages, the primary unit is a **time segment** (scene/shot).

## Core Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Video File                          │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                   VideoProvider                          │
│              (FFmpeg / FFprobe)                          │
│         Extracts metadata, codec, duration, FPS          │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  FrameExtractor                          │
│                 (OpenCV / FFmpeg)                        │
│            Extracts frames at configurable FPS           │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  AudioExtractor                          │
│                    (FFmpeg)                              │
│              Extracts audio as 16kHz WAV                 │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  SceneDetector                           │
│               (PySceneDetect)                            │
│         Detects cuts, transitions, slide changes         │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                 TimelineBuilder                          │
│           Groups scenes into chapters, builds timeline   │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                    Processors                            │
│  ┌──────────┐  ┌──────┐  ┌──────┐  ┌──────────┐       │
│  │Transcript│  │ OCR  │  │Vision│  │ Semantic │  ...   │
│  └──────────┘  └──────┘  └──────┘  └──────────┘       │
│         (Auto-discovered via PluginRegistry)            │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                    Renderer                              │
│              (MarkDirectory Renderer)                    │
│     Produces structured Markdown, JSON, images, etc.     │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                   MarkDirectory                          │
│         A structured directory with full output          │
└─────────────────────────────────────────────────────────┘
```

## Plugin System

Processors are discovered via `PluginRegistry`:

1. Scan `videomarker.processors` package
2. Scan user-specified plugin directories
3. Scan entry points
4. Register all `Processor` subclasses with `@processor()` decorator

## Data Flow

PipelineContext is the shared data bus:
- All stages read from and write to `context.data`
- No stage is coupled to any other stage's implementation
- The Renderer reads the final state and produces output

## Design Patterns

- **Strategy Pattern**: Each processor implements a common interface
- **Factory Pattern**: PluginRegistry creates processor instances
- **Dependency Injection**: Settings injected into processors
- **Repository Pattern**: Data models are Pydantic-based
- **Pipeline Pattern**: Sequential processing with context passing
