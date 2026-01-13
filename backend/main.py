from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.connection import get_db, init_db
from infrastructure.logging import get_logger, setup_logging
from presentation.api.middleware import RequestIDMiddleware
from presentation.api.routes.auth import router as auth_router
from presentation.config import settings


# Configure structured logging
setup_logging(environment=settings.environment, log_level="INFO")
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("app_startup", message="Initializing database connection")
    await init_db()
    yield
    # Shutdown (if needed)
    logger.info("app_shutdown", message="Shutting down application")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Financial Platform",
    debug=settings.debug,
    lifespan=lifespan,
)

# Register authentication router
app.include_router(auth_router, prefix="/api")

# Add Request ID middleware (must be added BEFORE CORS)
app.add_middleware(RequestIDMiddleware)

# CORS middleware with restricted methods and headers for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)


@app.get("/health")
async def health_check():
    """Basic health check endpoint for liveness probes."""
    return {"status": "healthy"}


@app.get("/health/db")
async def health_check_db(
    session: Annotated[AsyncSession, Depends(get_db)],
):
    """Database health check endpoint.

    Verifies database connectivity by executing a simple query.

    Raises:
        HTTPException: 503 if database is unreachable
    """
    try:
        # Simple query to check database connectivity
        result = await session.execute(text("SELECT 1"))
        result.scalar()
        logger.info("health_check_success", component="database")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(
            "health_check_failed",
            component="database",
            error=str(e),
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed",
        )


@app.get("/")
async def root():
    return {
        "message": "Argentum API is running",
        "version": settings.app_version,
        "status": "ok",
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(
        "server_starting",
        host=settings.host,
        port=settings.port,
        environment=settings.environment,
    )
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
