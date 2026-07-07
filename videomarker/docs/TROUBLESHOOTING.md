# Troubleshooting

## Common Issues

### `ModuleNotFoundError: No module named 'jinja2'`

```bash
pip install jinja2
```

### `FFmpeg not found`

Install FFmpeg:
- **Windows**: `winget install ffmpeg` or download from ffmpeg.org
- **macOS**: `brew install ffmpeg`
- **Linux**: `apt install ffmpeg`

### `CUDA out of memory`

Reduce `max_frames` or use `device=cpu` in config.

### `Pipeline failed: No provider registered`

Run `vdoc doctor` to check dependencies. Install missing packages:

```bash
pip install vdoc[audio]    # for speech recognition
pip install vdoc[vision]   # for vision analysis
pip install vdoc[search]   # for semantic search
```

### `OpenAI API key not set`

Set in `.env`:

```env
LLM_API_KEY=sk-your-key-here
```

Or pass via CLI: `--config config.yaml`

### Pipeline takes too long

Use `--profile fast` for quicker processing:

```bash
vdoc process video.mp4 --profile fast
```

### Checkpoint not resuming

Clear the checkpoint and restart:

```bash
rm -rf output.markdir/.checkpoints
vdoc process video.mp4 --overwrite
```
