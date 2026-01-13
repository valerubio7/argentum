import logging
import os
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

# Only override env vars if not already set (e.g., by tests)
load_dotenv(override=False)

logger = logging.getLogger(__name__)

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

# Get connection pool configuration from environment
pool_size = int(os.getenv("DB_POOL_SIZE", "5"))
max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "10"))
pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))
pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "3600"))

engine = create_async_engine(
    DATABASE_URL,
    echo=is_development,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=pool_size,  # Number of connections to maintain
    max_overflow=max_overflow,  # Additional connections when pool is full
    pool_timeout=pool_timeout,  # Seconds to wait for connection
    pool_recycle=pool_recycle,  # Recycle connections after N seconds
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
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database init failed: {type(e).__name__} - {str(e)}")
        raise
