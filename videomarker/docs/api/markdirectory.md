# `vdoc.renderers.markdirectory`

MarkDirectory renderer — produces the structured output directory.

## Classes

### `BaseRenderer()`

All renderers inherit from this.

Features:
    - Format name and version (#54)
    - Input validation (#55)
    - Deterministic by default (#57)

**Methods:**

- `render(doc: VideoDocument, output_dir: Path)` &mdash; Render a VideoDocument to the given output directory.
- `validate(doc: VideoDocument)` &mdash; Validate that a document can be rendered by this renderer.

### `MarkDirectoryRenderer()`

Render VideoDocument as a structured MarkDirectory.

video.markdir/
├── metadata.json
├── timeline.json
├── manifest.json
├── summary.md
├── chapters.md
├── transcript.md
├── frames/
├── assets/
├── thumbnails/
├── embeddings/
├── search/
└── scenes/
    └── scene_001/
        ├── metadata.json
        ├── transcript.md
        ├── caption.md
        ├── ocr.md
        ├── keyframe.jpg
        └── embedding.bin

**Methods:**

- `render(doc: VideoDocument, output_dir: Path)` &mdash; Render a VideoDocument to the given output directory.
- `validate(doc: VideoDocument)` &mdash; Validate that a document can be rendered by this renderer.

### `VideoDocument(uuid: str = <factory>, title: str = '', source_path: Path = WindowsPath('.'), created_at: datetime = <factory>, duration: float = 0.0, fps: float = 0.0, resolution: tuple = (0, 0), codec: str = '', file_size: int = 0, timeline: Timeline = <factory>, transcript: Transcript = <factory>, summary: str = '', keywords: List[str] = <factory>, concepts: List[Concept] = <factory>, entities: List[Entity] = <factory>, relationships: List[Relationship] = <factory>, document_version: str = '1.0.0', pipeline_version: str = '', embeddings: List[Embedding] = <factory>, assets: List[Asset] = <factory>, output_dir: Optional[Path] = None)`

Top-level document — the complete analysis result for one video.

This is the single source of truth. All renderers consume this.

**Methods:**

- `get_scene(number: int)` &mdash; 
