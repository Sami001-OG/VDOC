# Coding Standards

## Python

- Target Python 3.10+
- Use type hints everywhere
- Use `from __future__ import annotations` in all files
- Dataclasses for data objects, not dicts
- ABCs for interfaces, not duck typing
- Async/await for I/O and AI calls

## Imports

```python
# Standard library
from __future__ import annotations
import json
from pathlib import Path

# Third-party
import typer
from pydantic import BaseModel

# Internal
from vdoc.pipeline.base import PipelineContext
```

## Naming

- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_CASE`
- Private: `_leading_underscore`
- Type vars: short `T`, `F`

## Testing

- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- One test class per tested class
- Test public API only
- Mock AI providers, not internal logic
