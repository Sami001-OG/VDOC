# `vdoc.models.document.document`

Document model — the single source of truth for all video analysis.

Everything operates on these typed objects instead of raw strings or dicts.
Renderers convert these objects into Markdown, JSON, HTML, etc.

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

### `Frame(id: str = '', number: int = 0, timestamp: float = 0.0, path: Optional[Path] = None, provenance: Optional[Provenance] = None, uuid: str = <factory>)`

A single extracted frame from the video.

### `OCR(blocks: List[OCRBlock] = <factory>, text: str = '', language: str = 'en', uuid: str = <factory>)`

OCR text extracted from frames.

### `OCRBlock(text: str = '', confidence: float = 0.0, bbox: List[float] = <factory>, uuid: str = <factory>)`

A single block of recognized text.

### `Provenance(uuid: str = <factory>, processor: str = '', model: str = '', timestamp: datetime = <factory>, version: str = '1.0.0')`

Tracks which processor/generated a piece of data.

### `Relationship(subject: str = '', predicate: str = '', obj: str = '', confidence: float = 1.0, uuid: str = <factory>)`

A relationship between two entities in the knowledge graph.

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

### `Word(word: str, start: float = 0.0, end: float = 0.0, probability: float = 0.0, uuid: str = <factory>)`

A single word with timing information.

## Functions

### `_uuid()`
