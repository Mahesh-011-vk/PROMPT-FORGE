"""
PromptForge AI - Categories API Endpoints.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ResourceNotFoundException
from app.models.prompt import PromptCategory
from app.schemas.common import ResponseEnvelope

router = APIRouter(prefix="/categories", tags=["Prompt Taxonomy"])


@router.get("")
async def list_categories(
    modality: str | None = Query(None, description="Filter categories by modality (text, image, video, code, etc.)"),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[list[dict]]:
    """List all supported taxonomy prompt categories."""
    stmt = select(PromptCategory)
    if modality:
        stmt = stmt.where(PromptCategory.modality == modality)
    stmt = stmt.order_by(PromptCategory.name)

    result = await db.execute(stmt)
    categories = result.scalars().all()
    return ResponseEnvelope(data=[cat.to_dict() for cat in categories])


@router.get("/{slug}")
async def get_category(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[dict]:
    """Retrieve details for a specific taxonomy category by slug."""
    stmt = select(PromptCategory).where(PromptCategory.slug == slug)
    result = await db.execute(stmt)
    category = result.scalars().first()

    if not category:
        raise ResourceNotFoundException("PromptCategory", slug)

    return ResponseEnvelope(data=category.to_dict())
