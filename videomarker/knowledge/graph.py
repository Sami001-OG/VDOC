"""Knowledge graph — entity extraction and relationship mapping from video analysis."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Entity:
    name: str
    type: str
    mentions: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "mentions": self.mentions,
            "properties": self.properties,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Entity":
        return cls(
            name=data["name"],
            type=data.get("type", ""),
            mentions=data.get("mentions", []),
            properties=data.get("properties", {}),
        )


@dataclass
class Relation:
    source: str
    target: str
    relation: str
    context: Optional[str] = None
    weight: float = 1.0

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "relation": self.relation,
            "context": self.context,
            "weight": self.weight,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Relation":
        return cls(
            source=data["source"],
            target=data["target"],
            relation=data.get("relation", "related_to"),
            context=data.get("context"),
            weight=data.get("weight", 1.0),
        )


class KnowledgeGraph:
    """Entity-relation knowledge graph extracted from video content."""

    def __init__(self) -> None:
        self.entities: Dict[str, Entity] = {}
        self.relations: List[Relation] = []

    def add_entity(self, entity: Entity) -> None:
        self.entities[entity.name] = entity

    def add_relation(self, relation: Relation) -> None:
        self.relations.append(relation)

    def get_entity(self, name: str) -> Optional[Entity]:
        return self.entities.get(name)

    def get_relations(self, entity_name: str) -> List[Relation]:
        return [
            r
            for r in self.relations
            if r.source == entity_name or r.target == entity_name
        ]

    def query(self, entity_name: str, depth: int = 1) -> Dict[str, Any]:
        entity = self.entities.get(entity_name)
        if not entity:
            return {"entity": None, "relations": []}

        related = self.get_relations(entity_name)
        neighbors = set()
        for rel in related:
            if rel.source == entity_name:
                neighbors.add(rel.target)
            else:
                neighbors.add(rel.source)

        return {
            "entity": entity.to_dict(),
            "relations": [r.to_dict() for r in related],
            "neighbors": [self.entities.get(n).to_dict() for n in neighbors if self.entities.get(n)],
        }

    def extract_from_document(self, document) -> None:
        """Auto-extract entities and relations from a VideoDocument."""
        for scene in document.timeline.scenes:
            if scene.transcript:
                entities = self._extract_entities(scene.transcript.text)
                for name, etype in entities:
                    if name not in self.entities:
                        self.add_entity(Entity(name=name, type=etype))
                    self.entities[name].mentions.append(f"scene_{scene.number}")

            if scene.caption and scene.caption.concepts:
                for concept in scene.caption.concepts:
                    if concept not in self.entities:
                        self.add_entity(Entity(name=concept, type="concept"))
                    self.entities[concept].mentions.append(f"scene_{scene.number}")

    def _extract_entities(self, text: str) -> List[tuple]:
        """Simple noun-phrase entity extraction."""
        import re
        words = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text)
        entities = []
        for w in set(words):
            if len(w.split()) >= 2:
                entities.append((w, "named_entity"))
            elif w.isalpha() and len(w) > 2:
                entities.append((w, "concept"))
        return entities

    def to_dict(self) -> dict:
        return {
            "entities": {k: v.to_dict() for k, v in self.entities.items()},
            "relations": [r.to_dict() for r in self.relations],
        }

    def to_json(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def from_json(cls, path: str) -> "KnowledgeGraph":
        with open(path) as f:
            data = json.load(f)
        kg = cls()
        for v in data.get("entities", {}).values():
            kg.add_entity(Entity.from_dict(v))
        for r in data.get("relations", []):
            kg.add_relation(Relation.from_dict(r))
        return kg

    def merge(self, other: "KnowledgeGraph") -> None:
        for name, entity in other.entities.items():
            if name in self.entities:
                self.entities[name].mentions.extend(entity.mentions)
                self.entities[name].properties.update(entity.properties)
            else:
                self.add_entity(entity)
        self.relations.extend(other.relations)
