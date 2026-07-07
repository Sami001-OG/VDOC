# Provider Tutorial

Providers abstract AI/ML services behind a common interface.

## Built-in Providers

| Category | Provider | Config Key |
|----------|----------|------------|
| LLM | OpenAI Compatible | `llm_provider` |
| Speech | Whisper (faster-whisper) | `speech_provider` |
| Vision | OpenAI Vision | `vision_provider` |
| OCR | PaddleOCR | `ocr_provider` |
| Embedding | Sentence Transformers | `embedding_provider` |
| Video | FFmpeg | `video_provider` |
| Search | FAISS | (internal) |

## Creating a Custom Provider

```python
from vdoc.providers.base import (
    BaseProvider, ProviderCapability, ProviderConfig, ProviderStatus
)


class MyLLMProvider(BaseProvider):
    capabilities = {ProviderCapability.TEXT_GENERATION, ProviderCapability.CHAT}

    async def initialize(self):
        self._client = ...
        self.status = ProviderStatus.READY

    async def process(self, **kwargs):
        return self._client.generate(kwargs["prompt"])

    async def close(self):
        self._client.close()


# Register with the registry
from vdoc.providers.registry import ProviderRegistry
ProviderRegistry.register("my-llm", MyLLMProvider)

# Use it in config
# vdoc config --set llm_provider=my-llm
```

## Provider Capabilities

Each provider declares what it can do:

```python
class MyProvider(BaseProvider):
    capabilities = {
        ProviderCapability.TEXT_GENERATION,
        ProviderCapability.STREAMING,
    }
```

Check at runtime:

```python
if provider.supports(ProviderCapability.STREAMING):
    async for chunk in provider.stream(...):
        process(chunk)
```
