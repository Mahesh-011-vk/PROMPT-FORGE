"""
PromptForge AI - Model Registry & Pricing API Endpoints.
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.config import Modality, ProviderType, model_registry
from app.config.model_registry import ModelSpec
from app.core.exceptions import ResourceNotFoundException
from app.schemas.common import ResponseEnvelope

router = APIRouter(prefix="/models", tags=["Model Registry"])


class CostEstimateRequest(BaseModel):
    model_name: str = Field(..., description="Target model identifier")
    input_tokens: int = Field(..., ge=0, description="Estimated input token count")
    output_tokens: int = Field(..., ge=0, description="Estimated output token count")


class ModelRecommendRequest(BaseModel):
    modality: Modality = Field(default=Modality.TEXT, description="Target generation modality")
    requires_vision: bool = Field(default=False, description="Whether visual comprehension is required")
    prefer_local: bool = Field(default=False, description="Prefer locally-hosted Ollama model")


@router.get("")
async def list_models(
    provider: ProviderType | None = Query(None, description="Filter by provider"),
    modality: Modality | None = Query(None, description="Filter by modality"),
) -> ResponseEnvelope[list[ModelSpec]]:
    """List registered AI models and their capabilities."""
    models = model_registry.list_all(provider=provider, modality=modality)
    return ResponseEnvelope(data=models)


@router.get("/{model_name}")
async def get_model(model_name: str) -> ResponseEnvelope[ModelSpec]:
    """Retrieve detailed specification and pricing for a model."""
    spec = model_registry.get(model_name)
    if not spec:
        raise ResourceNotFoundException("Model", model_name)
    return ResponseEnvelope(data=spec)


@router.post("/estimate-cost")
async def estimate_cost(request: CostEstimateRequest) -> ResponseEnvelope[dict]:
    """Calculate token cost projection based on model pricing matrix."""
    spec = model_registry.get(request.model_name)
    if not spec:
        raise ResourceNotFoundException("Model", request.model_name)

    cost = model_registry.estimate_cost(
        model_name=request.model_name,
        input_tokens=request.input_tokens,
        output_tokens=request.output_tokens,
    )
    return ResponseEnvelope(
        data={
            "model_name": request.model_name,
            "input_tokens": request.input_tokens,
            "output_tokens": request.output_tokens,
            "estimated_cost_usd": cost,
            "currency": "USD",
        }
    )


@router.post("/recommend")
async def recommend_model(request: ModelRecommendRequest) -> ResponseEnvelope[ModelSpec]:
    """Recommend optimal AI model based on task constraints and modality."""
    recommended = model_registry.recommend_model(
        modality=request.modality,
        requires_vision=request.requires_vision,
        prefer_local=request.prefer_local,
    )
    return ResponseEnvelope(data=recommended)
