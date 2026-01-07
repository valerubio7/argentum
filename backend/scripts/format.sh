#!/usr/bin/env bash

# Format script - Auto-format code with ruff
set -e

echo "🎨 Formatting code with ruff..."

# Format code
uv run ruff format application domain infrastructure presentation main.py

# Fix auto-fixable linting issues
uv run ruff check application domain infrastructure presentation main.py --fix

echo "✅ Code formatted successfully!"
