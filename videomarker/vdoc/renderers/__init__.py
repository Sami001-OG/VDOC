"""Renderers — convert VideoDocument to output formats."""

from vdoc.renderers.base import BaseRenderer
from vdoc.renderers.html_renderer import HTMLRenderer
from vdoc.renderers.json_renderer import JSONRenderer
from vdoc.renderers.markdirectory import MarkDirectoryRenderer
from vdoc.renderers.markdown import MarkdownRenderer
from vdoc.renderers.registry import RendererRegistry

# Register built-in renderers
RendererRegistry.register("markdirectory", MarkDirectoryRenderer)
RendererRegistry.register("markdown", MarkdownRenderer)
RendererRegistry.register("json", JSONRenderer)
RendererRegistry.register("html", HTMLRenderer)

__all__ = [
    "BaseRenderer",
    "HTMLRenderer",
    "JSONRenderer",
    "MarkDirectoryRenderer",
    "MarkdownRenderer",
    "RendererRegistry",
]
