# Extension Guide

## Adding a New Pipeline Stage

1. Create `vdoc/pipeline/stages/mystage.py`
2. Inherit from `PipelineStage`
3. Implement `execute()` and `validate()`
4. Register in `__init__.py` and `PipelineService.STAGE_MAP`

```python
from vdoc.pipeline.base import PipelineContext, PipelineStage

class MyStage(PipelineStage):
    stage_name = "my_stage"

    async def execute(self, ctx: PipelineContext) -> PipelineContext:
        ctx.my_output = {"result": "processed"}
        return ctx

    async def validate(self, ctx: PipelineContext) -> bool:
        return bool(ctx.video_path)
```

## Adding a New Renderer

1. Create `vdoc/renderers/my_renderer.py`
2. Inherit from `BaseRenderer`
3. Implement `render()`
4. Register in `RenderStage._get_renderer()`

```python
from pathlib import Path
from vdoc.models.document import VideoDocument
from vdoc.renderers.base import BaseRenderer

class MyRenderer(BaseRenderer):
    format_name = "myformat"

    def render(self, doc: VideoDocument, output_dir: Path) -> Path:
        out = output_dir / "output.myformat"
        out.write_text(str(doc))
        return out
```

## Adding a New Config Option

1. Add field to `ConfigSchema` in `config/manager.py`
2. Add validation in `config/validator.py`
3. Add CLI flag in `cli/main.py`
4. Document in `docs/CONFIGURATION.md`
