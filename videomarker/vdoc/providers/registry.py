"""ProviderRegistry — central registry for all providers with multi-provider support."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Type

from vdoc.providers.base import BaseProvider, ProviderCapability, ProviderConfig

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """Central registry that manages provider lifecycle.

    Supports:
        - Multiple providers of the same type (#30)
        - Provider lookup by capability (#22)
        - Automatic fallback chains (#29)
    """

    _providers: Dict[str, BaseProvider] = {}
    _factories: Dict[str, Type[BaseProvider]] = {}
    _named_instances: Dict[str, Dict[str, BaseProvider]] = {}

    @classmethod
    def register(cls, name: str, factory: Type[BaseProvider]) -> None:
        """Register a provider class by name."""
        cls._factories[name] = factory
        logger.debug("Registered provider factory: %s → %s", name, factory.__name__)

    @classmethod
    async def get(cls, name: str, config: Optional[ProviderConfig] = None) -> BaseProvider:
        """Get or create a provider instance by name."""
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
    def register_instance(cls, name: str, instance_name: str, provider: BaseProvider) -> None:
        """Register a named instance of a provider (multi-provider support)."""
        if name not in cls._named_instances:
            cls._named_instances[name] = {}
        cls._named_instances[name][instance_name] = provider

    @classmethod
    async def get_instance(cls, name: str, instance_name: str) -> Optional[BaseProvider]:
        """Get a specific named instance of a provider type."""
        return cls._named_instances.get(name, {}).get(instance_name)

    @classmethod
    def get_by_capability(cls, capability: ProviderCapability) -> List[BaseProvider]:
        """Get all providers that support a given capability."""
        result = []
        for provider in cls._providers.values():
            if provider.supports(capability):
                result.append(provider)
        for instances in cls._named_instances.values():
            for provider in instances.values():
                if provider.supports(capability) and provider not in result:
                    result.append(provider)
        return result

    @classmethod
    async def close_all(cls) -> None:
        for name, provider in cls._providers.items():
            try:
                await provider.close()
                logger.info("Provider closed: %s", name)
            except Exception as e:
                logger.warning("Error closing provider %s: %s", name, e)
        for name, instances in cls._named_instances.items():
            for iname, provider in instances.items():
                try:
                    await provider.close()
                except Exception as e:
                    logger.warning("Error closing %s/%s: %s", name, iname, e)
        cls._providers.clear()
        cls._named_instances.clear()

    @classmethod
    def list_available(cls) -> Dict[str, str]:
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

    @classmethod
    async def health_check_all(cls) -> Dict[str, bool]:
        """Run health checks on all initialized providers (#23)."""
        results: Dict[str, bool] = {}
        for name, provider in cls._providers.items():
            results[name] = await provider.health_check()
        return results
