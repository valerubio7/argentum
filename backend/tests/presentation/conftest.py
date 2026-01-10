"""Conftest for presentation layer tests - sets up test environment.

This file MUST be loaded before main.py to ensure DATABASE_URL is set correctly.
"""

import os

# Set environment variable for SQLite BEFORE any other imports
# This is critical - it must be set before importing any modules that create database connections
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
