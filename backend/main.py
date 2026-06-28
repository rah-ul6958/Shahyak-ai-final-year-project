"""
SAHAYAK-AI Backend Entry Point

FastAPI application for the disaster response AI platform.
"""

import time
from contextlib import asynccontextmanager
from typing import Any, Dict

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings, detect_profile, get_model_config
from agents.graph import sahayak_graph
from api.routes import router as api_router

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Application state
app_state: Dict[str, Any] = {
    "startup_time": None,
    "model_loaded": False,
    "chroma_ready": False,
}


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    """
    Application lifespan handler for startup and shutdown.
    """
    logger.info(
        "sahayak_ai_starting",
        hardware_profile=settings.hardware_profile,
        model=get_model_config(settings.hardware_profile)["model"],
    )

    app_state["startup_time"] = time.time()

    # Initialize ChromaDB
    try:
        from rag.vector_store import get_chroma_client

        client = get_chroma_client()
        # Try to access collection to verify
        client.get_collection("ndma_protocols")
        app_state["chroma_ready"] = True
        logger.info("chroma_db_ready")
    except Exception as e:
        logger.warning("chroma_db_not_ready", error=str(e))
        app_state["chroma_ready"] = False

    # Test Ollama connection
    try:
        from llm.ollama_client import get_ollama_client

        client = get_ollama_client()
        client.list()
        app_state["model_loaded"] = True
        logger.info("ollama_ready")
    except Exception as e:
        logger.warning("ollama_not_ready", error=str(e))
        app_state["model_loaded"] = False

    logger.info(
        "sahayak_ai_started",
        uptime_seconds=time.time() - app_state["startup_time"],
    )

    yield

    logger.info("sahayak_ai_shutting_down")


# Create FastAPI application
app = FastAPI(
    title="SAHAYAK-AI API",
    description="State-Aware Hazard Assistance & Yielding Action Knowledge - Offline Disaster Response AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint returning basic info."""
    return {
        "name": "SAHAYAK-AI",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for monitoring.
    """
    profile = detect_profile()
    model_cfg = get_model_config(profile)

    # Check OSRM
    osrm_reachable = False
    try:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.osrm_host}/health",
                timeout=5.0,
            )
            osrm_reachable = response.status_code == 200
    except Exception:
        pass

    return {
        "status": (
            "healthy"
            if (app_state["model_loaded"] and app_state["chroma_ready"])
            else "degraded"
        ),
        "model_loaded": app_state["model_loaded"],
        "chroma_ready": app_state["chroma_ready"],
        "osrm_reachable": osrm_reachable,
        "hardware_profile": profile.value,
        "model": model_cfg["model"],
        "whisper_model": model_cfg["whisper"],
        "uptime_seconds": (
            time.time() - app_state["startup_time"]
            if app_state["startup_time"]
            else 0
        ),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
        log_level=settings.log_level.lower(),
    )