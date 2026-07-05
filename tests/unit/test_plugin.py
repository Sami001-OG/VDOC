"""Tests for the plugin system."""

from videomarker.core.plugin import PluginRegistry, ProcessorPlugin, processor
from videomarker.core.processor import Processor


class TestPluginRegistry:
    def setup_method(self):
        PluginRegistry.reset()

    def test_register_and_get_plugin(self):
        class TestProcessor(Processor):
            def process(self, context):
                pass

        plugin = ProcessorPlugin(
            name="test",
            processor_class=TestProcessor,
            priority=50,
        )
        PluginRegistry.register(plugin)
        assert PluginRegistry.get_plugin("test") is not None
        assert PluginRegistry.get_plugin("test").name == "test"

    def test_get_all_plugins_sorted(self):
        class LowPriorityProcessor(Processor):
            def process(self, context):
                pass

        class HighPriorityProcessor(Processor):
            def process(self, context):
                pass

        PluginRegistry.register(
            ProcessorPlugin(name="low", processor_class=LowPriorityProcessor, priority=100)
        )
        PluginRegistry.register(
            ProcessorPlugin(name="high", processor_class=HighPriorityProcessor, priority=10)
        )

        plugins = PluginRegistry.get_all_plugins()
        assert plugins[0].name == "high"
        assert plugins[1].name == "low"

    def test_processor_decorator(self):
        @processor("decorated_test", dependencies=[], priority=25)
        class DecoratedProcessor(Processor):
            def process(self, context):
                pass

        plugin = PluginRegistry.get_plugin("decorated_test")
        assert plugin is not None
        assert plugin.priority == 25
        assert plugin.name == "decorated_test"
