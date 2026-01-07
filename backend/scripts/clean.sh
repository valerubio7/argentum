#!/usr/bin/env bash

# Clean script - Remove temporary and cache files
set -e

echo "🧹 Cleaning temporary files and caches..."

# Remove Python cache files
echo "  ➜ Removing __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

echo "  ➜ Removing .pyc files..."
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo "  ➜ Removing .pyo files..."
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# Remove pytest cache
echo "  ➜ Removing .pytest_cache..."
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

# Remove coverage files
echo "  ➜ Removing coverage files..."
rm -rf .coverage htmlcov/ .coverage.* 2>/dev/null || true

# Remove mypy cache
echo "  ➜ Removing .mypy_cache..."
find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true

# Remove ruff cache
echo "  ➜ Removing .ruff_cache..."
find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true

# Remove build artifacts
echo "  ➜ Removing build artifacts..."
rm -rf build/ dist/ *.egg-info 2>/dev/null || true

# Remove temporary files
echo "  ➜ Removing temporary files..."
find . -type f -name "*~" -delete 2>/dev/null || true
find . -type f -name "*.swp" -delete 2>/dev/null || true
find . -type f -name "*.swo" -delete 2>/dev/null || true
find . -type f -name ".DS_Store" -delete 2>/dev/null || true

echo "✅ Cleanup complete!"
