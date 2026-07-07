# Sequence Diagrams

## Full Pipeline

```
User          CLI              PipelineService     PipelineOrchestrator    Providers
 │             │                     │                     │                  │
 │  vdoc process  │                     │                     │                  │
 │─────────────▶  │  load_config()      │                     │                  │
 │                │────────────────────▶│                     │                  │
 │                │  build_pipeline()   │                     │                  │
 │                │────────────────────▶│                     │                  │
 │                │  run_sync()         │                     │                  │
 │                │────────────────────▶│                     │                  │
 │                │                     │  run()              │                  │
 │                │                     │────────────────────▶│                  │
 │                │                     │                     │  stage.started   │
 │                │                     │                     │────────────────▶│
 │                │                     │                     │  validate()      │
 │                │                     │                     │◀────────────────│
 │                │                     │                     │  execute()       │
 │                │                     │                     │────────────────▶│
 │                │                     │                     │  stage.completed │
 │                │                     │                     │◀────────────────│
 │                │                     │  ◄─── return ctx ──│                  │
 │                │  ◄─── return ctx ───│                     │                  │
 │  ◄─── done ────│                     │                     │                  │
```

## Resumable Pipeline (interrupted then resumed)

```
User          CLI              PipelineOrchestrator     Checkpoint File
 │             │                     │                     │
 │  vdoc process --resume            │                     │
 │─────────────▶                     │                     │
 │             │  _load_checkpoint() │                     │
 │             │────────────────────▶│                     │
 │             │  ◄─── data ─────────│                     │
 │             │                     │                     │
 │             │  skip completed      │                     │
 │             │  stages              │                     │
 │             │                     │                     │
 │             │  run remaining       │                     │
 │             │  stages              │                     │
 │             │                     │                     │
 │             │  _save_checkpoint() │                     │
 │             │────────────────────▶│                     │
```
