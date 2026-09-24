"""
PromptForge AI - Reusable Prompt Templates API Endpoints.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ResourceNotFoundException
from app.models.prompt import PromptTemplate
from app.schemas.common import ResponseEnvelope

router = APIRouter(prefix="/templates", tags=["Prompt Templates"])


@router.get("")
async def list_templates(
    modality: str | None = Query(None, description="Filter templates by modality"),
    category: str | None = Query(None, description="Filter templates by category"),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[list[dict]]:
    """List system and custom prompt templates."""
    stmt = select(PromptTemplate)
    if modality:
        stmt = stmt.where(PromptTemplate.modality == modality)
    if category:
        stmt = stmt.where(PromptTemplate.category == category)
    stmt = stmt.order_by(PromptTemplate.title)

    result = await db.execute(stmt)
    templates = result.scalars().all()
    return ResponseEnvelope(data=[tmpl.to_dict() for tmpl in templates])


@router.get("/{template_id}")
async def get_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[dict]:
    """Retrieve template details, default variables, and template string."""
    stmt = select(PromptTemplate).where(PromptTemplate.id == template_id)
    result = await db.execute(stmt)
    template = result.scalars().first()

    if not template:
        raise ResourceNotFoundException("PromptTemplate", template_id)

    return ResponseEnvelope(data=template.to_dict())
