# Contributor Roadmap

## Current Priorities

1. **Multi-video projects** (#121)
2. **Knowledge graph visualization** (#122)
3. **Semantic search UI** (#123)
4. **AI chat over videos** (#124)
5. **Speaker diarization** (#125)
6. **Live stream support** (#126)
7. **Distributed workers** (#127)
8. **GPU scheduling** (#128)
9. **Browser extension** (#129)

## How to Contribute

1. Fork the repository
2. Pick an item from the roadmap
3. Create a feature branch
4. Implement with tests
5. Submit a PR

## Development Setup

```bash
git clone https://github.com/vdoc/vdoc
cd vdoc
pip install -e ".[dev,audio,search]"
vdoc doctor  # verify dependencies
```

## Code Review

- All PRs require tests
- All PRs require documentation
- Follow coding standards (see CODING_STANDARDS.md)
- Keep renderers free of business logic
- All AI goes through provider interfaces
