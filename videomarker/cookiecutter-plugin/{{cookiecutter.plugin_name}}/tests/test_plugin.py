"""Tests for {{cookiecutter.display_name}} plugin."""

from {{cookiecutter.python_package}} import {{cookiecutter.plugin_class}}


def test_plugin_import():
    assert {{cookiecutter.plugin_class}} is not None


def test_plugin_instantiate():
    instance = {{cookiecutter.plugin_class}}()
    assert instance is not None
