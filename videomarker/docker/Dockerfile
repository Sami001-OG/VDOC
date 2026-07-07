FROM python:3.11-slim

LABEL org.opencontainers.image.title="VDOC"
LABEL org.opencontainers.image.description="Convert videos to structured MarkDirectory"
LABEL org.opencontainers.image.license="Apache-2.0"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml README.md ./
COPY vdoc/ ./vdoc/

# Install Python dependencies
RUN pip install --no-cache-dir -e ".[all]"

# Volume for input/output
VOLUME ["/data"]

# Expose API port
EXPOSE 8080

# Default command
CMD ["vdoc", "--help"]
