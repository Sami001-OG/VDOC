# Design Principles

1. **Single Source of Truth**: `VideoDocument` is the canonical data model. Everything reads from and writes to it.

2. **Provider Abstraction**: No code calls AI/ML libraries directly. All AI goes through provider interfaces.

3. **Layered Architecture**: CLI/API → Services → Pipeline → Providers. Each layer only depends on the layer below.

4. **Stateless Stages**: Pipeline stages accept context and return context. No mutable state.

5. **Renderer Simplicity**: Renderers convert `VideoDocument` to output format. No business logic, no AI calls.

6. **Resumability**: Every pipeline stage is restartable. Checkpoints persist full context.

7. **Deterministic Rendering**: Same input → same output. No randomness in renderers.

8. **Configuration Layering**: CLI > YAML > .env > profiles > defaults. Every option is validated.

9. **Plugin Extensibility**: Custom stages, renderers, and providers via plugin interface.

10. **Fail Fast**: Validate inputs early. Clear error messages.
