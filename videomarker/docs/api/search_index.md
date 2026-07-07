# `vdoc.pipeline.stages.search_index`

Search index stage — builds the FAISS search index from embeddings.

## Classes

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

### `SearchEngine(search_provider: Optional[SearchProvider] = None)`

Semantic search over all video analysis data.

Uses SearchProvider for vector operations.

**Methods:**

- `add_document(doc: Dict[str, Any])` &mdash; Add a single document to the index.
- `build_index(documents: List[Dict[str, Any]])` &mdash; Build search index from documents with embeddings.
- `load(path: str)` &mdash; 
- `save(path: str)` &mdash; 
- `search(query: str, top_k: int = 10, embed_fn: Optional[Callable] = None)` &mdash; Search for content semantically similar to the query.

### `SearchIndexStage()`

Build a search index from generated embeddings for semantic search.

**Methods:**

- `execute(ctx: PipelineContext)` &mdash; Execute this stage.
- `get_progress()` &mdash; Return progress of this stage as 0.0-1.0.
- `run_standalone(video_path: str = '', output_dir: str = '', config: Optional[Dict[str, Any]] = None, prereqs: Optional[Dict[str, Any]] = None)` &mdash; Execute this stage standalone with minimal setup.
- `validate(ctx: PipelineContext)` &mdash; Check if this stage can execute given the current context.
