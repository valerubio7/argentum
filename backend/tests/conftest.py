"""Shared test fixtures."""

import os
import tempfile

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

# CRITICAL: Set DATABASE_URL BEFORE importing any application modules
# Use a file-based SQLite database instead of in-memory to allow sharing between engines
# Create a temporary file for the test database
_test_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_test_db_file.close()
TEST_DB_PATH = _test_db_file.name
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB_PATH}"

# NOW import application modules (after DATABASE_URL is set)
# ruff: noqa: E402
from domain.entities.user import User
from domain.value_objects.email import Email
from domain.value_objects.password import HashedPassword
from infrastructure.database.connection import Base
from infrastructure.database.models import (
    UserModel,
)  # Import to register model with SQLAlchemy metadata

# Ensure model is registered with SQLAlchemy metadata
_ = UserModel


# Use in-memory SQLite for tests or test PostgreSQL database
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")


def pytest_configure(config):
    """Configure pytest - runs before test collection."""
    # Ensure DATABASE_URL is set before any modules are imported
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB_PATH}"


def pytest_unconfigure(config):
    """Clean up after all tests."""
    # Remove temporary database file
    import time

    time.sleep(0.1)  # Give time for connections to close
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass  # Ignore errors during cleanup


@pytest.fixture
def valid_email() -> Email:
    """Create a valid Email value object."""
    return Email("test@example.com")


@pytest.fixture
def valid_hashed_password() -> HashedPassword:
    """Create a valid HashedPassword value object."""
    # Simulated bcrypt hash (60 characters)
    return HashedPassword("$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.M7")


@pytest.fixture
def valid_username() -> str:
    """Create a valid username."""
    return "testuser"


@pytest.fixture
def user_entity(valid_email, valid_hashed_password, valid_username) -> User:
    """Create a valid User entity."""
    return User(
        email=valid_email,
        hashed_password=valid_hashed_password,
        username=valid_username,
    )


@pytest_asyncio.fixture
async def async_engine():
    """Create async engine for testing."""
    if "sqlite" in TEST_DATABASE_URL:
        engine = create_async_engine(
            TEST_DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine) -> AsyncSession:
    """Create async session for testing."""
    async_session_maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def test_session_factory(async_engine):
    """Create session factory for tests."""
    return async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture
async def client(async_engine, test_session_factory, monkeypatch):
    """Create test client with database override for API tests."""
    import sys

    # Replace the engine in the connection module before importing main
    if "infrastructure.database.connection" in sys.modules:
        connection_module = sys.modules["infrastructure.database.connection"]
        monkeypatch.setattr(connection_module, "engine", async_engine)
        monkeypatch.setattr(
            connection_module, "AsyncSessionLocal", test_session_factory
        )

    # Import after patching
    from main import app
    from infrastructure.database.connection import get_db
    from httpx import AsyncClient, ASGITransport

    # Override get_db dependency
    async def override_get_db():
        async with test_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Clean up
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
