"""
PromptForge AI - FastAPI Application Entry Point.
"""

from fastapi import FastAPI

from app import __app_name__, __tagline__, __version__
from app.config.settings import settings

app = FastAPI(
    title=__app_name__,
    version=__version__,
    description=f"Enterprise AI Prompt Engineering Platform. {__tagline__}",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health and liveness endpoint."""
    return {
        "status": "healthy",
        "app": __app_name__,
        "version": __version__,
        "environment": settings.ENVIRONMENT,
        "demo_mode": settings.DEMO_MODE,
    }


@app.get("/", tags=["Root"])
async def root():
    """Root metadata endpoint."""
    return {
        "message": f"Welcome to {__app_name__}",
        "tagline": __tagline__,
        "docs": "/docs",
        "health": "/health",
    }
