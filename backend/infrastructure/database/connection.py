import os
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

from infrastructure.logging import get_logger

# Only override env vars if not already set (e.g., by tests)
load_dotenv(override=False)

logger = get_logger(__name__)

Base = declarative_base()

# Validate DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required. "
        "Please set it in your .env file or environment."
    )

# Only echo SQL in development
is_development = os.getenv("ENVIRONMENT", "development").lower() == "development"
engine = create_async_engine(
    DATABASE_URL,
    echo=is_development,
    pool_pre_ping=True,  # Verify connections before using
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide database session.

    Note: Transaction management (commit/rollback) should be handled
    by the caller (route handlers), not here.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """Initialize database tables."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("database_init_success", message="Database connection successful")
    except Exception as e:
        logger.error(
            "database_init_failed",
            error=str(e),
            error_type=type(e).__name__,
        )
        raise
