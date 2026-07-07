# VDOC REST API

## Overview

VDOC provides a FastAPI-based REST API for processing videos and accessing results.

**Base URL**: `http://localhost:8080`

**Interactive docs**: `/docs` (Swagger UI) or `/redoc` (ReDoc)

---

## Endpoints

### Health Check

```http
GET /health
```

**Response**:
```json
{"status": "healthy", "version": "0.1.0"}
```

---

### Process Video

```http
POST /process
```

Upload a video file and start processing.

**Request** (multipart/form-data):
| Field | Type | Description |
|-------|------|-------------|
| file | File | Video file (mp4, mov, avi, etc.) |
| config | string (optional) | JSON configuration overrides |

**Response** (202 Accepted):
```json
{
  "id": "8a3f1b2c",
  "status": "processing",
  "video": "demo.mp4",
  "video_path": "/tmp/vdoc_8a3f1b2c/demo.mp4",
  "output_dir": "/tmp/vdoc_8a3f1b2c/demo.markdir"
}
```

---

### Get Job Status

```http
GET /status/{job_id}
```

**Response**:
```json
{
  "id": "8a3f1b2c",
  "status": "completed",
  "video": "demo.mp4",
  "output_dir": "/tmp/vdoc_8a3f1b2c/demo.markdir",
  "errors": {}
}
```

Status values: `processing`, `completed`, `failed`

---

### Semantic Search

```http
POST /search
```

Search within a processed video's content.

**Request** (form data):
| Field | Type | Description |
|-------|------|-------------|
| job_id | string | Job ID from `/process` |
| query | string | Natural language query |
| top_k | int (default: 10) | Number of results |

**Response**:
```json
[
  {
    "id": "scene_005",
    "text": "The architecture uses microservices deployed on Kubernetes...",
    "score": 0.89,
    "source_type": "transcript",
    "timestamp": 42.5
  }
]
```

---

### Get Scene

```http
GET /scene/{job_id}/{scene_number}
```

**Response**:
```json
{
  "scene_number": 5,
  "files": {
    "metadata.json": "{...}",
    "transcript.md": "Speaker discusses architecture patterns...",
    "ocr.md": "Diagram showing microservices architecture"
  },
  "metadata": {
    "number": 5,
    "start_time": 42.5,
    "end_time": 58.2,
    "duration": 15.7,
    "description": "Architecture overview section"
  }
}
```

---

### Get Summary

```http
GET /summary/{job_id}
```

**Response**: Raw markdown content of the video summary.

---

### Get Timeline

```http
GET /timeline/{job_id}
```

**Response**:
```json
{
  "duration": 360.0,
  "scenes": [
    {
      "id": "f8e3a1",
      "number": 1,
      "start_time": 0.0,
      "end_time": 12.5,
      "description": "Introduction"
    }
  ]
}
```

---

### Download MarkDirectory

```http
GET /download/{job_id}
```

**Response**: ZIP file containing the complete MarkDirectory.

---

### List Processors

```http
GET /processors
```

**Response**:
```json
[
  {
    "name": "my_custom_plugin",
    "description": "Custom analysis plugin"
  }
]
```

---

## Client Examples

### Python

```python
import httpx

# Upload and process
with open("video.mp4", "rb") as f:
    res = httpx.post("http://localhost:8080/process",
                     files={"file": f})
    job = res.json()

# Poll until complete
job_id = job["id"]
while True:
    status = httpx.get(f"http://localhost:8080/status/{job_id}").json()
    if status["status"] in ("completed", "failed"):
        break

# Search
res = httpx.post("http://localhost:8080/search",
                 data={"job_id": job_id, "query": "architecture"})
results = res.json()
```

### cURL

```bash
# Upload video
curl -X POST http://localhost:8080/process \
  -F "file=@demo.mp4"

# Check status
curl http://localhost:8080/status/8a3f1b2c

# Search
curl -X POST http://localhost:8080/search \
  -d "job_id=8a3f1b2c" \
  -d "query=deployment" \
  -d "top_k=5"

# Download results
curl -O http://localhost:8080/download/8a3f1b2c
```
