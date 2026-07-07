"""Agent orchestrator — coordinates multiple agents for complex analysis."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional, Type

from vdoc.agent.base import BaseAgent, SimpleAgent

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Coordinates multiple agents for multi-step video analysis."""

    def __init__(self) -> None:
        self._agents: Dict[str, BaseAgent] = {}
        self._default_config: Dict[str, Any] = {}

    def register_agent(self, name: str, agent: BaseAgent) -> None:
        self._agents[name] = agent

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        return self._agents.get(name)

    def set_defaults(self, config: dict) -> None:
        self._default_config = config

    async def run_agent(self, name: str, context: dict) -> dict:
        agent = self._agents.get(name)
        if not agent:
            raise ValueError(f"Unknown agent: {name}")
        logger.info("Running agent: %s", name)
        return await agent.run(context)

    async def run_pipeline(self, pipeline: List[dict]) -> dict:
        results = {}
        for step in pipeline:
            name = step["agent"]
            context = step.get("context", {})
            result = await self.run_agent(name, context)
            results[name] = result
        return results

    async def analyze_video(self, transcript: str, questions: List[str]) -> Dict[str, str]:
        agent = self._agents.get("simple", SimpleAgent(self._default_config))
        tasks = {q: agent.analyze(transcript, q) for q in questions}
        completed = await asyncio.gather(*[tasks[q] for q in questions], return_exceptions=True)
        return {q: (str(r) if not isinstance(r, Exception) else f"Error: {r}") for q, r in zip(questions, completed)}
