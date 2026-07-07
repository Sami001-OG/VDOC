"""ProviderRegistry — central registry for all providers with dependency injection."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Type

from videomarker.providers.base import BaseProvider, ProviderConfig

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """Central registry that manages provider lifecycle.

    No code should instantiate OpenAI(), WhisperModel(), or PaddleOCR()
    directly. Everything comes through this registry.
    """

    _providers: Dict[str, BaseProvider] = {}
    _factories: Dict[str, Type[BaseProvider]] = {}

    @classmethod
    def register(cls, name: str, factory: Type[BaseProvider]) -> None:
        """Register a provider class by name."""
        cls._factories[name] = factory
        logger.debug("Registered provider factory: %s → %s", name, factory.__name__)

    @classmethod
    async def get(cls, name: str, config: Optional[ProviderConfig] = None) -> BaseProvider:
        """Get or create a provider instance.

        Args:
            name: Provider name (e.g. "openai", "whisper", "paddle").
            config: Optional provider configuration.

        Returns:
            An initialized provider instance.
        """
        if name in cls._providers:
            provider = cls._providers[name]
            if provider.is_ready:
                return provider
            await provider.initialize()
            return provider

        factory = cls._factories.get(name)
        if not factory:
            raise ValueError(f"No provider registered: {name}. Available: {list(cls._factories.keys())}")

        provider = factory(config)
        cls._providers[name] = provider
        await provider.initialize()
        logger.info("Provider initialized: %s (%s)", name, provider.config.model)
        return provider

    @classmethod
    async def close_all(cls) -> None:
        """Close all providers and release resources."""
        for name, provider in cls._providers.items():
            try:
                await provider.close()
                logger.info("Provider closed: %s", name)
            except Exception as e:
                logger.warning("Error closing provider %s: %s", name, e)
        cls._providers.clear()

    @classmethod
    def list_available(cls) -> Dict[str, str]:
        """List all registered providers and their status."""
        result: Dict[str, str] = {}
        for name, factory in cls._factories.items():
            if name in cls._providers:
                result[name] = cls._providers[name].status.value
            else:
                result[name] = "registered"
        return result

    @classmethod
    def is_registered(cls, name: str) -> bool:
        return name in cls._factories
