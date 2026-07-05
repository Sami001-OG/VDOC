# Contributing to VideoMarker

We welcome contributions of all kinds!

## Development Setup

```bash
git clone https://github.com/yourusername/videomarker
cd videomarker
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev,all]"
```

## Code Quality

```bash
# Lint
ruff check .

# Type check
mypy videomarker

# Test
pytest
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Write tests for your changes
4. Ensure all checks pass
5. Submit a PR with a clear description

## Adding Processors

See the [Plugin Development Guide](docs/guides/plugin_development.md).

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).
