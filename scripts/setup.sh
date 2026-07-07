#!/usr/bin/env bash
set -euo pipefail

echo "=== VideoMarker Setup ==="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# Install with dev dependencies
echo "Installing VideoMarker..."
pip install -e ".[dev,all]"

# Setup pre-commit hooks
if command -v pre-commit &> /dev/null; then
    echo "Setting up pre-commit hooks..."
    pre-commit install
fi

# Copy .env if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env from .env.example — edit it with your API keys."
fi

echo ""
echo "=== Setup Complete ==="
echo "Run 'source .venv/bin/activate' to activate"
echo "Run 'videomarker --help' to get started"
