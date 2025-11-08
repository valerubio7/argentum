"""Database configuration and session management."""

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.infrastructure.database.models import Base


class DatabaseConfig:
    """Database configuration and session management."""

    def __init__(self, database_url: str, echo: bool = False):
        """Initialize database configuration.

        Args:
            database_url: Database connection URL (e.g., postgresql+asyncpg://...)
            echo: Whether to echo SQL statements (for debugging)
        """
        self.engine = create_async_engine(database_url, echo=echo, future=True)
        self.async_session_maker = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def create_tables(self) -> None:
        """Create all database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self) -> None:
        """Drop all database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def get_session(self) -> AsyncGenerator[AsyncSession, Any]:
        """Get an async database session.

        Yields:
            AsyncSession: Database session
        """
        async with self.async_session_maker() as session:
            try:
                yield session
            finally:
                await session.close()

    async def close(self) -> None:
        """Close database engine."""
        await self.engine.dispose()
