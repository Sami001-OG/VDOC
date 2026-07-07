# `vdoc.knowledge.graph`

Knowledge graph — entity extraction and relationship mapping from video analysis.

## Classes

### `Entity(name: str, type: str, mentions: List[str] = <factory>, properties: Dict[str, Any] = <factory>)`

Entity(name: 'str', type: 'str', mentions: 'List[str]' = <factory>, properties: 'Dict[str, Any]' = <factory>)

**Methods:**

- `to_dict()` &mdash; 

### `KnowledgeGraph()`

Entity-relation knowledge graph extracted from video content.

**Methods:**

- `add_entity(entity: Entity)` &mdash; 
- `add_relation(relation: Relation)` &mdash; 
- `extract_from_document(document)` &mdash; Auto-extract entities and relations from a VideoDocument.
- `get_entity(name: str)` &mdash; 
- `get_relations(entity_name: str)` &mdash; 
- `merge(other: 'KnowledgeGraph')` &mdash; 
- `query(entity_name: str, depth: int = 1)` &mdash; 
- `to_dict()` &mdash; 
- `to_json(path: str)` &mdash; 

### `Relation(source: str, target: str, relation: str, context: Optional[str] = None, weight: float = 1.0)`

Relation(source: 'str', target: 'str', relation: 'str', context: 'Optional[str]' = None, weight: 'float' = 1.0)

**Methods:**

- `to_dict()` &mdash; 
