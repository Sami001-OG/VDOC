# `vdoc.search.engine`

Search engine — semantic search across transcript, OCR, captions, summaries, and concepts.

## Classes

### `FAISSSearchProvider()`

Vector search using FAISS index.

**Methods:**

- `add(vector: List[float], document: Dict[str, Any])` &mdash; 
- `build_index(vectors: List[List[float]], documents: List[Dict[str, Any]])` &mdash; 
- `load(path: str)` &mdash; 
- `save(path: str)` &mdash; 
- `search(query_vector: List[float], top_k: int = 10)` &mdash; 

### `SearchEngine(search_provider: Optional[SearchProvider] = None)`

Semantic search over all video analysis data.

Uses SearchProvider for vector operations.

**Methods:**

- `add_document(doc: Dict[str, Any])` &mdash; Add a single document to the index.
- `build_index(documents: List[Dict[str, Any]])` &mdash; Build search index from documents with embeddings.
- `load(path: str)` &mdash; 
- `save(path: str)` &mdash; 
- `search(query: str, top_k: int = 10, embed_fn: Optional[Callable] = None)` &mdash; Search for content semantically similar to the query.

### `SearchProvider()`

Abstract interface for vector search operations.

**Methods:**

- `add(vector: List[float], document: Dict[str, Any])` &mdash; 
- `build_index(vectors: List[List[float]], documents: List[Dict[str, Any]])` &mdash; 
- `load(path: str)` &mdash; 
- `save(path: str)` &mdash; 
- `search(query_vector: List[float], top_k: int = 10)` &mdash; 
