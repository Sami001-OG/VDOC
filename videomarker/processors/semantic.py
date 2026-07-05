"""Semantic understanding processor — extracts meaning, concepts, and relationships."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from videomarker.core.processor import Processor
from videomarker.core.plugin import processor
from videomarker.models.semantic import (
    Definition,
    KeyConcept,
    Relationship,
    SemanticUnderstanding,
    TopicSummary,
)

logger = logging.getLogger(__name__)


@processor("semantic", dependencies=["transcript", "vision"], priority=40)
class SemanticProcessor(Processor):
    """Extract semantic understanding from transcript and vision data."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._client = None

    def process(self, context: Any) -> None:
        """Generate semantic understanding of the video content."""
        transcript = context.data.get("transcript")
        timeline = context.data.get("timeline")
        vision_results = context.data.get("vision_results", {})

        if not transcript and not vision_results:
            logger.warning("No transcript or vision data for semantic analysis")
            return

        semantic = self._analyze_semantics(transcript, timeline, vision_results)
        context.data["semantic"] = semantic
        logger.info(
            "Semantic analysis complete: %d topics, %d concepts, %d relationships",
            len(semantic.topics),
            len(semantic.key_concepts),
            len(semantic.relationships),
        )

    def _analyze_semantics(
        self,
        transcript: Any,
        timeline: Any,
        vision_results: Dict[str, Any],
    ) -> SemanticUnderstanding:
        """Analyze video semantics using LLM or heuristic extraction."""
        try:
            return self._analyze_with_llm(transcript, timeline, vision_results)
        except Exception as e:
            logger.warning("LLM semantic analysis failed, using heuristics: %s", e)
            return self._analyze_heuristic(transcript, timeline)

    def _analyze_with_llm(
        self,
        transcript: Any,
        timeline: Any,
        vision_results: Dict[str, Any],
    ) -> SemanticUnderstanding:
        """Use an LLM to extract semantic understanding."""
        if not transcript or not transcript.full_text:
            return self._analyze_heuristic(transcript, timeline)

        text = transcript.full_text[:8000]  # Limit context length

        try:
            from openai import OpenAI
            client_kwargs = {}
            if self.settings:
                client_kwargs["base_url"] = self.settings.base_url
                if self.settings.api_key:
                    client_kwargs["api_key"] = self.settings.api_key

            client = OpenAI(**client_kwargs)
            model = self.settings.model if self.settings else "gpt-4o"

            prompt = (
                "Analyze the following video transcript. Extract:\n"
                "1. Overall summary (2-3 sentences)\n"
                "2. Key topics covered\n"
                "3. Important concepts and definitions\n"
                "4. Relationships between concepts\n"
                "5. Technical terms with explanations\n\n"
                f"Transcript:\n{text}\n\n"
                "Return the analysis as structured JSON with keys: "
                "summary, topics (list of {title, summary, key_points}), "
                "key_concepts (list of {name, description, importance}), "
                "definitions (list of {term, definition}), "
                "relationships (list of {source, target, relationship_type, description}), "
                "technical_terms (object of term->explanation mappings)."
            )

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=2000,
                temperature=0.1,
            )

            content = response.choices[0].message.content
            if content:
                import json
                data = json.loads(content)
                return self._parse_semantic_json(data, timeline)
        except Exception as e:
            logger.warning("LLM analysis failed: %s", e)

        return self._analyze_heuristic(transcript, timeline)

    def _parse_semantic_json(
        self, data: dict, timeline: Any
    ) -> SemanticUnderstanding:
        """Parse LLM JSON response into SemanticUnderstanding."""
        semantic = SemanticUnderstanding()
        semantic.overall_summary = data.get("summary")
        semantic.technical_terms = data.get("technical_terms", {})

        for t in data.get("topics", []):
            semantic.topics.append(
                TopicSummary(
                    title=t.get("title", "Untitled Topic"),
                    summary=t.get("summary", ""),
                    key_points=t.get("key_points", []),
                )
            )

        for c in data.get("key_concepts", []):
            semantic.key_concepts.append(
                KeyConcept(
                    name=c.get("name", ""),
                    description=c.get("description", ""),
                    importance=c.get("importance", 0.5),
                    related_concepts=c.get("related_concepts", []),
                )
            )

        for d in data.get("definitions", []):
            semantic.definitions.append(
                Definition(
                    term=d.get("term", ""),
                    definition=d.get("definition", ""),
                )
            )

        for r in data.get("relationships", []):
            semantic.relationships.append(
                Relationship(
                    source=r.get("source", ""),
                    target=r.get("target", ""),
                    relationship_type=r.get("relationship_type", "related_to"),
                    description=r.get("description"),
                )
            )

        if timeline and timeline.chapters:
            for i, chapter in enumerate(timeline.chapters):
                if i < len(data.get("topics", [])):
                    topic_data = data["topics"][i]
                    semantic.topics[i].start_time = chapter.start_time
                    semantic.topics[i].end_time = chapter.end_time

        return semantic

    def _analyze_heuristic(
        self, transcript: Any, timeline: Any
    ) -> SemanticUnderstanding:
        """Extract semantic understanding using heuristics."""
        semantic = SemanticUnderstanding()

        if transcript and transcript.full_text:
            words = transcript.full_text.split()
            semantic.overall_summary = (
                f"Video with {len(words)} words across "
                f"{len(transcript.segments)} transcript segments."
            )

            # Extract potential key terms (capitalized words, repeated terms)
            from collections import Counter
            word_freq = Counter(w.lower().strip(".,!?;:()[]") for w in words
                              if len(w) > 3 and w[0].isupper())
            for term, freq in word_freq.most_common(10):
                semantic.key_concepts.append(
                    KeyConcept(
                        name=term,
                        description=f"Mentioned {freq} times",
                        importance=min(freq / len(words) * 100, 1.0),
                    )
                )

        if timeline:
            for chapter in timeline.chapters:
                semantic.topics.append(
                    TopicSummary(
                        title=chapter.title,
                        summary=f"Content from {chapter.start_timestamp} to {chapter.end_timestamp}",
                        start_time=chapter.start_time,
                        end_time=chapter.end_time,
                    )
                )

        return semantic


