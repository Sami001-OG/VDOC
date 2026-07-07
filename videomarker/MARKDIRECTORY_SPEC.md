# MarkDirectory Specification v0.1.0

**Format**: `.markdir` — a structured filesystem directory produced by VDOC.

A MarkDirectory is a self-contained, portable directory that holds the complete analysis
result of a single video. It is designed to be human-readable, machine-parseable, and
version-controllable. Every `.markdir` is a directory named `<video_stem>.markdir/`.

---

## 1. Top-Level Structure

```
<video>.markdir/
├── metadata.json          # Video metadata & processing info
├── timeline.json          # Scene & chapter timeline (machine-readable)
├── manifest.json          # Processing manifest
├── summary.md             # AI-generated summary
├── chapters.md            # Chapter breakdown
├── transcript.md          # Full transcript with timestamps
├── keywords.md            # Extracted key terms
├── entities.json          # Knowledge graph entities
├── search_index.json      # FAISS vector index metadata
├── frames/                # Extracted frames at configured FPS
│   ├── frame_000001.jpg
│   ├── frame_000002.jpg
│   └── ...
├── assets/                # Additional output assets
│   ├── subtitles.srt
│   └── ...
├── thumbnails/            # Preview thumbnails
│   ├── thumbnail.jpg
│   └── ...
├── embeddings/            # Vector embeddings (chapter, scene, full)
│   ├── full.bin
│   └── ...
├── search/                # Semantic search index files
│   ├── index.faiss
│   └── index.meta.json
└── scenes/                # Per-scene detailed output
    ├── scene_001/
    ├── scene_002/
    └── ...
```

---

## 2. File Specifications

### 2.1 `metadata.json`

Video-level metadata. Always present.

```json
{
  "title": "Lecture Title",
  "source": "/path/to/source.mp4",
  "duration": 3600.0,
  "fps": 30.0,
  "resolution": { "width": 1920, "height": 1080 },
  "codec": "h264",
  "file_size": 104857600,
  "scenes": 12,
  "chapters": 5,
  "created_at": "2026-07-08T12:00:00"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Video title (from source or user-provided) |
| `source` | string | Original source file path |
| `duration` | number | Duration in seconds |
| `fps` | number | Frames per second |
| `resolution` | object | Video resolution `{width, height}` |
| `codec` | string | Video codec name |
| `file_size` | integer | Source file size in bytes |
| `scenes` | integer | Number of detected scenes |
| `chapters` | integer | Number of detected chapters |
| `created_at` | string (ISO 8601) | Processing timestamp |

### 2.2 `timeline.json`

Machine-readable scene and chapter timeline.

```json
{
  "duration": 3600.0,
  "scenes": [
    {
      "id": "scene_abc123",
      "number": 1,
      "start_time": 0.0,
      "end_time": 120.5,
      "description": "Introduction to topic",
      "confidence": 0.95
    }
  ],
  "chapters": [
    {
      "id": "ch_001",
      "title": "Introduction",
      "start_time": 0.0,
      "end_time": 300.0,
      "scene_ids": ["scene_001", "scene_002"]
    }
  ]
}
```

### 2.3 `manifest.json`

Processing manifest with pipeline metadata.

```json
{
  "version": "0.1.0",
  "created_at": "2026-07-08T12:00:00",
  "video": "lecture.mp4",
  "duration": 3600.0,
  "scenes": 12,
  "chapters": 5,
  "has_transcript": true,
  "has_embeddings": true,
  "has_ocr": true
}
```

### 2.4 `summary.md`

Human-readable Markdown summary. Optional — only present when semantic analysis was
enabled.

```markdown
# Summary

This lecture covers the fundamentals of recursion...

## Keywords

- recursion
- base case
- stack overflow
```

### 2.5 `chapters.md`

Human-readable chapter listing in Markdown.

```markdown
# Chapters

## Introduction
- **Time**: 0.0s – 300.0s
- **Scenes**: 2

## Core Concepts
- **Time**: 300.0s – 1200.0s
- **Scenes**: 4
```

### 2.6 `transcript.md`

Full speech transcription with timestamps.

```markdown
# Transcript

[0.0s - 5.2s] Welcome to this lecture on recursion.

[5.2s - 12.8s] Today we'll explore how recursive functions work...
```

### 2.7 `keywords.md`

Extracted keywords and key phrases.

```markdown
# Keywords

- recursion
- base case
- recursive case
- stack frame
- tail recursion
```

### 2.8 `entities.json`

Knowledge graph entities extracted from the video.

```json
[
  {
    "name": "Python",
    "type": "language",
    "description": "High-level programming language",
    "confidence": 0.95
  },
  {
    "name": "Dijkstra",
    "type": "person",
    "description": "Computer scientist",
    "confidence": 0.87
  }
]
```

### 2.9 `search_index.json`

Semantic search index metadata.

```json
{
  "dimension": 1024,
  "total_vectors": 50,
  "index_type": "Flat",
  "model": "BAAI/bge-large-en-v1.5"
}
```

---

## 3. Scene Directory Structure

Each scene is stored in `scenes/scene_<NNN>/`:

```
scenes/
└── scene_001/
    ├── metadata.json       # Scene-level metadata
    ├── transcript.md       # Scene-specific transcript excerpt
    ├── summary.md          # Scene-specific summary
    ├── caption.md          # Visual description from vision model
    ├── ocr.md              # OCR-extracted text
    ├── keyframe.jpg        # Representative frame
    └── embedding.bin       # Vector embedding (binary float32 array)
```

### 3.1 Scene `metadata.json`

```json
{
  "number": 1,
  "start_time": 0.0,
  "end_time": 120.5,
  "duration": 120.5,
  "description": "Introduction scene"
}
```

### 3.2 Scene `embedding.bin`

Raw float32 vector in binary format. Read with:

```python
import struct
with open("embedding.bin", "rb") as f:
    vec = struct.unpack(f"{len_bytes // 4}f", f.read())
```

---

## 4. Extension & Compatibility

### 4.1 Forward Compatibility

Consumers MUST ignore unknown files and directories. Producers MAY add new files
without changing the version.

### 4.2 Versioning

The `manifest.json` `version` field follows semver. Major version bumps MAY break
backward compatibility.

### 4.3 Custom Files

Plugins and custom processors MAY write additional files into any directory.
It is RECOMMENDED to prefix custom files with `_` (underscore) to avoid collisions
with future spec additions.

---

## 5. MIME Type

Suggested MIME type: `application/vnd.markdirectory`

Suggested file extension: `.markdir` (always a directory, never a flat file)
