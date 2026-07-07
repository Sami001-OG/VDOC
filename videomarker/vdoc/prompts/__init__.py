"""Prompt template loader and registry."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

logger = logging.getLogger(__name__)

_PROMPT_DIR = Path(__file__).parent
_env = Environment(
    loader=FileSystemLoader(str(_PROMPT_DIR)),
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
    """Programmatically register a prompt template."""
    from jinja2 import BaseLoader, Environment

    class _InlineLoader(BaseLoader):
        def get_source(self, environment, template_name):
            if template_name == name:
                return template_text, name, True
            raise TemplateNotFound(template_name)

    _env.loader = _InlineLoader()