@processor("keywords", dependencies=["transcript"], priority=45)
class KeywordProcessor(Processor):
    """Extract keywords and key phrases from the transcript."""

    def process(self, context: Any) -> None:
        transcript = context.data.get("transcript")
        if not transcript or not transcript.full_text:
            return

        keywords = self._extract_keywords(transcript.full_text)
        context.data["keywords"] = keywords
        logger.info("Extracted %d keywords", len(keywords))

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords using simple statistical methods."""
        from collections import Counter
        import re

        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        word_freq = Counter(words)
        stop_words = {
            "This", "That", "The", "And", "But", "For", "With", "From",
            "They", "What", "When", "Where", "Which", "There", "Their",
        }
        keywords = [
            word for word, freq in word_freq.most_common(50)
            if word not in stop_words and len(word) > 2
        ]
        return keywords


@processor("entities", dependencies=["transcript", "semantic"], priority=50)
class EntityProcessor(Processor):
    """Extract named entities and build knowledge graph."""

    def process(self, context: Any) -> None:
        transcript = context.data.get("transcript")
        if not transcript or not transcript.full_text:
            return

        from videomarker.models.knowledge import KnowledgeGraph, Entity, EntityType, Relation

        kg = KnowledgeGraph()
        text = transcript.full_text

        # Extract entities using LLM or simple patterns
        try:
            self._extract_entities_with_llm(text, kg)
        except Exception as e:
            logger.warning("LLM entity extraction failed: %s", e)
            self._extract_entities_heuristic(text, kg)

        # Add relations from semantic understanding
        semantic = context.data.get("semantic")
        if semantic:
            for rel in semantic.relationships:
                kg.add_relation(
                    Relation(
                        source=rel.source,
                        target=rel.target,
                        relation=rel.relationship_type,
                        evidence=rel.description,
                    )
                )

        context.data["knowledge_graph"] = kg
        logger.info(
            "Entity extraction complete: %d entities, %d relations",
            len(kg.entities), len(kg.relations),
        )

    def _extract_entities_with_llm(self, text: str, kg: KnowledgeGraph) -> None:
        """Use LLM to extract entities."""
        if not self.settings:
            return self._extract_entities_heuristic(text, kg)

        from openai import OpenAI
        client = OpenAI(
            base_url=self.settings.base_url,
            api_key=self.settings.api_key or "",
        )

        prompt = (
            "Extract named entities from this transcript. "
            "Return JSON with format: {entities: [{name, type, description}]}\n"
            "Types: person, library, framework, language, algorithm, company, tool, concept\n\n"
            f"Transcript:\n{text[:6000]}"
        )

        response = client.chat.completions.create(
            model=self.settings.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=1000,
        )

        content = response.choices[0].message.content
        if content:
            import json
            data = json.loads(content)
            for e_data in data.get("entities", []):
                entity = Entity(
                    name=e_data.get("name", ""),
                    entity_type=EntityType(e_data.get("type", "other")),
                    description=e_data.get("description"),
                )
                kg.add_entity(entity)

    def _extract_entities_heuristic(self, text: str, kg: KnowledgeGraph) -> None:
        """Extract entities using heuristic patterns."""
        import re

        # Find capitalized multi-word phrases
        patterns = [
            (r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', EntityType.CONCEPT),
            (r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+[A-Z][a-z]+\b', EntityType.CONCEPT),
            (r'\b[A-Z]{2,}\b', EntityType.TOOL),
        ]

        seen = set()
        for pattern, etype in patterns:
            for match in re.finditer(pattern, text):
                name = match.group()
                if name not in seen and len(name) > 3:
                    seen.add(name)
                    kg.add_entity(
                        Entity(
                            name=name,
                            entity_type=etype,
                            confidence=0.5,
                        )
                    )
