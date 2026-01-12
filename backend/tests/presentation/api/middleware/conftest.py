"""Conftest for middleware tests - reuses fixtures from auth endpoint tests."""

import os
import tempfile
import time

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create test database engine with SQLite file.

    Each test gets its own isolated SQLite database file to ensure
    complete independence from other tests.
    """
    # Import after DATABASE_URL is set in conftest
    from infrastructure.database.connection import Base

    # Create a NEW temporary database file for each test
    # This ensures complete isolation regardless of execution order
    test_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    test_db_file.close()
    test_db_path = test_db_file.name
    test_db_url = f"sqlite+aiosqlite:///{test_db_path}"

    engine = create_async_engine(
        test_db_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup: dispose engine and delete temp file
    await engine.dispose()

    # Remove temporary database file
    time.sleep(0.1)  # Give time for connections to close
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except Exception:
            pass  # Ignore errors during cleanup


@pytest_asyncio.fixture
async def test_session_factory(test_engine):
    """Create session factory for tests."""
    return async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def client(test_engine, test_session_factory, monkeypatch):
    """Create test client with database override.

    This fixture ensures complete isolation by:
    1. Replacing the global engine in connection module with test_engine
    2. Overriding FastAPI's get_db dependency to use test sessions
    """
    import sys

    # CRITICAL: Replace the engine in the connection module BEFORE importing main
    # This ensures that even if connection.py was already imported by other tests,
    # we use our test engine
    if "infrastructure.database.connection" in sys.modules:
        connection_module = sys.modules["infrastructure.database.connection"]
        # Replace with test engine
        monkeypatch.setattr(connection_module, "engine", test_engine)
        monkeypatch.setattr(
            connection_module, "AsyncSessionLocal", test_session_factory
        )

    # Now safe to import main
    from infrastructure.database.connection import get_db
    from main import app

    # Override function that will be called by FastAPI
    async def override_get_db():
        async with test_session_factory() as session:
            yield session

    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db

    # Create test client
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(client):
    """Create a test user for authentication tests."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123!",
    }

    response = await client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201

    # Return user data with plaintext password for login tests
    return user_data


@pytest_asyncio.fixture
async def test_user_token(client, test_user):
    """Get authentication token for test user."""
    response = await client.post(
        "/api/auth/login",
        json={
            "email": test_user["email"],
            "password": test_user["password"],
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]
