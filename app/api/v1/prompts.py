"""
PromptForge AI - Prompts API Endpoints.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ResourceNotFoundException
from app.models.analytics import UsageEvent
from app.models.prompt import Prompt, PromptVersion
from app.prompts.engine import prompt_engine
from app.schemas.common import ResponseEnvelope
from app.schemas.prompt import PromptGenerateRequest, PromptGenerationResult

router = APIRouter(prefix="/prompts", tags=["Prompt Generation & Management"])


@router.post("/generate")
async def generate_prompt(
    request: PromptGenerateRequest,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[PromptGenerationResult]:
    """
    Transforms a natural language idea into highly structured, optimized, multi-variant prompts.
    """
    result = await prompt_engine.generate(request)

    # Log analytics usage event
    event = UsageEvent(
        event_name="prompt_generated",
        modality=result.intent.modality.value,
        category=result.intent.category,
        model_used=request.target_model,
        latency_ms=120,
        tokens=350,
        cost=0.00005,
        status="SUCCESS",
        metadata_={"quality_score": result.quality_score},
    )
    db.add(event)

    return ResponseEnvelope(data=result)


@router.get("")
async def list_prompts(
    modality: str | None = Query(None, description="Filter by modality"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[list[dict]]:
    """List saved prompts with pagination."""
    stmt = select(Prompt)
    if modality:
        stmt = stmt.where(Prompt.modality == modality)
    stmt = stmt.order_by(Prompt.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(stmt)
    prompts = result.scalars().all()
    return ResponseEnvelope(data=[p.to_dict() for p in prompts])


@router.get("/{prompt_id}")
async def get_prompt(
    prompt_id: str,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[dict]:
    """Retrieve a specific prompt and its versions."""
    stmt = select(Prompt).where(Prompt.id == prompt_id)
    result = await db.execute(stmt)
    prompt = result.scalars().first()

    if not prompt:
        raise ResourceNotFoundException("Prompt", prompt_id)

    versions_stmt = select(PromptVersion).where(PromptVersion.prompt_id == prompt_id).order_by(PromptVersion.version_number)
    versions_result = await db.execute(versions_stmt)
    versions = versions_result.scalars().all()

    payload = prompt.to_dict()
    payload["versions"] = [v.to_dict() for v in versions]
    return ResponseEnvelope(data=payload)
