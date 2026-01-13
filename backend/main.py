import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.connection import get_db, init_db
from presentation.api.middleware import RequestIDMiddleware
from presentation.api.routes.auth import router as auth_router
from presentation.config import settings

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Initializing database connection")
    await init_db()
    yield
    logger.info("Shutting down application")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Financial Platform",
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(auth_router, prefix="/api")

# Must be added before CORS
app.add_middleware(RequestIDMiddleware)

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

    Raises:
        HTTPException: 503 if database is unreachable
    """
    try:
        result = await session.execute(text("SELECT 1"))
        result.scalar()
        logger.info("Database health check successful")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Database health check failed: {type(e).__name__}: {str(e)}")
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
        f"Server starting on {settings.host}:{settings.port} (environment: {settings.environment})"
    )
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
