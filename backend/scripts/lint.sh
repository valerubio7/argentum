#!/usr/bin/env bash

# Lint script - Run static analysis and type checking
set -e

echo "🔍 Running linters and type checkers..."

# Linting with ruff
uv run ruff check application domain infrastructure presentation main.py

# Format check with ruff
uv run ruff format application domain infrastructure presentation main.py --check

echo "✅ All checks passed!"
