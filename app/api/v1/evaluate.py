"""
PromptForge AI - Evaluation Lab API Endpoints.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.analytics import UsageEvent
from app.schemas.common import ResponseEnvelope
from app.schemas.evaluation import (
    ABTestRequest,
    ABTestResponse,
    BenchmarkReport,
    PromptEvaluateRequest,
    PromptEvaluateResponse,
)
from app.services.evaluator_service import evaluator_service

router = APIRouter(prefix="/prompts", tags=["Prompt Evaluation Lab"])


@router.post("/evaluate")
async def evaluate_prompt(
    request: PromptEvaluateRequest,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[PromptEvaluateResponse]:
    """
    Evaluates prompt quality, specificity, safety, and model compatibility with rubric scoring.
    """
    result = await evaluator_service.evaluate(request)

    # Log analytics
    event = UsageEvent(
        event_name="evaluation_completed",
        model_used=request.model,
        latency_ms=result.latency_ms,
        tokens=result.tokens_used,
        cost=result.estimated_cost_usd,
        status="SUCCESS",
        metadata_={"overall_score": result.overall_score},
    )
    db.add(event)

    return ResponseEnvelope(data=result)


@router.post("/ab-test")
async def ab_test_prompts(
    request: ABTestRequest,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[ABTestResponse]:
    """
    Runs head-to-head comparison between two prompt variants across evaluation rubrics.
    """
    result = await evaluator_service.compare_ab(request)
    return ResponseEnvelope(data=result)


@router.post("/benchmark")
async def run_benchmark(
    dataset_path: str = Query("datasets/image_prompts.jsonl", description="Path to evaluation dataset"),
    model: str = Query("mock-forge-v1", description="Model used for benchmark"),
    max_samples: int = Query(10, ge=1, le=100),
) -> ResponseEnvelope[BenchmarkReport]:
    """
    Executes batch offline benchmark evaluation over a .jsonl dataset.
    """
    result = await evaluator_service.run_benchmark(dataset_path=dataset_path, model=model, max_samples=max_samples)
    return ResponseEnvelope(data=result)
