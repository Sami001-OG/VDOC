# `vdoc.pipeline.stages.render`

Render stage — converts pipeline context to VideoDocument and renders output.

## Classes

### `Asset(path: Path, type: str = 'image', description: str = '', uuid: str = <factory>)`

A file asset (keyframe, thumbnail, subtitle, etc.).

### `Caption(summary: str = '', detailed: str = '', tags: List[str] = <factory>, provenance: Optional[Provenance] = None, uuid: str = <factory>)`

Visual description from vision model.

### `Chapter(title: str = '', start_time: float = 0.0, end_time: float = 0.0, scene_ids: List[str] = <factory>, uuid: str = <factory>)`

A chapter/ section in the video.

### `Concept(name: str, description: str = '', importance: float = 0.5, related_concepts: List[str] = <factory>, uuid: str = <factory>)`

A key concept extracted from the video.

### `Embedding(id: str, vector: List[float], text: str, source_type: str = '', timestamp: float = 0.0, model: str = '', uuid: str = <factory>)`

Vector embedding for a piece of content.

### `Entity(name: str, type: str = 'concept', description: Optional[str] = None, confidence: float = 0.5, uuid: str = <factory>)`

A named entity (person, library, framework, etc.).

### `HTMLRenderer()`

Render VideoDocument as a self-contained HTML page.

**Methods:**

- `render(doc: VideoDocument, output_dir: Path)` &mdash; Render a VideoDocument to the given output directory.
- `validate(doc: VideoDocument)` &mdash; Validate that a document can be rendered by this renderer.

### `JSONRenderer()`

Export VideoDocument as a single JSON file.

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

### `MarkdownRenderer()`

Render VideoDocument as a single Markdown file.

**Methods:**

- `render(doc: VideoDocument, output_dir: Path)` &mdash; Render a VideoDocument to the given output directory.
- `validate(doc: VideoDocument)` &mdash; Validate that a document can be rendered by this renderer.

### `OCR(blocks: List[OCRBlock] = <factory>, text: str = '', language: str = 'en', uuid: str = <factory>)`

OCR text extracted from frames.

### `PipelineContext(video_path: str = '', output_dir: str = '', config: Dict[str, Any] = <factory>, video_metadata: Dict[str, Any] = <factory>, scenes: List[Dict[str, Any]] = <factory>, transcript: Dict[str, Any] = <factory>, ocr_results: Dict[str, Any] = <factory>, vision_results: Dict[str, Any] = <factory>, llm_output: Dict[str, Any] = <factory>, embeddings: List[Dict[str, Any]] = <factory>, search_index: Dict[str, Any] = <factory>, knowledge_graph: Dict[str, Any] = <factory>, completed_stages: List[str] = <factory>, errors: Dict[str, str] = <factory>, cancelled: bool = False, stage_timing: Dict[str, float] = <factory>)`

Shared context that flows through all pipeline stages.

Each stage reads its inputs from and writes its outputs to this context.

### `PipelineStage()`

A single stage in the processing pipeline.

Each stage is self-contained and restartable.

**Methods:**

- `execute(ctx: PipelineContext)` &mdash; Execute this stage.
- `get_progress()` &mdash; Return progress of this stage as 0.0-1.0.
- `run_standalone(video_path: str = '', output_dir: str = '', config: Optional[Dict[str, Any]] = None, prereqs: Optional[Dict[str, Any]] = None)` &mdash; Execute this stage standalone with minimal setup.
- `validate(ctx: PipelineContext)` &mdash; Check if this stage can execute given the current context.

### `RenderStage(output_formats: List[str] | None = None)`

Produce final output in configured formats.

**Methods:**

- `execute(ctx: PipelineContext)` &mdash; Execute this stage.
- `get_progress()` &mdash; Return progress of this stage as 0.0-1.0.
- `run_standalone(video_path: str = '', output_dir: str = '', config: Optional[Dict[str, Any]] = None, prereqs: Optional[Dict[str, Any]] = None)` &mdash; Execute this stage standalone with minimal setup.
- `validate(ctx: PipelineContext)` &mdash; Check if this stage can execute given the current context.

### `Scene(id: str, number: int, start_time: float, end_time: float, confidence: float = 1.0, uuid: str = <factory>, transcript: Optional[Transcript] = None, ocr: Optional[OCR] = None, caption: Optional[Caption] = None, keyframe_path: Optional[Path] = None, embedding: Optional[Embedding] = None, frames: List[Frame] = <factory>, description: Optional[str] = None, tags: List[str] = <factory>, provenance: Optional[Provenance] = None)`

A detected scene or shot in the video.

### `Timeline(scenes: List[Scene] = <factory>, chapters: List[Chapter] = <factory>, duration: float = 0.0, uuid: str = <factory>)`

Structured timeline with scenes and chapters.

### `Transcript(segments: List[TranscriptSegment] = <factory>, text: str = '', language: Optional[str] = None, provenance: Optional[Provenance] = None, uuid: str = <factory>)`

Speech transcription output.

### `TranscriptSegment(start: float = 0.0, end: float = 0.0, text: str = '', confidence: float = 0.0, words: List[Word] = <factory>, speaker: Optional[str] = None, provenance: Optional[Provenance] = None, uuid: str = <factory>)`

A segment of transcribed speech.

### `VideoDocument(uuid: str = <factory>, title: str = '', source_path: Path = WindowsPath('.'), created_at: datetime = <factory>, duration: float = 0.0, fps: float = 0.0, resolution: tuple = (0, 0), codec: str = '', file_size: int = 0, timeline: Timeline = <factory>, transcript: Transcript = <factory>, summary: str = '', keywords: List[str] = <factory>, concepts: List[Concept] = <factory>, entities: List[Entity] = <factory>, relationships: List[Relationship] = <factory>, document_version: str = '1.0.0', pipeline_version: str = '', embeddings: List[Embedding] = <factory>, assets: List[Asset] = <factory>, output_dir: Optional[Path] = None)`

Top-level document — the complete analysis result for one video.

This is the single source of truth. All renderers consume this.

**Methods:**

- `get_scene(number: int)` &mdash; 
