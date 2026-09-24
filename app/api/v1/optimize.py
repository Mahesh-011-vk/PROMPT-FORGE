"""
PromptForge AI - Optimization, Repair, and Translation API Endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.analytics import UsageEvent
from app.schemas.common import ResponseEnvelope
from app.schemas.optimizer import (
    PromptOptimizeRequest,
    PromptOptimizeResponse,
    PromptRepairRequest,
    PromptRepairResponse,
    PromptTranslateRequest,
    PromptTranslateResponse,
)
from app.services.optimizer_service import optimizer_service

router = APIRouter(prefix="/prompts", tags=["Prompt Optimization & Repair"])


@router.post("/optimize")
async def optimize_prompt(
    request: PromptOptimizeRequest,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[PromptOptimizeResponse]:
    """
    Analyzes weaknesses in an existing prompt and produces an optimized before-and-after breakdown.
    """
    result = await optimizer_service.optimize(request)

    # Log analytics
    event = UsageEvent(
        event_name="prompt_optimized",
        latency_ms=85,
        tokens=250,
        cost=0.00003,
        status="SUCCESS",
        metadata_={"score_gain": result.score_after - result.score_before},
    )
    db.add(event)

    return ResponseEnvelope(data=result)


@router.post("/repair")
async def repair_prompt(
    request: PromptRepairRequest,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[PromptRepairResponse]:
    """
    Deconstructs vague or fragmented prompts and repairs them into production-ready specifications.
    """
    result = await optimizer_service.repair(request)
    return ResponseEnvelope(data=result)


@router.post("/translate")
async def translate_prompt(
    request: PromptTranslateRequest,
) -> ResponseEnvelope[PromptTranslateResponse]:
    """
    Translates prompt instructions to another language while preserving parameters, tags, and formatting.
    """
    result = await optimizer_service.translate(request)
    return ResponseEnvelope(data=result)
