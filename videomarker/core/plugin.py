"""Plugin system for automatic discovery and registration of processors."""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import logging
import pkgutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Type

from videomarker.core.processor import Processor

logger = logging.getLogger(__name__)


class ProcessorPlugin:
    """Wrapper for a processor class discovered via the plugin system.

    Attributes:
        name: Unique name of the processor.
        processor_class: The processor class.
        dependencies: Optional list of processor names this depends on.
        priority: Execution priority (lower = earlier).
    """

    def __init__(
        self,
        name: str,
        processor_class: Type[Processor],
        dependencies: Optional[List[str]] = None,
        priority: int = 100,
    ) -> None:
        self.name = name
        self.processor_class = processor_class
        self.dependencies = dependencies or []
        self.priority = priority

    def instantiate(self, **kwargs: object) -> Processor:
        """Create an instance of the processor."""
        return self.processor_class(**kwargs)


class PluginRegistry:
    """Global registry for discovering and managing processor plugins.

    Automatically discovers processors from installed packages and
    user-specified plugin directories.
    """

    _plugins: Dict[str, ProcessorPlugin] = {}
    _discovered: bool = False
    _search_paths: Set[Path] = set()

    @classmethod
    def register(cls, plugin: ProcessorPlugin) -> None:
        """Register a processor plugin."""
        if plugin.name in cls._plugins:
            logger.warning("Overwriting existing plugin: %s", plugin.name)
        cls._plugins[plugin.name] = plugin
        logger.debug("Registered plugin: %s", plugin.name)

    @classmethod
    def get_plugin(cls, name: str) -> Optional[ProcessorPlugin]:
        """Get a registered plugin by name."""
        cls.discover()
        return cls._plugins.get(name)

    @classmethod
    def get_all_plugins(cls) -> List[ProcessorPlugin]:
        """Get all registered plugins sorted by priority."""
        cls.discover()
        return sorted(cls._plugins.values(), key=lambda p: p.priority)

    @classmethod
    def add_search_path(cls, path: Path) -> None:
        """Add a directory to search for plugins."""
        cls._search_paths.add(path.resolve())

    @classmethod
    def discover(cls, force: bool = False) -> None:
        """Discover plugins from all registered paths and standard locations."""
        if cls._discovered and not force:
            return

        # Discover from videomarker.processors subpackage
        cls._discover_from_package("videomarker.processors")

        # Discover from custom search paths
        for path in cls._search_paths:
            cls._discover_from_path(path)

        # Discover from entry points
        cls._discover_from_entrypoints()

        cls._discovered = True
        logger.info("Discovered %d processor plugins", len(cls._plugins))

    @classmethod
    def _discover_from_package(cls, package_name: str) -> None:
        """Discover processors in a Python package."""
        try:
            package = importlib.import_module(package_name)
            for importer, modname, ispkg in pkgutil.walk_packages(
                package.__path__, package.__name__ + "."
            ):
                try:
                    module = importlib.import_module(modname)
                    cls._scan_module(module)
                except Exception as e:
                    logger.debug("Failed to load module %s: %s", modname, e)
        except ImportError:
            logger.debug("Package %s not found, skipping discovery", package_name)

    @classmethod
    def _discover_from_path(cls, path: Path) -> None:
        """Discover processors from a filesystem path."""
        if not path.exists() or not path.is_dir():
            logger.warning("Plugin path does not exist: %s", path)
            return

        sys.path.insert(0, str(path))

        for file_path in path.glob("*.py"):
            if file_path.name.startswith("_"):
                continue
            module_name = file_path.stem
            try:
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    cls._scan_module(module)
            except Exception as e:
                logger.warning("Failed to load plugin %s: %s", file_path, e)

    @classmethod
    def _discover_from_entrypoints(cls) -> None:
        """Discover processors via entry points (experimental)."""
        try:
            from importlib.metadata import entry_points
            eps = entry_points(group="videomarker.processors")
            for ep in eps:
                try:
                    processor_class = ep.load()
                    cls._register_processor_class(processor_class)
                except Exception as e:
                    logger.warning("Failed to load entry point %s: %s", ep.name, e)
        except Exception:
            pass

    @classmethod
    def _scan_module(cls, module: object) -> None:
        """Scan a module for Processor subclasses."""
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, Processor)
                and obj is not Processor
                and hasattr(obj, "__processor_name__")
            ):
                cls._register_processor_class(obj)

    @classmethod
    def _register_processor_class(cls, processor_class: Type[Processor]) -> None:
        """Register a processor class if it has a processor name."""
        name = getattr(processor_class, "__processor_name__", None)
        if name:
            plugin = ProcessorPlugin(
                name=name,
                processor_class=processor_class,
                dependencies=getattr(processor_class, "__processor_dependencies__", []),
                priority=getattr(processor_class, "__processor_priority__", 100),
            )
            cls.register(plugin)

    @classmethod
    def reset(cls) -> None:
        """Reset the registry (useful for testing)."""
        cls._plugins.clear()
        cls._discovered = False


def processor(
    name: str,
    dependencies: Optional[List[str]] = None,
    priority: int = 100,
) -> callable:
    """Decorator to register a processor class with metadata.

    Usage:
        @processor("transcript", dependencies=["audio"], priority=10)
        class TranscriptProcessor(Processor):
            ...
    """
    def decorator(cls: type) -> type:
        cls.__processor_name__ = name
        cls.__processor_dependencies__ = dependencies or []
        cls.__processor_priority__ = priority

        # Auto-register if the class is defined
        PluginRegistry.register(
            ProcessorPlugin(
                name=name,
                processor_class=cls,
                dependencies=dependencies or [],
                priority=priority,
            )
        )
        return cls

    return decorator



