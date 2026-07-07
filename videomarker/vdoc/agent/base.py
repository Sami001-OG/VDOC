"""Base agent — abstract agent for LLM-driven analysis tasks."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from vdoc.prompts import render as render_prompt


class BaseAgent(ABC):
    """Abstract base for all LLM-powered agents."""

    name: str = "base"

    def __init__(self, config: dict) -> None:
        self.config = config

    @abstractmethod
    async def run(self, context: dict) -> dict:
        """Run the agent with given context."""

    @abstractmethod
    async def analyze(self, content: str, question: str) -> str:
        """Analyze content and answer a question."""


class SimpleAgent(BaseAgent):
    """A simple agent that uses an LLM provider for Q&A."""

    name = "simple"

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self._provider = None

    async def _get_provider(self):
        if self._provider is None:
            from vdoc.providers.registry import ProviderRegistry
            self._provider = ProviderRegistry.get("llm")
        return self._provider

    async def run(self, context: dict) -> dict:
        provider = await self._get_provider()
        prompt = context.get("prompt") or render_prompt("agent/simple_default.j2")
        response = await provider.process({"prompt": prompt})
        return {"result": response, "agent": self.name}

    async def analyze(self, content: str, question: str) -> str:
        provider = await self._get_provider()
        prompt = render_prompt("agent/simple_analyze.j2", content=content, question=question)
        result = await provider.process({"prompt": prompt})
        return str(result)
