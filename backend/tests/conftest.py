"""Shared test fixtures."""

import os
import pytest
import pytest_asyncio
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from domain.entities.user import User
from domain.value_objects.email import Email
from domain.value_objects.password import HashedPassword
from infrastructure.database.connection import Base
from infrastructure.database.models import UserModel  # noqa: F401


# Use in-memory SQLite for tests or test PostgreSQL database
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")


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
