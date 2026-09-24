"""
PromptForge AI - Git-Like Prompt Version Control API Endpoints.
"""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.common import ResponseEnvelope
from app.schemas.versioning import (
    VersionCommitRequest,
    VersionDiffResponse,
    VersionRestoreResponse,
    VersionSummary,
)
from app.services.version_control import VersionControlService

router = APIRouter(prefix="/prompts/{prompt_id}", tags=["Prompt Version Control"])


@router.post("/versions")
async def commit_new_version(
    prompt_id: str,
    payload: VersionCommitRequest,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[VersionSummary]:
    """Commit an immutable new version to an existing prompt (advancing HEAD)."""
    version = await VersionControlService.commit_new_version(
        db=db,
        prompt_id=prompt_id,
        payload=payload,
    )
    return ResponseEnvelope(
        data=version,
        message=f"Committed new version v{version.version_number} successfully",
    )


@router.get("/versions")
async def list_versions(
    prompt_id: str,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[list[VersionSummary]]:
    """Retrieve the full commit log and version history for a prompt."""
    versions = await VersionControlService.list_versions(
        db=db,
        prompt_id=prompt_id,
    )
    return ResponseEnvelope(data=versions)


@router.get("/versions/{version_id_or_number}")
async def get_version(
    prompt_id: str,
    version_id_or_number: str,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[dict[str, Any]]:
    """Get snapshot of a specific historical version."""
    version = await VersionControlService.get_version(
        db=db,
        prompt_id=prompt_id,
        version_id_or_number=version_id_or_number,
    )
    return ResponseEnvelope(data=version)


@router.get("/diff")
async def get_version_diff(
    prompt_id: str,
    from_version: int = Query(..., ge=1, description="Base version number to compare from"),
    to_version: int = Query(..., ge=1, description="Target version number to compare to"),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[VersionDiffResponse]:
    """Compute line-by-line diff and semantic change analysis between two versions."""
    diff_result = await VersionControlService.compute_diff(
        db=db,
        prompt_id=prompt_id,
        from_ver_num=from_version,
        to_ver_num=to_version,
    )
    return ResponseEnvelope(data=diff_result)


@router.post("/restore/{version_number}")
async def restore_version(
    prompt_id: str,
    version_number: int,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[VersionRestoreResponse]:
    """Revert/restore prompt to a historical version by creating an append-only restore commit."""
    restore_result = await VersionControlService.restore_version(
        db=db,
        prompt_id=prompt_id,
        target_version_number=version_number,
    )
    return ResponseEnvelope(
        data=restore_result,
        message=restore_result.message,
    )
