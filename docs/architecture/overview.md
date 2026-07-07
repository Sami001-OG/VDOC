# Architecture Overview

## Design Philosophy

VDOC follows a layered architecture:

**Provider → Pipeline Stage → Document Model → Renderer**

All external services go through `ProviderRegistry` (dependency injection). The `VideoDocument` is the single source of truth. Renderers consume it to produce output.

## Core Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Video File                        │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                    Providers                         │
│  ┌────────┐  ┌──────┐  ┌───────┐  ┌────────────┐  │
│  │  Video  │  │Speech│  │Vision│  │   OCR      │  │
│  │(FFmpeg) │  │Whisper│  │ VLMs │  │  Paddle    │  │
│  └────────┘  └──────┘  └───────┘  └────────────┘  │
│              ┌──────────┐ ┌──────────┐            │
│              │   LLM    │ │Embedding │            │
│              │(OpenAI.) │ │(Sentence)│            │
│              └──────────┘ └──────────┘            │
│         (All accessed via ProviderRegistry)        │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                 Pipeline Stages                      │
│                                                      │
│  Video → SceneDetection → Speech → OCR →            │
│  Vision → LLM → Render                              │
│                                                      │
│  (Checkpoint/resume via JSON.                       │
│   PipelineContext is the shared data bus.)           │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│               VideoDocument (Model)                  │
│                                                      │
│  Scenes, Transcript, OCR, Captions, Concepts,        │
│  Entities, Embeddings, Knowledge Graph               │
│                                                      │
│  (Single source of truth. Typed dataclasses.)        │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                    Renderers                         │
│                                                      │
│  MarkDirectory  │  Markdown  │  JSON  │  HTML       │
│                                                      │
│  (Each consumes VideoDocument, produces output.)     │
└─────────────────────────────────────────────────────┘
```

## Plugin System

Plugins are auto-discovered from:
1. `plugins/` directory in the project root
2. `plugins/community/` directory
3. `plugins/local/` directory
4. Installed Python packages with entry points

Each plugin is loaded via `PluginLoader` and can provide custom processors, providers, or renderers.

## Data Flow

1. `ConfigManager` resolves config (CLI > YAML > .env > defaults)
2. `ProviderRegistry` registers and initializes providers lazily
3. `PipelineOrchestrator` runs stages sequentially with checkpoint/resume
4. Each stage reads/writes `PipelineContext`
5. `RenderStage` converts `PipelineContext` → `VideoDocument`
6. Renderers consume `VideoDocument` to produce output

## Design Patterns

- **Dependency Injection**: All external services go through `ProviderRegistry`
- **Strategy Pattern**: Each provider implements a common `BaseProvider` interface
- **Pipeline Pattern**: Sequential stages with shared context
- **Checkpoint Pattern**: JSON checkpoint files for resume
- **Singleton Pattern**: `VideoDocument` is the single source of truth
