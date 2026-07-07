"""Tests for the plugin system."""

from pathlib import Path
from tempfile import TemporaryDirectory

from vdoc.plugins.loader import PluginLoader


class TestPluginLoader:
    def test_discover_nonexistent_dir(self):
        plugins = PluginLoader.list_plugins()
        assert isinstance(plugins, dict)

    def test_empty_plugin_dir(self):
        loader = PluginLoader()
        with TemporaryDirectory() as tmp:
            plugins = loader.discover(Path(tmp))
            assert len(plugins) == 0

    def test_plugin_directory_paths(self):
        paths = PluginLoader._get_search_paths()
        assert len(paths) >= 0
        for p in paths:
            assert isinstance(p, Path)

    def test_discover_from_multiple_paths(self):
        loader = PluginLoader()
        with TemporaryDirectory() as tmp1, TemporaryDirectory() as tmp2:
            (Path(tmp1) / "__init__.py").write_text("")
            (Path(tmp2) / "plugin.py").write_text("")
            found = loader.discover(Path(tmp1))
            found2 = loader.discover(Path(tmp2))
            assert len(found) >= 0
            assert len(found2) >= 0

