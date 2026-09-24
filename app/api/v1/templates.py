"""
PromptForge AI - Reusable Prompt Templates API Endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ResourceNotFoundException
from app.models.prompt import PromptTemplate
from app.prompts.template_engine import TemplateEngine
from app.schemas.common import ResponseEnvelope
from app.schemas.library import (
    TemplateCreateRequest,
    TemplateExtractRequest,
    TemplateExtractResponse,
    TemplateRenderRequest,
    TemplateRenderResponse,
    TemplateVariableInfo,
)

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


@router.post("")
async def create_template(
    payload: TemplateCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[dict]:
    """Create a new reusable prompt template."""
    tmpl = PromptTemplate(
        title=payload.title,
        description=payload.description,
        modality=payload.modality,
        category=payload.category,
        template_str=payload.template_str,
        default_variables=payload.default_variables,
        is_system=payload.is_system,
    )
    db.add(tmpl)
    await db.commit()
    await db.refresh(tmpl)
    return ResponseEnvelope(data=tmpl.to_dict(), message="Prompt template created successfully")


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


@router.post("/extract-variables")
async def extract_template_variables(
    payload: TemplateExtractRequest,
) -> ResponseEnvelope[TemplateExtractResponse]:
    """Parse a template string and extract all variable names, defaults, and filters."""
    vars_list = TemplateEngine.extract_variables(payload.template_str)
    info_list = [
        TemplateVariableInfo(
            name=v.name,
            required=v.required,
            default_value=v.default_value,
            filters=v.filters,
        )
        for v in vars_list
    ]
    return ResponseEnvelope(
        data=TemplateExtractResponse(variables=info_list, count=len(info_list)),
        message="Variables extracted successfully",
    )


@router.post("/render")
async def render_template(
    payload: TemplateRenderRequest,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[TemplateRenderResponse]:
    """Render a template by ID or raw string with supplied variables."""
    template_str = payload.template_str
    merged_vars = dict(payload.variables)

    if payload.template_id:
        stmt = select(PromptTemplate).where(PromptTemplate.id == payload.template_id)
        result = await db.execute(stmt)
        tmpl = result.scalars().first()
        if not tmpl:
            raise ResourceNotFoundException("PromptTemplate", payload.template_id)
        template_str = tmpl.template_str
        # Merge default variables underneath provided variables
        if tmpl.default_variables:
            merged = dict(tmpl.default_variables)
            merged.update(merged_vars)
            merged_vars = merged

    if not template_str:
        return ResponseEnvelope(
            data=TemplateRenderResponse(
                rendered_text="",
                used_variables={},
                missing_variables=[],
                success=False,
                error_message="Either template_id or template_str must be provided",
            ),
            success=False,
            message="Template source missing",
        )

    result = TemplateEngine.render(template_str, merged_vars, strict=payload.strict)

    return ResponseEnvelope(
        data=TemplateRenderResponse(
            rendered_text=result.rendered_text,
            used_variables=result.used_variables,
            missing_variables=result.missing_variables,
            success=result.success,
            error_message=result.error_message,
        ),
        success=result.success,
        message="Template rendered successfully" if result.success else "Template render encountered errors",
    )
