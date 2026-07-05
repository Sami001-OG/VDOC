"""Semantic understanding models."""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Definition(BaseModel):
    """An important definition found in the video."""

    term: str
    definition: str
    context: Optional[str] = None
    timestamp: float = 0.0


class KeyConcept(BaseModel):
    """A key concept identified in the video."""

    name: str
    description: str
    importance: float = Field(0.5, ge=0.0, le=1.0)
    related_concepts: List[str] = Field(default_factory=list)


class Relationship(BaseModel):
    """A relationship between concepts."""

    source: str
    target: str
    relationship_type: str = "related_to"
    description: Optional[str] = None


class TopicSummary(BaseModel):
    """Summary of a topic or chapter."""

    title: str
    summary: str
    start_time: float = 0.0
    end_time: float = 0.0
    key_points: List[str] = Field(default_factory=list)
    concepts: List[KeyConcept] = Field(default_factory=list)


class SemanticUnderstanding(BaseModel):
    """Complete semantic understanding of the video."""

    title: Optional[str] = None
    overall_summary: Optional[str] = None
    topics: List[TopicSummary] = Field(default_factory=list)
    key_concepts: List[KeyConcept] = Field(default_factory=list)
    definitions: List[Definition] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
    technical_terms: Dict[str, str] = Field(default_factory=dict)
    code_explanations: List[Dict[str, str]] = Field(default_factory=list)
