"""Prompt template loader and registry."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import BaseLoader, ChoiceLoader, Environment, FileSystemLoader, TemplateNotFound

logger = logging.getLogger(__name__)

_PROMPT_DIR = Path(__file__).parent

class _InlineLoader(BaseLoader):
    """Loader for programmatically registered prompt templates."""
    def __init__(self) -> None:
        self._templates: Dict[str, str] = {}

    def register(self, name: str, source: str) -> None:
        self._templates[name] = source

    def get_source(self, environment: Environment, template_name: str) -> tuple:
        if template_name in self._templates:
            return self._templates[template_name], template_name, True
        raise TemplateNotFound(template_name)


_inline_loader = _InlineLoader()
_env = Environment(
    loader=ChoiceLoader([FileSystemLoader(str(_PROMPT_DIR)), _inline_loader]),
    trim_blocks=True,
    lstrip_blocks=True,
)


def render(template_name: str, **kwargs: Any) -> str:
    """Load and render a prompt template by name.

    Args:
        template_name: Relative path under prompts/ (e.g. "llm/transcript_analysis.j2")
        **kwargs: Variables to substitute into the template.

    Returns:
        Rendered prompt string.

    Raises:
        FileNotFoundError: If the template does not exist.
    """
    try:
        template = _env.get_template(template_name)
        return template.render(**kwargs)
    except TemplateNotFound:
        logger.error("Prompt template not found: %s", template_name)
        raise FileNotFoundError(f"Prompt template not found: {template_name}")


def register_prompt(name: str, template_text: str) -> None:
    """Programmatically register a prompt template without breaking file-based lookups."""
    _inline_loader.register(name, template_text)
