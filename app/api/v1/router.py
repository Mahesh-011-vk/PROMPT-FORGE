"""
PromptForge AI - API v1 Master Router.
"""

from fastapi import APIRouter

from app.api.v1.agents import router as agents_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.categories import router as categories_router
from app.api.v1.evaluate import router as evaluate_router
from app.api.v1.health import router as health_router
from app.api.v1.library import router as library_router
from app.api.v1.models import router as models_router
from app.api.v1.optimize import router as optimize_router
from app.api.v1.prompts import router as prompts_router
from app.api.v1.rag import router as rag_router
from app.api.v1.templates import router as templates_router
from app.api.v1.versions import router as versions_router

api_v1_router = APIRouter()

# Include sub-routers
api_v1_router.include_router(health_router)
api_v1_router.include_router(prompts_router)
api_v1_router.include_router(optimize_router)
api_v1_router.include_router(evaluate_router)
api_v1_router.include_router(rag_router)
api_v1_router.include_router(library_router)
api_v1_router.include_router(versions_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(agents_router)
api_v1_router.include_router(categories_router)
api_v1_router.include_router(models_router)
api_v1_router.include_router(templates_router)
