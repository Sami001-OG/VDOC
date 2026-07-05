# Changelog

## 0.1.0 (2026-07-05)

- Initial release
- Core pipeline architecture with plugin system
- Provider system with DI (ProviderRegistry)
- Video provider with FFmpeg metadata extraction
- Frame extraction via OpenCV
- Audio extraction via FFmpeg
- Scene detection via PySceneDetect
- Timeline builder with auto-chapterization
- Speech/transcript provider with faster-whisper
- OCR provider with PaddleOCR
- Vision provider with OpenAI-compatible VLMs
- LLM provider with OpenAI-compatible models
- Embedding provider with sentence-transformers
- Knowledge graph: Entity/Relation extraction and querying
- Semantic search engine with FAISS + brute-force fallback
- VideoDocument model (single source of truth, typed dataclasses)
- PipelineOrchestrator with checkpoint/resume
- 7 pipeline stages: Video, SceneDetection, Speech, OCR, Vision, LLM, Render
- 4 renderers: MarkDirectory, Markdown, JSON, HTML
- CLI with 9 subcommands: process, summarize, transcript, search, export, plugin, config, doctor, benchmark
- REST API with FastAPI (8 endpoints)
- Web UI dashboard (Next.js, dark theme, 37 files)
- ConfigManager with layered priority (CLI > YAML > .env > defaults)
- Plugin auto-discovery from plugins/, plugins/community/, plugins/local/
- Agent system: BaseAgent, SimpleAgent, AgentOrchestrator
- Docker + docker-compose support
- GitHub Actions CI (lint, test, docker)
- Logo (fold mark + wordmark, monochrome-first)
