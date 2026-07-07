# `vdoc.providers.search.faiss_provider`



## Classes

### `FAISSSearchProvider()`

Vector search using FAISS index.

**Methods:**

- `add(vector: List[float], document: Dict[str, Any])` &mdash; 
- `build_index(vectors: List[List[float]], documents: List[Dict[str, Any]])` &mdash; 
- `load(path: str)` &mdash; 
- `save(path: str)` &mdash; 
- `search(query_vector: List[float], top_k: int = 10)` &mdash; 

### `SearchProvider()`

Abstract interface for vector search operations.

**Methods:**

- `add(vector: List[float], document: Dict[str, Any])` &mdash; 
- `build_index(vectors: List[List[float]], documents: List[Dict[str, Any]])` &mdash; 
- `load(path: str)` &mdash; 
- `save(path: str)` &mdash; 
- `search(query_vector: List[float], top_k: int = 10)` &mdash; 
