from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import logging
from infrastructure.database.connection import init_db
from presentation.api.routes.auth import router as auth_router


# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Initializing database connection...")
    await init_db()
    yield
    # Shutdown (if needed)
    logger.info("Shutting down...")


app = FastAPI(
    title=os.getenv("APP_NAME", "Argentum"),
    version=os.getenv("APP_VERSION", "0.1.0"),
    description="Financial Platform",
    debug=os.getenv("DEBUG", "false").lower() in ("true", "1", "yes"),
    lifespan=lifespan,
)

# Register authentication router
app.include_router(auth_router, prefix="/api")


origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Argentum API is running",
        "version": os.getenv("APP_VERSION", "0.1.0"),
        "status": "ok",
    }


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))

    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=True)
