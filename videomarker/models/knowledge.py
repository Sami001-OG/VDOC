"""Knowledge graph models."""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class EntityType(str, Enum):
    """Types of entities that can appear in a video."""

    PERSON = "person"
    LIBRARY = "library"
    FRAMEWORK = "framework"
    LANGUAGE = "language"
    ALGORITHM = "algorithm"
    COMPANY = "company"
    TOOL = "tool"
    CONCEPT = "concept"
    EQUATION = "equation"
    DATASET = "dataset"
    PAPER = "paper"
    PRODUCT = "product"
    ORGANIZATION = "organization"
    LOCATION = "location"
    TECHNOLOGY = "technology"
    PROTOCOL = "protocol"
    STANDARD = "standard"
    OTHER = "other"


class Entity(BaseModel):
    """An entity identified in the video."""

    name: str
    entity_type: EntityType
    aliases: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    mentions: List[float] = Field(default_factory=list, description="Timestamps of mentions")
    metadata: Dict[str, str] = Field(default_factory=dict)


class Relation(BaseModel):
    """A relationship between two entities."""

    source: str
    target: str
    relation: str
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    evidence: Optional[str] = None


class KnowledgeGraph(BaseModel):
    """Complete knowledge graph extracted from the video."""

    entities: Dict[str, Entity] = Field(default_factory=dict)
    relations: List[Relation] = Field(default_factory=list)

    def add_entity(self, entity: Entity) -> None:
        self.entities[entity.name] = entity

    def add_relation(self, relation: Relation) -> None:
        self.relations.append(relation)

    def get_entity(self, name: str) -> Optional[Entity]:
        return self.entities.get(name)
