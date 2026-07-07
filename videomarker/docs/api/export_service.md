# `vdoc.services.export_service`

ExportService — export processed videos between formats.

## Classes

### `ExportService()`

Service for exporting processed videos between output formats.

**Methods:**

- `export(input_dir: str, fmt: str, output_path: Optional[str] = None)` &mdash; Export a MarkDirectory or processed output to another format.

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

### `MarkdownRenderer()`

Render VideoDocument as a single Markdown file.

**Methods:**

- `render(doc: VideoDocument, output_dir: Path)` &mdash; Render a VideoDocument to the given output directory.
- `validate(doc: VideoDocument)` &mdash; Validate that a document can be rendered by this renderer.
