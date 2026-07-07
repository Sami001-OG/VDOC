"""Plugin implementation for {{cookiecutter.display_name}}."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from vdoc.sdk import (
    BaseProvider,
    PipelineContext,
    PipelineStage,
    PluginInterface,
    ProviderCapability,
    ProviderConfig,
)
from vdoc.sdk.exceptions import ProviderError

logger = logging.getLogger(__name__)

{% if cookiecutter.plugin_type == "provider" %}

class {{cookiecutter.plugin_class}}(BaseProvider):
    """{{cookiecutter.display_name}} provider."""

    capabilities = {
        ProviderCapability.TEXT_GENERATION,
    }

    def __init__(self, config: Optional[ProviderConfig] = None) -> None:
        super().__init__(config)
        self._client = None

    async def initialize(self) -> None:
        logger.info("Initializing {{cookiecutter.plugin_class}}")
        self._client = await self._create_client()
        self.status = ProviderStatus.READY

    async def _health_check_impl(self) -> bool:
        return self._client is not None

    async def _create_client(self):
        # TODO: initialize your API client here
        return {"ready": True}

    async def process(self, prompt: str, **kwargs: Any) -> str:
        if not self._client:
            raise ProviderError("Provider not initialized")
        # TODO: call your AI provider
        return f"Processed: {prompt[:50]}..."

    async def close(self) -> None:
        self._client = None
        await super().close()

{% elif cookiecutter.plugin_type == "processor" %}

class {{cookiecutter.plugin_class}}(PipelineStage):
    """{{cookiecutter.display_name}} pipeline stage."""

    stage_name = "{{cookiecutter.plugin_name}}"
    parallel_group = "{{cookiecutter.plugin_name}}"

    async def validate(self, ctx: PipelineContext) -> bool:
        # TODO: check prerequisites
        return True

    async def execute(self, ctx: PipelineContext) -> PipelineContext:
        logger.info("Running {{cookiecutter.plugin_class}} stage")
        # TODO: process the video data
        return ctx

{% elif cookiecutter.plugin_type == "renderer" %}

from vdoc.sdk import BaseRenderer
from vdoc.sdk.exceptions import RendererError


class {{cookiecutter.plugin_class}}(BaseRenderer):
    """{{cookiecutter.display_name}} renderer."""

    RENDERER_VERSION = "1.0.0"

    async def render(self, document, output_dir: str) -> None:
        logger.info("Rendering with {{cookiecutter.plugin_class}}")
        # TODO: convert document to output format
        pass

{% endif %}
