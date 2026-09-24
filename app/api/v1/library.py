"""
PromptForge AI - Prompt Library API Endpoints.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.common import PaginatedResponse, ResponseEnvelope
from app.schemas.library import (
    PromptCreateRequest,
    PromptExportRequest,
    PromptExportResponse,
    PromptImportRequest,
    PromptImportResponse,
    PromptUpdateRequest,
)
from app.services.library_service import LibraryService

router = APIRouter(prefix="/library", tags=["Prompt Library"])


@router.get("/prompts")
async def list_library_prompts(
    q: str | None = Query(None, description="Search keyword in title or input"),
    modality: str | None = Query(None, description="Filter by modality"),
    category: str | None = Query(None, description="Filter by category"),
    tag: str | None = Query(None, description="Filter by specific tag"),
    favorite: bool | None = Query(None, description="Filter favorites"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[dict[str, Any]]:
    """Search and browse prompts stored in the prompt library."""
    offset = (page - 1) * page_size
    prompts, total = await LibraryService.list_prompts(
        db=db,
        query=q,
        modality=modality,
        category=category,
        tag=tag,
        is_favorite=favorite,
        limit=page_size,
        offset=offset,
    )
    return PaginatedResponse(
        items=prompts,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/prompts")
async def create_library_prompt(
    payload: PromptCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[dict[str, Any]]:
    """Save a new prompt to the library with initial version snapshot."""
    created = await LibraryService.create_prompt(db=db, payload=payload)
    return ResponseEnvelope(
        data=created,
        message="Prompt successfully added to library",
    )


@router.get("/prompts/{prompt_id}")
async def get_library_prompt(
    prompt_id: str,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[dict[str, Any]]:
    """Retrieve full prompt details with all version history."""
    prompt = await LibraryService.get_prompt(db=db, prompt_id=prompt_id)
    return ResponseEnvelope(data=prompt)


@router.put("/prompts/{prompt_id}")
async def update_library_prompt(
    prompt_id: str,
    payload: PromptUpdateRequest,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[dict[str, Any]]:
    """Update prompt metadata (title, category, tags, favorite)."""
    updated = await LibraryService.update_prompt(db=db, prompt_id=prompt_id, payload=payload)
    return ResponseEnvelope(
        data=updated,
        message="Prompt updated successfully",
    )


@router.delete("/prompts/{prompt_id}")
async def delete_library_prompt(
    prompt_id: str,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[dict[str, bool]]:
    """Delete a prompt and all its associated version history."""
    deleted = await LibraryService.delete_prompt(db=db, prompt_id=prompt_id)
    return ResponseEnvelope(
        data={"deleted": deleted},
        message="Prompt removed from library",
    )


@router.get("/tags")
async def list_library_tags(
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[list[str]]:
    """Get all unique tags used across all prompts in the library."""
    tags = await LibraryService.list_unique_tags(db=db)
    return ResponseEnvelope(data=tags)


@router.post("/export")
async def export_library_prompts(
    payload: PromptExportRequest,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[PromptExportResponse]:
    """Export prompts in JSON, CSV, Markdown, or YAML format."""
    export_data = await LibraryService.export_prompts(
        db=db,
        format_type=payload.format,
        modality=payload.modality,
        category=payload.category,
        tag=payload.tag,
        only_favorites=payload.only_favorites,
    )
    return ResponseEnvelope(
        data=export_data,
        message=f"Exported {export_data.prompt_count} prompts as {payload.format.upper()}",
    )


@router.post("/import")
async def import_library_prompts(
    payload: PromptImportRequest,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[PromptImportResponse]:
    """Batch import prompts into library."""
    count, ids, errors = await LibraryService.import_prompts(db=db, items=payload.prompts)
    return ResponseEnvelope(
        data=PromptImportResponse(
            imported_count=count,
            created_ids=ids,
            errors=errors,
        ),
        message=f"Successfully imported {count} prompts",
    )
