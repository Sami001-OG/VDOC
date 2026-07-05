"""Knowledge graph builder - constructs entity-relationship graphs from video content."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from videomarker.models.knowledge import Entity, EntityType, KnowledgeGraph, Relation

logger = logging.getLogger(__name__)


class KnowledgeGraphBuilder:
    """Builds and manages knowledge graphs from video analysis results."""

    def __init__(self) -> None:
        self.graph = KnowledgeGraph()

    def build_from_context(self, context: Any) -> KnowledgeGraph:
        """Build knowledge graph from pipeline context data."""
        kg = context.data.get("knowledge_graph")
        if kg:
            self.graph = kg
            return kg

        semantic = context.data.get("semantic")
        transcript = context.data.get("transcript")

        if semantic:
            for concept in semantic.key_concepts:
                entity = Entity(
                    name=concept.name,
                    entity_type=EntityType.CONCEPT,
                    description=concept.description,
                    confidence=concept.importance,
                )
                self.graph.add_entity(entity)

            for rel in semantic.relationships:
                self.graph.add_relation(
                    Relation(
                        source=rel.source,
                        target=rel.target,
                        relation=rel.relationship_type,
                        evidence=rel.description,
                    )
                )

        return self.graph

    def build_from_text(self, text: str) -> KnowledgeGraph:
        """Build knowledge graph by analyzing text."""
        import re

        patterns = [
            (r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', EntityType.CONCEPT),
            (r'\b[A-Z]{2,}\b', EntityType.TOOL),
        ]
        seen = set()
        for pattern, etype in patterns:
            for match in re.finditer(pattern, text):
                name = match.group()
                if name not in seen and len(name) > 3:
                    seen.add(name)
                    self.graph.add_entity(
                        Entity(name=name, entity_type=etype, confidence=0.5)
                    )
        return self.graph

    def export_json(self, path: Path) -> None:
        """Export the knowledge graph to JSON."""
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "entities": {
                name: {
                    "name": e.name,
                    "type": e.entity_type.value,
                    "aliases": e.aliases,
                    "description": e.description,
                    "confidence": e.confidence,
                    "mentions": e.mentions,
                }
                for name, e in self.graph.entities.items()
            },
            "relations": [
                {
                    "source": r.source,
                    "target": r.target,
                    "relation": r.relation,
                    "confidence": r.confidence,
                    "evidence": r.evidence,
                }
                for r in self.graph.relations
            ],
        }

        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(
            "Knowledge graph exported to %s (%d entities, %d relations)",
            path,
            len(self.graph.entities),
            len(self.graph.relations),
        )
