from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.presentation.api.dependencies import get_database_config
from app.presentation.api.routes import auth_router
from app.presentation.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    db_config = get_database_config()
    await db_config.create_tables()
    yield
    # Shutdown
    await db_config.close()


# Create FastAPI application
app = FastAPI(
    title="ARGENTUM API",
    description="API for the ARGENTUM application",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "ARGENTUM API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
