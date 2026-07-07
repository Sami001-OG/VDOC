"""OpenAI-compatible LLM provider — works with OpenAI, OpenRouter, Groq, Ollama, etc."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from vdoc.providers.base import ProviderCapability, ProviderConfig, ProviderStatus, retry
from vdoc.providers.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class OpenAICompatibleProvider(LLMProvider):
    """Provider for any OpenAI-compatible API endpoint.

    Change BASE_URL + API_KEY + MODEL in .env to switch between:
    OpenAI, OpenRouter, Groq, Ollama, LM Studio, vLLM, SGLang, Cerebras.
    """

    capabilities = {ProviderCapability.TEXT_GENERATION, ProviderCapability.CHAT, ProviderCapability.EMBEDDING}

    def __init__(self, config: Optional[ProviderConfig] = None) -> None:
        super().__init__(config)
        self._client: Optional[AsyncOpenAI] = None

    async def initialize(self) -> None:
        self._client = AsyncOpenAI(
            base_url=self.config.extra.get("base_url", "https://api.openai.com/v1"),
            api_key=self.config.extra.get("api_key", ""),
            max_retries=self.config.max_retries,
            timeout=self.config.timeout,
        )
        self.status = ProviderStatus.READY
        logger.info("LLM provider ready: %s", self.config.extra.get("base_url"))

    @retry(max_attempts=3)
    async def complete(
        self, prompt: str, system: Optional[str] = None, **kwargs: Any
    ) -> str:
        if not self._client:
            raise RuntimeError("Provider not initialized")
        await self._throttle()
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return await self.chat(messages, **kwargs)

    @retry(max_attempts=3)
    async def chat(
        self, messages: List[Dict[str, str]], **kwargs: Any
    ) -> str:
        if not self._client:
            raise RuntimeError("Provider not initialized")
        await self._throttle()
        cache_key = self._cache_key(messages=messages, **kwargs)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        response = await self._client.chat.completions.create(
            model=self.config.model or kwargs.get("model", "gpt-4o"),
            messages=messages,
            temperature=kwargs.get("temperature", 0.1),
            max_tokens=kwargs.get("max_tokens", 4096),
        )
        result = response.choices[0].message.content or ""
        self._cache.set(cache_key, result)
        return result

    @retry(max_attempts=2)
    async def embed(self, texts: List[str]) -> List[List[float]]:
        if not self._client:
            raise RuntimeError("Provider not initialized")
        await self._throttle()
        model = self.config.extra.get("embedding_model", "text-embedding-3-small")
        response = await self._client.embeddings.create(model=model, input=texts)
        return [d.embedding for d in response.data]

    async def close(self) -> None:
        await self._client.close() if self._client else None
        self.status = ProviderStatus.CLOSED
