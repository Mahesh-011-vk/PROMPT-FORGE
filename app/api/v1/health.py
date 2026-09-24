"""
PromptForge AI - Health, Readiness, and Metrics Endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app import __app_name__, __tagline__, __version__
from app.config import model_registry, settings
from app.core.database import get_db
from app.schemas.common import ResponseEnvelope

router = APIRouter(tags=["Health & Observability"])


@router.get("/health")
async def health_check() -> ResponseEnvelope[dict]:
    """Application liveness check."""
    return ResponseEnvelope(
        data={
            "status": "healthy",
            "app": __app_name__,
            "version": __version__,
            "tagline": __tagline__,
            "environment": settings.ENVIRONMENT,
            "demo_mode": settings.DEMO_MODE,
        }
    )


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)) -> ResponseEnvelope[dict]:
    """Application readiness check verifying database connectivity."""
    db_status = "connected"
    try:
        await db.execute(text("SELECT 1"))
    except SQLAlchemyError as e:
        db_status = f"unhealthy: {e!s}"

    return ResponseEnvelope(
        data={
            "status": "ready" if "unhealthy" not in db_status else "degraded",
            "database": db_status,
            "cache": "in-memory" if settings.USE_IN_MEMORY_CACHE else "redis",
            "active_providers": [p.value for p in settings.active_providers],
        }
    )


@router.get("/metrics")
async def metrics_summary() -> ResponseEnvelope[dict]:
    """Observability metrics summary."""
    models = model_registry.list_all()
    return ResponseEnvelope(
        data={
            "registered_models_count": len(models),
            "feature_flags": {
                "rag": settings.ENABLE_RAG,
                "agents": settings.ENABLE_AGENTS,
                "analytics": settings.ENABLE_ANALYTICS,
                "evaluation": settings.ENABLE_EVALUATION,
                "injection_defense": settings.ENABLE_PROMPT_INJECTION_DEFENSE,
            },
            "rate_limits": {
                "anonymous": settings.RATE_LIMITS.ANONYMOUS,
                "user": settings.RATE_LIMITS.USER,
                "power_user": settings.RATE_LIMITS.POWER_USER,
                "admin": settings.RATE_LIMITS.ADMIN,
            },
        }
    )
