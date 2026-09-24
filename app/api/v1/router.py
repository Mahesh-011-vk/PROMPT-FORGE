"""
PromptForge AI - API v1 Master Router.
"""

from fastapi import APIRouter

from app.api.v1.categories import router as categories_router
from app.api.v1.health import router as health_router
from app.api.v1.models import router as models_router
from app.api.v1.prompts import router as prompts_router
from app.api.v1.templates import router as templates_router

api_v1_router = APIRouter()

# Include sub-routers
api_v1_router.include_router(health_router)
api_v1_router.include_router(prompts_router)
api_v1_router.include_router(categories_router)
api_v1_router.include_router(models_router)
api_v1_router.include_router(templates_router)
