"""Plugin loader — auto-discovers plugins from multiple search paths."""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import logging
import pkgutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type

logger = logging.getLogger(__name__)


class PluginInterface:
    """Base class that all plugins should inherit from."""

    plugin_name: str = ""
    plugin_version: str = "0.1.0"
    plugin_description: str = ""

    @classmethod
    def initialize(cls) -> None:
        """Called when the plugin is loaded."""


class PluginLoader:
    """Discovers and loads plugins from multiple search paths.

    Searches in order:
        1. videomarker/plugins/ (built-in)
        2. plugins/community/ (community contributed)
        3. plugins/local/ (user local)
        4. Any additional registered paths
    """

    _loaded: bool = False
    _plugins: Dict[str, Type[PluginInterface]] = {}
    _search_paths: List[Path] = []

    @classmethod
    def add_path(cls, path: Path) -> None:
        cls._search_paths.append(path.resolve())

    @classmethod
    def discover(cls, force: bool = False) -> Dict[str, Type[PluginInterface]]:
        if cls._loaded and not force:
            return cls._plugins

        paths = cls._get_search_paths()
        for path in paths:
            if path.exists():
                cls._scan_path(path)

        cls._loaded = True
        logger.info("Discovered %d plugins from %d paths", len(cls._plugins), len(paths))
        return cls._plugins

    @classmethod
    def _get_search_paths(cls) -> List[Path]:
        base = Path(__file__).parent
        paths = [
            base,           # videomarker/plugins/
            base / "community",
            base / "local",
        ]
        paths.extend(cls._search_paths)
        return paths

    @classmethod
    def _scan_path(cls, path: Path) -> None:
        sys.path.insert(0, str(path))
        for file_path in path.glob("*.py"):
            if file_path.name.startswith("_") or file_path.name == "loader.py":
                continue
            try:
                module_name = file_path.stem
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    cls._scan_module(module)
            except Exception as e:
                logger.warning("Failed to load plugin %s: %s", file_path.name, e)

    @classmethod
    def _scan_module(cls, module: object) -> None:
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, PluginInterface)
                and obj is not PluginInterface
                and obj.plugin_name
            ):
                cls._plugins[obj.plugin_name] = obj
                logger.debug("Discovered plugin: %s v%s", obj.plugin_name, obj.plugin_version)

    @classmethod
    def get_plugin(cls, name: str) -> Optional[Type[PluginInterface]]:
        cls.discover()
        return cls._plugins.get(name)

    @classmethod
    def list_plugins(cls) -> Dict[str, str]:
        cls.discover()
        return {name: plugin.plugin_description for name, plugin in cls._plugins.items()}

    @classmethod
    def reset(cls) -> None:
        cls._plugins.clear()
        cls._loaded = False
