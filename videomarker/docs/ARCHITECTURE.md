# Architecture

## Overview

VDOC converts videos into structured, searchable documents. The architecture follows a layered design:

```
CLI / API          ← Presentation layer (thin)
    ↓
Services           ← Business logic layer
    ↓
Pipeline           ← Orchestration layer
    ↓
Providers          ← AI/ML integration layer
    ↓
Models/Documents   ← Data layer (single source of truth)
    ↓
Renderers          ← Output layer
```

## Data Flow

1. **Video Input** → `VideoStage` extracts metadata
2. **Scene Detection** → `SceneDetectionStage` splits video into scenes
3. **Speech Recognition** → `SpeechStage` transcribes audio
4. **OCR** → `OCRStage` extracts on-screen text
5. **Vision Analysis** → `VisionStage` describes visual content
6. **LLM Analysis** → `LLMStage` generates summary, chapters, concepts
7. **Embedding** → `EmbeddingStage` creates vector embeddings
8. **Search Index** → `SearchIndexStage` builds FAISS index
9. **Render** → `RenderStage` produces MarkDirectory, Markdown, JSON, HTML

## Key Design Decisions

- **Service layer** separates business logic from CLI/API
- **Provider interfaces** abstract all AI/ML interactions
- **Event bus** decouples pipeline stages
- **Checkpoints** enable resumable processing
- **Typed document model** (VideoDocument) is the single source of truth
